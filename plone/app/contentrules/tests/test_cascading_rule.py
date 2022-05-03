from plone.app.contentrules.api import edit_rule_assignment
from plone.app.contentrules.testing import PLONE_APP_CONTENTRULES_FUNCTIONAL_TESTING
from plone.app.testing import applyProfile
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.dexterity.utils import createContentInContainer

import unittest


class TestCascadingRule(unittest.TestCase):

    layer = PLONE_APP_CONTENTRULES_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        login(self.portal, TEST_USER_NAME)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.portal.invokeFactory("Folder", "news")
        self.portal.invokeFactory("Folder", "events")

        applyProfile(self.portal, "plone.app.contentrules:testing")
        edit_rule_assignment(self.portal, "test4", bubbles=1, enabled=1)
        edit_rule_assignment(self.portal, "test5", bubbles=1, enabled=1)

    def test_cascading_rule(self):
        # check that test2 rule and test4 rule are executed
        # test2 rule publishes the event in news folder
        # test4 rule moves it in events folder when it is published

        createContentInContainer(self.portal.news, "Event", id="my-event")
        self.assertFalse("my-event" in self.portal.news)
        self.assertTrue("my-event" in self.portal.events)

        wtool = self.portal.portal_workflow
        self.assertEqual(
            wtool.getInfoFor(self.portal.events["my-event"], "review_state"),
            "published",
        )
