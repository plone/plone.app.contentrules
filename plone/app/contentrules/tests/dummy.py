from OFS.SimpleItem import SimpleItem
from zope.interface import implements
from plone.contentrules.rule.interfaces import IRuleElementData

class DummyCondition(SimpleItem):
    implements(IRuleElementData)
    element = "dummy.condition"
    summary = "Dummy condition"
    
class DummyAction(SimpleItem):
    implements(IRuleElementData)
    element = "dummy.action"
    summary = "Dummy action"