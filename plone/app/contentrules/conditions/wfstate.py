from persistent import Persistent
from OFS.SimpleItem import SimpleItem

from zope.interface import implements, Interface
from zope.component import adapts
from zope.formlib import form
from zope import schema

from plone.contentrules.rule.interfaces import IExecutable, IRuleConditionData
from plone.contentrules.rule.rule import Node

from plone.app.contentrules.browser.formhelper import AddForm, EditForm 

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _

class IWorkflowStateCondition(IRuleConditionData):
    """Interface for the configurable aspects of a workflow state condition.
    
    This is also used to create add and edit forms, below.
    """
    
    wf_state = schema.Choice(title=u"Workflow state",
                            description=u"The short name (id) of the workflow state",
                            required=True,
                            vocabulary="plone.app.vocabularies.WorkflowStates")
         
class WorkflowStateCondition(SimpleItem):
    """The actual persistent implementation of the workflow state condition element.py.
    """
    implements(IWorkflowStateCondition)
    
    wf_state = u''

class WorkflowStateConditionExecutor(object):
    """The executor for this condition.
    """
    implements(IExecutable)
    adapts(Interface, IWorkflowStateCondition, Interface)
         
    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        portal_workflow = getToolByName(self.context, 'portal_workflow', None)
        if portal_workflow is None:
            return False
        state = portal_workflow.getInfoFor(self.context, 'review_state', None)
        if state is None:
            return False
        return state == self.element.wf_state
        
class WorkflowStateAddForm(AddForm):
    """An add form for workflow state conditions.
    """
    form_fields = form.FormFields(IWorkflowStateCondition)
    label = _(u"Add Workflow State Condition")
    description = _(u"A workflow state condition can restrict rules to objects in particular workflow states")
    form_name = _(u"Configure element")
    
    def create(self, data):
        c = WorkflowStateCondition()
        c.wf_state = data.get('wf_state')
        return Node('plone.conditions.WorkflowState', c)

class WorkflowStateEditForm(EditForm):
    """An edit form for portal type conditions
    
    Formlib does all the magic here.
    """
    form_fields = form.FormFields(IWorkflowStateCondition)
    label = _(u"Edit Workflow State Condition")
    description = _(u"A workflow state condition can restrict rules to objects in particular workflow states")
    form_name = _(u"Configure element")