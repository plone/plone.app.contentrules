import transaction
from zope.component import getUtility

from plone.contentrules.engine.interfaces import IRuleStorage
from plone.contentrules.engine.interfaces import IRuleAssignmentManager

from plone.contentrules.engine.assignments import RuleAssignment

from plone.app.contentrules.rule import Rule
from plone.app.contentrules.rule import get_assignments

from plone.app.contentrules.tests.base import ContentRulesTestCase
from plone.app.contentrules import api


class TestRuleAssignmentMapping(ContentRulesTestCase):

    def afterSetUp(self):
        self.folder.invokeFactory('Folder', 'f1')
        self.folder.f1.invokeFactory('Folder', 'f11')
        self.folder.f1.invokeFactory('Folder', 'f12')

        self.storage = getUtility(IRuleStorage)
        self.storage['r1'] = Rule()
        self.storage['r2'] = Rule()
        self.storage['r3'] = Rule()

        self.f11a = IRuleAssignmentManager(self.folder.f1.f11)
        self.f11a['r1'] = RuleAssignment('r1', bubbles=True)
        get_assignments(self.storage['r1']).insert('/'.join(self.folder.f1.f11.getPhysicalPath()))

        self.f12a = IRuleAssignmentManager(self.folder.f1.f12)
        self.f12a['r1'] = RuleAssignment('r1', bubbles=True)
        get_assignments(self.storage['r1']).insert('/'.join(self.folder.f1.f12.getPhysicalPath()))

        self.f12a['r2'] = RuleAssignment('r2', bubbles=True)
        get_assignments(self.storage['r2']).insert('/'.join(self.folder.f1.f12.getPhysicalPath()))

    def testRuleRemoved(self):
        self.failUnless('r1' in self.f11a)
        self.failUnless('r1' in self.f12a)

        del self.storage['r1']

        self.failIf('r1' in self.f11a)
        self.failIf('r1' in self.f12a)

    def testContainerMoved(self):
        f12path = '/'.join(self.folder.f1.f12.getPhysicalPath())
        self.failUnless(f12path in get_assignments(self.storage['r1']))
        self.failUnless(f12path in get_assignments(self.storage['r2']))

        transaction.savepoint(1)
        self.folder.f1.manage_renameObject('f12', 'f12a')
        f12apath = '/'.join(self.folder.f1.f12a.getPhysicalPath())

        self.failIf(f12path in get_assignments(self.storage['r1']))
        self.failIf(f12path in get_assignments(self.storage['r2']))

        self.failUnless(f12apath in get_assignments(self.storage['r1']))
        self.failUnless(f12apath in get_assignments(self.storage['r1']))

    def testParentOfContainerMoved(self):
        f12path = '/'.join(self.folder.f1.f12.getPhysicalPath())
        self.failUnless(f12path in get_assignments(self.storage['r1']))
        self.failUnless(f12path in get_assignments(self.storage['r2']))

        transaction.savepoint(1)
        self.folder.manage_renameObject('f1', 'f1a')
        f12apath = '/'.join(self.folder.f1a.f12.getPhysicalPath())

        self.failIf(f12path in get_assignments(self.storage['r1']))
        self.failIf(f12path in get_assignments(self.storage['r2']))

        self.failUnless(f12apath in get_assignments(self.storage['r1']))
        self.failUnless(f12apath in get_assignments(self.storage['r1']))

    def testContainerRemoved(self):
        f12path = '/'.join(self.folder.f1.f12.getPhysicalPath())
        self.failUnless(f12path in get_assignments(self.storage['r1']))
        self.failUnless(f12path in get_assignments(self.storage['r2']))

        transaction.savepoint(1)
        self.folder._delObject('f1')

        self.failIf(f12path in get_assignments(self.storage['r1']))
        self.failIf(f12path in get_assignments(self.storage['r2']))

    def testRuleAssignmentRemovedAPI(self):
        self.failUnless('r1' in self.f11a)
        self.failUnless('r1' in self.f12a)

        api.unassign_rule(self.folder.f1.f11, 'r1')

        self.failIf('r1' in self.f11a)
        self.failUnless('r1' in self.f12a)

    def testRuleAssignmentEditedAPI(self):
        self.failUnless(self.f11a['r1'].bubbles)
        self.failUnless(self.f11a['r1'].enabled)

        api.edit_rule_assignment(self.folder.f1.f11, 'r1',
                                 bubbles=False, enabled=False)

        self.failIf(self.f11a['r1'].bubbles)
        self.failIf(self.f11a['r1'].enabled)

        api.edit_rule_assignment(self.folder.f1.f11, 'r1',
                                 bubbles=True, enabled=True)

        self.failUnless(self.f11a['r1'].bubbles)
        self.failUnless(self.f11a['r1'].enabled)

    def testRuleAssignmentAddedAPI(self):
        api.assign_rule(self.folder.f1.f11, 'r2', enabled=True, bubbles=True)
        self.failUnless('r2' in self.f11a)
        self.failUnless(self.f11a['r2'].enabled)
        self.failUnless(self.f11a['r2'].bubbles)

        api.assign_rule(self.folder.f1.f11, 'r3', enabled=True, bubbles=False,
                        insert_before='r2')
        self.failUnless('r3' in self.f11a)
        self.failUnless(self.f11a['r3'].enabled)
        self.failIf(self.f11a['r3'].bubbles)

        self.assertEqual(self.f11a.keys(), ['r1', 'r3', 'r2'])


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestRuleAssignmentMapping))
    return suite

