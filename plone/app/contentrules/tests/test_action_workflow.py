# -*- coding: utf-8 -*-
from zope.interface import implementer
from zope.component import getUtility, getMultiAdapter

from plone.contentrules.engine.interfaces import IRuleStorage
from plone.contentrules.rule.interfaces import IRuleAction
from plone.contentrules.rule.interfaces import IExecutable

from plone.app.contentrules.actions.workflow import WorkflowAction
from plone.app.contentrules.actions.workflow import WorkflowEditFormView

from plone.app.contentrules.rule import Rule

from plone.app.contentrules.tests.base import ContentRulesTestCase

from zope.component.interfaces import IObjectEvent


@implementer(IObjectEvent)
class DummyEvent(object):

    def __init__(self, object):
        self.object = object


class TestWorkflowAction(ContentRulesTestCase):

    def afterSetUp(self):
        self.setRoles(('Manager', ))
        self.folder.invokeFactory('Document', 'd1')

    def testRegistered(self):
        element = getUtility(IRuleAction, name='plone.actions.Workflow')
        self.assertEqual('plone.actions.Workflow', element.addview)
        self.assertEqual('edit', element.editview)
        self.assertEqual(None, element.for_)
        self.assertEqual(IObjectEvent, element.event)

    def testInvokeAddView(self):
        element = getUtility(IRuleAction, name='plone.actions.Workflow')
        storage = getUtility(IRuleStorage)
        storage[u'foo'] = Rule()
        rule = self.portal.restrictedTraverse('++rule++foo')

        adding = getMultiAdapter((rule, self.portal.REQUEST), name='+action')
        addview = getMultiAdapter((adding, self.portal.REQUEST), name=element.addview)

        addview.form_instance.update()
        content = addview.form_instance.create(data={'transition': 'publish', })
        addview.form_instance.add(content)

        e = rule.actions[0]
        self.assertTrue(isinstance(e, WorkflowAction))
        self.assertEqual('publish', e.transition)

    def testInvokeEditView(self):
        element = getUtility(IRuleAction, name='plone.actions.Workflow')
        e = WorkflowAction()
        editview = getMultiAdapter((e, self.folder.REQUEST), name=element.editview)
        self.assertTrue(isinstance(editview, WorkflowEditFormView))

    def testExecute(self):
        e = WorkflowAction()
        e.transition = 'publish'

        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)), IExecutable)
        self.assertEqual(True, ex())

        self.assertEqual('published', self.portal.portal_workflow.getInfoFor(self.folder.d1,
                         'review_state'))

    def testExecuteWithError(self):
        e = WorkflowAction()
        e.transition = 'foobar'

        old_state = self.portal.portal_workflow.getInfoFor(self.folder.d1, 'review_state')

        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)), IExecutable)
        self.assertEqual(False, ex())

        self.assertEqual(old_state, self.portal.portal_workflow.getInfoFor(self.folder.d1,
                         'review_state'))
