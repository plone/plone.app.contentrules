# -*- coding: utf-8 -*-
from zope.interface import implementer, Interface
from zope.component import getUtility, getMultiAdapter
from zope.component.interfaces import IObjectEvent

from plone.contentrules.engine.interfaces import IRuleStorage
from plone.contentrules.rule.interfaces import IRuleAction
from plone.contentrules.rule.interfaces import IExecutable

from plone.app.contentrules.actions.logger import LoggerAction
from plone.app.contentrules.actions.logger import LoggerEditFormView

from plone.app.contentrules.rule import Rule

from plone.app.contentrules.tests.base import ContentRulesTestCase
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME


@implementer(Interface)
class DummyEvent(object):
    pass


@implementer(IObjectEvent)
class DummyObjectEvent(object):

    def __init__(self, obj):
        self.object = obj


class TestLoggerAction(ContentRulesTestCase):

    def afterSetUp(self):
        self.setRoles(('Manager', ))

    def testRegistered(self):
        element = getUtility(IRuleAction, name='plone.actions.Logger')
        self.assertEqual('plone.actions.Logger', element.addview)
        self.assertEqual('edit', element.editview)
        self.assertEqual(None, element.for_)
        self.assertEqual(None, element.event)

    def testInvokeAddView(self):
        element = getUtility(IRuleAction, name='plone.actions.Logger')
        storage = getUtility(IRuleStorage)
        storage[u'foo'] = Rule()
        rule = self.portal.restrictedTraverse('++rule++foo')

        adding = getMultiAdapter((rule, self.portal.REQUEST), name='+action')
        addview = getMultiAdapter((adding, self.portal.REQUEST), name=element.addview)

        addview.form_instance.update()
        content = addview.form_instance.create(data={'targetLogger': 'foo', 'loggingLevel': 10, 'message': 'bar'})
        addview.form_instance.add(content)

        e = rule.actions[0]
        self.assertTrue(isinstance(e, LoggerAction))
        self.assertEqual('foo', e.targetLogger)
        self.assertEqual(10, e.loggingLevel)
        self.assertEqual('bar', e.message)

    def testInvokeEditView(self):
        element = getUtility(IRuleAction, name='plone.actions.Logger')
        e = LoggerAction()
        editview = getMultiAdapter((e, self.folder.REQUEST), name=element.editview)
        self.assertTrue(isinstance(editview, LoggerEditFormView))

    def testProcessedMessage(self):
        e = LoggerAction()
        e.targetLogger = 'testing'
        e.loggingLevel = 0
        e.message = "Test log event"
        ex = getMultiAdapter((self.folder, e, DummyObjectEvent(self.folder)), IExecutable)
        self.assertEqual("Test log event", ex.processedMessage())

        e.message = "Test log event : &c"
        self.assertEqual("Test log event : <ATFolder at /plone/Members/%s>" % TEST_USER_ID,
                         ex.processedMessage())

        e.message = "Test log event : &e"
        self.assertEqual(
            "Test log event : plone.app.contentrules.tests.test_action_logger.DummyObjectEvent",
            ex.processedMessage())

        e.message = "Test log event : &u"
        self.assertEqual("Test log event : %s" % TEST_USER_NAME, ex.processedMessage())

    def testExecute(self):
        e = LoggerAction()
        e.targetLogger = 'testing'
        e.loggingLevel = 0
        e.message = "Test log event"
        ex = getMultiAdapter((self.folder, e, DummyEvent()), IExecutable)
        self.assertTrue(ex())
