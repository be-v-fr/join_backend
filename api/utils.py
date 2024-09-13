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

##### COLORS #####
PERSON_COLORS = (
    (1, _('#FDDC2F')),
    (2, _('#33DA81')),
    (3, _('#E98366')),
    (4, _('#C27177')),
    (5, _('#42F9B9')),
    (6, _('#2AEC8B')),
    (7, _('#6DD44A')),
    (8, _('#C7ACC0')),
    (9, _('#309CF4')),
    (10, _('#B663F3')),
    (11, _('#b579d2')),
    (12, _('#809283')),
    (13, _('#58AC47')),
    (14, _('#2FB287')),
    (15, _('#2AFDC3')),
    (16, _('#D2FA60')),
    (17, _('#A8EE51')),
    (18, _('#A9DDC7')),
    (19, _('#FE68C4')),
    (20, _('#DC3DF5')),
    (21, _('#05CDD7')),
    (22, _('#E07D47')),
    (23, _('#8EA906')),
    (24, _('#36B3F0')),
    (25, _('#BF59F2')),
)