from Acquisition import aq_inner
from Acquisition import aq_parent
from OFS.SimpleItem import SimpleItem
from plone.app.contentrules import PloneMessageFactory as _
from plone.app.contentrules.browser.formhelper import NullAddForm
from plone.base.utils import pretty_title_or_id
from plone.contentrules.rule.interfaces import IExecutable
from plone.contentrules.rule.interfaces import IRuleElementData
from Products.statusmessages.interfaces import IStatusMessage
from ZODB.POSException import ConflictError
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface

import transaction


class IDeleteAction(Interface):
    """Interface for the configurable aspects of a delete action."""


@implementer(IDeleteAction, IRuleElementData)
class DeleteAction(SimpleItem):
    """The actual persistent implementation of the action element."""

    element = "plone.actions.Delete"
    summary = _("Delete object")


@adapter(Interface, IDeleteAction, Interface)
@implementer(IExecutable)
class DeleteActionExecutor:
    """The executor for this action."""

    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        obj = self.event.object
        parent = aq_parent(aq_inner(obj))

        transaction.savepoint()

        try:
            parent.manage_delObjects(obj.getId())
        except ConflictError as e:
            raise e
        except Exception as e:
            self.error(obj, str(e))
            return False

        return True

    def error(self, obj, error):
        request = getattr(self.context, "REQUEST", None)
        if request is not None:
            title = pretty_title_or_id(obj, obj)
            message = _(
                "Unable to remove ${name} as part of content rule 'delete' action: ${error}",  # noqa
                mapping={"name": title, "error": error},
            )
            IStatusMessage(request).addStatusMessage(message, type="error")


class DeleteAddForm(NullAddForm):
    """A degenerate "add form" for delete actions."""

    def create(self):
        return DeleteAction()
