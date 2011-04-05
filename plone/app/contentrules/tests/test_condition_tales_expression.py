from zope.interface import implements
from zope.component import getUtility, getMultiAdapter

from zope.component.interfaces import IObjectEvent

from plone.contentrules.engine.interfaces import IRuleStorage
from plone.contentrules.rule.interfaces import IRuleCondition
from plone.contentrules.rule.interfaces import IExecutable

from plone.app.contentrules.conditions.talesexpression import TalesExpressionCondition
from plone.app.contentrules.conditions.talesexpression import TalesExpressionEditForm

from plone.app.contentrules.rule import Rule

from plone.app.contentrules.tests.base import ContentRulesTestCase


class DummyEvent(object):
    implements(IObjectEvent)

    def __init__(self, obj):
        self.object = obj


class TestTalesExpressionCondition(ContentRulesTestCase):

    def afterSetUp(self):
        self.setRoles(('Manager', ))

    def testRegistered(self):
        element = getUtility(IRuleCondition, name='plone.conditions.TalesExpression')
        self.assertEquals('plone.conditions.TalesExpression', element.addview)
        self.assertEquals('edit', element.editview)
        self.assertEquals(None, element.for_)
        self.assertEquals(IObjectEvent, element.event)

    def testInvokeAddView(self):
        element = getUtility(IRuleCondition, name='plone.conditions.TalesExpression')
        storage = getUtility(IRuleStorage)
        storage[u'foo'] = Rule()
        rule = self.portal.restrictedTraverse('++rule++foo')

        adding = getMultiAdapter((rule, self.portal.REQUEST), name='+condition')
        addview = getMultiAdapter((adding, self.portal.REQUEST), name=element.addview)

        addview.createAndAdd(data={'tales_expression': 'python:"plone" in object.Subject()'})

        e = rule.conditions[0]
        self.failUnless(isinstance(e, TalesExpressionCondition))
        self.assertEquals('python:"plone" in object.Subject()', e.tales_expression)

    def testInvokeEditView(self):
        element = getUtility(IRuleCondition, name='plone.conditions.TalesExpression')
        e = TalesExpressionCondition()
        editview = getMultiAdapter((e, self.folder.REQUEST), name=element.editview)
        self.failUnless(isinstance(editview, TalesExpressionEditForm))

    def testExecute(self):
        e = TalesExpressionCondition()
        e.tales_expression = 'python:"plone" in object.Subject()'

        ex = getMultiAdapter((self.portal, e, DummyEvent(self.folder)), IExecutable)
        self.assertEquals(False, ex())

        ex = getMultiAdapter((self.portal, e, DummyEvent(self.portal)), IExecutable)
        self.assertEquals(False, ex())

        self.folder.setSubject(('plone', 'contentrules'))
        ex = getMultiAdapter((self.portal, e, DummyEvent(self.folder)), IExecutable)
        self.assertEquals(True, ex())


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestTalesExpressionCondition))
    return suite
