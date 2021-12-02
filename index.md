# `CO2eq` Overview 

## Overview

Currently, `CO2eq` (Migault 2021) estimates \(CO_2\) equivalent
emissions associated to meetings. The `Meeting` class takes as input a
list of attendees as well as the meeting location. At minimum an
attendee is represented by a location (e.g. country), but can also be
associated other criteria such as organization, type of presence (e.g
on-site, remote, ...). These criteria can be used to cluster attendees
according to the different value of these criteria. Each value can be
associated an amount of \(CO_2\) equivalent emission or the number of
attendees. The `CityDB` class is responsible to associate an airport to
a location.

The \(CO_2\) equivalent emissions of a flight is estimated by a `mode` (
i.e. ’distance’ and ’flight’) and `co2eq` the methodology ( i.e.
’myclimate2018’ (“The myclimate Flight Emission Calculator” 2019) and
’goclimate2018’ (“GO. Climate Neutral: Calculations in the
GoClimateNeutral Flight Footprint API” 2019)). The ’distance’ mode is
solely based on the distance between the city of the meeting and the
city of the attendee. The resulting \(CO_2\) equivalent emitted
corresponds to a direct flight between these two cities – thus ignoring
detours, takeoff and landing operations associated to multi segment
flights. The ’flight’ mode, in return consider a real flight between the
two cities eventually with potentially multiple segments. The `FlightDB`
class returns such flight by requesting the Amadeus ’Flight Offer
Search’ API (“Amadeus for Developpers: Flight Offers Search” 2019)
that returns all available matching flights. The
`AmadeusOffersSearchResponse` class is responsible to parse that
response and select a plausible flight. The `Flight` class estimates the
\(CO_2\) equivalent of the flight by considering each segment as
individual flight. `CO2eq-v0.0.1` implements two methodologies to
compute the \(CO_2\) equivalent, ’myclimate2018’ and ’goclimate2018’ –
as detailed in Section [2](#sec:co2eq) . `Flight` directly implements
the ’myclimate2018’ methodology while ’goclimate’ is implemented by
requesting a GO Climate Neutral service.

In addition to the computation of \(CO_2\) for a single meeting, the
class `MeetingList` visualizes the evolution of \(CO_2\) equivalent
emission across various meetings. The `IETFMeeting` and
`IETFMeetingList` classes extend the `Meeting` and `MeetingList`
classes, mostly to retrieve, parse and cleanup of the attendee list from
the IETF web site. An IETF attendee is represents as a dictionary with
the following keys: ’organization’, ’presence’, ’country’. An additional
element ’flight\_segments’ that indicates the number of segments
associated to flight is computed on the fly. Attendees can be
partitioned according to these keys, and for each possible value, it is
possible to estimate the number of attendee or the \(CO_2\) equivalent
emission. The `IETFMeetingList` class - as opposed to taking a list of
Meeting objects - takes the list of all IETF meetings – set as an global
variable –, and instantiates IETFMeeting objects when these meetings
have not been created. In addition, it performs the necessary adjustment
(size, title, labels, ...) to plot a relevant figure.
Figure [\[fig:ietf100\]](#fig:ietf100) provides an example of the
estimation provided by `CO2eq` for a single meeting. For more example of
estimation provided for a list of meetings, please see
section [4](#sec:ietf).

## Design and Performance 

`CO2eq` is implemented in Python 3.8 as execution time was not
especially crucial. We briefly evaluate the performances using
cProfiler (“The Python Profilers” 2019) as it does not require any
changes to the code and estimate \(CO_2\) for the IETF 100 with all
necessary information being cached. As represented in
Figure [1](#fig:cprofiler), the total computation takes 523.941 seconds
with 464.239 seconds associated to the ourairports module and 35 seconds
associated to the read\_all function of jcache module involved by the
`CityBD` class. We suspect the `OurAirports` class ourairports modules
performs search within a list and this for any airports of any segments.
A `AirportDB` class should inherit from `OurAirports` and implement
dictionary search. Currently `CityDB` is still using a list of IATA
cities, but we also expect this class to undergo some major function
re-design – see section [3.3](#sec:evolution).

![Profiling the computation of IETF 100 with
cProfiler<span label="fig:cprofiler"></span>](./fig/profile-crop.pdf)

We have not performed an extended analysis over `CO2eq`, as performance
is not the primary purpose. However, we have favored the use of
dictionaries over lists to speedup search. The drawback is that list
enables search using multiple search entries while dictionaries have a
single entry key. This is especially true for flight offers that are
retrieved using multiple parameters such as origin, destination, dates,
classes. In order to provide some sort of flexibility for the search, we
used primary keys - in our case origin, destination - which refers to a
list of possible keys as to reduce the size of the list. We also limit
the size of the cached objects, and only the latest resulting flight and
input parameters are cached. In case the primary key match but not the
secondary parameters match the cached object a new search is performed.
The search firstly look whether a new flight can be derived from the
list of offers stored in a file origin-destination.tar.gz. If the file
cannot be found or the flight offers present in the file does not match
the criteria, a new request is sent to the Amadeus ’Flight Offer Search’
service. The flight response is derived, cached and the additional
offers are placed to the origin-destination.tar.gz.


# Flight \(CO_2\) Emission Estimation 

This section details the methodology used by `CO2eq` to estimate flight
\(CO_2\) equivalent emission, and their respective implementation –
namely ’myclimate2018’ (“The myclimate Flight Emission Calculator” 2019)
and ’goclimate’ (“GO. Climate Neutral: Calculations in the
GoClimateNeutral Flight Footprint API” 2019). Both start estimating the
\(CO_2\) equivalent emission associated to a flight, and then associate
a proportion of it to each passenger.

## Estimation of flight \(CO_2\) equivalent

Most \(CO_2\) equivalent emission during a flight (\(E_{flight}\)) is
associated to the combustion of the fuel whose quantity depends on the
category of aircraft, the flying distance as well as the different
phases of the flight. Flights are usually decoupled into short haul and
long haul aircraft with distinct consumption patterns. The different
phases of a flight can be described as Landing and Take Off (LTO) or
Climb Cruise Descent (CCD). The EMEP/EEA air pollutant emission
inventory guidebook (Winther et al. 2019c, 2019b, 2019a) provides for
each type of aircraft the quantity of fuel burnt during LTO and CCD – as
well as the quantities of pollutant emitted on each phase. To estimate
the average consumed fuel per flying km – across all acceptable aircraft
–, ICAODATA provides the total distance flown by each aircraft (as well
as the fuel consumption). This enables to derive a weighted average fuel
consumption as a function of the flying distance \(Fuel( d )\) in kg –
with \(d\) the flying distance in km. Note that \(Fuel\) includes LTO.

The \(CO_2\) resulting from the combustion for 1 kg of fuel is
\(e_{CO_2}\) = 3.15 kg / kg of burnt fuel. The impact of other
non-\(CO_2\) pollutant affecting the earth radiative balance - such as
nitrogen oxide (\(NO_x\)) are estimated through a Radiative Forcing
Index (\(RFI\)) factor over the emission of \(CO_2\) and (Jungbluth and
Meili 2019) recommends to use \(RFI\) = 2. Note that the factor measures
the effect of \(NO_x\) and not the quantity. In fact \(NO_x\) and
\(CO_2\) have significant differences and in particular act on different
time scales. Outside of fuel combustion \(CO_2\), one needs to consider
indirect source of emission that is the \(CO_2\) emission associated to
fuel PreProcessing (\(PP\)) which is set to 0.54 kg / kg of burnt fuel.

The flying distance between two airports considers the round shape of
the earth – using the Great Circle Distance – as well as some extra
Distance Correction (\(DC\)) due to inefficiency of the traffic control,
weather conditions, holding patterns.

As a result \(CO_2\) equivalent emission for a given flying distance
\(x = d + DC\) with \(d\) the distance between the two airports can be
expressed as:
\[E_{flight} ( x )  = Fuel(x) \times ( e_{CO_2}. RFI + PP )\]

## \(CO_2\) equivalent per passenger

The \(CO_2\) emission per passenger \(E_{flyer}\) is estimated from
\(E_{flight}\) by considering the fraction of the load associated to the
passenger, that is \(1 - CARGO_{ld}\) with \(CARGO_{ld}\) representing
the cargo load. This fraction of emission is shared between the
effective passengers weighted by the cabin class \(W_{cabin}\) which is
equivalent as occupying a certain number of economy seats. The effective
number of passengers is determined by the total capacity in term of
seats \(SEAT_{T}\) – which depends on the aircraft type an can be found
in ICAODATA – multiplied by the load passenger factor \(PSG_{ld}\)
published by ICAO.

As passenger and cargo are used to drive the demand for the construction
of an airport or a plane, these are expressed on a per passenger basis.
The aircraft life cycle is expressed as (\(AIRCRAFT_{lc}\)) is per
passenger / per flying km and the infrastructures are modeled by a
constant (\(INFRA\)) (Messmer and Frischknecht 2016)(Spielmann et al.
2007).

As a result, the emission per passenger are expressed as:
\[\begin{aligned}
E_{flyer} (x)  = & E_{flight}(x) ( 1 - CARGO_{ld} ) \frac{ W_{cabin} }{ SEAT_{T} \times PSG_{ld} } \\
                 & + AIRCRAFT_{lc}. x + INFRA
\end{aligned}\]

##  ’myclimate’ versus ’goclimate’

This section compares ’goclimate2019’ (“GO. Climate Neutral:
Calculations in the GoClimateNeutral Flight Footprint API” 2019) as
published on 2019-04-08 with ’myclimate2019’ (“The myclimate Flight
Emission Calculator” 2019) computation as published in 2019-08-13.
`CO2eq` implements ’myclimate2019’, but rely on the service provided by
GO Climate. As ’goclimate2019’ references to the latests version of
’myclimate’ - in our case ’myclimate2019’, we assume that the service
synchronizes its principles with the latest version of published by
’myclimate’.

The ’myclimate’ and ’goclimate’ methodologies mostly differ in the
estimation of the distance correction (\(DC\)) and the cargo load
(\(CARGO_{ld}\)). ’myclimate’ considers a constant value for \(DC\) = 95
km, while ’goclimate’ respectively sets \(DC\) to 50 km, 100 km and 125
km for flying distance respectively lower than 550 km, lower 5500 km and
greater than 5500 km. In the case of the IETF where a significant number
of flights are transcontinental \(DC\) is increased between 5% and 31%.
This is likely to increase the flying distance used by ’goclimate’ and
so the \(CO_2\) equivalent emissions. In addition, ’myclimate’ estimates
the cargo load (\(CARGO_{ld}\)) on a mass basis which is respectively
93% for short haul and 74% for long haul. On the other hand, ’goclimate’
estimates the cargo load on a monetary basis to \(CARGO_{ld}=95.1\%\).
While ’goclimate’ and ’myclimate’ use ICAO as the source of information
for the average number of seats and the passenger load (\(PSG_{ld}\)),
’goclimate’ uses respectively ICAODATA (“ICAO DATA+” 2021) 2012 and
ICAO (“ICAO Economic Development: Air Transport Monitor” 2021) 2012
while ’myclimate’ respectively uses ICAODATA 2019 and ICAO 2018. More
considerations may be needed to check if this presents an impact.


# Application

* [IETF](./IETF/ietf.html)



<div id="refs" class="references">

<div id="ref-airportandcitysearch">

“Amadeus for Developpers: Airport & City Search.” 2019.
<https://developers.amadeus.com/self-service/category/air/api-doc/airport-and-city-search>.

</div>

<div id="ref-flightsearchoffer">

“Amadeus for Developpers: Flight Offers Search.” 2019.
<https://developers.amadeus.com/self-service/category/air/api-doc/flight-offers-search>.

</div>

<div id="ref-ghgp">

Barrow, Martin, Benedict Buckley, Tom Caldicott, Tom Cumberlege, John
Hsu, Scott Kaufman, Kevin Ramm, et al. 2013. “Technical Guidance for
Calculating Scope 3 Emissions.” World Resources Institute with
GreenHouse Gas Protocol (GHG) Protocol; Carbon Trust.
<https://ghgprotocol.org/sites/default/files/standards/Scope3_Calculation_Guidance_0.pdf>.

</div>

<div id="ref-10.1145/3401335.3401711">

Bergmark, Pernilla, Vlad C. Coroamă, Mattias Höjer, and Craig Donovan.
2020. “A Methodology for Assessing the Environmental Effects Induced by
Ict Services: Part Ii: Multiple Services and Companies.” In *Proceedings
of the 7th International Conference on Ict for Sustainability*, 46–55.
ICT4S2020. New York, NY, USA: Association for Computing Machinery.
<https://doi.org/10.1145/3401335.3401711>.

</div>

<div id="ref-c4c">

“"CARING FOR CLIMATE: THE BUSINESS LEADERSHIP PLATFORM” A Statement by
the Business Leaders of the Caring for Climate Initiative.” 2021.
<https://d306pr3pise04h.cloudfront.net/docs/publications%2FC4C_Statement.pdf>.

</div>

<div id="ref-countryinfo">

Chandro, Porimol, Kasper Sørensen, Muhammad Arslan, and Jannik J. 2021.
“CountryInfo: A python module for returning data about countries, ISO
info and states/provinces within them.”
<https://pypi.org/project/countryinfo/>.

</div>

<div id="ref-ar6-wg1">

“Climate Change 2021: The Physical Science Basis, Working Group I
contribution to the Sixth Assessment Report AR6-WG1.” 2021. The
Intergovernmental Panel on Climate Change (IPCC).
<https://www.ipcc.ch/report/sixth-assessment-report-working-group-i/>.

</div>

<div id="ref-eia">

“COMMERCIAL BUILDINGS ENERGY CONSUMPTION SURVEY (CBECS).” 2021. US
Energy Information Administration (EIA).
<https://www.eia.gov/consumption/commercial/>.

</div>

<div id="ref-10.1145/3401335.3401716">

Coroamă, Vlad C., Pernilla Bergmark, Mattias Höjer, and Jens Malmodin.
2020. “A Methodology for Assessing the Environmental Effects Induced by
Ict Services: Part I: Single Services.” In *Proceedings of the 7th
International Conference on Ict for Sustainability*, 36–45. ICT4S2020.
New York, NY, USA: Association for Computing Machinery.
<https://doi.org/10.1145/3401335.3401716>.

</div>

<div id="ref-ipbes-2020">

Daszak, P., C. G. Amuasi J.and das Neves, D. Hayman, T. Kuiken, B.
Roche, C. Zambrana-Torrelio, P. Buss, et al. 2020. “IPBES WORKSHOP ON
BIODIVERSITY AND PANDEMICS.” United Nations Educational, Scientific;
Cultural Organization (UNESCO); Intergovernmental Science-Policy
Platform on Biodiversity; Ecosystem Services (IPBES).
<https://ipbes.net/sites/default/files/2020-12/IPBES%20Workshop%20on%20Biodiversity%20and%20Pandemics%20Report_0.pdf>.

</div>

<div id="ref-eri-sustainability">

“Ericsson Sustainability research.” 2021. Ericsson.
<https://www.ericsson.com/en/about-us/sustainability-and-corporate-responsibility/sustainability-metrics/sustainability-research>.

</div>

<div id="ref-gcp-2021">

Friedlingstein, P., M. W. Jones, M. O’Sullivan, R. M. Andrew, D. C. E.
Bakker, J. Hauck, C. Le Quéré, et al. 2021a. “Data supplement to the
Global Carbon Budget 2021.” Integrated Carbon Observation System (ICOS).
<https://doi.org/10.18160/gcp-2021>.

</div>

<div id="ref-essd-2021-386">

———. 2021b. “Global Carbon Budget 2021.” *Earth System Science Data
Discussions* 2021: 1–191. <https://doi.org/10.5194/essd-2021-386>.

</div>

<div id="ref-goclimate">

“GO. Climate Neutral: Calculations in the GoClimateNeutral Flight
Footprint API.” 2019. GO Climate Neutral.
<https://api.goclimateneutral.org/docs>.

</div>

<div id="ref-epa">

“Greenhouse Gas Inventory Guidance Indirect Emissions from Events and
Conferences).” 2018. US Environmental Protection Agency (EPA).
<https://www.epa.gov/climateleadership>.

</div>

<div id="ref-cop26">

Guterres, António. 2021. “Secretary-General’s Statement on the
Conclusion of the UN Climate Change Conference COP26.” United Nations
Climate Change.
<https://unfccc.int/news/secretary-general-s-statement-on-the-conclusion-of-the-un-climate-change-conference-cop26>.

</div>

<div id="ref-iso-3166">

Hyojun, Kang. 2021. “ISO 3361-1 Country code package for Python.”
<https://pypi.org/project/iso-3166-1/>.

</div>

<div id="ref-icao">

“ICAO Carbon Emissions Calculator Methodology.” 2018. International
Civil Aviation Organization (ICAO).

</div>

<div id="ref-icaodata">

“ICAO DATA+.” 2021. International Civil Aviation Organization (ICAO).
<https://data.icao.int/newDataPlus/Tools>.

</div>

<div id="ref-icaoeco">

“ICAO Economic Development: Air Transport Monitor.” 2021. International
Civil Aviation Organization (ICAO).
<https://www.icao.int/sustainability/Pages/Air-Traffic-Monitor.aspx>.

</div>

<div id="ref-ietf">

“Internet Engineering Task Force (IETF).” n.d. <https://www.ietf.org>.

</div>

<div id="ref-rfi">

Jungbluth, Niels, and Christoph Meili. 2019. “Recommendations for
calculation of the global warming potential of aviation including the
radiative forcing index.” The International Journal of Life Cycle
Assessment.
<https://www.researchgate.net/publication/329051755_Recommendations_for_calculation_of_the_global_warming_potential_of_aviation_including_the_radiative_forcing_index>.

</div>

<div id="ref-aviation-2021">

Klöwer, M, M R Allen, D S Lee, S R Proud, L Gallagher, and A Skowron.
2021. “Quantifying Aviation’s Contribution to Global Warming” 16 (10):
104027. <https://doi.org/10.1088/1748-9326/ac286e>.

</div>

<div id="ref-lc">

Messmer, Annika, and Rolf Frischknecht. 2016. “Life Cycle Inventories of
Air Transport Services.” treeze fair life cycle thinking.
<https://www.researchgate.net/publication/312196655_LCA_of_air_transport_services/link/5875d43608ae6eb871ca6cb7/download>.

</div>

<div id="ref-co2eq">

Migault, Daniel. 2021. “Compute \(CO_2\) equivalent emissions.”
<https://github.com/mglt/co2eq>.

</div>

<div id="ref-owid-aviation">

Ritchie, Hannah. 2020. “Climate change and flying: what share of global
\(CO_2\) emissions come from aviation?” October.
<https://ourworldindata.org/co2-emissions-from-aviation>.

</div>

<div id="ref-owidco2andothergreenhousegasemissions">

Ritchie, Hannah, and Max Roser. 2020. *Our World in Data*.
<https://ourworldindata.org/co2-and-other-greenhouse-gas-emissions>.

</div>

<div id="ref-ecoinvent">

Spielmann, Michael, Christian Bauer, Roberto Dones, Paul Scherrer, and
Matthias Tuchschmid. 2007. “Transport Services.” Ecoinvent Center.
<https://db.ecoinvent.org/reports/14_Transport.pdf>.

</div>

<div id="ref-ghgp-online">

“The GHG Emissions Calculation Tool.” 2021. GreenHouse Gas Protoco (GHG
Protocol)l. <https://ghgprotocol.org/ghg-emissions-calculation-tool>.

</div>

<div id="ref-myclimate">

“The myclimate Flight Emission Calculator.” 2019. Foundation myclimate.
[www.myclimate.org](www.myclimate.org).

</div>

<div id="ref-cprofiler">

“The Python Profilers.” 2019.
<https://docs.python.org/3/library/profile.html>.

</div>

<div id="ref-ungc">

“United Nations Global Compact.” 2021.
<https://www.unglobalcompact.org/>.

</div>

<div id="ref-climateclock">

Usher, David, and Damon Matthews. 2021. “The climate Clock.” Concordia
University. <https://climateclock.net/>.

</div>

<div id="ref-eeaaviation3">

Winther, Morten, Kristin Rypdal, Lene Sørensen, Manfred Kalivoda, Monica
Bukovnik, Niels Kilde, Riccardo De Lauretis, et al. 2019a. “1.A.3.a
Aviation 1 Master emissions calculator 2019.” EEA Report No 13/2019.
European Environment Agency (EEA) / European Monitoring; Evaluation
Programme (EMEP). <https://www.eea.europa.eu/ds_resolveuid/WFM2I9GHX8>.

</div>

<div id="ref-eeaaviation2">

———. 2019b. “1.A.3.a Aviation 2 LTO emissions calculator 2019.” EEA
Report No 13/2019. European Environment Agency (EEA) / European
Monitoring; Evaluation Programme (EMEP).
<https://www.eea.europa.eu/ds_resolveuid/VO7PBDEIY8>.

</div>

<div id="ref-eeaaviation1">

———. 2019c. “EMEP/EEA air pollutant emission inventory guidebook 2019:
Aviation.” EEA Report No 13/2019. European Environment Agency (EEA) /
European Monitoring; Evaluation Programme (EMEP).
<https://www.eea.europa.eu/ds_resolveuid/SEB4A9UJYD>.

</div>

</div>

