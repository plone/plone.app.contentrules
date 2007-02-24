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
     'trigger': 'object deleted',
     'description': 'Notify the administrator when an Event gets deleted.',
     'enabled': False,
     },
    {'id': 'notify-owner-on-comment',
     'title': 'Send discussion notification',
     'trigger': 'object is commented on',
     'description': 'Send email to the object owner when his object receives a comment.',
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

DUMMY_ACQUIRED_RULES = ( 
    {'ruleDescription': DUMMY_RULES[5], 'isActive': False },
    {'ruleDescription': DUMMY_RULES[3], 'isActive': True },
    )

DUMMY_ASSIGNED_RULES = (
    {'ruleDescription': DUMMY_RULES[0], 'enabled': True, 'bubble': True },
    {'ruleDescription': DUMMY_RULES[1], 'enabled': True, 'bubble': False },
    {'ruleDescription': DUMMY_RULES[4], 'enabled': True, 'bubble': True },
    )