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

class IGroupCondition(IRuleConditionData):
    """Interface for the configurable aspects of a group condition.
    
    This is also used to create add and edit forms, below.
    """
    
    group_name = schema.Choice(title=u"Group name",
                               description=u"The name of the group",
                               required=True,
                               vocabulary="plone.vocabulary.Groups")
         
class GroupCondition(SimpleItem):
    """The actual persistent implementation of the group condition element.
    
    Note that we must mix in SimpleItem to keep Zope 2 security happy.
    """
    implements(IGroupCondition)
    
    group_name = u''

class GroupConditionExecutor(object):
    """The executor for this condition.
    
    This is registered as an adapter in configure.zcml
    """
    implements(IExecutable)
    adapts(Interface, IGroupCondition, Interface)
         
    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        portal_membership = getToolByName(self.context, 'portal_membership', None)
        portal_groups = getToolByName(self.context, 'portal_groups', None)
        if portal_groups is None or portal_groups is None:
            return False
        member = portal_membership.getAuthenticatedMember()
        groupIds = [g.getId() for g in portal_groups.getGroupsByUserId(member.getId())]
        return self.element.group_name in groupIds
        
class GroupAddForm(AddForm):
    """An add form for group rule conditions.
    """
    form_fields = form.FormFields(IGroupCondition)
    
    def create(self, data):
        c = GroupCondition()
        c.group_name = data.get('group_name')
        return Node('plone.conditions.Group', c)

class GroupEditForm(EditForm):
    """An edit form for group conditions
    """
    form_fields = form.FormFields(IGroupCondition)