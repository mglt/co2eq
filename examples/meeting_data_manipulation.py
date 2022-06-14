from statistics import mean
import json 
from co2eq.ietf_meeting import IETFMeeting, IETFMeetingList
from conf import CONF


CONF[ 'OUTPUT_DIR' ] = "/home/emigdan/gitlab/ietf/co2eq/examples/IETF"

# Example 1: Getting the Total CO2 Emissions
## retrieving the Total amount of CO2 for a meeting computed with go climate
for meeting_name in [ 'IETF101', 'IETF102', 'IETF103', 'IETF104', 'IETF105', 'IETF106' ]:
  meeting = IETFMeeting( meeting_name, conf=CONF )
  goclimate = meeting.cluster_dict( mode='flight', cluster_key=None, co2eq='goclimate' )
  myclimate = meeting.cluster_dict( mode='flight', cluster_key=None, co2eq='myclimate' )
  print( f"{meeting_name}" )
  print( f"  - {goclimate} CO2 (Kg)" ) 
  print( f"  - {myclimate} CO2 (Kg)" ) 

# Example 2: Comparing Total Co2 emissions with a provided numbers
## comparing co2eq estimations versus Jay's numbers
jay_co2 = { 'IETF101' : 3508000, 
            'IETF102' : 2859000, 
            'IETF103' : 5328000, 
            'IETF104' : 4111000, 
            'IETF105' : 2974000,
            'IETF106' : 6433000 }

## building a dictionary with all values expressed in tonnes of CO2
co2_results = {}
for meeting_name in jay_co2.keys():
  meeting = IETFMeeting( meeting_name, conf=CONF )
  goclimate = meeting.cluster_dict( co2eq='goclimate' )[ 'total co2eq' ]
  myclimate = meeting.cluster_dict( co2eq='myclimate' )[ 'total co2eq' ] 
  co2_results[ meeting_name ] = [ jay_co2[  meeting_name ], goclimate, myclimate ]

print(f"Total CO2 ('on-site' and 'remote' versus Jay's results" )
print( f"| meeting | Jay (t CO2) | Go Climate (t CO2) | My Climate (t CO2) |" )
print( f"|---------|-------------|--------------------|--------------------|" )
for k,v in co2_results.items():
#  print( f"v : {v}")
  delta = [ ( i - v[0] ) / v[0] * 100 for i in v ]  
#  print( f"delta : {delta}")
  print( f"| {k} | {v[0] / 1000:.2f}     | "\
         f"{v[1] / 1000:.2f} [{delta[1]:.2f}%]   | "\
         f"{v[2] / 1000:.2f} [{delta[2]:.2f}%]   |" )
print('\n')

## Example 3:  Comparing 'on-site' Co2 emissions with a provided numbers
co2_results = {}
for meeting_name in jay_co2.keys():
  meeting = IETFMeeting( meeting_name, conf=CONF )
  goclimate = meeting.cluster_dict( cluster_key='presence', co2eq='goclimate' )[ 'on-site' ]
  myclimate = meeting.cluster_dict( cluster_key='presence', co2eq='myclimate' )[ 'on-site' ]
  co2_results[ meeting_name ] = [ jay_co2[  meeting_name ], goclimate, myclimate ]

print(f"'on-site' CO2 versus Jay's results" )
print( f"| meeting | Jay (t CO2) | Go Climate (t CO2) | My Climate (t CO2) |" )
print( f"|---------|-------------|--------------------|--------------------|" )
for k,v in co2_results.items():
#  print( f"v : {v}")
  delta = [ ( i - v[0] ) / v[0] * 100 for i in v ]  
#  print( f"delta : {delta}")
  print( f"| {k} | {v[0] / 1000:.2f}     | "\
         f"{v[1] / 1000:.2f} [{delta[1]:.2f}%]  | "\
         f"{v[2] / 1000:.2f} [{delta[2]:.2f}%]  |" )



ietf_meeting_list = IETFMeetingList( conf=CONF ) 

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




