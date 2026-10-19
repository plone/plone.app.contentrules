from plone.app.contentrules.browser.interfaces import IPloneAppContentrulesLayer
from plone.app.contentrules.rule import Rule
from plone.app.contentrules.testing import PLONE_APP_CONTENTRULES_INTEGRATION_TESTING
from plone.app.testing import applyProfile
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.base.utils import get_installer
from plone.browserlayer.utils import registered_layers
from plone.contentrules.engine.interfaces import IRuleStorage
from zope.component import getUtility
from zope.component import queryUtility

import unittest

PROFILE = "plone.app.contentrules:default"
PERMISSION = "Content rules: Manage rules"


class TestDefaultProfile(unittest.TestCase):
    layer = PLONE_APP_CONTENTRULES_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def test_profile_installed(self):
        installer = get_installer(self.portal, self.request)
        self.assertTrue(installer.is_profile_installed(PROFILE))
        self.assertEqual(
            self.portal.portal_setup.getLastVersionForProfile(PROFILE), ("7000",)
        )

    def test_storage_registered(self):
        self.assertIsNotNone(queryUtility(IRuleStorage))

    def test_browserlayer_registered(self):
        self.assertIn(IPloneAppContentrulesLayer, registered_layers())

    def test_configlet(self):
        ids = [
            c["id"]
            for c in self.portal.portal_controlpanel.enumConfiglets(
                group="plone-content"
            )
        ]
        self.assertIn("ContentRules", ids)

    def test_action_after_sharing(self):
        ids = list(self.portal.portal_actions.object.objectIds())
        self.assertIn("contentrules", ids)
        self.assertEqual(ids.index("contentrules"), ids.index("local_roles") + 1)

    def test_permission_roles(self):
        roles = sorted(
            r["name"]
            for r in self.portal.rolesOfPermission(PERMISSION)
            if r["selected"]
        )
        self.assertEqual(roles, ["Manager", "Site Administrator"])
        self.assertEqual(self.portal.acquiredRolesAreUsedBy(PERMISSION), "")

    def test_reapply_profile_keeps_rules(self):
        storage = getUtility(IRuleStorage)
        rule = Rule()
        rule.title = "Keep me"
        storage["keep-me"] = rule
        applyProfile(self.portal, PROFILE)
        storage_after = getUtility(IRuleStorage)
        self.assertIs(storage_after, storage)
        self.assertIn("keep-me", storage_after)

    def test_uninstall_profile_hidden(self):
        from plone.app.contentrules.setuphandlers import HiddenProfiles

        self.assertIn(
            "plone.app.contentrules:uninstall",
            HiddenProfiles().getNonInstallableProfiles(),
        )

    def test_request_has_layer(self):
        self.assertTrue(IPloneAppContentrulesLayer.providedBy(self.request))
