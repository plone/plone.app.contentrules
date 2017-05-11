# -*- coding: utf-8 -*-
from plone.app.contentrules.browser.formhelper import AddForm
from plone.app.contentrules.browser.formhelper import EditForm
from plone.app.uuid.utils import uuidToPhysicalPath
from plone.uuid.interfaces import IUUID
from z3c.form import form
from zope.component.hooks import getSite

import os


class ContentWrapper(object):
    """
    The sole purpose of this is to transform target_folder
    values from UUID to path, which all of content rules expects
    """

    def __init__(self, content):
        self.__dict__['content'] = content

    @property
    def target_folder(self):
        content = self.content

        if content.target_folder and content.target_folder[0] == '/':
            # need to convert to uuid
            site = getSite()
            site_path = '/'.join(site.getPhysicalPath())
            path = os.path.join(site_path, content.target_folder.lstrip('/'))
            target = site.restrictedTraverse(path, None)
            if target is not None:
                return IUUID(target, None)

    def __getattr__(self, name, default=None):
        return getattr(self.__dict__['content'], name, default)

    def __setattr__(self, name, value):
        setattr(self.__dict__['content'], name, value)


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
