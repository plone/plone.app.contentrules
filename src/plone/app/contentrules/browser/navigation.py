from plone.app.contentrules import PloneMessageFactory as _
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.browser.navigation import PhysicalNavigationBreadcrumbs


class RuleBreadcrumbs(PhysicalNavigationBreadcrumbs):
    def breadcrumbs(self):
        portal_url = getToolByName(self.context, "portal_url")()
        return (
            {
                "absolute_url": f"{portal_url}/@@rules-controlpanel",
                "Title": _(
                    "title_manage_contentrules",
                    default="Content Rules",
                ),
            },
            {
                "absolute_url": "{}/@@manage-elements".format(
                    self.context.absolute_url(),
                ),
                "Title": self.context.title or self.context.id,
            },
        )
