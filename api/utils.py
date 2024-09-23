from django.utils.translation import gettext as _

##### PRIO #####
NULL = 'null'
URGENT = 'Urgent'
MEDIUM = 'Medium'
LOW = 'Low'

PRIORITY = (
(NULL, _('null')),
(URGENT, _('Urgent')),
(MEDIUM, _('Medium')),
(LOW, _('Low')),
)

##### CATEGORY #####
TECHNICAL_TASK = 'Technical Task'
USER_STORY = 'User Story'

CATEGORY = (
(TECHNICAL_TASK, _('Technical Task')),
(USER_STORY, _('User Story')),
)

##### STATUS #####
TO_DO = 'To do'
IN_PROGRESS = 'In progress'
AWAIT_FEEDBACK = 'Await feedback'
DONE = 'Done'

STATUS_ALL = (
(TO_DO, _('To do')),
(IN_PROGRESS, _('In progress')),
(AWAIT_FEEDBACK, _('Await feedback')),
(DONE, _('Done')),
)

STATUS_BASE = (STATUS_ALL[0], STATUS_ALL[-1])