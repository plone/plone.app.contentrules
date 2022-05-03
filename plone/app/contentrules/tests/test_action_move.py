from plone.app.contentrules.actions.move import MoveAction
from plone.app.contentrules.actions.move import MoveEditFormView
from plone.app.contentrules.rule import Rule
from plone.app.contentrules.tests.base import ContentRulesTestCase
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
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


class TestMoveAction(ContentRulesTestCase):
    def testRegistered(self):
        element = getUtility(IRuleAction, name="plone.actions.Move")
        self.assertEqual("plone.actions.Move", element.addview)
        self.assertEqual("edit", element.editview)
        self.assertEqual(None, element.for_)
        self.assertEqual(IObjectEvent, element.event)

    def testInvokeAddView(self):
        element = getUtility(IRuleAction, name="plone.actions.Move")
        storage = getUtility(IRuleStorage)
        storage["foo"] = Rule()
        rule = self.portal.restrictedTraverse("++rule++foo")

        adding = getMultiAdapter((rule, self.portal.REQUEST), name="+action")
        addview = getMultiAdapter((adding, self.portal.REQUEST), name=element.addview)

        addview.form_instance.update()
        content = addview.form_instance.create(
            data={
                "target_folder": "/target",
            }
        )
        addview.form_instance.add(content)

        e = rule.actions[0]
        self.assertTrue(isinstance(e, MoveAction))
        self.assertEqual("/target", e.target_folder)

    def testInvokeEditView(self):
        element = getUtility(IRuleAction, name="plone.actions.Move")
        e = MoveAction()
        editview = getMultiAdapter((e, self.folder.REQUEST), name=element.editview)
        self.assertTrue(isinstance(editview, MoveEditFormView))

    def testExecute(self):
        e = MoveAction()
        e.target_folder = "/target"

        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)), IExecutable)
        self.assertEqual(True, ex())

        self.assertFalse("d1" in self.folder.objectIds())
        self.assertTrue("d1" in self.portal.target.objectIds())

        # test catalog is ok
        brains = self.portal.portal_catalog(id="d1")
        self.assertEqual(len(brains), 1)
        self.assertEqual(brains[0].getPath(), "/plone/target/d1")

    def testExecuteWithError(self):
        e = MoveAction()
        e.target_folder = "/dummy"

        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)), IExecutable)
        self.assertEqual(False, ex())

        self.assertTrue("d1" in self.folder.objectIds())
        self.assertFalse("d1" in self.portal.target.objectIds())

    def testExecuteWithoutPermissionsOnTarget(self):
        setRoles(self.portal, TEST_USER_ID, ("Member",))

        e = MoveAction()
        e.target_folder = "/target"

        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)), IExecutable)
        self.assertEqual(True, ex())

        self.assertFalse("d1" in self.folder.objectIds())
        self.assertTrue("d1" in self.portal.target.objectIds())

    def testExecuteWithNamingConflict(self):
        setRoles(self.portal, TEST_USER_ID, ("Manager",))
        self.portal.target.invokeFactory("Document", "d1")
        setRoles(self.portal, TEST_USER_ID, ("Member",))

        e = MoveAction()
        e.target_folder = "/target"

        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)), IExecutable)
        self.assertEqual(True, ex())

        self.assertFalse("d1" in self.folder.objectIds())
        self.assertTrue("d1" in self.portal.target.objectIds())
        self.assertTrue("d1.1" in self.portal.target.objectIds())

    def testExecuteWithSameSourceAndTargetFolder(self):
        setRoles(self.portal, TEST_USER_ID, ("Manager",))
        self.portal.target.invokeFactory("Document", "d1")
        setRoles(self.portal, TEST_USER_ID, ("Member",))

        e = MoveAction()
        e.target_folder = "/target"

        ex = getMultiAdapter(
            (self.portal.target, e, DummyEvent(self.portal.target.d1)),
            IExecutable,
        )
        self.assertEqual(True, ex())

        self.assertEqual(["d1"], list(self.portal.target.objectIds()))

    def testExecuteWithNamingConflictDoesNotStupidlyAcquireHasKey(self):
        # self.folder is an ATBTreeFolder and so has a has_key.
        # self.folder.target does not.
        # Let's make sure we don't accidentally acquire has_key and use
        # this for the check for unique id.

        self.folder.invokeFactory("Folder", "target")
        self.folder.target.invokeFactory("Document", "d1")

        e = MoveAction()
        e.target_folder = "/f1/target"

        ex = getMultiAdapter(
            (self.folder.target, e, DummyEvent(self.folder.d1)), IExecutable
        )
        self.assertEqual(True, ex())

        self.assertFalse("d1" in self.folder.objectIds())
        self.assertTrue("d1" in self.folder.target.objectIds())
        self.assertTrue("d1.1" in self.folder.target.objectIds())
