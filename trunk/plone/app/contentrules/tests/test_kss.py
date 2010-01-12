import unittest

from kss.core.tests.base import KSSViewTestCaseMixin
from plone.app.kss.tests.kss_and_plone_layer import KSSAndPloneLayer

from plone.app.contentrules.tests.base import ContentRulesTestCase

class KSSContentRulesTestCase(ContentRulesTestCase, KSSViewTestCaseMixin):

    layer = KSSAndPloneLayer

    def afterSetUp(self):
        self.setDebugRequest()
        self.setRoles(['Manager'])
        self.view = self.portal.restrictedTraverse('replaceRulesTable')

    def test_instantiation(self):
        view = self.view
        commands = view.getCommands()
        self.assertNotEquals(view, None)

    def test_replaceFilteredRulesForm(self):
        view = self.view
        commands = view.getCommands()
        res = view.replaceFilteredRulesForm(ruleType='state-enabled')
        # Adjust for different payload in newer kss versions
        html = res[0]['params']['html'].replace('<![CDATA[', '').replace(']]>', '')
        res[0]['params']['html'] = html
        self.assertEquals(res, [
            {'selectorType': '',    
             'params': {'html': u'\n<form style="display: inline" method="POST" id="rules_table_form" action="http://nohost/plone/@@rules-controlpanel">\n</form>\n', 
             'withKssSetup': u'True'}, 
             'name': 'replaceHTML', 
             'selector': '#rules_table_form'}
        ])

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(KSSContentRulesTestCase),
        ))
