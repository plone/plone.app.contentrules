from zope.app.container.interfaces import IAdding

class IRuleAdding(IAdding):
    """Marker interface for rule add views.
    
    Rules' addviews should be registered for this.
    """
    
class IRuleElementAdding(IAdding):
    """Marker interface for rule element (actions/conditions) add views.
    
    Rules' addviews should be registered for this.
    """