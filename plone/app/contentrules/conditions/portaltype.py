from persistent import Persistent 
from OFS.SimpleItem import SimpleItem
from Products.CMFPlone import PloneMessageFactory as _

from zope.interface import implements, Interface
from zope.component import adapts
from zope.formlib import form
from zope import schema

from plone.contentrules.rule.interfaces import IExecutable, IRuleConditionData
from plone.contentrules.rule.rule import Node

from plone.app.contentrules.browser.formhelper import AddForm, EditForm

class IPortalTypeCondition(IRuleConditionData):
    """Interface for the configurable aspects of a portal type condition.
    
    This is also used to create add and edit forms, below.
    """
    
    portal_type = schema.Choice(title=_(u"Portal type"),
                                  description=_(u"The name of the portal type, as found in the portal_types tool"),
                                  required=True,
                                  vocabulary="plone.app.vocabularies.PortalTypes")
         
class PortalTypeCondition(SimpleItem):
    """The actual persistent implementation of the portal type condition element.
    
    Note that we must mix in SimpleItem to keep Zope 2 security happy.
    """
    implements(IPortalTypeCondition)
    
    portal_type = u''

class PortalTypeConditionExecutor(object):
    """The executor for this condition.
    
    This is registered as an adapter in configure.zcml
    """
    implements(IExecutable)
    adapts(Interface, IPortalTypeCondition, Interface)
         
    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        typeInfo = getattr(self.event.object, 'getTypeInfo', None)
        if typeInfo is None:
            return False
        return typeInfo().getId() == self.element.portal_type
        
class PortalTypeAddForm(AddForm):
    """An add form for portal type rule conditions.
    
    Note that we create a Node(), not just a LoggerAction, since this is what
    the elements list of IRule expects. The namespace traversal adapter
    (see traversal.py) takes care of unwrapping the actual instance from
    a Node when it's needed.
    """
    form_fields = form.FormFields(IPortalTypeCondition)
    label = _(u"Add Portal Type Condition")
    description = _(u"A portal type condition can restrict rules to particular content types.")
    form_name = _(u"Configure element")
    
    def create(self, data):
        c = PortalTypeCondition()
        c.portal_type = data.get('portal_type')
        return Node('plone.conditions.PortalType', c)

class PortalTypeEditForm(EditForm):
    """An edit form for portal type conditions
    
    Formlib does all the magic here.
    """
    form_fields = form.FormFields(IPortalTypeCondition)
    label = _(u"Edit Portal Type Condition")
    description = _(u"A portal type condition can restrict rules to particular content types.")
    form_name = _(u"Configure element")