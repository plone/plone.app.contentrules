from Products.Five.browser import BrowserView

import dummies

class ManageAssignments(BrowserView):
    """Manage contextual rule assignments
    """

    def acquiredRules(self):
        return dummies.DUMMY_ACQUIRED_RULES

    def addableViews(self):
        existing = [ r['ruleDescription']['id']
                     for r in dummies.DUMMY_ACQUIRED_RULES ]
        existing += [ r['ruleDescription']['id']
                      for r in dummies.DUMMY_ASSIGNED_RULES ]
        result = [ {'id': r['id'], 'title': r['title'] }
                   for r in dummies.DUMMY_RULES
                   if r['id'] not in existing ]
        return tuple(result)

    def assignedRules(self):
        return dummies.DUMMY_ASSIGNED_RULES


