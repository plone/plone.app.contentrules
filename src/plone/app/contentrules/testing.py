from plone.app.contentrules.browser.interfaces import IPloneAppContentrulesLayer
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import MOCK_MAILHOST_FIXTURE
from plone.app.testing import PloneSandboxLayer
from zope.interface import alsoProvides

import plone.app.contentrules


class PloneAppContentrulesLayer(PloneSandboxLayer):
    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        self.loadZCML(package=plone.app.contentrules)
        self.loadZCML("testing.zcml", package=plone.app.contentrules.tests)

    def setUpPloneSite(self, portal):
        applyProfile(portal, "plone.app.contentrules:default")


PLONE_APP_CONTENTRULES_FIXTURE = PloneAppContentrulesLayer()


class ContentrulesIntegrationTesting(IntegrationTesting):
    """Integration testing whose requests carry the add-on browser layer,
    like requests to a site with the add-on activated."""

    def testSetUp(self):
        super().testSetUp()
        alsoProvides(self["request"], IPloneAppContentrulesLayer)


class ContentrulesFunctionalTesting(FunctionalTesting):
    """Functional testing whose requests carry the add-on browser layer."""

    def testSetUp(self):
        super().testSetUp()
        alsoProvides(self["request"], IPloneAppContentrulesLayer)


PLONE_APP_CONTENTRULES_INTEGRATION_TESTING = ContentrulesIntegrationTesting(
    bases=(PLONE_APP_CONTENTRULES_FIXTURE, MOCK_MAILHOST_FIXTURE),
    name="PloneAppContentrulesLayer:IntegrationTesting",
)


PLONE_APP_CONTENTRULES_FUNCTIONAL_TESTING = ContentrulesFunctionalTesting(
    bases=(PLONE_APP_CONTENTRULES_FIXTURE,),
    name="PloneAppContentrulesLayer:FunctionalTesting",
)
