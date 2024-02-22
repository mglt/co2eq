import kaleido ## to be able to export
import plotly.graph_objects 
import plotly.subplots


class OneRowSubfig:
  """
   
    Plotting a subset of figures using plotlyexpress is described here:
    from https://stackoverflow.com/questions/56727843/how-can-i-create-subplots-with-plotly-express
    How to add legend is discussed here:
    https://stackoverflow.com/questions/64778677/plotly-adding-legend-to-subplot
    https://plotly.com/python/legend/
    https://community.plotly.com/t/plotly-express-legend-grouping/39796
    The motivation to use plotly.express is that it provides 
    a high level API. The output is an graphical object to 
    which we apply lower level operations. 
    In our case all histograms are subfigures generated via
    plotlyexpress. 
    Each of these sub figures are manually added to the 
    general figure. That is each trace (i.e.'line') or any
    sort of information of the sub figure data subfig[ 'data' ] 
    is added to general figure with an indication of the sub 
    figure position in the general figure (row, col). 
    This is performed via the fig.add_trace function. 
    To handle individual legend, on needs to indicate 
    the legend associated to each subfigure. 
    This is performed by using a legend name 'legend', 
    legend2', 'legend3'..
    These legend tags are then associated parameters like 
    the position and provided to the geneal figure's layout.

    https://plotly.com/python/subplots/

  """
  def __init__( self, \
    subfig_list, \
    legend_offset=0, \
#    subfig_title_list=None, \
    fig_title="",\
    html_file_name=None, 
    svg_file_name=None, 
    fig_height=600,
    fig_width=1500,
    column_widths=None,
    row_heights=None,
    x_title=None,
    y_title=None,
    shared_xaxes=False,
    shared_yaxes=False,
    vertical_spacing=None, 
    horizontal_spacing=None, 
    print_grid=False, 
    show=False):


    rows = 1
    cols = len( subfig_list )
    if horizontal_spacing is None:
      horizontal_spacing = 0.2 #/ cols
    if vertical_spacing is None:
      vertical_spacing = 0.3 #/ rows
    if isinstance( legend_offset, ( int, float ) ):
      legend_offset = [ legend_offset  for i in range( cols ) ]  
    ## needed becaus eof teh lengend offset
    if column_widths is None:
      column_widths  = [ 1 / cols  for i in range( cols ) ]
    ## building legends, title_list
    ## legends for each subfigure are manually put in the global figure layout.
    ## titles for each subfigures are handled by the make_subplots, so we only 
    ## extract them to pass it as an argument.
    legend_layout = {}
    legend_name_list = []
    title_list = []
    print( f"column_widths: {column_widths}" )
    print( f"legend_offset: {legend_offset}" )
    for i, subfig in enumerate(subfig_list):
      if i + 1 >= 2:  
        legend_name = f"legend{i+1}" 
      else:
        legend_name = "legend"
      legend_name_list.append( legend_name )  
      ## legend is placed offset considering the boundary of the column
      ## margin of teh figure is expected to be 0.2 
      ## 
      total_legend_offset =  0.1 + column_widths[ i ] - horizontal_spacing + legend_offset[ i ]
      for j in range( i ):
        total_legend_offset += 0.1 + column_widths[ j ] 
      legend_layout[ legend_name ] = { 
#        'title' : "",
        'y' : 1,
#        'x' :  legend_offset + barwidth +  i * ( hspace + legend_offset + barwidth ),
        'x' :  total_legend_offset,
#        'bgcolor' : "orange" # usefull to determine the legend_offset
        'traceorder' : 'grouped' 
        }  
      if print_grid is True:
        legend_layout[ legend_name ][ 'bgcolor' ] = "orange" 
      title_list.append( subfig[ 'layout' ][ 'title' ][ 'text' ] )  
    ## building subtitle_list

    ## building subfigure
    self.fig = plotly.subplots.make_subplots( 
            rows=1, 
            cols=cols,
            subplot_titles=title_list,
            horizontal_spacing=horizontal_spacing,
            vertical_spacing=vertical_spacing,
            print_grid=print_grid,
            column_widths=column_widths,
            row_heights=row_heights,
            x_title=x_title,
            y_title=y_title,
            shared_xaxes=shared_xaxes,
            shared_yaxes=shared_yaxes,
            )
    for i, subfig in enumerate(subfig_list):
      xaxis_title_text = subfig[ 'layout' ][ 'xaxis' ][ 'title' ][ 'text' ]
      yaxis_title_text = subfig[ 'layout' ][ 'yaxis' ][ 'title' ][ 'text' ]
      for trace in range(len(subfig["data"])):
        subfig["data"][trace][ 'legend' ] = legend_name_list[ i ]
        self.fig.add_trace( subfig["data"][trace], row=1, col=i+1 )
      self.fig.update_xaxes( title_text=xaxis_title_text, row=1, col=i+1 )  
      self.fig.update_yaxes( title_text=yaxis_title_text, row=1, col=i+1 )  
    ## barmode applies to all subplots
    self.fig.update_layout(
      height=fig_height,
      width=fig_width,
      barmode='relative',
      title= { 'text': fig_title, 'automargin': True, 'xref': 'container', 'y':0.95 },
      margin={ 'l':0, 'r':0 }, 
      font_family="Rockwell",
      showlegend=True
            )
    for legend_name in legend_name_list:
      self.fig[ 'layout' ][ legend_name ] = legend_layout[ legend_name ]
    if html_file_name is not None:
      self.fig.write_html( html_file_name )
    if svg_file_name is not None:
      self.fig.write_image( svg_file_name )
    if show is True:
      self.fig.show()


