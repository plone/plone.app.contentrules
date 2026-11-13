from plone.app.contentrules.testing import PLONE_APP_CONTENTRULES_INTEGRATION_TESTING
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.base.utils import get_installer
from plone.browserlayer.utils import registered_layers
from plone.contentrules.engine.interfaces import IRuleStorage
from plone.contentrules.rule.rule import Rule
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.publisher.browser import TestRequest
from zope.traversing.interfaces import ITraversable

import unittest

LAYERED_SITE_VIEWS = (
    "+rule",
    "rules-controlpanel",
    "manage-content-rules",
    "contentrule-enable",
    "contentrule-disable",
    "contentrule-delete",
    "contentrule-globally-enable",
    "contentrule-globally-disable",
)


class TestBrowserLayer(unittest.TestCase):
    layer = PLONE_APP_CONTENTRULES_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def test_views_available_with_layer(self):
        for name in LAYERED_SITE_VIEWS:
            self.assertIsNotNone(
                queryMultiAdapter((self.portal, self.request), name=name), name
            )

    def test_views_missing_without_layer(self):
        request = TestRequest()
        for name in LAYERED_SITE_VIEWS:
            self.assertIsNone(
                queryMultiAdapter((self.portal, request), name=name), name
            )

    def test_rule_namespace_needs_layer(self):
        self.assertIsNotNone(
            queryMultiAdapter((self.portal, self.request), ITraversable, name="rule")
        )
        self.assertIsNone(
            queryMultiAdapter((self.portal, TestRequest()), ITraversable, name="rule")
        )

    def test_info_view_without_layer(self):
        view = queryMultiAdapter(
            (self.portal, TestRequest()), name="plone_contentrules_info"
        )
        self.assertIsNotNone(view)
        # Unlayered on purpose: old "contentrules" actions evaluate it on
        # every page.  Manager + active storage on the site root: tab shown.
        # An empty storage is falsy, so the storage needs at least one rule.
        queryUtility(IRuleStorage)["test-rule"] = Rule()
        self.assertTrue(view.show_rules_tab())


class TestUninstall(unittest.TestCase):
    layer = PLONE_APP_CONTENTRULES_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        installer = get_installer(self.portal, self.request)
        installer.uninstall_product("plone.app.contentrules")
        self.installer = installer

    def test_profile_not_installed(self):
        self.assertFalse(
            self.installer.is_profile_installed("plone.app.contentrules:default")
        )

    def test_storage_removed(self):
        self.assertIsNone(queryUtility(IRuleStorage))

    def test_configlet_removed(self):
        ids = [
            c["id"]
            for c in self.portal.portal_controlpanel.enumConfiglets(
                group="plone-content"
            )
        ]
        self.assertNotIn("ContentRules", ids)

    def test_action_removed(self):
        self.assertNotIn("contentrules", self.portal.portal_actions.object.objectIds())

    def test_browserlayer_removed(self):
        from plone.app.contentrules.browser.interfaces import IPloneAppContentrulesLayer

        self.assertNotIn(IPloneAppContentrulesLayer, registered_layers())

    def test_info_view_after_uninstall(self):
        view = queryMultiAdapter(
            (self.portal, self.request), name="plone_contentrules_info"
        )
        self.assertFalse(view.show_rules_tab())
