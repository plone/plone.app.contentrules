# -*- coding: utf-8 -*-
from OFS.SimpleItem import SimpleItem
from plone.app.contentrules import PloneMessageFactory as _
from plone.app.contentrules.browser.formhelper import AddForm
from plone.app.contentrules.browser.formhelper import ContentRuleFormWrapper
from plone.app.contentrules.browser.formhelper import EditForm
from plone.contentrules.rule.interfaces import IExecutable
from plone.contentrules.rule.interfaces import IRuleElementData
from z3c.form import form
from zope import schema
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface
from plone.app.contenttypes.interfaces import IFile
try:
    from Products.ATContentTypes.interfaces import IFileContent
except ImportError:
    IFileContent = None


class IFileExtensionCondition(Interface):
    """Interface for the configurable aspects of a portal type condition.

    This is also used to create add and edit forms, below.
    """

    file_extension = schema.TextLine(
        title=_(u'File extension'),
        description=_(u'The file extension to check for'),
        required=True
    )


@implementer(IFileExtensionCondition, IRuleElementData)
class FileExtensionCondition(SimpleItem):
    """The actual persistent implementation of the file extension condition.

    Note that we must mix in Explicit to keep Zope 2 security happy.
    """

    file_extension = u''
    element = 'plone.conditions.FileExtension'

    @property
    def summary(self):
        return _(
            u'File extension is ${ext}',
            mapping=dict(ext=self.file_extension)
        )


@implementer(IExecutable)
@adapter(Interface, IFileExtensionCondition, Interface)
class FileExtensionConditionExecutor(object):
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
            base_unit = getattr(obj, 'file', None)
            name = getattr(base_unit, 'filename', None)
        elif IFileContent is None:
            return False
        elif not IFileContent.providedBy(obj):
            return False
        else:
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
    label = _(u'Add File Extension Condition')
    description = _(
        u'A file extension condition can restrict a rule from '
        u'executing unless the target is a File with a particular extension.'
    )
    form_name = _(u'Configure element')

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
    label = _(u'Edit File Extension Condition')
    description = _(
        u'A file extension condition can restrict a rule from '
        u'executing unless the target is a File with a particular extension.'
    )
    form_name = _(u'Configure element')


class FileExtensionEditFormView(ContentRuleFormWrapper):
    form = FileExtensionEditForm
