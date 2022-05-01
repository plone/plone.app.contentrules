from Acquisition import aq_base
from OFS.event import ObjectClonedEvent
from OFS.SimpleItem import SimpleItem
from plone.app.contentrules import PloneMessageFactory as _
from plone.app.contentrules.actions import ActionAddForm
from plone.app.contentrules.actions import ActionEditForm
from plone.app.contentrules.browser.formhelper import ContentRuleFormWrapper
from plone.app.vocabularies.catalog import CatalogSource
from plone.base.utils import pretty_title_or_id
from plone.contentrules.rule.interfaces import IExecutable
from plone.contentrules.rule.interfaces import IRuleElementData
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from ZODB.POSException import ConflictError
from zope import schema
from zope.component import adapter
from zope.event import notify
from zope.interface import implementer
from zope.interface import Interface
from zope.lifecycleevent import ObjectCopiedEvent

import OFS.subscribers


class ICopyAction(Interface):
    """Interface for the configurable aspects of a move action.

    This is also used to create add and edit forms, below.
    """

    target_folder = schema.Choice(
        title=_("Target folder"),
        description=_("As a path relative to the portal root."),
        required=True,
        source=CatalogSource(is_folderish=True),
    )


@implementer(ICopyAction, IRuleElementData)
class CopyAction(SimpleItem):
    """The actual persistent implementation of the action element."""

    target_folder = ""
    element = "plone.actions.Copy"

    @property
    def summary(self):
        return _("Copy to folder ${folder}.", mapping=dict(folder=self.target_folder))


@adapter(Interface, ICopyAction, Interface)
@implementer(IExecutable)
class CopyActionExecutor:
    """The executor for this action."""

    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        portal_url = getToolByName(self.context, "portal_url", None)
        if portal_url is None:
            return False

        obj = self.event.object

        path = self.element.target_folder
        if len(path) > 1 and path[0] == "/":
            path = path[1:]
        target = portal_url.getPortalObject().unrestrictedTraverse(
            str(path),
            None,
        )

        if target is None:
            self.error(
                obj,
                _("Target folder ${target} does not exist.", mapping={"target": path}),
            )
            return False

        try:
            obj._notifyOfCopyTo(target, op=0)
        except ConflictError:
            raise
        except Exception as e:
            self.error(obj, str(e))
            return False

        old_id = obj.getId()
        new_id = self.generate_id(target, old_id)

        orig_obj = obj
        obj = obj._getCopy(target)
        obj._setId(new_id)

        notify(ObjectCopiedEvent(obj, orig_obj))

        target._setObject(new_id, obj)
        obj = target._getOb(new_id)
        obj.wl_clearLocks()

        obj._postCopy(target, op=0)

        OFS.subscribers.compatibilityCall("manage_afterClone", obj, obj)

        notify(ObjectClonedEvent(obj))

        return True

    def error(self, obj, error):
        request = getattr(self.context, "REQUEST", None)
        if request is not None:
            title = pretty_title_or_id(obj, obj)
            message = _(
                "Unable to copy ${name} as part of content rule "
                "'copy' action: ${error}",
                mapping={"name": title, "error": error},
            )
            IStatusMessage(request).addStatusMessage(message, type="error")

    def generate_id(self, target, old_id):
        taken = getattr(aq_base(target), "has_key", None)
        if taken is None:
            item_ids = set(target.objectIds())

            def taken(x):
                return x in item_ids

        if not taken(old_id):
            return old_id
        idx = 1
        while taken(f"{old_id}.{idx}"):
            idx += 1
        return f"{old_id}.{idx}"


class CopyAddForm(ActionAddForm):
    """An add form for move-to-folder actions."""

    schema = ICopyAction
    label = _("Add Copy Action")
    description = _("A copy action can copy an object to a different folder.")
    Type = CopyAction


class CopyAddFormView(ContentRuleFormWrapper):
    form = CopyAddForm


class CopyEditForm(ActionEditForm):
    """An edit form for copy rule actions.

    z3c.form does all the magic here.
    """

    schema = ICopyAction
    label = _("Edit Copy Action")
    description = _("A copy action can copy an object to a different folder.")
    form_name = _("Configure element")


class CopyEditFormView(ContentRuleFormWrapper):
    form = CopyEditForm
