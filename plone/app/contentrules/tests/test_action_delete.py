from plone.app.contentrules.actions.delete import DeleteAction
from plone.app.contentrules.rule import Rule
from plone.app.contentrules.tests.base import ContentRulesTestCase
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.contentrules.engine.interfaces import IRuleStorage
from plone.contentrules.rule.interfaces import IExecutable
from plone.contentrules.rule.interfaces import IRuleAction
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import implementer
from zope.interface.interfaces import IObjectEvent


@implementer(IObjectEvent)
class DummyEvent:
    def __init__(self, object):
        self.object = object


class TestDeleteAction(ContentRulesTestCase):
    def testRegistered(self):
        element = getUtility(IRuleAction, name="plone.actions.Delete")
        self.assertEqual("plone.actions.Delete", element.addview)
        self.assertEqual(None, element.editview)
        self.assertEqual(None, element.for_)
        self.assertEqual(IObjectEvent, element.event)

    def testInvokeAddView(self):
        element = getUtility(IRuleAction, name="plone.actions.Delete")
        storage = getUtility(IRuleStorage)
        storage["foo"] = Rule()
        rule = self.portal.restrictedTraverse("++rule++foo")

        adding = getMultiAdapter(
            (rule.__of__(self.portal), self.portal.REQUEST), name="+action"
        )
        addview = getMultiAdapter(
            (adding.__of__(rule), self.portal.REQUEST), name=element.addview
        )
        addview()

        e = rule.actions[0]
        self.assertTrue(isinstance(e, DeleteAction))

    def testExecute(self):
        e = DeleteAction()

        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)), IExecutable)
        self.assertEqual(True, ex())

        self.assertFalse("d1" in self.folder.objectIds())
