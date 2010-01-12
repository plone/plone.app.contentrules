from zope.interface import implements

from plone.app.kss.interfaces import IPloneKSSView
from plone.app.kss.plonekssview import PloneKSSView as base

class ContentrulesControlpanelCommand(base):
    """Operations on contentrules done using KSS
    """
    implements(IPloneKSSView)
    
    def replaceFilteredRulesForm(self, ruleType):
        content = self.macroContent('@@rules-controlpanel/template/macros/rules_table_form', ruleType=ruleType)
        self.getCommandSet('core').replaceHTML('#rules_table_form', content)
        return self.render()

