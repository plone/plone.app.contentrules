from plone.contentrules.engine.interfaces import IRuleContainer
from plone.contentrules.engine.interfaces import IRuleExecutor

from zope.app.container.interfaces import IObjectMovedEvent

from Acquisition import aq_inner, aq_parent

def objectEvent(evt):
    """Generic handler for object-moved events.
    
    If the event is an IObjectMoved event or sub-type, the handler will
    attempt to execute rules on the context, and on the old and new parents, 
    if given.
    
    If not, attempt to execute rules found in the parent of the object
    """
    
    obj = event.object
    
    container = IRuleContainer(obj, None)
    if container is not None:
        executor = IRuleExecutor(container)
        executor.executeAll(event)
        
    if IObjectMovedEvent.providedBy(event):        
        if event.oldParent is not None:
            container = IRuleContainer(event.oldParent, None)
            if container is not None:
                executor = IRuleExecutor(event.oldParent)
                executor.executeAll(event)
            
        if event.newParent is not None and event.newParent != event.oldParent:
            container = IRuleContainer(event.newParent, None)
            if container is not None:
                executor = IRuleExecutor(event.newParent)
                executor.executeAll(event)
    else:
        parent = aq_parent(aq_inner(obj))
        container = IRuleContainer(parent, None)
        if container is not None:
            executor = IRuleExecutor(parent)
            executor.executeAll(event)