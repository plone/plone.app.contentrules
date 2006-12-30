from persistent import Persistent 
from OFS.SimpleItem import SimpleItem

from zope.interface import implements, Interface
from zope.component import adapts
from zope.formlib import form
from zope import schema

from plone.contentrules.rule.interfaces import IExecutable, IRuleConditionData
from plone.contentrules.rule.rule import Node

from plone.app.contentrules.browser.formhelper import AddForm, EditForm 

from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName

class IRoleCondition(IRuleConditionData):
    """Interface for the configurable aspects of a role condition.
    
    This is also used to create add and edit forms, below.
    """
    
    role_name = schema.Choice(title=u"Role name",
                              description=u"The name of the role",
                              required=True,
                              vocabulary="plone.app.vocabularies.Roles")
         
class RoleCondition(SimpleItem):
    """The actual persistent implementation of the role condition element.
    
    Note that we must mix in SimpleItem to keep Zope 2 security happy.
    """
    implements(IRoleCondition)
    
    role_name = u''

class RoleConditionExecutor(object):
    """The executor for this condition.
    
    This is registered as an adapter in configure.zcml
    """
    implements(IExecutable)
    adapts(Interface, IRoleCondition, Interface)
         
    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        portal_membership = getToolByName(self.context, 'portal_membership', None)
        if portal_membership is None:
            return False
        member = portal_membership.getAuthenticatedMember()
        return self.element.role_name in member.getRolesInContext(aq_inner(self.context))
        
class RoleAddForm(AddForm):
    """An add form for role rule conditions.
    """
    form_fields = form.FormFields(IRoleCondition)
    
    def create(self, data):
        c = RoleCondition()
        c.role_name = data.get('role_name')
        return Node('plone.conditions.Role', c)

class RoleEditForm(EditForm):
    """An edit form for role conditions
    """
    form_fields = form.FormFields(IRoleCondition)