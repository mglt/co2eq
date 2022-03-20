`co2eq` estimates the CO2 emissions associated to air flights.
It is currently focused on a single meeting or a serie of meetings like a conference that happens multiple times a year for example. 
CO2 emissions can be estimated according to the flying distance between each attendee and the meeting place (distance mode). 
However, CO2 emissions are highly dependent on the number of legs of a given flight itineraries. 
The originality of `co2eq` is that for each participant, `co2eq` derive an effective flight and estimates the CO2 emissions considering each of these legs (flight mode).

`co2eq` plots the repartitions of CO2 emissions according to any criteria associated to each attendee.

While the focus is on C02 `co2eq` also performs more standard representations of attendance in number of participants (attendee mode).

A detailed description of `co2eq` can be found here:

* Daniel Migault *CO2eq*: "Estimating Meetings' Air Flight CO2 Equivalent Emissions - An Illustrative Example with IETF meetings", Show me the numbers: Workshop on Analyzing IETF Data (AID), 2021. [https://www.iab.org/wp-content/IAB-uploads/2021/11/Migault.pdf](https://www.iab.org/wp-content/IAB-uploads/2021/11/Migault.pdf). 


A example of the outputs of `co2eq` outputs can be found on the `co2eq` web site https://mglt.github.io/co2eq/, 
where CO2 emissions have been computed for the [IETF](https://mglt.github.io/co2eq/IETF/IETF/) meetings and the [ICANN](https://mglt.github.io/co2eq/ICANN/ICANN/).

# Installation 

Installation of co2eq can be done using pip
```
pip install co2eq
```

or directly from github

```
git clone https://github.com/mglt/co2eq
cd co2eq # 
python3 -m build && pip3 install --force-reinstall  dist/co2eq-0.0.2.tar.gz 
```


The development of co2eq have lead to the data of the country_info package to be updated. Before this modification being released in the country_info release, the updated version of country_info can be installed as follows:

```
git clone https://github.com/mglt/countryinfo
cd country_info
python3 setup.py install
```

To compute the CO2 using GO Climate service, the climate neutral package needs to be installed.

```
git clone https://github.com/codeboten/climate_neutral
cd climate_neutral
sudo python3 install setup.py

``
If other classes than 'economy' are used, an advanced use of co2eq may also require an updated version of climate neutral 

```
git clone https://github.com/mglt/climate_neutral
cd climate_neutral
sudo python3 install setup.py
```

# Configuring and using co2eq

The example directory contains examples on how to use co2eq.

In general, you will need a configuration object commonly designated as `conf`. 
It is recommended to generated it by completeing the conf_template.py file which contains the following dictionary:

```
CONF = {
  ## The directory where air flights, or CO2 emissions for a given air flight 
  ## requested to GO Climate are stored after it has been requested. 
  ## The main purpose if to prevent co2eq to resolve the same request multiple time 
  'CACHE_DIR' : "",

  ## co2eq retrieves flight offers to estimate a real flight and uses the AMADEUS API:
  ## https://developers.amadeus.com/get-started/get-started-with-amadeus-apis-334
  ## You need to register and request and an API Key and an API Secret for the 
  ## Flight Offers Search service.
  'AMADEUS_ID' : "",
  'AMADEUS_SECRET' : "",

  ## To compute the CO2 emissions associated a flight a request is sent to GO Climate 
  ## Please go through https://api.goclimate.com/docs to get an account.
  'GOCLIMATE_SECRET' : "" ,
  'NOMINATIM_ID' : "",

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
  'ISO3166_REPRESENTATIVE_CITY' : { }
  }
```




