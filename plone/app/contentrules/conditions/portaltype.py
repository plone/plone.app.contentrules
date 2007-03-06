from OFS.SimpleItem import SimpleItem

from zope.interface import implements, Interface
from zope.component import adapts
from zope.formlib import form
from zope import schema

from plone.contentrules.rule.interfaces import IExecutable, IRuleElementData

from plone.app.contentrules.browser.formhelper import AddForm, EditForm 

from Acquisition import aq_inner
from Products.CMFPlone import PloneMessageFactory as _

class IPortalTypeCondition(Interface):
    """Interface for the configurable aspects of a portal type condition.
    
    This is also used to create add and edit forms, below.
    """
    
    portal_types = schema.Set(title=_(u"Content type"),
                              description=_(u"The content type to check for"),
                              required=True,
                              value_type=schema.Choice(vocabulary="plone.app.vocabularies.PortalTypes"))
         
class PortalTypeCondition(SimpleItem):
    """The actual persistent implementation of the portal type condition element.
    
    Note that we must mix in SimpleItem to keep Zope 2 security happy.
    """
    implements(IPortalTypeCondition, IRuleElementData)
    
    portal_types = []
    element = "plone.conditions.PortalType"
    
    @property
    def summary(self):
        return _(u"Content type is ${names}", mapping=dict(names=", ".join(self.portal_types)))

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
        getTypeInfo = getattr(aq_inner(self.event.object), 'getTypeInfo', None)
        if getTypeInfo is None:
            return False
        return getTypeInfo().getId() in self.element.portal_types
        
class PortalTypeAddForm(AddForm):
    """An add form for portal type conditions.
    """
    form_fields = form.FormFields(IPortalTypeCondition)
    label = _(u"Add Content Type Condition")
    description = _(u"A portal type condition makes the rule apply only to certain content types.")
    form_name = _(u"Configure element")
    
    def create(self, data):
        c = PortalTypeCondition()
        form.applyChanges(c, self.form_fields, data)
        return c

class PortalTypeEditForm(EditForm):
    """An edit form for portal type conditions
    """
    form_fields = form.FormFields(IPortalTypeCondition)
    label = _(u"Edit Content Type Condition")
    description = _(u"A portal type condition makes the rule apply only to certain content types.")
    form_name = _(u"Configure element")