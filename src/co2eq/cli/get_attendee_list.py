#!/usr/bin/python3
"""
Take ICANN txt input and generate appropriated JSON files

ICANN input files are txt files with the following format:
country name number of attendees
"""

import json
import sys 
import argparse
import pathlib
import gzip
import requests

from os import listdir
from os.path import join, isfile

#sys.path.insert(0, './../../../countryinfo/countryinfo/')
from countryinfo import CountryInfo

#txt_directory = './ICANN/doc/txt'
#json_directory = './ICANN/doc/json'


def country_name_clean_up( country_name ):
  """ common rules that apply to country_name 
  
  Note that in some cases, it might be better to introduce 
  an altername spelling to tyhe countryInfo data as opposed
  to twick the names.
  """

  country_name = country_name.strip()
  if ' (' in country_name.lower() and ')' in country_name.lower():
    country_name = country_name.replace( ' (', ', ' )
    country_name = country_name.replace( ')', '' )
  ## when the country name is spelt like "Gambia, Republic of"
  ## we transform it in to Republic of, Gambia
  if ',' in country_name and ( "Republic" in country_name or "République" in country_name ):
    l = country_name.split( ',' )
    country_name = f"{l[1].strip()} {l[0].strip()}"
  if 'ivoire' in country_name.lower() :
    country_name = "C\u00f4te d'Ivoire"
  elif country_name.lower() == 'curacao' :
    country_name = "Curaçao"
  elif 'holy see' in country_name.lower() or \
       'vatican' in country_name.lower():
    country_name = "Holy See (Vatican City State)"
  elif 'hong kong' in country_name.lower():
    country_name = "Hong Kong"
  elif 'taipei' in country_name.lower():
    country_name = "Taiwan"
  ## korea is usually understood as replublic of korea
  elif country_name.lower().strip() == 'korea' :
#    ( 'korea' in country_name.lower() and 'republic' in country_name.lower()) :
    country_name = "Republic of Korea"
  elif 'northern' in country_name.lower() and 'ireland' in country_name.lower() :
    country_name = "United Kingdom of Great Britain and Northern Ireland"
  elif 'scotland' in country_name.lower() :
    country_name = "United Kingdom of Great Britain and Northern Ireland"
  if country_name in [ 'no country given', 'No Country Given', 'Global', 'Multiple Countries' ]:
    return None
  return country_name.strip()

def txt2json( txt_file, json_file ):
  """ converts txt_file into a json_file 

  Args:
    txt_file: input file
    json_file: output file
  """

  print( f"processing {txt_file}" )
  attendee_list = []
  with open( txt_file, 'rt', encoding='utf8' ) as f:
    line_list = f.readlines( )
  for line in line_list:
    line = line.strip()
    array = line.split()
    if len( array ) == 0:
      continue
    attendee_nbr = int( array[ -1 ] )
    country_name = ""
    for s in array[:-1]:
      country_name = f"{country_name} {s}"
    country_name = country_name_clean_up( country_name )
    if country_name is None :
      continue
    try:
      print( f"country_name: {country_name}" )  
      country = CountryInfo( country_name )
    except :
      raise ValueError( f"cannot instantiate CountryInfo( {country_name} )" )
    try: 
      iso = country.iso( 2 ) 
    except :
      raise ValueError( f"cannot find iso from CountryInfo( {country_name} )" )
      
    for i in range( attendee_nbr ) :
      attendee_list.append( { 'country' : iso  } )  
#    json_file_name = f"{file_name[:-4]}.json"
#  with open( join( json_directory, json_file_name ), 'wt', encoding='utf8' ) as f:
  with gzip.open( json_file, 'wt', encoding='utf8' ) as f:
    json.dump( attendee_list, f, indent=2 )

#for txt_file_name in listdir( txt_directory ) :
#  if txt_file_name[-3:] != 'txt':
#    continue
#  json_file_name = f"{txt_file_name[:-4]}.json"
#  if isfile( join( json_directory, json_file_name ) ) == False :
#    txt2json( txt_file_name )



ORG_MATCH = { 'huaw' : "Huawei",
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



def ietf_clean_org( org_value ):
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
    for match in ORG_MATCH.keys():
      if isinstance( match, str ):
        if match in org_value:
          org_value = ORG_MATCH[ match ]
          break
      elif isinstance( match, tuple ):
        ## match all members of the tuple
        for m in match :
          if m not in org_value :
            break
        else : ## no break found
          org_value = ORG_MATCH[ match ]
          break
  return org_value



def ietf2json( ietf_meeting, json_file=None ):
  """ return the attendee list in a json format 

  The output is [ { 'country' : <ISO 3166 Code>, 
                    'organization' : <string>
                    'presence' : remote / on-site },
                    ...
                  
                ]"
  Args:
    ietf_meeting : a string or a number. IETF 112 is represented as 
      ietf112, IETF112 or 112.
  """
  if json_file is None:
    json_file = f"./{ietf_meeting}.json.gz"

  try: 
    ietf_nbr = int( ietf_meeting )
  except ValueError:
    ietf_nbr = int( ietf_meeting[ 4 : ] )
  url = f"https://datatracker.ietf.org/api/v1/stats/meetingregistration/?format=json&meeting__number={ietf_nbr}&limit=5000"
  r = requests.get( url )
  json_obj = json.loads( r.content.decode('utf8') )
  ##print( json.dumps( json_obj, indent=2) )
  attendee_list = []
  for attendee in json_obj[ 'objects' ]:
    cc = attendee[ "country_code" ]
    if cc in [ None, 'NA' ]:
      print( "unspecified country: Unable to consider {attendee}" )
      continue
    org =  ietf_clean_org( attendee[ "affiliation" ] )
    pres = attendee[ "reg_type" ]
    if pres not in [ 'remote', 'onsite', 'hackathon_onsite', 'hackathon_remote' ]:
      raise ValueError ( f"Unexpected reg_type in {attendee}" )
    if 'onsite' in pres :
      pres = 'on-site'    
    attendee_list.append( { 'country' : cc, 'organization' : org, 'presence' : pres } )   
  with gzip.open( json_file, 'wt', encoding='utf8' ) as f:
    json.dump( attendee_list, f, indent=2 )


def cli():

  description = """ Builds the json input file for co2eq. """
  parser = argparse.ArgumentParser( description=description )
  parser.add_argument('input', help="necessary input to generate the attendee list" )
  parser.add_argument( '-o', '--output_file', type=pathlib.Path, help="output JSON file" )
  parser.add_argument( '-t', '--template', \
  help="""Define the template. Currenlt possible values are "txt" or "ietf".\n\n   
          - "txt": (default) input designates a file . Each line of the input 
          contains a country and the number 
          of attendees associated to that country. The country can be 
          expressed in various ways, that is the full name or the ISO code. 
          The output file is a JSON file that contains a list where 
          each attendee is represented by a country code.
          - "ietf" : input designates the meeting. 
          \n""" )
  args = parser.parse_args()
  print( args )

  ## trying to guess the template when omitted. 
  if args.template is None:
    if 'ietf' in args.input.lower() :
      args.template = "ietf"
    print( f"template has not been specified: considering --template {args.template}" ) 

  if args.template == "txt":
    input_file = args.input
    if isfile( input_file ) is False :
      raise ValueError( f"Cannot find file {input_file}" )
    if args.output_file is None:
      output_file = pathlib.PurePath( input_file ).with_suffix( '.json.gz' )
      print( f"output_file has not been specified: considering --output_file {output_file}" ) 

  elif args.template == 'ietf' :
    ietf_meeting = args.input   
    if args.output_file is None:
      output_file = f"./{ietf_meeting}.json.gz"
      print( f"output_file has not been specified: considering --output_file {output_file}" ) 
  else: 
    raise ValueError( "Unable to find appropriated template" )
    
  if pathlib.PurePath( output_file ).suffixes != [ '.json', '.gz' ]:
    raise ValueError( f"unexpected output_file {output_file}. Expecting '.json.gz'." )    
  if isfile( output_file ) is True :
      print( f"""ERROR: the ouput_file already exists. Please remove it 
                with rm {output_file} """)

  if args.template == "txt":
    txt2json( input_file, output_file )
  elif args.template == 'ietf' :
    ietf2json( ietf_meeting, output_file )
  else: 
    raise ValueError( "Unable to find appropriated template" )
  


if __name__ == "__main__":
  cli()
