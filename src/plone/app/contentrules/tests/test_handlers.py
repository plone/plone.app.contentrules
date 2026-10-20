from plone.app.contentrules import api
from plone.app.contentrules import handlers
from plone.app.contentrules.actions.logger import LoggerAction
from plone.app.contentrules.rule import Rule
from plone.app.contentrules.tests import dummy
from plone.app.contentrules.tests.base import ContentRulesTestCase
from plone.contentrules.engine.interfaces import IRuleStorage
from zope.component import getUtility
from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent
from zope.lifecycleevent import ObjectModifiedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent

import logging


class TestDuplicateRuleFilter(ContentRulesTestCase):
    def setUp(self):
        super().setUp()
        self.context = self.folder
        self.event = dummy.DummyEvent(self.context)
        self.rulefilter = handlers.DuplicateRuleFilter()
        self.rule = dummy.DummyRule()
        self.uuidaware = dummy.DummyNonArchetypesContext()
        notify(ObjectCreatedEvent(self.uuidaware))

    def test_call_archetypescontext(self):
        to_execute = self.rulefilter(self.context, self.rule, self.event)
        self.assertTrue(to_execute)
        to_execute = self.rulefilter(self.context, self.rule, self.event)
        self.assertTrue(not to_execute)

    def test_call_two_events_in_same_context(self):
        # if events on two different objects are handled in the same context,
        # they are not filtered
        to_execute = self.rulefilter(self.context, self.rule, self.event)
        self.assertTrue(to_execute)
        self.portal.invokeFactory("Folder", "folder2")
        event2 = dummy.DummyEvent(self.portal.folder2)
        to_execute = self.rulefilter(self.context, self.rule, event2)
        self.assertTrue(to_execute)

    def test_call_uuidaware(self):
        to_execute = self.rulefilter(self.uuidaware, self.rule, self.event)
        self.assertTrue(to_execute)
        to_execute = self.rulefilter(self.uuidaware, self.rule, self.event)
        self.assertTrue(not to_execute)


SITE_ROOT_LOGGER = "plone.app.contentrules.tests.siteroot"


class TestSiteRootModified(ContentRulesTestCase):
    """A rule assigned at the site root should fire when the site root is edited.

    This is not a corner case. In a Volto/Plone 6 site the homepage IS the site
    root: its blocks live on the portal object, and plone.restapi's site-root
    deserializer notifies ObjectModifiedEvent on the portal when they change.
    So the single most frequently edited page on such a site is the one page
    whose edits never run a rule.

    Each test below asserts the SAME rule with the SAME assignment, once
    against ordinary content and once against the site root, so a failure can
    only be about the site root and not about the wiring.
    """

    def setUp(self):
        super().setUp()
        storage = getUtility(IRuleStorage)
        rule = Rule()
        rule.event = IObjectModifiedEvent
        action = LoggerAction()
        action.targetLogger = SITE_ROOT_LOGGER
        action.loggingLevel = logging.INFO
        action.message = "rule fired for &c"
        rule.actions.append(action)
        storage["siteroot-rule"] = rule
        api.assign_rule(self.portal, "siteroot-rule", enabled=True, bubbles=True)

    def test_rule_fires_for_content_in_the_site_root(self):
        with self.assertLogs(SITE_ROOT_LOGGER, level="INFO") as captured:
            notify(ObjectModifiedEvent(self.folder))
        self.assertIn("rule fired for", captured.output[0])

    def test_rule_fires_for_the_site_root_itself(self):
        with self.assertLogs(SITE_ROOT_LOGGER, level="INFO") as captured:
            notify(ObjectModifiedEvent(self.portal))
        self.assertIn("rule fired for", captured.output[0])
