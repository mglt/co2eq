from os import listdir
from os.path import isdir

def ietf_banner():
  prefix = 'https://co2eq.gihub.io'
  banner = f"[co2eq]({prefix}/index.html) - [IETF]({prefix}/ietf.html) - [MeetingsList]({prefix}/all_ietf_meetings.html)"

  ## ordergin the files according to the number
  file_dict = {}
  file_list = listdir()
  for f in file_list:
    if isdir( f ) == False:
      continue
    f_list = f.split( '.' )
    name = f_list[ 0 ] 
    ietf_nbr = name[ 4 : ]
    try:
      file_dict[ int( ietf_nbr ) ] = f 
    except:
      continue
  file_list = [ item[1] for item in sorted( file_dict.items(), key=lambda x: x[0] ) ]
  for d in file_list:
    if 'All' in d or 'IETF' not in d:
      continue
    banner += f" - [{d}]({prefix}/{d}/{d.lower()}.html)"
  return banner

ietf_banner()

def ietf_md( ietf_dir ):
  """ create the md page of the ietf_dir meeting """
  svg_dict = { 'co2' : "", 'attendee' : "" }
  for f in listdir( ietf_dir ):
    if 'svg' not  in f:
      continue
    md_text =  f"![]({f})\n"  
    if 'attendee' in f:
      svg_dict[ 'attendee' ] += md_text
    elif 'flight' in f or 'distance' in f :
      svg_dict[ 'co2' ] += md_text
  with open( f"{ietf_dir.lower()}.md", 'wt', encoding='utf8' ) as f:
    f.write( ietf_banner() )
    f.write("\n\n")
    f.write( f"# Data of {ietf_dir}\n\n" ) 
    f.write( f"## $CO_2$ Estimation in for 'flight' and 'distance' mode\n\n" )
    f.write( svg_dict[ 'co2' ] )
    f.write("\n")
    f.write( f"## Number of Attendee 'attendee' mode\n\n" )
    f.write( svg_dict[ 'attendee' ] )
    f.write("\n")


def meeting_list_md( ietf_dir ):
  """ generates the md page associated to All_Meetings"""
  svg_dict = { 'flight' : "", 'distance' : "", 'attendee' : "" }
  for f in listdir( ietf_dir ):
    if 'svg' not  in f:
      continue
    md_text =  f"![]({f})\n"  
    if 'attendee' in f:
      svg_dict[ 'attendee' ] += md_text
    elif 'flight' in f:
      svg_dict[ 'flight' ] += md_text
    elif 'distance' in f:
      svg_dict[ 'distance' ] += md_text
  with open( f"{ietf_dir.lower()}.md", 'wt', encoding='utf8' ) as f:
    f.write( ietf_banner() )
    f.write("\n\n")
    f.write( f"# Data of {ietf_dir}\n\n" ) 
    for mode in [ 'flight' ]:
      f.write( f"## $CO_2$ Estimation in {mode} mode\n\n" )
      f.write( svg_dict[ mode ] )
      f.write("\n")
    f.write( f"## Number of Attendee 'attendee' mode\n\n" )
    f.write( svg_dict[ 'attendee' ] )
    f.write("\n")

def generate_md():
  """ generates all md pages for the IETF meeting """
  for ietf_dir in listdir():
    if 'IETF' not in ietf_dir:
      continue
    if not isdir( ietf_dir ) :
      continue
    if ietf_dir == 'All_IETF_Meetings':
      meeting_list_md( ietf_dir )
    else:
      ietf_md( ietf_dir )

generate_md()
