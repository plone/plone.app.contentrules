from zope.interface import implements
from zope.component import adapts, getUtility

from zope.traversing.interfaces import ITraversable
from zope.publisher.interfaces.browser import IBrowserRequest

from plone.contentrules.engine.interfaces import IRuleStorage
from plone.contentrules.rule.interfaces import IRule

from Products.CMFCore.interfaces import ISiteRoot

class RuleNamespace(object):
    """Used to traverse to a rule.
    
    Traversing to portal/++rule++foo will retrieve the rule with id 'foo'
    stored in context, acquisition-wrapped.
    """
    implements(ITraversable)
    adapts(ISiteRoot, IBrowserRequest)
    
    def __init__(self, context, request=None):
        self.context = context
        self.request = request
        
    def traverse(self, name, ignore):
        manager = getUtility(IRuleStorage)
        return manager[name].__of__(self.context)

class RuleConditionNamespace(object):
    """Used to traverse to a rule condition
    
    Traversing to portal/++rule++foo/++condition++1 will retrieve the second
    condition of the rule rule with id 'foo', acquisition-wrapped.
    """
    implements(ITraversable)
    adapts(IRule, IBrowserRequest)
    
    def __init__(self, context, request=None):
        self.context = context
        self.request = request
        
    def traverse(self, name, ignore):
        condition = self.context.conditions[int(name)]
        class ConditionProxy(condition.__class__):
            __name__ = id = "++condition++%s" % name
        new_condition = ConditionProxy()
        new_condition.__dict__ = condition.__dict__
        return new_condition
        
class RuleActionNamespace(object):
    """Used to traverse to a rule condition
    
    Traversing to portal/++rule++foo/++action++1 will retrieve the second
    condition of the rule rule with id 'foo', acquisition-wrapped.
    """
    implements(ITraversable)
    adapts(IRule, IBrowserRequest)
    
    def __init__(self, context, request=None):
        self.context = context
        self.request = request
        
    def traverse(self, name, ignore):
        url = "%s/++condition++%s" % (self.context.absolute_url(), name,)
        action = self.context.actions[int(name)].__of__(self.context)
        class ActionProxy(action.__class__):
            __name__ = id = "++action++%s" % name
            
        new_action = ActionProxy()
        new_action.__dict__ = action.__dict__
        return new_action