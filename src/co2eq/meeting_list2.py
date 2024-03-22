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
                  goclimateDB=True,
                  mode_list= [ 'attendee', 'flight'], 
                  cabin_list=[ 'AVERAGE' ], 
                  ## can be derived from the meeting objects
                  cluster_key_list=None,
                  co2eq_method_list=None
                  ):

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
    self.init_meeting_list( mode_list=mode_list, 
            cabin_list=cabin_list, 
            cluster_key_list=cluster_key_list, 
            co2eq_method_list=co2eq_method_list)
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
    ## number of meeting names per line displayed in the banner
    self.banner_col=11


    ## we remove 'co2eq' 
    if 'co2eq' in self.cluster_key_list: 
      self.cluster_key_list.remove( 'co2eq' )

  def init_meeting_list( self, 
          mode_list=[ 'attendee', 'flight'],
          cabin_list=[ 'AVERAGE' ], 
          cluster_key_list=None, 
          co2eq_method_list=None ):
    self.meeting_list = []
    self.cluster_key_list = cluster_key_list
    self.co2eq_method_list = co2eq_method_list
    for json_meeting in self.json_meeting_list:
      m_name = json_meeting[ 'name' ]  
      m_loc = json_meeting[ 'location' ] 
#      pickle_file = os.path.join( self.output_dir, f"{m_name}.pickle" )
#      if os.path.isfile( pickle_file ) :
#        meeting = pickle.load( pickle_file )
#      else:

      m_base_output_dir = self.output_dir
      meeting = co2eq.meeting2.Meeting( 
              m_name, m_loc,  self.conf, \
              attendee_list=json_meeting[ 'attendee_list' ], 
              base_output_dir=m_base_output_dir, \
              airportDB=self.airportDB, 
              cityDB=self.cityDB, 
              flightDB=self.flightDB, 
              goclimateDB=self.goclimateDB )
      ## self.cluster_key_list is derived from meetings 
      ## only when cluster_key_list is not provided
      if cluster_key_list is None:
        if self.cluster_key_list is None:
          self.cluster_key_list = meeting.cluster_key_list
        else:
          for cluster_key in meeting.cluster_key_list:
            if cluster_key not in self.cluster_key_list:
              self.cluster_key_list.append( cluster_key )
      ## self.co2eq_method_list is derived from meetings 
      ## only when co2eq_method_list is not provided
      if co2eq_method_list is None:
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

    ## this is useful to adjust presentation
    pickle_file = self.image_file_name( 'data', 'pickle', mode, cabin=cabin )
#    file_name = f"meeting_list--name-{self.name}--mode-{mode}"
#    if cabin is not None:
#      file_name = f"{file_name}--cabin-{cabin}"
#    file_name = f"{file_name}.pickle"  
#    file_name = os.path.join( self.output_dir, file_name )
    if os.path.isfile( pickle_file ) :
      return pd.read_pickle( pickle_file )    

    df_list = []
    ## to keep the order of the meeting_list we provide the 
    ## index as opposed to the meeting name.
    for i, meeting in enumerate( self.meeting_list ):
      m_df = meeting.build_data( mode=mode, cabin=cabin )
      # m_df.insert( 0, 'meeting', f"{meeting.name} - {meeting.meeting_iata_city}"  )
      m_df.insert( 0, 'meeting', i  )
##      m_df = df_list.append( m_df )
      df_list.append( m_df )
    df = pd.concat( df_list, ignore_index=True, sort=False)
    self.df_data[ ( mode, cabin ) ] =  df

    df.to_pickle( file_name )
    return df

  def is_fig_generated( self, suffix, mode, cabin, on_site ):
    """ returns True is html/svg files are already generated

    """
    if on_site not in [ True, False, None ]:
      raise ValueError( f"Unknown value {on_site} for on_site.\
        Expecting True, False or None" )

    is_file_list = []
    for cluster_key in self.cluster_key_list :
      html_file_name = self.image_file_name( suffix, 'html', mode, cabin=cabin,
              cluster_key=cluster_key, on_site=on_site )
      svg_file_name=self.image_file_name( suffix, 'svg', mode, cabin=cabin,
              cluster_key=cluster_key, on_site=on_site )
      is_file_list.append( os.path.isfile( html_file_name ) and\
              os.path.isfile( svg_file_name ) )
    if False not in is_file_list :
      return True
    return False

  def meeting_axis( self, sub_df ):
    """generates the x-axis with meeting names

    Meetings are represented with their index, This function
    provides the names associated to the meetings. The order
    is the one of the meeting list. 
    """
    meeting_index_list = sub_df[ 'meeting' ].tolist()
#    print( f"meeting_index_list: [{meeting_index_list}] {meeting_index_list}" )
#    for i in meeting_index_list:
    x = []
    for i in sub_df[ 'meeting' ].tolist():
      m = self.meeting_list[ i ]  
      x.append( f"{m.name} - {m.meeting_iata_city}" )    
#    print( f"x: [{type(x)}] {x}" )
    return x

  def zero_fill_df( self, sub_df, cluster_key ):
    """Ensures non defined values are set to zero
    
    Histograms do not handle missing values appropriately. In our case, we observed that when a category was missing in a cluster_key, the full column was 're-ordered' and put at the end.   
    """
    for m in sub_df[ 'meeting' ].unique():
      for v in sub_df[ cluster_key ].unique():  
        if not sub_df.loc[(sub_df['meeting'] == m ) & (sub_df[ cluster_key ] == v)].any().all():
          d = {}  
          for col in sub_df.columns: 
            if col == 'meeting' :
              d[ 'meeting' ] = m
            elif col == cluster_key :
              d[ cluster_key ] = v
            else:
              d[ col ] = 0  
          sub_df = pd.concat( [ sub_df, pd.DataFrame ( [ d ] ) ], ignore_index = True )

    return sub_df
#    return sub_df.sort_values(by=[ 'meeting', 'myclimate' ], ascending=[ True, False ] )
      
#     print( f"sub_df with zeros: {sub_df.head(100)}" )



  def plot_co2eq_distribution( self, mode='flight', cabin='AVERAGE', on_site=None, show=False, print_grid=False):


#    cluster_key_list = self.cluster_key_list[ : ]
#    cluster_key_list.remove( 'co2eq' )

    suffix = 'distribution'
    if self.is_fig_generated( suffix, mode, cabin, on_site ) :
      return None

##    is_file_list = []
##    for cluster_key in cluster_key_list :
##      html_file_name = self.image_file_name( suffix, 'html', mode, cabin=cabin,
##              cluster_key=cluster_key, on_site=on_site )
##      svg_file_name=self.image_file_name( suffix, 'svg', mode, cabin=cabin,
##              cluster_key=cluster_key, on_site=on_site )
##      is_file_list.append( os.path.isfile( html_file_name ) and\
##              os.path.isfile( svg_file_name ) )
##    if False not in is_file_list :
##      return None


    df = self.build_data( mode=mode, cabin=cabin )
    
    if 'presence' not in df.columns and on_site is not None:
      raise ValueError( f"on_site is specified to {on_site} but "\
        f"'presence' is not specified in the data frame.\n"\
        f"{df.info}\ndf.columns: {df.columns}" )

    agg_dict = {}
    for co2eq_method in self.co2eq_method_list :
      agg_dict[ co2eq_method ] = 'sum'

    for cluster_key in self.cluster_key_list :
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

      ## completing values that are not filled with zero.
      ## This is to prevent the histogram to re-order 
      ## the meetings as it as not found a value.
      sub_df = self.zero_fill_df( sub_df, cluster_key )
      sub_df = sub_df.sort_values(by=[ 'meeting', 'myclimate' ], ascending=[ True, False ] )
                
      subfig_list = []
#      subfig_title_list = []
      for co2eq_method in self.co2eq_method_list:
        subfig_title = f"Estimated with {co2eq_method}"
        ## meetings must be displayed in the meeting list order
        ## not the alphabetical order.
        #subfig = px.bar( sub_df, x='meeting',  y=co2eq_method,
#        x = []
        meeting_index_list = sub_df[ 'meeting' ].tolist()
#        print( f"meeting_index_list: [{meeting_index_list}] {meeting_index_list}" )
#        for i in meeting_index_list:
#          m = self.meeting_list[ i ]  
#          x.append( f"{m.name} - {m.meeting_iata_city}" )    
#        print( f"x: [{type(x)}] {x}" )
#        def meeting_axis( self, sub_df ):
        subfig = px.bar( sub_df, x=self.meeting_axis( sub_df ),\
                  y=co2eq_method,
                  color=cluster_key,\
                  ##color=d.index.name,\
                  # text=d.index.name, 
                  title=subfig_title, 
                  ## labels are displayed when mouse is hand over the value.
                  labels={ 'value': "CO2eq (Kg)", 'index': "Meetings" },
                )
        subfig.update_xaxes(tickangle=90 )#, tickvals=x, ticktext=x)
#        subfig.update_traces(width=2)
        subfig_list.append( subfig )


      html_file_name = self.image_file_name( suffix, 'html', \
              mode, cabin=cabin, cluster_key=cluster_key,\
              on_site=on_site )
      svg_file_name=self.image_file_name( suffix, 'svg',\
              mode, cabin=cabin, cluster_key=cluster_key,\
              on_site=on_site )

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
#      print_grid=True 
      fig = co2eq.fig.OneRowSubfig( \
        subfig_list,
        fig_title=title,
        fig_width=int( 2.5 * self.fig_width ),
        fig_height=int( 1 * self.fig_height ),
        print_grid=print_grid,
        show=show,
        shared_xaxes=False,
        shared_yaxes=False,
        legend_offset=[ -0.065, -0.133, -0.2 ],
        horizontal_spacing=0.1,
        html_file_name=html_file_name,
        svg_file_name=svg_file_name )
#      fig.fig.show()

  def plot_attendee_distribution( self, on_site=None, show=False, print_grid=False ):

#    cluster_key_list = self.cluster_key_list[ : ]
#    cluster_key_list.remove( 'co2eq' )
#    is_file_list = []
    suffix = 'distribution'
    mode = 'attendee'
#    for cluster_key in cluster_key_list :
#      html_file_name = self.image_file_name( suffix, 'html', mode,\
#              cluster_key=cluster_key, on_site=on_site )
#      svg_file_name=self.image_file_name( suffix, 'svg', mode,\
#              cluster_key=cluster_key, on_site=on_site )
#      is_file_list.append( os.path.isfile( html_file_name ) and\
#              os.path.isfile( svg_file_name ) )
#    if False not in is_file_list :
#      return None
    if self.is_fig_generated( suffix, mode, None, on_site ) :
      return None

    df = self.build_data( mode=mode )
#    if on_site not in [ True, False, None ]:
#      raise ValueError( f"Unknown value {on_site} for on_site.\
#        Expecting True, False or None" )
    if 'presence' not in df.columns and on_site is not None:
      raise ValueError( f"on_site is specified to {on_site} but "\
        f"'presence' is not specified in the data frame.\n"\
        f"{df.info}\ndf.columns: {df.columns}" )
    subfig_list = []

    for cluster_key in self.cluster_key_list :
      ## with cluster_key set to presence, we plot the number
      ## of attendees. 
      ## associated to the presence, which includes remote,
      ## not arrived and on-site
      if cluster_key in [ 'presence' ] :
        fig_df = df.groupby( by=[ 'meeting', cluster_key, ], sort=False )[ cluster_key ].count().reset_index(name='count').sort_values(by=[ 'meeting', 'count'], ascending=[ False, False ] )
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

      fig_df = self.zero_fill_df( fig_df, cluster_key )
      fig_df = fig_df.sort_values(by=[ 'meeting', 'count' ], ascending=[ True, False ] )

      if on_site is True:
        title = f"On-Site Attendee Distribution"
      elif on_site is False:
        title = f"Remote Attendee Distribution"
      elif on_site is None:
        title = f"Attendee Distribution (On-Site and Remote)"
#        subfig = px.bar( sub_df, x=self.meeting_axis( sub_df ),\
#      fig = px.bar( fig_df, x='meeting',  y='count',
      fig = px.bar( fig_df, x=self.meeting_axis( fig_df ),\
              y='count',
              color=cluster_key,\
              # text=d.index.name, 
              title=title,
              ## labels are displayed when mouse is hand over the value.
                labels={ 'count': "Number of Attendees", 'meeting': "Meetings" },
              )
      html_file_name = self.image_file_name( suffix, 'html', mode,\
              cluster_key=cluster_key, on_site=on_site )
      svg_file_name=self.image_file_name( suffix, 'svg', mode,\
              cluster_key=cluster_key, on_site=on_site )
      ## scaling figure to the distribution mode.
#      if len( self.co2eq_method_list ) != 0:
#        fig_width = self.fig_width / len( self.co2eq_method_list )

      fig.update_layout(
        height=int( 0.6 * self.fig_height ),
        width=int( 0.6 * self.fig_width ),
        barmode='relative',
        title= { 'text': title, 'automargin': True, 'xref': 'container', 'y':0.95 },
        margin={ 'l':0, 'r':0 },
        font_family="Rockwell",
        showlegend=True
            )
      fig.update_xaxes(tickangle=90)
#      if html_file_name is not None:
      fig.write_html( html_file_name )
#      if svg_file_name is not None:
      fig.write_image( svg_file_name )
      if show is True:
        fig.show()

  def plot_co2eq_remote_ratio( self, mode='flight', cabin='AVERAGE', show=False, print_grid=False, most_emitters=None ):
    """ plots the ratio of remote/on-site """

    cluster_key_list = self.cluster_key_list[ : ]
#    cluster_key_list.remove( 'co2eq' )
    suffix = 'remote_ratio'
    is_file_list = []
    for cluster_key in cluster_key_list :
      html_file_name = self.image_file_name( suffix, 'html', mode,\
              cabin=cabin, cluster_key=cluster_key, \
              most_emitters=most_emitters )
      svg_file_name=self.image_file_name( suffix, 'svg', mode,\
              cabin=cabin, cluster_key=cluster_key, \
              most_emitters=most_emitters )
      is_file_list.append( os.path.isfile( html_file_name ) and\
              os.path.isfile( svg_file_name ) )
    if False not in is_file_list:
      return    

    df = self.build_data( mode=mode, cabin=cabin )
    if 'presence' not in df.columns :
      raise ValueError( f"on_site is specified to {on_site} but "\
        f"'presence' is not specified in the data frame.\n"\
        f"{df.info}\ndf.columns: {df.columns}" )
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

      ## computing ration for all co2eq_methods
      for co2eq_method in self.co2eq_method_list:
        ratio = f"ratio_{co2eq_method}"
        fig_df[ ratio ] = fig_remote[ co2eq_method ] / fig_df[ co2eq_method ] * 100 
        fig_df[ ratio ] = fig_df[ ratio ].fillna( 0 )
      fig_df = fig_df.reset_index()
      ## getting the X most emitters
      if most_emitters is not None:
        fig_df = fig_df.nlargest( n=most_emitters, columns= [ co2eq_method ] )

      html_file_name = self.image_file_name( suffix, 'html', mode,\
              cabin=cabin, cluster_key=cluster_key, \
              most_emitters=most_emitters )
      svg_file_name=self.image_file_name( suffix, 'svg', mode,\
              cabin=cabin, cluster_key=cluster_key, \
              most_emitters=most_emitters )
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

  def plot_attendee_remote_ratio( self, show=False, print_grid=False, most_present=None ):
    """ plots the ratio of remote/on-site """

    cluster_key_list = self.cluster_key_list[ : ]
#    cluster_key_list.remove( 'co2eq' )
    suffix = 'remote_ratio'
    mode = 'attendee'
    is_file_list = []
    for cluster_key in cluster_key_list :
      html_file_name = self.image_file_name( suffix, 'html', mode,\
              cluster_key=cluster_key, most_present=most_present )
      svg_file_name=self.image_file_name( suffix, 'svg', mode,\
              cluster_key=cluster_key, most_present=most_present)
      is_file_list.append( os.path.isfile( html_file_name ) and\
              os.path.isfile( svg_file_name ) )
    if False not in is_file_list:
      return    


    df = self.build_data( mode='attendee' )
    if 'presence' not in df.columns :
      raise ValueError( f"on_site is specified to {on_site} but "\
        f"'presence' is not specified in the data frame.\n"\
        f"{df.info}\ndf.columns: {df.columns}" )
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
      fig_df = fig_df.reset_index()
      if most_present is not None:
        fig_df = fig_df.nlargest( n=most_present, columns=['sum' ] )
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

  def dist_md_subsection_txt( self, mode, on_site_list, cabin=None ):
    """ overwrite the dist_md_subsection
    
    The dist_md_subsection_txt outputs a single figure with all
    cluster_key. This is not possible to display them all as we
    already agregate th emultiple meetings. To address this we 
    generate a scetion for each cluster_key.
    """

    return self.md_subsection_txt( 'distribution', mode, 
            on_site_list=on_site_list, cabin=cabin )     
  
  def md_subsection_txt( self, suffix, mode, on_site_list=[ None ], cabin=None, most_emitters=None, most_present=None ): #, section_no=None):
    cluster_key_list = self.cluster_key_list[ : ]
#    cluster_key_list.remove( 'co2eq' )

    md_txt = "" 
    for cluster_key in cluster_key_list:
      if mode in [ 'flight', 'distance' ]:  
        most_present=None  
        subsection_title = f"CO2eq Distribution by `{cluster_key}` with {self.co2eq_method_list}"  
      elif mode == 'attendee':  
        most_emitters=None  
        subsection_title = f"Attendee Distribution by `{cluster_key}`"  
      md_txt += f"\n\n### {subsection_title}\n\n" 
      for on_site in on_site_list:
        md_txt += self.fig_svg_md( suffix, mode, cabin=cabin, 
                cluster_key=cluster_key, on_site=on_site,\
                most_emitters=most_emitters, most_present=most_present )
    return md_txt 



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
      cell_list.append( f"<a href='{home_url}' style='font-size: 10px; {cell_style}'>&#127968;</a>" )
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
    banner="",
    toc=True, output_md="index.md",
    most_emitters=None,
    most_present=None ):

  
    md_file = os.path.join( self.output_dir, output_md )

    co2eq_dist = 'flight' in mode_list or 'distance' in mode_list
    atten_dist = 'attendee' in mode_list
    if atten_dist and co2eq_dist :
      title = f"{self.name} Remote Participation" # (CO2 and Attendees)"  
      txt = f"This page estimates the remote participation CO2 emitted for {self.name} as well as the distribution of the attendees of {self.name}."
    elif atten_dist and not co2eq_dist: 
      title = f"{self.name}: Remote Attendance Ratio"  
      txt = f"This page displays the distribution of the attendees of {self.name}."
    elif not atten_dist and co2eq_dist :
      title = f"{self.name}: Remote Ratio of CO2 Emissions"  
      txt = f"This page estimates the CO2 emitted according for {self.name}."
    else: 
      raise ValueError( f"only ")
 
    header = self.header_md( title, banner=banner, toc=toc, md_file=md_file)
    if header is None:
      return None
#    md_txt =f"# {title} \n\n{banner}\n\n{toc_md}\n\n{txt}\n\n"
    md_txt =f"{header}\n\n{txt}\n\n"
    md_txt += """In term of CO2eq emissions, the most effective way to reduce these emissions is to 'not flight'. 'not flying' is represented by 'remote' participation in our current model. This comes with some simplifications, but remains overall quite realistic with the current behavior of 'flying by default' and the data we have. 

Unless behaviors changes, the CO2eq Remote Ratio estimates the ratio of CO2eq being offset by 'remote' participation over the CO2eq if everyone where participating 'onsite'.
The Attendee Remote Ratio estimates the number of 'remote' participants over the total number of participant.  

Both Ratios provide indicators of a net-zero policy. The CO2 Remote Ratio measures its efficiency while the Attendee Remote Ratio indicates the level of acceptance of remote participation which can also be translated as the level of conciousness of a more sustainable meeting.  
This could be seen as an indicator of the sustainability policy put in place which is usually designated as net-zero policy.

Currently the CO2 estimation is considering that everyone flies unless the distance is too short - in which case the emission is set to zero. Unfortunately, the behavior of flying by default is pretty much what we can observe for ICANN and IETF meetings. As result, the current model do not reflect the efforts of someone taking the train over a long distance. It also does not consider someone taking the train even for a shorter distance when there is a flight between the meeting location and the capital of the city the participant is coming from. We can only encourage meeting organizer to enable participants to indicate the type of transport taken to go to the meeting.   


A meeting MAY propose attendee to participate remotely, but such participation is only effective if the propose remote participation experience matches the expectation or contains of the remote participants. In some meetings, this means for example, the ability to ask questions and queuing in a list that is completely forgotten.
The main argument for on site participation is the ability to 'socialize'. This makes remote attendance especially difficult when the main purpose of attendee is to meet colleagues as opposed to exchange information.  
There is a critical ratio to meet in order to make remote participation effective. As long as critical ratio has not been met, remote participant are still 'second class' participants. 

Note that in some cases, attendees are considered as 'remote' when they registered as 'remote' all other categories are considered as non remote and are assimilated to 'on-site' users. This includes for example users that are some times indicated as 'not-arrived'. The reasoning is that such attendee was expected to attend 'on-site'. Then, it is difficult to estimate if he effectively has not travelled or if he is attending as a remote user. Note also that these attendee does not represent a huge portion of the attendees. 
"""
    txt_co2 = """The Remote Ratio expressed with CO2 emission indicates the ratio of CO2 mission being offset by remote participants versus the CO2 emissions associated to the meetings. Such metric is a direct estimation of a successful net-zero strategy as it estimates the CO2eq offset over the total CO2eq emitted. """

    txt_attend = """The Remote Ratio expressed with attendee numbers reflects the acceptance of the remote participation and its evolution.
Acceptance of Remote participation is probably what leadership should focus on to develop a sustainable meeting. """

    for mode in mode_list:
      if mode in [ 'flight', 'distance' ]:
        for cabin in cabin_list :
          md_txt += f"\n\n## CO2 Remote Ratio for '{mode}' mode in cabin {cabin} for {self.name}\n\n"
          md_txt += txt_co2
          md_txt += self.md_subsection_txt( 'remote_ratio', mode,
                  cabin=cabin, most_emitters=most_emitters, 
                  most_present=most_present )
      elif mode == 'attendee':
        md_txt += f"\n\n## Attendee Remote Ratio for {self.name}\n\n"
        md_txt += txt_attend
        md_txt += self.md_subsection_txt( 'remote_ratio', mode,
                most_emitters=most_emitters, 
                most_present=most_present ) #, secti

    md = co2eq.md.MdFile( md_txt )
    md.number_sections()
    md.save( md_file )


  def highlights_md( self, mode_list=[ 'flight' , 'attendee' ], 
          cabin_list=[ 'AVERAGE' ],
          on_site_list=[ None, True, False],
          banner="",
          toc=True, output_md="index.md", 
          most_present=None, most_emitters=None ):   
    
    md_file = os.path.join( self.output_dir, output_md )
    title = f"{self.name} Highlights" 
    md_txt = self.header_md( title, banner=banner, toc=toc, md_file=md_file)
    if md_txt is None:
      return None

    md_txt += f"This page provides some selected highlights for {self.name} to depict the evolution of the CO2eq emissions  as well as the perspectives in term of offset.\n\n"
    md_txt += "## CO2 Offset\n\n"

    if 'presence' in self.cluster_key_list and\
        cabin_list != [] and\
        'flight' in mode_list and\
        None in on_site_list:
      if 'AVERAGE' in cabin_list:
        cabin = 'AVERAGE'
      else: 
        cabin = cabin_list[ 0 ]

      mode = 'flight'
#      on_site = None
      md_txt += f"""The figure below depicts the evolution of the CO2eq associated by the meeting of the various meetings. The effective CO2eq is represented by the CO2eq emissions associated to 'on-site' participants. CO2eq emissions associated to 'remote' participants reflects the portion of CO2eq being offset. The total amount of CO2eq reflects a metric that can reveals an increase/decrease of participation and the evolution associated to 'on-site' and 'remote' participations. When a net-zero strategy has been defined, it is expected to favor 'offsetting' CO2eq and this figure measures how successful that strategy is.   

The CO2eq emissions are estimated using different methods ({self.co2eq_method_list}) for the flight cabin {cabin}. Please check [Distributions](./distributions.html) for additional CO2eq distributions.\n\n
"""
      md_txt += self.fig_svg_md( 'distribution', mode, cabin=cabin, 
             cluster_key='presence' ) 

      md_txt += """The Picture below depicts the Remote Ratio of the emissions being offset over the total emissions of the meeting. Please check [Remote Ratio](./remote_ratio.html) for additional CO2eq distributions.\n\n"""
      md_txt += self.fig_svg_md( 'remote_ratio', mode, cabin=cabin, 
          cluster_key='presence', most_emitters=most_emitters )
      if 'organization' in self.cluster_key_list:
        cluster_key = 'organization' 
      elif 'country' in self.cluster_key_list: 
        cluster_key = 'country'
      else:
        cluster_key = None

      if cluster_key is not None:
        md_txt += f"""The figure below depicts the Remote Ratio of the emissions being offset per {cluster_key}. The overall performance in term of offsetof a meeting may reflect the performance of its main participants or might be influenced by its participants. The figures shows the evolution of the offset Remote Ratio for the {most_emitters} most contributors."""

      md_txt += self.fig_svg_md( 'remote_ratio', mode, cabin=cabin, 
          cluster_key=cluster_key, most_emitters=most_emitters )

    if 'presence' in self.cluster_key_list and\
        cabin_list != [] and\
        'attendee' in mode_list and\
        None in on_site_list:
      mode = 'attendee'
#      on_site = None
      md_txt += f"\n## Remote Participation\n\n"

      md_txt += f"The figure below depicts the distribution between 'remote' and 'on-site' participants. The graph here reflects the how participants are inclined to participate 'remotely' and thus avoids the emissions associated to flying. Please check [Distributions](./distributions.html) for additional Attendee distributions.\n\n"""
      md_txt += self.fig_svg_md( 'distribution', mode, cluster_key='presence' ) 
    
      md_txt += """The Picture below depicts the Ratio of Remote participants  over the meeting total number of participants. Please check [Remote Ratio](./remote_ratio.html) for additional Remote Ratio distributions.\n\n"""
      md_txt += self.fig_svg_md( 'remote_ratio', mode, 
          cluster_key='presence' )

      if 'organization' in self.cluster_key_list:
        cluster_key = 'organization' 
      elif 'country' in self.cluster_key_list: 
        cluster_key = 'country'
      else:
        cluster_key = None

      if cluster_key is not None:
        md_txt += f"""The figure below depicts the Remote Ratio of the remote participants per {cluster_key}. The overall performance in term of offset of a meeting may reflect the performance of its main participants or might be influenced by its participants. The figures shows the evolution of the offset Remote Ratio for the {most_present} most contributors."""
        md_txt += self.fig_svg_md( 'remote_ratio', mode, 
          cluster_key=cluster_key, most_present=most_present )

    md = co2eq.md.MdFile( md_txt )
    md.number_sections()
    md.save( md_file )

  def www( self,\
          mode_list=[ 'flight', 'attendee'],\
          cabin_list=[ 'AVERAGE' ], most_emitters=20, most_present=20 ):
    """plots and generates the md for the web site

    plot_distribution considers on_site_list=[ None, True, False] )
    so this is what we are considering here. 
    """
    if 'presence' in self.cluster_key_list :
      on_site_list=[ None, True, False] 
      dist_md = 'distributions.md'
    else:
      on_site_list=[ None ]
      dist_md = 'index.md'

    banner = self.md_banner( )
    ## When 'co2eq' is computed and presence is mentioned generating 
    ## figures and text for ratio. 

    ## generating the figures for the meeting_list.
    ## When 'presence' is a cluster_key, remote_ratio figures are generated
    self.plot_distribution( mode_list=mode_list, cabin_list=cabin_list )
    if 'presence' in self.cluster_key_list :
      self.plot_co2eq_remote_ratio( show=False, print_grid=False, most_emitters=most_emitters )
      ## ratio md pages are plotting everything.
      if most_emitters is not None:
        self.plot_co2eq_remote_ratio( show=False, print_grid=False, most_emitters=None )
        
      self.plot_attendee_remote_ratio( show=False, print_grid=False, most_present=most_present )
      if most_present is not None:
        self.plot_attendee_remote_ratio( show=False, print_grid=False, most_present=None )
          
      ## generating figures for all meetings
    for m in self.meeting_list:
      m.plot_distribution( mode_list=mode_list, cabin_list=cabin_list )

    ## generating the md file
    ## When 'presence' is a cluster_key, remote_ratio figures are generated
    self.dist_md( mode_list=mode_list, cabin_list=cabin_list,\
             on_site_list=on_site_list, banner=banner, 
             output_md=dist_md )
    if 'presence' in self.cluster_key_list :
      self.ratio_md( mode_list=mode_list, cabin_list=cabin_list, 
        #on_site_list=on_site_list, 
        banner=banner, toc=True,
        output_md="remote_ratio.md", most_emitters=most_emitters,
        most_present=most_present )
      self.highlights_md( mode_list=mode_list, cabin_list=cabin_list, 
        on_site_list=on_site_list, banner=banner, toc=True,
        output_md="index.md", most_emitters=most_emitters,
        most_present=most_present )
      ## generating md files for all meetings
    for m in self.meeting_list:
      m.dist_md( mode_list=mode_list, cabin_list=cabin_list,
             on_site_list=on_site_list, banner=banner )
