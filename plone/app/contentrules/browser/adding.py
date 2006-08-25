from warnings import warn

from zope.interface import implements
from zope.component import getMultiAdapter
from zope.app.container.interfaces import INameChooser


from Acquisition import Implicit

from Products.Five import BrowserView

from plone.contentrules.engine.interfaces import IRuleAdding
from plone.contentrules.engine.interfaces import IRuleManager

class RuleAdding(Implicit, BrowserView):
    implements(IRuleAdding)

    contentName = None

    def add(self, content):
        """Add the rule to the context
        """
        manager = IRuleManager(self.context)
        
        if not self.contentName:
            chooser = INameChooser(manager)
            self.contentName = chooser.chooseName('', content)
            
        manager[self.contentName] = content
        
    def nextURL(self):
        return str(getMultiAdapter((self.context, self.request), name=u"absolute_url"))

    def renderAddButton(self):
        warn("The renderAddButton method is deprecated, use nameAllowed",
            DeprecationWarning, 2)

    def namesAccepted(self):
        return False

    def nameAllowed(self):
        return False
