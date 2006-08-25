from zope.interface import implements
from zope.component import adapts

from zope.traversing.interfaces import ITraversable
from zope.publisher.interfaces.http import IHTTPRequest

from plone.contentrules.engine.interfaces import IRuleContainer
from plone.contentrules.engine.interfaces import IRuleManager

class RuleNamespace(object):
    """Used to traverse to a rule.
    """
    implements(ITraversable)
    adapts(IRuleContainer, IHTTPRequest)
    
    def __init__(self, context, request=None):
        self.context = context
        self.request = request
        
    def traverse(self, name, ignore):
        manager = IRuleManager(self.context)
        return manager[name].__of__(self.context)