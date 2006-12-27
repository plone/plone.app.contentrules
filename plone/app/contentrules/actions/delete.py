from OFS.SimpleItem import SimpleItem
from persistent import Persistent 

from zope.interface import implements, Interface
from zope.component import adapts
from zope.formlib import form
from zope import schema

from plone.contentrules.rule.interfaces import IExecutable, IRuleActionData
from plone.contentrules.rule.rule import Node

from plone.app.contentrules.browser.formhelper import NullAddForm

import transaction
from Acquisition import aq_inner, aq_parent
from ZODB.POSException import ConflictError

class IDeleteAction(IRuleActionData):
    """Interface for the configurable aspects of a delete action.
    """
             
class DeleteAction(SimpleItem):
    """The actual persistent implementation of the action element.
    """
    implements(IDeleteAction)
    
class DeleteActionExecutor(object):
    """The executor for this action.
    """
    implements(IExecutable)
    adapts(Interface, IDeleteAction, Interface)
         
    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        obj = self.event.object
        parent = aq_parent(aq_inner(obj))
        
        transaction.savepoint()        
        
        try:
            parent.manage_delObjects(obj.getId())
        except ConflictError, e:
            raise e
        except:
            return False
        
        return True 
        
class DeleteAddForm(NullAddForm):
    """A degenerate "add form"" for delete actions.
    """
    
    def create(self):
        return Node('plone.actions.Delete', DeleteAction())