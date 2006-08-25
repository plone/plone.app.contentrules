from plone.contentrules.rule.rule import Rule as BaseRule

from Acquisition import Explicit

class Rule(Explicit, BaseRule):
    """A Zope 2 version of a rule, subject to acqusition, but otherwise
    identical.
    """