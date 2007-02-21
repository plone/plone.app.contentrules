from zope.interface import Interface
from zope.app.container.interfaces import IAdding

class IRuleAdding(IAdding):
    """Marker interface for rule add views.
    
    Rules' addviews should be registered for this.
    """
    
class IRuleElementAdding(IAdding):
    """Marker interface for rule element (actions/conditions) add views.
    
    Rules' addviews should be registered for this.
    """
class IContentRulesForm(Interface):
    """Marker interface for forms that need content rules layout
    """