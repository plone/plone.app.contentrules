import logging

from OFS.SimpleItem import SimpleItem
from persistent import Persistent 

from zope.interface import implements, Interface
from zope.component import adapts
from zope.formlib import form
from zope import schema

from Products.CMFPlone import PloneMessageFactory
from plone.contentrules.rule.interfaces import IExecutable, IRuleActionData
from plone.contentrules.rule.rule import Node

from plone.app.contentrules.browser.formhelper import AddForm, EditForm 


class INotifyAction(IRuleActionData):
    """Interface for the configurable aspects of a logger action.
    
    This is also used to create add and edit forms, below.
    """
    
    message = schema.TextLine(title=u"message",
                                    description=u"The message to send to the user",
                                    default=u"contentRule evoked")
         
class NotifyAction(SimpleItem):
    """The actual persistent implementation of the logger action element.
    
    Note that we must mix in Explicit to keep Zope 2 security happy.
    """
    implements(INotifyAction)
    
    message = ''

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
        self.context.plone_utils.addPortalMessage(PloneMessageFactory(self.element.message))
        return True 
        
class NotifyAddForm(AddForm):
    """An add form for logger rule actions.
    
    Note that we create a Node(), not just a NotifyAction, since this is what
    the elements list of IRule expects. The namespace traversal adapter
    (see traversal.py) takes care of unwrapping the actual instance from
    a Node when it's needed.
    """
    form_fields = form.FormFields(INotifyAction)
    
    def create(self, data):
        a = NotifyAction()
        a.message = data.get('message')
        return Node('plone.actions.Notify', a)

class NotifyEditForm(EditForm):
    """An edit form for logger rule actions.
    
    Formlib does all the magic here.
    """
    form_fields = form.FormFields(INotifyAction)