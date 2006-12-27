from zope.component import getMultiAdapter
from zope.formlib import form
import zope.event
import zope.lifecycleevent

from Acquisition import aq_parent, aq_inner

from Products.Five.browser import BrowserView
from Products.Five.formlib.formbase import AddFormBase, EditFormBase

class AddForm(AddFormBase):
    """A base add form for content rule.
    
    Use this for rule elements that require configuration before being added to
    a rule. Element types that do not should use NullAddForm instead.
    
    Sub-classes should define create() and set the form_fields class variable.
    
    Notice the suble difference between AddForm and NullAddform in that the
    create template method for AddForm takes as a parameter a dict 'data':
    
        def create(self, data):
            return MyAssignment(data.get('foo'))
            
    whereas the NullAddForm has no data parameter:
    
        def create(self):
            return MyAssignment()
    """
    
    def nextURL(self):
        rule = aq_parent(aq_inner(self.context))
        context = aq_parent(aq_inner(rule))
        url = str(getMultiAdapter((context, self.request), name=u"absolute_url"))
        return '%s/++rule++%s/@@manage-elements' % (url, rule.__name__)
    
    @form.action("Save")
    def handle_save_action(self, action, data):
        self.createAndAdd(data)
    
    @form.action("Cancel", validator=lambda *args, **kwargs: {})
    def handle_cancel_action(self, action, data):
        nextURL = self.nextURL()
        if nextURL:
            self.request.response.redirect(self.nextURL())
        return ''
        
class NullAddForm(BrowserView):
    """An add view that will add its content immediately, without presenting
    a form.
    
    You should subclass this for rule elements that do not require any 
    configuration before being added, and write a create() method that takes no 
    parameters and returns the appropriate assignment instance.
    """
    
    def __call__(self):
        ob = self.create()
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(ob))
        self.context.add(ob)
        nextURL = self.nextURL()
        if nextURL:
            self.request.response.redirect(self.nextURL())
        return ''
    
    def nextURL(self):
        rule = aq_parent(aq_inner(self.context))
        context = aq_parent(aq_inner(rule))
        url = str(getMultiAdapter((context, self.request), name=u"absolute_url"))
        return '%s/++rule++%s/@@manage-elements' % (url, rule.__name__)
    
    def create(self):
        raise NotImplementedError("concrete classes must implement create()")
    

class EditForm(EditFormBase):
    """An edit form for rule elements.
    """
    
    @form.action("Save", condition=form.haveInputWidgets)
    def handle_save_action(self, action, data):
        if form.applyChanges(self.context, self.form_fields, data, self.adapters):
            zope.event.notify(zope.lifecycleevent.ObjectModifiedEvent(self.context))
            self.status = "Changes saved"
        else:
            self.status = "No changes"
            
        nextURL = self.nextURL()
        if nextURL:
            self.request.response.redirect(self.nextURL())
        return ''
            
    @form.action("Cancel", validator=lambda *args, **kwargs: None)
    def handle_cancel_action(self, action, data):
        nextURL = self.nextURL()
        if nextURL:
            self.request.response.redirect(self.nextURL())
        return ''

    def nextURL(self):
        element = aq_inner(self.context)
        rule = aq_parent(element)
        context = aq_parent(rule)
        url = str(getMultiAdapter((context, self.request), name=u"absolute_url"))
        return '%s/++rule++%s/@@manage-elements' % (url, rule.__name__,)