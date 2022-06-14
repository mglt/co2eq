# from decouple import config
from environs import Env
import json 
import os
import os.path 

class Conf:
  
  def __init__( self ):
    ## os.getcwd shoudl not be needed but without forcing it the object 
    ## looks intot the module directory. 
    self.env = Env()
    self.env.read_env( os.path.join( os.getcwd(), '.env' ) )  # read .env file, if it exists

    self.CONF = {
      ## The directory where air flights, or CO2 emissions for a given air flight
      ## requested to GO Climate are stored after it has been requested.
      ## The main purpose if to prevent co2eq to resolve the same request multiple time
      'CACHE_DIR' : self.env.path( 'CACHE_DIR', './cache' ), 
  
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
      'NOMINATIM_ID' : self.env.str( 'GOCLIMATE_SECRET', "" ), 

      ## where logs are stored. We suggest you perform tail -f your_log_file
      ## to monitor what can possibly go wrong.
      'log' : self.env.path( 'log', './co2eq.log' ),
 
      ## Directory where all outputs are stored
      'OUTPUT_DIR' : self.env.path( 'OUTPUT_DIR', './output' ),
 
      ## CityDB specific parameters
      ## ISO3166_REPRESENTATIVE_CITY enable to indicate a specific
      ## representative city for that country.
      ## This is usually useful when the capital is not the main 
      ## representative city or when no flight can be retrieved from 
      ## that country
      ##'ISO3166_REPRESENTATIVE_CITY' : env.dict( 'ISO3166_REPRESENTATIVE_CITY',  parsed_key=str, parsed_value=dict) 
      'ISO3166_REPRESENTATIVE_CITY' : self.json_file_content( 'ISO3166_REPRESENTATIVE_CITY' )
      }
    print( self.env.dump() )
 
  def json_file_content( self, conf_key, default={} ):
    file_path = self.env.path( conf_key, None )
    if file_path != None:
      with open( file_path, 'rt', encoding='utf8' ) as f:
        json_dict = json.load( f ) 
    else: 
      json_dict = default
    return json_dict
  
