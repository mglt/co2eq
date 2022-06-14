from co2eq.ietf_meeting import IETFMeetingList

## configuration parameters are stored in .env


## building a meeting serie 
ietf_meeting_list = IETFMeetingList( ) 

## building all graphs
ietf_meeting_list.plot_all()

## building web pages in md format
  ## url is the URL under which you have:
  ## * IETF or ALL with figures for all IETFs
  ## * IETF72, IETF73... each individual IETF meetings
  ## Jekyll local installation uses 'http://127.0.0.1:4000/IETF/' as the base URL
  ## gh-pages uses https://mglt.github.io/co2eq/IETF
  ## the leap theme seems to be the only one that generates a TOC
#ietf_meeting_list.www_md( 'http://127.0.0.1:4000/IETF/', toc=False, home_url='http://127.0.0.1:4000/')
#ietf_meeting_list.www_md( 'https://mglt.github.io/co2eq/IETF/', toc=False, home_url='https://mglt.github.io/co2eq' )

