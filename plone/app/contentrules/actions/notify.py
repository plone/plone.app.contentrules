# -*- coding: utf-8 -*-
from plone.contentrules.rule.interfaces import IExecutable, IRuleElementData
from zope.component import adapts
from zope.interface import implementer, Interface
from zope import schema

from OFS.SimpleItem import SimpleItem
from Products.statusmessages.interfaces import IStatusMessage

from plone.app.contentrules import PloneMessageFactory
from plone.app.contentrules import PloneMessageFactory as _
from plone.app.contentrules.actions import ActionAddForm, ActionEditForm
from plone.app.contentrules.browser.formhelper import ContentRuleFormWrapper


class INotifyAction(Interface):
    """Interface for the configurable aspects of a notify action.

    This is also used to create add and edit forms, below.
    """

    message = schema.TextLine(title=_(u"Message"),
                              description=_(u"The message to send to the user."),
                              required=True)

    message_type = schema.Choice(title=_(u"Message type"),
                                 description=_(u"Select the type of message to display."),
                                 values=("info", "warning", "error"),
                                 required=True,
                                 default="info")


@implementer(INotifyAction, IRuleElementData)
class NotifyAction(SimpleItem):
    """The actual persistent implementation of the notify action element.
    """

    message = ''
    message_type = ''

    element = 'plone.actions.Notify'

    @property
    def summary(self):
        return _(u"Notify with message ${message}", mapping=dict(message=self.message))


@implementer(IExecutable)
class NotifyActionExecutor(object):
    """The executor for this action.

    This is registered as an adapter in configure.zcml
    """
    adapts(Interface, INotifyAction, Interface)

    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        request = self.context.REQUEST
        message = PloneMessageFactory(self.element.message)
        message_type = self.element.message_type
        IStatusMessage(request).addStatusMessage(message, type=message_type)
        return True


class NotifyAddForm(ActionAddForm):
    """An add form for notify rule actions.
    """
    schema = INotifyAction
    label = _(u"Add Notify Action")
    description = _(u"A notify action can show a message to the user.")
    form_name = _(u"Configure element")
    Type = NotifyAction


class NotifyAddFormView(ContentRuleFormWrapper):
    form = NotifyAddForm


class NotifyEditForm(ActionEditForm):
    """An edit form for notify rule actions.

    z3c.form does all the magic here.
    """
    schema = INotifyAction
    label = _(u"Edit Notify Action")
    description = _(u"A notify action can show a message to the user.")
    form_name = _(u"Configure element")


class NotifyEditFormView(ContentRuleFormWrapper):
    form = NotifyAddForm
