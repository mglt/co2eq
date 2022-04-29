from meeting import MeetingList
from conf import CONF

def get_meeting_list(data):
  ietf_meeting_list = MeetingList( name=data['name'], conf=CONF, meeting_list=[ data ] ) 
  ietf_meeting_list.plot_all()
