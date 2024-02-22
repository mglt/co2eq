import os.path
import pickle
import pandas as pd
pd.options.plotting.backend = "plotly"
import plotly.express as px
import matplotlib.pyplot as plt
import kaleido ## to be able to export
import roman
import math

import co2eq.meeting2

class MeetingList( co2eq.meeting2.Meeting ): 

  def __init__( self, name:str, 
                  meeting_list=None,\
                  conf=co2eq.conf.Conf().CONF, 
                  base_output_dir=None,
                  airportDB=True, 
                  cityDB=True, 
                  flightDB=True,
                  goclimateDB=True ):

    """ instantiates a MeetingList object 

    Args: 
      meeting_list (list): a list of meeting dictionary
        { 'name' : meeting_name, 
          'location' : { 
            'country' : meeting_country, 
            'city' : meeting_city,
            'iata' : the meeting iata_airport # especially useful when city has a small airport
           }                                  # and we prefer to select a larger airport      
        }
        meeting_list could also be a list of Meeting objects, but this use is not the prefrred way.
    """

    self.name = name
    self.conf = conf
    self.init_DB( airportDB, cityDB, flightDB, goclimateDB )
    self.init_output_dir( base_output_dir )
    self.json_meeting_list = meeting_list
    self.init_meeting_list()
    self.df_data = {}
    self.info = {}
    self.fig_height=600
    self.fig_width=1500
    ## URL underwhich we have:
    ## self.meeting_list_url=
    ##   meeting_list.name
    ##     meeting.name
    ##     ...
    ##     meeting.name
    self.meeting_list_url="http://127.0.0.1:4000/"
    ## The home URL to the web site
    self.home_url=self.meeting_list_url
    self.banner_col=10

  def init_meeting_list( self, mode_list=[ 'attendee', 'flight'], cabine_list=[ 'AVERAGE' ] ):
    self.meeting_list = []
    self.cluster_key_list = None 
    self.co2eq_method_list = None
    for json_meeting in self.json_meeting_list:
      m_name = json_meeting[ 'name' ]  
      m_loc = json_meeting[ 'location' ] 
#      pickle_file = os.path.join( self.output_dir, f"{m_name}.pickle" )
#      if os.path.isfile( pickle_file ) :
#        meeting = pickle.load( pickle_file )
#      else:

#      m_base_output_dir = os.path.join( self.output_dir, m_name )  
      m_base_output_dir = self.output_dir
      meeting = co2eq.meeting2.Meeting( 
              m_name, m_loc,  self.conf, \
              attendee_list=json_meeting[ 'attendee_list' ], 
              base_output_dir=m_base_output_dir, \
              airportDB=self.airportDB, 
              cityDB=self.cityDB, 
              flightDB=self.flightDB, 
              goclimateDB=self.goclimateDB )
#      meeting.plot_distribution( mode_list=mode_list, cabine_list=cabin_list )
#      meeting.md( mode_list=mode_list, cabine_list=cabin_list, banner="", toc=True )
      if self.cluster_key_list is None:
        self.cluster_key_list = meeting.cluster_key_list
      else:
        for cluster_key in meeting.cluster_key_list:
          if cluster_key not in self.cluster_key_list:
            self.cluster_key_list.append( cluster_key )
      if self.co2eq_method_list is None:
        self.co2eq_method_list = meeting.co2eq_method_list
      else:
        for co2eq_method in meeting.co2eq_method_list:
          if co2eq_method not in self.co2eq_method_list:
            self.co2eq_method_list.append( co2eq_method )
      self.meeting_list.append( meeting )

  def build_data( self, mode='flight', cabin=None):

    ## return the df in cache is present
    if ( mode, cabin )  in self.df_data.keys():
      return self.df_data[ ( mode, cabin ) ]

    df_list = []
    for meeting in self.meeting_list:
      m_df = meeting.build_data( mode=mode, cabin=cabin )
      m_df.insert( 0, 'meeting', f"{meeting.name} - {meeting.meeting_iata_city}"  )
      m_df = df_list.append( m_df )
    df = pd.concat( df_list, ignore_index=True, sort=False)
    self.df_data[ ( mode, cabin ) ] =  df
    return df


  def plot_co2eq_distribution( self, mode='flight', cabin='AVERAGE', on_site=None, show=False, print_grid=False):

    df = self.build_data( mode=mode, cabin=cabin )
    print( f"df: {df}" )
    print( f"df.columns: {df.columns}" )
    print( f"df.head: {df.head}" )

    if on_site not in [ True, False, None ]:
      raise ValueError( f"Unknown value {on_site} for on_site.\
        Expecting True, False or None" )
    if 'presence' not in df.columns and on_site is not None:
      raise ValueError( f"on_site is specified to {on_site} but "\
        f"'presence' is not specified in the data frame.\n"\
        f"{df.info}\ndf.columns: {df.columns}" )
 
    cluster_key_list = self.cluster_key_list[ : ]
    cluster_key_list.remove( 'co2eq' )
    agg_dict = {}
    for co2eq_method in self.co2eq_method_list :
      agg_dict[ co2eq_method ] = 'sum'

    for cluster_key in cluster_key_list :
      if cluster_key in [ 'presence' ] :
        sub_df = df.groupby( by=[ 'meeting', cluster_key, ], sort=True ).agg( agg_dict ).reset_index().sort_values(by='myclimate', ascending=False )
      ## for other cluster_key we only focus on the CO2 associated to 
      ## on-site participants'
      else:
        if on_site is True:
          sub_df = df[ df.presence == 'on-site' ].groupby( by=[ 'meeting', cluster_key, ], sort=True ).agg( agg_dict ).reset_index().sort_values(by='myclimate', ascending=False )
        elif on_site is False:
          sub_df = df[ df.presence != 'on-site' ].groupby( by=[ 'meeting', cluster_key, ], sort=True ).agg( agg_dict ).reset_index().sort_values(by='myclimate', ascending=False )
        elif on_site is None:
          sub_df = df.groupby( by=[ 'meeting', cluster_key, ], sort=True ).agg( agg_dict ).reset_index().sort_values(by='myclimate', ascending=False )
#      sub_df = sub_df.set_index( cluster_key ).transpose()
      print( f"sub_df: {sub_df}" )
      print( f"sub_df.columns: {sub_df.columns}" )
      print( f"sub_df.head: {sub_df.head}" )
      subfig_list = []
      subfig_title_list = []
      for co2eq_method in self.co2eq_method_list:
        method_df = sub_df.pivot( index='meeting', columns=cluster_key, values=co2eq_method )
        print( f"method_df: {method_df}" )
        print( f"method_df.columns: {method_df.columns}" )
        print( f"method_df.head: {method_df.head}" )
       
#        subfig = px.bar(sub_df, x=sub_df.index,  y=sub_df.columns,
        subfig_title = f"Estimated with {co2eq_method}"
        subfig = px.bar( method_df, x=method_df.index,  y=method_df.columns,
                  ##color=d.index.name,\
                  # text=d.index.name, 
                  title=subfig_title, 
                  ## labels are displayed when mouse is hand over the value.
                  labels={ 'value': "CO2eq (Kg)", 'index': "Meetings" },
                )
#        subfig.update_xaxes(tickangle=90)
        print( f"subfig: {subfig}" )
##        raise ValueError
        subfig_list.append( subfig )
        subfig_title_list.append( subfig_title ) 
      suffix = 'distribution'
      if on_site is True:
        title = f"CO2eq Distribution for On-Site Participants (Effective CO2eq)"
      elif on_site is False:
        title = f"CO2eq Distribution for Remote Participants (~Offset CO2eq)"
      elif on_site is None:
        title = f"CO2eq Distribution for ALL Participants (On-Site and Remote)"
      html_file_name = self.image_file_name( suffix, 'html', mode, cabin=cabin,
              cluster_key=cluster_key, on_site=on_site )
      svg_file_name=self.image_file_name( suffix, 'svg', mode, cabin=cabin,
              cluster_key=cluster_key, on_site=on_site )
      
      fig = co2eq.fig.OneRowSubfig( \
        subfig_list,
#        subfig_title_list=subfig_title_list, ## we shoudl be able to read the title from the figure.
        fig_title=title,
        fig_width=self.fig_width,
        fig_height=self.fig_height,
        print_grid=print_grid,
        show=show,
        shared_xaxes=False,
        shared_yaxes=False,
        legend_offset=0,
        horizontal_spacing=0.3,
        html_file_name=html_file_name,
        svg_file_name=svg_file_name )
#      fig.fig.show()

  def plot_attendee_distribution( self, on_site=None, show=False, print_grid=False ):


    df = self.build_data( mode='attendee' )
    if on_site not in [ True, False, None ]:
      raise ValueError( f"Unknown value {on_site} for on_site.\
        Expecting True, False or None" )
    if 'presence' not in df.columns and on_site is not None:
      raise ValueError( f"on_site is specified to {on_site} but "\
        f"'presence' is not specified in the data frame.\n"\
        f"{df.info}\ndf.columns: {df.columns}" )
    cluster_key_list = self.cluster_key_list[ : ]
    cluster_key_list.remove( 'co2eq' )
    subfig_list = []
    agg_dict = { 'count' : 'sum' }
##      agg_dict[ 'count' ] = 'sum'

    for cluster_key in cluster_key_list :
      ## with cluster_key set to presence, we plot the number
      ## of attendees. 
      ## associated to the presence, which includes remote,
      ## not arrived and on-site
#      agg( agg_dict ).reset_index()

      if cluster_key in [ 'presence' ] :
        print( f"df.head: {df.head}" )
        #sub_df = df.groupby( by=[ 'meeting', cluster_key, ], sort=True )[ cluster_key].agg( { cluster_key : 'count' } ).reset_index()
        fig_df = df.groupby( by=[ 'meeting', cluster_key, ], sort=False )[ cluster_key ].count().reset_index(name='count').sort_values(by='count', ascending=False )

        print( f"fig_df.head (groupby): {fig_df}" )
      else:
        if on_site is True:
          fig_df = df[ df.presence == 'on-site' ].groupby( by=[ 'meeting', cluster_key, ], sort=False )[ cluster_key ].count().reset_index( name='count' ).sort_values(by='count', ascending=False )
        elif on_site is False:
          fig_df = df[ df.presence != 'on-site' ].groupby( by=[ 'meeting', cluster_key, ], sort=False )[ cluster_key ].count().reset_index( name='count' ).sort_values(by='count', ascending=False )
        elif on_site is None:
          fig_df = df.groupby( by=[ 'meeting', cluster_key, ], sort=False )[ cluster_key ].count().reset_index( name='count' ).sort_values(by='count', ascending=False )

        else:
          raise ValueError( f"unexpected value for on_site: {on_site}"\
                  f" on_site MUST be in True, False or None." )
      print( f"fig_df: {fig_df}" )
      print( f"fig_df.columns: {fig_df.columns}" )
      print( f"fig_df.head: {fig_df.head}" )
#      subfig_list = []
#      subfig_title_list = []

#      cluster_df = sub_df.pivot( index='meeting', columns=cluster_key, values='count' )
#      sub_df = pd.DataFrame( [ sub_serie ] )
#      sub_df.columns.name = cluster_key
      if on_site is True:
        title = f"On-Site Attendee Distribution"
      elif on_site is False:
        title = f"Remote Attendee Distribution"
      elif on_site is None:
        title = f"Attendee Distribution (On-Site and Remote)"
#      fig_title = f"Attende Distribution per {cluster_key}"
#      subfig = px.bar( method_df, x=method_df.index,  y=method_df.columns,
      fig = px.bar( fig_df, x='meeting',  y='count',
                color=cluster_key,\
                # text=d.index.name, 
                title=title,
                ## labels are displayed when mouse is hand over the value.
                labels={ 'count': "Number of Attendees", 'meeting': "Meetings" },
              )
##      fig.update_xaxes(tickangle=90)
##      print( f"subfig: {subfig}" )
##      raise ValueError
##      subfig_list.append( subfig )
##      subfig_title_list.append( subfig_title )
      suffix = 'distribution'
      mode = 'attendee'
      html_file_name = self.image_file_name( suffix, 'html', mode,\
              cluster_key=cluster_key, on_site=on_site )
      svg_file_name=self.image_file_name( suffix, 'svg', mode,\
              cluster_key=cluster_key, on_site=on_site )
      ## scaling figure to the distribution mode.
      if len( self.co2eq_method_list ) != 0:
        fig_width = self.fig_width / len( self.co2eq_method_list )

      fig.update_layout(
        height=self.fig_height,
        width=fig_width,
        barmode='relative',
        title= { 'text': title, 'automargin': True, 'xref': 'container', 'y':0.95 },
        margin={ 'l':0, 'r':0 },
        font_family="Rockwell",
        showlegend=True
            )
#    for legend_name in legend_name_list:
#      self.fig[ 'layout' ][ legend_name ] = legend_layout[ legend_name ]
      if html_file_name is not None:
        fig.write_html( html_file_name )
      if svg_file_name is not None:
        fig.write_image( svg_file_name )
      if show is True:
        fig.show()

#      fig = co2eq.fig.OneRowSubfig( \
#        subfig_list,
#        subfig_title_list=subfig_title_list, ## we shoudl be able to read the title from the figure.
#        fig_title=title,
#        fig_width=self.fig_width,
#        fig_height=self.fig_height,
#        print_grid=True,
#        show=True,
#        shared_xaxes=False,
#        shared_yaxes=False,
#        legend_offset=0,
#        horizontal_spacing=0.3,
#        html_file_name=html_file_name,
#        svg_file_name=svg_file_name )
#      fig.fig.show()

  def plot_remote_versus_on_site( self ):
    """ plots the ratio of remote/on-site """
    pass

  def md_subsection_txt( self, mode, on_site_list, cabin=None, section_no=None):
    ## html_file name
#    if mode in [ 'flight', 'distance' ]:
#      html_file_name = self.image_file_name( 'distribution', 'html', mode,
#            on_site=on_site, cabin=cabin, no_path=True )
#    elif: mode == 'attendee' :
#      html_file_name = self.image_file_name( 'distribution', 'html', mode,
#            on_site=on_site, no_path=True )
#    else:        
#      raise ValueError( f"Unknown mode {mode}. Expecting 'attendee', 'distance' or 'flight'" )
    cluster_key_list = self.cluster_key_list[ : ]
    cluster_key_list.remove( 'co2eq' )

    md = "" 
    subsubsection_no = 1
    for cluster_key in cluster_key_list:
      if mode in [ 'flight', 'distance' ]:  
        subsection_title = f"CO2eq Distribution by `{cluster_key}` with {self.co2eq_method_list}"  
      elif mode == 'attendee':  
        subsection_title = f"Attendee Distribution by `{cluster_key}`"  
      if section_no is not None:
        subsection_no_str = f"{section_no}.{subsubsection_no}"
      else: 
        subsection_no_str = f"{subsubsection_no}"
      md += f"### {subsection_no_str} {subsection_title}\n\n"  
      for on_site in on_site_list:
        html_file_name = self.image_file_name( 'distribution', 'html', mode,\
              cabin=cabin, cluster_key=cluster_key, on_site=on_site, no_path=True )
#      if mode == 'attendee':
        md += self.embed_html( f"./{html_file_name}")
#      elif mode in [ 'flight', 'distance' ]:     
#        md += self.embed_html( f"./{html_file_name}")
#          md += f"<iframe src='./{html_file_name}'></iframe>\n\n"
#          md += f"<iframe src='./{html_file_name}'></iframe>\n\n"
#      else: 
#        raise ValueError( f"Uknown mode {mode}. Expecting 'attendee', 'flight', 'distance'" )
    return md 



  def md_banner( self, meeting_list_url=None, col_nbr=None, home_url=None ) -> str :
    """ returns the banner for a md page - though html is used.

    The banner contains a link to the main meeting list page as well as
    every individual meetings.
    Optionally, another home url may be added, for example when the meeting
    list pages are part of another web site.

    Args:
      meeting_list_url (str) : the url associated to the meeting list. The pages
        urls are derived as follows: the meetinglist name is appened to
        form the meeting list url. Each meeting names are appended to the url.
        For the IETF it is like if we had the following subdirectories:
        IETF and IETF99, IETF100, ...
      col_nbr (int) : the number of meeting names that can be shown on the web page.
        When multiple meetings are considered, these may b eprinted on multiple lines.
        To be aligned these are placed in a table of col_nbr columns.
    """
    if meeting_list_url is None:
      meeting_list_url = self.meeting_list_url
    if col_nbr is None:
      col_nbr = self.banner_col
    if home_url is None:
      home_url = self.home_url
      
    if meeting_list_url[ -1 ] != '/' :
      meeting_list_url += '/'
    cell_list = []
    cell_style = "text-decoration: none; padding: 0px; margin: 0px;"
    if home_url != None:
      cell_list.append( f"<a href='{home_url}' style='font-size: 30px; {cell_style}'>⌂</a>" )
    cell_list.append( f"<a href='{meeting_list_url}{self.name}' style='{cell_style}' >{self.name}</a>" )
    for m in self.meeting_list :
      cell_list.append( f"<a href='{meeting_list_url}{self.name}/{m.name}' style='{cell_style}' >{m.name}</a>" )

    row_nbr = math.ceil( len( cell_list ) / col_nbr )
    
    ## note that modifying the indentiation of the html block makes it
    ## mis-interpreted by jekyl and so produces a bad html rendering.
    begin_table = \
    """
  <html>
  <style>
  table, th, td {
    border: none;
    padding: 0px;
    padding-top: 0px;
    padding-bottom: 0px;
    padding-left: 0px;
    padding-right: 0px;
    margin: 0;
  }
  </style>
  <body>
    <table cellspacing="0" cellpadding="0" borrder="0"  style="width:100%;font-size:10px">
    """
    end_table = \
    """
    </table>
  </body>
  </html>
    """
    banner = begin_table
    for row in range( row_nbr ):
      banner += "      <tr>\n"
      for col in range( col_nbr ):
        try:
          banner += f"<td>{cell_list[ row * col_nbr + col ]}</td>\n"
        except IndexError:
          banner += f"<td> </td>\n"
      banner += "      </tr>\n"

    banner += end_table
    return banner

  def www( self,\
          mode_list=[ 'flight', 'attendee'],\
          cabin_list=[ 'AVERAGE' ] ):
##          on_site_list=[ None, True, False] ):
    """plots and generates the md for the web site

    plot_distribution considers on_site_list=[ None, True, False] )
    so this is what we are considering here. 
    """
    if 'presence' in self.cluster_key_list :
      on_site_list=[ None, True, False] 
    else:
      on_site_list=[ None ]

    banner = self.md_banner( )

    self.plot_distribution( mode_list=mode_list, cabin_list=cabin_list )
    for m in self.meeting_list:
      m.plot_distribution( mode_list=mode_list, cabin_list=cabin_list )

    self.md( mode_list=mode_list, cabin_list=cabin_list,\
             on_site_list=on_site_list, banner=banner )
    for m in self.meeting_list:
      m.md( mode_list=mode_list, cabin_list=cabin_list,
             on_site_list=on_site_list, banner=banner )
