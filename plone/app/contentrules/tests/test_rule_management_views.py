from zope.component import getMultiAdapter, getUtility
from zope.lifecycleevent.interfaces import IObjectModifiedEvent

from plone.contentrules.engine.interfaces import IRuleStorage

from plone.app.contentrules.rule import Rule
from plone.app.contentrules.browser.rule import RuleEditForm

from plone.app.contentrules.tests.base import ContentRulesTestCase

from dummy import DummyCondition, DummyAction


class DummyModifiedRule(Rule):

    title = "My test rule"
    description = "Test my rule"
    event = IObjectModifiedEvent
    enabled = True


class TestRuleManagementViews(ContentRulesTestCase):

    def afterSetUp(self):
        self.setRoles(('Manager', ))

    def testRuleAdding(self):
        adding = getMultiAdapter((self.portal, self.portal.REQUEST), name='+rule')
        storage = getUtility(IRuleStorage)
        self.assertEquals(0, len(storage))
        r = Rule()
        adding.add(r)
        self.assertEquals(1, len(storage))
        self.failUnless(storage.values()[0] is r)

    def testRuleAddView(self):
        adding = getMultiAdapter((self.portal, self.portal.REQUEST), name='+rule')
        addview = getMultiAdapter((adding, self.portal.REQUEST), name='plone.ContentRule')
        storage = getUtility(IRuleStorage)
        self.assertEquals(0, len(storage))
        addview.createAndAdd({'title': 'foo', 'description': 'bar', 'event': None})
        self.assertEquals(1, len(storage))
        self.assertEquals('foo', storage.values()[0].title)

    def testRuleEditView(self):
        r = Rule()
        editview = getMultiAdapter((r, self.portal.REQUEST), name='edit')
        self.failUnless(isinstance(editview, RuleEditForm))


class TestRuleElementManagementViews(ContentRulesTestCase):

    def afterSetUp(self):
        self.setRoles(('Manager', ))

    def testRuleStopModification(self):
        storage = getUtility(IRuleStorage)
        storage[u'foo'] = Rule()

        rule = self.portal.restrictedTraverse('++rule++foo')
        view = rule.restrictedTraverse("manage-elements")
        view.template = lambda: "No template thanks"

        self.portal.REQUEST.form['stopExecuting'] = 'on'
        self.portal.REQUEST.form['form.button.Save'] = True


        self.assertEquals(False, rule.stop)
        view()
        self.assertEquals(True, rule.stop)

    def testRuleConditionAdding(self):
        storage = getUtility(IRuleStorage)
        storage[u'foo'] = Rule()
        rule = self.portal.restrictedTraverse('++rule++foo')
        adding = getMultiAdapter((rule, self.portal.REQUEST), name='+condition')
        d = DummyCondition()
        self.assertEquals(0, len(rule.conditions))
        adding.add(d)
        self.assertEquals(1, len(rule.conditions))
        self.failUnless(rule.conditions[0] is d)

    def testRuleActionAdding(self):
        storage = getUtility(IRuleStorage)
        storage[u'foo'] = Rule()
        rule = self.portal.restrictedTraverse('++rule++foo')
        adding = getMultiAdapter((rule, self.portal.REQUEST), name='+action')
        d = DummyAction()
        self.assertEquals(0, len(rule.actions))
        adding.add(d)
        self.assertEquals(1, len(rule.actions))
        self.failUnless(rule.actions[0] is d)

    def testRulesControlPanel(self):
        storage = getUtility(IRuleStorage)
        storage[u'foo'] = DummyModifiedRule()
        controlpanel = self.portal.restrictedTraverse('@@rules-controlpanel')
        registered_rules = controlpanel.registeredRules()
        self.assertEquals(1, len(registered_rules))
        registered_rule = registered_rules[0]
        self.assertEquals(registered_rule['row_class'],
                          'trigger-iobjectmodifiedevent state-enabled')
        self.assertEquals(registered_rule['trigger'],
                          'Object modified')
        self.assertTrue(registered_rule['enabled'])
        self.assertFalse(registered_rule['assigned'])

        rule_types = controlpanel.ruleTypesToShow()
        rule_types_ids = [r['id'] for r in rule_types]
        self.assertIn('trigger-iobjectmodifiedevent', rule_types_ids)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestRuleManagementViews))
    suite.addTest(makeSuite(TestRuleElementManagementViews))
    return suite
