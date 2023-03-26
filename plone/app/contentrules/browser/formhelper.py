from Acquisition import aq_inner
from Acquisition import aq_parent
from plone.app.contentrules import PloneMessageFactory as _
from plone.app.contentrules.browser.interfaces import IContentRulesForm
from plone.autoform.form import AutoExtensibleForm
from plone.z3cform import layout
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form import button
from z3c.form import form
from zope.component import getMultiAdapter
from zope.event import notify
from zope.interface import implementer

import zope.lifecycleevent


@implementer(IContentRulesForm)
class AddForm(AutoExtensibleForm, form.AddForm):
    """A base add form for content rule.

    Use this for rule elements that require configuration before being added to
    a rule. Element types that do not should use NullAddForm instead.

    Sub-classes should define create() and set the form_fields class variable.

    Notice the subtle difference between AddForm and NullAddform in that the
    create template method for AddForm takes as a parameter a dict 'data':

        def create(self, data):
            return MyAssignment(data.get('foo'))

    whereas the NullAddForm has no data parameter:

        def create(self):
            return MyAssignment()
    """

    ignoreContext = True

    def updateActions(self):
        super().updateActions()
        self.actions["save"].addClass("btn btn-primary")
        self.actions["cancel"].addClass("btn btn-secondary")

    def nextURL(self):
        rule = aq_parent(aq_inner(self.context))
        context = aq_parent(aq_inner(rule))
        url = str(getMultiAdapter((context, self.request), name="absolute_url"))
        focus = self.context.id.strip("+")
        return "{}/++rule++{}/@@manage-elements#{}".format(
            url,
            rule.__name__,
            focus,
        )

    def add(self, content):
        self.context.add(content)

    @button.buttonAndHandler(_("label_save", default="Save"), name="save")
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

    @button.buttonAndHandler(
        _("label_cancel", default="Cancel"),
        name="cancel",
    )
    def handle_cancel_action(self, action):
        nextURL = self.nextURL()
        if nextURL:
            self.request.response.redirect(self.nextURL())
        return ""


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
        return ""

    def nextURL(self):
        rule = aq_parent(aq_inner(self.context))
        context = aq_parent(aq_inner(rule))
        url = str(getMultiAdapter((context, self.request), name="absolute_url"))
        return f"{url}/++rule++{rule.__name__}/@@manage-elements"

    def create(self):
        raise NotImplementedError("concrete classes must implement create()")


@implementer(IContentRulesForm)
class EditForm(AutoExtensibleForm, form.EditForm):
    """An edit form for rule elements."""

    def updateActions(self):
        super().updateActions()
        self.actions["save"].addClass("btn btn-primary")
        self.actions["cancel"].addClass("btn btn-secondary")

    @button.buttonAndHandler(_("label_save", default="Save"), name="save")
    def handle_save_action(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        self.applyChanges(data)
        nextURL = self.nextURL()
        if nextURL:
            self.request.response.redirect(self.nextURL())
        return ""

    @button.buttonAndHandler(
        _("label_cancel", default="Cancel"),
        name="cancel",
    )
    def handle_cancel_action(self, action):
        nextURL = self.nextURL()
        if nextURL:
            self.request.response.redirect(self.nextURL())
        return ""

    def nextURL(self):
        element = aq_inner(self.context)
        rule = aq_parent(element)
        context = aq_parent(rule)
        url = str(getMultiAdapter((context, self.request), name="absolute_url"))
        focus = self.context.id.strip("+")
        return "{}/++rule++{}/@@manage-elements#{}".format(
            url,
            rule.__name__,
            focus,
        )


class ContentRuleFormWrapper(layout.FormWrapper):
    index = ViewPageTemplateFile("templates/contentrules-pageform.pt")
