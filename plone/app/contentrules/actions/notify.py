from OFS.SimpleItem import SimpleItem
from plone.app.contentrules import PloneMessageFactory as _
from plone.app.contentrules.actions import ActionAddForm
from plone.app.contentrules.actions import ActionEditForm
from plone.app.contentrules.browser.formhelper import ContentRuleFormWrapper
from plone.contentrules.rule.interfaces import IExecutable
from plone.contentrules.rule.interfaces import IRuleElementData
from Products.statusmessages.interfaces import IStatusMessage
from zope import schema
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


class INotifyAction(Interface):
    """Interface for the configurable aspects of a notify action.

    This is also used to create add and edit forms, below.
    """

    message = schema.TextLine(
        title=_("Message"),
        description=_("The message to send to the user."),
        required=True,
    )

    message_type = schema.Choice(
        title=_("Message type"),
        description=_("Select the type of message to display."),
        values=("info", "warning", "error"),
        required=True,
        default="info",
    )


@implementer(INotifyAction, IRuleElementData)
class NotifyAction(SimpleItem):
    """The actual persistent implementation of the notify action element."""

    message = ""
    message_type = ""

    element = "plone.actions.Notify"

    @property
    def summary(self):
        return _(
            "Notify with message ${message}",
            mapping=dict(message=self.message),
        )


@adapter(Interface, INotifyAction, Interface)
@implementer(IExecutable)
class NotifyActionExecutor:
    """The executor for this action.

    This is registered as an adapter in configure.zcml
    """

    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        request = self.context.REQUEST
        message = _(self.element.message)
        message_type = self.element.message_type
        IStatusMessage(request).addStatusMessage(message, type=message_type)
        return True


class NotifyAddForm(ActionAddForm):
    """An add form for notify rule actions."""

    schema = INotifyAction
    label = _("Add Notify Action")
    description = _("A notify action can show a message to the user.")
    form_name = _("Configure element")
    Type = NotifyAction


class NotifyAddFormView(ContentRuleFormWrapper):
    form = NotifyAddForm


class NotifyEditForm(ActionEditForm):
    """An edit form for notify rule actions.

    z3c.form does all the magic here.
    """

    schema = INotifyAction
    label = _("Edit Notify Action")
    description = _("A notify action can show a message to the user.")
    form_name = _("Configure element")


class NotifyEditFormView(ContentRuleFormWrapper):
    form = NotifyAddForm
