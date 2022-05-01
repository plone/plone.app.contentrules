from OFS.SimpleItem import SimpleItem
from plone.app.contentrules import PloneMessageFactory as _
from plone.app.contentrules.actions import ActionAddForm
from plone.app.contentrules.actions import ActionEditForm
from plone.app.contentrules.browser.formhelper import ContentRuleFormWrapper
from plone.base.utils import pretty_title_or_id
from plone.base.utils import safe_text
from plone.contentrules.rule.interfaces import IExecutable
from plone.contentrules.rule.interfaces import IRuleElementData
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from ZODB.POSException import ConflictError
from zope import schema
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


class IWorkflowAction(Interface):
    """Interface for the configurable aspects of a workflow action.

    This is also used to create add and edit forms, below.
    """

    transition = schema.Choice(
        title=_("Transition"),
        description=_("Select the workflow transition to attempt"),
        required=True,
        vocabulary="plone.app.vocabularies.WorkflowTransitions",
    )


@implementer(IWorkflowAction, IRuleElementData)
class WorkflowAction(SimpleItem):
    """The actual persistent implementation of the action element."""

    transition = ""
    element = "plone.actions.Workflow"

    @property
    def summary(self):
        return _(
            "Execute transition ${transition}",
            mapping=dict(transition=self.transition),
        )


@adapter(Interface, IWorkflowAction, Interface)
@implementer(IExecutable)
class WorkflowActionExecutor:
    """The executor for this action."""

    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        portal_workflow = getToolByName(self.context, "portal_workflow", None)
        if portal_workflow is None:
            return False

        obj = self.event.object

        try:
            portal_workflow.doActionFor(obj, self.element.transition)
        except ConflictError as e:
            raise e
        except Exception as e:
            self.error(obj, str(e))
            return False

        return True

    def error(self, obj, error):
        request = getattr(self.context, "REQUEST", None)
        if request is not None:
            title = safe_text(pretty_title_or_id(obj, obj))
            error = safe_text(error)
            message = _(
                "Unable to change state of ${name} as part of content rule 'workflow' action: ${error}",  # noqa
                mapping={"name": title, "error": error},
            )
            IStatusMessage(request).addStatusMessage(message, type="error")


class WorkflowAddForm(ActionAddForm):
    """An add form for workflow actions."""

    schema = IWorkflowAction
    label = _("Add Workflow Action")
    description = _("A workflow action triggers a workflow transition on an object.")
    form_name = _("Configure element")
    Type = WorkflowAction


class WorkflowAddFormView(ContentRuleFormWrapper):
    form = WorkflowAddForm


class WorkflowEditForm(ActionEditForm):
    """An edit form for workflow rule actions."""

    schema = IWorkflowAction
    label = _("Edit Workflow Action")
    description = _("A workflow action triggers a workflow transition on an object.")
    form_name = _("Configure element")


class WorkflowEditFormView(ContentRuleFormWrapper):
    form = WorkflowAddForm
