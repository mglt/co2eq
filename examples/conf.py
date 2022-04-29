CONF = {
  ## The directory where air flights, or CO2 emissions for a given air flight
  ## requested to GO Climate are stored after it has been requested.
  ## The main purpose if to prevent co2eq to resolve the same request multiple time
  'CACHE_DIR' : "", 

  ## co2eq retrieves flight offers to estimate a real flight and uses the AMADEUS API:
  ## https://developers.amadeus.com/get-started/get-started-with-amadeus-apis-334
  ## You need to register and request and an API Key and an API Secret for the
  ## Flight Offers Search service.
  'AMADEUS_ID' : "ZVCEHBaThOa3dgit8AkvVC4ATmLpcMAv",
  'AMADEUS_SECRET' : "wKv8R9a23vuhs2uG",

  ## To compute the CO2 emissions associated a flight a request is sent to GO Climate
  ## Please go through https://api.goclimate.com/docs to get an account.
  'GOCLIMATE_SECRET' :  "75a14c715582fd1613297e5c",
  'NOMINATIM_ID' : "P2LGDAyXKBJFv34F", 

  ## where logs are stored. We suggest you perform tail -f your_log_file
  ## to monitor what can possibly go wrong.
  'log' : './co2eq.log',

  ## Directory where all outputs are stored
  'OUTPUT_DIR' : "",

  ## CityDB specific parameters
  ## ISO3166_REPRESENTATIVE_CITY enable to indicate a specific
  ## representative city for that country.
  ## This is usually useful when the capital is not the main 
  ## representative city or when no flight can be retrieved from 
  ## that country
  'ISO3166_REPRESENTATIVE_CITY' : {
    'IL' : { 'name' : "Tel Aviv Yafo", 'iata' : 'TLV' },
    'PS' : { 'name' : "Tel Aviv Yafo", 'iata' : 'TLV' }, # no capital
    'AU' : { 'name' : "Sydney", 'iata' : 'YQY' },
    'NZ' : { 'name' : "Auckland", 'iata' : 'AKL' },
    'CY' : { 'name' : "Larnaca", 'iata' : 'LCA' },
    'CH' : { 'name' : "Zurich", 'iata' : 'ZRH' },
    'ZA' : { 'name' : "Johannesburg", 'iata' : 'JNB' },
    'CI' : { 'name' : "Abidjan", 'iata' : 'ABJ' },
    'SK' : { 'name' : "Kosice", 'iata' : 'KSC' },
    'BO' : { 'name' : 'Sao Paulo', 'iata' : 'SAO' },
    'CA' : { 'name' : "Toronto", 'iata' : 'YTO' },
    'CM' : { 'name' : "Douala", 'iata' : 'DLA' },
    'NG' : { 'name' : "Lagos", 'iata' : 'LOS' },
  ##  'BM' : 'Bermuda',
    'TZ' : { 'name' : "Dar Es Salaam", 'iata' : 'DAR' },
  #  'GU' : 'Guam',
    'KZ' : { 'name' : "Almaty", 'iata' : 'ALA' },
  ###  'GD' : 'Grenada',
    'BR' : { 'name' : 'Sao Paulo', 'iata' : 'SAO' },
    'AD' : { 'name' : 'Toulouse', 'iata' : 'TLS' },
    'AD' : { 'name' : 'Toulouse', 'iata' : 'TLS' },
    'VN' : { 'name' : 'Ho Chi Minh', 'iata' : 'SGN' },
  #  'TG' : { 'name' : 'Abidjan', 'iata': 'ABJ' }, ## Lome has the largest airport of 
                                                   ## TG but a very limited number of flights
    'MM' : { 'name' : "Yangon", 'iata' : 'RGN' },
  
     ### The following redirections happens as AMADEUX is not able to retrieve an itinerary 
     ## from these airport.
    'KY' : { 'name' : "Kingston", 'iata' : 'KIN'},  ##  few routes redirection to Jamaica
    'TC' : { 'name' : 'Santo Domingo', 'iata' : 'SDQ' },
    'HT' : { 'name' : 'Santo Domingo', 'iata' : 'SDQ' },
    'MS' : { 'name' : "San Juan", 'iata' : 'SJU' },
    'SX' : { 'name' : "San Juan", 'iata' : 'SJU' },
    'LC' : { 'name' : "San Juan", 'iata' : 'SJU' },
    'BB' : { 'name' : "San Juan", 'iata' : 'SJU' },
    'VC' : { 'name' : "San Juan", 'iata' : 'SJU' },
    'GY' : { 'name' : "San Juan", 'iata' : 'SJU' },
    'KN' : { 'name' : "San Juan", 'iata' : 'SJU' },
    'GD' : { 'name' : "San Juan", 'iata' : 'SJU' },
    'VI' : { 'name' : "San Juan", 'iata' : 'SJU' },
    'DM' : { 'name' : "San Juan", 'iata' : 'SJU' },
    'AW' : { 'name' : "San Juan", 'iata' : 'SJU' },
    'AI' : { 'name' : "San Juan", 'iata' : 'SJU' },
    'CW' : { 'name' : "San Juan", 'iata' : 'SJU' },
    'UM' : { 'name' : "San Juan", 'iata' : 'SJU' }, ## Needs to be specified. country_info 
                                                    ## returns 3 cities for capital.  
    'CU' : { 'name' : "Miami", 'iata' : 'MIA' },
    'HN' : { 'name' : "Miami", 'iata' : 'MIA' },
    'BZ' : { 'name' : "Mexico City", 'iata' : 'MEX' },
    'GT' : { 'name' : "Mexico City", 'iata' : 'MEX' },
    'VE' : { 'name' : "Panama City", 'iata' : 'PTY' },
    'EC' : { 'name' : "Panama City", 'iata' : 'PTY' },
    'SR' : { 'name' : "Panama City", 'iata' : 'PTY' },
  #
    'AS' : { 'name' : "Auckland", 'iata' : 'AKL' },
    'FJ' : { 'name' : "Auckland", 'iata' : 'AKL' },
    'NU' : { 'name' : "Auckland", 'iata' : 'AKL' },
    'CK' : { 'name' : "Auckland", 'iata' : 'AKL' },
    'TK' : { 'name' : "Auckland", 'iata' : 'AKL' },
    'TV' : { 'name' : "Auckland", 'iata' : 'AKL' },
    'TO' : { 'name' : "Auckland", 'iata' : 'AKL' },
    'KI' : { 'name' : "Auckland", 'iata' : 'AKL' },
    'AQ' : { 'name' : "Auckland", 'iata' : 'AKL' }, ## Needs to be specified as country_info 
                                                    ## does not returns capital or capital_latlng 
                                                    ## - likely to be an error as none lives in AQ, 
                                                    ## redirected to New Zealand
  #  'PG' : { 'name' : "Jayapura", 'iata' : 'DJJ' }
    'UM' : { 'name' : "Brisbane", 'iata' : 'BNE' }, ## Needs to be specified as country_info does not 
                                                    ## return capital or capital_latlng. The capital 
                                                    ## is Washignton DC which is only administrative
    'NC' : { 'name' : "Brisbane", 'iata' : 'BNE' },
    'PG' : { 'name' : "Brisbane", 'iata' : 'BNE' },
    'NR' : { 'name' : "Brisbane", 'iata' : 'BNE' },
    'VU' : { 'name' : "Sydney", 'iata' : 'YQY' },
    'FM' : { 'name' : "Quezon", 'iata' : 'MNL' },
  #
    'GG' : { 'name' : "Paris", 'iata' : 'PAR' }, ## closest airport is too small and Paris is well 
                                                 ## connected by train
    'KM' : { 'name' : "Dar Es Salaam", 'iata' : 'DAR' },
    'GI' : { 'name' : "Malaga", 'iata' : 'AGP' },
  #  'GW' : { 'name' : "Conakry", 'iata' : 'CKY' },
    'GW' : { 'name' : "Dakar", 'iata' : 'DKR' },
    'GN' : { 'name' : "Dakar", 'iata' : 'DKR' },
    'SL' : { 'name' : "Dakar", 'iata' : 'DKR' },
    'TD' : { 'name' : "Lagos", 'iata' : 'LOS' },
    'BI' : { 'name' : "Nairobi", 'iata' : 'NBO' },
    'CF' : { 'name' : "Douala", 'iata' : 'DLA' },
    'LY' : { 'name' : "Tunis", 'iata' : 'TUN' },
    'SZ' : { 'name' : "Johannesburg", 'iata' : 'JNB' },
    'TF' : { 'name' : "Johannesburg", 'iata' : 'JNB' }, ## Needs to be specified as country_info does 
                                                        ## not returns capital or capital_latlng - likely 
                                                        ## to be an error as few live in the Kerguelen Islands.
    'BV' : { 'name' : "Johannesburg", 'iata' : 'JNB' }, ## Needs to be specified as country_info does not 
                                                        ## returns capital or capital_latlng - likely to be 
                                                        ## an error as none lives inthe Bouvet Islands.
    'HM' : { 'name' : "Johannesburg", 'iata' : 'JNB' }, ## Needs to be specified as country_info does not 
                                                        ## returns capital or capital_latlng - likely to be 
                                                        ## an error as none lives inthe Heard Island and 
                                                        ## McDonald Islands.
    'ST' : { 'name' : "Abidjan", 'iata' : 'ABJ' }, ## few routes redirecting to Cote d'Ivoire
    'MG' : { 'name' : "Mauritius", 'iata' : 'MRU' },
    'YT' : { 'name' : "Mauritius", 'iata' : 'MRU' },
    'LI' : { 'name' : "Brussels", 'iata' : 'ZRH' },
    'LU' : { 'name' : "Brussels", 'iata' : 'BRU' },
    'SI' : { 'name' : "Vienna", 'iata' : 'VIE' },
    'FO' : { 'name' : "Oslo", 'iata' : 'OSL' },
  ##'CN' : { 'name' : "Shanghai", 'iata' : 'SHA' },  ## no connection to San Juan from Beijn
    'DE' : { 'name' : "Frankfurt", 'iata' : 'FRA' },
    'PF' : { 'name' : "Tahiti", 'iata' : 'PPT' },
    'NP' : { 'name' : "Patna", 'iata' : 'PAT' },
    'BT' : { 'name' : "Patna", 'iata' : 'GAU' },
    'ID' : { 'name' : "Singapore", 'iata' : 'SIN' }, ## default is JKT specifying a specific airport
    'CC' : { 'name' : "Singapore", 'iata' : 'SIN' }, 
    'KP' : { 'name' : "Singapore", 'iata' : 'SEL' }, 
    'EH' : { 'name' : "Marrakech", 'iata' : 'RAK' },
    'YE' : { 'name' : "Muscat", 'iata' : 'MCT' },
    'SY' : { 'name' : "Beirut", 'iata' : 'BEY' },
  }
}
