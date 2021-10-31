from conf import CONF
import matplotlib.pyplot as plt
from co2eq.flight_utils import Flight

f = Flight( conf=CONF )

x = [ i * 5 for i in range( 8000) ]
y = [ f.co2eq_myclimate2018( i ) for i in x ] 
fig, ax = plt.subplots( )
ax.plot( x, y )
plt.show()


