from Acquisition import Explicit

from zope.component import getMultiAdapter

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
        adding = getMultiAdapter((self.folder, self.folder.REQUEST), name='+rule')
        storage = IRuleStorage(self.folder)
        self.assertEquals(0, len(storage))
        r = Rule()
        adding.add(r)
        self.assertEquals(1, len(storage))
        self.failUnless(storage.values()[0] is r)

    def testRuleAddView(self): 
        adding = getMultiAdapter((self.folder, self.folder.REQUEST), name='+rule')
        addview = getMultiAdapter((adding, self.folder.REQUEST), name='plone.ContentRule')
        storage = IRuleStorage(self.folder)
        self.assertEquals(0, len(storage))
        addview.createAndAdd({'title' : 'foo', 'description' : 'bar', 'event' : None})
        self.assertEquals(1, len(storage))
        self.assertEquals('foo', storage.values()[0].title)
        
    def testRuleEditView(self): 
        r = Rule()
        editview = getMultiAdapter((r, self.folder.REQUEST), name='edit.html')
        self.failUnless(isinstance(editview, RuleEditForm))

    def testDeleteRule(self): 
        storage = IRuleStorage(self.folder)
        storage[u'foo'] = Rule()
        rule = self.folder.restrictedTraverse('++rule++foo')
        deleteview = getMultiAdapter((rule, self.folder.REQUEST), name='delete-rule')
        deleteview()
        self.assertEquals(0, len(storage))

class TestRuleElementManagementViews(ContentRulesTestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))

    def testRuleElementAdding(self): 
        storage = IRuleStorage(self.folder)
        storage[u'foo'] = Rule()
        rule = self.folder.restrictedTraverse('++rule++foo')
        adding = getMultiAdapter((rule, self.folder.REQUEST), name='+')
        n = Node('foo', Dummy())
        self.assertEquals(0, len(rule.elements))
        adding.add(n)
        self.assertEquals(1, len(rule.elements))
        self.failUnless(rule.elements[0] is n)
        
    def testDeleteElement(self):
        storage = IRuleStorage(self.folder)
        r = Rule()
        r.elements.append(Node('foo', Dummy()))
        storage[u'foo'] = r
        rule = self.folder.restrictedTraverse('++rule++foo')
        request = self.folder.REQUEST
        request.set('id', 0)
        deleteview = getMultiAdapter((rule, request), name='delete-element')
        self.assertEquals(1, len(r.elements))
        deleteview()
        self.assertEquals(0, len(r.elements))
        
    def testMoveElementUp(self): 
        storage = IRuleStorage(self.folder)
        r = Rule()
        n1 = Node('foo', Dummy())
        n2 = Node('bar', Dummy())
        r.elements += [n1, n2]
        storage[u'foo'] = r
        rule = self.folder.restrictedTraverse('++rule++foo')
        request = self.folder.REQUEST
        request.set('id', 1)
        moveview = getMultiAdapter((rule, request), name='move-element-up')
        self.failUnless(r.elements[0] is n1)
        self.failUnless(r.elements[1] is n2)
        moveview()
        self.failUnless(r.elements[0] is n2)
        self.failUnless(r.elements[1] is n1)

    def testMoveElementDown(self): 
        storage = IRuleStorage(self.folder)
        r = Rule()
        n1 = Node('foo', Dummy())
        n2 = Node('bar', Dummy())
        r.elements += [n1, n2]
        storage[u'foo'] = r
        rule = self.folder.restrictedTraverse('++rule++foo')
        request = self.folder.REQUEST
        request.set('id', 0)
        moveview = getMultiAdapter((rule, request), name='move-element-down')
        self.failUnless(r.elements[0] is n1)
        self.failUnless(r.elements[1] is n2)
        moveview()
        self.failUnless(r.elements[0] is n2)
        self.failUnless(r.elements[1] is n1)
        
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestRuleManagementViews))
    suite.addTest(makeSuite(TestRuleElementManagementViews))
    return suite
