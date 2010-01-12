from zope.interface import implements, Interface
from zope.component import getUtility, getMultiAdapter

from plone.contentrules.engine.interfaces import IRuleStorage
from plone.contentrules.rule.interfaces import IRuleAction
from plone.contentrules.rule.interfaces import IExecutable

from plone.app.contentrules.actions.notify import NotifyAction
from plone.app.contentrules.actions.notify import NotifyEditForm

from plone.app.contentrules.rule import Rule

from plone.app.contentrules.tests.base import ContentRulesTestCase

from Products.statusmessages import STATUSMESSAGEKEY
from Products.statusmessages.interfaces import IStatusMessage
from Products.statusmessages.adapter import _decodeCookieValue

class DummyEvent(object):
    implements(Interface)

class TestNotifyAction(ContentRulesTestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))

    def testRegistered(self): 
        element = getUtility(IRuleAction, name='plone.actions.Notify')
        self.assertEquals('plone.actions.Notify', element.addview)
        self.assertEquals('edit', element.editview)
        self.assertEquals(None, element.for_)
        self.assertEquals(None, element.event)
    
    def testInvokeAddView(self): 
        element = getUtility(IRuleAction, name='plone.actions.Notify')
        storage = getUtility(IRuleStorage)
        storage[u'foo'] = Rule()
        rule = self.portal.restrictedTraverse('++rule++foo')
        
        adding = getMultiAdapter((rule, self.portal.REQUEST), name='+action')
        addview = getMultiAdapter((adding, self.portal.REQUEST), name=element.addview)
        
        addview.createAndAdd(data={'message' : 'Hello world', 'message_type' : 'info'})
        
        e = rule.actions[0]
        self.failUnless(isinstance(e, NotifyAction))
        self.assertEquals('Hello world', e.message)
        self.assertEquals('info', e.message_type)
    
    def testInvokeEditView(self): 
        element = getUtility(IRuleAction, name='plone.actions.Notify')
        e = NotifyAction()
        editview = getMultiAdapter((e, self.folder.REQUEST), name=element.editview)
        self.failUnless(isinstance(editview, NotifyEditForm))

    def testExecute(self): 
        e = NotifyAction()
        e.message = 'Hello world'
        e.message_type = 'info'
        
        ex = getMultiAdapter((self.folder, e, DummyEvent()), IExecutable)
        self.assertEquals(True, ex())
        
        status = IStatusMessage(self.app.REQUEST)
        new_cookies = self.app.REQUEST.RESPONSE.cookies[STATUSMESSAGEKEY]
        messages = _decodeCookieValue(new_cookies['value'])
        self.assertEquals(1, len(messages))
        self.assertEquals('Hello world', messages[0].message)
        self.assertEquals('info', messages[0].type)
        
        
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestNotifyAction))
    return suite
