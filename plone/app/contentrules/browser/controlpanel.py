from Products.Five.browser import BrowserView 

DUMMY_RULES = (
    {'id': 'send-email-on-publication',
     'title': 'Send email on publication',
     'trigger': 'object workflow transition',
     'description': 'Send out a notification email to subscribers when the object is published and make a copy of the object in the archives.',
     'enabled': True,
     },
    {'id': 'send-review-notification',
     'title': 'Send review notification',
     'trigger': 'object workflow transition',
     'description': 'Rule for sending out email notification to reviewers.',
     'enabled': True,
     },
    {'id': 'archive-closed-project',
     'title': 'Archive closed projects',
     'trigger': 'object workflow transition',
     'description': 'Move projects to the archive when they are closed.',
     'enabled': False,
     },
    {'id': 'move-on-publish',
     'title': 'Move on publish',
     'trigger': 'object workflow transition',
     'description': 'Move objects to their public location after they are published.',
     'enabled': True,
     },
    {'id': 'notify-admin-on-event-removal',
     'title': 'Notify admin on Event removal',
     'trigger': '(object deleted)',
     'description': 'Notify the administrator when an Event gets deleted.',
     'enabled': False,
     },
    )

DUMMY_RULES_ASSIGNMENTS = {
    'send-email-on-publication': (
        {'object_title': 'Projects', 'path': '/projects',
         'content_icon': 'folder_icon.gif', 'bubble': True, 'enabled': True,},
        {'object_title': 'Management', 'path': '/company/management',
         'content_icon': 'folder_icon.gif', 'bubble': True,  'enabled': True,},
        {'object_title': 'UI Design', 'path': '/teams/uidesign',
         'content_icon': 'folder_icon.gif', 'bubble': True, 'enabled': True,}
        ),
    'move-on-publish': (
        {'object_title': 'Draft', 'path': '/draft', 'content_icon': 'folder_icon.gif', 'bubble': False, 'enabled': True,},
        ),
    }

class ContentRulesControlPanel(BrowserView):
    """Manage rules in a the global rules container
    """

    def registeredRules(self):
        return DUMMY_RULES
    
    def ruleTypesToShow(self):
        dummy = (
            {'id': 'trigger-object-created',
             'title': 'Trigger type: object is created',},
            {'id': 'trigger-object-moved',
             'title': 'Trigger type: object is moved',},
            {'id': 'trigger-object-deleted',
             'title': 'Trigger type: object is deleted',},
            {'id': 'trigger-wf-transition',
             'title': 'Trigger type: object workflow transition',},
            {'id': 'trigger-object-commented',
             'title': 'Trigger type: object is commented on',},
            {'id': 'state-enable',
             'title': 'Enabled',},
            {'id': 'state-disabled',
             'title': 'Disabled',},
            {'id': 'state-rule-assigned',
             'title': 'Rule is being utilized in the portal',},
            {'id': 'state-rule-not-assigned',
             'title': 'Rule is not used anywhere',},
            )
        return dummy
    
    def assignmentsFor(self, ruleid):
        return DUMMY_RULES_ASSIGNMENTS.get(ruleid)