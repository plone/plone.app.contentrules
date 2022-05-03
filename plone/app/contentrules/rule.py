from Acquisition import aq_base
from BTrees.OOBTree import OOSet
from OFS.SimpleItem import SimpleItem
from plone.contentrules.engine.interfaces import IRuleAssignmentManager
from plone.contentrules.engine.interfaces import IRuleStorage
from plone.contentrules.rule.rule import Rule as BaseRule
from Products.CMFCore.interfaces import ISiteRoot
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility
from zope.component import queryUtility


ANNOTATION_KEY = "plone.app.contentrules.ruleassignments"


class Rule(SimpleItem, BaseRule):
    """A Zope 2 version of a rule, subject to acqusition, but otherwise
    identical.
    """

    __name__ = ""

    @property
    def id(self):
        return f"++rule++{self.__name__}"


def get_assignments(rule):
    annotations = IAnnotations(rule)
    # do not use setdefault here as it'll write to the database on read
    return annotations.get(ANNOTATION_KEY, OOSet())


def insert_assignment(rule, path):
    annotations = IAnnotations(rule)
    if ANNOTATION_KEY not in annotations:
        annotations[ANNOTATION_KEY] = OOSet()
    annotations[ANNOTATION_KEY].insert(path)


# Events that keep track of rule-to-assignment mappings
def rule_removed(rule, event):

    storage = queryUtility(IRuleStorage)
    rule_name = rule.__name__

    if storage is None:
        return

    portal = getUtility(ISiteRoot)
    for path in get_assignments(rule):
        container = portal.unrestrictedTraverse(path)
        if container is not None:
            assignable = IRuleAssignmentManager(container, None)
            if assignable is not None and rule_name in assignable:
                del assignable[rule_name]


def container_moved(container, event):

    if event.oldParent is None or event.newParent is None or event.oldName is None:
        return

    assignable = IRuleAssignmentManager(container, None)
    storage = queryUtility(IRuleStorage)

    if assignable is None or storage is None:
        return

    old_path = "{}/{}".format(
        "/".join(event.oldParent.getPhysicalPath()),
        event.oldName,
    )
    new_path = "/".join(container.getPhysicalPath())

    if aq_base(event.object) is not aq_base(container):
        new_path_of_moved = "/".join(event.object.getPhysicalPath())
        old_path = old_path + new_path[len(new_path_of_moved) :]

    for rule_name in assignable.keys():
        rule = storage.get(rule_name, None)
        if rule is not None:
            assignments = get_assignments(rule)
            if old_path in assignments:
                assignments.remove(old_path)
                assignments.insert(new_path)


def container_removed(container, event):

    assignable = IRuleAssignmentManager(container, None)
    storage = queryUtility(IRuleStorage)

    if assignable is None or storage is None:
        return

    path = "/".join(container.getPhysicalPath())
    for rule_name in assignable.keys():
        rule = storage.get(rule_name, None)
        if rule is not None:
            assignments = get_assignments(rule)
            if path in assignments:
                assignments.remove(path)
