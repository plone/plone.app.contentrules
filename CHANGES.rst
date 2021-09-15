Changelog
=========

.. You should *NOT* be adding new change log entries to this file.
   You should create a file in the news directory instead.
   For helpful instructions, please see:
   https://github.com/plone/plone.releaser/blob/master/ADD-A-NEWS-ITEM.rst

.. towncrier release notes start

5.0.0a2 (2021-09-15)
--------------------

Bug fixes:


- Remove cyclic dependency with Products.CMFPlone
  [ericof] (#64)


5.0.0a1 (2021-04-20)
--------------------

Breaking changes:


- Update for Plone 6 with Bootstrap markup
  [andreesg, agitator] (#63)


4.1.6 (2021-01-08)
------------------

Bug fixes:


- Simplify test setup by using the MOCK_MAILHOST_FIXTURE (#59)


4.1.5 (2020-09-26)
------------------

Bug fixes:


- Fixed deprecation warning for ComponentLookupError.
  Fixed deprecation warning for zope.site.hooks.
  Fixed deprecation warning for IObjectEvent from zope.component.
  [maurits] (#3130)
- Fixed test failures on Python 3 with Products.MailHost 4.10.
  [maurits] (#3178)


4.1.4 (2020-04-20)
------------------

Bug fixes:


- Minor packaging updates. (#1)


4.1.3 (2019-11-25)
------------------

Bug fixes:


- fix genericsetup export of properties of rules that have more complex fields such as IDict. (#50)


4.1.2 (2019-10-12)
------------------

Bug fixes:


- Fix file extension condition. [mtrebron] (#48)


4.1.1 (2019-03-21)
------------------

New features:


- Add new action `Version object`.
  [gbastien] (#44)


Bug fixes:

- Fix default value for a msgid [erral] (#42)


4.1 (2018-10-30)
----------------

New features:

- Adapt tests to `Products.GenericSetup >= 2.0` thus requiring at least that
  version.

Bug fixes:

- Migrate all tests to use dexterity
  [pbauer]

- Work around issue where new item is moved before it's completely addeed
  [davisagli]

- Fix all tests with py3 and py2
  [pbauer, alert, davisagli]


4.0.18 (2018-02-04)
-------------------

Bug fixes:

- Add Python 2 / 3 compatibility
  [pbauer]

- Fix test with CMF 2.3. [davisagli]


4.0.17 (2017-07-20)
-------------------

Bug fixes:

- Fix UnicodeEncodeError if portal from name contains Umlauts
  [agitator]


4.0.16 (2017-05-23)
-------------------

Bug fixes:

- Fix action edit form. Previously, changes would not be persisted due
  to a bug.
  [malthe]


4.0.15 (2017-05-06)
-------------------

Bug fixes:

- Ensure error message is an unicode object
  [mtrebron]

- Cleanup: isort, autopep8, manual formatting.
  [jensens]

- Cleanup: update code to follow Plone styleguide.
  [gforcada]


4.0.14 (2017-04-02)
-------------------

Bug fixes:

-  Fix issue where content rules edit forms were broken because of move of
   getIcon from @@plone to @@plone_layout
   [datakurre]


4.0.13 (2016-12-30)
-------------------

Bug fixes:

- In browser tests, specify the buttons to be clicked by their name instead of their index.
  [thet]

- Fix import location for Products.ATContentTypes.interfaces.
  [thet]


4.0.12 (2016-11-10)
-------------------

Bug fixes:

- Add coding header to python files.
  [gforcada]

4.0.11 (2016-08-17)
-------------------

Fixes:

- Use zope.interface decorator.
  [gforcada]

- Replace docstring mentions of Formlib with z3c.form
  [staeff]

4.0.10 (2015-11-26)
-------------------

Fixes:

- Update Site Setup link in all control panels (fixes https://github.com/plone/Products.CMFPlone/issues/1255)
  [davilima6]

- Declare i18n_domain="plone" in zcml files to be able to extract messages
  for translation.
  [vincentfretin]


4.0.9 (2015-10-28)
------------------

Fixes:

- CSRF fix: safe write on read.
  [gforcada]


4.0.8 (2015-09-20)
------------------

- Fix i18n in mail.pt
  [vincentfretin]

- Pull email_charset from the configuration registry instead of site properties
  [esteele]

4.0.7 (2015-09-11)
------------------

- Use z3c.form for custom email-action form template.
  Fixes https://github.com/plone/Products.CMFPlone/issues/892
  [pbauer]


4.0.6 (2015-07-18)
------------------

- Use MockMailHost of Plone for tests
  [tomgross]

- Make configlets titles consistent across the site, first letter capitalized
  [sneridagh]


4.0.5 (2015-06-05)
------------------

- Move to z3c.form
  [vangheem]


4.0.4 (2015-05-30)
------------------

- Removed CMFDefault dependency
  [tomgross]


4.0.3 (2015-05-04)
------------------

- I18n fixes.
  [vincentfretin]

- pat-modal pattern has been renamed to pat-plone-modal
  [jcbrand]

4.0.2 (2015-03-20)
------------------

- Nothing changed yet.


4.0.1 (2015-03-11)
------------------

- Fetch email settings from registry instead of properties.
  Refs PLIP 10359.
  [jcerjak, khink]

- Fix control panel to work with Plone 5 Modals
  [vangheem]


4.0.0 (2014-10-23)
------------------

- Ported tests to plone.app.testing
  [tomgross]

- Registered the copy event so rules can now be triggered for it.
  [alecghica]

- Integration of the new markup update and CSS for both Plone and Barceloneta
  theme. This is the work done in the GSOC Barceloneta theme project.
  [albertcasado, sneridagh]


3.0.7 (2014-04-13)
------------------

- Do not write on read
  [vangheem]


3.0.6 (2014-01-27)
------------------

- Make sure CHANGES.rst is included in distributions.
  [esteele]


3.0.5 (2014-01-27)
------------------

- Fixed 3.0.4 regression: add/move/remove events where not handled
  anymore on discussion items.
  [thomasdesvenain]

- Fixed reordering of actions / conditions.
  This occured when 'jq' was not defined as 'jQuery'.
  [thomasdesvenain]

- User that manage a rule can now allow actions executed by this rule
  to recursively trigger other rules.
  For example, if you have a rule that automatically publish added content,
  and an other rule that sends an email when a content is published,
  if autopublish rule is marked as 'cascading', then send mail rule will be triggered.
  [thomasdesvenain]

- Mail action: if string interpolation of recipient gives several times
  the same email address,
  the email is sent only once to this recipient.
  [thomasdesvenain]

- Workaround ``KeyError: context`` for unicode TALES expressions in content
  rules by providing the expression ``context``. This was triggered by a
  TALES expression such as ``u'string:${portal_url}``.
  [davidjb]


3.0.4 (2013-08-13)
------------------

- When we assign a rule, it is enabled by default and is applied to subfolders.
  When we apply a rule to subfolders, it is enabled if it wasn't.
  [thomasdesvenain]

- Provides an API to easily deal with rules assignment management.
  [thomasdesvenain]

- Do not display Rules action unless some Content Rules are defined.
  [runyaga]

- Fix overlay acting funky on the delete action
  [vangheem]

- Move, Removed and Added handlers are not launched anymore
  on non contentish objects.
  This fixes plone upgrades - content rules where launched on tools.
  [thomasdesvenain]

- Fixed i18n
  [jianaijun]


3.0.3 (2013-05-30)
------------------

- Any event can use the tales condition [thomasdesvenain]

- Remove handler for 'User removed' event [thomasdesvenain]


3.0.2 (2013-05-23)
------------------

- Fix for Plone 4.3: fixed enable back content rules after having disabled it.
  [thomasdesvenain]

- Import step depends on workflow step
  so that rules can manage specific transitions / states of profile.
  [thomasdesvenain]

- Add stub nextURL method to
  plone.app.contentrules.browser.adding.RuleAdding to prevent
  security WARNING message on startup:
  "Init Class plone.app.contentrules.browser.adding.RuleAdding has
  a security declaration for nonexistent method 'nextURL'"
  [smcmahon]

- Content rules can handle user events [Julien Marinescu, kiorky]

- Any event can use the email handler  [Julien Marinescu, kiorky]


3.0.1 (2013-04-06)
------------------

- Use single quotes instead of double to avoid breaking translation
  [ericof]

- Fix multi assignment of rules
  [ericof]


3.0 (2013-03-05)
----------------

- Improve management pages user interface :

  - Improve and ajaxify rules table. Avoids scrolling and page reloads.
  - Improve rules table filter (multiple selection, more readable).
  - Improve content rules forms usability.
    We are redirected to edit form after a rule has been added.
  - Add form and Edit form are now consistent.
  - Notify user by many ways when a rule is not assigned anywhere yet.
  - We can assign a rule on whole site by a simple button.
  - Ajaxify conditions and actions reordering and removing.
  - Focus on elements after adding an action or a condition.
  - Improve rule edit pages breadcrumbs.
  - Added tests.
    [vsomogyi, thomasdesvenain, vangheem
    contribution wimbou,
    made @ploneconf2012 sprint]


2.2.1 (2013-01-01)
------------------

- Remove KSS dependency.
  [davisagli]


2.2.0 (2012-10-16)
------------------

- Unified the site setup html structure
  [TH-code]


2.1.9 (2012-08-30)
------------------

- Change mail template to use hex for curly brackets so that it doesn't barf when
  used with chameleon. This is a short term fix until https://github.com/malthe/chameleon/issues/88
  is appropriately fixed.
  [eleddy]

- Notify user with error message instead of a core dump if they set up a content
  mail action without the mailer set up. Prevents users from throwing computer out
  of window when they click save and all their hard entered data is gone.
  [eleddy]


2.1.8 (2012-08-11)
------------------

- Adding a content rule is not handled by 'added' rule...
  Fixes infinite loop on adding a content rule.
  [thomasdesvenain]

- ContainerModified event is excluded from 'modified' event handling.
  This avoids for example adding a comment to lauch 'modified' rules registered for it.
  [thomasdesvenain]


2.1.7 (2012-08-04)
------------------

- Added an option in email action
  to exclude user who did the action from recipients.
  [thomasdesvenain]


2.1.6 (2012-07-02)
------------------

- Avoid hard dependency on Archetypes.
  [davisagli]

- Fixed portaltype condition made
  type creation fail in portal_types.
  [thomasdesvenain]

- Don't trigger modified actions if the event was
  for adding or removing content. Fixes #12461
  [do3cc]

- Logger action: Default values that make sense
  for "Logger name" (Plone) and "Logging level" (20).
  [kleist]


2.1.5 (2012-04-15)
------------------

- Fixed <link /> element wasn't closed in controlpanel.
  [mjpieters]

2.1.4 (2012-01-04)
------------------

- Fix missing CMF Permissions declaration in ZCML declaration (Julien Stegle)
  [encolpe]

- Fixed wrong error plone message after a failure on a delete content rule.
  [thomasdesvenain]

2.1.3 - 2011-06-19
------------------

- Fixed i18n regression caused by the pep8 cleanup.
  [vincentfretin]


2.1.2 - 2011-05-12
------------------

- If email content rule 'From' field interpolation gives empty string,
  from is site from address.
  [thomasdesvenain]

- Import IEndRequestEvent from zope.publisher instead of zope.app.publication
  [davisagli]

- Rules execution filter is no more based on event context,
  but in rule assignment context.
  This allows the same rule to be executed on different objects during the same request,
  including during the same test.
  [thomasdesvenain]

- Fixed: When two or more objects are initialized during the same request,
  'Object added' content rule handler is executed only once.
  Refs https://dev.plone.org/plone/ticket/11706.
  [thomasdesvenain]

- Add MANIFEST.in.
  [WouterVH]

- Internationalization fix on local rules management screen.
  [thomasdesvenain]

- Use site_url instead of deprecated portal_url.
  [WouterVH]

- Code cleanup and some PEP8.
  [WouterVH]


2.1.1 - 2011-04-03
------------------

- Dynamic behavior is fixed on rules controlpanel, including rules list filter.
  Refs http://dev.plone.org/plone/ticket/10831.
  [thomasdesvenain]


2.1.0 - 2011-01-03
------------------

- Depend on ``Products.CMFPlone`` instead of ``Plone``.
  [elro]

- Use plone.uuid to look up content UUIDs.
  [toutpt, davisagli]

- Protect content rules management views using the
  "Content rules: Manage rules" permission, instead of the generic
  "Manage portal".
  [davisagli]

- Do not force to send mails in same transaction if mail queuing is on.
  [thomasdesvenain]


2.0.6 - 2011-01-03
------------------

- Protect content rules management views using the
  "Content rules: Manage rules" permission, instead of the generic
  "Manage portal".
  [davisagli]

- Do not force to send mails in same transaction if mail queuing is on.
  [thomasdesvenain]


2.0.5 - 2010-11-06
------------------

- Added TALES expression condition. This closes
  http://dev.plone.org/plone/ticket/9939.
  [thomasdesvenain]


2.0.4 - 2010-10-27
------------------

- Added missing ``</thead>`` tag.
  [swampmonkey]

- Fixed typo on logger message field description.
  [thomasdesvenain]


2.0.3 - 2010-09-28
------------------

- Internationalize event trigger types.
  [thomasdesvenain]

- Added user login variable '&u' to use in logger action message template.
  [thomasdesvenain]


2.0.2 - 2010-09-20
------------------

- Internationalize some values on management pages.
  [thomasdesvenain]


2.0.1 - 2010-09-09
------------------

- Raises an ImportError in generic setup import if the value for the "event"
  attribute in contentrules.xml rule element can't be imported.
  [thomasdesvenain]

- Fix duplicate rule filter crashed at site root level in Acquisition Wrapper
  case. This closes http://dev.plone.org/plone/ticket/10597.
  [thomasdesvenain]

- Mail action doesn't add an error log when recipient list is empty,
  it just doesn't send the mail.
  [thomasdesvenain]

- Fix for Chameleon compatibility.
  [vangheem]


2.0 - 2010-07-18
----------------

- Update license to GPL version 2 only.
  [hannosch]

- Code cleanup and some PEP8.
  [hannosch]


2.0b4 - 2010-06-13
------------------

- Avoid deprecation warnings under Zope 2.13.
  [hannosch]

- Updated to use five.formlib.
  [hannosch]


2.0b3 - 2010-04-12
------------------

- Fix control panel templates to show the prefs portlet correctly again. This
  closes http://dev.plone.org/plone/ticket/10419.
  [davisagli]


2.0b2 - 2010-02-17
------------------

- Updated @@manage-content-rules to the recent markup conventions.
  References http://dev.plone.org/plone/ticket/9981.
  [spliter]

- Updated mail.pt to follow the recent markup conventions.
  References http://dev.plone.org/plone/ticket/9981.
  [spliter]

- Add "stop executing after this rule" checkbox to edit page of content rule.
  Fixes http://dev.plone.org/plone/ticket/8396.
  [MatthewWilkes]


2.0b1 - 2010-01-11
------------------

- Allow '@' in site from name. Fixes http://dev.plone.org/plone/ticket/9780.
  [smcmahon]


2.0a2 - 2009-12-27
------------------

- Declare package dependencies and replace zope.thread by the standard
  libraries threading module.
  [hannosch]

- Prepend mail messages with ``\n`` to avoid interpretation of first
  line as a mail header.
  [smcmahon]

- Renamed label_contentrules_rule_enabled by
  label_contentrules_rule_enabled_question in manage-assignments.pt.
  It conflicted with label_contentrules_rule_enabled in
  plone/app/contentrules/browser/templates/controlpanel.pt
  [vincentfretin]

- Don't include <q> tag in title_contentrules_assigned message.
  [vincentfretin]


2.0a1 - 2009-11-14
------------------

- Use zope.container and zope.browser in favor of zope.app dependencies.
  [hannosch]

- Change mailing send action to use "immediate=True" so that we can catch
  SMTPException. See note with code.
  [smcmahon]

- Fixed typo in manage-assignments.pt, so the disable button was not properly
  translated.
  [vincentfretin]

- Log error rather than fail with exception on MailHostError in mail action.
  [smcmahon]

- Use plone.stringinterp for adaptable string substitution in mail action.
  Plip #9256.
  [smcmahon]

- Removed SecureMailHost dependency.
  [alecm]

- Adjusted some import statements to use the new zope.container.
  [hannosch]


1.1.7 - 2010-09-20
------------------

- Fixed untranslatable content types in @@manage-content-rules. This closes
  http://dev.plone.org/plone/ticket/9778
  [vincenfretin]

- Fixed some duplicated msgids with different defaults.
  There is no new strings to translate.
  See http://dev.plone.org/plone/ticket/9633
  [vincenfretin]


1.1.6 - 2009-05-16
------------------

- Add check to see if getTypeInfo can be None (which is a valid value)
  [tesdal]

- Changed the simplepublish test to use a copy instead of a move action.
  The move action causes the content item to be moved away while editing
  it and causes a NotFound error. In Plone 3 this is hidden by the
  customized NotFound handling.
  [hannosch]

- Fixed GenericSetup tests layer to not pollute the general test
  environment.
  [hannosch]

- Modified a macro call in contentrules-pageform.pt for forwards
  compatibility with Zope 2.12.
  [davisagli]

- Fixed a SyntaxError in test_configuration.
  [hannosch]


1.1.1 - 2008-04-18
------------------

- Added proper unicode handling to mail action. This closes
  http://dev.plone.org/plone/ticket/7650.
  [hannosch]

- Made the GS import handlers more tolerant in case the storage utility
  is missing. This closes http://dev.plone.org/plone/ticket/8133.
  [hannosch]

- Changed wording on the IMailAction interface to remove a reference to a
  newly created item, since the action can be used on existing content
  as well. This closes http://dev.plone.org/plone/ticket/8225.
  [hannosch]


1.1 - 2008-04-20
----------------

- Ensure that if a contentrules.xml step is imported twice, conditions and
  actions are not duplicated.
  Fixes http://dev.plone.org/plone/ticket/8027
  [optilude]

- Fix invalid leading space in all 'Up to Site Setup' links.
  [wichert]


1.1.0a1 - 2008-03-09
--------------------

- Fixed a small bug related to getTypeInfo() being acquired.
  http://dev.plone.org/plone/ticket/7385
  [optilude]

- Fixed bug causing content rule actions/conditions to not be properly
  saved.
  http://dev.plone.org/plone/ticket/7909
  [optilude]

- Merge PLIP 204 - GenericSetup support. A contentrules.xml file can now
  be used to import and export rule definitions and assignments.
  [optilude]


1.0.5 - 2008-01-03
------------------

- Made absolute_url() work properly on the custom adding views. This is
  necessary for the <base /> URL to be set correctly.
  [optilude]

- Made absolute_url() work across the namespace traversal adapters for
  rules, actions and conditions, at time resorting to some serious
  Cowboy Development.
  [optilude]

- Adjusted tests for different payload in newer kss versions.
  [hannosch]


1.0 - 2007-08-17
----------------

- Added i18n markup for the confirm_icon.gif alternate text. This closes
  http://dev.plone.org/plone/ticket/7062.
  [hannosch]

- Changed the portal type condition to use the ReallyUserFriendlyTypes
  vocabulary. This closes http://dev.plone.org/plone/ticket/6911.
  [hannosch]
