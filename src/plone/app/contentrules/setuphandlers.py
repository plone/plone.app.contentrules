from plone.base.interfaces import INonInstallable
from zope.interface import implementer


@implementer(INonInstallable)
class HiddenProfiles:
    def getNonInstallableProfiles(self):
        """Hide the uninstall profile from site creation and the add-ons control panel."""
        return ["plone.app.contentrules:uninstall"]
