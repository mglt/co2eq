# import requests
import json
import gzip
#from datetime import timedelta
from glob import glob
from os.path import join, isfile, realpath, dirname # getsize, isfile
from os import path
from statistics import median
from random import random
from datetime import date, timedelta, datetime
import calendar
from time import sleep, ctime
from pkg_resources import resource_filename
from amadeus import Client, ResponseError
from isodate import parse_duration
import iso8601
import countryinfo ## to get __file__
from countryinfo import CountryInfo
from ourairports import OurAirports
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from geopy.distance import great_circle
from pip._vendor import pkg_resources
import logging
from climate_neutral import GoClimateNeutralAPI, Segment # Footprint

import co2eq.conf
from co2eq.jcache import JCacheList, JCacheDict

## Global variable
## long term data are stored in DATA_DIR
## example: iata_city_codes publishe din 2015
DATA_DIR = resource_filename( 'co2eq', 'data' )

def cache_dir( conf ):
  """ returns the cache directory specified in the conf or a default value """
  try:
    cache_directory = conf[ 'CACHE_DIR' ]
  except KeyError:
    cache_directory = './cache'
  return cache_directory

def logger( conf, __name__ ):   
  try: 
    log_file = conf[ 'log' ]
  except KeyError :
    log_file = './co2eq.log'
  logger = logging.getLogger(__name__)
  FORMAT = "[%(asctime)s : %(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
  logger.setLevel( logging.DEBUG )
  logging.basicConfig(filename=log_file, format=FORMAT )
  return logger



class AirportDB( OurAirports ):

  def __init__( self ):
    """ enhances OurAiports class for our purpose """
    super().__init__( )
    self.iata_dict  = self.init_iata_dict( )
    self.airports = self.narrow_down_airport_list( )


  def init_iata_dict( self ):
    """ build a dictionary with iata code as key

    The purpose of the creation of the dict is to speed up search
    """

    pkg_version = self.ourairports_version( )
    file_name = join( DATA_DIR, f"iata_dict_airportdb_{pkg_version}.json.gz" )
    if isfile( file_name ):
      with gzip.open( file_name, 'rt', encoding="utf8" ) as f:
        iata_dict = json.loads( f.read() )
    else:
      iata_dict = {} 
      for airport in self.airports :
        if airport.iata != '' :
          airport_json = { 'ident' : airport.ident, 
                           'name' : airport.name, 
                           'type' : airport.type, 
                           'latitude' : airport.latitude, 
                           'longitude' : airport.longitude, 
                           'elevation' : airport.elevation, 
                           'continent' : airport.continent, 
                           'country' : airport.country, 
                           'iata' : airport.iata, 
                           'icao' : airport.icao }

          if airport.iata in iata_dict.keys():
            continue;
          iata_dict[ airport.iata ] = airport_json 
      with gzip.open( file_name, 'wt', encoding="utf8" ) as f:
        f.write( json.dumps( iata_dict, indent=2 ) )
    return iata_dict

  def narrow_down_airport_list( self ):
    """ limits the airports considered to those with IATA code """
    airport_list = []
    for airport in self.airports :
      if airport.iata == '':
        continue
      if airport.type not in [ "large_airport", "medium_airport", "small_airport" ]:
        continue
      airport_list.append( airport )
    return airport_list 

  def ourairports_version( self ):
    """ returns the version of the parent package OurAirports """
    for p in pkg_resources.working_set:
      if p.project_name.lower() == 'ourairports' :
        return p.version 
    raise ValueError( "unable to find ourairports package" )

  
  def get_airport_by_iata(self, iata):
    """ returns the airport objects 
    
    Overwrite the original function to avoid list search 
    """
    return self.iata_dict[ iata ]
    ## the function below would have ensured compatibility
    ## but we our dictionary uses JSON
    ##  def  getAirportsByIATA( self, iata ): 
    ##    a = self.iata_dict[ iata ]
    ##    return [ Airport( a.ident, a.name, a.type, a.latitude, a.longitude, \
    ##                      a.elevation, a.continent, a.country, a.iata, a.icao ) ]

  def is_iata_airport_code( self, iata ) -> bool:
    """ returns true is iata is an airport IATA code """
    if iata in self.iata_dict.keys():
      return True
    return False


class MyCountryInfo( CountryInfo ) :

  def __init__( self, json_dictionary ):
    self._CountryInfo__country_name = json_dictionary[ 'name' ]
    self._CountryInfo__countries = {}
    self._CountryInfo__countries[ self._CountryInfo__country_name ] = json_dictionary


class CountryDB :

  def __init__( self ):
    __file_dir_path = dirname( realpath( countryinfo.__file__ ) )
    __country_files = __file_dir_path + '/data/'
    __files_path = [files for files in glob( __country_files + '*.json' ) ]
    self.countryDB = {}
    for file_path in __files_path:
      if isfile(file_path):
        with open(file_path, encoding='utf-8') as f:
#          print( f"file_path : {file_path}" )
          country_info = json.load( f )
        if 'name' in country_info:
          key_list = [ country_info[ 'name' ].lower() ]
          if 'altSpellings' in country_info.keys() :
            for k in country_info[ 'altSpellings' ]:
              key_list.append( k.lower() )
          for k in key_list :
            self.countryDB[ k ] = country_info
#    self.country_info = CountryInfo()  

  def input_clean_up( self, country_name ):
    """ common rules that apply to country_name """

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
##     ( 'korea' in country_name.lower() and 'republic' in country_name.lower()) :
      country_name = "Republic of Korea"
    elif 'northern' in country_name.lower() and 'ireland' in country_name.lower() :
      country_name = "United Kingdom of Great Britain and Northern Ireland"
    elif 'scotland' in country_name.lower() :
      country_name = "United Kingdom of Great Britain and Northern Ireland"
    elif country_name in [ 'no country given', 'No Country Given', 'Global', \
                           'Multiple Countries' ]:
      return None
    return country_name.strip()

  def get_country_info( self, country:str ):
    """ return the country_info object """
    country_key = self.input_clean_up( country ).lower()
#    self.country_info._CountryInfo__countries = self.countryDB[ country_key ]
#    self.country_info._CountryInfo__country_name = country_key
    return MyCountryInfo( self.countryDB[ country_key ] )
  

class CityDB :
  def __init__( self, conf=co2eq.conf.Conf().CONF, airportDB=AirportDB() ):
    """ This class contains function related to cities.

    The current use of this class is to retrieve the IATA associated to a
    city, which may be expressed using different ways.
    Note that IATA city code are different from those used for airports.

    Todo:
    * not sure we need to rely on JCacheList anymore

    Arg:
      cache_path (str): the location of the json file with current known
        city information.
        By default the file provided by the package is considered
        - iata_city_codes-2015.json.
        This file has been generated from a txt file also provided in the package).
    """

    self.micro_cache = {}
    self.micro_cache_representative_city = {}
    self.airportDB = airportDB
    self.countryDB = CountryDB()
    ## ISO3166_REPRESENTATIVE_CITY enable to indicate a specific
    ## representative city for that country.
    ## This is usually useful when the capital is not the main 
    ## representative city or when no flight can be retrieved from 
    ## that country
    try:
      self.ISO3166_REPRESENTATIVE_CITY = conf[ 'ISO3166_REPRESENTATIVE_CITY' ]
    except KeyError:
      self.ISO3166_REPRESENTATIVE_CITY = {}
    ## list of cities with iata city codes. each city is an object 
    ## {
    ##   "name": "Paris",
    ##   "iata": "PAR",
    ##   "latitude": 48.8566969,
    ##   "longitude": 2.3514616,
    ##   "country": "FR",
    ##   "state": null
    ## },
    with gzip.open( join( DATA_DIR, 'iata_city_codes-2015.json.gz' ), 'rt', encoding="utf8" ) as f:
      self.iata_city_list = json.loads( f.read() )
    ## dictionary with key a iata_city_code and value being the list 
    ## of corresponding iata airport codes
    with gzip.open( join( DATA_DIR, 'iata_city_airport_map.json.gz' ), 'rt', encoding="utf8" ) as f:
      self.iata_city_iata_airport_list_dict = json.loads( f.read() )

    self.iata_airport_iata_city_dict = {}
    for iata_city, iata_airport_list in self.iata_city_iata_airport_list_dict.items():
      for iata_airport in iata_airport_list :
        self.iata_airport_iata_city_dict[ iata_airport ] = iata_city 
    self.logger = logger( conf, __name__ )   
    self.iata_dict = {}
    for city in self.iata_city_list:
      self.iata_dict[ city[ 'iata' ] ] = city

  def is_iata_city_code( self, iata ) -> bool:
    """ returns true is iata is an IATA city code"""
    if iata in self.iata_city_iata_airport_list_dict.keys():
      return True
    return False

  def airport_list_of( self, city:dict ) -> list :
    """ for a valid iata_city code, the list of mapped iata airport codes are returned

    Args:
      city (dict) : the iata city code

    Returns:
      airport_list (list): when the iata city codes is a valid iata
        code, the list of corresponding iata airport codes is returned.
        Note that the list may also contain the iata_city code.
        In the vast majority of the cases the iata city code and airport
        code is the same.
    """
    try:
      iata_list = self.iata_city_iata_airport_list_dict[ city[ 'iata' ] ]
    except KeyError:
      iata_list =  []
    airport_list = []
    for iata in iata_list :
      ## we do only have an on purpose  partial list of airport
      ## so we only considers those we have e.g large - medium - small
      try:
        airport_list.append( self.airportDB.get_airport_by_iata( iata ) )
      except KeyError:
        pass
    return airport_list

  def has_airports( self, city:dict, airport_type:str=None ):
    """ checks a city has at least one airports of specified type 
     
    Args:
      city (dict) a city object
      airport_type (str): None or one of "large_airport", "medium_airport", "small_airport" 
    Returns:
      result (bool)
    """
    if airport_type not in [ None, "large_airport", "medium_airport", "small_airport" ] :
      raise ValueError( f"Unvalid airport type {airport_type}. "\
                        f" Expected values are None, 'large_airport', " \
                        f"'medium_airport', 'small_airport' " )
    result = False
    airport_list = self.airport_list_of( city )

    if airport_type is None :
      if len( airport_list ) != 0:
        result = True
    else:
      if airport_type == "small_airport":
        check_type_list = [ "large_airport", "medium_airport", "small_airport" ]
      elif airport_type == "medium_airport":
        check_type_list = [ "large_airport", "medium_airport" ]
      elif airport_type == "large_airport":
        check_type_list = [ "large_airport" ]
      for airport in airport_list:
        if airport[ 'type' ] in check_type_list :
          result = True
          break
    return result

  def get_city_by_iata( self, iata ):

    return self.iata_dict[ iata] 

  def get_city( self,  **kwargs ) -> list :
    """ returns cities matching keywords arguments """
    ## the key associated to city_name is 'name' while we frequently
    ## use the key 'city'
    if 'city' in kwargs.keys() :
      kwargs[ 'name' ] = kwargs[ 'city' ]
      del kwargs[ 'city' ]
    ## checking keys matching the iata_city_codes-2015 database
    removed_keys = []
    for k in kwargs.keys() :
      if k not in [ 'name', 'iata', 'latitude', 'longitude', 'country', 'state' ] :
        removed_keys.append( k )
        del kwargs[ k ]
    if removed_keys != [] :
      self.logger.debug( f"The {removed_keys} have been ignored" ) 
    ## country field of iata_city_list is using iso(2)
    if 'country' in kwargs.keys() : 
      country_info = self.countryDB.get_country_info( kwargs[ 'country' ] )
      kwargs[ 'country' ] = country_info.iso( 2 )
    city_list = []
    for city in self.iata_city_list :
      for k, v in kwargs.items() :
        if city[ k ] != v :
          break
      else:
        city_list.append( city )
      continue
    return city_list  


  def country_representative_city( self, country:str ) -> dict :
    """ returns a list of representative cities associate to the country 

    The input is a country that is either a string or a country code. 
    From that country code, a representative city is selected. 
    That city is the largest economic city of the country - which 
    usually is the capital of the country. 
    For the US, the representative city is WS or LAX that is randomly chosen. 
   
    Nominatim is a general purpose api that matches a specific address to a geodesic point. 
    In the case of country code, we do prefer to rely on a data base provided by country_info.
    """
    ## deprecated countries
    if country == 'AN': ## Netherlands Antilles We should maybe add 
                        ## an entry to country_info
      country = 'CW'
    ## try a cache lookup
    try:
      city = self.micro_cache[ country ]
      if len( self.micro_cache.keys() ) > 10000:
        self.micro_cache = {}
      return city
    except KeyError:
      pass
    try:
      country_info = self.countryDB.get_country_info( country )
    except:
      raise ValueError( f"Unable to retrieve country_info from {country}." )
    try:
      country_iso = country_info.iso( 2 )
    except:
      raise ValueError( f"Unable to provide ISO(2) for {country}." )
    
    ## the use of random prevents the use of the cache
    if country_iso == 'US':
      r = random()
      if r < 0.5:
        iata_city = 'WAS' ## "Washington D.C."
      else:
        iata_city = 'LAX'
      city = self.get_city_by_iata( iata_city )
    elif country_iso in self.ISO3166_REPRESENTATIVE_CITY.keys() :
      city = self.get_city_by_iata( self.ISO3166_REPRESENTATIVE_CITY[ country_iso ][ 'iata' ] )
    else: 
      iata_coordinates = country_info.capital_latlng()
      self.logger.debug( f"{iata_coordinates} for ( {country_info.name()}, "\
                         f"{country_iso}, {country_info.capital()} )" )
      iata_city  = { "latitude" : iata_coordinates[ 0 ], 
                     "longitude" : iata_coordinates[ 1 ] }
      city_list = self.neighboring_city_list( iata_city, list_len=1, max_dist=None)  
      city = city_list[ 0 ]
    self.micro_cache[ country ] = city
    return city 
      
  def neighboring_city_list( self, ref_city, list_len=10, \
                             max_dist=1000, airport_type=None ) -> list :
    """ returns a list of sure sundering iata_cities 
     
    Lists all cities that are within the max_dist distance from iata_city.
    The resulting list is sorted in increasing distance and only the closest list_len are 
    retuned.
  
    Args:
      ref_city (dict): a city represented by a dictionary. 
        Note that only the latitude and longitude parameters are used.
      list_len (int): the maximum number of surrounding cities that are returned.
        default list len is 10. WHen set to 1 it returns the closest iata 
        city of self.iata_city_list.
      max_dist (float): the distance range in km of surrounding cities to be considered. 
    
    """
    city_list = []
    for city in self.iata_city_list : 
      if self.has_airports( city, airport_type=airport_type ) is False :
        continue
      city[ 'distance' ] = self.dist( ref_city , city )
      if list_len == 1: ## we are looking at the closest
        if len( city_list ) == 0:
          city_list = [ city ]
        else: 
          if city[ 'distance' ] < city_list[ 0 ][ 'distance' ]:
            city_list = [ city ]
      else : ## list is != 1 and can be None
        appened = False
        if max_dist is None :
          city_list.append( city )
          appened = True
        else :
          if city[ 'distance' ] < max_dist :
            city_list.append( city )
            appened = True
        if appened is True:
          city_list.sort( key = lambda city : city[ 'distance' ] )
          city_list = city_list[: list_len]
#      print( f" city_list : {city_list[:]}" ) 
    return city_list

  def closest_city( ref_city, airport_type=None ) -> dict :
    city_list = self.neighboring_city_list( ref_city, list_len=1, max_dist=None,\
                                            airport_type=airport_type)
    return city_list[ 0 ]

  def representative_city( self, location:dict ) -> dict:
    """ makes its best to output a city from location

    Args:

    Returns:
      city (dict) : a JSON object that represents the city
    Todo:
      * micro_cache is expected handle repeated queries. It currently
        applies to all queries, though we mostly tested it for country.
    """

    if 'iata' in location.keys() :
      iata = location[ 'iata' ]
      ## if IATA airport return IATA city
      if iata in self.iata_airport_iata_city_dict.keys():
        iata = self.iata_airport_iata_city_dict[ iata ]
      ## return city from IATA city code
      if iata in self.iata_city_iata_airport_list_dict.keys():
        city = self.get_city_by_iata( iata )
      else:
        raise ValueError( f"IATA {iata} not recognized as IATA code "\
                          f" error happening with {location}" ) 
    elif 'country' in location.keys() and 'state' in location.keys() and\
       'city' in location.keys():
      city_list = self.get_city( name=location[ 'city' ], \
                                 country=location[ 'country' ], 
                                 state=location[ 'state' ] )
      city = city_list[ 0 ] 
    elif 'country' in location.keys() and 'city' in location.keys():
      city_list = self.get_city( name=location[ 'city' ], \
                                 country=location[ 'country' ] )
#      print( f"city_list : {city_list} - location {location}" )
      city = city_list[ 0 ] 
    elif 'country' in location.keys() :
      city = self.country_representative_city( location[ 'country' ] )
    return city

  def dist( self, departure: dict, arrival: dict, dist_type='geodesic') :
    """ geodesic distance

       dep. / arrival are city object ( -- eventually returned by representative_city )
    """

    coordinates = []
    for city in [ departure, arrival ]:
      coordinates.append( ( city[ 'latitude' ], city[ 'longitude' ] ) )
    if dist_type == 'geodesic':
        distance = geodesic( coordinates[0], coordinates[1] ).km
    elif dist_type == 'great_circle':
      distance = great_circle( coordinates[0], coordinates[1] ).km
    return distance

class GoClimateDB (JCacheDict):
  def __init__( self, conf ):
    self.key = conf[ 'GOCLIMATE_SECRET' ]
    ## list of IATA codes not accepted by goclimate
    self.IATA_SWAP = { 'ANK' : 'ESB',
                       'ZYR' : 'BRU' # brussels midi
                     }
    super().__init__( join( conf[ 'CACHE_DIR' ], 'goclimateDB', 'goclimateDB.json.gz' ) )

  def kwarg_to_key( self, **kwargs ):
    return f"{kwargs[ 'origin' ]}-{kwargs[ 'destination' ]}-{kwargs[ 'cabin' ]}"

  def cache_read_all( self, **kwargs ):
    """ reading (origin, destination) or (destination, origin) """
    origin = kwargs[ 'origin' ]
    destination = kwargs[ 'destination' ]
    cabin = kwargs[ 'cabin' ]
    try :
      match_list = super().cache_read_all( origin=origin, destination=destination, cabin=cabin )
    except KeyError:
      try :
        match_list = super().cache_read_all( origin=origin, destination=destination, cabin=cabin )
      except :
        match_list = []
    return match_list

  def retrieve_item(self, **kwargs):
    for key in [ 'origin', 'destination' ]:
      try:
        kwargs[ key ] = self.IATA_SWAP [ kwargs[ key ] ]
      except KeyError:
        pass
    print( f"   - Requesting GoClimate for {kwargs}" )
    gc = GoClimateNeutralAPI( self.key, cabin_class=kwargs[ 'cabin' ].lower() )
    gc.add_segment( Segment( kwargs[ 'origin' ], kwargs[ 'destination' ] ) )
    footprint = gc.send()
    if footprint is None:
      raise ValueError( f"Unable to retreive CO2eq from GoClimate for {kwargs}" )
    return { "date" : date.today().isoformat(),
             "co2eq" :  footprint.tons * 1000  }

def is_iso8601( str_date:str):
  """ checks the date is of format ISO8601 """
  try:
    iso8601.parse_date( str_date )
  except iso8601.iso8601.ParseError:
    raise ValueError( f"{str_date} is not ISO8601 (YYYY-MM-DD)" )


class AmadeusOffersSearchResponse:
  """ Handle Amadeus Offer Search Response to select a flight from the list of offers.

  Amadeux responses are pretty completed, and only a few pieces of
  information is useful for our work.
  In addition, we need to select one flight from the multiple offers.
  """
  def __init__( self, response ):
    """ analyzes teh response received from amaedus """
    self.response = response
    self.flight_list = []


  def is_valid( self, offer, cabin_list=[ 'ECONOMY' ] )-> bool:
    cabin_list = [ cabin.upper() for cabin in cabin_list ]
    for leg in offer[ 'itineraries' ]:
      for segment in leg[ 'segments' ]:
        if segment[ 'blacklistedInEU' ] is True:
          return False
    for traveler in offer[ 'travelerPricings' ]:
      for pricing_segment in traveler[ 'fareDetailsBySegment']:
        if pricing_segment[ 'cabin' ].upper() not in cabin_list:
          return False
    return True

  def build_flight_list( self, cabin='ECONOMY', relax=True ):
    """ extract information from the full Search Response and build self.flight_list"""
    if isinstance( cabin, str ) is True:
      cabin_list = [ cabin ]
    elif isinstance( cabin, list ) is True:
      cabin_list = cabin

    for offer in self.response:
      if self.is_valid( offer, cabin_list=cabin_list ) is False:
        continue
      travel_duration = timedelta(0)
      flight_duration = timedelta(0)
      segment_list = []
      for leg in offer[ 'itineraries' ]:
        travel_duration += parse_duration( leg[ 'duration' ] )
        for segment in leg[ 'segments' ]:
          flight_duration += parse_duration( segment[ 'duration' ] )
          segment_list.append( ( segment['departure']['iataCode'],
                                 segment['arrival']['iataCode'] ) )
      flight = {
        'price' :  offer[ 'price' ][ 'total' ],
        'currency' : offer[ 'price' ][ 'currency' ],
        'travel_duration' : travel_duration,
        'flight_duration' : flight_duration,
        'segment_list' : segment_list }
      self.flight_list.append( flight )
    if len( self.flight_list ) == 0 and relax is True:
      ## opening to higher/lower class. Currently we only improve the cabin
      ## class, assuming that cabin class is the lowest acceptable.
      ##  travelClass='ECONOMY', PREMIUM_ECONOMY, BUSINESS, FIRST
      if 'ECONOMY' in cabin_list :
        if 'PREMIUM_ECONOMY' in cabin_list:
          if 'BUSINESS' in cabin_list:
            if 'FIRST' in cabin_list:
              raise ValueError( "UNable to find appropriated offer" )
            else:
              cabin_list.append( 'FIRST' )
          else:
            cabin_list.append( 'BUSINESS' )
        else:
          cabin_list.append( 'PREMIUM_ECONOMY' )

        self.build_flight_list( cabin=cabin_list, relax=True )


  def select_flight(self, cabin='ECONOMY',  direct_perc=20, price_perc=30, time_perc=50):
    """ selects a flight among the proposed flights  (in self.flight_list)

        The selection balances the minimal travel time with prices.
        If more than 1 + "direct_perc" % of the offers provide a direct flight.
        Only direct flight are considered.
        Otherwise, if T is the minimum travel time, offers are limited to those
        that provide between T and ( 1 + "time_perc" ) T.
        Let P be the minimal price, the
        selected flight is the one with the median price between P
        and ( 1 + price_perc ) P.
    """
    self.build_flight_list( cabin='ECONOMY' )
    offer_nbr = len( self.flight_list )
    seg_nbr = [ len( flight[ 'segment_list' ] ) for flight in self.flight_list ]
    ## in some cases we cannot find 'ECONOMY' for all segments so we need to relax
    ## a bit the selection.
##    print( f" select_flight - self.flight_list : {self.flight_list}" )
    if self.response[0][ 'oneWay' ] is False:
      direct_seg_nbr = 2
    else:
      direct_seg_nbr = 1
    direct_ratio = seg_nbr.count( direct_seg_nbr ) / len( seg_nbr )
    # print( f"direct_ratio: {direct_ratio}" )

    if direct_ratio > direct_perc:
      ## only direct flight are considered.
      self.flight_list = [ flight for flight in self.flight_list \
                           if len(flight[ 'segment_list' ] ) == direct_seg_nbr  ]
    else:
      time_min  = min( [ flight[ 'travel_duration' ] for flight in self.flight_list ] )
      self.flight_list = [ flight for flight in self.flight_list \
                           if flight[ 'travel_duration' ] <= (1 + time_perc) * time_min ]

    price_min = min( [ float( flight[ 'price' ] ) for flight in self.flight_list ] )
    self.flight_list = [ flight for flight in self.flight_list \
                         if float( flight[ 'price' ] ) <= (1 + price_perc) * price_min ]
    ## to ensure median price belongs to list the length of the list must be an odd number.
    price_list = [ float( flight[ 'price' ] ) for flight in self.flight_list ]
    if len( self.flight_list ) %2 == 0:
      price_list.pop()
    median_price = median( price_list )
    for flight in self.flight_list:
      if float( flight[ 'price' ] )  == median_price :
        selected_flight = flight
    return selected_flight


class FlightDB(JCacheDict):
## FLIGHTS_CACHE = join( CACHE_DIR, 'flights.json' )
  def __init__( self, conf=co2eq.conf.Conf().CONF, airportDB=True, \
                cityDB=True, goclimateDB=True):
    """ retrieve and compute flights related information such as CO2 equivalent.

    Since conf is used to generate some DB (goclimateDB), DB can either be
    provided as object of set to True to indicate these need to be generated.

    Args:
      conf (dict): configuration parameters
      airportDB: the airportDB object ( AirportDB ) or True to indicate
        the DB is generated by FlightDB.
        By default it is set to True.
      cityDB: the cityDB object ( CityDB ) or True to indicate the DB is
        generated by FlightDB.
        By default it is set to True.
      goclimateDB: the cityDB object ( GoClimateDB ) or True to indicate
        the DB is generated by FlightDB.
        By default it is set to True. Note that this is the only DB that
        needs the configuration parameters.

    """

    self.cache_dir = cache_dir( conf )
    self.cache_flight = join( self.cache_dir, 'flightDB', 'flightDB.json' )
    self.cache_amadeus_dir = join( self.cache_dir, 'flightDB', 'amadeus' )
    self.amadeus_id = conf[ 'AMADEUS_ID' ]
    self.amadeus_secret = conf[ 'AMADEUS_SECRET' ]
    self.output = conf['OUTPUT_DIR']
    if airportDB is True:
      self.airportDB = AirportDB()
    else:
      self.airportDB = airportDB
    if  cityDB is True:
      self.cityDB = CityDB( )
    else:
      self.cityDB = cityDB
    if goclimateDB is True:
      self.goclimateDB=GoClimateDB( conf )
    else:
      self.goclimateDB = goclimateDB
    super().__init__( self.cache_flight )
    self.departure_date = self.default_date().isoformat()
    self.return_date = ( self.default_date() + timedelta( weeks=1 ) ).isoformat()
    self.logger = logger( conf, __name__ )
    ## non persistent micro-cache
    self.micro_cache_force_select_flight = {}

  def default_date( self ):
    """ reurn next Friday next month in iso8601 format

      requests to amadeus requires dates, but are not necessarily a effective criteria.
    """
    today = date.today()
    if today.weekday() <= calendar.FRIDAY:
      days = calendar.FRIDAY - today.weekday()
    else:
      days = calendar.FRIDAY + calendar.SUNDAY - today.weekday()
    return today + timedelta( weeks=4, days=days)

  def get_dates( self, departure_date, return_date ):
    """ check date format and return dates according to conventions
    """
    for input_date in [ departure_date, return_date ]:
      if input_date is not None:
        is_iso8601( input_date )
    if departure_date is None:
      departure_date = self.departure_date
      if return_date is not None:
        return_date = self.return_date
    else:
      if return_date == '0001-01-01':
        ## convert departure_date into a date object
        dep_date = datetime.strptime(departure_date + 'T16:41:24+0200', "%Y-%m-%dT%H:%M:%S%z")
        return_date = ( dep_date + timedelta( weeks=1 ) ).isoformat()
    return departure_date, return_date

  def cache_init(self):
    """ sets the amadeux client to request the search offers when not found in the cache """
    self.amadeus = Client( client_id=self.amadeus_id,
                           client_secret=self.amadeus_secret )

  def retrieve_amadeus(self, origin, destination, departure_date=None,
                    return_date='0001-01-01', adults=1 ):
    """ add a new element in the cache.

    This fcuntion is called with the same parameter provided for the cache lookup.
    It is important that unspecifie parameters got specified when requesting amadeus.
    """
    if origin == destination :
      raise ValueError( f"origin ({origin}) and destination ({destination}) are equal" )
    departure_date, return_date = self.get_dates( departure_date, return_date )
    ## we need to complete the unspecified parameters here so get_dates is usefull here.

    ## origin and destination must be IATA cities or airports
    ## when a country is provided we should take the capital as an approximation
    ## IATA country codes: http://www.fedex.com/mp/tracking/codes.html
    ## we may also check IATA / ISO country codes.

    try:
      ## https://developers.amadeus.com/self-service/category/air/api-doc/flight-offers-search/api-reference
      ## https://amadeus4dev.github.io/amadeus-python/#amadeus.Response
      ## https://pypi.org/project/amadeus/
      ## https://nvbn.github.io/2019/05/13/summer-trip/
      if return_date is None :
        self.logger.info( f"requesting amadeus single flight {origin} - {destination},"\
                          f" {departure_date} for {adults} adult(s)" )
        response = self.amadeus.shopping.flight_offers_search.get(
          originLocationCode=origin,
          destinationLocationCode=destination,
          departureDate=departure_date,
##        travelClass='ECONOMY',  #ECONOMY, PREMIUM_ECONOMY, BUSINESS, FIRST
##        includedAirlineCodes  or excludedAirlineCodes,
##        maxPrice
##        max
          adults=adults)
      else:
        self.logger.info( f"requesting amadeus round trip flight for {origin} " \
                          f"-{destination} - {departure_date} for {adults} adult(s)" )
        print( f"requesting amadeus round trip flight for {origin} " \
                          f"-{destination} - {departure_date} for {adults} adult(s)" )
        response = self.amadeus.shopping.flight_offers_search.get(
          originLocationCode=origin,
          destinationLocationCode=destination,
          departureDate=departure_date,
          returnDate=return_date,
##        travelClass='ECONOMY',  #ECONOMY, PREMIUM_ECONOMY, BUSINESS, FIRST
##        includedAirlineCodes  or excludedAirlineCodes,
##        maxPrice
##        max
          adults=adults)
    except ResponseError as error:
      msg = f"Unable to retrieve Amadeus response {error} for "\
            f"{origin} -{destination} - {departure_date} for {adults} adult(s)"
      print(msg)
      self.logger.warning( msg )
      print( f"error: {error} / {type(error)} {error == [400] }") 
      if error != [400]:
        # self.logger( f" {error} is a service error - probably over quotat")
        print( " {error} is a service error - probably over quotat") 
      raise ValueError( error )
      
    cache_resp = { 'origin' : origin,
                   'destination' : destination,
                   'departure_date' : departure_date,
                   'return_date' : return_date,
                   'adults' : adults,
                   'response' : response.data }
##    print( f"response_data : {cache_resp}"  )
    if len( response.data ) == 0:
      raise ValueError( f"Empty offer retrieved from Amadeus {cache_resp} " \
                        f"Maybe try with other departure / return dates" )
    return cache_resp


  def match_item( self, item : dict, origin : str, destination : str,\
                  departure_date : str =None, return_date : str ='0001-01-01',\
                  adults : int =1, cabin = None ):
    """ returns True if the json / dictionary item match the request, False otherwise

    items are currenlty flight ( which include a cabin parameter, and
    amadeus offers which do not include a cabin parameter.
    As aresult, cabin needs to be explicitly provided when flights are checked.

    Args:
      return_date: None indicates a single trip, '0001-01-01' a round trip
        with no specific return date.
    """
    ##
    if cabin is not None:
      if item[ 'cabin' ] != cabin :
        return False

    match = False
    if departure_date is None: ## departure date does not matters
      if return_date == '0001-01-01':
        if item[ 'origin' ] in [ origin, destination ] and \
           item[ 'destination' ] in [ origin, destination ] and \
           item[ 'adults' ] == adults :
          match = True
      else : ##  return_date is None or something else specific
        if item[ 'origin' ] in [ origin, destination ] and \
           item[ 'destination' ] in [ origin, destination ] and \
           item[ 'adults' ] == adults and \
           item[ 'return_date' ] == return_date :
          match = True
    else :                     ## departure date matters
      if return_date == '0001-01-01':
        if item[ 'origin' ] == origin and \
           item[ 'destination' ] == destination and \
           item[ 'departure_date' ] == departure_date and \
           item[ 'adults' ] == adults:
          match = True
      else : ##  return_date is None or something else specific
        if item[ 'origin' ] == origin and \
           item[ 'destination' ] == destination and \
           item[ 'departure_date' ] == departure_date and \
           item[ 'return_date' ] == return_date and \
           item[ 'adults' ] == adults :
          match = True
    return match

  def kwarg_to_key( self, **kwargs ):
    return f"{kwargs[ 'origin' ]}-{kwargs[ 'destination' ]}"

  def cache_read_all( self, origin, destination, departure_date=None, \
                      return_date='0001-01-01', adults=1, cabin="ECONOMY" ):
    """ performs a cache lookup and returns a JSON object that contains
        information of the flight

    The function returns a non empty list if a match occurs and the match
    meets the requested criteria.
    This overwrites the JCache Dict function by performing a double cache
    lookup and checking the returned items.

    The JCacheList perform a cache lookup based on some matching parameters
    (e.g origin, destination, departure_date, return_date, adult).
    The same parameters are used to retrieve a new element from the
    amadeus data base.
    Querying the amadeux databases mandates a departure_date, and the
    presence of a return_date indicates a round_trip flight.
    In other words, there is not a 'single' parameter.
    This function uses the same convention and set to return_date to
    None to specify a single trip.
    While amadeux queries require a departure_date parameter, in some
    cases, the dates may not be important.
    To avoid using another parameter, this function indicates that dates do
    not matter by setting departure_date to None.
    In case of a cache miss, the query to Amadeus will use the default date.
    To specify that dates do not matter and that round trip flights
    are considered, the return_date is set to 0001-01-01.

    Args:
      departure_date: a specific departure date (YYYY-MM-DD) or None (default)
        when dates are ignored
      return_date: a specific return date, '0001-01-01' (default) or None to
        for a single flight.
    """
    try:
      key = self.kwarg_to_key( origin=origin, destination=destination )
      match_list = [ self.cache[ key ] ]
    except KeyError:
      try:
        key = self.kwarg_to_key( origin=destination, destination=origin )
        match_list = [ self.cache[ key ] ]
      except KeyError:
        match_list = []

    if match_list != []:
      for item in match_list:
        if self.match_item( item, origin, destination, departure_date=departure_date,\
                            return_date=return_date, adults=adults, cabin=cabin ) is False:
          match_list.remove( item )
    return match_list

  def retrieve_item( self, origin, destination, departure_date=None, \
                     return_date='0001-01-01', adults=1, cabin="ECONOMY" ):
    """ retrieve the corresponding flight in case of case miss

    At first the function checks the corresponding amadeus files are present.
    This includes flights from origin to destination as well as those from destination to origin.
    In case the files are not found or we do not have corresponding
    items, an amadeus request is performed.

    """
    key = self.kwarg_to_key( origin=origin, destination=destination )
    amadeus_file = join( self.cache_amadeus_dir, f"{key}.json.gz" )
    amadeus_file = path.join(self.output,amadeus_file)
    print(amadeus_file)

    ## look for amadeus files
    try:
      with gzip.open( amadeus_file, 'rt', encoding="utf8" ) as f:
        amadeus_offer_list = json.loads( f.read() )
    except FileNotFoundError :
      try:
        reverse_key = self.kwarg_to_key( origin=destination, destination=origin )
        reverse_amadeus_file = join( self.cache_amadeus_dir, f"{reverse_key}.json" )
        with gzip.open( reverse_amadeus_file, 'rt', encoding="utf8" ) as f:
          amadeus_offer_list = json.loads( f.read() )
      except FileNotFoundError :
        amadeus_offer_list = []

    ## check whether offers match the request
    if amadeus_offer_list != []:
      for item in amadeus_offer_list:
        if self.match_item( item, origin, destination, departure_date=departure_date,\
                            return_date=return_date, adults=adults ) is False:
          amadeus_offer_list.remove( item )
    ## take the first offer
    if amadeus_offer_list != []:
      search_offer = amadeus_offer_list[ 0 ]
    else:
      print( f"    - retrieve amadeus : {origin} - {destination} "\
            f"(departure_date, return_date) : {str((departure_date, return_date))}" )
      search_offer = self.retrieve_amadeus(origin, destination, \
                       departure_date=departure_date, return_date=return_date, \
                       adults=adults )
      try: ## if a file exists, than we simply append the new amadeus search
        with gzip.open( amadeus_file, 'rt', encoding="utf8" ) as f:
          amadeus_offer_list = json.loads( f.read() )
        amadeus_offer_list.append( search_offer )
      except FileNotFoundError :
        amadeus_offer_list = [ search_offer ]
      with gzip.open( amadeus_file, 'wt', encoding="utf8" ) as f:
        f.write( json.dumps( amadeus_offer_list, indent=2 ) )
    ## selecting one flight among available flights
    offer_list = AmadeusOffersSearchResponse( search_offer[ 'response' ] )
    flight = offer_list.select_flight()
    ## adding complementary information related to the selected flight
    flight[ 'origin' ] =  origin
    flight[ 'destination' ] = destination
    flight[ 'departure_date' ] = search_offer[ 'departure_date' ]
    flight[ 'return_date' ] = search_offer[ 'return_date' ]
    flight[ 'adults' ] = adults
    flight[ 'cabin' ] = cabin
    ## computes the flight
    flight =  Flight( **flight, airportDB=self.airportDB, cityDB=self.cityDB, \
                      goclimateDB=self.goclimateDB )

    return flight.export()


  def select_flight(self, origin, destination, departure_date=None, \
                    return_date='0001-01-01', adults=1, cabin="ECONOMY" ):
    """ selects a flight """
    return self.get_first( origin=origin, destination=destination,\
                           departure_date=departure_date, \
                           return_date=return_date, adults=adults, cabin=cabin )

  def force_select_flight(self, origin, destination ):
    """ implements multiple tries to search an acceptable flight

    In some cases, flight search fails, and for the purpose of CO2 computation some arguments may be twicked.
    This function proceeds as follows. 
    1- the same request is retried in case the service is failing
    2- the date are change to 5 days ahead. This only reason for taking 5 is that it is not 7.
    3- the may try up to 3 with different cities with a large airport

    The function is limited to origin destination to ease the implementation of a additional level of cache. 
    The force function may lead to multiple amadeus request and the cache function does not perform negative caching. 
    As a result, in case of errors the same group of requests may be performed several times. 
    To prevent this to happen, the origin destination result is cached into the micro_cache 
    which is destroyed  at any restart. 
    """
    
    try:
      flight = self.micro_cache_force_select_flight[ (origin, destination) ]
      return flight 
    except KeyError:
      try :
        flight = self.micro_cache_force_select_flight[ (destination, origin) ]
        return flight 
      except KeyError:
        pass
     
    try:
      flight = self.select_flight( origin, destination )
    except ValueError as error :
      self.logger.warning( f"Unable to retrieve flight from {origin} to {destination} "\
                           f"with default dates - retrying")
      if error != [400]:
        raise ValueError( f" {error} is a service error - probably over quotat") 
      try:
        flight = self.select_flight( origin, destination )
      except ValueError :
        ## retry with other dates - in this case 5 days later
        departure_date = self.departure_date
        return_date = self.return_date
        alt_departure = datetime.strptime( departure_date + 'T16:41:24+0200', "%Y-%m-%dT%H:%M:%S%z")
        alt_departure = ( alt_departure + timedelta( days=5 ) ).isoformat()
        alt_return = datetime.strptime( return_date + 'T16:41:24+0200', "%Y-%m-%dT%H:%M:%S%z")
        alt_return = ( alt_return + timedelta( days=5 ) ).isoformat()
        self.logger.warning( f"Unable to retrieve flight from {origin} to {destination} "\
                             f"with default dates - changing dates + 5 days")
        try:
          flight = self.select_flight( origin, destination, departure_date=alt_departure, return_date=alt_return )
        except ValueError :
          ## trying with other cities
          origin_city = self.cityDB.representative_city( origin )
          city_list = self.cityDB.neighboring_city_list( origin_city, list_len=4, \
                                                     max_dist=None, airport_type="large_airport" )
          ## removing origin_city - if it already had an large airport
          if origin_city in city_list:
            city_list.remove( origin_city )
          for city in city_list[ : 3 ] :
            try:
              self.logger.warning( f"Unable to retrieve flight from {origin} to {destination} "\
                                   f"with changed dates - changing {origin_city} destination to {city}")
              flight = self.select_flight( city[ 'iata' ], destination )
            except ValueError :
              continue
            break
          else:
            msg = f"Unable to retrieve flight from {origin} to {destination} "\
                  f"including changing dates and cities {city_list} "
            self.logger.warning( msg )
            raise ValueError( msg )
    self.micro_cache_force_select_flight[ (origin, destination) ] = flight
    return flight

class Flight:

  def __init__( self, origin=None, destination=None, departure_date=None,
                return_date=None, adults=None, cabin='ECONOMY',
                segment_list=None, co2eq=None, price=None, currency=None,
                flight_duration=None, travel_duration=None,
                airportDB = True, cityDB = True, goclimateDB=True, \
                conf=co2eq.conf.Conf().CONF ):
    """ computes co2eq associated to the flight

      Args:
      airportDB: the airportDB object ( AirportDB ) or True to indicate the DB is
        generated by FlightDB.
        By default it is set to True.
      cityDB: the cityDB object ( CityDB ) or True to indicate the DB is generated
        by FlightDB.
        By default it is set to True.
      goclimateDB: the cityDB object ( GoClimateDB ) or True to indicate the DB is
        generated by FlightDB.
        By default it is set to True.
        Note that this is the only DB that needs the configuration parameters.
      conf (dict): the configuration. It is optional and only required when
        goclianteDB is set to True.
    """
    self.origin = origin
    self.destination = destination
    self.adults = adults
    self.departure_date = departure_date
    self.return_date = return_date
    for date in [ departure_date, return_date ]:
      if date is not None:
        is_iso8601( date )
    self.cabin = cabin
    ## segment_list is expressed with iata codes
    self.segment_list = segment_list
    self.price = price
    self.currency = currency
    self.travel_duration = travel_duration
    self.flight_duration = flight_duration
    self.co2eq = co2eq
    if airportDB is True:
      self.airportDB = AirportDB()
    else:
      self.airportDB = airportDB
    if  cityDB is True:
      self.cityDB = CityDB( )
    else:
      self.cityDB = cityDB
    if goclimateDB is True:
      self.goclimateDB=GoClimateDB( conf )
    else :
      self.goclimateDB = goclimateDB
    if segment_list is not None and co2eq is None:
      self.co2eq = self.compute_co2eq( )


## amadeux provides means to compute Co2
## https://amadeus.readthedocs.io/en/latest/usage.html#co2-emissions


  def dist( self, iata_departure, iata_arrival ):
    ## collecting information from airport can be made via:
    ## https://pypi.org/project/Flighter/
    ## https://github.com/matthewgall/ourairports
    ## we choose ourairport API as it also provides a airport location API.

    coordinates = []
    for iata in [ iata_departure, iata_arrival ]:
      try:
        airport = self.airportDB.get_airport_by_iata( iata )
        coordinates.append( ( airport[ 'latitude' ], airport[ 'longitude' ] ) )
      except KeyError:
        try:
          city = self.cityDB.get_city_by_iata( iata )
          coordinates.append( ( city[ 'latitude' ], city[ 'longitude' ] ) )
        except:
          raise ValueError(f"{city} cannot be retrieved from {iata}: "\
                           f"Check {iata} is proper IATA airport or city code" )
    return great_circle( coordinates[0], coordinates[1] ).km

  ## myclimate2018_co2
  def co2eq_myclimate2018( self, distance, cabin='ECONOMY') :
    """ total CO2 equivalent per passenger in kg

      class can be in 'ECONOMY', 'BUSINESS' or 'FIRST'
    """
    PLF = 0.82
    DC = 95
    EF = 3.15
    P = 0.54
    M = 2
    AF = 0.00038
    A = 11.68
    x = distance + DC
    if x <= 1500 :
      S = 153.51
      CF = 1 - 0.93
      CW = { 'ECONOMY' : 0.96, 'BUSINESS' : 1.26, 'FIRST' : 2.4 }
      a = 0
      b = 2.714
      c = 1166.52
    elif x >= 2500:
      S = 280.21
      CF = 1 - 0.74
      CW = { 'ECONOMY' : 0.80, 'BUSINESS' : 1.54, 'FIRST' : 2.4 }
      a = 0.0001
      b = 7.104
      c = 5044.93

    if x <= 1500 or x >= 2500:
      E = ( a * x ** 2 + b * x + c ) / ( S * PLF ) * ( 1 - CF ) *\
          CW[ cabin ] * ( EF * M + P ) + AF * x + A
    elif x > 1500 and x < 2500:
      alpha  = ( self.co2eq_myclimate2018( 2500 - DC, cabin=cabin ) - \
               self.co2eq_myclimate2018( 1500 - DC, cabin=cabin ) ) / 1000
      beta = self.co2eq_myclimate2018( 2500 - DC, cabin=cabin ) - alpha * ( 2500 )
      E = alpha * x + beta
    return E


  def convert_to_iata_airport_list( self, iata ) -> list:
    """ converts IATA (city or airport) codes into a list of IATA airport code

    Some application require airport code IATA
    """
    if iata in [ 'ZYR' ] or self.airportDB.is_iata_airport_code( iata ) == True :
      iata_list = [ iata ]
    elif self.cityDB.is_iata_city_code( iata ):
      airport_list = self.cityDB.airport_list_of( { 'iata': iata } )
      iata_list = [ airport[ 'iata' ]  for airport in airport_list ]
    else : 
      raise ValueError( f"Unexpected city IATA code {iata}" \
        f"-- neither city IATA code nor airport IATA code. Consider " \
        f"updating IATA_SWAP in iata_airport function." )
    return iata_list

  ## icao2018

  def compute_co2eq( self ):
    ## for amadeus CO2 computation
    ## https://amadeus.readthedocs.io/en/latest/usage.html
    co2eq = { 'myclimate' : 0 }
    if self.goclimateDB is not None:
      co2eq[ 'goclimate' ] = 0
    for seg in self.segment_list:
      origin = seg[0]
      destination = seg[1]
      for co2_computation in co2eq.keys() :
        if co2_computation == 'myclimate':
          distance = self.dist( origin, destination )
          added_co2 = self.co2eq_myclimate2018( distance, cabin=self.cabin )
        elif co2_computation == 'goclimate':
          ## goclimate only seems to take iata airport code,
          ## so this does not work for city iata codes
          origin_list = self.convert_to_iata_airport_list( origin )
          destination_list  = self.convert_to_iata_airport_list( destination )
          for origin in origin_list:
            for destination in destination_list:
              try:
                added_co2 = self.goclimateDB.get_first( origin=origin, \
                              destination=destination, cabin=self.cabin )[ 'co2eq' ]
                break
              except ValueError:
                print( "Unable to get origin: {origin} - destination: {destination}" )
                pass
            else: # if no breaks occurs
              continue
            break # if a break occurs in the inner break the outer loop
          else: ## no break occured
            raise ValueError( f"GoClimate: Unable to resolve any combination of " \
              f"origin_list: {origin_list} - destination_list: {destination_list}. " \
              f"Consider chosing a alternative airport by updating IATA_SWAP in " \
              f"the GoClimate class." )
        co2eq[ co2_computation ] += added_co2
    return co2eq

  def export( self ):
    return {
      'origin' : self.origin,
      'destination' : self.destination,
      'departure_date' : self.departure_date,
      'return_date' : self.return_date,
      'cabin' : self.cabin,
      'adults' : self.adults,
      'segment_list' : self.segment_list,
      'price' : self.price,
      'currency' : self.currency,
      'travel_duration' : str( self.travel_duration ),
      'flight_duration' : str( self.flight_duration ),
      'co2eq' : self.co2eq }

