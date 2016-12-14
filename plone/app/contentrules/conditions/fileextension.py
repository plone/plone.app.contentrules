# -*- coding: utf-8 -*-
from plone.contentrules.rule.interfaces import IExecutable, IRuleElementData
from zope.component import adapts
from z3c.form import form
from zope.interface import implementer, Interface
from zope import schema

from OFS.SimpleItem import SimpleItem
try:
    from Products.ATContentTypes.interfaces import IFileContent
except ImportError:
    IFileContent = None

from plone.app.contentrules import PloneMessageFactory as _
from plone.app.contentrules.browser.formhelper import AddForm, EditForm
from plone.app.contentrules.browser.formhelper import ContentRuleFormWrapper


class IFileExtensionCondition(Interface):
    """Interface for the configurable aspects of a portal type condition.

    This is also used to create add and edit forms, below.
    """

    file_extension = schema.TextLine(title=_(u"File extension"),
                                     description=_(u"The file extension to check for"),
                                     required=True)


@implementer(IFileExtensionCondition, IRuleElementData)
class FileExtensionCondition(SimpleItem):
    """The actual persistent implementation of the file extension condition.

    Note that we must mix in Explicit to keep Zope 2 security happy.
    """

    file_extension = u''
    element = "plone.conditions.FileExtension"

    @property
    def summary(self):
        return _(u"File extension is ${ext}", mapping=dict(ext=self.file_extension))


@implementer(IExecutable)
class FileExtensionConditionExecutor(object):
    """The executor for this condition.

    This is registered as an adapter in configure.zcml
    """
    adapts(Interface, IFileExtensionCondition, Interface)

    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        obj = self.event.object
        if IFileContent is None:
            return False
        if not IFileContent.providedBy(obj):
            return False

        base_unit = obj.getFile()
        get_filename = getattr(base_unit, 'getFilename', None)
        if not get_filename:
            return False

        name = get_filename()
        extension = name[name.rfind('.') + 1:]
        return extension == self.element.file_extension


class FileExtensionAddForm(AddForm):
    """An add form for file extension rule conditions.
    """
    schema = IFileExtensionCondition
    label = _(u"Add File Extension Condition")
    description = _(u"A file extension condition can restrict a rule from "
                    "executing unless the target is a File with a particular extension.")
    form_name = _(u"Configure element")

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
    label = _(u"Edit File Extension Condition")
    description = _(u"A file extension condition can restrict a rule from "
                    "executing unless the target is a File with a particular extension.")
    form_name = _(u"Configure element")


class FileExtensionEditFormView(ContentRuleFormWrapper):
    form = FileExtensionEditForm
