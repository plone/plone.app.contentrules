from plone.contentrules.engine.interfaces import IRuleContainer
from plone.contentrules.engine.interfaces import IRuleExecutor

from Acquisition import aq_inner, aq_parent
            
def added(event):
    container = IRuleContainer(event.newParent, None)
    if container is not None:
        executor = IRuleExecutor(container)
        executor.executeAll(event)

def removed(event):
    container = IRuleContainer(event.oldParent, None)
    if container is not None:
        executor = IRuleExecutor(container)
        executor.executeAll(event)
    
def modified(event):
    container = IRuleContainer(aq_parent(aq_inner(event.object)), None)
    if container is not None:
        executor = IRuleExecutor(container)
        executor.executeAll(event)