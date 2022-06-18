from co2eq.meeting import get_flight

## For a single query, the simplest way to request a flight
origin = 'PAR'      # IATA city code
destination = 'LAX' # IATA airport code
flight = flightDB.select_flight( origin, destination )

print( "The simplest way to retireve a flight!" )
print( flight )

