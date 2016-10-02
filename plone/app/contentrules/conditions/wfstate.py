# -*- coding: utf-8 -*-
from plone.contentrules.rule.interfaces import IExecutable, IRuleElementData
from zope.component import adapts
from zope.interface import implementer, Interface
from z3c.form import form
from zope import schema

from OFS.SimpleItem import SimpleItem
from Products.CMFCore.utils import getToolByName

from plone.app.contentrules.browser.formhelper import AddForm, EditForm
from plone.app.contentrules import PloneMessageFactory as _
from plone.app.contentrules.browser.formhelper import ContentRuleFormWrapper


class IWorkflowStateCondition(Interface):
    """Interface for the configurable aspects of a workflow state condition.

    This is also used to create add and edit forms, below.
    """

    wf_states = schema.Set(
        title=_(u"Workflow state"),
        description=_(u"The workflow states to check for."),
        required=True,
        value_type=schema.Choice(vocabulary="plone.app.vocabularies.WorkflowStates"))


@implementer(IWorkflowStateCondition, IRuleElementData)
class WorkflowStateCondition(SimpleItem):
    """The actual persistent implementation of the workflow state condition element.py.
    """

    wf_states = []
    element = "plone.conditions.WorkflowState"

    @property
    def summary(self):
        return _(u"Workflow states are: ${states}", mapping=dict(states=", ".join(self.wf_states)))


@implementer(IExecutable)
class WorkflowStateConditionExecutor(object):
    """The executor for this condition.
    """
    adapts(Interface, IWorkflowStateCondition, Interface)

    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        portal_workflow = getToolByName(self.context, 'portal_workflow', None)
        if portal_workflow is None:
            return False
        state = portal_workflow.getInfoFor(self.event.object, 'review_state', None)
        if state is None:
            return False
        return state in self.element.wf_states


class WorkflowStateAddForm(AddForm):
    """An add form for workflow state conditions.
    """
    schema = IWorkflowStateCondition
    label = _(u"Add Workflow State Condition")
    description = _(u"A workflow state condition can restrict rules to "
                    u"objects in particular workflow states")
    form_name = _(u"Configure element")

    def create(self, data):
        c = WorkflowStateCondition()
        form.applyChanges(self, c, data)
        return c


class WorkflowStateAddFormView(ContentRuleFormWrapper):
    form = WorkflowStateAddForm


class WorkflowStateEditForm(EditForm):
    """An edit form for portal type conditions

    z3c.form does all the magic here.
    """
    schema = IWorkflowStateCondition
    label = _(u"Edit Workflow State Condition")
    description = _(u"A workflow state condition can restrict rules to "
                    u"objects in particular workflow states")
    form_name = _(u"Configure element")


class WorkflowStateEditFormView(ContentRuleFormWrapper):
    form = WorkflowStateEditForm
