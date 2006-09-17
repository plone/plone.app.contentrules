from plone.app.contentrules.tests.base import ContentRulesTestCase

class TestEvents(ContentRulesTestCase):

    def testEventHandlerExecutesRules(self): 
        self.fail('Test missing')
        
    def testEventHandlerExecutesRulesOnlyOnce(self): 
        self.fail('Test missing')
        
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestEvents))
    return suite
