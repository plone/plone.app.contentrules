from plone.contentrules.engine.interfaces import IRuleContainer
from plone.contentrules.engine.interfaces import IRuleExecutor

from Acquisition import aq_inner, aq_parent
from Products.Archetypes.interfaces import IObjectInitializedEvent

# XXX: Disabled for now, see comment in configure.zcml
def added(event):
    container = IRuleContainer(event.newParent, None)
    if container is not None:
        executor = IRuleExecutor(container)
        executor.executeAll(event)
        
def initialized(event):
    container = IRuleContainer(aq_parent(aq_inner(event.object)), None)
    if container is not None:
        executor = IRuleExecutor(container)
        executor.executeAll(event)

def removed(event):
    container = IRuleContainer(event.oldParent, None)
    if container is not None:
        executor = IRuleExecutor(container)
        executor.executeAll(event)
    
def modified(event):
    
    # Because we have a special handler for IObjectInitializedEvent, make sure
    # we don't react to it twice
    
    if IObjectInitializedEvent.providedBy(event):
        return
    
    container = IRuleContainer(aq_parent(aq_inner(event.object)), None)
    if container is not None:
        executor = IRuleExecutor(container)
        executor.executeAll(event)