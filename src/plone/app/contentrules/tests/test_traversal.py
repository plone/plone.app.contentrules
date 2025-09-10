from .dummy import DummyAction
from .dummy import DummyCondition
from Acquisition import aq_base
from Acquisition import aq_parent
from plone.app.contentrules.rule import Rule
from plone.app.contentrules.tests.base import ContentRulesTestCase
from plone.contentrules.engine.interfaces import IRuleStorage
from zope.component import getUtility


class TestTraversal(ContentRulesTestCase):
    def testTraverseToRule(self):
        r = Rule()
        storage = getUtility(IRuleStorage)
        storage["r1"] = r
        traversed = self.portal.restrictedTraverse("++rule++r1")
        self.assertTrue(aq_parent(traversed) is self.portal)
        self.assertTrue(aq_base(traversed) is r)

    def testTraverseToRuleCondition(self):
        r = Rule()
        e1 = DummyCondition()
        e1.x = "x"

        e2 = DummyCondition()
        e2.x = "y"

        r.conditions.append(e1)
        r.conditions.append(e2)
        storage = getUtility(IRuleStorage)
        storage["r1"] = r

        tr = self.portal.restrictedTraverse("++rule++r1")
        te1 = tr.restrictedTraverse("++condition++0")
        te2 = tr.restrictedTraverse("++condition++1")

        self.assertTrue(aq_parent(te1) is tr)
        self.assertEqual("x", te1.x)

        self.assertTrue(aq_parent(te2) is tr)
        self.assertEqual("y", te2.x)

    def testTraverseToRuleAction(self):
        r = Rule()
        e1 = DummyAction()
        e1.x = "x"

        e2 = DummyAction()
        e2.x = "y"

        r.actions.append(e1)
        r.actions.append(e2)
        storage = getUtility(IRuleStorage)
        storage["r1"] = r

        tr = self.portal.restrictedTraverse("++rule++r1")
        te1 = tr.restrictedTraverse("++action++0")
        te2 = tr.restrictedTraverse("++action++1")

        self.assertTrue(aq_parent(te1) is tr)
        self.assertEqual("x", te1.x)

        self.assertTrue(aq_parent(te2) is tr)
        self.assertEqual("y", te2.x)
