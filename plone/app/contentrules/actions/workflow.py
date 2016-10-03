# -*- coding: utf-8 -*-
from plone.contentrules.rule.interfaces import IExecutable, IRuleElementData
from zope.interface import implementer, Interface
from zope.component import adapts
from zope import schema

from OFS.SimpleItem import SimpleItem
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import utils
from Products.statusmessages.interfaces import IStatusMessage
from ZODB.POSException import ConflictError

from plone.app.contentrules import PloneMessageFactory as _
from plone.app.contentrules.actions import ActionAddForm, ActionEditForm
from plone.app.contentrules.browser.formhelper import ContentRuleFormWrapper


class IWorkflowAction(Interface):
    """Interface for the configurable aspects of a workflow action.

    This is also used to create add and edit forms, below.
    """

    transition = schema.Choice(title=_(u"Transition"),
                               description=_(u"Select the workflow transition to attempt"),
                               required=True,
                               vocabulary='plone.app.vocabularies.WorkflowTransitions')


@implementer(IWorkflowAction, IRuleElementData)
class WorkflowAction(SimpleItem):
    """The actual persistent implementation of the action element.
    """

    transition = ''
    element = "plone.actions.Workflow"

    @property
    def summary(self):
        return _(u"Execute transition ${transition}", mapping=dict(transition=self.transition))


@implementer(IExecutable)
class WorkflowActionExecutor(object):
    """The executor for this action.
    """
    adapts(Interface, IWorkflowAction, Interface)

    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        portal_workflow = getToolByName(self.context, 'portal_workflow', None)
        if portal_workflow is None:
            return False

        obj = self.event.object

        try:
            portal_workflow.doActionFor(obj, self.element.transition)
        except ConflictError, e:
            raise e
        except Exception, e:
            self.error(obj, str(e))
            return False

        return True

    def error(self, obj, error):
        request = getattr(self.context, 'REQUEST', None)
        if request is not None:
            title = utils.pretty_title_or_id(obj, obj)
            message = _(
                u"Unable to change state of ${name} as part of content rule 'workflow' action: ${error}",  # noqa
                mapping={'name': title, 'error': error})
            IStatusMessage(request).addStatusMessage(message, type="error")


class WorkflowAddForm(ActionAddForm):
    """An add form for workflow actions.
    """
    schema = IWorkflowAction
    label = _(u"Add Workflow Action")
    description = _(u"A workflow action triggers a workflow transition on an object.")
    form_name = _(u"Configure element")
    Type = WorkflowAction


class WorkflowAddFormView(ContentRuleFormWrapper):
    form = WorkflowAddForm


class WorkflowEditForm(ActionEditForm):
    """An edit form for workflow rule actions.
    """
    schema = IWorkflowAction
    label = _(u"Edit Workflow Action")
    description = _(u"A workflow action triggers a workflow transition on an object.")
    form_name = _(u"Configure element")


class WorkflowEditFormView(ContentRuleFormWrapper):
    form = WorkflowAddForm
