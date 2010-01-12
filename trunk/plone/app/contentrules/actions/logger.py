import logging

from plone.contentrules.rule.interfaces import IExecutable, IRuleElementData
from zope.component import adapts
from zope.component.interfaces import IObjectEvent
from zope.formlib import form
from zope.interface import implements, Interface
from zope import schema

from OFS.SimpleItem import SimpleItem

from plone.app.contentrules import PloneMessageFactory as _
from plone.app.contentrules.browser.formhelper import AddForm, EditForm


logger = logging.getLogger("plone.contentrules.logger")
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s -  %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


class ILoggerAction(Interface):
    """Interface for the configurable aspects of a logger action.
    
    This is also used to create add and edit forms, below.
    """
    
    targetLogger = schema.ASCIILine(title=_(u"Logger name"),
                                    default="rule_log")
                                   
    loggingLevel = schema.Int(title=_(u"Logging level"), 
                              default=1000)
                              
    message = schema.TextLine(title=_(u"Message"),
                                    description=u"&e = the triggering event, &c = the context",
                                    default=u"Caught &e at &c")
         
class LoggerAction(SimpleItem):
    """The actual persistent implementation of the logger action element.
    
    Note that we must mix in Explicit to keep Zope 2 security happy.
    """
    implements(ILoggerAction, IRuleElementData)
    
    targetLogger = ''
    loggingLevel = ''
    message = ''

    element = 'plone.actions.Logger'
    
    @property
    def summary(self):
        return _(u"Log message ${message}", mapping=dict(message=self.message))

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
        processedMessage = self.element.message.replace("&e", "%s.%s" % (self.event.__class__.__module__, self.event.__class__.__name__))
        if IObjectEvent.providedBy(self.event):
            processedMessage = processedMessage.replace("&c", repr(self.event.object))
        logger.log(self.element.loggingLevel, processedMessage)
        return True 
        
class LoggerAddForm(AddForm):
    """An add form for logger rule actions.
    """
    form_fields = form.FormFields(ILoggerAction)
    label = _(u"Add Logger Action")
    description = _(u"A logger action can output a message to the system log.")
    form_name = _(u"Configure element")
    
    def create(self, data):
        a = LoggerAction()
        form.applyChanges(a, self.form_fields, data)
        return a

class LoggerEditForm(EditForm):
    """An edit form for logger rule actions.
    
    Formlib does all the magic here.
    """
    form_fields = form.FormFields(ILoggerAction)
    label = _(u"Edit Logger Action")
    description = _(u"A logger action can output a message to the system log.")
    form_name = _(u"Configure element")