import threading

from zope.component import queryUtility
from zope.component.interfaces import IObjectEvent

from plone.contentrules.engine.interfaces import IRuleStorage
from plone.contentrules.engine.interfaces import IRuleExecutor
from plone.contentrules.engine.interfaces import StopRule

from Acquisition import aq_inner, aq_parent
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.interfaces import IBaseObject
from Products.Archetypes.interfaces import IObjectInitializedEvent

class DuplicateRuleFilter(object):
    """A filter which can prevent rules from being executed more than once
    regardless of context.
    """
    
    def __init__(self):
        self.reset()

    def reset(self):
        self.executed = set()
        self.in_progress = False

    def __call__(self, context, rule, event):
        obj = context
        if IObjectEvent.providedBy(event):
            obj = event.object
        
        uid_method = getattr(obj, 'UID', None)
        if uid_method is not None:
            uid = uid_method()
        else:
            uid = '/'.join(context.getPhysicalPath())
        if (uid, rule.__name__,) in self.executed:
            return False
        else:
            self.executed.add((uid, rule.__name__,))
            return True

# A thread local for keeping track of rule execution across events
_status = threading.local()

def init():
    if not hasattr(_status, 'rule_filter'):
        _status.rule_filter = DuplicateRuleFilter()
    if not hasattr(_status, 'delayed_events'):
        _status.delayed_events = {}

def close(event):
    """Close the event processing when the request ends
    """
    if hasattr(_status, 'rule_filter'):
        _status.rule_filter.reset()
    if hasattr(_status, 'delayed_events'):
        _status.delayed_events = {}
    
def execute(context, event):
    """Execute all rules relative to the context, and bubble as appropriate.
    """
    
    # Do nothing if there is no rule storage or it is not active
    storage = queryUtility(IRuleStorage)
    if storage is None or not storage.active:
        return
    
    init()
    
    rule_filter = _status.rule_filter
    
    # Stop if someone else is already executing. This could happen if,
    # for example, a rule triggered here caused another event to be fired.
    if rule_filter.in_progress:
        return
        
    # Tell other event handlers to be equally kind
    rule_filter.in_progress = True
    
    # Prepare to break hard if a rule demanded execution be stopped
    try:
    
        # Try to execute rules in the context. It may not work if the context
        # is not a rule executor, but we may still want to bubble events
        executor = IRuleExecutor(context, None)
        if executor is not None:
            executor(event, bubbled=False, rule_filter=rule_filter)
    
        # Do not bubble beyond the site root
        if not ISiteRoot.providedBy(context):
            parent = aq_parent(aq_inner(context))
            while parent is not None:
                executor = IRuleExecutor(parent, None)
                if executor is not None:
                    executor(event, bubbled=True, rule_filter=rule_filter)
                if ISiteRoot.providedBy(parent):
                    parent = None
                else:
                    parent = aq_parent(aq_inner(parent))

    except StopRule:
        pass
    
    # We are done - other events that occur after this one will be allowed to
    # execute rules again
    rule_filter.in_progress = False

    
# Event handlers

def is_portal_factory(context):
    """Find out if the given object is in portal_factory
    """
    portal_factory = getToolByName(context, 'portal_factory', None)
    if portal_factory is not None:
        return portal_factory.isTemporary(context)
    else:
        return False

def added(event):
    """When an object is added, execute rules assigned to its new parent.

    There is special handling for Archetypes objects.
    """
    if is_portal_factory(event.object):
        return
    
    # The object added event executes too early for Archetypes objects.
    # We need to delay execution until we receive a subsequent IObjectInitializedEvent
    
    if not IBaseObject.providedBy(event.object):
        execute(event.newParent, event)
    else:
        init()
        _status.delayed_events[IObjectInitializedEvent] = event

def archetypes_initialized(event):
    """Pick up the delayed IObjectAddedEvent when an Archetypes object is
    initialised.
    """
    if is_portal_factory(event.object):
        return
    
    if not IBaseObject.providedBy(event.object):
        return

    init()
    delayed_event = _status.delayed_events.get(IObjectInitializedEvent, None)
    if delayed_event is not None:
        _status.delayed_events[IObjectInitializedEvent] = None
        execute(delayed_event.newParent, delayed_event)
        
def removed(event):
    """When an IObjectRemevedEvent was received, execute rules assigned to its
     previous parent.
    """
    
    if is_portal_factory(event.object):
        return
        
    execute(event.oldParent, event)
    
def modified(event):
    """When an object is modified, execute rules assigned to its parent
    """
    
    if is_portal_factory(event.object):
        return
    
    # Let the special handler take care of IObjectInitializedEvent
    if not IObjectInitializedEvent.providedBy(event):
        execute(aq_parent(aq_inner(event.object)), event)
        
def workflow_action(event):
    """When a workflow action is invoked on an object, execute rules assigned
    to its parent.
    """
    
    if is_portal_factory(event.object):
        return
    
    execute(aq_parent(aq_inner(event.object)), event)
