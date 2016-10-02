# -*- coding: utf-8 -*-
from zope.interface import implementer, Interface
from zope.component import getUtility, getMultiAdapter

from plone.contentrules.engine.interfaces import IRuleStorage
from plone.contentrules.rule.interfaces import IRuleAction
from plone.contentrules.rule.interfaces import IExecutable

from plone.app.contentrules.actions.notify import NotifyAction
from plone.app.contentrules.actions.notify import NotifyEditFormView

from plone.app.contentrules.rule import Rule

from plone.app.contentrules.tests.base import ContentRulesTestCase

from Products.statusmessages import STATUSMESSAGEKEY
from Products.statusmessages.adapter import _decodeCookieValue


@implementer(Interface)
class DummyEvent(object):
    pass


class TestNotifyAction(ContentRulesTestCase):

    def afterSetUp(self):
        self.setRoles(('Manager', ))
        self.request = self.layer['request']

    def testRegistered(self):
        element = getUtility(IRuleAction, name='plone.actions.Notify')
        self.assertEqual('plone.actions.Notify', element.addview)
        self.assertEqual('edit', element.editview)
        self.assertEqual(None, element.for_)
        self.assertEqual(None, element.event)

    def testInvokeAddView(self):
        element = getUtility(IRuleAction, name='plone.actions.Notify')
        storage = getUtility(IRuleStorage)
        storage[u'foo'] = Rule()
        rule = self.portal.restrictedTraverse('++rule++foo')

        adding = getMultiAdapter((rule, self.request), name='+action')
        addview = getMultiAdapter((adding, self.request), name=element.addview)

        addview.form_instance.update()
        content = addview.form_instance.create(data={'message': 'Hello world',
                                                     'message_type': 'info'})
        addview.form_instance.add(content)

        e = rule.actions[0]
        self.assertTrue(isinstance(e, NotifyAction))
        self.assertEqual('Hello world', e.message)
        self.assertEqual('info', e.message_type)

    def testInvokeEditView(self):
        element = getUtility(IRuleAction, name='plone.actions.Notify')
        e = NotifyAction()
        editview = getMultiAdapter((e, self.request), name=element.editview)
        self.assertTrue(isinstance(editview, NotifyEditFormView))

    def testExecute(self):
        e = NotifyAction()
        e.message = 'Hello world'
        e.message_type = 'info'

        ex = getMultiAdapter((self.folder, e, DummyEvent()), IExecutable)
        self.assertEqual(True, ex())

        new_cookies = self.request.RESPONSE.cookies[STATUSMESSAGEKEY]
        messages = _decodeCookieValue(new_cookies['value'])
        self.assertEqual(1, len(messages))
        self.assertEqual('Hello world', messages[0].message)
        self.assertEqual('info', messages[0].type)
