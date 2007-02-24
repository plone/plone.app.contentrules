from zope.component import getMultiAdapter, getUtility
from zope.publisher.interfaces.browser import IBrowserPublisher

from Acquisition import aq_base, aq_parent, Explicit

from plone.contentrules.engine.interfaces import IRuleStorage
from plone.contentrules.rule.rule import Node

from plone.app.contentrules.rule import Rule
from plone.app.contentrules.tests.base import ContentRulesTestCase

class Dummy(Explicit):
    pass

class TestTraversal(ContentRulesTestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))

    def testTraverseToRule(self):
        r = Rule()
        storage = getUtility(IRuleStorage)
        storage[u'r1'] = r
        traversed = self.portal.restrictedTraverse('++rule++r1')
        self.failUnless(aq_parent(traversed) is self.portal)
        self.failUnless(aq_base(traversed) is r)
    
    def testTraverseToRuleElement(self): 
        r = Rule()
        e1 = Dummy()
        e2 = Dummy()
        r.elements.append(Node('dummy', e1))
        r.elements.append(Node('dummy', e2))
        storage = getUtility(IRuleStorage)
        storage[u'r1'] = r
        
        tr = self.portal.restrictedTraverse('++rule++r1')
        
        request = self.folder.REQUEST
        publisher = getMultiAdapter((tr, request), IBrowserPublisher)
        
        te1 = publisher.publishTraverse(request, '0')
        te2 = publisher.publishTraverse(request, '1')
        
        self.failUnless(aq_parent(te1) is tr)
        self.failUnless(aq_base(te1) is e1)
        
        self.failUnless(aq_parent(te2) is tr)
        self.failUnless(aq_base(te2) is e2)
        
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestTraversal))
    return suite
