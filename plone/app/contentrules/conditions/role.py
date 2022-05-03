from Acquisition import aq_inner
from OFS.SimpleItem import SimpleItem
from plone.app.contentrules import PloneMessageFactory as _
from plone.app.contentrules.browser.formhelper import AddForm
from plone.app.contentrules.browser.formhelper import ContentRuleFormWrapper
from plone.app.contentrules.browser.formhelper import EditForm
from plone.contentrules.rule.interfaces import IExecutable
from plone.contentrules.rule.interfaces import IRuleElementData
from Products.CMFCore.utils import getToolByName
from z3c.form import form
from zope import schema
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


class IRoleCondition(Interface):
    """Interface for the configurable aspects of a role condition.

    This is also used to create add and edit forms, below.
    """

    role_names = schema.Set(
        title=_("Roles"),
        description=_("The roles to check for."),
        required=True,
        value_type=schema.Choice(vocabulary="plone.app.vocabularies.Roles"),
    )


@implementer(IRoleCondition, IRuleElementData)
class RoleCondition(SimpleItem):
    """The actual persistent implementation of the role condition element.

    Note that we must mix in SimpleItem to keep Zope 2 security happy.
    """

    role_names = []
    element = "plone.conditions.Role"

    @property
    def summary(self):
        return _("Roles are: ${names}", mapping=dict(names=", ".join(self.role_names)))


@implementer(IExecutable)
@adapter(Interface, IRoleCondition, Interface)
class RoleConditionExecutor:
    """The executor for this condition.

    This is registered as an adapter in configure.zcml
    """

    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        portal_membership = getToolByName(self.context, "portal_membership", None)
        if portal_membership is None:
            return False
        member = portal_membership.getAuthenticatedMember()
        roles_in_context = member.getRolesInContext(aq_inner(self.event.object))
        for r in self.element.role_names:
            if r in roles_in_context:
                return True
        return False


class RoleAddForm(AddForm):
    """An add form for role rule conditions."""

    schema = IRoleCondition
    label = _("Add Role Condition")
    description = _(
        "A role condition can prevent rules from executing unless "
        "the current user has a particular role."
    )
    form_name = _("Configure element")

    def create(self, data):
        c = RoleCondition()
        form.applyChanges(self, c, data)
        return c


class RoleAddFormView(ContentRuleFormWrapper):
    form = RoleAddForm


class RoleEditForm(EditForm):
    """An edit form for role conditions"""

    schema = IRoleCondition
    label = _("Add Role Condition")
    description = _(
        "A role condition can prevent rules from executing unless "
        "the current user has a particular role."
    )
    form_name = _("Configure element")


class RoleEditFormView(ContentRuleFormWrapper):
    form = RoleEditForm
