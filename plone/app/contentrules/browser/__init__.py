from Products.Five.browser import BrowserView
from Acquisition import aq_chain
class TestingView(BrowserView):
    
    def debug(self):
        import pdb; pdb.set_trace()
        
    def check(self, obj):
        return aq_chain(obj)