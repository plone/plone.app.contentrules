from plone.app.contentrules.tests.base import ContentRulesTestCase

class TestLoggerAction(ContentRulesTestCase):

    def testRegistered(self): 
        self.fail('Test missing')
    
    def testInvokeAddView(self): 
        self.fail('Test missing')
    
    def testInvokeEditView(self): 
        self.fail('Test missing')

    def testExecute(self): 
        self.fail('Test missing')

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestLoggerAction))
    return suite
