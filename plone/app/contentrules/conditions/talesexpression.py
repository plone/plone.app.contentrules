from OFS.SimpleItem import SimpleItem
from plone.app.contentrules import PloneMessageFactory as _
from plone.app.contentrules.browser.formhelper import AddForm
from plone.app.contentrules.browser.formhelper import ContentRuleFormWrapper
from plone.app.contentrules.browser.formhelper import EditForm
from plone.contentrules.rule.interfaces import IExecutable
from plone.contentrules.rule.interfaces import IRuleElementData
from Products.CMFCore.Expression import createExprContext
from Products.CMFCore.Expression import Expression
from Products.CMFCore.utils import getToolByName
from z3c.form import form
from zope import schema
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


class ITalesExpressionCondition(Interface):
    """Interface for the configurable aspects of a TALES expression condition.

    This is also used to create add and edit forms, below.
    """

    tales_expression = schema.TextLine(
        title=_("TALES expression"),
        description=_("The TALES expression to check."),
        required=True,
    )


@implementer(ITalesExpressionCondition, IRuleElementData)
class TalesExpressionCondition(SimpleItem):
    """The actual persistent implementation of the TALES expression condition
    element.
    """

    tales_expression = ""
    element = "plone.conditions.TalesExpression"

    @property
    def summary(self):
        return _(
            "TALES expression is: ${tales_expression}",
            mapping={"tales_expression": self.tales_expression},
        )


@implementer(IExecutable)
@adapter(Interface, ITalesExpressionCondition, Interface)
class TalesExpressionConditionExecutor:
    """The executor for this condition.

    This is registered as an adapter in configure.zcml
    """

    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        object = self.event.object
        folder = self.context
        portal = getToolByName(folder, "portal_url").getPortalObject()
        expression = self.element.tales_expression
        ec = createExprContext(folder, portal, object)
        # Workaround CMFCore/PageTemplates issue with unicode missing context
        ec.contexts["context"] = ec.contexts["here"]
        return bool(Expression(expression)(ec))


class TalesExpressionAddForm(AddForm):
    """An add form for tales expression condition."""

    schema = ITalesExpressionCondition
    label = _("Add TALES Expression Condition")
    description = _(
        "A TALES expression condition makes the rule apply "
        "only if TALES expression is not False in context."
    )
    form_name = _("Configure element")

    def create(self, data):
        c = TalesExpressionCondition()
        form.applyChanges(self, c, data)
        return c


class TalesExpressionAddFormView(ContentRuleFormWrapper):
    form = TalesExpressionAddForm


class TalesExpressionEditForm(EditForm):
    """An edit form for TALES expression condition"""

    schema = ITalesExpressionCondition
    label = _("Edit TALES Expression Condition")
    description = _(
        "A TALES expression condition makes the rule apply "
        "only if TALES expression is not False in context."
    )
    form_name = _("Configure element")


class TalesExpressionEditFormView(ContentRuleFormWrapper):
    form = TalesExpressionEditForm
