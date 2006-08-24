from zope.interface import implements, Interface
from zope import schema
from zope.component import getUtility
from Products.Five import BrowserView

from plone.contentrules.engine.interfaces import IRuleManager
from plone.contentrules.rule.interfaces import IRuleAction
from plone.contentrules.rule.rule import Rule, Node

from zope.formlib import form
from Products.Five.formlib import formbase

class IFooForm(Interface):
    
    foo = schema.TextLine(title=u'Foo')
    bar = schema.TextLine(title=u'Bar')
    
class FooForm(formbase.PageForm):
    form_fields = form.FormFields(IFooForm)
    
    @form.action(u"OK")
    def handle_ok(self, action, data):
        print action, data, self.request.form

class Testing(BrowserView):
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
    
    def __call__(self):
        
        # Clear out any existing rules.
        # We know the context is an IRuleContainer because of the
        # declaration of this view!
        
        manager = IRuleManager(self.context)
        
        for r in manager.listRules():
            manager.removeRule(r)
        
        # The UI may build one of these
        rule = Rule()
        rule.title = "Testing rule"
        rule.description = "Description"
        rule.event = None
        
        # The user may select one of these
        element = getUtility(IRuleAction, name='plone.actions.logger')
        
        # The UI may use a form generated from element.schema, and save
        # the result in one of these
        instance = element.factory()
        instance.loggingLevel = 2000
        
        # The UI would save all elements like so
        rule.elements = (Node('plone.actions.logger', instance),)
        
        # The UI would attach this rule to the context using a rule manager
        manager.saveRule(rule)