
## These lines are used to test the module without building the package.
import os
import sys
sys.path.insert( 0, '../src/' )

import co2eq.meeting2
import co2eq.meeting_list2

# Testing single meeting
if False:
  m = co2eq.meeting2.Meeting( name="TEST",
               location={
                 "country": "CZ",
                 "city": "Prague"
               },
               attendee_list="/home/mglt/.local/lib/python3.10/site-packages/co2eq/data/ietf/meeting_attendee_list/json/ietf72.json.gz",
  #             base_output_dir=None,
  #             conf=co2eq.conf.Conf().CONF,  \
               airportDB=True,
               cityDB=True,
               flightDB=True )
  
  m.plot_distribution()
  m.md()

if False:
  meeting_list = [ { 'name' : 'TEST1', 
                     'location' : {
                       'country' : 'CZ',
                       'city' : 'Prague'
                       },
                     'attendee_list' : "./ietf99.json.gz"
                    },
                    { 'name' : 'TEST2', 
                     'location' : {
                       'country' : 'CZ',
                       'city' : 'Prague'
                       },
                     'attendee_list' : "./ietf99.json.gz"
                    }]
  
  ml = co2eq.meeting_list2.MeetingList( name='LIST_TEST', 
                                        meeting_list=meeting_list, 
                                        airportDB=True,
                                        cityDB=True,
                                        flightDB=True )
##  ml.plot_co2eq_distribution( mode='flight', cabin='AVERAGE', on_site=None )
#  ml.plot_co2eq_distribution( mode='flight', cabin='AVERAGE' )

#  ml.plot_attendee_distribution( on_site=None, show=False )
#  banner = ml.md_banner( "http://127.0.0.1:4000/", col_nbr=10, home_url="http://127.0.0.1:4000/" )
#  ml.plot_distribution( )
#  ml.md( on_site_list=[ None ], banner=banner )
#  for m in ml.meeting_list:
#    m.md( on_site_list=[ None ], banner=banner )

  ml.www( mode_list=[ 'flight', 'attendee' ], cabin_list=[ 'AVERAGE' ] )


ietf_list = {
  "name": "IETFTEST",
  "meeting_list": [
    {
      "name": "IETF72",
      "location": {
        "country": "IE",
        "city": "Dublin"
      },
      "attendee_list": "/home/mglt/.local/lib/python3.10/site-packages/co2eq/data/ietf/meeting_attendee_list/json/ietf72.json.gz"
    },
    {
      "name": "IETF73",
      "location": {
        "country": "US",
        "city": "Minneapolis"
      },
      "attendee_list": "/home/mglt/.local/lib/python3.10/site-packages/co2eq/data/ietf/meeting_attendee_list/json/ietf73.json.gz"
    }] }

## Plotting the CO2 emissions for the meeting list (only the figures)
if True:
  print( "--- MeetingList: Building co2 distribution ---" )  
  ml = co2eq.meeting_list2.MeetingList( name=ietf_list[ 'name' ], 
                                        meeting_list=ietf_list[ 'meeting_list' ], 
                                        airportDB=True,
                                        cityDB=True,
                                        flightDB=True )
  ml.plot_co2eq_distribution( mode='flight', cabin='AVERAGE', on_site=None )
    
## Ploting Ratio (only the figures)
if True:
  print( "--- MeetingList: Building ratio_distribution ---" )  
  ml = co2eq.meeting_list2.MeetingList( name=ietf_list[ 'name' ], 
                                        meeting_list=ietf_list[ 'meeting_list' ], 
                                        airportDB=True,
                                        cityDB=True,
                                        flightDB=True )
  ml.plot_attendee_remote_ratio( show=True, print_grid=True, most_present=15 )
  ml.plot_co2eq_remote_ratio( show=True, print_grid=True, most_emitters=15  )

## Plotting the md files an all necessary files for the web site
## md is then converted into HTML files via jekly
if True:
  print( "--- MeetingList: Building the web site ---" )  
  ml = co2eq.meeting_list2.MeetingList( name=ietf_list[ 'name' ], 
                                        meeting_list=ietf_list[ 'meeting_list' ], 
                                        airportDB=True,
                                        cityDB=True,
                                        flightDB=True )

  ml.www( mode_list=[ 'flight', 'attendee' ], cabin_list=[ 'AVERAGE' ] )

