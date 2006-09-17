from plone.contentrules.rule.rule import Rule as BaseRule

from OFS.SimpleItem import SimpleItem

class Rule(SimpleItem, BaseRule):
    """A Zope 2 version of a rule, subject to acqusition, but otherwise
    identical.
    """
