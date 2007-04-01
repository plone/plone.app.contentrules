from zope.interface import implements
from zope.component import getUtility, getMultiAdapter

from Acquisition import aq_inner

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.kss.interfaces import IPloneAzaxView
from plone.app.kss.azaxview import AzaxBaseView as base

class ContentrulesControlpanelCommand(base):
    """Operations on contentrules done using KSS
    """
    implements(IPloneAzaxView)
    
    def replaceFilteredRulesForm(self, ruleType):
        content = self.macroContent('@@rules-controlpanel/template/macros/rules_table_form', ruleType=ruleType)
        self.getCommandSet('core').replaceHTML('#rules_table_form', content)
        return self.render()

