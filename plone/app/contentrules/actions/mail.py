# -*- coding: utf-8 -*-
import logging
from Acquisition import aq_inner
from smtplib import SMTPException
from zope import schema

from OFS.SimpleItem import SimpleItem
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.controlpanel import IMailSchema
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.MailHost.MailHost import MailHostError
from Products.statusmessages.interfaces import IStatusMessage
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from plone.app.contentrules import PloneMessageFactory as _
from plone.app.contentrules.actions import ActionAddForm
from plone.app.contentrules.actions import ActionEditForm
from plone.app.contentrules.browser.formhelper import ContentRuleFormWrapper
from plone.contentrules.rule.interfaces import IExecutable
from plone.contentrules.rule.interfaces import IRuleElementData
from plone.registry.interfaces import IRegistry
from plone.stringinterp.interfaces import IStringInterpolator
from zope.component import adapter
from zope.component import getUtility
from zope.component.interfaces import ComponentLookupError
from zope.globalrequest import getRequest
from zope.interface import Interface
from zope.interface import implementer

logger = logging.getLogger('plone.contentrules')


class IMailAction(Interface):
    """Definition of the configuration available for a mail action
    """
    subject = schema.TextLine(
        title=_(u'Subject'),
        description=_(u'Subject of the message'),
        required=True
    )
    source = schema.TextLine(
        title=_(u'Email source'),
        description=_(
            'The email address that sends the email. If no email is provided '
            'here, it will use the portal from address.'
        ),
        required=False
    )
    recipients = schema.TextLine(
        title=_(u'Email recipients'),
        description=_(
            'The email where you want to send this message. To send it to '
            'different email addresses, just separate them with ,'
        ),
        required=True
    )
    exclude_actor = schema.Bool(
        title=_(u'Exclude actor from recipients'),
        description=_('Do not send the email to the user that did the action.')
    )
    message = schema.Text(
        title=_(u'Message'),
        description=_(u'The message that you want to mail.'),
        required=True
    )


@implementer(IMailAction, IRuleElementData)
class MailAction(SimpleItem):
    """
    The implementation of the action defined before
    """

    subject = u''
    source = u''
    recipients = u''
    message = u''
    exclude_actor = False

    element = 'plone.actions.Mail'

    @property
    def summary(self):
        return _(u'Email report to ${recipients}',
                 mapping=dict(recipients=self.recipients))


@implementer(IExecutable)
@adapter(Interface, IMailAction, Interface)
class MailActionExecutor(object):
    """The executor for this action.
    """

    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event
        registry = getUtility(IRegistry)
        self.mail_settings = registry.forInterface(IMailSchema,
                                                   prefix='plone')

    def __call__(self):
        mailhost = getToolByName(aq_inner(self.context), 'MailHost')
        if not mailhost:
            raise ComponentLookupError(
                'You must have a Mailhost utility to execute this action'
            )

        self.email_charset = self.mail_settings.email_charset
        obj = self.event.object
        interpolator = IStringInterpolator(obj)
        self.source = self.element.source

        if self.source:
            self.source = interpolator(self.source).strip()

        if not self.source:
            # no source provided, looking for the site wide from email
            # address
            from_address = self.mail_settings.email_from_address
            if not from_address:
                # the mail can't be sent. Try to inform the user
                request = getRequest()
                if request:
                    messages = IStatusMessage(request)
                    msg = _(
                        u'Error sending email from content rule. You must '
                        u'provide a source address for mail '
                        u'actions or enter an email in the portal properties'
                    )
                    messages.add(msg, type=u'error')
                return False

            from_name = self.mail_settings.email_from_name.strip('"')
            self.source = '"{0}" <{1}>'.format(from_name.encode('utf8'),
                                               from_address)

        recip_string = interpolator(self.element.recipients)
        if recip_string:  # check recipient is not None or empty string
            recipients = set([
                str(mail.strip()) for mail in recip_string.split(',')
                if mail.strip()
            ])
        else:
            recipients = set()

        if self.element.exclude_actor:
            mtool = getToolByName(aq_inner(self.context), 'portal_membership')
            actor_email = mtool.getAuthenticatedMember().getProperty(
                'email',
                ''
            )
            if actor_email in recipients:
                recipients.remove(actor_email)

        # prepend interpolated message with \n to avoid interpretation
        # of first line as header
        self.message = u'\n{0}'.format(interpolator(self.element.message))
        self.subject = interpolator(self.element.subject)

        for email_recipient in recipients:
            try:
                # XXX: We're using "immediate=True" because otherwise we won't
                # be able to catch SMTPException as the smtp connection is made
                # as part of the transaction apparatus.
                # AlecM thinks this wouldn't be a problem if mail queuing was
                # always on -- but it isn't. (stevem)
                # so we test if queue is not on to set immediate
                mime_msg = self.create_mime_msg(email_recipient)
                if not mime_msg:
                    return False
                mailhost.send(mime_msg,
                              immediate=not mailhost.smtp_queue)
            except (MailHostError, SMTPException):
                logger.exception(
                    'mail error: Attempt to send mail in content rule failed'
                )

        return True

    def create_mime_msg(self, recipient):

        # Prepare multi-part-message to send html with
        # plain-text-fallback-message, for non-html-capable-mail-clients.
        # Thanks to Peter Bengtsson for valuable information about this in this
        # post: http://www.peterbe.com/plog/zope-html-emails
        mime_msg = MIMEMultipart('related')
        mime_msg['Subject'] = self.subject
        mime_msg['From'] = self.source
        mime_msg['To'] = recipient
        mime_msg.preamble = 'This is a multi-part message in MIME format.'

        # Encapsulate the plain and HTML versions of the message body
        # in an 'alternative' part, so message agents can decide
        # which they want to display.
        msgAlternative = MIMEMultipart('alternative')
        mime_msg.attach(msgAlternative)

        # Convert html-message to plain text.
        transforms = getToolByName(aq_inner(self.context), 'portal_transforms')
        stream = transforms.convertTo('text/plain',
                                      self.message,
                                      mimetype='text/html')
        body_plain = stream.getData().strip()

        # We attach the plain text first, the order is mandatory.
        msg_txt = MIMEText(body_plain,
                           _subtype='plain',
                           _charset=self.email_charset)
        msgAlternative.attach(msg_txt)

        # After that, attach html.
        msg_txt = MIMEText(self.message,
                           _subtype='html',
                           _charset=self.email_charset)
        msgAlternative.attach(msg_txt)

        return mime_msg


class MailAddForm(ActionAddForm):
    """
    An add form for the mail action
    """
    schema = IMailAction
    label = _(u'Add Mail Action')
    description = _(u'A mail action can mail different recipient.')
    form_name = _(u'Configure element')
    Type = MailAction
    # custom template will allow us to add help text
    template = ViewPageTemplateFile('templates/mail.pt')


class MailAddFormView(ContentRuleFormWrapper):
    form = MailAddForm


class MailEditForm(ActionEditForm):
    """
    An edit form for the mail action
    """
    schema = IMailAction
    label = _(u'Edit Mail Action')
    description = _(u'A mail action can mail different recipient.')
    form_name = _(u'Configure element')

    # custom template will allow us to add help text
    template = ViewPageTemplateFile('templates/mail.pt')


class MailEditFormView(ContentRuleFormWrapper):
    form = MailEditForm
