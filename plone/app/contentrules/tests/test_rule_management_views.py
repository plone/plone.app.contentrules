from Acquisition import Explicit

from zope.component import getMultiAdapter, getUtility

from zope.publisher.interfaces.browser import IBrowserPublisher

from plone.contentrules.engine.interfaces import IRuleStorage
from plone.contentrules.rule.rule import Node

from plone.app.contentrules.rule import Rule
from plone.app.contentrules.browser.rule import RuleEditForm

from plone.app.contentrules.tests.base import ContentRulesTestCase

class Dummy(Explicit):
    pass

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
        editview = getMultiAdapter((r, self.portal.REQUEST), name='edit.html')
        self.failUnless(isinstance(editview, RuleEditForm))

class TestRuleElementManagementViews(ContentRulesTestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))

    def testRuleElementAdding(self): 
        storage = getUtility(IRuleStorage)
        storage[u'foo'] = Rule()
        rule = self.portal.restrictedTraverse('++rule++foo')
        adding = getMultiAdapter((rule, self.portal.REQUEST), name='+')
        n = Node('foo', Dummy())
        self.assertEquals(0, len(rule.elements))
        adding.add(n)
        self.assertEquals(1, len(rule.elements))
        self.failUnless(rule.elements[0] is n)
        
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestRuleManagementViews))
    suite.addTest(makeSuite(TestRuleElementManagementViews))
    return suite
