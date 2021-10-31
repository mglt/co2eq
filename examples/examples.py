from co2eq.meeting import IETFMeeting, IETFMeetingList, get_flight
# from meeting import IETFMeeting, IETFMeetingList, get_flight
from co2eq.flight_utils import FlightDB
from conf import CONF

## For a single query, the simplest way to request a flight
origin = 'PAR'      # IATA city code
destination = 'LAX' # IATA airport code
flightDB = FlightDB( conf=CONF )
flight = flightDB.select_flight( origin, destination )

print( "The simplest way to retireve a flight!" )
print( flight )

## Retrieving a flight from origin to destination
## get_flight may perform requests at different dates in case, it does not get any response. 
## in this example, the databases are generated and passed to the requests as argument to avoid being instantiated for each request.
flight = get_flight( conf=CONF,  origin='PAR', destination='LAX' )
print( "A simple way to retrieve a flight!" )
print( flight )

## Ploting a single IETF meeting
ietf_meeting = IETFMeeting( name='IETF100', conf = CONF ) 
for cluster_key in [ None, 'country', 'organization', 'presence', 'flight_segments' ]:
  ietf_meeting.plot_co2eq( cluster_key=cluster_key, cluster_nbr=15)


## Plotting all IETF meetings
ietf_meeting_list = IETFMeetingList( conf=CONF ) 
ietf_meeting_list.plot_all()


