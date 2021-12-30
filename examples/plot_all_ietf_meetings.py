from co2eq.meeting import IETFMeetingList
from conf import CONF

## Plotting all IETF meetings
ietf_meeting_list = IETFMeetingList( conf=CONF ) 
ietf_meeting_list.plot_all()


