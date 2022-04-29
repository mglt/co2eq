from statistics import mean
import json 
from meeting import MeetingList
from conf import CONF

meeting_list = [
  { 
    'name' : 'meeting_namee', 
    'location' : { 
      'country' : 'DE', 
      'city' : 'BER',
      'iata' : "BER",
    },
    'attendee_list': [                 
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

ietf_meeting_list = MeetingList( name='Test', conf=CONF, meeting_list=meeting_list ) 

## computing average CO2
mode = 'flight'
cluster_key = None #'presence'
cluster_value = None #'on-site'
co2eq = 'myclimate'

## Computing the average effective CO2 per capita: That is CO2 associated to remote
## participants divided by the numbe rof participants
mean_co2eq_per_attendee = {}
co2eq_total = {}
for meeting_dict in ietf_meeting_list.meeting_list :
  meeting = ietf_meeting_list.get_meeting( meeting_dict )
  attendee_nbr = len( meeting.select_attendee_list( cluster_key=cluster_key, cluster_value=cluster_value ) )
  cluster = meeting.cluster_dict( mode=mode, cluster_key=cluster_key, co2eq=co2eq )
  try: 
    co2eq_total[ meeting.name ] = cluster[ cluster_value ]
    mean_co2eq_per_attendee[ meeting.name ] = cluster[ cluster_value ] / attendee_nbr
  except KeyError: ## cluster_value does not exist
    continue

print( f"{cluster_value} Total CO2eq {json.dumps( co2eq_total, indent=2) }" )
print( f"{cluster_value} Per Participant CO2eq {json.dumps( mean_co2eq_per_attendee, indent=2) }" )
print( f"Average onsite CO2 ({mode}, {cluster_key}->{cluster_value}, {co2eq}): {mean(mean_co2eq_per_attendee.values())}" )

## Computing the average number of flight segments per participants
## considering all participants 
## Note that the consideration of a flight segments for remote 
## participants corresponds to a cross-cluster correlation. 
## Probably the easiest way to do so, is to generate a meeting object 
## with the sub selection of participants

mode = 'attendee'
cluster_key = 'flight_segments'
cluster_value = None
co2eq = 'myclimate'

value_dict = {}
for meeting_designation in ietf_meeting_list.meeting_list :
  meeting = ietf_meeting_list.get_meeting( meeting_designation )
  attendee_nbr = len( meeting.select_attendee_list( ) )
  cluster = meeting.cluster_dict( mode=mode, cluster_key=cluster_key, co2eq=co2eq )
  print( f"{meeting_designation}  {json.dumps( cluster, indent=2)}" )
  mean_segments = 0
  for k, v in cluster.items():
    mean_segments += v * int( k )
  value_dict[ meeting_designation ] = mean_segments / attendee_nbr
print( f"{cluster_value} Average flight segments {json.dumps( value_dict, indent=2)}" )
print( f"min average : {min( value_dict.values() )}" )  
print( f"max average : {max( value_dict.values() )}" )  
print( f"{sorted( value_dict.items() , key= lambda item : item[1]  ) }" ) 




