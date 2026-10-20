Add "Object contents reordered" as a content rule event.

Reordering a folder was the one content change no rule could observe:
``plone.folder``'s ``moveObjectsByDelta`` ends in ``notifyContainerModified``
and emits nothing else — no add, no remove, no move — while ``modified`` has
excluded ``IContainerModifiedEvent`` since 2012 so that adding a comment to a
page does not fire "modified" rules registered on that page.

``IContainerModifiedEvent`` is now selectable as a rule event. It fires for
reordering only: ``zope.container`` emits ObjectAdded/ObjectRemoved *before* the
container event, so an add or a remove claims the one that follows it. Rules
bound to ``IObjectModifiedEvent`` are unaffected — dispatch is restricted to
rules that name the container event, so the 2012 behaviour is kept.
