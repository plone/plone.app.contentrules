import logging

from OFS.SimpleItem import SimpleItem
from persistent import Persistent 

from zope.interface import implements, Interface
from zope.component import adapts
from zope.formlib import form
from zope import schema

from plone.contentrules.rule.interfaces import IExecutable, IRuleActionData
from plone.contentrules.rule.rule import Node

from plone.app.contentrules.browser.formhelper import AddForm, EditForm 

from Products.CMFPlone import PloneMessageFactory as _

logger = logging.getLogger("plone.contentrules.logger")
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s -  %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

class ILoggerAction(IRuleActionData):
    """Interface for the configurable aspects of a logger action.
    
    This is also used to create add and edit forms, below.
    """
    
    targetLogger = schema.ASCIILine(title=_(u"Logger name"),
                                    default="rule_log")
                                   
    loggingLevel = schema.Int(title=_(u"Logging level"), 
                              default=1000)
                              
    message = schema.TextLine(title=_(u"Message"),
                                    description=_(u"&e = the triggering event, &c = the context"),
                                    default=u"Caught &e at &c")
         
class LoggerAction(SimpleItem):
    """The actual persistent implementation of the logger action element.
    
    Note that we must mix in Explicit to keep Zope 2 security happy.
    """
    implements(ILoggerAction)
    
    targetLogger = ''
    loggingLevel = ''
    message = ''

class LoggerActionExecutor(object):
    """The executor for this action.
    
    This is registered as an adapter in configure.zcml
    """
    implements(IExecutable)
    adapts(Interface, ILoggerAction, Interface)
         
    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        logger = logging.getLogger(self.element.targetLogger)
        processedMessage = self.element.message.replace("&e", str(self.event))
        processedMessage = processedMessage.replace("&c", str(self.context))
        logger.log(self.element.loggingLevel, processedMessage)
        return True 
        
class LoggerAddForm(AddForm):
    """An add form for logger rule actions.
    
    Note that we create a Node(), not just a LoggerAction, since this is what
    the elements list of IRule expects. The namespace traversal adapter
    (see traversal.py) takes care of unwrapping the actual instance from
    a Node when it's needed.
    """
    form_fields = form.FormFields(ILoggerAction)
    label = _(u"Add Logger Action")
    description = _(u"A logger action can output a message to the system log.")
    form_name = _(u"Configure element")
    
    def create(self, data):
        a = LoggerAction()
        a.targetLogger = data.get('targetLogger')
        a.loggingLevel = data.get('loggingLevel')
        a.message = data.get('message')
        return Node('plone.actions.Logger', a)

class LoggerEditForm(EditForm):
    """An edit form for logger rule actions.
    
    Formlib does all the magic here.
    """
    form_fields = form.FormFields(ILoggerAction)
    label = _(u"Edit Logger Action")
    description = _(u"A logger action can output a message to the system log.")
    form_name = _(u"Configure element")