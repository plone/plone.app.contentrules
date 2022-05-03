from plone.app.contentrules.actions.versioning import VersioningAction
from plone.app.contentrules.actions.versioning import VersioningEditFormView
from plone.app.contentrules.rule import Rule
from plone.app.contentrules.tests.base import ContentRulesTestCase
from plone.contentrules.engine.interfaces import IRuleStorage
from plone.contentrules.rule.interfaces import IExecutable
from plone.contentrules.rule.interfaces import IRuleAction
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import implementer
from zope.interface import Interface


@implementer(Interface)
class DummyEvent:
    def __init__(self, object):
        self.object = object


class TestVersioningAction(ContentRulesTestCase):
    def testRegistered(self):
        element = getUtility(IRuleAction, name="plone.actions.Versioning")
        self.assertEqual("plone.actions.Versioning", element.addview)
        self.assertEqual("edit", element.editview)
        self.assertEqual(None, element.for_)
        self.assertEqual(None, element.event)

    def testInvokeAddView(self):
        element = getUtility(IRuleAction, name="plone.actions.Versioning")
        storage = getUtility(IRuleStorage)
        storage["foo"] = Rule()
        rule = self.portal.restrictedTraverse("++rule++foo")

        adding = getMultiAdapter((rule, self.request), name="+action")
        addview = getMultiAdapter((adding, self.request), name=element.addview)

        addview.form_instance.update()
        content = addview.form_instance.create(data={"comment": "Hello world"})
        addview.form_instance.add(content)

        e = rule.actions[0]
        self.assertTrue(isinstance(e, VersioningAction))
        self.assertEqual("Hello world", e.comment)

    def testInvokeEditView(self):
        element = getUtility(IRuleAction, name="plone.actions.Versioning")
        e = VersioningAction()
        editview = getMultiAdapter((e, self.request), name=element.editview)
        self.assertTrue(isinstance(editview, VersioningEditFormView))

    def testExecute(self):
        e = VersioningAction()
        e.comment = "Hello world"

        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder)), IExecutable)
        # not version for now
        pr = self.portal.portal_repository
        self.assertEqual(pr.getHistoryMetadata(self.folder), [])

        # action will create first version
        self.assertEqual(True, ex())
        self.assertEqual(
            pr.getHistoryMetadata(self.folder).getLength(countPurged=False), 1
        )
        # calling action again will create a second version
        ex()
        self.assertEqual(
            pr.getHistoryMetadata(self.folder).getLength(countPurged=False), 2
        )
