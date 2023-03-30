from Acquisition import aq_inner
from OFS.SimpleItem import SimpleItem
from plone.app.contentrules import PloneMessageFactory as _
from plone.app.contentrules.actions import ActionAddForm
from plone.app.contentrules.actions import ActionEditForm
from plone.app.contentrules.browser.formhelper import ContentRuleFormWrapper
from plone.base.interfaces.controlpanel import IMailSchema
from plone.contentrules.rule.interfaces import IExecutable
from plone.contentrules.rule.interfaces import IRuleElementData
from plone.registry.interfaces import IRegistry
from plone.stringinterp.interfaces import IStringInterpolator
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.MailHost.MailHost import MailHostError
from Products.statusmessages.interfaces import IStatusMessage
from smtplib import SMTPException
from zope import schema
from zope.component import adapter
from zope.component import getUtility
from zope.globalrequest import getRequest
from zope.interface import implementer
from zope.interface import Interface
from zope.interface.interfaces import ComponentLookupError

import logging


logger = logging.getLogger("plone.contentrules")


class IMailAction(Interface):
    """Definition of the configuration available for a mail action"""

    subject = schema.TextLine(
        title=_("Subject"), description=_("Subject of the message"), required=True
    )
    source = schema.TextLine(
        title=_("Email source"),
        description=_(
            "The email address that sends the email. If no email is provided "
            "here, it will use the portal from address."
        ),
        required=False,
    )
    recipients = schema.TextLine(
        title=_("Email recipients"),
        description=_(
            "The email where you want to send this message. To send it to "
            "different email addresses, just separate them with ,"
        ),
        required=True,
    )
    exclude_actor = schema.Bool(
        title=_("Exclude actor from recipients"),
        description=_("Do not send the email to the user that did the action."),
        required=False,
    )
    message = schema.Text(
        title=_("Message"),
        description=_("The message that you want to mail."),
        required=True,
    )


@implementer(IMailAction, IRuleElementData)
class MailAction(SimpleItem):
    """
    The implementation of the action defined before
    """

    subject = ""
    source = ""
    recipients = ""
    message = ""
    exclude_actor = False

    element = "plone.actions.Mail"

    @property
    def summary(self):
        return _(
            "Email report to ${recipients}", mapping=dict(recipients=self.recipients)
        )


@implementer(IExecutable)
@adapter(Interface, IMailAction, Interface)
class MailActionExecutor:
    """The executor for this action."""

    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event
        registry = getUtility(IRegistry)
        self.mail_settings = registry.forInterface(IMailSchema, prefix="plone")

    def __call__(self):
        mailhost = getToolByName(aq_inner(self.context), "MailHost")
        if not mailhost:
            raise ComponentLookupError(
                "You must have a Mailhost utility to execute this action"
            )

        email_charset = self.mail_settings.email_charset
        obj = self.event.object
        interpolator = IStringInterpolator(obj)
        source = self.element.source

        if source:
            source = interpolator(source).strip()

        if not source:
            # no source provided, looking for the site wide from email
            # address
            from_address = self.mail_settings.email_from_address
            if not from_address:
                # the mail can't be sent. Try to inform the user
                request = getRequest()
                if request:
                    messages = IStatusMessage(request)
                    msg = _(
                        "Error sending email from content rule. You must "
                        "provide a source address for mail "
                        "actions or enter an email in the portal properties"
                    )
                    messages.add(msg, type="error")
                return False

            from_name = self.mail_settings.email_from_name.strip('"')
            source = f'"{from_name}" <{from_address}>'

        recip_string = interpolator(self.element.recipients)
        if recip_string:  # check recipient is not None or empty string
            recipients = {
                str(mail.strip()) for mail in recip_string.split(",") if mail.strip()
            }
        else:
            recipients = set()

        if self.element.exclude_actor:
            mtool = getToolByName(aq_inner(self.context), "portal_membership")
            actor_email = mtool.getAuthenticatedMember().getProperty("email", "")
            if actor_email in recipients:
                recipients.remove(actor_email)

        # prepend interpolated message with \n to avoid interpretation
        # of first line as header
        message = f"\n{interpolator(self.element.message)}"

        subject = interpolator(self.element.subject)

        for email_recipient in recipients:
            try:
                # XXX: We're using "immediate=True" because otherwise we won't
                # be able to catch SMTPException as the smtp connection is made
                # as part of the transaction apparatus.
                # AlecM thinks this wouldn't be a problem if mail queuing was
                # always on -- but it isn't. (stevem)
                # so we test if queue is not on to set immediate
                mailhost.send(
                    message,
                    email_recipient,
                    source,
                    subject=subject,
                    charset=email_charset,
                    immediate=not mailhost.smtp_queue,
                )
            except (MailHostError, SMTPException):
                logger.exception(
                    "mail error: Attempt to send mail in content rule failed"
                )

        return True


class MailAddForm(ActionAddForm):
    """
    An add form for the mail action
    """

    schema = IMailAction
    label = _("Add Mail Action")
    description = _("A mail action can mail different recipient.")
    form_name = _("Configure element")
    Type = MailAction
    # custom template will allow us to add help text
    template = ViewPageTemplateFile("templates/mail.pt")


class MailAddFormView(ContentRuleFormWrapper):
    form = MailAddForm


class MailEditForm(ActionEditForm):
    """
    An edit form for the mail action
    """

    schema = IMailAction
    label = _("Edit Mail Action")
    description = _("A mail action can mail different recipient.")
    form_name = _("Configure element")

    # custom template will allow us to add help text
    template = ViewPageTemplateFile("templates/mail.pt")


class MailEditFormView(ContentRuleFormWrapper):
    form = MailEditForm
