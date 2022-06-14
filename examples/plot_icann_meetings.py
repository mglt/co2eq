
meeting_list = [
  { 'name' : 'ICANN55', 
    'location' : { 
      'country' : 'Morocco',
      'city' : 'Marrakesh',
      'iata' : 'RAK' }, 
    'attendee_list' : './ICANN/doc/json/icann55_RAK.json'
  },
  { 'name' : 'ICANN56',
    'location' : {
      'country' : 'Finland', 
      'city' : 'Helsinki', 
      'iata' : 'HEL' }, 
    'attendee_list' : './ICANN/doc/json/icann56_HEL.json'
  },
  { 'name' : 'ICANN57', 
    'location' : {
      'country' : 'India', 
      'city' : 'Hyderabad',
      'iata' : 'HYD' },
    'attendee_list' : './ICANN/doc/json/icann57_HYD.json'
  }, 
  { 'name' : 'ICANN58', 
    'location' : {
      'country' : 'Denmark', 
      'city' : 'Copenhagen', 
      'iata' : 'CPH' },
    'attendee_list' : './ICANN/doc/json/icann58_CPH.json'
  },
  { 'name' : 'ICANN59',
    'location' : {
      'country' : 'South Africa', 
      'city' : 'Johannesburg ',
      'iata' : 'JNB' },
    'attendee_list' : './ICANN/doc/json/icann59_JNB.json'
  },
  { 'name' : 'ICANN60', 
    'location' : {
      'country' : 'United Arab Emirates', 
      'city' : 'Abu Dhabi', 
      'iata' : 'AUH' },
    'attendee_list' : './ICANN/doc/json/icann60_AUH.json'
  },
  { 'name' : 'ICANN61', 
    'location' : {
      'country' : 'Puerto Rico', 
      'city' : 'San Juan', 
      'iata' : 'SJU' }, 
    'attendee_list' : './ICANN/doc/json/icann61_SJU.json'
  },
  { 'name' : 'ICANN62', 
    'location' : {
      'country' : 'Panama', 
      'city' : 'Panama', 
      'iata' : 'PTY' },
    'attendee_list' : './ICANN/doc/json/icann62_PTY.json'
  },
  { 'name' : 'ICANN63', 
    'location' : {
      'country' : 'Spain', 
      'city' : 'Barcelona', 
      'iata' : 'BCN' },
    'attendee_list' : './ICANN/doc/json/icann63_BCN.json'
  },
  { 'name' : 'ICANN64', 
    'location' : {
      'country' : 'Japan', 
      'city' : 'Osaka', 
      'iata' : 'OSA' },
    'attendee_list' : './ICANN/doc/json/icann64_KIX.json'
  },
  { 'name' : 'ICANN65', 
    'location' : {
      'country' : 'Morocco',
      'city' : 'Marrakesh',
      'iata' : 'RAK' }, 
    'attendee_list' : './ICANN/doc/json/icann65_RAK.json'
  },
  { 'name' : 'ICANN66', 
    'location' : {
      'country' : 'Canada', 
      'city' : 'Montreal', 
      'iata' : 'YUL' },
    'attendee_list' : './ICANN/doc/json/icann66_YUL.json'
  }  
]

from co2eq.meeting import Meeting, MeetingList

meeting_list = meeting_list[ :2 ]

## ======= illustrative =======
## This is not necessary to generate teh meeting objects 
## however, this is usefull to adjust the locations
for meeting in meeting_list :
##  meeting.build_co2eq_data( )
  m = Meeting( **meeting )
  print( f"Processing meeting {m.name}" )
  for mode in [ None, 'distance', 'flight', 'attendee' ]:
    for cluster_key in [ None, 'country', 'flight_segment_number' ]:
      m.plot_co2eq( mode=mode, cluster_key=cluster_key, cluster_nbr=15)
## ========================

## If meeting are not generated, it generates them, 
icann = MeetingList( 'ICANN', meeting_list=meeting_list )
## building all graphs
icann.plot_all()


## building web pages in md format
## url is the URL under which you have:
## * ICANN or ALL with figures for all ICANN meetings
## * ICAN55, ICANN66... each individual ICANN meetings
## Jekyll local installation uses 'http://127.0.0.1:4000/IETF/' as the base URL
## gh-pages uses https://mglt.github.io/co2eq/ICANN
## the leap theme seems to be the only one that generates a TOC
##icann.www_md( 'http://127.0.0.1:4000/ICANN/', col_nbr=7, toc=False, home_url='http://127.0.0.1:4000/')
## For the real web site
# icann.www_md( 'https://mglt.github.io/co2eq/ICANN/', col_nbr=7, toc=False, home_url='https://mglt.github.io/co2eq/')
