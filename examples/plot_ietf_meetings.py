from co2eq.ietf_meeting import IETFMeeting, IETFMeetingList

## When anything has been generated but th elast meeting
## it makes sense to retrieve all flights for the last meeting before
## actually loading all meetings - this is just an optimization.
#last_meeting = IETFMeeting( 'IETF114' )
#last_meeting.plot_co2eq( mode=None, cluster_key=None, cluster_nbr=None, co2eq=None, cabin=None )
#print( f" average co2eq / passenger / km: {last_meeting.co2eq_per_passenger_per_km( cabin='ECONOMY', co2eq='myclimate' )}" )
## configuration parameters are stored in .env


## building a meeting serie 
ietf_meeting_list = IETFMeetingList( ) 

## building all graphs
ietf_meeting_list.plot_all()


## building web pages in md format
  ## url is the URL under which you have:
  ## * IETF or ALL with figures for all IETFs
  ## * IETF72, IETF73... each individual IETF meetings
  ## Jekyll local installation uses 'http://127.0.0.1:4000/IETF/' as the base URL
  ## gh-pages uses https://mglt.github.io/co2eq/IETF
  ## the leap theme seems to be the only one that generates a TOC
#ietf_meeting_list.www_md( 'http://127.0.0.1:4000/IETF/', toc=False, home_url='http://127.0.0.1:4000/')
ietf_meeting_list.www_md( 'https://mglt.github.io/co2eq/IETF/', toc=False, home_url='https://mglt.github.io/co2eq' )

