import matplotlib.pyplot as plt
from math import floor

starting_year = 2015
ending_year = 2050
fig_file = 'meeting_strategies.svg' 

scenario_list  = [ { 'name' : 'no pandemic', 
                    'pre24_growth' : 0, 
                    'post24_growth' : 0, 
                    'color' : 'red', 
                    'warming effect' : 0.1 }, 
                   { 'name' : 'back to nomal', 
                     'pre24_growth' : 0.16, 
                     'post24_growth' : 0.03, 
                     'color' : 'orange', 
                     'warming effect' : 0.09 }, 
                   { 'name' : 'zero long term growth', 
                     'pre24_growth' : 0.13, 
                     'post24_growth' : 0, 
                     'color' : 'yellow', 
                     'warming effect' : 0.06 },
                   { 'name' : 'long term decline', 
                     'pre24_growth' : 0.1, 
                     'post24_growth' : -0.025, 
                     'color' : 'green', 
                     'warming effect': 0.04 } ]

def scenario_y( scenario ):
  """implements the models of https://iopscience.iop.org/article/10.1088/1748-9326/ac286e """
  year_list = []
  y = []
  for year in range( ending_year - starting_year + 1):
    year = starting_year + year 
    year_list.append( year )
    if scenario[ 'name' ] == 'no pandemic':
      y.append ( 3 )
    else:
      if year <= 2019:
        y.append( 3 )
      elif year <= 2020:
        y.append( 0 )
      elif year <= 2021:
        y.append( 3 * (1 - 0.45 ) )
      ## increas of 10 % per year untill 2024
      elif year <= 2024:
        y.append( min( y[ -1 ] * ( 1 + scenario[ 'pre24_growth' ] ) , 3 ) )
      else :
        ## decrease of -2.5% per year 
        y.append( min( y[ -1 ] * ( 1 + scenario[ 'post24_growth' ] ) , 3 ) )
  y_floor = [ floor(i) for i in y ]
  return y, y_floor, year_list

for scenario in scenario_list:
  y, y_floor, year_list = scenario_y( scenario )
  label = f"{scenario[ 'name' ]} ( +{scenario[ 'warming effect' ]} °C )" 
  plt.plot( year_list, y_floor, color=scenario[ 'color' ], label=label )
  plt.plot( year_list, y, linestyle='dashed', color=scenario[ 'color' ] )

x_label = []
for y in year_list:
  if  y%5 == 0:
    x_label.append( y )
  x_label.append( '' )
  
plt.xticks( year_list, x_label )
plt.xlabel( 'years' )
plt.ylabel( 'Number of IETF meeting per year' )
plt.legend()
plt.savefig( fig_file, bbox_inches='tight' )
plt.show()



