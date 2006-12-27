from zope.app.schema.vocabulary import IVocabularyFactory
from zope.interface import implements
from zope.schema.vocabulary import SimpleVocabulary

from Products.CMFCore.utils import getToolByName

class RolesVocabulary(object):
    """Vocabulary factory for roles in the portal
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        context = getattr(context, 'context', context)
        mtool = getToolByName(context, 'portal_membership')
        items = [ (r, r) for r in mtool.getPortalRoles() ]
        items.sort()
        return SimpleVocabulary.fromItems(items)

RolesVocabularyFactory = RolesVocabulary()

class GroupsVocabulary(object):
    """Vocabulary factory for groups in the portal
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        context = getattr(context, 'context', context)
        mtool = getToolByName(context, 'portal_groups')
        items = [ (g.getGroupId(), g.getGroupName()) for g in mtool.listGroups() ]
        items.sort()
        return SimpleVocabulary.fromItems(items)
        
GroupsVocabularyFactory = GroupsVocabulary()
        
class WorkflowTransitionsVocabulary(object):
    """Vocabulary factory for workflow transitions
    """
    implements(IVocabularyFactory)
    
    def __call__(self, context):
        context = getattr(context, 'context', context)
        wtool = getToolByName(context, 'portal_workflow')
        
        transitions = []
        dup_list = {}
        for wf in wtool.objectValues():
            transition_folder = getattr(wf, 'transitions', None)
            if transition_folder is not None:
                for transition in transition_folder.objectValues():
                    key = '%s:%s' % (transition.id, transition.title,)
                    if not dup_list.has_key(key):
                        transitions.append(transition)
                    dup_list[key] = True
        items = [(s.title, s.getId()) for s in transitions]
        items.sort()
        return SimpleVocabulary.fromItems(items)

WorkflowTransitionsVocabularyFactory = WorkflowTransitionsVocabulary()