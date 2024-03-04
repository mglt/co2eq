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
import co2eq.md

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
##      m_df = df_list.append( m_df )
      df_list.append( m_df )
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
        sub_df = df.groupby( by=[ 'meeting', cluster_key, ], sort=False).agg( agg_dict ).reset_index().sort_values(by=[ 'meeting', 'myclimate'], ascending=[ True, False ] )
      ## for other cluster_key we only focus on the CO2 associated to 
      ## on-site participants'
      else:
        if on_site is True:
          sub_df = df[ df.presence == 'on-site' ].groupby( by=[ 'meeting', cluster_key, ], sort=False ).agg( agg_dict ).reset_index().sort_values(by=[ 'meeting', 'myclimate'], ascending=[ True, False ] )
        elif on_site is False:
          sub_df = df[ df.presence != 'on-site' ].groupby( by=[ 'meeting', cluster_key, ], sort=False ).agg( agg_dict ).reset_index().sort_values(by=[ 'meeting', 'myclimate'], ascending=[ True, False ] )
        elif on_site is None:
          sub_df = df.groupby( by=[ 'meeting', cluster_key, ], sort=False ).agg( agg_dict ).reset_index().sort_values(by=[ 'meeting', 'myclimate' ], ascending=[ True, False ] )
#      sub_df = sub_df.set_index( cluster_key ).transpose()
      print( "----------------------------" )
      print( f"sub_df: {sub_df}" )
      print( f"sub_df.columns: {sub_df.columns}" )
      print( f"sub_df.head: {sub_df.head}" )
      subfig_list = []
#      subfig_title_list = []
      for co2eq_method in self.co2eq_method_list:
        subfig_title = f"Estimated with {co2eq_method}"
        subfig = px.bar( sub_df, x='meeting',  y=co2eq_method,
                  color=cluster_key,\
                  ##color=d.index.name,\
                  # text=d.index.name, 
                  title=subfig_title, 
                  ## labels are displayed when mouse is hand over the value.
                  labels={ 'value': "CO2eq (Kg)", 'index': "Meetings" },
                )
        subfig.update_xaxes(tickangle=90)
        subfig_list.append( subfig )
#        subfig_title_list.append( subfig_title )
      
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
#      raise ValueError

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
##    agg_dict = { 'count' : 'sum' }
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
        fig_df = df.groupby( by=[ 'meeting', cluster_key, ], sort=False )[ cluster_key ].count().reset_index(name='count').sort_values(by=[ 'meeting', 'count'], ascending=[ False, False ] )

        print( f"fig_df.head (groupby): {fig_df}" )
      else:
        if on_site is True:
          fig_df = df[ df.presence == 'on-site' ].groupby( by=[ 'meeting', cluster_key, ], sort=False )[ cluster_key ].count().reset_index( name='count' ).sort_values(by=[ 'meeting', 'count'], ascending=[ False, False ] )
        elif on_site is False:
          fig_df = df[ df.presence != 'on-site' ].groupby( by=[ 'meeting', cluster_key, ], sort=False )[ cluster_key ].count().reset_index( name='count' ).sort_values(by=[ 'meeting', 'count'], ascending=[ False, False ] )
        elif on_site is None:
          fig_df = df.groupby( by=[ 'meeting', cluster_key, ], sort=False )[ cluster_key ].count().reset_index( name='count' ).sort_values(by=[ 'meeting', 'count'], ascending=[ False, False ] )

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
      fig.update_xaxes(tickangle=90)
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

  def plot_co2eq_remote_ratio( self, mode='flight', cabin='AVERAGE', show=False, print_grid=False, most_emitters=None ):
    """ plots the ratio of remote/on-site """

    df = self.build_data( mode=mode, cabin=cabin )
    if 'presence' not in df.columns :
      raise ValueError( f"on_site is specified to {on_site} but "\
        f"'presence' is not specified in the data frame.\n"\
        f"{df.info}\ndf.columns: {df.columns}" )
    cluster_key_list = self.cluster_key_list[ : ]
    cluster_key_list.remove( 'co2eq' )
    subfig_list = []

    agg_dict = {}
    for co2eq_method in self.co2eq_method_list :
      agg_dict[ co2eq_method ] = 'sum'

    title = f"Remote Ratio of CO2eq Distribution"
    for cluster_key in cluster_key_list :
      if cluster_key in [ 'presence' ] :
        print( f"--> 1. df.head: {df.head}" )
        ## summinf emissions by presence type
        fig_df = df.groupby( by=[ 'meeting', 'presence' ], sort=False ).agg( agg_dict ).reset_index()
        print( f"--> 2. fig_df.head: {fig_df.head}" )
        print( f"--> 2. fig_df.info: {fig_df.info()}" )
        fig_remote = fig_df[ fig_df.presence != 'on-site' ].agg( agg_dict )
       # .groupby( by=[ 'meeting', 'presence', ], sort=True )[ cluster_key ]
        print( f"--> 3. fig_remote.head: {fig_remote}" )
        print( f"--> 3. fig_remote.info: {fig_remote.info()}" )
        fig_df = fig_df.groupby( by=[ 'meeting'], sort=False ).agg( agg_dict )
        print( f"--> 4. fig_df.head: {fig_df.head}" )
        print( f"--> 4. fig_df.info: {fig_df.info()}" )

##          subfig = px.bar( sub_df, x='meeting',  y=co2eq_method,
##                    color=cluster_key,\
##                    ##color=d.index.name,\
##                    # text=d.index.name, 
##                    title=subfig_title, 
##                    ## labels are displayed when mouse is hand over the value.
##                    labels={ 'value': "CO2eq (Kg)", 'index': "Meetings" },
##                  )
##          subfig.update_xaxes(tickangle=90)
##          subfig_list.append( subfig )
      else:
        pd.set_option("display.max_rows", None, "display.max_columns", None)
        print( f"--> 1. df.head: {df.head(60)}" )
        ## counting the number of participants for each typ eof presence
        fig_df = df.groupby( by=[ 'meeting', cluster_key, 'presence' ], sort=False ).agg( agg_dict ).reset_index()
        print( f"--> 2. fig_df.head: {fig_df}" )
        ## summing all possible values that are not on-site (in our case,
        ## it could be not-arrived, remote) per cluster_key
        fig_remote = fig_df[ fig_df.presence != 'on-site' ].groupby( by=[ 'meeting', cluster_key], sort=False ).agg( agg_dict )
#[ [ 'meeting', cluster_key, 'presence','count' ] ].reset_index()
       # .groupby( by=[ 'meeting', 'presence', ], sort=True )[ cluster_key ]
        print( f"--> 3. fig_remote.head: {fig_remote}" )
        ## counting the total number of participants per cluster_key
        fig_df = fig_df.groupby( by=[ 'meeting', cluster_key, ], sort=False ).agg( agg_dict )
        print( f"--> 4. fig_df.head: {fig_df}" )
        ## index is ( meeting, cluster_key )


##        fig_df[ 'ratio' ] = fig_remote[ 'sum' ] / fig_df[ 'sum' ] * 100 
##        ## flatering the index
##        print( f"--> 5. fig_df.head: {fig_df}" )
##        ## when remote is not defined a value set to nan is provided.
##        ## we replace it by 0
##        fig_df[ 'ratio' ] = fig_df[ 'ratio' ].fillna( 0 )
##        ## cluster_key is the union of all values. (not needed)
##        ## cluster_key_list = fig_df[ cluster_key ].unique().tolist()
#      fig_title = f"Attende Distribution per {cluster_key}"
#      subfig = px.bar( method_df, x=method_df.index,  y=method_df.columns,
#        meeting_list = [ f"{m.name} - {m.meeting_iata_city}"  for m in self.meeting_list ]
#        fig_df = fig_df[ fig_df.sum >= 5 ]
##        fig_df = fig_df.reset_index()

##        fig = px.line( fig_df, x='meeting',  y='ratio',
##                color=cluster_key,\
##                # text=d.index.name, 
##                title=title,
##                ## labels are displayed when mouse is hand over the value.
##                labels={ 'ratio': "Ratio Remote / On Site (%)", 'meeting': "Meetings" },
##              )
##        fig.update_xaxes(tickangle=90)
##        fig.show( )
##      print( f"subfig: {subfig}" )
##      raise ValueError
##      subfig_list.append( subfig )
##      subfig_title_list.append( subfig_title )

      ## computing ration for all co2eq_methods
      for co2eq_method in self.co2eq_method_list:
        ratio = f"ratio_{co2eq_method}"
        print( f" ----- fig_remote: {fig_remote}" )
        print( f" ----- fig_df: {fig_df}" )
        fig_df[ ratio ] = fig_remote[ co2eq_method ] / fig_df[ co2eq_method ] * 100 
        fig_df[ ratio ] = fig_df[ ratio ].fillna( 0 )
      fig_df = fig_df.reset_index()
      ## getting the X most emitters
      if most_emitters is not None:
        fig_df = fig_df.nlargest( n=most_emitters, columns= [ co2eq_method ] )

      suffix = 'remote_ratio'
      html_file_name = self.image_file_name( suffix, 'html', mode,\
              cluster_key=cluster_key, most_emitters=most_emitters )
      svg_file_name=self.image_file_name( suffix, 'svg', mode,\
              cluster_key=cluster_key, most_emitters=most_emitters )
      ## scaling figure to the distribution mode.
      if len( self.co2eq_method_list ) != 0:
        fig_width = self.fig_width / len( self.co2eq_method_list )
      if cluster_key == "presence":
        color = None
      else: 
        color = cluster_key
      subfig_list = []
      for co2eq_method in self.co2eq_method_list:
        ratio = f"ratio_{co2eq_method}"
        subfig_title = f"Estimated with {co2eq_method}"
        subfig = px.line( fig_df, x='meeting',  y=ratio,
                color = color,
                # text=d.index.name, 
                title=subfig_title,
                ## labels are displayed when mouse is hand over the value.
                labels={ 'ratio': "CO2 Ratio Remote / (Remote  + On Site ) (%)", 'meeting': "Meetings" },
              )
        subfig.update_xaxes( tickangle=90 )
        subfig.update_layout(
          height=self.fig_height,
          width=fig_width,
          barmode='relative',
          title= { 'text': title, 'automargin': True, 'xref': 'container', 'y':0.95 },
          margin={ 'l':0, 'r':0 },
          font_family="Rockwell",
          showlegend=True
              )
        subfig_list.append( subfig )

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

#    for legend_name in legend_name_list:
#      self.fig[ 'layout' ][ legend_name ] = legend_layout[ legend_name ]
#      if html_file_name is not None:
#        fig.write_html( html_file_name )
#      if svg_file_name is not None:
#        fig.write_image( svg_file_name )
#      if show is True:
#        fig.show()

#      fig = co2eq.fig.OneRowSubfig( \

  def plot_attendee_remote_ratio( self, show=False, print_grid=False, most_present=None ):
    """ plots the ratio of remote/on-site """

    df = self.build_data( mode='attendee' )
    if 'presence' not in df.columns :
      raise ValueError( f"on_site is specified to {on_site} but "\
        f"'presence' is not specified in the data frame.\n"\
        f"{df.info}\ndf.columns: {df.columns}" )
    cluster_key_list = self.cluster_key_list[ : ]
    cluster_key_list.remove( 'co2eq' )
    subfig_list = []

    title = f"Remote Attendee Ratio Distribution"
    for cluster_key in cluster_key_list :
      if cluster_key in [ 'presence' ] :
        print( f"--> 1. df.head: {df.head}" )
        fig_df = df.groupby( by=[ 'meeting', 'presence' ], sort=False )[ cluster_key ].agg( [ 'count' ] ).reset_index()
        print( f"--> 2. fig_df.head: {fig_df.head}" )
        print( f"--> 2. fig_df.info: {fig_df.info()}" )
        fig_remote = fig_df[ fig_df.presence != 'on-site' ][ 'count' ].agg( [ 'sum' ] )
       # .groupby( by=[ 'meeting', 'presence', ], sort=True )[ cluster_key ]
        print( f"--> 3. fig_remote.head: {fig_remote}" )
        print( f"--> 3. fig_remote.info: {fig_remote.info()}" )
        fig_df = fig_df.groupby( by=[ 'meeting'], sort=False )[ 'count' ].agg( [ 'sum' ] )
        print( f"--> 4. fig_df.head: {fig_df.head}" )
        print( f"--> 4. fig_df.info: {fig_df.info()}" )
####        fig_df[ 'ratio' ] = fig_remote[ 'sum' ] / fig_df[ 'sum' ] * 100 
####        print( f"--> 5. fig_df.head: {fig_df.head}" )
####        print( f"--> 5. fig_df.info: {fig_df.info()}" )
####        fig_df[ 'ratio' ] = fig_df[ 'ratio' ].fillna( 0 )
####        fig_df = fig_df.reset_index()
####        fig = px.line( fig_df, x='meeting',  y='ratio',
####                # text=d.index.name, 
####                title=title,
####                ## labels are displayed when mouse is hand over the value.
####                labels={ 'ratio': "Ratio Remote / On Site (%)", 'meeting': "Meetings" },
####              )
####        fig.update_xaxes(tickangle=90)
      else:
        pd.set_option("display.max_rows", None, "display.max_columns", None)
        print( f"--> 1. df.head: {df.head(60)}" )
        ## counting the number of participants for each typ eof presence
        fig_df = df.groupby( by=[ 'meeting', cluster_key, 'presence' ], sort=False )[ cluster_key ].agg( [ 'count' ] ).reset_index()
        print( f"--> 2. fig_df.head: {fig_df}" )
        ## summing all possible values that are not on-site (in our case,
        ## it could be not-arrived, remote) per cluster_key
        fig_remote = fig_df[ fig_df.presence != 'on-site' ].groupby( by=[ 'meeting', cluster_key], sort=False )[ 'count' ].agg( [ 'sum' ] )
#[ [ 'meeting', cluster_key, 'presence','count' ] ].reset_index()
       # .groupby( by=[ 'meeting', 'presence', ], sort=True )[ cluster_key ]
        print( f"--> 3. fig_remote.head: {fig_remote}" )
        ## counting the total number of participants per cluster_key
        fig_df = fig_df.groupby( by=[ 'meeting', cluster_key, ], sort=True )[ 'count' ].agg( [ 'sum' ] )
        print( f"--> 4. fig_df.head: {fig_df}" )
        ## index is ( meeting, cluster_key )
      fig_df[ 'ratio' ] = fig_remote[ 'sum' ] / fig_df[ 'sum' ] * 100 
      ## flatering the index
      print( f"--> 5. fig_df.head: {fig_df}" )
      ## when remote is not defined a value set to nan is provided.
      ## we replace it by 0
      fig_df[ 'ratio' ] = fig_df[ 'ratio' ].fillna( 0 )
      ## cluster_key is the union of all values. (not needed)
      ## cluster_key_list = fig_df[ cluster_key ].unique().tolist()
#      fig_title = f"Attende Distribution per {cluster_key}"
#      subfig = px.bar( method_df, x=method_df.index,  y=method_df.columns,
#        meeting_list = [ f"{m.name} - {m.meeting_iata_city}"  for m in self.meeting_list ]
#        fig_df = fig_df[ fig_df.sum >= 5 ]
      fig_df = fig_df.reset_index()
      if most_present is not None:
        fig_df = fig_df.nlargest( n=most_present, columns=['sum' ] )
####        fig = px.line( fig_df, x='meeting',  y='ratio',
####                color=cluster_key,\
####                # text=d.index.name, 
####                title=title,
####                ## labels are displayed when mouse is hand over the value.
####                labels={ 'ratio': "Ratio Remote / On Site (%)", 'meeting': "Meetings" },
####              )
####        fig.update_xaxes(tickangle=90)
##        fig.show( )
##      print( f"subfig: {subfig}" )
##      raise ValueError
##      subfig_list.append( subfig )
##      subfig_title_list.append( subfig_title )
      suffix = 'remote_ratio'
      mode = 'attendee'
      html_file_name = self.image_file_name( suffix, 'html', mode,\
              cluster_key=cluster_key, most_present=most_present )
      svg_file_name=self.image_file_name( suffix, 'svg', mode,\
              cluster_key=cluster_key, most_present=most_present)
      ## scaling figure to the distribution mode.
      if len( self.co2eq_method_list ) != 0:
        fig_width = self.fig_width / len( self.co2eq_method_list )
      if cluster_key == "presence":
        color = None # no legend
      else:
        color = cluster_key # cluster_key is displayed in the legend

      fig = px.line( fig_df, x='meeting',  y='ratio',
              color=color,\
              # text=d.index.name, 
              title=title,
              ## labels are displayed when mouse is hand over the value.
              labels={ 'ratio': "Ratio Remote / ( Remote + On Site ) (%)", 'meeting': "Meetings" },
            )
      fig.update_xaxes(tickangle=90)

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
    

  def md_subsection_txt( self, mode, on_site_list, cabin=None ): #, section_no=None):
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
####    subsubsection_no = 1
    for cluster_key in cluster_key_list:
      if mode in [ 'flight', 'distance' ]:  
        subsection_title = f"CO2eq Distribution by `{cluster_key}` with {self.co2eq_method_list}"  
      elif mode == 'attendee':  
        subsection_title = f"Attendee Distribution by `{cluster_key}`"  
####      if section_no is not None:
####        subsection_no_str = f"{section_no}.{subsubsection_no}"
####      else: 
####        subsection_no_str = f"{subsubsection_no}"
####      md += f"### {subsection_no_str} {subsection_title}\n\n"  
      md += f"### {subsection_title}\n\n"  
      for on_site in on_site_list:
        html_file_name = self.image_file_name( 'distribution', 'html', mode,\
              cabin=cabin, cluster_key=cluster_key, on_site=on_site, no_path=True )
#      if mode == 'attendee':
####        md += self.embed_html( f"./{html_file_name}")
        md += co2eq.md.embed_html( f"./{html_file_name}" )
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

  def ratio_md( self, mode_list=[ 'flight' , 'attendee' ], 
    cabin_list=[ 'AVERAGE' ], 
    on_site_list=[ None, True, False], 
    banner="",
    toc=True, output_md="index.md",
    most_emitters=None,
    most_present=None ):
 
    co2eq_dist = 'flight' in mode_list or 'distance' in mode_list
    atten_dist = 'attendee' in mode_list
    if atten_dist and co2eq_dist :
      title = f"{self.name}: Remote Participation Ratio of CO2 Emission and Attendees"  
      txt = f"This page estimates the remote participation CO2 emitted for {self.name} as well as the distribution of the attendees of {self.name}."
    elif atten_dist and not co2eq_dist: 
      txt = f"This page displays the distribution of the attendees of {self.name}."
    elif not atten_dist and co2eq_dist :
      txt = f"This page estimates the CO2 emitted according for {self.name}."
    else: 
      raise ValueError( f"only ")
      
    txt = """This page provides the ratio of users that attends the meeting remotely.

Such ratio, seems to be a good indicator on how the meeting is achieving a transition toward a sustainable implementation with less flights. 

A meeting MAY propose attendee to participate remotely, but such participation is only effective if the propose remote participation experience matches the expectation or contrains of the remote participants. In some meetings, this means for example, the ability to ask questions and queing in a list that is completely forgotten.
The main argument for on site participation is the ability to 'socialize'. This makes remote attendancy especially difficult when the main purpose of attendee is to meet colleagues as opposed to exchange information.  

There is a critical ratio to meet in order to make remote participation effective. As long as critical ratio has not been met, remote participant are still 'second class' participants. 

Note that in some cases, attendes are considered as 'remote' when they registered as 'remote' all other categories are considered as non remote andf are assimilated to 'on-site' users. This includes for example users that are some times indicated as 'not-arrived'. The reasonning is that such attendee was expected to attend 'on-site'. Then, it is difficult to estimate if he effectively has not travelled or if he is attending as a remote user. Note also that these attendee does not represent a huge portion of the attendees. 

The Remote Ratio is both expressed in term of CO2 Emission as well as in term of Particiapation. 
"""
    txt_co2 = """The Remote Ratio expressed with CO2 emission indicates the ratio of CO2 mission being offset by remote participants versus the CO2 emissions associated to the meetings. If the remote access is seen as a way to reduce the CO2 emissions associated to the meetings, this Remote Ratio illustrates the effectiveness of the remote policy of the meetings and its evolution.

Note that this constitutes a first approximation as a participant that does not flight for example may still have some emission that may be associated to its life style. While further analysis, one can estimate that emissions associated to a flight remains way above the standard emissions associated to its every-day- life."""

    txt_attend = """The Remote Ratio expressed with attendee numbers reflects the acceptance of teh remote participation and its evolution."""

    for mode in mode_list:
      if mode in [ 'flight', 'distance' ]:
        for cabin in cabin_list :
          md_txt += f"## CO2 Estimation for '{mode}' mode in cabin {cabin} for {self.name}\n\n"
          md_txt += self.md_subsection_txt( mode, on_site_list, cabin )
      elif mode == 'attendee':
        md_txt += f"## Attendee Distribution for {self.name}\n\n"
        md_txt += self.md_subsection_txt( mode, on_site_list ) #, secti

    md = co2eq.md.MdFile( md_txt )
    md.number_sections()
    md.save( join( self.output_dir, output_md ) )


  def summary_md( self ):    
    pass

  def www( self,\
          mode_list=[ 'flight', 'attendee'],\
          cabin_list=[ 'AVERAGE' ], most_emitters=None, most_present=None ):
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
    ## When 'co2eq' is computed and presence is mentioned generating 
    ## figures and text for ratio. 
    if 'presence' in self.cluster_key_list :
      ##plot ratios
      ## 
      pass

    ## generating the figures for the meeting_list as well as for each meeting
    self.plot_distribution( mode_list=mode_list, cabin_list=cabin_list )
    for m in self.meeting_list:
      m.plot_distribution( mode_list=mode_list, cabin_list=cabin_list )

    ## generating the md file
    self.dist_md( mode_list=mode_list, cabin_list=cabin_list,\
             on_site_list=on_site_list, banner=banner, output_md='dist.md' )
    for m in self.meeting_list:
      m.dist_md( mode_list=mode_list, cabin_list=cabin_list,
             on_site_list=on_site_list, banner=banner )
