from OFS.SimpleItem import SimpleItem
from plone.contentrules.rule.interfaces import IRuleElementData
from plone.uuid.interfaces import IAttributeUUID
from zope.interface import implementer
from zope.interface.interfaces import IObjectEvent


@implementer(IRuleElementData)
class DummyCondition(SimpleItem):
    element = "dummy.condition"
    summary = "Dummy condition"


@implementer(IRuleElementData)
class DummyAction(SimpleItem):
    element = "dummy.action"
    summary = "Dummy action"


@implementer(IObjectEvent)
class DummyEvent:
    def __init__(self, object):
        self.object = object


class DummyRule:
    def __init__(self, name="dummy"):
        self.__name__ = name


@implementer(IAttributeUUID)
class DummyNonArchetypesContext:
    pass
