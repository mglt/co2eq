#!/usr/bin/python3
"""
Take ICANN txt input and generate appropriated JSON files

ICANN input files are txt files with the following format:
country name number of participants
"""

import json
import sys 
import argparse
import pathlib

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
  participant_list = []
  with open( txt_file, 'rt', encoding='utf8' ) as f:
    line_list = f.readlines( )
  for line in line_list:
    line = line.strip()
    array = line.split()
    if len( array ) == 0:
      continue
    participant_nbr = int( array[ -1 ] )
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
      
    for i in range( participant_nbr ) :
      participant_list.append( { 'country' : iso  } )  
#    json_file_name = f"{file_name[:-4]}.json"
#  with open( join( json_directory, json_file_name ), 'wt', encoding='utf8' ) as f:
  with open( json_file, 'wt', encoding='utf8' ) as f:
    json.dump( participant_list, f, indent=2 )

#for txt_file_name in listdir( txt_directory ) :
#  if txt_file_name[-3:] != 'txt':
#    continue
#  json_file_name = f"{txt_file_name[:-4]}.json"
#  if isfile( join( json_directory, json_file_name ) ) == False :
#    txt2json( txt_file_name )

 
def cli():

  description = """ Builds the json input file for co2eq. """
  parser = argparse.ArgumentParser( description=description )
  parser.add_argument('input_file', type=pathlib.Path, help="input file" )
  parser.add_argument( '-o', '--output_file', type=pathlib.Path, help="output JSON file" )
  parser.add_argument( '-t', '--template', default="txt",  const="txt",\
  action='store_const', \
  help="""Define the template. Currenlt possible values are "txt".\n\n   
          - "txt": (default) Each line contains a country and the number 
          of attendees associated to that country. The country can be 
          expressed in various ways, that is the full name or the ISO code. 
          The output file is a JSON file that contains a list where 
          each attendee is represented by a country code.\n""" )
  args = parser.parse_args()
  print( args )

  if args.output_file is None:
    input_file = args.input_file 
    output_file = pathlib.PurePath( input_file ).with_suffix( '.json' )
  if isfile( output_file ) is True :
      print( f"""ERROR: the ouput_file already exists. Please remove it 
                with rm {output_file} """)

  if args.template == "txt":
    txt2json( input_file, output_file )
     
 
if __name__ == "__main__":
  cli()
