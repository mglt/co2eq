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
    offset=None, \
    subfig_title_list=None, \
    fig_title="",\
    html_file_name=None, 
    svg_file_name=None, 
    fig_height=600,
    fig_width=None):
    ## organization of the dimensions 
    ## fig_width set to 1500 seems fine for 6 histograms with legends
    ## 
    cols = len( subfig_list )
    if fig_width is None:
      fig_width = 1500 / 6 * cols
    ## each columns is divided:
    ## - 1/9 for the bar
    ## - 8/9 for the legend
    n = 9 
    barwidth = 1 / ( n * cols ) 
    hspace = (n - 1) / ( n * cols )
    ## offset is how much the legend is offsets to 
    ## be alonside the bar. 
    if offset is None:
      offset = 1.32 * barwidth
    else:
      offset = offset * barwidth

    ## building legends
    legend_layout = {}
    legend_name_list = []
    for i, subfig in enumerate(subfig_list):
      if i + 1 >= 2:  
        legend_name = f"legend{i+1}" 
      else:
        legend_name = "legend"
      legend_name_list.append( legend_name )  
      legend_layout[ legend_name ] = { 
#        'title' : "",
        'y' : 1,
        'x' :  offset + barwidth +  i * ( hspace + offset + barwidth ),
#        'bgcolor' : "orange" # usefull to determine the offset
        }    
    ## building subfigure
    self.fig = plotly.subplots.make_subplots( rows=1, cols=cols, \
            subplot_titles= subfig_title_list,
            horizontal_spacing = hspace,
            column_widths=[ barwidth for i in range( cols ) ]
            )
    for i, subfig in enumerate(subfig_list):
      for trace in range(len(subfig["data"])):
        subfig["data"][trace][ 'legend' ] = legend_name_list[ i ]
        self.fig.add_trace( subfig["data"][trace], row=1, col=i+1 )
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



