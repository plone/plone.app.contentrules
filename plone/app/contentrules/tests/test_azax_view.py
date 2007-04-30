# Copyright (c) 2005
# Authors:
#   Godefroid Chapelle <gotcha@bubblenet.be>
#   Tarek Ziade <tz@nuxeo.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
import unittest, os
from zope import interface
#from zope.testing import doctest
from Testing.ZopeTestCase import ZopeTestCase
from plone.app.kss.tests.kss_and_plone_layer import KSSAndPloneTestCase

from Products.CMFCore.interfaces import ISiteRoot
from plone.app.contentrules.browser.azax import ContentrulesControlpanelCommand
import plone.app.contentrules
#from kss.demo.azaxview import AzaxView
#from Products.Five.zcml import load_string
from Products.Five.zcml import load_config

from Products.PloneTestCase import PloneTestCase
PloneTestCase.setupPloneSite()

class AzaxContentRulesTestCase(KSSAndPloneTestCase):

    def afterSetUp(self):
        KSSAndPloneTestCase.afterSetUp(self)
        self.setDebugRequest()
        self.setRoles(['Manager'])
        class request:
            form = {}
        interface.alsoProvides(self.folder, ISiteRoot)
        self.view = self.folder.restrictedTraverse('replaceRulesTable')

    def test_instantiation(self):
        view = self.view
        commands = view.getCommands()
        self.assertNotEquals(view, None)

    # XXX This shows the idea of how the commands output can be
    # tested by using DebugTestRequest. 
    def test_replaceFilteredRulesForm(self):
        view = self.view
        commands = view.getCommands()
        res = view.replaceFilteredRulesForm(ruleType='state-enabled')
        self.assertEquals(res, [
            {'selectorType': '',
             'params': {'html': u'\n<form style="display: inline" method="POST" id="rules_table_form" action="http://nohost/plone/Members/test_user_1_/@@rules-controlpanel">\n</form>\n', 'withKssSetup': u'True'},
             'name': 'replaceHTML', 'selector': '#rules_table_form'
             }
            ])

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(AzaxContentRulesTestCase),
#        doctest.DocTestSuite('kss.demo.azaxview'),
        ))
