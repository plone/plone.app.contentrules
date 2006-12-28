from OFS.SimpleItem import SimpleItem
from persistent import Persistent 

from zope.interface import implements, Interface
from zope.component import adapts
from zope.formlib import form
from zope import schema

from plone.contentrules.rule.interfaces import IExecutable, IRuleActionData
from plone.contentrules.rule.rule import Node

from plone.app.contentrules.browser.formhelper import AddForm, EditForm 

import transaction
from Acquisition import aq_inner, aq_parent
from ZODB.POSException import ConflictError
from Products.CMFCore.utils import getToolByName

class IWorkflowAction(IRuleActionData):
    """Interface for the configurable aspects of a workflow action.
    
    This is also used to create add and edit forms, below.
    """
    
    transition = schema.Choice(title=u"Transition",
                               description=u"Select the workflow transition to attempt",
                               required=True,
                               vocabulary='plone.vocabulary.WorkflowTransitions')
         
class WorkflowAction(SimpleItem):
    """The actual persistent implementation of the action element.
    """
    implements(IWorkflowAction)
    
    transition = ''
    
class WorkflowActionExecutor(object):
    """The executor for this action.
    """
    implements(IExecutable)
    adapts(Interface, IWorkflowAction, Interface)
         
    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        portal_workflow = getToolByName(self.context, 'portal_workflow', None)
        if portal_workflow is None:
            return False
            
        obj = self.event.object
        
        try:
            portal_workflow.doActionFor(obj, self.element.transition)
        except ConflictError, e:
            raise e
        except:
            return False
        
        return True 
        
class WorkflowAddForm(AddForm):
    """An add form for workflow actions.
    """
    form_fields = form.FormFields(IWorkflowAction)
    
    def create(self, data):
        a = WorkflowAction()
        a.transition = data.get('transition')
        return Node('plone.actions.Workflow', a)

class WorkflowEditForm(EditForm):
    """An edit form for workflow rule actions.
    
    Formlib does all the magic here.
    """
    form_fields = form.FormFields(IWorkflowAction)