# -*- coding: utf-8 -*-
from email import message_from_string
from zope.component import getUtility, getMultiAdapter, getSiteManager
from zope.component.interfaces import IObjectEvent
from zope.interface import implementer

from plone.app.contentrules.rule import Rule
from plone.app.contentrules.tests.base import ContentRulesTestCase
from plone.app.contentrules.actions.mail import MailAction, MailEditFormView, MailAddFormView
from plone.contentrules.engine.interfaces import IRuleStorage
from plone.contentrules.rule.interfaces import IRuleAction, IExecutable
from plone.registry.interfaces import IRegistry

from Acquisition import aq_base
from Products.CMFPlone.interfaces.controlpanel import IMailSchema
from Products.CMFPlone.tests.utils import MockMailHost
from Products.MailHost.interfaces import IMailHost
from Products.MailHost.MailHost import MailHost

import unittest


@implementer(IObjectEvent)
class DummyEvent(object):

    def __init__(self, object):
        self.object = object


class TestMailAction(ContentRulesTestCase):

    def afterSetUp(self):
        self.setRoles(('Manager', ))
        self.portal.invokeFactory('Folder', 'target')
        self.folder.invokeFactory('Document', 'd1',
                                  title='W\xc3\xa4lkommen'.decode('utf-8'))

        users = (
            ('userone', 'User One', 'user@one.com', ('Manager', 'Member')),
            ('usertwo', 'User Two', 'user@two.com', ('Reviewer', 'Member')),
            ('userthree', 'User Three', 'user@three.com', ('Owner', 'Member')),
            ('userfour', 'User Four', 'user@four.com', ('Member', )),
        )
        for id, fname, email, roles in users:
            self.portal.portal_membership.addMember(id, 'secret', roles, [])
            member = self.portal.portal_membership.getMemberById(id)
            member.setMemberProperties({'fullname': fname, 'email': email})

    def _setup_mockmail(self):
        sm = getSiteManager(self.portal)
        sm.unregisterUtility(provided=IMailHost)
        dummyMailHost = MockMailHost('MailHost')
        sm.registerUtility(dummyMailHost, IMailHost)
        self.portal._original_MailHost = self.portal.MailHost
        self.portal.MailHost = dummyMailHost
        return dummyMailHost

    def _teardown_mockmail(self):
        self.portal.MailHost = self.portal._original_MailHost
        sm = getSiteManager(context=self.portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(aq_base(self.portal._original_MailHost),
                           provided=IMailHost)

    def testRegistered(self):
        element = getUtility(IRuleAction, name='plone.actions.Mail')
        self.assertEqual('plone.actions.Mail', element.addview)
        self.assertEqual('edit', element.editview)
        self.assertEqual(None, element.for_)

    def testInvokeAddView(self):
        element = getUtility(IRuleAction, name='plone.actions.Mail')
        storage = getUtility(IRuleStorage)
        storage[u'foo'] = Rule()
        rule = self.portal.restrictedTraverse('++rule++foo')

        adding = getMultiAdapter((rule, self.portal.REQUEST), name='+action')
        addview = getMultiAdapter((adding, self.portal.REQUEST),
                                  name=element.addview)
        self.assertTrue(isinstance(addview, MailAddFormView))

        addview.form_instance.update()
        output = addview.form_instance()
        self.assertIn('<h1>Substitutions</h1>', output)
        content = addview.form_instance.create(data={'subject': 'My Subject',
                                                     'source': 'foo@bar.be',
                                                     'recipients': 'foo@bar.be,bar@foo.be',
                                                     'message': 'Hey, Oh!'})
        addview.form_instance.add(content)

        e = rule.actions[0]
        self.assertTrue(isinstance(e, MailAction))
        self.assertEqual('My Subject', e.subject)
        self.assertEqual('foo@bar.be', e.source)
        self.assertEqual('foo@bar.be,bar@foo.be', e.recipients)
        self.assertEqual('Hey, Oh!', e.message)

    def testInvokeEditView(self):
        element = getUtility(IRuleAction, name='plone.actions.Mail')
        e = MailAction()
        editview = getMultiAdapter((e, self.folder.REQUEST),
                                   name=element.editview)
        self.assertTrue(isinstance(editview, MailEditFormView))

    def testExecute(self):
        self.loginAsPortalOwner()   # this avoids sending mail as currentuser@foobar.com
        self.portal.portal_membership.getAuthenticatedMember().setProperties(
            email='currentuser@foobar.com')
        dummyMailHost = self._setup_mockmail()
        e = MailAction()
        e.source = "$user_email"
        e.recipients = "bar@foo.be, bar@foo.be, $reviewer_emails, $manager_emails, $member_emails"   # noqa
        e.message = "P\xc3\xa4ge '${title}' created in ${url} !".decode('utf-8')
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)),
                             IExecutable)
        ex()
        sent_mails = {}
        for mail_sent in dummyMailHost.messages:
            mail_sent_msg = message_from_string(mail_sent)
            sent_mails[mail_sent_msg.get('To')] = mail_sent_msg

        mailSent = sent_mails['bar@foo.be']
        self.assertEqual('text/plain; charset="utf-8"',
                         mailSent.get('Content-Type'))
        self.assertEqual("currentuser@foobar.com", mailSent.get('From'))
        # The output message should be a utf-8 encoded string
        self.assertEqual(
            "P\xc3\xa4ge 'W\xc3\xa4lkommen' created in http://nohost/plone/Members/test_user_1_/d1 !",  # noqa
            mailSent.get_payload(decode=True))

        # check interpolation of $reviewer_emails
        self.assertTrue("user@two.com" in sent_mails)

        # check interpolation of $manager_emails
        self.assertTrue("user@one.com" in sent_mails)

        # check interpolation of $member_emails
        self.assertEqual(
            set(["bar@foo.be", "user@one.com", "user@two.com", "user@three.com", "user@four.com", ]),  # noqa
            set(sent_mails.keys()))
        self._teardown_mockmail()

    def testExecuteNoSource(self):
        dummyMailHost = self._setup_mockmail()
        e = MailAction()
        e.recipients = 'bar@foo.be,foo@bar.be'
        e.message = 'Document created !'
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)),
                             IExecutable)
        # this no longer errors since it breaks usability
        self.assertTrue(ex)
        # and will return False for the unsent message
        self.assertEqual(ex(), False)
        # if we provide a site mail address the message sends correctly
        registry = getUtility(IRegistry)
        mail_settings = registry.forInterface(IMailSchema, prefix='plone')
        mail_settings.email_from_address = 'manager@portal.be'
        mail_settings.email_from_name = u'plone@rulez'
        ex()
        mailSent = message_from_string(dummyMailHost.messages[0])
        self.assertEqual('text/plain; charset="utf-8"',
                         mailSent.get('Content-Type'))
        self.assertEqual("bar@foo.be", mailSent.get('To'))
        self.assertEqual('"plone@rulez" <manager@portal.be>',
                         mailSent.get('From'))
        self.assertEqual("Document created !",
                         mailSent.get_payload(decode=True))
        self._teardown_mockmail()

    def testExecuteMultiRecipients(self):
        dummyMailHost = self._setup_mockmail()
        e = MailAction()
        e.source = 'foo@bar.be'
        e.recipients = 'bar@foo.be,foo@bar.be'
        e.message = 'Document created !'
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)),
                             IExecutable)
        ex()
        self.assertEqual(len(dummyMailHost.messages), 2)
        mailSent = message_from_string(dummyMailHost.messages[0])
        self.assertEqual('text/plain; charset="utf-8"',
                         mailSent.get('Content-Type'))
        self.assertEqual('bar@foo.be', mailSent.get('To'))
        self.assertEqual('foo@bar.be', mailSent.get('From'))
        self.assertEqual('Document created !', mailSent.get_payload(decode=True))
        mailSent = message_from_string(dummyMailHost.messages[1])
        self.assertEqual('text/plain; charset="utf-8"',
                         mailSent.get('Content-Type'))
        self.assertEqual('foo@bar.be', mailSent.get('To'))
        self.assertEqual('foo@bar.be', mailSent.get('From'))
        self.assertEqual('Document created !', mailSent.get_payload(decode=True))
        self._teardown_mockmail()

    def testExecuteExcludeActor(self):
        dummyMailHost = self._setup_mockmail()
        self.portal.portal_membership.getAuthenticatedMember().setProperties(
            email='currentuser@foobar.com')
        e = MailAction()
        e.source = "$user_email"
        e.exclude_actor = True
        e.recipients = "bar@foo.be, currentuser@foobar.com"
        e.message = u"A dummy event juste happened !!!!!"
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)),
                             IExecutable)
        ex()
        self.assertEqual(len(dummyMailHost.messages), 1)

        mailSent = message_from_string(dummyMailHost.messages[0])
        self.assertEqual("bar@foo.be", mailSent.get('To'))
        self._teardown_mockmail()

    def testExecuteNoRecipients(self):
        # no recipient
        dummyMailHost = self._setup_mockmail()
        e = MailAction()
        e.source = 'foo@bar.be'
        e.recipients = ''
        e.message = 'Document created !'
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)),
                             IExecutable)
        ex()
        self.assertEqual(len(dummyMailHost.messages), 0)
        self._teardown_mockmail()

    @unittest.skip('Monkey patching does not work well with mocking. Needs fixing.')
    def testExecuteBadMailHost(self):
        # Our goal is that mailing errors should not cause exceptions
        self.loginAsPortalOwner()
        self.portal.portal_membership.getAuthenticatedMember().setProperties(
            email='currentuser@foobar.com')
        e = MailAction()
        e.source = "$user_email"
        e.recipients = "bar@foo.be, $reviewer_emails, $manager_emails, $member_emails"
        e.message = u"PÃ¤ge '${title}' created in ${url} !"
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)),
                             IExecutable)
        ex()
