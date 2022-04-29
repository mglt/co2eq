meeting_list = [
  { 'name' : 'ICANN555', 
    'location' : { 
      'country' : 'DE',
      'city' : 'BER',
      'iata' : 'BER' 
    }, 
    'attendee_list' : [                 
      {  
      "country": "US" 
      }, 
      { 
      "country": "JP"                       
      },
      {
      "country": "UY"
      },
      {
      "country": "VU"
      },
      {
      "country": "ZW"
      }
    ]
  }
]

from meeting import Meeting, MeetingList
from conf import CONF

icann = MeetingList( 'ICANN', meeting_list=meeting_list, conf=CONF )
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
icann.www_md( 'https://mglt.github.io/co2eq/ICANN/', col_nbr=7, toc=False, home_url='https://mglt.github.io/co2eq/')
