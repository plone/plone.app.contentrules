from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory

from plone.memoize.instance import memoize

from plone.contentrules.engine.interfaces import IRuleStorage

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone import PloneMessageFactory as _

DUMMY_RULES = (
    {'id': 'send-email-on-publication',
     'title': 'Send email on publication',
     'trigger': 'object workflow transition',
     'description': 'Send out a notification email to subscribers when the object is published and make a copy of the object in the archives.',
     'enabled': True,
     },
    {'id': 'send-review-notification',
     'title': 'Send review notification',
     'trigger': 'object workflow transition',
     'description': 'Rule for sending out email notification to reviewers.',
     'enabled': True,
     },
    {'id': 'archive-closed-project',
     'title': 'Archive closed projects',
     'trigger': 'object workflow transition',
     'description': 'Move projects to the archive when they are closed.',
     'enabled': False,
     },
    {'id': 'move-on-publish',
     'title': 'Move on publish',
     'trigger': 'object workflow transition',
     'description': 'Move objects to their public location after they are published.',
     'enabled': True,
     },
    {'id': 'notify-admin-on-event-removal',
     'title': 'Notify admin on Event removal',
     'trigger': '(object deleted)',
     'description': 'Notify the administrator when an Event gets deleted.',
     'enabled': False,
     },
    )

DUMMY_RULES_ASSIGNMENTS = {
    'send-email-on-publication': (
        {'object_title': 'Projects', 'path': '/projects',
         'content_icon': 'folder_icon.gif', 'bubble': True, 'enabled': True,},
        {'object_title': 'Management', 'path': '/company/management',
         'content_icon': 'folder_icon.gif', 'bubble': True,  'enabled': True,},
        {'object_title': 'UI Design', 'path': '/teams/uidesign',
         'content_icon': 'folder_icon.gif', 'bubble': True, 'enabled': True,}
        ),
    'move-on-publish': (
        {'object_title': 'Draft', 'path': '/draft', 'content_icon': 'folder_icon.gif', 'bubble': False, 'enabled': True,},
        ),
    }

class ContentRulesControlPanel(BrowserView):
    """Manage rules in a the global rules container
    """
    
    template = ViewPageTemplateFile('templates/controlpanel.pt')

    def __call__(self):
        form = self.request.form
        ruleIds = form.get('ruleId', [])
        storage = getUtility(IRuleStorage)
        if form.get('form.button.EnableRule', None) is not None:
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
     
    def assignmentsFor(self, ruleid):
        """ TODO: We don't yet have a way to find the assignments associated
        with a rule.
        """
        return DUMMY_RULES_ASSIGNMENTS.get(ruleid)
     
    def ruleTypesToShow(self):
        selector = []
        for event in self._events():
            selector.append(dict(id = "trigger-" + event.value.__identifier__,
                                 title = _(u"Trigger: ${name}", mapping = {'name' : event.token})),)
                                 
        selector += ({'id': 'state-enabled', 'title': _(u"Enabled")},
                     {'id': 'state-disabled', 'title': _(u"Disabled"),},
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