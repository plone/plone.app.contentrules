from zope.interface import Interface

class ITesting(Interface):
    """A testing view.
    
    Call this to add a logging action to the container, e.g.
    
    http://localhost:8080/plone/folder/@@contentrules_testing
    """
    
    def __call__(self):
        """Add a logger
        """