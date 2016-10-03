# -*- coding: utf-8 -*-
from z3c.form import form, button
from plone.z3cform import layout
from zope.component import getMultiAdapter
from zope.event import notify
from zope.interface import implementer
import zope.lifecycleevent

from Acquisition import aq_parent, aq_inner
from Products.Five.browser import BrowserView

from plone.app.contentrules import PloneMessageFactory as _
from plone.app.contentrules.browser.interfaces import IContentRulesForm

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.autoform.form import AutoExtensibleForm


@implementer(IContentRulesForm)
class AddForm(AutoExtensibleForm, form.AddForm):
    """A base add form for content rule.

    Use this for rule elements that require configuration before being added to
    a rule. Element types that do not should use NullAddForm instead.

    Sub-classes should define create() and set the form_fields class variable.

    Notice the suble difference between AddForm and NullAddform in that the
    create template method for AddForm takes as a parameter a dict 'data':

        def create(self, data):
            return MyAssignment(data.get('foo'))

    whereas the NullAddForm has no data parameter:

        def create(self):
            return MyAssignment()
    """
    ignoreContext = True

    def updateActions(self):
        super(AddForm, self).updateActions()
        self.actions['save'].addClass("context")
        self.actions['cancel'].addClass("standalone")

    def nextURL(self):
        rule = aq_parent(aq_inner(self.context))
        context = aq_parent(aq_inner(rule))
        url = str(getMultiAdapter((context, self.request), name=u"absolute_url"))
        focus = self.context.id.strip('+')
        return '%s/++rule++%s/@@manage-elements#%s' % (url, rule.__name__, focus)

    def add(self, content):
        self.context.add(content)

    @button.buttonAndHandler(_(u"label_save", default=u"Save"), name='save')
    def handle_save_action(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        content = self.create(data)
        self.add(content)
        nextURL = self.nextURL()
        if nextURL:
            self.request.response.redirect(self.nextURL())

    @button.buttonAndHandler(_(u"label_cancel", default=u"Cancel"), name='cancel')
    def handle_cancel_action(self, action):
        nextURL = self.nextURL()
        if nextURL:
            self.request.response.redirect(self.nextURL())
        return ''


class NullAddForm(BrowserView):
    """An add view that will add its content immediately, without presenting
    a form.

    You should subclass this for rule elements that do not require any
    configuration before being added, and write a create() method that takes no
    parameters and returns the appropriate assignment instance.
    """

    def __call__(self):
        ob = self.create()
        notify(zope.lifecycleevent.ObjectCreatedEvent(ob))
        self.context.add(ob)
        nextURL = self.nextURL()
        if nextURL:
            self.request.response.redirect(self.nextURL())
        return ''

    def nextURL(self):
        rule = aq_parent(aq_inner(self.context))
        context = aq_parent(aq_inner(rule))
        url = str(getMultiAdapter((context, self.request), name=u"absolute_url"))
        return '%s/++rule++%s/@@manage-elements' % (url, rule.__name__)

    def create(self):
        raise NotImplementedError("concrete classes must implement create()")


@implementer(IContentRulesForm)
class EditForm(AutoExtensibleForm, form.EditForm):
    """An edit form for rule elements.
    """

    def updateActions(self):
        super(EditForm, self).updateActions()
        self.actions['save'].addClass("context")
        self.actions['cancel'].addClass("standalone")

    @button.buttonAndHandler(_(u"label_save", default=u"Save"), name='save')
    def handle_save_action(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        self.applyChanges(data)
        nextURL = self.nextURL()
        if nextURL:
            self.request.response.redirect(self.nextURL())
        return ''

    @button.buttonAndHandler(_(u"label_cancel", default=u"Cancel"), name='cancel')
    def handle_cancel_action(self, action):
        nextURL = self.nextURL()
        if nextURL:
            self.request.response.redirect(self.nextURL())
        return ''

    def nextURL(self):
        element = aq_inner(self.context)
        rule = aq_parent(element)
        context = aq_parent(rule)
        url = str(getMultiAdapter((context, self.request), name=u"absolute_url"))
        focus = self.context.id.strip('+')
        return '%s/++rule++%s/@@manage-elements#%s' % (url, rule.__name__, focus)


class ContentRuleFormWrapper(layout.FormWrapper):

    index = ViewPageTemplateFile('templates/contentrules-pageform.pt')