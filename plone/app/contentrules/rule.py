from plone.contentrules.rule.rule import Rule as BaseRule

from Acquisition import Explicit, Implicit

class Rule(Implicit, BaseRule):
    """A Zope 2 version of a rule, subject to acqusition, but otherwise
    identical.
    """
    
    def __getitem__(self, key):
        return self.elements[self._key(key)].instance.__of__(self)

    def get(self, key, default=None):
        try:
            key = self._key(key)
            return self.elements[key].instance.__of__(self)
        except (IndexError, KeyError,):
            return default

    def values(self):
        return [x.instance.__of__(self) for x in self.elements]

    def items(self):
        i = []
        idx = 0
        for n in self.elements:
            i.append((idx, n.instance.__of__(self)),)
            idx += 1
        return i