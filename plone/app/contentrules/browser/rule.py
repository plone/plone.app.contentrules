from zope.component import getMultiAdapter, getUtilitiesFor, getUtility

from zope.schema.interfaces import IVocabularyFactory
from zope.formlib import form

from Acquisition import aq_parent, aq_inner
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile 
from Products.CMFPlone import PloneMessageFactory as _

from plone.contentrules.engine.interfaces import IRuleAssignmentManager, IRuleStorage
from plone.contentrules.rule.interfaces import IRule, IRuleAction, IRuleCondition

from plone.app.contentrules.rule import Rule
from plone.app.contentrules.browser.formhelper import AddForm, EditForm

from plone.memoize.instance import memoize 

import dummies

class RuleAddForm(AddForm):
    """An add form for rules.
    """
    form_fields = form.FormFields(IRule).omit('elements').omit('__name__')
    label = _(u"Add Rule")
    description = _(u"Add a new rule. Once complete, you can manage the rule's actions and conditions separately")
    form_name = _(u"Configure rule")
    
    def nextURL(self):
        context = aq_parent(aq_inner(self.context))
        url = str(getMultiAdapter((context, self.request), name=u"absolute_url"))
        return url + '/@@rules-controlpanel.html'
    
    def create(self, data):
        rule = Rule()
        form.applyChanges(rule, self.form_fields, data)
        return r

class RuleEditForm(EditForm):
    """An edit form for rules.
    """
    form_fields = form.FormFields(IRule).omit('event').omit('elements').omit('__name__')
    label = _(u"Edit Rule")
    description = _(u"Edit ane existing rule")
    form_name = _(u"Configure rule")
    
    def nextURL(self):
        context = aq_parent(aq_inner(self.context))
        url = str(getMultiAdapter((context, self.request), name=u"absolute_url"))
        return url + '/@@rules-controlpanel.html'

class ManageAssignments(BrowserView):
    """Manage contextual rule assignments
    """
    pass



class ManageElements(BrowserView):
    """Manage elements in a rule
    """
    
    template = ViewPageTemplateFile('templates/manage-elements.pt')
            
    def __call__(self):
        return self.template()
            
    # view @@manage-elements
    
    def view_url(self):
        rule = aq_inner(self.context)
        context = aq_parent(rule)
        url = str(getMultiAdapter((self.context, self.request), name=u"absolute_url"))
        return '%s/++rule++%s/@@manage-elements' % (url, rule.__name__)
    
    def rule_title(self):
        return self.context.title
        
    def rule_description(self):
        return self.context.description
        
    def rule_event(self):
        for e in self._events():
            if e.value == self.context.event:
                return e.token
        return "Unknown event" # should not happen
    
    def actions(self):
        ignored, info = self._elements()
        return self._populate_info(info)
        
    def conditions(self):
        info, ignored = self._elements()
        return self._populate_info(info)
    
    def addable_conditions(self):
        rule = aq_inner(self.context)
        context = aq_parent(rule)
        baseUrl = str(getMultiAdapter((context, self.request), name=u"absolute_url"))
        
        info = []
        for element in utils.allAvailableConditions(rule.event):
            info.append({'title'       : element.title,
                         'description' : element.description,
                         'add_url'    : '%s/++rule++%s/+/%s' % (baseUrl, rule.__name__, element.addview),
                        })
        return info
    
    def addable_actions(self):
        rule = aq_inner(self.context)
        context = aq_parent(rule)
        baseUrl = str(getMultiAdapter((context, self.request), name=u"absolute_url"))
        
        manager = IRuleManager(context)
        info = []
        for element in utils.allAvailableActions(rule.event):
            info.append({'title'       : element.title,
                         'description' : element.description,
                         'add_url'    : '%s/++rule++%s/+/%s' % (baseUrl, rule.__name__, element.addview),
                        })
        return info
        
    def delete_element(self, idx):
        rule = aq_inner(self.context)
        context = aq_parent(rule)
        del rule.elements[idx]
        
    # view @@move-element-up
        
    def move_up(self):
        rule = aq_inner(self.context)
        context = aq_parent(rule)
        idx = int(self.request.get('id'))
        node = rule.elements[idx]
        del rule.elements[idx]
        rule.elements.insert(idx - 1, node)
        self.request.response.redirect(self.view_url())
        return ''
        
    # view @@move-element-down
        
    def move_down(self):
        rule = aq_inner(self.context)
        context = aq_parent(rule)
        idx = int(self.request.get('id'))
        node = rule.elements[idx]
        del rule.elements[idx]
        rule.elements.insert(idx + 1, node)
        self.request.response.redirect(self.view_url())
        return ''
        
    @memoize
    def _events(self):
        eventsFactory = getUtility(IVocabularyFactory, name="plone.contentrules.events")
        return eventsFactory(self.context)
        
    def _populate_info(self, info):
        """Turn a list of info items as returned by _elements() into a list
        of dicts for consumption by the template.
        """
        context = aq_parent(rule)
        
        url = str(getMultiAdapter((context, self.request), name=u"absolute_url"))
        baseUrl = "%s/++rule++%s" % (url, rule.__name__,)
        
        elements = []
        last = len(info) - 1
        for i in range(len(action_info)):
            idx, element, instance = info[i]
            
            upURL = None
            if idx > 0:
                upURL = '%s/@@move-element-up?id=%d' % (baseUrl, idx,)
            
            downURL = None
            if idx < last:
                downURL = '%s/@@move-element-down?id=%d' % (baseUrl, idx,)
        
            editview = None
            if element.editview:
                editview = '%s/%d/%s' % (baseUrl, idx, element.editview,)
            
            elements.append({'title'        : element.title,
                             'description'  : element.description,
                             'edit_url'     : editview,
                             'delete_url'   : '%s/@@delete-element?id=%d' % (baseUrl, idx,),
                             'up_url'       : upURL,
                             'down_url'     : downURL,
                            })
        return elements
        
    @memoize
    def _elements(self):
        """Return a tuple containing condition_info and action_info,
        each a list of tuples containing the index in the rule itself, the
        element configuration, and the instance of the element.
        
        This is a little awkward because the rule API does not enforce an
        ordering of actions and conditions, but we want to make sure that
        the conditions go first in the UI, to simplify things.
        """
        rule = aq_inner(self.context)
        
        condition_info = []
        action_info = []
        
        conditions = {}
        for name, utility in getUtilitiesFor(IRuleCondition):
            conditions[name] = utility
            
        actions = {}
        for name, utility in getUtilitiesFor(IRuleAction):
            actions[name] = utility
        
        nodes = rule.elements
        for idx in range(len(nodes)):
            node = nodes[idx]
            
            if node.name in conditions:
                element = conditions[node.name]
                condition_info.append((idx, element, node.instance,))
            elif node.name in actions:
                element = actions[node.name]
                action_info.append((idx, element, node.instance))                    
            
        return condition_info, action_info