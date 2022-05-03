from plone.app.contentrules.conditions.role import RoleCondition
from plone.app.contentrules.conditions.role import RoleEditFormView
from plone.app.contentrules.rule import Rule
from plone.app.contentrules.tests.base import ContentRulesTestCase
from plone.contentrules.engine.interfaces import IRuleStorage
from plone.contentrules.rule.interfaces import IExecutable
from plone.contentrules.rule.interfaces import IRuleCondition
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import implementer
from zope.interface.interfaces import IObjectEvent


@implementer(IObjectEvent)
class DummyEvent:
    def __init__(self, obj):
        self.object = obj


class TestRoleCondition(ContentRulesTestCase):
    def testRegistered(self):
        element = getUtility(IRuleCondition, name="plone.conditions.Role")
        self.assertEqual("plone.conditions.Role", element.addview)
        self.assertEqual("edit", element.editview)
        self.assertEqual(None, element.for_)
        self.assertEqual(None, element.event)

    def testInvokeAddView(self):
        element = getUtility(IRuleCondition, name="plone.conditions.Role")
        storage = getUtility(IRuleStorage)
        storage["foo"] = Rule()
        rule = self.portal.restrictedTraverse("++rule++foo")

        adding = getMultiAdapter((rule, self.portal.REQUEST), name="+condition")
        addview = getMultiAdapter((adding, self.portal.REQUEST), name=element.addview)

        addview.form_instance.update()
        content = addview.form_instance.create(
            data={"role_names": ["Manager", "Member"]}
        )
        addview.form_instance.add(content)

        e = rule.conditions[0]
        self.assertTrue(isinstance(e, RoleCondition))
        self.assertEqual(["Manager", "Member"], e.role_names)

    def testInvokeEditView(self):
        element = getUtility(IRuleCondition, name="plone.conditions.Role")
        e = RoleCondition()
        editview = getMultiAdapter((e, self.folder.REQUEST), name=element.editview)
        self.assertTrue(isinstance(editview, RoleEditFormView))

    def testExecute(self):
        e = RoleCondition()
        e.role_names = ["Manager", "Member"]

        ex = getMultiAdapter((self.portal, e, DummyEvent(self.folder)), IExecutable)
        self.assertTrue(ex())

        e.role_names = ["Reviewer"]

        ex = getMultiAdapter((self.portal, e, DummyEvent(self.portal)), IExecutable)
        self.assertFalse(ex())
