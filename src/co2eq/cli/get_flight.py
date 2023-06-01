#!/usr/bin/python
#import sys
#sys.path.insert(0, './../../')


import json
import argparse
import os
import pathlib
import co2eq.conf
import co2eq.flight_utils

def get_flight( origin, destination, conf=co2eq.conf.Conf().CONF,\
                departure_date=None, return_date='0001-01-01', \
                adults=1, cabin="ECONOMY" ):
  """ return a flight from origin to destination

  The function tries with default values provided by FlightDB and in case no
  offer is provided performs another lookup with different dates.
  In our cases, the dates are 5 days latter.
  """
  airportDB = co2eq.flight_utils.AirportDB()
  cityDB = co2eq.flight_utils.CityDB( conf, airportDB=airportDB )
  goclimateDB = co2eq.flight_utils.GoClimateDB( conf )
  flightDB = co2eq.flight_utils.FlightDB( conf, cityDB=cityDB, airportDB=airportDB, goclimateDB=goclimateDB)
  try:
    flight = flightDB.select_flight( origin, destination )
  except ( ValueError ) :
    ## retry with other dates - in this case 5 days later
    ## if no specific dates were specified
    if departure_date is None and return_date in [ None, '0001-01-01' ] :
      departure_date = flightDB.departure_date
      return_date = flightDB.return_date
      alt_departure = datetime.strptime( departure_date + 'T16:41:24+0200', "%Y-%m-%dT%H:%M:%S%z")
      alt_departure = ( alt_departure + timedelta( days=5 ) ).isoformat()
      alt_return = datetime.strptime( return_date + 'T16:41:24+0200', "%Y-%m-%dT%H:%M:%S%z")
      alt_return = ( alt_return + timedelta( days=5 ) ).isoformat()
      flight = flightDB.select_flight( origin, destination, departure_date=alt_departure, return_date=alt_return )
  return flight

def cli():
  description = """ Retrieves Air Flight information between IATA cities 

  Example: to return the information associated to flight between 
  PAR and LAX, type: co2eq-flight LAX PAR

  The output is as follows:

  {
  "origin": "PAR",
  "destination": "LAX",
  "departure_date": "2021-11-18",
  "return_date": "2021-11-25",
  "cabin": "ECONOMY",
  "adults": 1,
  "segment_list": [
    [
      "CDG",
      "FRA"
    ],
    [
      "FRA",
      "LAX"
    ],
    [
      "LAX",
      "YUL"
    ],
    [
      "YUL",
      "CDG"
    ]
  ],
  "price": "719.98",
  "currency": "EUR",
  "travel_duration": "1 day, 5:50:00",
  "flight_duration": "1 day, 0:53:00",
  "co2eq": {
    "myclimate": 3081.790499572582,
    "goclimate": 3900.0
  }
}

  """
  parser = argparse.ArgumentParser( description=description )
  parser.add_argument('origin', type=ascii,\
    help="Flight origin (IATA airport code or IATA city code)" )
  parser.add_argument('destination', type=ascii,\
    help="Flight destination (IATA airport code or IATA city code)" )
  parser.add_argument('-e', '--env', type=pathlib.Path, help="configuration file" )
  parser.add_argument('-d', '--departure_date', \
    help="Departure date expressed as YYYY-MM-DD" )
  parser.add_argument('-r', '--return_date',\
    action='store_const', default='0001-01-01', const='0001-01-01',\
    help="""Return date expressed as YYYY-MM-DD. The special value
      '0001-01-01' indicates a return but no specific date. For a 
      single flight the return_date needs to be set to 'single'.""" )
  parser.add_argument('-a', '--adults', default=1, help="Number of adults" )
  parser.add_argument('-c', '--cabin', type=ascii,\
    default='ECONOMY', help="Cabin class can be ECONOMY, BUSINESS, FIRST" )

  args = parser.parse_args()
  print( f"args: {args}" )
  
  if args.env is not None: 
    if os.path.isfile( args.env ) is False:
      raise ValueError( f"Unable to locate {args.env}")
  conf = co2eq.conf.Conf( env_file=args.env ).CONF 
  origin = args.origin[ 1 : -1 ]
  destination = args.destination[ 1 : -1 ]
  if args.departure_date is None:
    departure_date = args.departure_date
  else: 
    departure_date = args.departure_date[ 1 : -1 ]
  if args.return_date == "'single'":
    return_date = None
  else: 
    return_date = args.return_date[ 1 : -1 ]
  adults = args.adults  
  cabin = args.cabin[ 1 : -1 ] 

  flight = get_flight( origin, destination, conf=conf,\
                departure_date=departure_date, return_date=return_date, \
                adults=adults, cabin=cabin )
  print( json.dumps( flight, indent=2  ) )
