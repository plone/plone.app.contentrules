# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import MOCK_MAILHOST_FIXTURE
from plone.app.testing import PloneSandboxLayer

import plone.app.contentrules


class PloneAppContentrulesLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        self.loadZCML('testing.zcml', package=plone.app.contentrules.tests)


PLONE_APP_CONTENTRULES_FIXTURE = PloneAppContentrulesLayer()


PLONE_APP_CONTENTRULES_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONE_APP_CONTENTRULES_FIXTURE, MOCK_MAILHOST_FIXTURE),
    name='PloneAppContentrulesLayer:IntegrationTesting',
)


PLONE_APP_CONTENTRULES_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONE_APP_CONTENTRULES_FIXTURE,),
    name='PloneAppContentrulesLayer:FunctionalTesting',
)
