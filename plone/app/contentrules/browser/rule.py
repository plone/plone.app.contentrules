from zope.formlib import form
from Products.Five.formlib import formbase
from Products.Five.browser import BrowserView 

from plone.contentrules.engine.interfaces import IRuleManager
from plone.contentrules.rule.interfaces import IRule
from plone.contentrules.rule.rule import Rule

class RuleAddForm(formbase.AddForm):
    """An add form for rules.
    """
    form_fields = form.FormFields(IRule).omit('event').omit('elements')
    
    def create(self, data):
        r = Rule()
        r.title = data.get('title')
        r.description = data.get('description')
        return r

class ListRules(BrowserView):
    """List rules in the context
    """
    
    def rule_info(self):
        manager = IRuleManager(self.context)
        rules = []
        for r in manager.listRules():
            rules.append({'title' : r.title,
                          'description' : r.description})
        return rules