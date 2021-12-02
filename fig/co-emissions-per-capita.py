import json
import matplotlib.pyplot as plt
from math import ceil

fig_file = 'co-emissions-per-capita-chart.svg'

json_data = []

with open( './co-emissions-per-capita.txt', 'rt', encoding='utf8' ) as f:
  for line in f.readlines() :
    l = line.split()
    ## skip header and empty line
    if  len( l ) == 0:
      continue
    if l[ -1 ] != 't':
      continue
    co2 = float( l[ -2 ] )
    country = ''
    for txt in l[:-2]:
      country = f"{country} {txt}"
    json_data.append( { 'country' : country, 'co2' : co2 } )

data = sorted( json_data, key=lambda item : float( item[ 'co2' ] ), reverse=True )

print( f"len(data): {len( data )}" )
data = [ item for item in data if item[ 'co2' ] > 2.8 ]
print( f"len(data): {len( data )}" )

x = range( len(data) )
y = [ item[ 'co2'] for item in data]
y_ietf1 = [ 2.49 for item in data ]
y_ietf2 = [ 2.49 * 2 for item in data ]
y_ietf3 = [ 2.49 * 3 for item in data ]

fig = plt.figure( figsize=(30, 10 ) )
plt.plot( x, y, label='capita')
plt.plot( x, y_ietf1, label='1 IETF' )
plt.plot( x, y_ietf2, label='2 IETF' )
plt.plot( x, y_ietf3, label='3 IETF' )

#plt.title("")
plt.ylabel("CO2 per Capita (Tonne)" )
plt.xlabel("Cities" )
plt.xticks( x, [ item[ 'country' ] for item in data], rotation = 'vertical')
yticks = range( ceil( max( y ) ) ) 
plt.yticks( [ y for y in yticks if y%5  == 0 ])
plt.legend()
plt.gca().margins(x=0)
plt.tight_layout()
fig.subplots_adjust(bottom=0.5)
plt.savefig( fig_file, bbox_inches='tight' )
plt.show()

