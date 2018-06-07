# -*- coding: utf-8 -*-
from plone.app.testing.bbb import PTC_FUNCTIONAL_TESTING
from plone.testing import layered

import doctest
import unittest


optionflags = (doctest.NORMALIZE_WHITESPACE |
               doctest.ELLIPSIS |
               doctest.REPORT_NDIFF)


def test_suite():
    suite = unittest.TestSuite()
    for doc in ['assignment.txt', 'simplepublish.txt', 'multipublish.txt']:
        suite.addTest(layered(
            doctest.DocFileSuite(doc, package='plone.app.contentrules.tests',
                                 optionflags=optionflags),
            layer=PTC_FUNCTIONAL_TESTING))
    return suite
