from email import message_from_bytes
from plone.app.contentrules.actions.mail import MailAction
from plone.app.contentrules.actions.mail import MailAddFormView
from plone.app.contentrules.actions.mail import MailEditFormView
from plone.app.contentrules.rule import Rule
from plone.app.contentrules.tests.base import ContentRulesTestCase
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.base.interfaces.controlpanel import IMailSchema
from plone.contentrules.engine.interfaces import IRuleStorage
from plone.contentrules.rule.interfaces import IExecutable
from plone.contentrules.rule.interfaces import IRuleAction
from plone.registry.interfaces import IRegistry
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import implementer
from zope.interface.interfaces import IObjectEvent

import unittest


@implementer(IObjectEvent)
class DummyEvent:
    def __init__(self, object):
        self.object = object


class TestMailAction(ContentRulesTestCase):
    def setUp(self):
        super().setUp()
        self.folder["d1"].setTitle("Wälkommen")

        users = (
            ("userone", "User One", "user@one.com", ("Manager", "Member")),
            ("usertwo", "User Two", "user@two.com", ("Reviewer", "Member")),
            ("userthree", "User Three", "user@three.com", ("Owner", "Member")),
            ("userfour", "User Four", "user@four.com", ("Member",)),
        )
        for id, fname, email, roles in users:
            self.portal.portal_membership.addMember(id, "secret", roles, [])
            member = self.portal.portal_membership.getMemberById(id)
            member.setMemberProperties({"fullname": fname, "email": email})
        # XXX: remove the manager role that was set in the base class
        setRoles(self.portal, TEST_USER_ID, [])

    def testRegistered(self):
        element = getUtility(IRuleAction, name="plone.actions.Mail")
        self.assertEqual("plone.actions.Mail", element.addview)
        self.assertEqual("edit", element.editview)
        self.assertEqual(None, element.for_)

    def testInvokeAddView(self):
        element = getUtility(IRuleAction, name="plone.actions.Mail")
        storage = getUtility(IRuleStorage)
        storage["foo"] = Rule()
        rule = self.portal.restrictedTraverse("++rule++foo")

        adding = getMultiAdapter((rule, self.portal.REQUEST), name="+action")
        addview = getMultiAdapter((adding, self.portal.REQUEST), name=element.addview)
        self.assertTrue(isinstance(addview, MailAddFormView))

        addview.form_instance.update()
        output = addview.form_instance()
        self.assertIn("<h1>Substitutions</h1>", output)
        content = addview.form_instance.create(
            data={
                "subject": "My Subject",
                "source": "foo@bar.be",
                "recipients": "foo@bar.be,bar@foo.be",
                "message": "Hey, Oh!",
            }
        )
        addview.form_instance.add(content)

        e = rule.actions[0]
        self.assertTrue(isinstance(e, MailAction))
        self.assertEqual("My Subject", e.subject)
        self.assertEqual("foo@bar.be", e.source)
        self.assertEqual("foo@bar.be,bar@foo.be", e.recipients)
        self.assertEqual("Hey, Oh!", e.message)

    def testInvokeEditView(self):
        element = getUtility(IRuleAction, name="plone.actions.Mail")
        e = MailAction()
        editview = getMultiAdapter((e, self.folder.REQUEST), name=element.editview)
        self.assertTrue(isinstance(editview, MailEditFormView))

    def testExecute(self):
        # this avoids sending mail as currentuser@foobar.com
        self.portal.portal_membership.getAuthenticatedMember().setProperties(
            email="currentuser@foobar.com"
        )
        e = MailAction()
        e.source = "$user_email"
        e.recipients = (
            "bar@foo.be, bar@foo.be, $reviewer_emails, "
            "$manager_emails, $member_emails"
        )
        e.message = "Päge '${title}' created in ${url} !"
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)), IExecutable)
        ex()
        sent_mails = {}
        for mail_sent in self.portal.MailHost.messages:
            mail_sent_msg = message_from_bytes(mail_sent)
            sent_mails[mail_sent_msg.get("To")] = mail_sent_msg

        mailSent = sent_mails["bar@foo.be"]
        self.assertEqual('text/plain; charset="utf-8"', mailSent.get("Content-Type"))
        self.assertEqual("currentuser@foobar.com", mailSent.get("From"))
        # The output message should be a utf-8 encoded string
        self.assertEqual(
            "Päge 'Wälkommen' created in http://nohost/plone/f1/d1 !",
            mailSent.get_payload(decode=True).decode("utf8"),
        )

        # check interpolation of $reviewer_emails
        self.assertTrue("user@two.com" in sent_mails)

        # check interpolation of $manager_emails
        self.assertTrue("user@one.com" in sent_mails)

        # check interpolation of $member_emails
        emails = [
            "bar@foo.be",
            "user@one.com",
            "user@two.com",
            "user@three.com",
            "user@four.com",
        ]
        self.assertEqual(set(emails), set(sent_mails.keys()))

    def testExecuteNoSource(self):
        e = MailAction()
        e.recipients = "bar@foo.be,foo@bar.be"
        e.message = "Document created !"
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)), IExecutable)
        # this no longer errors since it breaks usability
        self.assertTrue(ex)
        # and will return False for the unsent message
        # (happens when no sender address can be computed)
        registry = getUtility(IRegistry)
        mail_settings = registry.forInterface(IMailSchema, prefix="plone")
        mail_settings.email_from_address = ""
        self.assertEqual(ex(), False)

        # if we provide a site mail address the message sends correctly
        mail_settings.email_from_address = "manager@portal.be"
        mail_settings.email_from_name = "plone@rulez"
        ex()
        self.assertEqual(len(self.portal.MailHost.messages), 2)
        mailSent = message_from_bytes(self.portal.MailHost.messages[0])
        self.assertEqual('text/plain; charset="utf-8"', mailSent.get("Content-Type"))
        self.assertIn(mailSent.get("To"), ["bar@foo.be", "foo@bar.be"])
        self.assertEqual('"plone@rulez" <manager@portal.be>', mailSent.get("From"))
        self.assertEqual("Document created !", mailSent.get_payload())

    def testExecuteMultiRecipients(self):
        e = MailAction()
        e.source = "foo@bar.be"
        e.recipients = "bar@foo.be,foo@bar.be"
        e.message = "Document created !"
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)), IExecutable)
        ex()
        self.assertEqual(len(self.portal.MailHost.messages), 2)
        # in py3 the order of mails is non-determininistic
        # because sending iterates over a set of recipients
        for msg in self.portal.MailHost.messages:
            if b"bar@foo.be" in msg:
                mailSent1 = message_from_bytes(msg)
            else:
                mailSent2 = message_from_bytes(msg)
        self.assertEqual('text/plain; charset="utf-8"', mailSent1.get("Content-Type"))
        self.assertEqual("bar@foo.be", mailSent1.get("To"))
        self.assertEqual("foo@bar.be", mailSent1.get("From"))
        self.assertEqual("Document created !", mailSent1.get_payload())
        self.assertEqual('text/plain; charset="utf-8"', mailSent2.get("Content-Type"))
        self.assertEqual("foo@bar.be", mailSent2.get("To"))
        self.assertEqual("foo@bar.be", mailSent2.get("From"))
        self.assertEqual("Document created !", mailSent2.get_payload())

    def testExecuteExcludeActor(self):
        self.portal.portal_membership.getAuthenticatedMember().setProperties(
            email="currentuser@foobar.com"
        )
        e = MailAction()
        e.source = "$user_email"
        e.exclude_actor = True
        e.recipients = "bar@foo.be, currentuser@foobar.com"
        e.message = "A dummy event just happened !!!!!"
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)), IExecutable)
        ex()
        self.assertEqual(len(self.portal.MailHost.messages), 1)

        mailSent = message_from_bytes(self.portal.MailHost.messages[0])
        self.assertEqual("bar@foo.be", mailSent.get("To"))

    def testExecuteNoRecipients(self):
        # no recipient
        e = MailAction()
        e.source = "foo@bar.be"
        e.recipients = ""
        e.message = "Document created !"
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)), IExecutable)
        ex()
        self.assertEqual(len(self.portal.MailHost.messages), 0)

    @unittest.skip("Monkey patching does not work well with mocking. Needs fixing.")
    def testExecuteBadMailHost(self):
        # Our goal is that mailing errors should not cause exceptions
        self.portal.portal_membership.getAuthenticatedMember().setProperties(
            email="currentuser@foobar.com"
        )
        e = MailAction()
        e.source = "$user_email"
        e.recipients = (
            "bar@foo.be, $reviewer_emails, $manager_emails, " "$member_emails"
        )
        e.message = "PÃ¤ge '${title}' created in ${url} !"
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)), IExecutable)
        ex()
