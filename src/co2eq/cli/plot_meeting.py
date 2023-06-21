import os
import pathlib
import json
import gzip
import pkg_resources
import argparse
import co2eq.meeting
import co2eq.ietf_meeting
#from co2eq.ietf_meeting import IETFMeeting, IETFMeetingList


##IETFMeeting( 'IETF114' )
##last_meeting.plot_co2eq( mode=None, cluster_key=None, cluster_nbr=None, co2eq=None, cabin=None )
##print( f" average co2eq / passenger / km: {last_meeting.co2eq_per_passenger_per_km( cabin='ECONOMY', co2eq='myclimate' )}" )
##
## building a meeting serie
##ietf_meeting_list = IETFMeetingList( )
##
## building all graphs
##ietf_meeting_list.plot_all()



DATA_DIR = pkg_resources.resource_filename( 'co2eq', 'data' )

def get_json_obj( file_path ):
  """ opens th e.json or .json.gz and returns the content as an object

  """
  suffixes = pathlib.PurePath( file_path ).suffixes
  print( f"get_json_obj: file_path {file_path} / suffixes: {suffixes}")
  if suffixes == [ '.json', '.gz']:
    with gzip.open( file_path, 'rt', encoding="utf8" ) as f: 
      obj = json.load( f )
  else:
    with open( file_path, 'rt', encoding="utf8" ) as f: 
      obj = json.load( f )
  return obj 

def meeting_list_conf_from_meeting_type( meeting_type ):
  """ returns the meeting_list_conf from the meeting type """
  meeting_list_conf = os.path.join( DATA_DIR, meeting_type.lower(), 'meeting_list_conf.json.gz' )
  meeting_list_conf = get_json_obj( meeting_list_conf  )
  ## updating the path of the attende_list with the full path
  for i in range( len( meeting_list_conf[ 'meeting_list' ]) ):
    partial_path = meeting_list_conf[ 'meeting_list' ][ i ][ 'attendee_list' ]  
    meeting_list_conf[ 'meeting_list' ][ i ][ 'attendee_list' ] = os.path.join( DATA_DIR, partial_path )
  return meeting_list_conf


def get_ascii( arg_value ):
  """ returns the argument of type ascii or None 

  The main issue is that args returns "'string'" for the input "string".
  """

  if arg_value is not None:
    arg_value = arg_value[ 1 : -1 ]
  return arg_value

def plot_meeting( output_dir='./co2eq_output', meeting_type=None, \
                  meeting_list_conf=None, meeting_name=None, \
                  meeting_location_iata=None, meeting_attendee_list=None ):

  ## meeting_list_conf contains the description of the list of meetings
  ## For ICANN and IETF meetings, this information is known by the 
  ## package and does not need to be provided.
  ## That configuration can be indicated by the --meeting_type or 
  ## directly by the --meeting_name
  ## Note that meeting_name is only present when a single meeting is plot.
  if meeting_list_conf is None:
    if meeting_type is not None :
      meeting_list_conf = meeting_list_conf_from_meeting_type( meeting_type )
    ## meeting_type is set to None    
    elif meeting_name is not None :
      if 'ietf' in meeting_name.lower() :
        meeting_list_conf = meeting_list_conf_from_meeting_type( 'ietf' )
      elif 'icann' in meeting_name.lower() :
        meeting_list_conf = meeting_list_conf_from_meeting_type( 'icann' )
  else:
    meeting_list_conf = get_json_obj( meeting_list_conf  )

  if meeting_list_conf is None:
    meeting_list_name = None
    meeting_list = None
  else: 
    meeting_list_name = meeting_list_conf[ 'name' ]
    meeting_list = meeting_list_conf[ 'meeting_list' ]

  ## To plot a single meeting, we need  to provide the 
  ## following arguments:
  ##   {'name' : 'ICANN66',
  ##    'location' : {
  ##      'country' : 'Canada',
  ##      'city' : 'Montreal',
  ##      'iata' : 'YUL' },
  ##    'attendee_list' : './ICANN/doc/json/icann66_YUL.json'
  ##  }
  ## setting attendee_list 

  ## meeting_name is supposed to be an individual meeting.
  ## in the case of ICANN and IETF meetings, meeting_name 
  ## set to ICANN or IETF is interpreted as the full list.
  ## we already derived the meeting_list_conf, so we only 
  ## need to set the  meeting_name to None, to indicate the 
  ## full list of meeting is considered.
  if meeting_name is not None and meeting_name.lower() in [ 'icann', 'ietf' ]:
    meeting_name = None
  ## unless a specific meeting is specified, the full list of meeting is considered.
  if meeting_name is None:
    if meeting_list_name is not None and meeting_list is not None:
      ## when meeting_list_name and meeting_list are defined
      ## we have everything to plot_all
      meeting_list = co2eq.meeting.MeetingList( meeting_list_name, meeting_list=meeting_list, \
        base_output_dir=output_dir )
      meeting_list.plot_all( )
      meeting_list.www_md( f"https://mglt.github.io/co2eq/{meeting_list_name}/", col_nbr=7, toc=True, \
                           home_url='https://mglt.github.io/co2eq/')
    else:
      raise ValueError( "A meeting_name or a meeting_list_conf MUST be specified" )
  else:
    ## a specific meeting is requested  
    meeting_conf = { 'name' : meeting_name, 
                      'location' : { 'country' : None,
                                     'city' : None, 
                                     'iata' : meeting_location_iata },
                      'attendee_list': meeting_attendee_list }
#    print( f"DEBUG: The following meeting configuration is provided by command line: {meeting_conf}" ) 

    ## when arguments have not been provided, we try to retrieve them from the 
    ## meeting_list provided by meeting_list_conf when possible.
    ## m_list identifies the potential meeting in the list
    if meeting_list is not None:
      m_list = None
      for m in meeting_list :
        if m[ 'name' ].lower()  == meeting_name.lower():
          m_list = m
          break
#      print( f"DEBUG: The following configuration has been found from (meeting_list): {m_list}" ) 
    if meeting_conf[ 'location' ][ 'iata' ] is None:
      if m_list is None : 
        raise ValueError( """Cannot retrieve the meeting location. Either provide it
                          via the --meeting_list_conf or specify it with the 
                          --meeting_location_iata option. """ )
      else:
        meeting_conf[ 'location' ] = m_list[ 'location' ]
          
    if meeting_conf[ 'attendee_list' ] is None:
      if m_list is None : 
        raise ValueError( """Cannot retrieve the meeting location. Either provide it
                          via the --meeting_list_conf or specify it with the 
                          --meeting_attendee_list option. """ )
      else:
        meeting_conf[ 'attendee_list' ] = m_list[ 'attendee_list' ]
    
    ## The only reason we need a different treatment for IETF is when the 
    ## attendee_list has not been provided in the package in which case it
    ## needs to be retrieved from the IETF web site 
    if 'ietf' in meeting_conf[ 'name' ].lower():
      m = co2eq.meeting.IETFMeeting( **meeting_conf, base_output_dir=output_dir )
    else:
      m = co2eq.meeting.Meeting( **meeting_conf, base_output_dir=output_dir )
    print( f"Processing meeting {m.name} -- {meeting_conf}, {output_dir}" )
    for mode in [ None, 'distance', 'flight', 'attendee' ]:
      for cluster_key in [ None, 'country', 'flight_segment_number', 'subregion' ]:
        m.plot_co2eq( mode=mode, cluster_key=cluster_key, cluster_nbr=15)


def cli():

  description = """Computes CO2eq emissions for a meeting or a serie of meetings"""
  parser = argparse.ArgumentParser( description=description )
  parser.add_argument('-o', '--output_dir', type=pathlib.Path, default='./co2eq_output',\
    help=""""output directory. The default output directory is ./co2eq_output.
      The structure of the directories are as follow:

      a) when meeting_list_conf is provided
      output_dir
        +- meeting_list_name
          +- meeting_list_name
          +- meeting_name_1
          ...
          +- meeting_name_n

      b) when meeting_list_conf is not provided

      output_dir
        +- meeting_name_1
        ...
        +- meeting_name_n
    """ )
  parser.add_argument('-t', '--meeting_type', type=ascii, \
    help="""Specifies the type of the meeting. The type of the meeting is usefull to
      indicate some default parameters. Currenlty the following types have been
      defined: IETF for IETF meetings and ICANN for ICANN meetings.""" )   
  parser.add_argument('-c', '--meeting_list_conf', type=pathlib.Path,\
    help="""The file that describes the meetings. This argument is mandatory to be 
    specified when the CO2 is computed for a serie of meetings. When that parameter
    is unspecified, the --meeting_type determine the default values 
    data/ietf/meeting_list_conf.json  or data/icann/meeting_list_conf.json.

    The meeting_list_conf file is a json or json.gz file that looks as shown below:

    { 'name' = 'ICANN', 
      'meeting_list' = [
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
        } ]
    }


    """ )
  parser.add_argument('-n', '--meeting_name', type=ascii, \
    help="""Indicates the name of the meeting. co2eq computes CO2 emission of a 
      single meeting OR the CO2 emissions associated to a serie of meetings. The
      specification of the meeting name indicates that CO2 emissions are computed
      for a single meeting as opposed to the serie of meetings. When the 
      meeting_list_conf is specified, the meeting name is looked in the 
      meeting_list_conf and the attendee list is taken from that file.
      When meeting_list_conf is not specified, the attendee_list parameter MUST be
      specified.  
      For IETF meeting, the convention is to specifie the name as IETFXX with XX being
      the number of the meeting. For ICANN meeting the convention is to specify 
      the name as ICANNXX with XX being the number of the meeting.""" )
  parser.add_argument('-l', '--meeting_location_iata', type=ascii, \
    help="""The location of the meeting. The location MUST be expressed as a IATA code.""" )
  parser.add_argument('-a', '--meeting_attendee_list', type=pathlib.Path,\
    help="""The file that provides the list of attendees of a given meeting. 
      The specification of that file indicates that a single meeting is considered. 
      This option MUST be combined with --meeting_name.""")
    
  args = parser.parse_args()
  print( f"args: {args}" )

  ## Converting arguments provided by argparse into an appropriate format
  ## The main purpose is to convert the input "'string'" into "string"
  output_dir = args.output_dir
  meeting_list_conf = args.meeting_list_conf 
  meeting_type = get_ascii( args.meeting_type )
  meeting_name = get_ascii( args.meeting_name )
  meeting_location_iata = get_ascii( args.meeting_location_iata )
  meeting_attendee_list = args.meeting_attendee_list

  plot_meeting( output_dir=output_dir, meeting_type=meeting_type, \
                meeting_list_conf=meeting_list_conf, meeting_name=meeting_name, \
                meeting_location_iata=meeting_location_iata,\
                meeting_attendee_list=meeting_attendee_list )


     
          
        
