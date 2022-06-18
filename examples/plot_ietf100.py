from co2eq.ietf_meeting import IETFMeeting

## Ploting a single IETF meeting
ietf_meeting = IETFMeeting( name='IETF100' ) 
for cluster_key in [ None, 'country', 'organization', 'presence', 'flight_segment_number' ]:
  ietf_meeting.plot_co2eq( mode=[ 'flight', 'distance' ], cluster_key=cluster_key, cluster_nbr=15)
  ietf_meeting.plot_co2eq( mode='attendee', cluster_key=cluster_key, cluster_nbr=15)

## generating md page
ietf_meeting.md()
