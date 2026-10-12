Introduction
============

plone.app.contentrules provides Plone-specific conditions and actions, as well
as a user interface for plone.contentrules.

Installation
------------

Since version 7.0, this package provides its own GenericSetup profile, ``plone.app.contentrules:default``.
The profile registers the rule storage, the content rules control panel, the "Rules" tab, and the browser layer.
In Plone 6.3, content rules are installed automatically as part of a new site.
Deactivating the add-on removes the control panel, the "Rules" tab, and all rule definitions.

Compatibility with Plone versions
---------------------------------

The 3.x series is intended for usage with Plone 4.3 and up and features
the new content rules UI. Development of this package continues in the
``master`` branch.

For use with versions of Plone earlier than 4.3, use versions <= 2.2.1.
Development of maintenance versions can be found in the ``2.x`` branch.
