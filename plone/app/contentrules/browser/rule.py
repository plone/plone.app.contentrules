# -*- coding: utf-8 -*-
from plone.contentrules.rule.interfaces import IRuleConfiguration
from zope.component import getMultiAdapter

from Acquisition import aq_parent, aq_inner

from Products.CMFPlone.utils import base_hasattr
from plone.app.contentrules import PloneMessageFactory as _
from plone.app.contentrules.rule import Rule
from plone.app.contentrules.browser.formhelper import AddForm
from plone.app.contentrules.browser.formhelper import EditForm
from plone.app.contentrules.browser.formhelper import ContentRuleFormWrapper

from z3c.form.form import applyChanges


class RuleAddForm(AddForm):
    """An add form for rules.
    """
    schema = IRuleConfiguration
    ignoreContext = True
    label = _(u"Add Rule")
    description = _(u"Add a new rule. Once complete, you can manage the "
                    "rule's actions and conditions separately.")

    def nextURL(self):
        context = aq_parent(aq_inner(self.context))
        url = str(getMultiAdapter((context, self.request), name=u"absolute_url"))
        if base_hasattr(self.context, '_chosen_name'):
            return '%s/++rule++%s/@@manage-elements' % (url, self.context._chosen_name)
        else:
            return '%s/@@rules-controlpanel' % url

    def create(self, data):
        rule = Rule()
        applyChanges(self, rule, data)
        return rule


class RuleAddFormView(ContentRuleFormWrapper):
    form = RuleAddForm


class RuleEditForm(EditForm):
    """An edit form for rules.
    """
    schema = IRuleConfiguration
    label = _(u"Edit Rule")
    description = _(u"Edit an existing rule.")

    def nextURL(self):
        context = aq_parent(aq_inner(self.context))
        url = str(getMultiAdapter((context, self.request), name=u"absolute_url"))
        return url + '/@@rules-controlpanel'


class RuleEditFormView(ContentRuleFormWrapper):
    form = RuleEditForm