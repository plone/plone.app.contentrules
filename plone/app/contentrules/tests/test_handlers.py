from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent

from plone.app.contentrules.tests import base
from plone.app.contentrules.tests import dummy
from plone.app.contentrules import handlers


class TestDuplicateRuleFilter(base.ContentRulesTestCase):

    def setUp(self):
        super(TestDuplicateRuleFilter, self).setUp()
        self.setRoles(('Manager',))
        self.context = self.folder
        self.event = dummy.DummyEvent(self.context)
        self.rulefilter = handlers.DuplicateRuleFilter()
        self.rule = dummy.DummyRule()
        self.uuidaware = dummy.DummyNonArchetypesContext()
        notify(ObjectCreatedEvent(self.uuidaware))

    def test_call_archetypescontext(self):
        to_execute = self.rulefilter(self.context, self.rule, self.event)
        self.failUnless(to_execute)
        to_execute = self.rulefilter(self.context, self.rule, self.event)
        self.failUnless(not to_execute)

    def test_call_uuidaware(self):
        to_execute = self.rulefilter(self.uuidaware, self.rule, self.event)
        self.failUnless(to_execute)
        to_execute = self.rulefilter(self.uuidaware, self.rule, self.event)
        self.failUnless(not to_execute)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestDuplicateRuleFilter))
    return suite
