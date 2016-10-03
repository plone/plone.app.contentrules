# -*- coding: utf-8 -*-
from plone.contentrules.rule.interfaces import IExecutable, IRuleElementData
from zope.component import adapts
from z3c.form import form
from zope.interface import implementer, Interface
from zope import schema

from OFS.SimpleItem import SimpleItem
from Products.CMFCore.interfaces import IActionSucceededEvent

from plone.app.contentrules import PloneMessageFactory as _
from plone.app.contentrules.browser.formhelper import AddForm, EditForm
from plone.app.contentrules.browser.formhelper import ContentRuleFormWrapper


class IWorkflowTransitionCondition(Interface):
    """Interface for the configurable aspects of a workflow transition condition.

    This is also used to create add and edit forms, below.
    """

    wf_transitions = schema.Set(
        title=_(u"Workflow transition"),
        description=_(u"The workflow transitions to check for."),
        required=True,
        value_type=schema.Choice(vocabulary="plone.app.vocabularies.WorkflowTransitions"))


@implementer(IWorkflowTransitionCondition, IRuleElementData)
class WorkflowTransitionCondition(SimpleItem):
    """The actual persistent implementation of the workflow transition condition element.
    """

    wf_transitions = []
    element = "plone.conditions.WorkflowTransition"

    @property
    def summary(self):
        return _(u"Workflow transitions are: ${transitions}",
                 mapping=dict(transitions=", ".join(self.wf_transitions)))


@implementer(IExecutable)
class WorkflowTransitionConditionExecutor(object):
    """The executor for this condition.
    """
    adapts(Interface, IWorkflowTransitionCondition, IActionSucceededEvent)

    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        return self.event.action in self.element.wf_transitions


class WorkflowTransitionAddForm(AddForm):
    """An add form for workflow transition conditions.
    """
    schema = IWorkflowTransitionCondition
    label = _(u"Add Workflow Transition Condition")
    description = _(u"A workflow transition condition can restrict rules to "
                    u"execute only after a certain transition.")
    form_name = _(u"Configure element")

    def create(self, data):
        c = WorkflowTransitionCondition()
        form.applyChanges(self, c, data)
        return c


class WorkflowTransitionAddFormView(ContentRuleFormWrapper):
    form = WorkflowTransitionAddForm


class WorkflowTransitionEditForm(EditForm):
    """An edit form for portal type conditions

    z3c.form does all the magic here.
    """
    schema = IWorkflowTransitionCondition
    label = _(u"Edit Workflow Transition Condition")
    description = _(u"A workflow transition condition can restrict rules to "
                    u"execute only after a certain transition.")
    form_name = _(u"Configure element")


class WorkflowTransitionEditFormView(ContentRuleFormWrapper):
    form = WorkflowTransitionEditForm
