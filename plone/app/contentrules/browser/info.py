# -*- coding: utf-8 -*-
from AccessControl import getSecurityManager
from plone.contentrules.engine.interfaces import IRuleAssignable
from plone.contentrules.engine.interfaces import IRuleStorage
from Products.Five.browser import BrowserView
from zope.component import queryUtility


class ContentRulesInfo(BrowserView):

    def show_rules_tab(self):
        """Whether or not the rules tab should be shown
        """

        if not IRuleAssignable.providedBy(self.context):
            return False

        check_permission = getSecurityManager().checkPermission
        can_manage_rules = check_permission(
            'Content rules: Manage rules',
            self.context,
        )
        if not can_manage_rules:
            return False

        storage = queryUtility(IRuleStorage)
        if not storage:
            return False

        return storage.active
