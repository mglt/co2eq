
# Estimating Air Flight Emissions with *CO2eq*


  <html>
  <style>
  table, th, td {
    border: 0px none;
    padding: 0px;
  }
  </style>
  <body>
    <table style="width:100%">
          <tr>
<td><a href='https://mglt.github.io/co2eq/IETF/IETF'> CO2eq data for IETF</a></td>
<td><a href='https://mglt.github.io/co2eq/ICANN/ICANN'> CO2eq data for ICANN</a></td>
<td> </td>
<td> </td>
<td> </td>
<td> </td>
      </tr>
    </table>
  </body>
  </html>

* TOC
{:toc}

## I. *CO2eq* Overview

The IPCC Working Group I contribution to the Sixth Assessment Report AR6-WG1 [ [1](#ar6-wg1) ] urged every sectors to reduce its CO2 emissions to keep the target of 1.5 C. 
While we are currently on track to a 2.4 C increase of temperature, the 1.5 C remains possible to reach. 

[*co2eq*](https://github.com/mglt/co2eq) estimates the CO2 equivalent (CO2eq) emission associated to international meetings where hundreds of persons are flying from all around the world to meet at one given location. 
The CO2eq depends on the flying distance as well as the number of flight segments and these parameters are retrieved  by `co2eq` via the [Amadeus API](https://developers.amadeus.com/get-started/get-started-with-amadeus-apis-334). The corresponding CO2eq is then estimated for each leg using different methodologies such as [myclimate](https://www.myclimate.org/), the one provided by the UK government or the online service proposed by [GoClimate](https://www.goclimate.com/).
 
The CO2 emissions are estimated using two modes: the *distance* and the *flight* modes. 
The *distance* mode considers a single and direct flight from the location of the meeting attendee to the meeting. This estimation is largely underestimated and as such only informative. 
The *flight* mode, on the other hand, considers a real flight that may be composed of multiple segments.  
For each mode, the CO2 emission associated to each leg is computed using *myclimate2018* [ [2](#myclimate) ], *goclimate2018* [ [3](#goclimate) ] and *2021 Government Greenhouse Gas Conversion Factors for Company Reporting*  [ [4](#ukgov) ]. 

*CO2eq* has been experimented for:

*  Internet Engineering Task Force ([IETF](https://www.ietf.org)) with *CO2eq* [data and results](https://mglt.github.io/co2eq/IETF/IETF) available online as well as an analysis [ [5](#coe2eq-aid) ]. 
* Internet Corporation for Assigned Names and Numbers ([ICANN ](https://www.icann.org/)) with *CO2eq* [data and results](https://mglt.github.io/co2eq/ICANN/ICANN).

## II Conclusion for IETF meetings

The recommendations from *CO2eq* [measurements](https://mglt.github.io/co2eq/IETF/IETF) and associated analysis [ [5](#coe2eq-aid) ] are:

1. The IETF should limit the frequency of its meeting to 1 per year.
2. The IETT should consider corporate sustainability by adhering to the [caring for climate initiative](https://d306pr3pise04h.cloudfront.net/docs/publications%2FC4C_Statement.pdf) led by the Global Compact, UN Environment Program (UNEP) and the secretariat of the UN Framework Convention on Climate Change (UNFCCC). 

[ [4](#coe2eq-aid) ] shows the amount of CO2 emission for an IETFer attending 3 'on-site' meetings per year corresponds to the average CO2 per capita emitted by European countries producing energy based on coal such as Germany or Poland. The amount of CO2 emission for IETFers  attending 2 IETF meetings a year corresponds to the average CO2 per capita emitted by European countries such as UK, Greece or Italy, and the attendance to a single IETF meeting per year corresponds to the CO2 per capita of countries like Venezuela  or Mauritius. It is unsure there are substantial justifications for the IETF to contribute to that extend to the world wide CO2 emissions and the limiting  IETF 'on-site' meeting to at most 1 per year should be considered.  

The same limit of 1 meeting per year is also the one found when considering the Paris agreement that required a 45% decrease, as well as a more recent studies evaluating the evolution of aviation in the next coming years. More specifically, 3 IETF meeting a year match evolution to the air traffic that would result in aviation being responsible to increase the temperature between 0.09 C and 0.1 C. 2 IETF (resp. 1 IETF) meetings a year match scenario where aviation would be responsible to increase the temperature of 0.06 C (resp. 0.04 C).

The IETF has already demonstrated that remote meetings are entirely feasible during the COVID-19 pandemic. Such effort should continue outside the pandemic.


That experimentation of 'remote' meeting came so late and in a forced way may highlight that more effort on corporate sustainability to ensure IETF operates in ways that, at a minimum, meet fundamental responsibilities. For example, the [United Nations Global Compact](https://www.unglobalcompact.org) set 10 principles to address corporate sustainability in a broad sense, and only principles 7-9 are related to the environment. Adherence to such program ensures these principles are part of the IETF strategy and culture with the publication of Communication on Progress. 

More specifically related to CO2 emissions, the IETF should consider adhering to the [caring for climate initiative](https://d306pr3pise04h.cloudfront.net/docs/publications%2FC4C_Statement.pdf) led by the Global Compact, UN Environment Program (UNEP) and the secretariat of the UN Framework Convention on Climate Change (UNFCCC). 

## III. References

<div id="ar6-wg1"></div>
* [1] “Climate Change 2021: The Physical Science Basis, Working Group I contribution to the Sixth Assessment Report AR6-WG1.” 2021. The Intergovernmental Panel on Climate Change (IPCC). [https://www.ipcc.ch/report/sixth-assessment-report-working-group-i/](https://www.ipcc.ch/report/sixth-assessment-report-working-group-i).
<div id="myclimate"></div>
* [2] “The myclimate Flight Emission Calculator.” 2019. Foundation myclimate. [https://www.myclimate.org](https://www.myclimate.org).
<div id="goclimate"></div> 
* [3] “GO. Climate Neutral: Calculations in the GoClimateNeutral Flight Footprint API” 2019) [https://api.goclimateneutral.org/docs](https://api.goclimateneutral.org/docs).
<div id="ukgov"></div> 
* [4] “2021 Government Greenhouse Gas Conversion Factors for Company Reporting” 2021) [PDF]( https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1049346/2021-ghg-conversion-factors-methodology.pdf), [WEB](https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2021).
<div id="coe2eq-aid"> </div>
* [5]  Daniel Migault *CO2eq*: "Estimating Meetings' Air Flight CO2 Equivalent Emissions - An Illustrative Example with IETF meetings", Show me the numbers: Workshop on Analyzing IETF Data (AID), 2021. [https://arxiv.org/pdf/2212.03172](https://arxiv.org/pdf/2212.03172). 


## IV. Publications

* Estimating Air Flight Emissions with CO2eq, IETF 113 Stay Home Meet Occasionally Online (shmoo) 25/03/2022 [slides](https://datatracker.ietf.org/meeting/113/materials/slides-113-shmoo-air-flight-co-2-emissions-associated-to-ietf-meetings-00), [video](https://www.youtube.com/watch?v=JnnPIBmSD28)
* Air Flight CO2 Emissions associated to in-person IETF meetings, IETF113 Hot RFC Lightning Talks, 20/03/2022 [slides](https://datatracker.ietf.org/meeting/113/materials/slides-113-hotrfc-sessa-migault-00), [video](https://www.youtube.com/watch?v=rt-2H_AAucc)
* Daniel Migault *CO2eq*: "Estimating Meetings' Air Flight CO2 Equivalent Emissions - An Illustrative Example with IETF meetings", Show me the numbers: Workshop on Analyzing IETF Data (AID), 2021. [https://www.iab.org/wp-content/IAB-uploads/2021/11/Migault.pdf](https://www.iab.org/wp-content/IAB-uploads/2021/11/Migault.pdf).