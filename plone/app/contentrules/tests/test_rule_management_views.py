from plone.app.contentrules.tests.base import ContentRulesTestCase

class TestRuleManagementViews(ContentRulesTestCase):

    def testRuleAdding(self): 
        self.fail('Test missing')

    def testRuleAddView(self): 
        self.fail('Test missing')

    def testRuleEditView(self): 
        self.fail('Test missing')

    def testDeleteRule(self): 
        self.fail('Test missing')

class TestRuleElementManagementViews(ContentRulesTestCase):

    def testRuleElementAdding(self): 
        self.fail('Test missing')
        
    def testDeleteElement(self): 
        self.fail('Test missing')
    
    def testMoveElementUp(self): 
        self.fail('Test missing')

    def testMoveElementDown(self): 
        self.fail('Test missing')    
        
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestRuleManagementViews))
    suite.addTest(makeSuite(TestRuleElementManagementViews))
    return suite
