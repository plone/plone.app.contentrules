from OFS.SimpleItem import SimpleItem
from plone.app.contentrules import PloneMessageFactory as _
from plone.app.contentrules.actions import ActionAddForm
from plone.app.contentrules.actions import ActionEditForm
from plone.app.contentrules.browser.formhelper import ContentRuleFormWrapper
from plone.contentrules.rule.interfaces import IExecutable
from plone.contentrules.rule.interfaces import IRuleElementData
from Products.CMFCore.utils import getToolByName
from zope import schema
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface
from zope.interface.interfaces import IObjectEvent

import logging


logger = logging.getLogger("plone.contentrules.logger")
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s -  %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


class ILoggerAction(Interface):
    """Interface for the configurable aspects of a logger action.

    This is also used to create add and edit forms, below.
    """

    targetLogger = schema.ASCIILine(title=_("Logger name"), default="Plone")

    loggingLevel = schema.Int(title=_("Logging level"), default=20)  # INFO

    message = schema.TextLine(
        title=_("Message"),
        description=_(
            "help_contentrules_logger_message",
            default="&e = the triggering event, " "&c = the context, &u = the user",
        ),
        default=_(
            "text_contentrules_logger_message",
            default="Caught &e at &c by &u",
        ),
    )


@implementer(ILoggerAction, IRuleElementData)
class LoggerAction(SimpleItem):
    """The actual persistent implementation of the logger action element.

    Note that we must mix in Explicit to keep Zope 2 security happy.
    """

    targetLogger = ""
    loggingLevel = ""
    message = ""

    element = "plone.actions.Logger"

    @property
    def summary(self):
        return _("Log message ${message}", mapping=dict(message=self.message))


@adapter(Interface, ILoggerAction, Interface)
@implementer(IExecutable)
class LoggerActionExecutor:
    """The executor for this action.

    This is registered as an adapter in configure.zcml
    """

    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def processedMessage(self):
        processedMessage = self.element.message
        if "&e" in processedMessage:
            event_class = self.event.__class__
            processedMessage = processedMessage.replace(
                "&e",
                "{}.{}".format(
                    event_class.__module__,
                    event_class.__name__,
                ),
            )

        if "&c" in processedMessage and IObjectEvent.providedBy(self.event):
            processedMessage = processedMessage.replace("&c", repr(self.event.object))

        if "&u" in processedMessage:
            mtool = getToolByName(self.context, "portal_membership")
            member = mtool.getAuthenticatedMember().getUserName()
            processedMessage = processedMessage.replace("&u", member)

        return processedMessage

    def __call__(self):
        logger = logging.getLogger(self.element.targetLogger)
        logger.log(self.element.loggingLevel, self.processedMessage())
        return True


class LoggerAddForm(ActionAddForm):
    """An add form for logger rule actions."""

    schema = ILoggerAction
    label = _("Add Logger Action")
    description = _("A logger action can output a message to the system log.")
    form_name = _("Configure element")
    Type = LoggerAction


class LoggerAddFormView(ContentRuleFormWrapper):
    form = LoggerAddForm


class LoggerEditForm(ActionEditForm):
    """An edit form for logger rule actions.

    z3c.form does all the magic here.
    """

    schema = ILoggerAction
    label = _("Edit Logger Action")
    description = _("A logger action can output a message to the system log.")
    form_name = _("Configure element")


class LoggerEditFormView(ContentRuleFormWrapper):
    form = LoggerAddForm
