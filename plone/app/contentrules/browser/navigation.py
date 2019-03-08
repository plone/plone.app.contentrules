# -*- coding: utf-8 -*-
from plone.app.contentrules import PloneMessageFactory as _
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.browser.navigation import PhysicalNavigationBreadcrumbs


class RuleBreadcrumbs(PhysicalNavigationBreadcrumbs):

    def breadcrumbs(self):
        portal_url = getToolByName(self.context, 'portal_url')()
        return (
            {
                'absolute_url': '{0}/@@rules-controlpanel'.format(portal_url),
                'Title': _(
                    'title_manage_contentrules',
                    default=u'Content Rules',
                ),
            },
            {
                'absolute_url': '{0}/@@manage-elements'.format(
                    self.context.absolute_url(),
                ),
                'Title': self.context.title or self.context.id,
            },
        )
