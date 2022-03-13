def iata_city_airport_csv_to_json( self ):
  """ generates a json dictionary matching a IATA city code to a list of IATA airport code.

  The cvs is built from the ICAO publication and provided into the package.
  Since the json format is provided as part of the package, this function
  is unlikely to be useful.
  Eventually, the code might be re-use if the database is regenerated
  from a more recent txt file.

  """
  iata_city_iata_airport_list_dict = {}
  with gzip.open( join( DATA_DIR, 'iata_city_airport_map.csv.gz' ), 'rt', encoding="utf8" ) as f:
    for l in f.readlines():
      array = l.split( ',' )
      iata_airport = array[ 0 ].strip()
      iata_city = array[ 1 ].strip()
      if "Code" in array[ 0 ]: # skip header
        continue
      try:
        iata_city_iata_airport_list_dict[ iata_city ].append( iata_airport )
      except KeyError:
        iata_city_iata_airport_list_dict[ iata_city ] = [ iata_airport ]
    with gzip.open( join( DATA_DIR, 'iata_city_airport_map.json.gz' ), 'wt', encoding="utf8"  ) as out:
      out.write( json.dumps( iata_city_iata_airport_list_dict, indent=2 ) )

def is_iata_city_code( self, iata ) -> bool:
  """ returns true is iata is an IATA city code"""
  if iata in self.iata_city_iata_airport_list_dict.keys():
    return True
  return False
