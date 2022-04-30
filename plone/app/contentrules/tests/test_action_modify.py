from plone.app.contentrules import handlers
from unittest import TestCase
from zope.lifecycleevent import ObjectAddedEvent
from zope.lifecycleevent import ObjectRemovedEvent


class TestModifyAction(TestCase):
    def setUp(self):
        self.called = False

        def register_call(testcase):
            def inner_register_call(event):
                testcase.called = True

            return inner_register_call

        self.original_execute_rules = handlers.execute_rules
        handlers.execute_rules = register_call(self)

    def tearDown(self):
        handlers.execute_rules = self.original_execute_rules
        self.called = False

    def testIgnoreAddedEvents(self):
        class Content:
            __parent__ = None
            __name__ = None

        handlers.modified(ObjectAddedEvent(Content()))
        self.assertFalse(self.called)

    def testIgnoreDeletedEvents(self):
        class Content:
            __parent__ = None
            __name__ = None

        handlers.modified(ObjectRemovedEvent(Content()))
        self.assertFalse(self.called)
