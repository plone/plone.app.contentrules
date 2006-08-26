from warnings import warn

from zope.interface import implements
from zope.component import getMultiAdapter
from zope.app.container.interfaces import INameChooser

from Acquisition import Implicit, aq_parent

from Products.Five import BrowserView

from plone.contentrules.engine.interfaces import IRuleAdding
from plone.contentrules.engine.interfaces import IRuleElementAdding
from plone.contentrules.engine.interfaces import IRuleManager

class RuleAdding(Implicit, BrowserView):
    implements(IRuleAdding)

    def add(self, content):
        """Add the rule to the context
        """
        manager = IRuleManager(self.context)
        manager.saveRule(content)
        
    def nextURL(self):
        url = str(getMultiAdapter((self.context, self.request), name=u"absolute_url"))
        return url + "/@@manage-content-rules"

    def renderAddButton(self):
        warn("The renderAddButton method is deprecated, use nameAllowed",
            DeprecationWarning, 2)

    def namesAccepted(self):
        return False

    def nameAllowed(self):
        return False

class RuleElementAdding(Implicit, BrowserView):
    implements(IRuleElementAdding)
    
    def add(self, content):
        """Add the rule element to the context rule
        """
        self.context.elements.append(content)
        
    def nextURL(self):
        url = str(getMultiAdapter((aq_parent(self.context), self.request), name=u"absolute_url"))
        return url + "/@@manage-content-rules"

    def renderAddButton(self):
        warn("The renderAddButton method is deprecated, use nameAllowed",
            DeprecationWarning, 2)

    def namesAccepted(self):
        return False

    def nameAllowed(self):
        return False