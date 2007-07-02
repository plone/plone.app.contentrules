from zope.interface import Interface
from zope.app.container.interfaces import IAdding

class IContentRulesInfo(Interface):
    """Site-wide information about content rules
    """
    
    def show_rules_tab():
        """Determine whether or not the rules tab should be shown.
        """

class IRuleAdding(IAdding):
    """Marker interface for rule add views.
    
    Rules' addviews should be registered for this.
    """
    
class IRuleElementAdding(IAdding):
    """Marker interface for rule element (actions/conditions) add views.
    
    Rules' addviews should be registered for this.
    """
    
class IRuleConditionAdding(IRuleElementAdding):
    pass
    
class IRuleActionAdding(IRuleElementAdding):
    pass

class IContentRulesForm(Interface):
    """Marker interface for forms that need content rules layout
    """