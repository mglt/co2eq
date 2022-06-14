from os.path import join, isfile, isdir
from os.path import join, isfile, isdir
import json
import gzip 
import requests
import pandas as pd
from co2eq.meeting import Meeting, MeetingList
import co2eq.conf 

IETF_MEETING_LIST = [
  { 'name' : 'IETF72', 
    'location' : {
      'country' : 'IE', 
      'city' : 'Dublin'
    }
  }, 
  { 'name' : 'IETF73', 
    'location' : { 
      'country' : 'US', 
      'city' : 'Minneapolis'
    }
  }, 
  { 'name' : 'IETF74', 
    'location' : { 
      'country' : 'US',
      'city' : 'San Francisco',
      'iata' : 'SFO'
    }
  },
  { 'name' : 'IETF75', 
    'location' : { 
      'country' : 'SE',
      'city' : 'Stockholm'
    }
  },
  { 'name' : 'IETF76',
    'location' : { 
      'country' : 'JP', 
      'city' : 'Hiroshima',
      'iata' : 'OSA'          ## Hiroshima is too small
     }
  }, 
  { 'name' : 'IETF77', 
    'location' : {
      'country' : 'US',
      'city' : 'Los Angeles'
    } 
  }, 
  { 'name' : 'IETF78', 
    'location' : { 
      'country' : 'NE', 
      'city' : 'Maastricht', 
      'iata' : 'BRU'          ## Next closest airport  
    }
  }, 
  { 'name' : 'IETF79', 
    'location' : { 
      'country' : 'CN', 
      'city' : 'Beijing'
    }
  }, 
  { 'name' : 'IETF80', 
    'location' : {
      'country' : 'CZ',
      'city' : 'Prague'
    }
  }, 
  { 'name' : 'IETF81', 
    'location' : { 
      'country' : 'CA', 
      'city' : 'Montreal'
    } 
  }, 
  { 'name' : 'IETF82', 
    'location' : { 
      'country' : 'TW', 
      'city' : 'Taipei'
    } 
  }, 
  { 'name' : 'IETF83', 
    'location' : { 
      'country' : 'FR', 
      'city' : 'Paris'
    } 
  }, 
  { 'name' : 'IETF84', 
    'location' : {
      'country' : 'CA', 
      'city' : 'Vancouver'
    } 
  }, 
  { 'name' : 'IETF85', 
    'location' : {
      'country' : 'US', 
      'city' : 'Atlanta'
    }
  }, 
  { 'name' : 'IETF86', 
    'location' : {
      'country' : 'US', 
      'city' : 'Orlando'
    }
  }, 
  { 'name' : 'IETF87', 
    'location' : {
      'country' : 'DE', 
      'city' : 'Berlin'
    } 
  }, 
  { 'name' : 'IETF88', 
    'location' : {
      'country' : 'CA', 
      'city' : 'Vancouver'
    }
  }, 
  { 'name' : 'IETF89', 
    'location' : { 
      'country' : 'GB', 
      'city' : 'London'
    }
  },
  { 'name' : 'IETF90', 
    'location' : {
      'country' : 'CA',
      'city' : 'Toronto'
    }
  }, 
  { 'name' : 'IETF91', 
    'location' : {
      'country' : 'US', 
      'city' : 'Honolulu'
    }
  }, 
  { 'name' : 'IETF92', 
    'location' : {
      'country' : 'US', 
      'city' : 'Dallas', 
      'iata' : 'DFW'
    }
  }, 
  { 'name' : 'IETF93',
    'location' : {
      'country' : 'CZ', 
      'city' : 'Prague', 
    }
  }, 
  { 'name' : 'IETF94',
    'location' : {
      'country' : 'JP', 
      'city' : 'Tokyo', 
    }
  }, 
  { 'name' : 'IETF95',
    'location' : {
      'country' : 'AR', 
      'city' : 'Buenos Aires', 
    }
  }, 
  { 'name' : 'IETF96',
    'location' : {
      'country' : 'DE', 
      'city' : 'Berlin', 
    }
  }, 
  { 'name' : 'IETF97',
    'location' : {
      'country' : 'KR', 
      'city' : 'Seoul', 
    }
  }, 
  { 'name' : 'IETF98',
    'location' : {
      'country' : 'US', 
      'city' : 'Chicago', 
    }
  }, 
  { 'name' : 'IETF99',
    'location' : {
      'country' : 'CZ', 
      'city' : 'Prague', 
    }
  }, 
  { 'name' : 'IETF100',
    'location' : {
      'country' : 'SG', 
      'city' : 'Singapore', 
    }
  }, 
  { 'name' : 'IETF101',
    'location' : {
      'country' : 'GB', 
      'city' : 'London', 
    }
  }, 
  { 'name' : 'IETF102',
    'location' : {
      'country' : 'CA', 
      'city' : 'Montreal', 
    }
  }, 
  { 'name' : 'IETF103',
    'location' : {
      'country' : 'TH', 
      'city' : 'Bangkok', 
    }
  }, 
  { 'name' : 'IETF104',
    'location' : {
      'country' : 'CZ', 
      'city' : 'Prague', 
    }
  }, 
  { 'name' : 'IETF105',
    'location' : {
      'country' : 'CA', 
      'city' : 'Montreal', 
    }
  }, 
  { 'name' : 'IETF106',
    'location' : {
      'country' : 'SG', 
      'city' : 'Singapore', 
    }
  }, 
  { 'name' : 'IETF107',
    'location' : {
      'country' : 'CA', 
      'city' : 'Vancouver', 
    }
  }, 
  { 'name' : 'IETF108',
    'location' : {
      'country' : 'ES', 
      'city' : 'Madrid', 
    }
  }, 
  { 'name' : 'IETF109',
    'location' : {
      'country' : 'TH', 
      'city' : 'Bangkok', 
    }
  }, 
  { 'name' : 'IETF110',
    'location' : {
      'country' : 'CZ', 
      'city' : 'Prague', 
    }
  }, 
  { 'name' : 'IETF111',
    'location' : {
      'country' : 'US', 
      'city' : 'San Fransisco',
      'iata' : 'SFO'
    }
  }, 
  { 'name' : 'IETF112',
    'location' : {
      'country' : 'ES', 
      'city' : 'Madrid', 
    }
  } 
]

ORGANIZATION_MATCH = { 'huaw' : "Huawei",
                       'futurewei' : "Huawei",
                       'cisco' : "Cisco",
                       'ericsson' : "Ericsson",
                       'microsoft' : "Microsoft",
                       'google' : "Google",
                       'juniper' : "Juniper",
                       'orange' : "Orange",
                       ( 'france', 'telecom' ) : "Orange",
                       'francetelecom' : "Orange",
                       'oracle' : "Oracle",
                       'isoc' : "ISOC",
                       ( 'internet', 'society' ) : "ISOC",
                       'akama' : "Akamai",
                       'nist' : "NIST",
                       ( 'dehli', 'institute' ) : "Dehli Institute of Advanced studies",
                       ( 'amity', 'university' ) : "Amity University",
                       'intel'  : "Intel",
                       'verisign' : "Verisign",
                       'salesforce' : "Salesforce",
                       'facebook' : "Facebook",
                       'upsa' : "UPSA",
                       'ntt' : "NTT",
                       'apple' : "Apple",
                       'cloudflare' : "Cloudflare",
                       'nokia' : "Nokia",
                       'amsl' : "IETF",
                       'ietf' : "IETF",
                       'interdigital' : "Interdigital",
                       ( 'internet', 'systems', 'consortium' ) : "ISC",
                       'tencent' : "Tencent",
                       'verizon' : "Verizon",
                       'apnic' : 'APNIC',
                       'zte' : 'ZTE',
                       'yokogawa' : 'Yokogawa',
                       'alcatel' : "Alcatel-Lucent",
                       'lucent' : "Alcatel-Lucent",
                       'samsung' : "Samsung",
                       'nortel' : "Nortel",
                       ( 'british', 'telecom' ) : 'BT',
                       ( 'deutsche', 'telekom' ) : 'DT',
                       'tsinghua' : 'Tsinghua University',
                       'hitachi' : 'Hitachi',
                       'siemens' : 'Siemens',
                       ( 'china', 'mobile' ): 'China Mobile',
                       'icann' : 'ICANN',
                       'comcast' : 'Comcast',
                       'mozilla' : 'Mozilla'
                   }


## generic co2eq = { 'optional_keys' :
##                    origin : { 'street' 
##                               'city'
##                               'region'  
##                               'country'
##                               'iata'
##                     'destination' : { 'street' 
##                                  'city'
##                                  'region'  
##                                  'country' 
##                                  'iata'
##                                  } 
##                      } 

## attendee = { 'presence' : 'on-site', 'not-arrived', 'remote'  optional
##              'organization' :                                 optional 
##              'country' # mandatory
##              'region' 
##              'state'
##              'city'
##              'iata' 
##              'street'


class IETFMeeting ( Meeting ):

  def __init__( self, name:str, base_output_dir=None, \
                conf=co2eq.conf.Conf().CONF,  airportDB=True,\
                cityDB=True, flightDB=True, goclimateDB=True ):
    for meeting in IETF_MEETING_LIST:
      if meeting[ 'name' ] == name:
        self.ietf_nbr = int( name[ 4 : ] )
        location = meeting[ 'location' ]
        break 
    super().__init__( name, location, base_output_dir=base_output_dir, conf=conf, \
                      cityDB=cityDB, flightDB=flightDB, airportDB=airportDB )
    self.attendee_list_html = join( self.output_dir,  'attendee_list.html.gz' )
    self.attendee_list_json = join( self.output_dir,  'attendee_list.json.gz' )
    self.attendee_list = self.get_attendee_list()

#  def get_location( self ):
#    return IETF_LOCATION[ self.name ]
#
#  def attendee_location( self, attendee ):
#    return attendee[ 'country' ]

  def get_attendee_list_html( self ):
    self.logger.info( f"{self.name}: Getting HTML file" )
    if self.ietf_nbr >= 108 :
      url = "https://registration.ietf.org/" + str( self.ietf_nbr ) + "/participants/remote/"
    else:
      url = "https://www.ietf.org/registration/ietf" + str( self.ietf_nbr ) + \
          "/attendance.py"
    r = requests.get( url )
    ## while encoding is always utf-8 in some places r.text did not work
    ## while specifying the encoding seemed to work.
    if self.ietf_nbr <= 73 or self.ietf_nbr >= 89:
      txt = r.text
    else:
      txt = r.content.decode('utf8')
    ## note that IETF web pages for 74 - 93 the html file has an error.
    ## The line 31 indicates colspan=2" which should be colspan="2" instead
    if self.ietf_nbr >= 74 and self.ietf_nbr <= 93:
      txt = txt.replace( "colspan=2\"", "colspan\"=2\"" )
    with gzip.open(self.attendee_list_html, 'wt', encoding="utf8" ) as f:
      f.write( txt )

  def parse_htm_remote( self ) :
    """ parses remote meeting  108, 109, 110, 111 
 
    Parsing function returns an input list for meetings. 
    The attendee_list is a list of attendee JSON object where:
    attendee = { 'country' : ISO3611, 'organization' : string, 'presence' : on-site, remote, not-arrived }
    """
    with gzip.open( self.attendee_list_html, 'rt', encoding="utf8" ) as f:
      dfs = pd.read_html(f.read(), header=0 )
      json_obj = json.loads( dfs[0].to_json( orient="records" ) )
      for attendee in json_obj:
        try:
          attendee[ 'country' ] = attendee.pop( 'Country' )
          attendee[ 'firstname' ] = attendee.pop( 'First Name' )
          attendee[ 'lastname' ] = attendee.pop( 'Last Name' )
          attendee[ 'organization' ] = attendee.pop( 'Organization' )
####          attendee[ 'presence' ] = attendee.pop( 'On-Site' )
        except:
          self.logger.info( f"Cannot create attendee: {attendee}" )
      for attendee in json_obj:
        del attendee[ 'firstname' ]
        del attendee[ 'lastname' ]
        attendee[ 'presence' ] = 'remote'
      return json_obj

  def parse_htm_104( self ):
    """ new IETF 103 meeting """
    with gzip.open( self.attendee_list_html, 'rt', encoding="utf8" ) as f:
      dfs = pd.read_html(f.read(), header=0 )
      json_obj_1 = json.loads( dfs[1].to_json( orient="records" ) )
      for attendee in json_obj_1:
        try:
          attendee[ 'country' ] = attendee.pop( 'In Person Participants - Checked In OnSite.4' )
          attendee[ 'firstname' ] = attendee.pop( 'In Person Participants - Checked In OnSite.2' )
          attendee[ 'lastname' ] = attendee.pop( 'In Person Participants - Checked In OnSite.1' )
          attendee[ 'organization' ] = attendee.pop( 'In Person Participants - Checked In OnSite.3' )
          attendee[ 'presence' ] = attendee.pop( 'In Person Participants - Checked In OnSite' )
          attendee[ 'presence' ] = 'on-site'
        except:
          self.logger.info( f"Cannot create attendee: {attendee}" )

      self.logger.info( f"type json_1:{type(json_obj_1)}" )
      json_obj_2 = json.loads( dfs[2].to_json( orient="records" ) )
      for attendee in json_obj_2:
        try:
          attendee[ 'country' ] = attendee.pop( 'In Person Participants - Not Yet Arrived.4' )
          attendee[ 'firstname' ] = attendee.pop( 'In Person Participants - Not Yet Arrived.2' )
          attendee[ 'lastname' ] = attendee.pop( 'In Person Participants - Not Yet Arrived.1' )
          attendee[ 'organization' ] = attendee.pop( 'In Person Participants - Not Yet Arrived.3' )
          attendee[ 'presence' ] = attendee.pop( 'In Person Participants - Not Yet Arrived' )
          attendee[ 'presence' ] = 'not-arrived'
        except:
          self.logger.info( f"Cannot create attendee: {attendee}" )
      json_obj_3 = json.loads( dfs[3].to_json( orient="records" ) )
      for attendee in json_obj_3:
        try:
          attendee[ 'country' ] = attendee.pop( 'Remote Participants.4' )
          attendee[ 'firstname' ] = attendee.pop( 'Remote Participants.2' )
          attendee[ 'lastname' ] = attendee.pop( 'Remote Participants.1' )
          attendee[ 'organization' ] = attendee.pop( 'Remote Participants.3' )
          attendee[ 'presence' ] = attendee.pop( 'Remote Participants' )
          attendee[ 'presence' ] = 'remote'
        except:
          self.logger.info( f"Cannot create attendee: {attendee}" )

      ## header may appears in each list as an attendee
      for json_obj in [ json_obj_1, json_obj_2, json_obj_3 ] :
        self.logger.debug( f"{json_obj[:5]}" )
        if json_obj[ 0 ][ 'country' ] == 'ISO 3166 Code' :
          del json_obj[ 0 ]
##      header = { "country": "ISO 3166 Code",
##                 "firstname": "First Name",
##                 "lastname": "Last Name",
##                 "organization": "Organization",
##                 "presence": "on-site" }
#      print( f"{json_obj_1 [:5]}" )
##      json_obj_1.remove( header )
##      header[ 'presence' ] = 'not-arrived'
##      json_obj_2.remove( header )
##      header[ 'presence' ] = 'remote'
##      json_obj_3.remove( header )

##      json_obj_1.extend( json_obj_2 )
##      json_obj_1.extend( json_obj_3 )
##      json_obj = json_obj_1
      json_obj_1.extend( json_obj_2 )
      json_obj_1.extend( json_obj_3 )
      for attendee in json_obj_1:
        del attendee[ 'firstname' ]
        del attendee[ 'lastname' ]
      return json_obj_1

  def parse_htm_72( self ):
    with gzip.open( self.attendee_list_html, 'rt', encoding="utf8" ) as f:
      dfs = pd.read_html(f.read(), header=0 )
      if len( dfs ) == 3: ## IETF 74 -92 propose a login to view Profiles
        table_index = 2
      else: ## IETF 72 - 73, and IETF 93 - do not have login
        table_index = 1
      json_obj = json.loads( dfs[ table_index ].to_json( orient="records" ) )
      attendee_list = []
      for attendee in json_obj:
        try:
          ## we use pop in order to avoid creating a new filed. JSON objects
          ## breaks when a new field is added.
          ## note that not renaming will leave the fields unchanged -- as opposed to remove it
          ## this is why we just rename also the firstname and lastname
          attendee[ 'country' ] = attendee.pop( 'ISO 3166 Code' )
          attendee[ 'firstname' ] = attendee.pop( 'First Name' )
          attendee[ 'lastname' ] = attendee.pop( 'Last Name' )
          attendee[ 'organization' ] = attendee.pop( 'Organization' )
          if 'Paid' in attendee.keys(): ## IETF 72 - 79
            attendee[ 'presence' ] = attendee.pop( 'Paid' )
          elif 'On-Site' in attendee.keys(): ## replaces 'Paid' for IETF >= 80
            attendee[ 'presence' ] = attendee.pop( 'On-Site' )
        except:
          self.logger.info( f"Cannot create attendee: {attendee}" )
#      for attendee in json_obj:
#        del attendee[ 'firstname' ]
#        del attendee[ 'lastname' ]
        presence = attendee[ 'presence' ]
        if presence in [ 'Yes', 'Comp', 'Comp - Host' ]:
          presence = 'on-site'
        elif presence == 'Remote':
          presence  = 'remote'
        elif presence == 'No':
          presence = 'not-arrived'
        else:
          raise ValueError( f"unexpected attendee format {attendee}." \
                            f"Expecting 'Yes', 'No' or 'Remote' for presence" )
        organization = self.clean_org( attendee[ 'organization' ] )
        attendee_list.append( { 'country' : attendee[ 'country' ], 
                                'organization' : organization,
                                'presence' : presence } )
      return attendee_list 
#      return json_obj

  def get_attendee_list_json( self ):

    self.logger.info( f"{self.name}: Parsing HTML file" )
    if self.ietf_nbr <= 103 :
      json_obj = self.parse_htm_72()
    elif self.ietf_nbr in [ 108, 109, 110, 111, 112 ] : #remote meetings
      json_obj = self.parse_htm_remote( )
    elif self.ietf_nbr > 103 and self.ietf_nbr <= 107:
      json_obj = self.parse_htm_104( )
    else:
      with gzip.open( self.attendee_list_html, 'rt', encoding="utf8" ) as f:
        dfs = pd.read_html(f.read(), header=0 )
        for i in range( len( dfs ) ):
          print( f"      - dfs[{i}]: {dfs[i]}" )
        raise ValueError ( f"Unable to parse attendees for IETF{self.ietf_nbr}" )
    with gzip.open( self.attendee_list_json, 'wt', encoding="utf8" ) as f:
      f.write( json.dumps( json_obj, indent=2) )


  def clean_org( self, org_value ):
    """ get a more conventional string for Organization """

    if org_value is None:
      return 'Not Provided'
    org_value = org_value.lower()
    if org_value == 'bt': ## special cases where we look at exact match
      org_value = 'BT'
    elif org_value == 'nec':
      org_value = 'NEC'
    elif org_value == 'isc':
      org_value = 'ISC'
    else:
      for match in ORGANIZATION_MATCH.keys():
        if isinstance( match, str ):
          if match in org_value:
            org_value = ORGANIZATION_MATCH[ match ]
            break
        elif isinstance( match, tuple ):
          ## match all members of the tuple
          for m in match :
            if m not in org_value :
              break
          else : ## no break found
            org_value = ORGANIZATION_MATCH[ match ]
            break
    return org_value

  def get_attendee_list( self ):
    if self.attendee_list is not None:
      return self.attendee_list
    if isfile( self.attendee_list_json ) is False:
      if isfile( self.attendee_list_html ) is False:
        self.get_attendee_list_html( )
      self.get_attendee_list_json( )
    with gzip.open( self.attendee_list_json, 'rt', encoding="utf8" ) as f:
      attendee_list = json.loads( f.read() )
      ## removing countries set to None
      for attendee in attendee_list:
        if attendee[ 'country' ]  == 'None':
          attendee_list.remove( attendee )
        ## This is unexplained to me that 'NA' is replace by None
        ## I suspect, this is interpreted as Not Applicable, but thi sneeds to be checked.
        elif attendee[ 'country' ] is None :
          attendee[ 'country' ] = 'NA'
        attendee[ 'organization' ] = self.clean_org( attendee[ 'organization' ] )
    return attendee_list

class IETFMeetingList(MeetingList):

  def __init__( self, name="IETF", conf=co2eq.conf.Conf().CONF, \
                meeting_list=IETF_MEETING_LIST, \
                airportDB=True, cityDB=True, flightDB=True, goclimateDB=True ):
    super().__init__( name, conf=conf, meeting_list=meeting_list )
##    if self.meeting_list is None:
###      min_ietf_nbr =  min( IETF_LOCATION.keys() )
###      max_ietf_nbr = max( IETF_LOCATION.keys() )
###      self.meeting_list = [ min_ietf_nbr + i for i in  range( max_ietf_nbr - min_ietf_nbr + 1 ) ]
##      self.meeting_list = list( IETF_LOCATION.keys() )
##      self.meeting_list.sort( key = lambda meeting_name: int( meeting_name[4:] ) )

  def get_meeting( self, meeting ):
    """ returns a meeting object from various representation used to designate that object """
    
    if isinstance( meeting, Meeting ):
      return meeting
    else:
      name = meeting[ 'name' ]
      location = meeting[ 'location' ]
      if 'attendee_list' in meeting.keys():
        attendee_list = meeting[ 'attendee_list' ]
      else: 
        attendee_list = None
      return IETFMeeting( name, conf=self.conf, airportDB=self.airportDB, \
                          cityDB=self.cityDB, flightDB=self.flightDB,\
                          goclimateDB=self.goclimateDB )
    raise ValueError("Unable to return meeting object from meeting_list" )

