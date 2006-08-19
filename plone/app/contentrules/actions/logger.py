import logging

# If Persistent doesn't work, try from OFS.SimpleItem import SimpleItem instead
from persistent import Persistent 

from zope.interface import implements, Interface
from zope.component import adapts
from zope import schema

from plone.contentrules.rule.interfaces import IExecutable

logger = logging.getLogger("plone.contentrules.logger")
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s -  %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

class ILoggerAction(Interface):
    targetLogger = schema.TextLine(title=u"target logger",default=u"temporary_logger")
    loggingLevel = schema.Int(title=u"logging level", default=1000)
    loggerMessage = schema.TextLine(title=u"message",
                                    description=u"&e = the triggering event, &c = the context",
                                    default=u"caught &e at &c")
         
class LoggerAction(Persistent):
    implements(ILoggerAction)
    
    loggingLevel = ''
    targetLogger = ''
    message = ''

class LoggerActionExecutor(object):
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