from plone.contentrules.engine.interfaces import IRuleStorage
from plone.memoize.instance import memoize
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.contentrules import PloneMessageFactory as _


class ContentRulesControlPanel(BrowserView):
    """Manage rules in a the global rules container
    """
    
    template = ViewPageTemplateFile('templates/controlpanel.pt')

    def __call__(self):
        form = self.request.form
        ruleIds = form.get('ruleId', [])
        storage = getUtility(IRuleStorage)
        if form.get('form.button.SaveSettings', None) is not None:
            storage.active = form.get('global_enable', True)
        elif form.get('form.button.EnableRule', None) is not None:
            for r in ruleIds:
                if r in storage:
                    storage[r].enabled = True
        elif form.get('form.button.DisableRule', None) is not None:
            for r in ruleIds:
                if r in storage:
                    storage[r].enabled = False
        elif form.get('form.button.DeleteRule', None) is not None:
            for r in ruleIds:
                if r in storage:
                    del storage[r]
        return self.template()

    def globally_enabled(self):
        storage = getUtility(IRuleStorage)
        return storage.active 

    def registeredRules(self):
        selector = self.request.get('ruleType', 'all')
        rules = []
        if selector.startswith('state-'):
            rules = self._rulesByState(selector[6:] == 'enabled')
        elif selector.startswith('trigger-'):
            rules = self._rulesByTrigger(selector[8:])
        else:
            rules = self._getRules()
        events = dict([(e.value, e.token) for e in self._events()])
        info = []
        for r in rules:
            info.append(dict(id = r.__name__,
                        title = r.title,
                        description = r.description,
                        enabled = r.enabled,
                        trigger = events[r.event]))
        return info
     
    def ruleTypesToShow(self):
        selector = []
        for event in self._events():
            selector.append(dict(id = "trigger-" + event.value.__identifier__,
                                 title = _(u"Trigger: ${name}", mapping = {'name' : event.token})),)
                                 
        selector += ({'id': 'state-enabled', 'title': _(u"label_rule_enabled", default=u"Enabled")},
                     {'id': 'state-disabled', 'title': _(u"label_rule_disabled", default=u"Disabled"),},
                     # {'id': 'state-rule-assigned', 'title': _(u"Rule is in use")},
                     # {'id': 'state-rule-not-assigned', 'title': _(u"Rule is not assigned anywhere"),},
                     )
        
        return selector
        
    def _rulesByState(self, state):
        return [r for r in self._getRules() if r.enabled == state]
        
    def _rulesByTrigger(self, trigger):
        return [r for r in self._getRules() if r.event.__identifier__ == trigger]
        
    def _getRules(self):
        storage = getUtility(IRuleStorage)
        return storage.values()
        
    @memoize
    def _events(self):
        eventsFactory = getUtility(IVocabularyFactory, name="plone.contentrules.events")
        return eventsFactory(self.context)