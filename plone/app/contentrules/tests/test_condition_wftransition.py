# -*- coding: utf-8 -*-
from zope.component import getUtility, getMultiAdapter

from plone.contentrules.engine.interfaces import IRuleStorage
from plone.contentrules.rule.interfaces import IRuleCondition
from plone.contentrules.rule.interfaces import IExecutable

from plone.app.contentrules.conditions.wftransition import WorkflowTransitionCondition
from plone.app.contentrules.conditions.wftransition import WorkflowTransitionEditFormView

from plone.app.contentrules.rule import Rule

from plone.app.contentrules.tests.base import ContentRulesTestCase

from Products.CMFCore.interfaces import IActionSucceededEvent
from Products.CMFCore.WorkflowCore import ActionSucceededEvent


class TestWorkflowTransitionCondition(ContentRulesTestCase):

    def afterSetUp(self):
        self.setRoles(('Manager', ))

    def testRegistered(self):
        element = getUtility(IRuleCondition, name='plone.conditions.WorkflowTransition')
        self.assertEqual('plone.conditions.WorkflowTransition', element.addview)
        self.assertEqual('edit', element.editview)
        self.assertEqual(None, element.for_)
        self.assertEqual(IActionSucceededEvent, element.event)

    def testInvokeAddView(self):
        element = getUtility(IRuleCondition, name='plone.conditions.WorkflowTransition')
        storage = getUtility(IRuleStorage)
        storage[u'foo'] = Rule()
        rule = self.portal.restrictedTraverse('++rule++foo')

        adding = getMultiAdapter((rule, self.portal.REQUEST), name='+condition')
        addview = getMultiAdapter((adding, self.portal.REQUEST), name=element.addview)

        addview.form_instance.update()
        content = addview.form_instance.create(data={'wf_transitions': ['publish', 'hide']})
        addview.form_instance.add(content)

        e = rule.conditions[0]
        self.assertTrue(isinstance(e, WorkflowTransitionCondition))
        self.assertEqual(['publish', 'hide'], e.wf_transitions)

    def testInvokeEditView(self):
        element = getUtility(IRuleCondition, name='plone.conditions.WorkflowTransition')
        e = WorkflowTransitionCondition()
        editview = getMultiAdapter((e, self.folder.REQUEST), name=element.editview)
        self.assertTrue(isinstance(editview, WorkflowTransitionEditFormView))

    def testExecute(self):
        e = WorkflowTransitionCondition()
        e.wf_transitions = ['publish', 'hide']

        ex = getMultiAdapter((self.portal, e,
                              ActionSucceededEvent(self.folder, 'dummy_workflow', 'publish', None)),
                             IExecutable)
        self.assertTrue(ex())

        ex = getMultiAdapter((self.portal, e,
                              ActionSucceededEvent(self.folder, 'dummy_workflow', 'retract', None)),
                             IExecutable)
        self.assertFalse(ex())

        ex = getMultiAdapter((self.portal, e,
                              ActionSucceededEvent(self.folder, 'dummy_workflow', 'hide', None)),
                             IExecutable)
        self.assertTrue(ex())
