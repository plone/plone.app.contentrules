from OFS.SimpleItem import SimpleItem
from persistent import Persistent 

from zope.interface import implements, Interface
from zope.component import adapts
from zope.formlib import form
from zope import schema

from plone.contentrules.rule.interfaces import IExecutable, IRuleActionData
from plone.contentrules.rule.rule import Node

from plone.app.contentrules.browser.formhelper import AddForm, EditForm 



class IMoveToFolderAction(IRuleActionData):
    """Interface for the configurable aspects of a logger action.
    
    This is also used to create add and edit forms, below.
    """
    
    targetFolder = schema.TextLine(title=u"Target folder",default=u"relative/path/to/target")
         
class MoveToFolderAction(SimpleItem):
    """The actual persistent implementation of the logger action element.
    
    Note that we must mix in Explicit to keep Zope 2 security happy.
    """
    implements(IMoveToFolderAction)
    
    targetFolder = ''
    
class MoveToFolderActionExecutor(object):
    """The executor for this action.
    
    This is registered as an adapter in configure.zcml
    """
    implements(IExecutable)
    adapts(Interface, IMoveToFolderAction, Interface)
         
    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        print "Trying to move %s to %s."%(self.element.id,self.element.targetFolder)
        originalObject = self.context.manage_copyObjects(self.event.object.id)
        import pdb; pdb.set_trace()
        targetContext = self.context.portal_url.getPortalObject().unrestrictedTraverse('target')#self.element.targetFolder)
        import pdb; pdb.set_trace()
        targetContext.manage_pasteObjects(originalObject)
        import pdb; pdb.set_trace()
        return True 
        
class MoveToFolderAddForm(AddForm):
    """An add form for logger rule actions.
    
    Note that we create a Node(), not just a MoveToFolderAction, since this is what
    the elements list of IRule expects. The namespace traversal adapter
    (see traversal.py) takes care of unwrapping the actual instance from
    a Node when it's needed.
    """
    form_fields = form.FormFields(IMoveToFolderAction)
    
    def create(self, data):
        a = MoveToFolderAction()
        a.targetFolder = data.get('targetFolder')
        return Node('plone.actions.MoveToFolder', a)

class MoveToFolderEditForm(EditForm):
    """An edit form for logger rule actions.
    
    Formlib does all the magic here.
    """
    form_fields = form.FormFields(IMoveToFolderAction)