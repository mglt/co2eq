

# `co2eq` Overview

`co2eq` estimates the CO2 equivalent of air flight and is especially targeting international meetings. 

Estimating the CO2 emission from flying from location A to location B requires:

1. Estimating a realistic flight which might be direct of composed of multiple segments. To do so we select flights based on existing flight using the Amadeus API.
2. Estimating the emission for each segments. To do so we implemented the methodology of myclimate, as well as teh UK governement rely on the online service proposed by goclimate.  

[CO2eq: "Estimating Meetings' Air Flight CO2eq - An Illustrative Example with IETF meetings](https://www.iab.org/wp-content/IAB-uploads/2021/11/Migault.pdf) provides a more detailled description of teh methodology. [co2eq-IETF](https://mglt.github.io/co2eq/IETF/IETF/) and [co2eq-ICANN](https://mglt.github.io/co2eq/ICANN/ICANN/) show `co2eq` outputs for IETF and ICANN meetings.

The `co2eq` package contains a few command lines.

`co2eq-get-flight` can estimate a realistic flight from Los Angeles (LAX) to Paris (PAR). In the example below, the flight consisted of 4 segment flight and the corresponding emissions are 3081 kg (resp. 3900 kg) when estimated with myclimate  (resp. goclimate). 

```
co2eq-get-flight LAX PAR
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
```

For international meetings, we generaly do not know the exact origin of each attendee, but in many case we know the country of origin and the (exact) closest airport of the meeting. 
`co2eq-plot-meeting` estimate the origin of the participant. In general the participant is considered flying from the capitalk of the country, but in some cases, the capital is not the most important city. In addition, in the US, we split attendees between Est and West coast, to better reflect the air flight distance. 

If ietf72.json.gz lists the participants of the meeting IETF72, various representations of the estimation of the CO2 can be generated as follows:

```
co2eq-plot-meeting   --output_dir  ./output --meeting_name IETF72 --meeting_attendee_list ./ietf72.json.gz --meeting_location_iata 'DUB'
```

The attendee list is stored in ietf72.json.gz as follows:

```
[
  {
    "country": "US",
    "organization": "Cisco",
    "presence": "on-site"
  },
  {
    "country": "FR",
    "organization": "Nokia",
    "presence": "remote"
  },
  {
    "country": "US",
    "organization": "Google",
    "presence": "on-site"
  },
  {
    "country": "IN",
    "organization": "indian career welfare society",
    "presence": "remote"
  },
  {
    "country": "JP",
    "organization": "japan registry services co., ltd.",
    "presence": "on-site"
  }
]
```

Note that as, this package is maintained for IETF and ICANN meetings, `co2eq-plot-meeting   --output_dir  ./output --meeting_name IETF72` is sufficient.

In addition, international meetings often consist in a serie of meetings. Typically IETF and ICANN meetings occur 3 time a year.   
The serie of meetings (including all individual meetings) is plot as follows:

```
co2eq-plot-meeting   --output_dir  ./output --meeting_list_conf meeting_list_conf.json.gz
```

where meeting_list_conf.json.gz contains all information related to the meetings:

```
{
  "name": "IETF",
  "meeting_list": [
    {
      "name": "IETF72",
      "location": {
        "country": "IE",
        "city": "Dublin"
      },
      "attendee_list": "ietf/meeting_attendee_list/json/ietf72.json.gz"
    },
    {
      "name": "IETF73",
      "location": {
        "country": "US",
        "city": "Minneapolis"
      },
      "attendee_list": "ietf/meeting_attendee_list/json/ietf73.json.gz"
    },
   ...
```

Note that for IETF and ICANN meeting, these pieces of information are provided by the package and `co2eq-plot-meeting   --output_dir  ./output --meeting_template IETF` is sufficient. 




## Contributors: 

* Peeyush Man Singh ([pssingh21](https://github.com/pssingh21)) Dockerized and implemented co2eq as a web service, with web interface and backend service. An example of the service is available here: https://co2eq.netlify.app/ as well as in example/docker.
He also integrate the use of a configuration file .env


# Installation 

Installation of co2eq can be done directly from github

```bash
pip3 install co2eq
```
The development of co2eq have lead to the data of the country_info package to be updated. Before this modification being released in the country_info release, the updated version of country_info can be installed as follows:

```bash
git clone https://github.com/mglt/countryinfo
cd country_info
python3 setup.py install
To compute the CO2 using GO Climate service, the climate neutral package needs to be installed.
```

```bash
git clone https://github.com/mglt/climate_neutral
cd climate_neutral
sudo python3 setup.py install
```

## Local installation

For installing co2eq in a python virtual environment
```bash
$ pip3 install virtualenv       # If you do not have virtualenv installed
$ python3 -m virtualenv co2eq   # Create a bew virtual environment
$ source co2eq/bin/activate     # Activate the virtual environment 
```
# Configuring and using co2eq

You will need a configuration file with filename `.env`. There is already a `.env.example` file contaning the format and required parameters for reference. 
It is recommended to generated it by copying the .env.example file and filling in the configuration details.

```bash
$ cp ./example/env.example .env
```

The `.env` file should have the following format:
```
## The directory where air flights, or CO2 emissions for a given air flight
## requested to GO Climate are stored after it has been requested.
## The main purpose if to prevent co2eq to resolve the same request multiple time
CACHE_DIR = "./cache"

## co2eq retrieves flight offers to estimate a real flight and uses the AMADEUS API:
## https://developers.amadeus.com/get-started/get-started-with-amadeus-apis-334
## You need to register and request and an API Key and an API Secret for the
## Flight Offers Search service.
AMADEUS_ID = 'XXXXXXX'
AMADEUS_SECRET = 'XXXXXXXXXX'

## To compute the CO2 emissions associated a flight a request is sent to GO Climate
## Please go through https://api.goclimate.com/docs to get an account.
GOCLIMATE_SECRET =  'XXXXXXXXXX'
NOMINATIM_ID = "ietf"

## where logs are stored. We suggest you perform tail -f your_log_file
## to monitor what can possibly go wrong.
log = './co2eq.log'

## CityDB specific parameters
## ISO3166_REPRESENTATIVE_CITY enable to indicate a specific
## representative city for that country.
## This is usually useful when the capital is not the main 
## representative city or when no flight can be retrieved from 
## that country. Typically, the free account from amadeux only provides 
## sub set of the flights
ISO3166_REPRESENTATIVE_CITY = './conf_rep_cities.json'
```


# [Live App](https://co2eq.netlify.app) Deployment Status:&nbsp; [![Netlify Status](https://api.netlify.com/api/v1/badges/d8891a86-be1d-4e5a-8789-b4592385910a/deploy-status)](https://app.netlify.com/sites/co2eq/deploys)

## Running docker container (examples/docker)

```bash
$ docker build --tag co2eq .      # Build the image using Docker
$ docker run -p8000:8000 co2eq    # Run the Docker image
```

## Running the frontend

To run the frontend, open [src/frontend/index.html](src/frontend/index.html) on your browser.

If you are running the server on your local machine or a different remote server, make sure to update the backend URL in the [src/frontend/index.html](src/frontend/index.html) file. Change [const socketUrl="ws://..."](https://github.com/pssingh21/co2eq/blob/68983eb8c7506031cb830c9e6989fca2e2028db9/src/frontend/index.html#L325) to your backend URL.

## Deploying the application

To deploy the backend, build the Docker image and push the image to the server. 
To deploy the frontend, upload the [examples/docker/frontend/index.html](/frontend/index.html) file to the server.

## JSON format for the web interface
Format of JSON file to upload via frontend:
```json
{ 
    "name" : "required", 
    "location" : { 
        "country" : "required", 
        "iata": "optional"
    },
    "attendee_list": [
        {
            "country": "required",
            "iata": "optional",
            "number_of_attendee": required
        }
    ]                                    
}
```
Example:
```json
{ 
    "name" : "meeting_201", 
    "location" : { 
        "country" : "DE", 
        "iata": "SXF"
    },
    "attendee_list": [
        {
            "country": "US",
            "iata": "LAX",
            "number_of_attendee": 1
        },
        {
            "country": "FR",
            "number_of_attendee": 2
        },
        {
            "country": "JP",
            "number_of_attendee": 5
        }
    ]                                    
}

```

## JSON Format for web service (typically the one used for MeetingList)
Format of data to be sent to API endpoint:
```json
{ 
    "name" : "required", 
    "location" : { 
        "country" : "required", 
        "iata": "optional"
    },
    "attendee_list": [
        {
            "country": "required",
            "iata": "optional"
        }
    ]                                    
}
```
Example:
```json
{ 
    "name" : "meeting_201", 
    "location" : { 
        "country" : "DE", 
        "iata": "SXF"
    },
    "attendee_list": [
        {
            "country": "US",
            "iata": "LAX",
        },
        {
            "country": "FR"
        },
        {
            "country": "FR"
        },
        {
            "country": "JP"
        }
    ]                                    
}

```

# Example scripts

## simple_flight.py

`simple_flight.py` shows how to retrieve a flight from one Origin to a Destination. 
This example does not consider any estimation of CO2 emissions.

## IETF related scripts

If you are interested in running IETF meetings, you may have a look at the script with 'ietf'. 
The advantage is that you may run them without any data as the IETFMeeting class is retrieving the data from the Internet - or from the co2eq package. 
On the other hand IETFMeeting related classes have their own specificities that you may not be very interested in.

`plot_ietf100.py` computes the data for a single meeting (the IETF 100). 
It is useful of course when you are only interested in a single specific meeting or if you want to make some adjustments. 
In our case we used `plot_ietf100.py` to profile `co2eq` to check how to enhance the application, this was especially useful in co2eq-0.0.1 where many search were being performed by searching into a list. `plot_ietf100.profile` represent the output of the profiling.
There are many profiler and we are using cProfiler as it does not require any change to the code. The profile is generated as follows:

```
python3 -m cProfile -o plot_ietf100.profile plot_ietf100.py
```

plot_ietf100.profile is a binary file so to view the output file I am using cprofilev

```bash
pip3 install cprofilev
cprofilev -f plot_ietf100.profile
```

While current processing for an IETF meeting takes an average of 6 minutes, we will be looking to improve this time. 
```bash
time python3 plot_ietf100.py 
real    6m23.401s
user    5m55.853s
sys     0m4.359s

```


`plot_ietf_meetings.py` plots all IETF meetings.



### ICANN related scripts

The ICANN meeting is probably a better and more generic approach to consider.
With ICANN meeting data are not published, and so two steps are needed:

1. Format the data appropriately for `co2eq`
2. Run `co2eq`

The process of formating the data is illustrated by `icann_txt2json.py`. Of course the program in itself is really dependent on the format of the data you have. In our case we were reading the data from a txt file. WHat matters is that at the end for each meeting you are able to generate the list of the attendees of the meeting and store it into a specific file.
Suppose we are formatting the list of attendees for the ICANN 72 meeting. The file storing the list of attendees can be called `icann_72.json` for example - It could also be another name. The file contains a json object that represents the list of attendees and that object has the following format:

```
[
 {
   "country": "JP"
 },
 {
   "country": "JP"
 },
.....
 {
    "country": "UY"
  },
  {
    "country": "VU"
  },
  {
    "country": "ZW"
  }
]
```

The object is a list where each element represents an attendee.
We do not care so much of the name of the attendee and the minimum information is the country of origin. As a result, two participants from the same country are duplicated in the list.
It is recommended to use the alpha2 code for the country, though `co2eq` is able to handle the full name of the country.
Other information may include the organization the attendee belongs to or the type of presence in the meeting - remote or in person.

`plot_icann_meetings.py` details how to run `co2eq` for these meetings. 
In particular it shows how to present for each meeting the necessary information to provide to `co2eq`. 
This includes the name of the meeting, the location and the attendee_list. 
The location is an object that includes the country, the city and iata which corresponds to the IATA city code of that city - or the IATA airport code. 
The IATA code is not mandatory, but when provided, this will be the first to be considered. 
Without IATA codes, `co2eq` will attempt to derive it from the country and city.
While we recommend always specifying the IATA code, it enables us to associate an airport that is not the closest one to the meeting location but that is likely to be the one used by most attendees.
Suppose you have a meeting in a small city (Maastricht) attendee are likely to land in Brussels for example.


```

meeting_list = [
  { 'name' : 'ICANN55',
    'location' : {
      'country' : 'Morocco',
      'city' : 'Marrakesh',
      'iata' : 'RAK' },
    'attendee_list' : './examples/ICANN/doc/json/icann55_RAK.json'
  },
  { 'name' : 'ICANN56',
    'location' : {
      'country' : 'Finland',
      'city' : 'Helsinki',
      'iata' : 'HEL' },
    'attendee_list' : './examples/ICANN/doc/json/icann56_HEL.json'
  },

...

  { 'name' : 'ICANN66',
    'location' : {
      'country' : 'Canada',
      'city' : 'Montreal',
      'iata' : 'YUL' },
    'attendee_list' : './examples/ICANN/doc/json/icann66_YUL.json'
  }
]
```



### Working on data

Once the graphs have been generated, it is often not sufficient, and further analysis require to perform some operation such as computing the mean CO2eq across the meetings for example. 

`meeting_data_manipulation.py` is an attempt to achieve this, but remains largely a work in progress.



### CLI

### co2eq-get-attendee-list

co2-attendee-list is a tool to output the attende-list into an appropriated format for co2eq.
The current `txt` template enables to output json files out of the following files:
These is the format we use to convert files we receive from ICANN.

```
Japan   680
United States of America        372
United Kingdom of Great Britain and Northern Ireland    44
Canada  41
Australia       38
Germany 38
Belgium 29
...
```  
The json attendee list are output as follows:

```
co2eq-get-attendee-list --template txt icann64_KIX.txt 

```

By default the output file is icann64_KIX.json.gz, that is to say the same as the input_file with a different extensions llocated in the same directory.


The IETF attendee list are collected from the IETF website.

```
co2eq-get-attendee-list ietf114 
co2eq-get-attendee-list --template ietf ietf114 
```
By default the output file is ./ietf114.json.gz but you can specify the specific output file as follows:

### co2eq-plot-meeting

The `co2eq-plot-meeting` displays the COeq emissions for the meetings. It enables to plot a single meeting or the CO2 emissions for a serie of meetings.
The package contains the data for IETF and ICANN meeting, that is the package co2eq provided the list of attendees as well as the location associated to each meetings. As a result, these argument do not need to be provided. 

To plot a specific meeting in this example ICANN55:
 
```
co2eq-plot-meeting --output_dir  ./output_test/ --meeting_type ICANN --meeting_name ICANN55
co2eq-plot-meeting --output_dir  ./output_test/ --meeting_name ICANN55
```
This will result in :

```
  output_test
    +- ICANN55 
```

To plot all ICANN meetings:

```
co2eq-plot-meeting --output_dir  ./output_test --meeting_type ICANN 
co2eq-plot-meeting --output_dir  ./output_test --meeting_name ICANN
```

```
  output_test
    +- ICANN 
    +- ICANN55
    +- ...
    +-ICANN76 
```


To generate all our web site

```
co2eq-plot-meeting --output_dir  ./IETF --meeting_type IETF 
co2eq-plot-meeting --output_dir  ./ICANN --meeting_type ICANN
```

As a developper, this is how to update th eco2eq package and generate an additional IETF meeting for example

```
## 1. configure package with new data
## vim co2eq/src/co2eq/data/meeting_list_conf.json.gz
## 2. generates the attendee_list for that IETFXX
cd co2eq/src/co2eq/data/ietf/meeting_attendee_list/json/
co2eq-get-attendee-list ietfXXX 
## 3. update package
cd co2eq/
python3 -m build && pip3 install --force-reinstall  dist/co2eq-0.0.4.tar.gz
## git branch gh-pages
## 4. plot the new graph and generate the web site
co2eq-plot-meeting --output_dir  ./IETF --meeting_type IETF 
``` 

Without updating the package 

```
## 1. generates the attendee_list for that IETFXX
co2eq-get-attendee-list ietfXX
## 2) generates meeting_list_conf.json.gz by adding
## {'name' : 'IETFXX',
##    'location' : {
##      'country' : 'Country',
##      'city' : 'City',
##      'iata' : 'IATA' },
##    'attendee_list' : './ietfXX.json.gz'
##  }
co2eq-plot-meeting --output_dir  ./IETF --meeting_type IETF --meeting_list_conf meeting_list_conf.json.gz 

