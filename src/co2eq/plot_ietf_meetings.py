from meeting import MeetingList
from conf import CONF

## building a meeting serie 
meeting_list = [
  { 
    'name' : 'meeting_nameq', 
    'location' : { 
      'country' : 'DE', 
      'city' : 'BER',
      'iata' : "BER",
    },
    'attendee_list': [                 
      {  
      "country": "NP" 
      }, 
      { 
      "country": "JP"                       
      },
      {
      "country": "NZ"
      },
      {
      "country": "UK"
      },
      {
      "country": "FR"
      }
    ]                                    
  },
  { 
    'name' : 'meeting_namew', 
    'location' : { 
      'country' : 'DE', 
      'city' : 'BER',
      'iata' : "BER",
    },
    'attendee_list': [                 
      {  
      "country": "NP" 
      }, 
      { 
      "country": "JP"                       
      },
      {
      "country": "NZ"
      },
      {
      "country": "UK"
      },
      {
      "country": "FR"
      }
    ]                                    
  }
]

ietf_meeting_list = MeetingList( name='Test', conf=CONF, meeting_list=meeting_list ) 
ietf_meeting_list.plot_all()
