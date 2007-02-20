from zope.interface import implements
from zope.component import adapts, getUtility, queryMultiAdapter

from zope.traversing.interfaces import ITraversable

from zope.publisher.interfaces import NotFound
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.browser import IBrowserPublisher

from zope.app.publisher.browser import getDefaultViewName

from plone.contentrules.engine.interfaces import IRuleAssignable
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
        
class RuleTraverser(object):
    """A traverser for rules.
    
    Traversing to ++rule++foo/2 will return the third element of the rule
    'foo', acquisition-wrapped.
    """
    implements(IBrowserPublisher)
    adapts(IRule, IBrowserRequest)
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
    
    def browserDefault(self, request):
        view = getDefaultViewName(self.context, request)
        url = "@@%s" % view_name
        return self.context, (url,)
    
    def publishTraverse(self, request, name):
        try:
            idx = int(name)
            if idx >= 0 and idx < len(self.context.elements):
                return self.context.elements[idx].instance.__of__(self.context)
        except ValueError, TypeError:
            pass
        view = queryMultiAdapter((self.context, request), name=name)
        if view is not None:
            return view.__of__(self.context)
        raise NotFound(self.context, name, request)