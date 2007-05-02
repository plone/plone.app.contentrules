from warnings import warn

from zope.interface import implements
from zope.component import getMultiAdapter, getUtility
from zope.app.container.interfaces import INameChooser

from Acquisition import aq_base, aq_inner, aq_parent, Implicit
from OFS.SimpleItem import SimpleItem
from Products.Five import BrowserView

from plone.contentrules.engine.interfaces import IRuleStorage

from plone.app.contentrules.browser.interfaces import IRuleAdding
from plone.app.contentrules.browser.interfaces import IRuleConditionAdding
from plone.app.contentrules.browser.interfaces import IRuleActionAdding

class RuleAdding(Implicit, BrowserView):
    implements(IRuleAdding)

    def add(self, content):
        """Add the rule to the context
        """
        storage = getUtility(IRuleStorage)
        chooser = INameChooser(storage)
        storage[chooser.chooseName(None, content)] = content
        
    def nextURL(self):
        url = str(getMultiAdapter((self.context, self.request), name=u"absolute_url"))
        return url + "/@@rules-controlpanel"

    def renderAddButton(self):
        warn("The renderAddButton method is deprecated, use nameAllowed",
            DeprecationWarning, 2)

    def namesAccepted(self):
        return False

    def nameAllowed(self):
        return False

class RuleElementAdding(Implicit, BrowserView):
        
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
        
class RuleConditionAdding(RuleElementAdding):
    implements(IRuleConditionAdding)
    
    def add(self, content):
        """Add the rule element to the context rule
        """
        rule = aq_base(aq_inner(self.context))
        rule.conditions.append(content)
        
class RuleActionAdding(RuleElementAdding):
    implements(IRuleActionAdding)
    
    def add(self, content):
        """Add the rule element to the context rule
        """
        rule = aq_base(aq_inner(self.context))
        rule.actions.append(content)
