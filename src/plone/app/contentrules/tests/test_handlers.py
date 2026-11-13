from plone.app.contentrules import api
from plone.app.contentrules import handlers
from plone.app.contentrules.actions.logger import LoggerAction
from plone.app.contentrules.rule import Rule
from plone.app.contentrules.tests import dummy
from plone.app.contentrules.tests.base import ContentRulesTestCase
from plone.contentrules.engine.interfaces import IRuleStorage
from zope.component import getUtility
from zope.container.contained import ContainerModifiedEvent
from zope.container.interfaces import IContainerModifiedEvent
from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent
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


CONTAINER_LOGGER = "plone.app.contentrules.tests.container"


class TestContainerModified(ContentRulesTestCase):
    """A reorder is observable only as IContainerModifiedEvent.

    `plone.folder` calls `notifyContainerModified` when a folder's membership or
    ordering changes. For an add or a remove that arrives alongside a more
    specific event, so a rule can already see it. A REORDER emits nothing else:
    no add, no remove, no move. Today no rule can observe one at all.

    `modified()` has excluded IContainerModifiedEvent since 2012, so that adding
    a comment to a page does not fire "modified" rules registered on that page.
    That exclusion is right and these tests pin it: a rule that asks for
    IObjectModifiedEvent must still not run for a container event, even once a
    rule CAN ask for the container event directly.
    """

    def _rule(self, name, event_iface, message):
        storage = getUtility(IRuleStorage)
        rule = Rule()
        rule.event = event_iface
        action = LoggerAction()
        action.targetLogger = CONTAINER_LOGGER
        action.loggingLevel = logging.INFO
        action.message = message
        rule.actions.append(action)
        storage[name] = rule
        api.assign_rule(self.folder, name, enabled=True, bubbles=True)

    def setUp(self):
        super().setUp()
        self._rule("container-rule", IContainerModifiedEvent, "container rule fired")
        self._rule("modified-rule", IObjectModifiedEvent, "modified rule fired")

    def test_a_rule_can_subscribe_to_the_container_event(self):
        with self.assertLogs(CONTAINER_LOGGER, level="INFO") as captured:
            notify(ContainerModifiedEvent(self.folder))
        self.assertTrue(
            any("container rule fired" in line for line in captured.output),
            captured.output,
        )

    def test_the_container_event_does_not_run_modified_rules(self):
        # The 2012 behaviour, kept: a container event means "my children
        # changed", not "my fields changed".
        with self.assertLogs(CONTAINER_LOGGER, level="INFO") as captured:
            notify(ContainerModifiedEvent(self.folder))
        self.assertFalse(
            any("modified rule fired" in line for line in captured.output),
            captured.output,
        )

    def test_adding_content_is_not_a_reorder(self):
        # zope.container fires ObjectAdded and THEN notifyContainerModified on
        # the same container. The add claims that container event, so a rule
        # watching for reordering does not fire on it.
        with self.assertNoLogs(CONTAINER_LOGGER, level="INFO"):
            self.folder.invokeFactory("Document", "added-doc")

    def test_removing_content_is_not_a_reorder(self):
        self.folder.invokeFactory("Document", "doomed")
        with self.assertNoLogs(CONTAINER_LOGGER, level="INFO"):
            self.folder.manage_delObjects(["doomed"])
