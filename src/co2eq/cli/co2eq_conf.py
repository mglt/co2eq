import os

conf_dir = os.expanduser( ~/.config/co2eq/ )
cache_dir = os.expanduser( ~/.cache/co2eq/ )

if os.path.isdir( conf_dir) is False:
  create .config/co2eq/

env = os.path.join( conf_dir, 'env' )

if os.path.isfile( env_file ):
  print( File already exists, Please remove if you want to replave by default.)
else:  
  cp data/conf/env 

if os.path.isfile( ISO ):
  print( File already exists, Please remove if you want to replave by default.)
else:  
  cp data/conf/ISO

Do you wnat to retrieve cache from github.com ?
wget 

