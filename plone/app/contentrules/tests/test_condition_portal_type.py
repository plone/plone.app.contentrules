# -*- coding: utf-8 -*-
from zope.interface import implementer
from zope.component import getUtility, getMultiAdapter

from zope.component.interfaces import IObjectEvent

from plone.contentrules.engine.interfaces import IRuleStorage
from plone.contentrules.rule.interfaces import IRuleCondition
from plone.contentrules.rule.interfaces import IExecutable

from plone.app.contentrules.conditions.portaltype import PortalTypeCondition
from plone.app.contentrules.conditions.portaltype import PortalTypeEditFormView

from plone.app.contentrules.rule import Rule

from plone.app.contentrules.tests.base import ContentRulesTestCase


@implementer(IObjectEvent)
class DummyEvent(object):

    def __init__(self, obj):
        self.object = obj


class TestPortalTypeCondition(ContentRulesTestCase):

    def afterSetUp(self):
        self.setRoles(('Manager', ))

    def testRegistered(self):
        element = getUtility(IRuleCondition, name='plone.conditions.PortalType')
        self.assertEqual('plone.conditions.PortalType', element.addview)
        self.assertEqual('edit', element.editview)
        self.assertEqual(None, element.for_)
        self.assertEqual(IObjectEvent, element.event)

    def testInvokeAddView(self):
        element = getUtility(IRuleCondition, name='plone.conditions.PortalType')
        storage = getUtility(IRuleStorage)
        storage[u'foo'] = Rule()
        rule = self.portal.restrictedTraverse('++rule++foo')

        adding = getMultiAdapter((rule, self.portal.REQUEST), name='+condition')
        addview = getMultiAdapter((adding, self.portal.REQUEST), name=element.addview)

        addview.form_instance.update()
        content = addview.form_instance.create(data={'check_types': ['Folder', 'Image']})
        addview.form_instance.add(content)

        e = rule.conditions[0]
        self.assertTrue(isinstance(e, PortalTypeCondition))
        self.assertEqual(['Folder', 'Image'], e.check_types)

    def testInvokeEditView(self):
        element = getUtility(IRuleCondition, name='plone.conditions.PortalType')
        e = PortalTypeCondition()
        editview = getMultiAdapter((e, self.folder.REQUEST), name=element.editview)
        self.assertTrue(isinstance(editview, PortalTypeEditFormView))

    def testExecute(self):
        e = PortalTypeCondition()
        e.check_types = ['Folder', 'Image']

        ex = getMultiAdapter((self.portal, e, DummyEvent(self.folder)), IExecutable)
        self.assertTrue(ex())

        ex = getMultiAdapter((self.portal, e, DummyEvent(self.portal)), IExecutable)
        self.assertFalse(ex())

        self.folder.portal_types = None
        ex = getMultiAdapter((self.portal, e, DummyEvent(self.folder)), IExecutable)
        self.assertFalse(ex())
