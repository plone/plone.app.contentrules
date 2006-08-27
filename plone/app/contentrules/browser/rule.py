from zope.component import getMultiAdapter, getUtilitiesFor

from zope.formlib import form

from Acquisition import aq_parent, aq_inner
from Products.Five.browser import BrowserView 

from plone.contentrules.engine.interfaces import IRuleManager
from plone.contentrules.rule.interfaces import IRule, IRuleAction, IRuleCondition

from plone.app.contentrules.rule import Rule
from plone.app.contentrules.browser.formhelper import AddForm, EditForm

class RuleAddForm(AddForm):
    """An add form for rules.
    """
    form_fields = form.FormFields(IRule).omit('elements').omit('__name__')
    
    def nextURL(self):
        context = aq_parent(aq_inner(self.context))
        url = str(getMultiAdapter((context, self.request), name=u"absolute_url"))
        return url + '/@@manage-content-rules'
    
    def create(self, data):
        r = Rule()
        r.title = data.get('title')
        r.description = data.get('description')
        r.event = data.get('event')
        return r

class RuleEditForm(EditForm):
    """An edit form for rules.
    """
    form_fields = form.FormFields(IRule).omit('event').omit('elements').omit('__name__')
    
    def nextURL(self):
        context = aq_parent(aq_inner(self.context))
        url = str(getMultiAdapter((context, self.request), name=u"absolute_url"))
        return url + '/@@manage-content-rules'

class ManageRules(BrowserView):
    """Manage rules in a context
    """
    # view @@manage-rules
    
    def rule_info(self):
        manager = IRuleManager(self.context)
        rules = []
        baseUrl = str(getMultiAdapter((self.context, self.request), name=u"absolute_url"))
        for k, r in manager.items():
            rules.append({'title'        : r.title,
                          'description'  : r.description,
                          'edit_url'     : '%s/++rule++%s/edit.html' % (baseUrl, k),
                          'delete_url'   : '%s/++rule++%s/@@delete-rule' % (baseUrl, k),
                          'elements_url' : '%s/++rule++%s/@@manage-elements' % (baseUrl, k),
                          })
        return rules
   
    # view @@delete-rule
        
    def delete_rule(self):
        rule = aq_inner(self.context)
        context = aq_parent(aq_inner(rule))
        manager = IRuleManager(context)
        del manager[rule.__name__]
        url = str(getMultiAdapter((context, self.request), name=u"absolute_url"))
        self.request.response.redirect("%s/@@manage-content-rules" % (url,))
        return ''
        
class ManageElements(BrowserView):
    """Manage elements in a rule
    """
            
    # view @@manage-elements
    
    def element_info(self):
        rule = aq_inner(self.context)
        context = aq_parent(rule)
        
        url = str(getMultiAdapter((context, self.request), name=u"absolute_url"))
        baseUrl = "%s/++rule++%s" % (url, rule.__name__,)
        
        elements = rule.elements
        info = []
        
        conditions = {}
        for name, utility in getUtilitiesFor(IRuleCondition):
            conditions[name] = utility
            
        actions = {}
        for name, utility in getUtilitiesFor(IRuleAction):
            actions[name] = utility
        
        last = len(elements) - 1
        for idx in range(len(elements)):
            node = elements[idx]
            
            isCondition = False
            isAction = False
            element = None
            
            if node.name in conditions:
                element = conditions[node.name]
                isCondition = True
            elif node.name in actions:
                element = actions[node.name]
                isAction = True
                
            if element is None:
                continue
                
            upURL = None
            if idx > 0:
                upURL = '%s/@@move-element-up?id=%d' % (baseUrl, idx,)
            downURL = None
            if idx < last:
                downURL = '%s/@@move-element-down?id=%d' % (baseUrl, idx,)
                
            info.append({'title'        : element.title,
                         'description'  : element.description,
                         'edit_url'     : '%s/%d/%s' % (baseUrl, idx, element.editview,),
                         'delete_url'   : '%s/@@delete-element?id=%d' % (baseUrl, idx,),
                         'up_url'       : upURL,
                         'down_url'     : downURL,
                         'is_action'    : isAction,
                         'is_condition' : isCondition,
                        })
        return info
    
    def addable_conditions(self):
        rule = aq_inner(self.context)
        context = aq_parent(rule)
        baseUrl = str(getMultiAdapter((context, self.request), name=u"absolute_url"))
        
        manager = IRuleManager(context)
        info = []
        for element in manager.getAvailableConditions(rule.event):
            info.append({'title'       : element.title,
                         'description' : element.description,
                         'add_url'    : '%s/++rule++%s/+element/%s' % (baseUrl, rule.__name__, element.addview),
                        })
        return info
    
    def addable_actions(self):
        rule = aq_inner(self.context)
        context = aq_parent(rule)
        baseUrl = str(getMultiAdapter((context, self.request), name=u"absolute_url"))
        
        manager = IRuleManager(context)
        info = []
        for element in manager.getAvailableActions(rule.event):
            info.append({'title'       : element.title,
                         'description' : element.description,
                         'add_url'    : '%s/++rule++%s/+element/%s' % (baseUrl, rule.__name__, element.addview),
                        })
        return info
        
    # view @@delete-element
        
    def delete_element(self):
        rule = aq_inner(self.context)
        context = aq_parent(rule)
        idx = int(self.request.get('id'))
        del rule.elements[idx]
        url = str(getMultiAdapter((context, self.request), name=u"absolute_url"))
        self.request.response.redirect('%s/++rule++%s/@@manage-elements' % (url, rule.__name__))
        return ''
        
    # view @@move-element-up
        
    def move_up(self):
        rule = aq_inner(self.context)
        context = aq_parent(rule)
        idx = int(self.request.get('id'))
        node = rule.elements[idx]
        del rule.elements[idx]
        rule.elements.insert(idx - 1, node)
        url = str(getMultiAdapter((context, self.request), name=u"absolute_url"))
        self.request.response.redirect('%s/++rule++%s/@@manage-elements' % (url, rule.__name__))
        return ''
        
    # view @@move-element-down
        
    def move_down(self):
        rule = aq_inner(self.context)
        context = aq_parent(rule)
        idx = int(self.request.get('id'))
        node = rule.elements[idx]
        del rule.elements[idx]
        rule.elements.insert(idx + 1, node)
        url = str(getMultiAdapter((context, self.request), name=u"absolute_url"))
        self.request.response.redirect('%s/++rule++%s/@@manage-elements' % (url, rule.__name__))
        return ''