from Acquisition import aq_inner
from Acquisition import aq_parent
from plone.contentrules.engine.interfaces import IRuleExecutor
from plone.contentrules.engine.interfaces import IRuleStorage
from plone.contentrules.engine.interfaces import StopRule
from plone.uuid.interfaces import IUUID
from Products.CMFCore.interfaces import IContentish
from Products.CMFCore.interfaces import ISiteRoot
from zope.component import queryUtility
from zope.component.hooks import getSite
from zope.container.interfaces import IContainerModifiedEvent
from zope.interface import Interface
from zope.lifecycleevent.interfaces import IObjectAddedEvent
from zope.lifecycleevent.interfaces import IObjectCopiedEvent
from zope.lifecycleevent.interfaces import IObjectRemovedEvent

import threading

try:
    from plone.app.discussion.interfaces import IComment
except ImportError:

    class IComment(Interface):
        """Dummy interface if there is no plone.app.discussion available."""


def _get_uid(context):
    uid = IUUID(context, None)
    if uid is not None:
        return uid

    try:
        return "/".join(context.getPhysicalPath())
    except AttributeError:
        pass

    try:
        return context.id
    except AttributeError:
        return ""


class DuplicateRuleFilter:
    """A filter which can prevent rules from being executed more than once
    regardless of context.
    """

    def __init__(self):
        self.reset()

    def reset(self):
        self.executed = set()
        self.in_progress = False
        self.cascade = False

    def __call__(self, context, rule, event):
        exec_context = getattr(event, "object", context)
        uid = _get_uid(exec_context)
        if (
            uid,
            rule.__name__,
        ) in self.executed:
            return False
        else:
            self.executed.add(
                (
                    uid,
                    rule.__name__,
                )
            )
            return True


# A thread local for keeping track of rule execution across events
_status = threading.local()


def init():
    if not hasattr(_status, "rule_filter"):
        _status.rule_filter = DuplicateRuleFilter()


def close(event):
    """Close the event processing when the request ends"""
    if hasattr(_status, "rule_filter"):
        _status.rule_filter.reset()
    _status.consumed_container_events = {}


def _consumed_container_events():
    """Container events already accounted for by a more specific event.

    zope.container fires ObjectAdded/ObjectRemoved and THEN
    notifyContainerModified on the same container (see setitem and
    uncontained), so an add or a remove can claim the container event that
    follows it. What is left over is a reorder, which emits nothing else.
    """
    if not hasattr(_status, "consumed_container_events"):
        _status.consumed_container_events = {}
    return _status.consumed_container_events


def _claim_container_event(container):
    """Record that the next container event for this container is not a reorder."""
    if container is None:
        return
    pending = _consumed_container_events()
    uid = _get_uid(container)
    pending[uid] = pending.get(uid, 0) + 1


def execute(context, event, only_event=None):
    """Execute all rules relative to the context, and bubble as appropriate.

    ``only_event`` restricts execution to rules that asked for THAT event
    interface. The rule engine matches on ``rule.event.providedBy(event)``, so
    a more specific event also matches rules bound to its base — a
    ContainerModifiedEvent is an ObjectModifiedEvent. Without this, dispatching
    a container event would fire every "Object modified" rule on the site, the
    behaviour the IContainerModifiedEvent exclusion in ``modified`` has
    prevented since 2012.
    """
    # Do nothing if there is no rule storage or it is not active
    storage = queryUtility(IRuleStorage)
    if storage is None or not storage.active:
        return

    init()

    rule_filter = _status.rule_filter

    # What the EXECUTOR filters with. `rule_filter` itself stays the
    # DuplicateRuleFilter, because the in_progress/cascade bookkeeping below is
    # its own.
    exec_filter = rule_filter
    if only_event is not None:

        def exec_filter(context, rule, event, _base=rule_filter, _only=only_event):
            rule_event = getattr(rule, "event", None)
            if rule_event is None:
                return False
            if not (rule_event is _only or rule_event.extends(_only)):
                return False
            return _base(context, rule, event)

    # Stop if someone else is already executing. This could happen if,
    # for example, a rule triggered here caused another event to be fired.
    # We continue if we are in the context of a 'cascading' rule.

    if rule_filter.in_progress and not rule_filter.cascade:
        return

    # Tell other event handlers to be equally kind
    rule_filter.in_progress = True

    # Prepare to break hard if a rule demanded execution be stopped
    try:
        # Try to execute rules in the context. It may not work if the context
        # is not a rule executor, but we may still want to bubble events
        executor = IRuleExecutor(context, None)
        if executor is not None:
            executor(event, bubbled=False, rule_filter=exec_filter)

        # Do not bubble beyond the site root
        if not ISiteRoot.providedBy(context):
            parent = aq_parent(aq_inner(context))
            while parent is not None:
                executor = IRuleExecutor(parent, None)
                if executor is not None:
                    executor(event, bubbled=True, rule_filter=exec_filter)
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
def execute_rules(event):
    """When an action is invoked on an object,
    execute rules assigned to its parent.
    Base action executor handler"""
    execute(aq_parent(aq_inner(event.object)), event)


def added(event):
    """When an object is added, execute rules assigned to its new parent."""
    obj = event.object
    _claim_container_event(event.newParent)

    if IContentish.providedBy(obj) or IComment.providedBy(obj):
        execute(event.newParent, event)


def removed(event):
    """When an IObjectRemovedEvent was received, execute rules assigned to its
    previous parent.
    """
    obj = event.object
    _claim_container_event(event.oldParent)
    if not (IContentish.providedBy(obj) or IComment.providedBy(obj)):
        return

    execute(event.oldParent, event)


def modified(event):
    """When an object is modified, execute rules assigned to its parent"""

    obj = event.object
    if not (IContentish.providedBy(obj) or IComment.providedBy(obj)):
        return

    object_events = (
        IObjectAddedEvent,
        IObjectRemovedEvent,
        IContainerModifiedEvent,
        IObjectCopiedEvent,
    )
    for event_if in object_events:
        if event_if.providedBy(event):
            return

    execute_rules(event)


def copied(event):
    """When an object is copied, execute rules assigned to its parent"""
    obj = event.object
    if not (IContentish.providedBy(obj) or IComment.providedBy(obj)):
        return

    execute(aq_parent(aq_inner(event.original)), event)


def workflow_action(event):
    """When a workflow action is invoked on an object, execute rules assigned
    to its parent.
    """
    execute_rules(event)


def execute_user_rules(event):
    site = getSite()
    execute(site, event)


def user_created(event):
    """When a user has been created, execute rules assigned to the Plonesite."""
    execute_user_rules(event)


def user_logged_in(event):
    """When a user is logged in, execute rules assigned to the Plonesite."""
    execute_user_rules(event)


def user_logged_out(event):
    """When a user is logged out, execute rules assigned to the Plonesite."""
    execute_user_rules(event)


def container_modified(event):
    """A folder's contents were REORDERED — execute rules assigned to it.

    Reordering is the one content change nothing can observe. plone.folder's
    moveObjectsByDelta ends in notifyContainerModified and emits no other
    event: no add, no remove, no move. And `modified` has excluded
    IContainerModifiedEvent since 2012, so that adding a comment to a page does
    not fire "modified" rules registered on that page — rightly, since a
    container event means "my children changed", not "my fields changed".

    That exclusion assumed a container event always arrives alongside a more
    specific one. For an add or a remove it does, and those claim it here (see
    _claim_container_event), so what reaches this point is a reorder. Rules
    bound to IObjectModifiedEvent are untouched: only a rule that names
    IContainerModifiedEvent runs, and only for reordering.

    The container is the subject of the event, so rules assigned to it apply
    directly, bubbling to its ancestors as usual.
    """
    obj = aq_inner(event.object)
    pending = _consumed_container_events()
    uid = _get_uid(obj)
    if pending.get(uid):
        pending[uid] -= 1
        return
    execute(obj, event, only_event=IContainerModifiedEvent)
