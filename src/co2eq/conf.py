# from decouple import config
from environs import Env
import json 
import os
import gzip
import pathlib
#import os.path 

class Conf:
  
  def __init__( self, env_file=None ):
    ## os.getcwd shoudl not be needed but without forcing it the object 
    ## looks intot the module directory. 
    self.env = Env()
    if env_file is None:
      for env_file in [ os.path.join( os.getcwd(), '.env' ), \
                        os.path.expanduser( '~/.config/co2eq/env' ) ]:  
        if os.path.isfile( env_file ) is True :
          break
    self.env.read_env( env_file )  # read .env file, if it exists
#    self.env.read_env( os.path.join( os.getcwd(), '.env' ) )  # read .env file, if it exists
    
    ISO3166_REPRESENTATIVE_CITY_file_path = self.env.path( 'ISO3166_REPRESENTATIVE_CITY', 
             os.path.expanduser( '~/.config/co2eq/ISO3166_REPRESENTATIVE_CITY.json.gz' ) )
    self.CONF = {
      ## The directory where air flights, or CO2 emissions for a given air flight
      ## requested to GO Climate are stored after it has been requested.
      ## The main purpose if to prevent co2eq to resolve the same request multiple time
      'CACHE_DIR' : self.env.path( 'CACHE_DIR', os.path.expanduser( '~/.cache/co2eq' ) ), 
  
      ## co2eq retrieves flight offers to estimate a real flight and uses the AMADEUS API:
      ## https://developers.amadeus.com/get-started/get-started-with-amadeus-apis-334
      ## You need to register and request and an API Key and an API Secret for the
      ## Flight Offers Search service.
      ##  'AMADEUS_ID' : config('AMADEUS_ID'),
      'AMADEUS_ID' : self.env.str('AMADEUS_ID', ""),
      ##  'AMADEUS_SECRET' : config('AMADEUS_SECRET'),
      'AMADEUS_SECRET' : self.env.str('AMADEUS_SECRET', ""),

      ## To compute the CO2 emissions associated a flight a request is sent to GO Climate
      ## Please go through https://api.goclimate.com/docs to get an account.
      ##  'GOCLIMATE_SECRET' :  config('GOCLIMATE_SECRET'),
      'GOCLIMATE_SECRET' :  self.env.str( 'GOCLIMATE_SECRET', "" ),
      ##  'NOMINATIM_ID' : config('GOCLIMATE_SECRET'), 
      'NOMINATIM_ID' : self.env.str( 'NOMINATIM_ID', "" ), 

      ## where logs are stored. We suggest you perform tail -f your_log_file
      ## to monitor what can possibly go wrong.
      'log' : self.env.path( 'log', '/tmp/co2eq.log' ),
 
      ## Directory where all outputs are stored
      'OUTPUT_DIR' : self.env.path( 'OUTPUT_DIR', './output' ),
 
      ## CityDB specific parameters
      ## ISO3166_REPRESENTATIVE_CITY enable to indicate a specific
      ## representative city for that country.
      ## This is usually useful when the capital is not the main 
      ## representative city or when no flight can be retrieved from 
      ## that country
      ##'ISO3166_REPRESENTATIVE_CITY' : env.dict( 'ISO3166_REPRESENTATIVE_CITY',  parsed_key=str, parsed_value=dict)  
      'ISO3166_REPRESENTATIVE_CITY' : self.json_file_content( ISO3166_REPRESENTATIVE_CITY_file_path )
      }

  def show( self ): 
    print( json.dumps( self.env.dump(), indent=2 ) )
 
  def json_file_content( self, file_path, default={} ):
##  def json_file_content( self, conf_key, default={} ):
   ## file_path =  os.path.expanduser( self.env.path( conf_key, None )
    if file_path != None:
      suffixes = pathlib.PurePath( file_path ).suffixes
      if suffixes == [ '.json', '.gz']:
        with gzip.open( file_path, 'rt', encoding='utf8' ) as f:
          json_dict = json.load( f )
      elif suffixes == [ '.json' ]:
        with open( file_path, 'rt', encoding='utf8' ) as f:
          json_dict = json.load( f )
      else:
        raise ValueError( f"Unexpected file: {file_path} must be '.json' or '.json.gz'" ) 
    else: 
      json_dict = default
    return json_dict
  
