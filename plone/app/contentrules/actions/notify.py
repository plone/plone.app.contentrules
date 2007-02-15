import logging

from OFS.SimpleItem import SimpleItem
from persistent import Persistent 

from zope.interface import implements, Interface
from zope.component import adapts
from zope.formlib import form
from zope import schema

from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone import PloneMessageFactory
from plone.contentrules.rule.interfaces import IExecutable, IRuleActionData
from plone.contentrules.rule.rule import Node

from plone.app.contentrules.browser.formhelper import AddForm, EditForm 

from Products.statusmessages.interfaces import IStatusMessage

class INotifyAction(IRuleActionData):
    """Interface for the configurable aspects of a logger action.
    
    This is also used to create add and edit forms, below.
    """
    
    message = schema.TextLine(title=_(u"Message"),
                              description=_(u"The message to send to the user"),
                              required=True)
                                    
    message_type = schema.Choice(title=_(u"Message type"),
                                 description=_(u"Select the type of message to display"),
                                 values=("info", "warn", "stop"),
                                 required=True,
                                 default="info")
         
class NotifyAction(SimpleItem):
    """The actual persistent implementation of the logger action element.
    
    Note that we must mix in Explicit to keep Zope 2 security happy.
    """
    implements(INotifyAction)
    
    message = ''
    message_type = ''

class NotifyActionExecutor(object):
    """The executor for this action.
    
    This is registered as an adapter in configure.zcml
    """
    implements(IExecutable)
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
        
class NotifyAddForm(AddForm):
    """An add form for logger rule actions.
    
    Note that we create a Node(), not just a NotifyAction, since this is what
    the elements list of IRule expects. The namespace traversal adapter
    (see traversal.py) takes care of unwrapping the actual instance from
    a Node when it's needed.
    """
    form_fields = form.FormFields(INotifyAction)
    label = _(u"Add Notify Action")
    description = _(u"A notify action can show a message to the user.")
    form_name = _(u"Configure element")
    
    def create(self, data):
        a = NotifyAction()
        a.message = data.get('message')
        a.message_type = data.get('message_type')
        return Node('plone.actions.Notify', a)

class NotifyEditForm(EditForm):
    """An edit form for logger rule actions.
    
    Formlib does all the magic here.
    """
    form_fields = form.FormFields(INotifyAction)
    label = _(u"Edit Notify Action")
    description = _(u"A notify action can show a message to the user.")
    form_name = _(u"Configure element")