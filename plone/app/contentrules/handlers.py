from plone.contentrules.engine.interfaces import IRuleAssignable
from plone.contentrules.engine.interfaces import IRuleExecutor

from Acquisition import aq_inner, aq_parent
from Products.Archetypes.interfaces import IObjectInitializedEvent

# TODO: Bubbling of rules

# XXX: Disabled for now, see comment in configure.zcml
def added(event):
    return
    container = IRuleAssignable(event.newParent, None)
    if container is not None:
        executor = IRuleExecutor(container)
        executor(event)
        
def initialized(event):
    return
    container = IRuleAssignable(aq_parent(aq_inner(event.object)), None)
    if container is not None:
        executor = IRuleExecutor(container)
        executor(event)

def removed(event):
    return
    container = IRuleAssignable(event.oldParent, None)
    if container is not None:
        executor = IRuleExecutor(container)
        executor(event)
    
def modified(event):
    return
    # Because we have a special handler for IObjectInitializedEvent, make sure
    # we don't react to it twice
    
    if IObjectInitializedEvent.providedBy(event):
        return
    
    container = IRuleAssignable(aq_parent(aq_inner(event.object)), None)
    if container is not None:
        executor = IRuleExecutor(container)
        executor.execute(event)