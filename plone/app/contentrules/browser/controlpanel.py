# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from plone.app.contentrules import PloneMessageFactory as _
from plone.app.contentrules.browser.interfaces import IContentRulesControlPanel
from plone.app.contentrules.rule import get_assignments
from plone.contentrules.engine.interfaces import IRuleStorage
from plone.memoize.instance import memoize
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.i18n import translate
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory


def get_trigger_class(trigger):
    return 'trigger-{0}'.format(trigger.__identifier__.split('.')[-1].lower())


@implementer(IContentRulesControlPanel)
class ContentRulesControlPanel(BrowserView):
    """Manage rules in a the global rules container
    """
    template = ViewPageTemplateFile('templates/controlpanel.pt')

    def __call__(self):
        form = self.request.form
        if form.get('rule-id', False):
            if form.get('form.button.EnableRule', None) is not None:
                self.enable_rule()
            elif form.get('form.button.DisableRule', None) is not None:
                self.disable_rule()
            elif form.get('form.button.DeleteRule', None) is not None:
                self.delete_rule()

        if form.get('global_disable', None) is not None:
            if form['global_disable']:
                msg = self.globally_disable()
            else:
                msg = self.globally_enable()

            IStatusMessage(self.request).add(msg)

        return self.template()

    def authorize(self):
        authenticator = getMultiAdapter((self.context, self.request),
                                        name=u'authenticator')
        if not authenticator.verify():
            raise Unauthorized

    def globally_disabled(self):
        storage = getUtility(IRuleStorage)
        return not storage.active

    def registeredRules(self):
        rules = self._getRules()

        events = dict([(e.value, e.token) for e in self._events()])
        info = []
        for r in rules:
            trigger_class = get_trigger_class(r.event)
            enabled_class = r.enabled and 'state-enabled' or 'state-disabled'
            assigned = len(get_assignments(r)) > 0

            assigned_class = 'assignment-unassigned'
            if assigned:
                assigned_class = 'assignment-assigned'

            info.append({
                'id': r.__name__,
                'title': r.title,
                'description': r.description,
                'enabled': r.enabled,
                'assigned': assigned,
                'trigger': events[r.event],
                'row_class': '{0} {1} {2}'.format(
                    trigger_class,
                    enabled_class,
                    assigned_class,
                )
            })

        return info

    def ruleTypesToShow(self):
        selector = []
        rules = self._getRules()
        for event in self._events():
            # filter unused rule types
            for rule in rules:
                if rule.event == event.value:
                    break
            else:
                continue

            eventname = translate(
                event.token, context=self.request, domain='plone')
            selector.append({'id': get_trigger_class(event.value),
                             'title': eventname})

        return selector

    def statesToShow(self):
        return (
            {
                'id': 'state-enabled',
                'title': _(u'label_rule_enabled', default=u'Enabled'),
            },
            {
                'id': 'state-disabled',
                'title': _(u'label_rule_disabled', default=u'Disabled'),
            },
        )

    def _getRules(self):
        storage = getUtility(IRuleStorage)
        return storage.values()

    @memoize
    def _events(self):
        eventsFactory = getUtility(
            IVocabularyFactory, name='plone.contentrules.events')
        return eventsFactory(self.context)

    def delete_rule(self):
        self.authorize()
        rule_id = self.request['rule-id']
        storage = getUtility(IRuleStorage)
        del storage[rule_id]
        return 'ok'

    def enable_rule(self):
        self.authorize()
        storage = getUtility(IRuleStorage)
        rule_id = self.request['rule-id']
        storage[rule_id].enabled = True
        return 'ok'

    def disable_rule(self):
        self.authorize()
        storage = getUtility(IRuleStorage)
        rule_id = self.request['rule-id']
        storage[rule_id].enabled = False
        return 'ok'

    def globally_disable(self):
        self.authorize()
        storage = getUtility(IRuleStorage)
        storage.active = False
        return translate(_('Content rules has been globally disabled'),
                         context=self.request)

    def globally_enable(self):
        self.authorize()
        storage = getUtility(IRuleStorage)
        storage.active = True
        return translate(_('Content rules has been globally enabled'),
                         context=self.request)
