from zope.interface import implements, Interface
from zope.component import getUtility, getMultiAdapter
from zope.component.interfaces import IObjectEvent

from plone.contentrules.engine.interfaces import IRuleStorage
from plone.contentrules.rule.interfaces import IRuleAction
from plone.contentrules.rule.interfaces import IExecutable

from plone.app.contentrules.actions.logger import LoggerAction
from plone.app.contentrules.actions.logger import LoggerEditForm

from plone.app.contentrules.rule import Rule

from plone.app.contentrules.tests.base import ContentRulesTestCase


class DummyEvent(object):
    implements(Interface)


class DummyObjectEvent(object):
    implements(IObjectEvent)

    def __init__(self, obj):
        self.object = obj

    pass


class TestLoggerAction(ContentRulesTestCase):

    def afterSetUp(self):
        self.setRoles(('Manager', ))

    def testRegistered(self):
        element = getUtility(IRuleAction, name='plone.actions.Logger')
        self.assertEquals('plone.actions.Logger', element.addview)
        self.assertEquals('edit', element.editview)
        self.assertEquals(None, element.for_)
        self.assertEquals(None, element.event)

    def testInvokeAddView(self):
        element = getUtility(IRuleAction, name='plone.actions.Logger')
        storage = getUtility(IRuleStorage)
        storage[u'foo'] = Rule()
        rule = self.portal.restrictedTraverse('++rule++foo')

        adding = getMultiAdapter((rule, self.portal.REQUEST), name='+action')
        addview = getMultiAdapter((adding, self.portal.REQUEST), name=element.addview)

        addview.createAndAdd(data={'targetLogger': 'foo', 'loggingLevel': 10, 'message': 'bar'})

        e = rule.actions[0]
        self.failUnless(isinstance(e, LoggerAction))
        self.assertEquals('foo', e.targetLogger)
        self.assertEquals(10, e.loggingLevel)
        self.assertEquals('bar', e.message)

    def testInvokeEditView(self):
        element = getUtility(IRuleAction, name='plone.actions.Logger')
        e = LoggerAction()
        editview = getMultiAdapter((e, self.folder.REQUEST), name=element.editview)
        self.failUnless(isinstance(editview, LoggerEditForm))

    def testProcessedMessage(self):
        e = LoggerAction()
        e.targetLogger = 'testing'
        e.loggingLevel = 0
        e.message = "Test log event"
        ex = getMultiAdapter((self.folder, e, DummyObjectEvent(self.folder)), IExecutable)
        self.assertEquals("Test log event", ex.processedMessage())

        e.message = "Test log event : &c"
        self.assertEquals("Test log event : <ATFolder at /plone/Members/test_user_1_>",
                          ex.processedMessage())

        e.message = "Test log event : &e"
        self.assertEquals("Test log event : plone.app.contentrules.tests.test_action_logger.DummyObjectEvent",
                          ex.processedMessage())

        e.message = "Test log event : &u"
        self.assertEquals("Test log event : test_user_1_", ex.processedMessage())

    def testExecute(self):
        e = LoggerAction()
        e.targetLogger = 'testing'
        e.loggingLevel = 0
        e.message = "Test log event"
        ex = getMultiAdapter((self.folder, e, DummyEvent()), IExecutable)
        self.assertEquals(True, ex())


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestLoggerAction))
    return suite
