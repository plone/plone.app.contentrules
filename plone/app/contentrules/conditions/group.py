# -*- coding: utf-8 -*-
from plone.contentrules.rule.interfaces import IExecutable, IRuleElementData
from zope.component import adapts
from z3c.form import form
from zope.interface import implementer, Interface
from zope import schema

from OFS.SimpleItem import SimpleItem
from Products.CMFCore.utils import getToolByName

from plone.app.contentrules import PloneMessageFactory as _
from plone.app.contentrules.browser.formhelper import AddForm, EditForm
from plone.app.contentrules.browser.formhelper import ContentRuleFormWrapper


class IGroupCondition(Interface):
    """Interface for the configurable aspects of a group condition.

    This is also used to create add and edit forms, below.
    """

    group_names = schema.Set(title=_(u"Group name"),
                             description=_(u"The name of the group."),
                             required=True,
                             value_type=schema.Choice(vocabulary="plone.app.vocabularies.Groups"))


@implementer(IGroupCondition, IRuleElementData)
class GroupCondition(SimpleItem):
    """The actual persistent implementation of the group condition element.

    Note that we must mix in SimpleItem to keep Zope 2 security happy.
    """

    group_names = []
    element = "plone.conditions.Group"

    @property
    def summary(self):
        return _(u"Groups are: ${names}", mapping=dict(names=", ".join(self.group_names)))


@implementer(IExecutable)
class GroupConditionExecutor(object):
    """The executor for this condition.

    This is registered as an adapter in configure.zcml
    """
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
        for g in self.element.group_names:
            if g in groupIds:
                return True
        return False


class GroupAddForm(AddForm):
    """An add form for group rule conditions.
    """
    schema = IGroupCondition
    label = _(u"Add Group Condition")
    description = _(u"A group condition can prevent a rule from executing "
                    u"unless the current user is a member of a particular group.")
    form_name = _(u"Configure element")

    def create(self, data):
        c = GroupCondition()
        form.applyChanges(self, c, data)
        return c

class GroupAddFormView(ContentRuleFormWrapper):
    form = GroupAddForm


class GroupEditForm(EditForm):
    """An edit form for group conditions
    """
    schema = IGroupCondition
    label = _(u"Edit Group Condition")
    description = _(u"A group condition can prevent a rule from executing "
                    u"unless the current user is a member of a particular group.")
    form_name = _(u"Configure element")


class GroupEditFormView(ContentRuleFormWrapper):
    form = GroupAddForm
