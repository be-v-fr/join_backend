from django.utils.translation import gettext as _

##### PRIO #####
URGENT = 1
MEDIUM = 2
LOW = 3

PRIORITY = (
(URGENT, _('urgent')),
(MEDIUM, _('medium')),
(LOW, _('low')),
)

##### CATEGORY #####
TECHNICAL_TASK = 1
USER_STORY = 2

CATEGORY = (
(TECHNICAL_TASK, _('technical task')),
(USER_STORY, _('user story')),
)

##### STATUS #####
TO_DO = 1
IN_PROGRESS = 2
AWAIT_FEEDBACK = 3
DONE = 4

STATUS_ALL = (
(TO_DO, _('to do')),
(IN_PROGRESS, _('in progress')),
(AWAIT_FEEDBACK, _('await feedback')),
(DONE, _('done')),
)

STATUS_BASE = (STATUS_ALL[0], STATUS_ALL[-1])