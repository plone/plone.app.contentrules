from OFS.SimpleItem import SimpleItem
from persistent import Persistent 

from zope.interface import implements, Interface
from zope.component import adapts
from zope.formlib import form
from zope import schema

from plone.contentrules.rule.interfaces import IExecutable, IRuleActionData
from plone.contentrules.rule.rule import Node

from plone.app.contentrules.browser.formhelper import AddForm, EditForm 



class IDebugAction(IRuleActionData):
    """Interface for the configurable aspects of a logger action.
    
    This is also used to create add and edit forms, below.
    """
    
         
class DebugAction(SimpleItem):
    """The actual persistent implementation of the logger action element.
    
    Note that we must mix in Explicit to keep Zope 2 security happy.
    """
    implements(IDebugAction)
    

class DebugActionExecutor(object):
    """The executor for this action.
    
    This is registered as an adapter in configure.zcml
    """
    implements(IExecutable)
    adapts(Interface, IDebugAction, Interface)
         
    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        
        print "*** Debugger Rule Element reached"
        print "self.context = %s"%str(self.context)
        print "self.element = %s"%str(self.element)
        print "  self.event = %s\n"%str(self.event)
        import pdb; pdb.set_trace()
        return True 
        
class DebugAddForm(AddForm):
    """An add form for logger rule actions.
    
    Note that we create a Node(), not just a DebugAction, since this is what
    the elements list of IRule expects. The namespace traversal adapter
    (see traversal.py) takes care of unwrapping the actual instance from
    a Node when it's needed.
    """
    form_fields = form.FormFields(IDebugAction)
    
    def create(self, data):
        a = DebugAction()
        return Node('plone.actions.Debug', a)

class DebugEditForm(EditForm):
    """An edit form for logger rule actions.
    
    Formlib does all the magic here.
    """
    form_fields = form.FormFields(IDebugAction)