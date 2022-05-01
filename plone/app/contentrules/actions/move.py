from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from OFS.CopySupport import sanity_check
from OFS.event import ObjectWillBeMovedEvent
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
from zope.container.contained import notifyContainerModified
from zope.event import notify
from zope.interface import implementer
from zope.interface import Interface
from zope.lifecycleevent import ObjectMovedEvent


class IMoveAction(Interface):
    """Interface for the configurable aspects of a move action.

    This is also used to create add and edit forms, below.
    """

    target_folder = schema.Choice(
        title=_("Target folder"),
        description=_("As a path relative to the portal root."),
        required=True,
        source=CatalogSource(is_folderish=True),
    )


@implementer(IMoveAction, IRuleElementData)
class MoveAction(SimpleItem):
    """The actual persistent implementation of the action element."""

    target_folder = ""
    element = "plone.actions.Move"

    @property
    def summary(self):
        return _("Move to folder ${folder}", mapping=dict(folder=self.target_folder))


@adapter(Interface, IMoveAction, Interface)
@implementer(IExecutable)
class MoveActionExecutor:
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
        parent = aq_parent(aq_inner(obj))

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
                _(
                    "Target folder ${target} does not exist.",
                    mapping={"target": path},
                ),
            )
            return False

        if target.absolute_url() == parent.absolute_url():
            # We're already here!
            return True

        try:
            obj._notifyOfCopyTo(target, op=1)
        except ConflictError:
            raise
        except Exception as e:
            self.error(obj, str(e))
            return False

        # Are we trying to move into the same container that we copied from?
        if not sanity_check(target, obj):
            return False

        old_id = obj.getId()
        new_id = self.generate_id(target, old_id)

        notify(ObjectWillBeMovedEvent(obj, parent, old_id, target, new_id))

        obj.manage_changeOwnershipType(explicit=1)

        parent._delObject(old_id, suppress_events=True)
        obj = aq_base(obj)
        obj._setId(new_id)

        target._setObject(new_id, obj, set_owner=0, suppress_events=True)
        obj = target._getOb(new_id)

        notify(ObjectMovedEvent(obj, parent, old_id, target, new_id))
        notifyContainerModified(parent)
        if aq_base(parent) is not aq_base(target):
            notifyContainerModified(target)

        obj._postCopy(target, op=1)

        # try to make ownership implicit if possible
        obj.manage_changeOwnershipType(explicit=0)

        return True

    def error(self, obj, error):
        request = getattr(self.context, "REQUEST", None)
        if request is not None:
            title = pretty_title_or_id(obj, obj)
            message = _(
                "Unable to move ${name} as part of content rule "
                "'move' action: ${error}",
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


class MoveAddForm(ActionAddForm):
    """An add form for move-to-folder actions."""

    schema = IMoveAction
    label = _("Add Move Action")
    description = _("A move action can move an object to a different folder.")
    form_name = _("Configure element")
    Type = MoveAction


class MoveAddFormView(ContentRuleFormWrapper):
    form = MoveAddForm


class MoveEditForm(ActionEditForm):
    """An edit form for move rule actions.

    z3c.form does all the magic here.
    """

    schema = IMoveAction
    label = _("Edit Move Action")
    description = _("A move action can move an object to a different folder.")
    form_name = _("Configure element")


class MoveEditFormView(ContentRuleFormWrapper):
    form = MoveEditForm
