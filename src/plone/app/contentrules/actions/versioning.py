from OFS.SimpleItem import SimpleItem
from plone.app.contentrules import PloneMessageFactory as _
from plone.app.contentrules.actions import ActionAddForm
from plone.app.contentrules.actions import ActionEditForm
from plone.app.contentrules.browser.formhelper import ContentRuleFormWrapper
from plone.contentrules.rule.interfaces import IExecutable
from plone.contentrules.rule.interfaces import IRuleElementData
from Products.CMFCore.utils import getToolByName
from zope import schema
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


class IVersioningAction(Interface):
    """Interface for the configurable aspects of a versioning action.

    This is also used to create add and edit forms, below.
    """

    comment = schema.TextLine(
        title=_("Comment"),
        description=_("The comment added to the history while versioning the content."),
        required=False,
    )


@implementer(IVersioningAction, IRuleElementData)
class VersioningAction(SimpleItem):
    """The actual persistent implementation of the versioning action element."""

    comment = ""

    element = "plone.actions.Versioning"

    @property
    def summary(self):
        return _(
            "Versioning with comment ${comment}",
            mapping=dict(comment=self.comment),
        )


@adapter(Interface, IVersioningAction, Interface)
@implementer(IExecutable)
class VersioningActionExecutor:
    """The executor for this action.

    This is registered as an adapter in configure.zcml
    """

    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        comment = _(self.element.comment)
        pr = getToolByName(self.context, "portal_repository")
        pr.save(obj=self.event.object, comment=comment)
        return True


class VersioningAddForm(ActionAddForm):
    """An add form for versioning rule actions."""

    schema = IVersioningAction
    label = _("Add Versioning Action")
    description = _(
        "A versioning action will store a version of a content "
        "no matter versioning is enabled for it or not."
    )
    form_name = _("Configure element")
    Type = VersioningAction


class VersioningAddFormView(ContentRuleFormWrapper):
    form = VersioningAddForm


class VersioningEditForm(ActionEditForm):
    """An edit form for versioning rule actions.

    z3c.form does all the magic here.
    """

    schema = IVersioningAction
    label = _("Edit Versioning Action")
    description = _(
        "A versioning action will store a version of a content "
        "no matter versioning is enabled for it or not."
    )
    form_name = _("Configure element")


class VersioningEditFormView(ContentRuleFormWrapper):
    form = VersioningEditForm
