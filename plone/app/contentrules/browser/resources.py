from plone.app.layout.viewlets.common import ViewletBase


class Resources(ViewletBase):

    def render(self):
        return u"""
      <script type="text/javascript" src="%(portal_url)s/++resource++manage-contentrules.js"></script>
      <link rel="stylesheet" type="text/css" media="all" href="%(portal_url)s/++resource++manage-contentrules.css"></link>
      """ % {'portal_url': self.site_url}