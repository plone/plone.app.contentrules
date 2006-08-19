from plone.contentrules.engine.interfaces import IRuleContainer
from plone.contentrules.engine.interfaces import IRuleExecutor

def objectMovedEvent(context, event):
    """Generic handler for object-moved events.
    
    Will attempt to execute rules on the context, and on the old and new
    parents, if given.
    """
    
    obj = IRuleContainer(event.object, None)
    if obj is not None:
        executor = IRuleExecutor(obj)
        executor.executeAll(event)
        
    if event.oldParent is not None:
        obj = IRuleContainer(event.oldParent, None)
        if obj is not None:
            executor = IRuleExecutor(obj)
            executor.executeAll(event)
            
    if event.newParent is not None:
        obj = IRuleContainer(event.newParent, None)
        if obj is not None:
            executor = IRuleExecutor(obj)
            executor.executeAll(event)