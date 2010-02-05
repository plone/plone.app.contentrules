from zope.component import getMultiAdapter, getUtility

from plone.contentrules.engine.interfaces import IRuleStorage

from plone.app.contentrules.rule import Rule
from plone.app.contentrules.browser.rule import RuleEditForm

from plone.app.contentrules.tests.base import ContentRulesTestCase

from dummy import DummyCondition, DummyAction


class TestRuleManagementViews(ContentRulesTestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))

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
        addview.createAndAdd({'title' : 'foo', 'description' : 'bar', 'event' : None})
        self.assertEquals(1, len(storage))
        self.assertEquals('foo', storage.values()[0].title)
        
    def testRuleEditView(self): 
        r = Rule()
        editview = getMultiAdapter((r, self.portal.REQUEST), name='edit')
        self.failUnless(isinstance(editview, RuleEditForm))

class TestRuleElementManagementViews(ContentRulesTestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))

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
        
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestRuleManagementViews))
    suite.addTest(makeSuite(TestRuleElementManagementViews))
    return suite
