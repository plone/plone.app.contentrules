from zope.component import getMultiAdapter

from zope.formlib import form
from Products.Five.formlib import formbase
from Products.Five.browser import BrowserView 

from plone.contentrules.engine.interfaces import IRuleManager
from plone.contentrules.rule.interfaces import IRule
from plone.contentrules.rule.rule import Rule

class RuleAddForm(formbase.AddForm):
    """An add form for rules.
    """
    form_fields = form.FormFields(IRule).omit('event').omit('elements').omit('__name__')
    
    def create(self, data):
        r = Rule()
        r.title = data.get('title')
        r.description = data.get('description')
        return r

class RuleEditForm(formbase.EditForm):
    """An edit form for rules.
    """
    form_fields = form.FormFields(IRule).omit('event').omit('elements').omit('__name__')

class ListRules(BrowserView):
    """List rules in the context
    """
    
    def rule_info(self):
        manager = IRuleManager(self.context)
        rules = []
        baseUrl = str(getMultiAdapter((self.context, self.request), name=u"absolute_url"))
        for k, r in manager.items():
            rules.append({'title' : r.title,
                          'description' : r.description,
                          'edit_url' : '%s/++rule++%s/edit.html' % (baseUrl, k)
                          })
        return rules