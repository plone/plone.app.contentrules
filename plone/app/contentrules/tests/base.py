# -*- coding: utf-8 -*-
"""Base class for integration tests, based on plone.app.testing
"""

from plone.app.testing.bbb import PloneTestCase
from zope.component import getMultiAdapter


class ContentRulesTestCase(PloneTestCase):
    """Base class for integration tests for plone.app.contentrules.
    This may provide specific set-up and tear-down operations, or provide
    convenience methods.
    """

    def addAuthToRequest(self):
        portal = self.layer['portal']
        request = self.layer['request']
        authenticator = getMultiAdapter((portal, request), name=u"authenticator")
        auth = authenticator.authenticator().split('value="')[1].rstrip('"/>')
        request.form['_authenticator'] = auth


class ContentRulesFunctionalTestCase(PloneTestCase):
    """Base class for functional integration tests for plone.app.contentrules.
    This may provide specific set-up and tear-down operations, or provide
    convenience methods.
    """
