# -*- coding: utf-8 -*-
import os
from plone.uuid.interfaces import IUUID
from zope.component.hooks import getSite
from plone.app.uuid.utils import uuidToPhysicalPath
from plone.app.contentrules.browser.formhelper import AddForm, EditForm
from z3c.form import form


class ContentWrapper(object):
    """
    The sole purpose of this is to transform target_folder
    values from UUID to path, which all of content rules expects
    """
    def __init__(self, content):
        self.content = content

    def __getattr__(self, name, default=None):
        if name == 'content':
            return self.__dict__['content']
        if name == 'target_folder':
            return self._get_target_folder()
        return getattr(self.__dict__['content'], name, default)

    def _get_target_folder(self):
        content = self.__dict__['content']
        if content.target_folder and content.target_folder[0] == '/':
            # need to convert to uuid
            site = getSite()
            site_path = '/'.join(site.getPhysicalPath())
            path = os.path.join(site_path, content.target_folder.lstrip('/'))
            target = site.restrictedTraverse(path, None)
            if target is not None:
                return IUUID(target, None)


class ActionAddForm(AddForm):
    Type = None

    def create(self, data):
        """
        Since content rules expects paths, we're transforming UUID, which
        is what the z3c form widget uses, to paths.
        """
        a = self.Type()
        if data.get('target_folder', None):
            site = getSite()
            site_path = '/'.join(site.getPhysicalPath())
            path = uuidToPhysicalPath(data['target_folder'])
            if path:
                data['target_folder'] = path[len(site_path):]
        form.applyChanges(self, a, data)
        return a


class ActionEditForm(EditForm):
    def getContent(self):
        return ContentWrapper(super(ActionEditForm, self).getContent())