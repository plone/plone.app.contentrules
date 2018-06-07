# -*- coding: utf-8 -*-
"""Base class for integration tests, based on plone.app.testing
"""
from plone.app.contentrules.testing import PLONE_APP_CONTENTRULES_INTEGRATION_TESTING  # noqa: E501
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from zope.component import getMultiAdapter

import unittest


class ContentRulesTestCase(unittest.TestCase):
    """Base class for integration tests for plone.app.contentrules.
    This may provide specific set-up and tear-down operations, or provide
    convenience methods.
    """

    layer = PLONE_APP_CONTENTRULES_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        login(self.portal, TEST_USER_NAME)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'f1')
        self.folder = self.portal['f1']
        self.folder.invokeFactory('Document', 'd1')
        self.portal.invokeFactory('Folder', 'target')

    def addAuthToRequest(self):
        portal = self.layer['portal']
        request = self.layer['request']
        authenticator = getMultiAdapter(
            (portal, request), name=u'authenticator')
        auth = authenticator.authenticator().split('value="')[1].rstrip('"/>')
        request.form['_authenticator'] = auth
