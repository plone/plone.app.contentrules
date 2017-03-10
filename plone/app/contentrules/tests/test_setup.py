# -*- coding: utf-8 -*-
from plone.app.contentrules.tests.base import ContentRulesTestCase
from plone.contentrules.engine.interfaces import IRuleAssignable
from plone.contentrules.rule.interfaces import IRuleEventType
from zope.lifecycleevent.interfaces import IObjectAddedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from zope.lifecycleevent.interfaces import IObjectRemovedEvent


class TestProductInstall(ContentRulesTestCase):

    def testRuleContainerInterfaces(self):
        self.assertTrue(IRuleAssignable.providedBy(self.folder))
        self.assertTrue(IRuleAssignable.providedBy(self.portal))

    def testEventTypesMarked(self):
        self.assertTrue(IRuleEventType.providedBy(IObjectAddedEvent))
        self.assertTrue(IRuleEventType.providedBy(IObjectModifiedEvent))
        self.assertTrue(IRuleEventType.providedBy(IObjectRemovedEvent))
