# import requests
import json
import gzip
#from datetime import timedelta
from os.path import join # getsize, isfile
from statistics import median
from random import random
from datetime import date, timedelta, datetime
import calendar
from time import sleep, ctime
from pkg_resources import resource_filename
from amadeus import Client, ResponseError
from isodate import parse_duration
import iso8601
from countryinfo import CountryInfo
from ourairports import OurAirports
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from geopy.distance import great_circle


from climate_neutral import GoClimateNeutralAPI, Segment # Footprint

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


class MultipleMatchError( Exception ):
  def __init__(self, message=""):
    """ returns a printable message with the selectors and resulting outputs """
    self.message = f"Multiple matching locations for {message}\n." \
                   f"Consider using IATA code instead."\
                   f" https://www.iata.org/en/publications/directories/code-search/?airport.search=XXXX \n"
    super().__init__(self.message)

class NoMatchError( Exception ):
  def __init__(self, message=""):
    self.message = f"No matching location for {message}.\n" \
                   f"Consider using IATA code instead" \
                   f"https://www.iata.org/en/publications/directories/code-search/?airport.search=XXXX \n"
    super().__init__(self.message)

## swaps countries to a geographically most relevant to find an airport

## when a country is provided as a location (origin or departure),
## we need to find a corresponding IATA airport (from the IATA city DB)
## and that IATA airport needs to provide flights offers amadeus databases search.
## At the time we performed the tests (during covid19 pandemy) some
## countries did not provide flights to expected destinations.
## For that reasons we swap the country to another geographically relevant country.

ISO3166_SWAP = { 'PS' : 'IL',
                 'AD' : 'FR',
                 'TF' : 'NZ',
                 'CK' : 'NZ',
                 'TV' : 'NZ',
                 'TK' : 'NZ',
                 'FJ' : 'NZ',
                 'NR' : 'NZ',
                 'AS' : 'NZ',
                 'WS' : 'NZ',
                 'TO' : 'NZ',
                 'VU' : 'NZ',
                 'NC' : 'AU',
                 'BT' : 'CN',
                 'NP' : 'CN',
                 'BO' : 'PE',
                 'MM' : 'TH',
                 'SR' : 'CO',
                 'LY' : 'TN',
                 'YE' : 'OM',
                 'CW' : 'LC',
                 'SX' : 'LC',
                 'AN' : 'LC',
                 'MS' : 'LC',
                 'VC' : 'LC',
                 'BB' : 'LC',
                 'AG' : 'LC',
                 'VG' : 'LC',
                 'KN' : 'LC',
                 'LI' : 'CH',
                 'TL' : 'ID',
                 'CX' : 'ID',
                 'LA' : 'TH',
                 'VA' : 'IT',
                 'VE' : 'CO',
                 'HM' : 'ZA',
                 'LS' : 'ZA',
                 'AQ' : 'ZA',
                 'UM' : 'JP',
                 'HT' : 'DO',
                 'AI' : 'DO',
                 'VI' : 'DO',
                 'TC' : 'DO',
                 'CC' : 'ID',
                 'SY' : 'LB',
                 'BJ' : 'TG',
                 'GA' : 'CM',
                 'CF' : 'CM',
                 'MG' : 'MU',
                 'GW' : 'SN',
                 'GG' : 'GB',
                 'JE' : 'GB',
                 'AX' : 'FI',
                 'FM' : 'ID',
                 'SC' : 'MU',
                 'EH' : 'MR',
                 'CD' : 'AO',
                 'KP' : 'KR'
                }

## Binds ISO3166 country code to a city that is in the IATA DB with the largest airport.

## This is typically usefull when the economic city does not corresponds to the capital.
## In some cases this overwrite the capital to the corresponding entry in the IATA DB
## - typically when the entry is not the capital but the country name.

ISO3166_TO_IATA_CITY = { 'IL' : 'Tel Aviv Yafo',
                         'RS' : 'Belgrade',
                         'ME' : 'Podgorica',
                         'AU' : 'Sydney',
                         'NZ' : 'Auckland',
                         'CY' : 'Larnaca',
                         'CH' : 'Zurich',
                         'DO' : 'Punta Cana',
                         'ZA' : 'Johannesburg',
                         'CI' : 'Abidjan',
                         'BZ' : 'Belize',
                         'SK' : 'Kosice',
                         'HK' : 'Hong Kong',
                         'UG' : 'Entebbe',
                         'BO' : 'Santa Cruz',
                         'CA' : 'Toronto',
                         'BJ' : 'Cotonou',
                         'LC' : 'St Lucia',
                         'MO' : 'Macao',
                         'AW' : 'Aruba',
                         'KY' : 'Grand Cayman',
                         'BB' : 'BGI',
                         'YT' : 'Dzaoudzi',
                         'PY' : 'Asuncion',
                         'KW' : 'Kuwait',
                         'BN' : 'Bandar Seri B',
                         'MT' : 'Malta',
                         'CM' : 'Douala',
                         'BM' : 'Bermuda',
                         'TZ' : 'Dar Es Salaam',
                         'GU' : 'Guam',
                         'KZ' : 'Almaty',
                         'GD' : 'Grenada',
                         'BR' : 'Sao Paulo'
                       }



class CityDB (JCacheList):
  def __init__( self, cache_path= join( DATA_DIR, "iata_city_codes-2015.json.gz" ) ):
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
    super().__init__( cache_path )
    self.micro_cache = {}
    with gzip.open( join( DATA_DIR, 'iata_city_airport_map.json.gz' ), 'rt', encoding="utf8" ) as f:
      self.iata_city_airport_map = json.loads( f.read() )

  def citydb_txt_to_json( self, conf ):
    """ Converts the txt database of IATA cities into a json file

    Since the json format is provided as part of the package, this function
    is unlikely to be useful.
    Eventually, the code might be re-use if the database is regenerated
    from a more recent txt file.

    """
    city_db = []
    geolocator = Nominatim( user_agent=conf[ 'NOMINATIM_ID' ] )
    with open( join( DATA_DIR, "iata_city_codes-2015.txt.gz"), 'r', encoding="utf8" ) as f:
      for line in f:
        if line[0] == '#' or len(line) == 1: # skip commented line or empty line
          continue
        line = line.split()
        iata = line[0]
        country = line[ -1 ]
        state = line[ -2 ]
        if state.isupper() and len( state ) == 2:
          tmp_name = line[1:-2]
        else:
          state = None
          tmp_name = line[1:-1]
        name = tmp_name[0]

        for n in tmp_name[1:]:
          name += ' ' + n
        sleep(2)
        try:
          location  = geolocator.geocode( country + ' ' + name )
          if location: ## a location is returned
            latitude =  location.latitude
            longitude = location.longitude
          else: ## no location is returned
            ## we will assume that location is not returned by the
            ## API for cities we do not need.... let's keep finger crossed.
            latitude =  None
            longitude = None
          city_db.append({
            'name' : name,
            'iata' : iata,
            'latitude' : latitude,
            'longitude' : longitude,
            'country' : country,
            'state' : state })
          ## entering table after each new entry
          ## this is to avoid to replay the full cities when an error occurs
          with gzip.open( join( DATA_DIR, "iata_city_codes-2015.tmp.gz"), 'w', encoding="utf8" ) as f:
            f.write( json.dumps( city_db, indent=2 ) )
        except:
          with gzip.open( join( DATA_DIR, "iata_city_codes-2015.log.gz"), 'a', encoding="utf8" ) as f:
            f.write( f"ERROR: {ctime()} cannot find localisation for {country} - {name}\n" )
    with gzip.open( join( DATA_DIR, "iata_city_codes-2015.json.gz"), 'wt', encoding="utf8" ) as f:
      f.write( json.dumps( self.cache, indent=2 ) )

  def iata_city_airport_csv_to_json( self ):
    """ generates a json dictionary matching a IATA city code to a list of IATA airport code.

    the cvs is built from the ICAO publication and provided into the package.
    Since the json format is provided as part of the package, this function
    is unlikely to be useful.
    Eventually, the code might be re-use if the database is regenerated
    from a more recent txt file.

    """
    iata_city_airport_map = {}
    with gzip.open( join( DATA_DIR, 'iata_city_airport_map.csv.gz' ), 'rt', encoding="utf8" ) as f:
      for l in f.readlines():
        array = l.split( ',' )
        iata_airport = array[ 0 ].strip()
        iata_city = array[ 1 ].strip()
        if "Code" in array[ 0 ]: # skip header
          continue
        try:
          iata_city_airport_map[ iata_city ].append( iata_airport )
        except KeyError:
          iata_city_airport_map[ iata_city ] = [ iata_airport ]
      with gzip.open( join( DATA_DIR, 'iata_city_airport_map.json.gz' ), 'wt', encoding="utf8"  ) as out:
        out.write( json.dumps( iata_city_airport_map, indent=2 ) )


  def get_iata_airport_list( self, iata_city ) -> list :
    """ for a valid iata_city code, the list of mapped iata airport codes are returned

    Args:
      iata_city (str) : the iata city code

    Returns:
      iata_airport_list (list): when the iata city codes is a valid iata
        code, the list of corresponding iata airport codes is returned.
        Note that the list may also contain the iata_city code.
        In the vast majority of the cases the iata city code and airport
        code is the same.
      None: when the input does not match a iata city code, None is
        returned. This may result from an unvalid iata code or a valid
        iata code that is only an airport iata code - not a city iata code.
    """
    try:
      iata_list = self.iata_city_airport_map[ iata_city ]
    except KeyError:
      iata_list =  None
    return iata_list

##  def iata_db_format( self, city_name ):
  def matching_city_db_name( self, city_name ):
    """ return a corresponding city_name that match the format of the IATA city database

    This corresponds to a manual adjustment and only works for capital city name.
    Something more generic must be provided su that we may only use the
    get_city_list_by_name function.

    Todo:

    """

    ## city map can be usefull to address character issue not considered
    ## in the data base.
    ## It can also be useful to redirect a full country to another city
    ## by redirecting the capital.
    ## It does not deal with country that are not part of the module iso,
    ## nor country that have no capital, nor countries not represented
    ## in the module.
    city_name_map = { 'New Delhi' : 'Delhi',
                      'Manama' : 'Bahrain',
                      'Bern'   : 'Berne',
                      'Port Louis': 'Mauritius',
                      'Port of Spain': 'Port Of Spain',
                      'Thimphu' : 'Paro',
                      "Nuku'alofa" : 'Eua',
                      "Saint John's" : 'Antigua',
                      'Roseau' : 'Dominica',
                      'Ulan Bator' : 'Ulaanbaatar',
                      'Saint-Denis' : 'St Denis'
                      }

    letters = { 'á' : 'a', 'ă' : 'a', 'é' : 'e', 'ș' : 's', 'í' : 'i',  }
    try:
      return city_name_map[ city_name ]
    except KeyError:
      for l in letters.keys():
        city_name = city_name.replace( l, letters[ l ] )
      return city_name

  def get_city_list_by_name( self, city_name : str ) -> list:
    """ returns a list of cities whose name match city_name

    Todo:
      * A NoMatchError means the name has not been found in the data base.
      However, this may be due to mispelling for example.
      We need to be able to relax the exact match constraint and consider
      at least different spelling, or providing the closest city based
      on coordinates. (see matching_city_db_name ).

    """

    return self.get_all( name=city_name )

  def get_city_list_by_iata_code( self, iata_code : str) -> list:
    """ returns a list of cities whose name match iata_code """
    return self.get_all( iata=iata_code )

  def get_city_list_by_city_name_country( self, city_name :str ,\
                                          country : str, state=None ) -> list:
    """ returns a list of cities matching city_name, country and state (when provided) """

    if country in [ 'RS', 'ME' , 'MM' ]: ## not in CountryInfo. Check how to update CountryInfo
      pass
    else:
      country = CountryInfo( country ).iso( 2 )
    if state is None:
      city_list = self.get_all( name=city_name, country=country )
    else:
      city_list = self.get_all( name=city_name, country=country, state=state )
    return city_list

  def is_city( self, city_list : list):
    """ returns the city object if there is a single match,

    Returns:
       city: the single city when ther eis a single match
    Raises:
      MultipleMatchError, NoMatchError
    """

    if len( city_list ) == 1:
      if city_list[ 0 ] is not None:
        return city_list[ 0 ]
      else:
        raise NoMatchError( )
    elif len( city_list ) >= 2:
      raise MultipleMatchError( city_list )
    elif len( city_list ) == 0:
      raise NoMatchError( )

  def get_city_by_name( self, city_name : str ) -> dict :
    """ returns a list of cities whose name match city_name


    Args:
      city_name (str): the name of the city
    Raises:
      MultipleMatchError or NoCityError
    """
    try:
      city_list = self.get_city_list_by_name( city_name )
      city = self.is_city( city_list )
    except NoMatchError:
      raise NoMatchError( f"unable to find city  {city_name}" )
    return city

  def get_city_by_iata_code( self, iata_code : str ) -> dict:
    """ returns a list of cities whose name match iata_code

    Raises:
      MultipleMatchError or NoCityError


    """
    cities = self.get_city_list_by_iata_code( iata_code )
    if len( cities ) >=1:
      return cities[ 0 ]
    raise NoMatchError( f"unable to find city with IATA code {iata_code}" )

  def get_city_by_city_name_country( self, city_name, country, state=None ) -> dict:
    """ returns the unique city (when possible) whose name match
        city_name, country and state (when provided)

    Raises:
      MultipleMatchError or NoCityError
    """
    try:
      city_list =  self.get_city_list_by_city_name_country( city_name, country, state=state )
      city = self.is_city( city_list )
    except NoMatchError:
      raise NoMatchError( f"ERROR: unable to find {city_name}, {country}, {state}" )
    return city

  def get_city_by_country( self, country:str ):
    """ returns a city from country which designates a country

    Args:
     country (str) : It has currenlty beein tested with country set
       to ISO3166 country codes, but country is expected to be the
       ISO code or any other country designation.


     Todo:
       * needs to be rewritten so it works with input that are
         different from the ISO code. I think we should consider
         the country, country_iso (which is a representation of
         country ) and country_effective_iso, is the actual country
         considered for the airport. In our case country_iso should
         be designated as country_effective_iso.
     """
    if country in [ 'RS', 'ME' ]:
      country_iso = country
    else:
      ## check country neeeds to be swapped
      try :
        country = ISO3166_SWAP[ country ]
      except KeyError:
        pass
      ## try to get country ( and country_iso) from country
      try:
        country_info = CountryInfo( country )
      except:
        raise ValueError( f"Unable to recognize {country} as a country." )
      try:
        country_iso = country_info.iso( 2 )
      except:
        raise ValueError( f"Unable to provide ISO(2) country code for {country}." )

    ## get city_name
    ## mapping to a city is usually done by mapping a country code to the largest city
    ## designation that is in the IATA DB - to get an airport.
    ## Note that in some case, the largest city is not in the country and is not
    ## the largest city of that neighbor country.
    ## For that reason a country is bound to a country (se above country swapping) and
    ## also a country.
    if country == 'AD': ## country = FR
      city_name = 'Toulouse'
    elif country == [ 'BT', 'NP' ]:
      city_name = 'Lhasa/Lasa'
    elif country == 'TL':
      city_name = 'Makassar'
    elif country_iso == 'US':
      r = random()
      if r < 0.5:
        city_name = 'Washington D.C.'
      else:
        city_name = 'Los Angeles'
    else :
      try:
        city_name = ISO3166_TO_IATA_CITY[ country_iso ]
      except KeyError :
        try:
          city_name = self.matching_city_db_name( country_info.capital() )
        except:
          raise ValueError( f"Unable to find capital of country {country_iso}." )
    return self.get_city_by_city_name_country( city_name, country_iso, state=None )


  def best_guess( self, location ) -> dict:
    """ makes its best to output a city from location

    Args:
      location: may be a string that represents a IATA code, a city name,
        a tuple (city, state, coutry) or ( city, country )

    Returns:
      city (dict) : a JSON object that represents the city
    Todo:
      * micro_cache is expected handle repeated queries. It currently
        applies to all queries, though we mostly tested it for country.
    """

    ## cache
    if len( self.micro_cache.keys() ) > 10000:
      self.micro_cache = {}
    try: ## check value is in micro cache
      if location == 'US':
        r = random()
        if r < 0.5:
          city =   {
            "name": "Washington D.C.",
            "iata": "WAS",
            "latitude": 38.8949924,
            "longitude": -77.0365581,
            "country": "US",
            "state": None }
        else:
          city =  {
            "name": "Los Angeles",
            "iata": "LAX",
            "latitude": 34.0536909,
            "longitude": -118.242766,
            "country": "US",
            "state": "CA"}
      else:
        city = self.micro_cache[ location ]
      return city
    except KeyError:
      pass
##    print( f"best_guess : location: {str(location)}" )
    if isinstance( location, str ):
      try:
        ## guessing a city from IATA code
        city = self.get_city_list_by_iata_code( location )
##        print( f"best_guess : self.get_city_list_by_iata: {city}" )
        self.is_city( city )
      except NoMatchError:
        try:
          ## guessing city from name. We pick one we have teh corresponding IATA code
          city_name = self.matching_city_db_name( location )
          city = self.get_city_by_name( city_name )
          self.is_city( city )
        except NoMatchError:
          ## trying from a country
          city = self.get_city_by_country( location )
##          print( f"best_guess : self.get_city_by_country: {city}" )
    elif isinstance( location, tuple ):
      city_name = location [ 0 ]
      if len( location ) == 2:
        country = location[ 1 ]
        state = None
      if len( location ) == 3:
        state = location[ 1 ]
        country = location[ 2 ]
      city = self.get_city_by_city_name_country( city_name, country, state=state )
    else:
      raise NoMatchError( location )
    self.micro_cache[ location ] = city
##    print( f"best_guess: len( micro_cache ) : {len( self.micro_cache )}" )
    return city

  def dist( self, departure: dict, arrival: dict, dist_type='geodesic') :
    """ geodesic distance

       dep. / arrival are city object ( -- eventually returned by best_guess )
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
  def __init__( self, conf, airportDB=True, cityDB=True, goclimateDB=True):
    """ retrieve and compute flights related information such as CO2 equivalent.

    Since conf is used to generate some DB (goclimateDB), DB can either be
    provided as object of set to True to indicate these need to be generated.

    Args:
      conf (dict): configuration parameters
      airportDB: the airportDB object ( OurAirports ) or True to indicate
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
    if airportDB is True:
      self.airportDB = OurAirports()
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
        print( f"    - requesting amadeus single flight {origin} - {destination},"\
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
        print( f"    - requesting amadeus round trip flight for {origin} " \
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
      raise ValueError( f"Unable to retrieve Amadeus response {error}" )
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

class Flight:

  def __init__( self, origin=None, destination=None, departure_date=None,
                return_date=None, adults=None, cabin='ECONOMY',
                segment_list=None, co2eq=None, price=None, currency=None,
                flight_duration=None, travel_duration=None,
                airportDB = True, cityDB = True, goclimateDB=True, conf={} ):
    """ computes co2eq associated to the flight

      Args:
      airportDB: the airportDB object ( OurAirports ) or True to indicate the DB is
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
      self.airportDB = OurAirports()
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
        airport_list = self.airportDB.getAirportsByIATA( iata )
        if len( airport_list ) == 0:
          raise NoMatchError( f"IATA airport code {iata}" )
        elif len( airport_list ) > 1:
          raise MultipleMatchError( f"IATA airport code {iata} - [{airport_list}]" )
        airport = airport_list[ 0 ]
        coordinates.append( ( airport.latitude, airport.longitude ) )
      except:
        try:
          city = self.cityDB.get_city_by_iata_code( iata )
          coordinates.append( ( city[ 'latitude' ], city[ 'longitude' ] ) )
        except:
          raise ValueError(f"{iata}: Not proper IATA airport or city code" )
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


  def iata_airport( self, iata ) -> list:
    """ returns the "closest" IATA airport code

    Some application require an IATA
    """
    if iata in [ 'ZYR' ]:
      iata_list = [ iata ]
    else:
      airport_list = self.airportDB.getAirportsByIATA( iata )
      if len( airport_list ) != 0: ## iata is airport iata code
        iata_list = [ airport.iata for airport in airport_list ]
      else:
        ## iata is city iata code
        iata_list = self.cityDB.get_iata_airport_list( iata )
        if iata_list is None:
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
          origin_list = self.iata_airport( origin )
          destination_list = self.iata_airport( destination )
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



##  methods to get Co2
## https://api.goclimate.com/docs
## https://applications.icao.int/icec
## https://github.com/Alec-Stashevsky/GAP-climate-research

##maybe there is a need to get a cookie by HTTP GET
##
##GET /icec HTTP/1.1
##Host: applications.icao.int
##Connection: keep-alive
##Cache-Control: max-age=0
##Upgrade-Insecure-Requests: 1
##User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36
##Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
##Sec-GPC: 1
##Sec-Fetch-Site: none
##Sec-Fetch-Mode: navigate
##Sec-Fetch-User: ?1
##Sec-Fetch-Dest: document
##Accept-Encoding: gzip, deflate, br
##Accept-Language: en-GB,en-US;q=0.9,en;q=0.8
##Cookie: ASP.NET_SessionId=lgqltsrhs3ufaezc04pyaqns; TS01e182e3=0106b70136df93a9bed7c1b6119011c900da5b0be25884683140ef886eb6436da9ada42c5dee735e72c9b3375fe8a7933be6716a1cf20f704daab30d9d0c5d9dc2c636a230
##dnt: 1
##
##
##response
##HTTP/1.1 200 OK
##Cache-Control: private
##Content-Type: text/html; charset=utf-8
##Content-Encoding: gzip
##Vary: Accept-Encoding
##Date: Fri, 20 Aug 2021 13:39:24 GMT
##Content-Length: 17799
##Strict-Transport-Security: max-age=31104000; includeSubDomains
##Set-Cookie: TS01e182e3=0106b70136834bdbc0872e32f6f0aaa28d47fa097b620c3c673de4dcaff16c410cf8849ada23f2d9e0257a4d32e25a7e60500bde1a72e27b0d2cc1b266b272bb34e855a71a; Path=/; Domain=.applications.icao.int
##
##
##
##POST /icec/Home/getCompute HTTP/1.1
##Host: applications.icao.int
##Connection: keep-alive
##Content-Length: 151
##Accept: */*
##X-Requested-With: XMLHttpRequest
##User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36
##Content-Type: application/x-www-form-urlencoded; charset=UTF-8
##Sec-GPC: 1
##Origin: https://applications.icao.int
##Sec-Fetch-Site: same-origin
##Sec-Fetch-Mode: cors
##Sec-Fetch-Dest: empty
##Referer: https://applications.icao.int/icec
##Accept-Encoding: gzip, deflate, br
##Accept-Language: en-GB,en-US;q=0.9,en;q=0.8
##Cookie: ASP.NET_SessionId=lgqltsrhs3ufaezc04pyaqns; TS01e182e3=0106b70136df93a9bed7c1b6119011c900da5b0be25884683140ef886eb6436da9ada42c5dee735e72c9b3375fe8a7933be6716a1cf20f704daab30d9d0c5d9dc2c636a230
##dnt: 1
##
##
## ASP.NET_SessionId=lgqltsrhs3ufaezc04pyaqns; TS01e182e3=0106b70136df93a9bed7c1b6119011c900da5b0be25884683140ef886eb6436da9ada42c5dee735e72c9b3375fe8a7933be6716a1cf20f704daab30d9d0c5d9dc2c636a230


