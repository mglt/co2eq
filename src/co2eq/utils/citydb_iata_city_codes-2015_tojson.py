
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
