import json
from co2eq.flight_utils import get_flight, FlightDB

## For a single query, the simplest way to request a flight
origin = 'PAR'      # IATA city code
destination = 'LAX' # IATA airport code

print( "get_flight: The simplest reliable way to retrieve a flight!" )
print( "  get_flight is simple and handle a number of errors" )
print( "  transparently - such as bad date, Amadeus not responding,...." )
print( f"The resulting round trip from {origin} to {destination}:" )
flight = get_flight( origin, destination )
print( json.dumps( flight, indent=2  ) )

print("\n\n")
print( "lightDB.select_flight: a simple way to retrieve a flight!" )
print( "  The basic function, that enables finer search, but may also" )
print( "  require to handle erros manually" )
print( f"The resulting round trip from {origin} to {destination}:" )
flightDB = FlightDB()
flight = flightDB.select_flight( origin, destination )
print( json.dumps( flight, indent=2  ) )


