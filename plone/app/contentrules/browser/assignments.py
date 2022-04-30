from Acquisition import aq_inner
from Acquisition import aq_parent
from plone.app.contentrules import api
from plone.app.contentrules import PloneMessageFactory as _
from plone.contentrules.engine.interfaces import IRuleAssignmentManager
from plone.contentrules.engine.interfaces import IRuleStorage
from plone.memoize.instance import memoize
from Products.CMFCore.interfaces import ISiteRoot
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory


class ManageAssignments(BrowserView):
    """Manage contextual rule assignments"""

    template = ViewPageTemplateFile("templates/manage-assignments.pt")

    def __call__(self):
        context = aq_inner(self.context)
        request = aq_inner(self.request)
        form = request.form
        status = IStatusMessage(self.request)

        operation = request.get("operation", None)

        if operation == "move_up":
            assignable = IRuleAssignmentManager(context)
            rule_id = request.get("rule_id")
            keys = list(assignable.keys())
            idx = keys.index(rule_id)
            del keys[idx]
            keys.insert(idx - 1, rule_id)
            assignable.updateOrder(keys)
        elif operation == "move_down":
            assignable = IRuleAssignmentManager(context)
            rule_id = request.get("rule_id")
            keys = list(assignable.keys())
            idx = keys.index(rule_id)
            del keys[idx]
            keys.insert(idx + 1, rule_id)
            assignable.updateOrder(keys)
        elif "form.button.AddAssignment" in form:
            rule_id = form.get("rule_id")
            api.assign_rule(self.context, rule_id)
        elif "form.button.Delete" in form:
            rule_ids = form.get("rule_ids", ())
            for r in rule_ids:
                api.unassign_rule(self.context, r)

            status.addStatusMessage(_("Assignments deleted."), type="info")
        elif "form.button.Enable" in form:
            rule_ids = form.get("rule_ids", ())
            for r in rule_ids:
                api.edit_rule_assignment(context, r, enabled=True)

            status.addStatusMessage(_("Assignments enabled."), type="info")
        elif "form.button.Disable" in form:
            rule_ids = form.get("rule_ids", ())
            for r in rule_ids:
                api.edit_rule_assignment(context, r, enabled=False)

            status.addStatusMessage(_("Assignments disabled."), type="info")
        elif "form.button.Bubble" in form:
            rule_ids = form.get("rule_ids", ())
            for r in rule_ids:
                api.edit_rule_assignment(context, r, bubbles=True, enabled=True)

            status.addStatusMessage(_("Changes saved."), type="info")
        elif "form.button.NoBubble" in form:
            rule_ids = form.get("rule_ids", ())
            for r in rule_ids:
                api.edit_rule_assignment(context, r, bubbles=False)

            status.addStatusMessage(_("Changes saved."), type="info")

        return self.template()

    def globally_enabled(self):
        storage = getUtility(IRuleStorage)
        return storage.active

    @memoize
    def view_url(self):
        return self.context.absolute_url() + "/@@manage-content-rules"

    @memoize
    def type_name(self):
        context = aq_inner(self.context)
        fti = context.getTypeInfo()
        return fti.Title()

    @memoize
    def acquired_rules(self):

        # Short circuit if this is the root of the portal
        if ISiteRoot.providedBy(self.context):
            return []

        in_use = {r["id"] for r in self.assigned_rules()}

        storage = getUtility(IRuleStorage)
        events = self._events()

        assignments = []
        context = aq_parent(aq_inner(self.context))

        while context is not None:
            assignable = IRuleAssignmentManager(context, None)
            if assignable is not None:
                for key, assignment in assignable.items():
                    if key not in in_use and assignment.bubbles:
                        rule = storage.get(key, None)
                        if rule is not None:
                            url = "{}/@@manage-content-rules".format(
                                context.absolute_url(),
                            )
                            assignments.append(
                                dict(
                                    id=key,
                                    title=rule.title,
                                    description=rule.description,
                                    trigger=events.get(rule.event, "Unknown"),
                                    url=url,
                                    enabled=(assignment.enabled and rule.enabled),
                                )
                            )
            if ISiteRoot.providedBy(context):
                context = None
            else:
                context = aq_parent(context)

        return assignments

    @memoize
    def assigned_rules(self):
        assignable = IRuleAssignmentManager(self.context)
        storage = getUtility(IRuleStorage)
        events = self._events()

        assignments = []
        for key, assignment in assignable.items():
            rule = storage.get(key, None)
            if rule is not None:
                assignments.append(
                    dict(
                        id=key,
                        title=rule.title,
                        description=rule.description,
                        trigger=events.get(rule.event, "Unknown"),
                        url=self._rule_url(key),
                        bubbles=assignment.bubbles,
                        enabled=assignment.enabled,
                        global_enabled=rule.enabled,
                    )
                )
        return assignments

    def has_rules(self):
        return len(self.assigned_rules()) > 0 or len(self.acquired_rules()) > 0

    def assignable_rules(self):
        in_use = {r["id"] for r in self.assigned_rules()}
        assignable = []
        for key, rule in getUtility(IRuleStorage).items():
            if key not in in_use:
                assignable.append(
                    dict(
                        id=key,
                        title=rule.title,
                        description=rule.description,
                    )
                )
        return assignable

    @memoize
    def _events(self):
        eventsFactory = getUtility(IVocabularyFactory, name="plone.contentrules.events")
        return {e.value: e.token for e in eventsFactory(self.context)}

    def _rule_url(self, key):
        return "{}/++rule++{}/@@manage-elements".format(
            self._portal_url(),
            key,
        )

    @memoize
    def _portal_url(self):
        portal_state = getMultiAdapter(
            (self.context, self.request), name="plone_portal_state"
        )
        return portal_state.portal_url()
