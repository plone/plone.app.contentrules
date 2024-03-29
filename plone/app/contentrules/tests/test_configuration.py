from plone.app.contentrules.testing import (  # noqa: E501
    PLONE_APP_CONTENTRULES_FUNCTIONAL_TESTING,
)
from plone.app.testing import applyProfile
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.contentrules.engine.interfaces import IRuleAssignmentManager
from plone.contentrules.engine.interfaces import IRuleStorage
from Products.GenericSetup.context import TarballExportContext
from Products.GenericSetup.interfaces import IBody
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.lifecycleevent.interfaces import IObjectModifiedEvent

import time
import unittest


class TestGenericSetup(unittest.TestCase):
    layer = PLONE_APP_CONTENTRULES_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        login(self.portal, TEST_USER_NAME)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.portal.invokeFactory("Folder", "news")
        self.portal.invokeFactory("Folder", "events")
        self.storage = getUtility(IRuleStorage)
        applyProfile(self.portal, "plone.app.contentrules:testing")

    def testRuleInstalled(self):
        self.assertTrue("test1" in self.storage)
        self.assertTrue("test2" in self.storage)

    def testRulesConfigured(self):
        rule1 = self.storage["test1"]
        self.assertEqual("Test rule 1", rule1.title)
        self.assertEqual("A test rule", rule1.description)
        self.assertEqual(IObjectModifiedEvent, rule1.event)
        self.assertEqual(True, rule1.enabled)
        self.assertEqual(False, rule1.stop)

        self.assertEqual(2, len(rule1.conditions))
        self.assertEqual("plone.conditions.PortalType", rule1.conditions[0].element)
        self.assertEqual(
            {"Document", "News Item"}, set(rule1.conditions[0].check_types)
        )
        self.assertEqual("plone.conditions.Role", rule1.conditions[1].element)
        self.assertEqual(["Manager"], list(rule1.conditions[1].role_names))

        self.assertEqual(1, len(rule1.actions))
        self.assertEqual("plone.actions.Notify", rule1.actions[0].element)
        self.assertEqual("A message: Hej d\xe5", rule1.actions[0].message)
        self.assertEqual("info", rule1.actions[0].message_type)

        rule2 = self.storage["test2"]
        self.assertEqual("Test rule 2", rule2.title)
        self.assertEqual("Another test rule", rule2.description)
        self.assertEqual(IObjectModifiedEvent, rule2.event)
        self.assertEqual(False, rule2.enabled)
        self.assertEqual(True, rule2.stop)

        self.assertEqual(1, len(rule2.conditions))
        self.assertEqual("plone.conditions.PortalType", rule2.conditions[0].element)
        self.assertEqual(["Event"], list(rule2.conditions[0].check_types))

        self.assertEqual(1, len(rule2.actions))
        self.assertEqual("plone.actions.Workflow", rule2.actions[0].element)
        self.assertEqual("publish", rule2.actions[0].transition)

    def testRuleAssigned(self):
        assignable = IRuleAssignmentManager(self.portal.news)
        self.assertEqual(3, len(assignable))

        self.assertEqual(True, assignable["test1"].enabled)
        self.assertEqual(False, assignable["test1"].bubbles)

        self.assertEqual(False, assignable["test2"].enabled)
        self.assertEqual(True, assignable["test2"].bubbles)

        self.assertEqual(False, assignable["test3"].enabled)
        self.assertEqual(False, assignable["test3"].bubbles)

    def testAssignmentOrdering(self):
        assignable = IRuleAssignmentManager(self.portal.news)
        self.assertEqual({"test3", "test2", "test1"}, set(assignable.keys()))

    def testImportTwice(self):
        # Ensure rules, actions/conditions and assignments are not duplicated
        # if the profile is re-imported; see bug #8027.
        portal_setup = self.portal.portal_setup
        time.sleep(1)  # avoid timestamp collision
        portal_setup.runAllImportStepsFromProfile(
            "profile-plone.app.contentrules:testing"
        )

        # We should get the same results as before
        self.testRuleInstalled()
        self.testRulesConfigured()
        self.testRuleAssigned()

    def testExport(self):
        self.maxDiff = None
        site = self.portal
        context = TarballExportContext(self.portal.portal_setup)
        exporter = getMultiAdapter((site, context), IBody, name="plone.contentrules")

        body = exporter.body.decode("utf8")

        # There is a bug in supermodel such that Set fields can be exported in a random order
        body = body.replace(
            """
     <element>News Item</element>
     <element>Document</element>
""",
            """
     <element>Document</element>
     <element>News Item</element>
""",
        )

        expected = """<?xml version="1.0" encoding="utf-8"?>
<contentrules>
 <rule name="test1" title="Test rule 1" cascading="False"
    description="A test rule" enabled="True"
    event="zope.lifecycleevent.interfaces.IObjectModifiedEvent"
    stop-after="False">
  <conditions>
   <condition type="plone.conditions.PortalType">
    <property name="check_types">
     <element>Document</element>
     <element>News Item</element>
    </property>
   </condition>
   <condition type="plone.conditions.Role">
    <property name="role_names">
     <element>Manager</element>
    </property>
   </condition>
  </conditions>
  <actions>
   <action type="plone.actions.Notify">
    <property name="message">A message: Hej då</property>
    <property name="message_type">info</property>
   </action>
  </actions>
 </rule>
 <rule name="test2" title="Test rule 2" cascading="False"
    description="Another test rule" enabled="False"
    event="zope.lifecycleevent.interfaces.IObjectModifiedEvent"
    stop-after="True">
  <conditions>
   <condition type="plone.conditions.PortalType">
    <property name="check_types">
     <element>Event</element>
    </property>
   </condition>
  </conditions>
  <actions>
   <action type="plone.actions.Workflow">
    <property name="transition">publish</property>
   </action>
  </actions>
 </rule>
 <rule name="test3" title="Test rule 3" cascading="False"
    description="Third test rule" enabled="True"
    event="zope.lifecycleevent.interfaces.IObjectMovedEvent"
    stop-after="False">
  <conditions/>
  <actions/>
 </rule>
 <rule name="test4" title="Test rule 4" cascading="False"
    description="We move published events in a folder" enabled="True"
    event="Products.CMFCore.interfaces.IActionSucceededEvent"
    stop-after="True">
  <conditions>
   <condition type="plone.conditions.PortalType">
    <property name="check_types">
     <element>Event</element>
    </property>
   </condition>
   <condition type="plone.conditions.WorkflowTransition">
    <property name="wf_transitions">
     <element>publish</element>
    </property>
   </condition>
  </conditions>
  <actions>
   <action type="plone.actions.Move">
    <property name="target_folder">/events</property>
   </action>
  </actions>
 </rule>
 <rule name="test5" title="Test rule 5" cascading="True"
    description="Auto publish events" enabled="True"
    event="zope.lifecycleevent.interfaces.IObjectAddedEvent"
    stop-after="False">
  <conditions>
   <condition type="plone.conditions.PortalType">
    <property name="check_types">
     <element>Event</element>
    </property>
   </condition>
  </conditions>
  <actions>
   <action type="plone.actions.Workflow">
    <property name="transition">publish</property>
   </action>
  </actions>
 </rule>
 <assignment name="test4" bubbles="False" enabled="False" location=""/>
 <assignment name="test5" bubbles="False" enabled="False" location=""/>
 <assignment name="test1" bubbles="False" enabled="True" location="/news"/>
 <assignment name="test2" bubbles="True" enabled="False" location="/news"/>
 <assignment name="test3" bubbles="False" enabled="False" location="/news"/>
</contentrules>
"""

        self.assertEqual(expected.strip(), body.strip())
