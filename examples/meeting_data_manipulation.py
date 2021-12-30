from statistics import mean
import json 
from co2eq.meeting import IETFMeetingList
from conf import CONF


ietf_meeting_list = IETFMeetingList( conf=CONF ) 

## computing average CO2
mode = 'flight'
cluster_key = 'presence'
cluster_value = 'on-site'
co2eq = 'myclimate'

## Computing the average effective CO2 per capita: That is CO2 associated to remote
## participants divided by the numbe rof participants
value_dict = {}
for meeting_designation in ietf_meeting_list.meeting_list :
  meeting = ietf_meeting_list.get_meeting( meeting_designation )
  attendee_nbr = len( meeting.select_attendee_list( cluster_key=cluster_key, cluster_value=cluster_value ) )
  cluster = meeting.cluster_dict( mode=mode, cluster_key=cluster_key, co2eq=co2eq )
  try: 
    value_dict[ meeting_designation ] = cluster[ cluster_value ] / attendee_nbr
  except KeyError: ## cluster_value does not exist
    continue

print( f"{cluster_value} CO2eq {json.dumps( value_dict, indent=2) }" )
print( f"Average onsite CO2 ({mode}, {cluster_key}->{cluster_value}, {co2eq}): {mean(value_dict.values())}" )

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
print( f"{sorted( value_dict.items() , key key= lambda item : item[1]  ) }" ) 




