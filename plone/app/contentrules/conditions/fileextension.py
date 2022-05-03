from OFS.SimpleItem import SimpleItem
from plone.app.contentrules import PloneMessageFactory as _
from plone.app.contentrules.browser.formhelper import AddForm
from plone.app.contentrules.browser.formhelper import ContentRuleFormWrapper
from plone.app.contentrules.browser.formhelper import EditForm
from plone.app.contenttypes.interfaces import IFile
from plone.contentrules.rule.interfaces import IExecutable
from plone.contentrules.rule.interfaces import IRuleElementData
from z3c.form import form
from zope import schema
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


class IFileExtensionCondition(Interface):
    """Interface for the configurable aspects of a portal type condition.

    This is also used to create add and edit forms, below.
    """

    file_extension = schema.TextLine(
        title=_("File extension"),
        description=_("The file extension to check for"),
        required=True,
    )


@implementer(IFileExtensionCondition, IRuleElementData)
class FileExtensionCondition(SimpleItem):
    """The actual persistent implementation of the file extension condition.

    Note that we must mix in Explicit to keep Zope 2 security happy.
    """

    file_extension = ""
    element = "plone.conditions.FileExtension"

    @property
    def summary(self):
        return _("File extension is ${ext}", mapping=dict(ext=self.file_extension))


@implementer(IExecutable)
@adapter(Interface, IFileExtensionCondition, Interface)
class FileExtensionConditionExecutor:
    """The executor for this condition.

    This is registered as an adapter in configure.zcml
    """

    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        obj = self.event.object

        if IFile.providedBy(obj):
            base_unit = getattr(obj, "file", None)
            name = getattr(base_unit, "filename", None)
        else:
            base_unit = obj.getFile()
            get_filename = getattr(base_unit, "getFilename", None)
            if not get_filename:
                return False
            name = get_filename()

        extension = name[name.rfind(".") + 1 :]
        return extension == self.element.file_extension


class FileExtensionAddForm(AddForm):
    """An add form for file extension rule conditions."""

    schema = IFileExtensionCondition
    label = _("Add File Extension Condition")
    description = _(
        "A file extension condition can restrict a rule from "
        "executing unless the target is a File with a particular extension."
    )
    form_name = _("Configure element")

    def create(self, data):
        c = FileExtensionCondition()
        form.applyChanges(self, c, data)
        return c


class FileExtensionAddFormView(ContentRuleFormWrapper):
    form = FileExtensionAddForm


class FileExtensionEditForm(EditForm):
    """An edit form for portal type conditions

    z3c.form does all the magic here.
    """

    schema = IFileExtensionCondition
    label = _("Edit File Extension Condition")
    description = _(
        "A file extension condition can restrict a rule from "
        "executing unless the target is a File with a particular extension."
    )
    form_name = _("Configure element")


class FileExtensionEditFormView(ContentRuleFormWrapper):
    form = FileExtensionEditForm
