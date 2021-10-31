import os
from os.path import getsize, exists, dirname
import json
import gzip

class JCache:
  """ implements a cache in JSON objects.

  When your program is likely to request multiple times a JSON object
  to a external server, JCacheList limits the number of request by
  caching the JSON object and only requests the object when it has
  not been already requested.
  The cache also survives multiple installations by keeping the cache
  content into the a file (data).

  This class is expected to be generic and re-used by other more specific databases.
  The principle are:
    - the cache is loaded from a file located at path.
    - cached objects are stored in a list.

  Arg:
    cache_path: the path of the data file that contains the cached objects.
    This file is read at the instantiation of JCacheList

  """
  def __init__( self, cache_path:str ):
    self.cache_path = cache_path
    ## checking for non empty file to avoid json load raising error
    try:
      if getsize( cache_path ) > 0:
        with gzip.open( cache_path, 'rt', encoding="utf8" ) as f:
          self.cache = json.loads( f.read() )
      else:
        self.cache = self.empty_cache( )
    except FileNotFoundError:
      ## create the directory so the file can be created.
      cache_dir = dirname( cache_path )
      if exists( cache_dir ) is False:
        os.makedirs( cache_dir )
      self.cache = self.empty_cache( )
    self.cache_init()

  def empty_cache( self ):
    """ returns the empty structure of teh cache """
    return []

  def cache_init( self ):
    """ specific actions performed at the initialization """
    pass

  def cache_read_all( self, **kwargs )-> list:
    """ returns all matching elements of the cache """

  def cache_read_first( self, **kwargs ):
    """ return teh first matchin element in the cache

    This function is defined in JCache by default and based on cache_read.
    This function is mostly useful when providing the first match provides
    significant performance advanatge over returning all elements.
    """
    match_list = self.cache_read_all(  **kwargs )
    if len( match_list ) != 0:
      match_item = match_list[ 0 ]
    else:
      match_item = None
    return match_item

  def cache_miss( self, **kwargs):
    """ define action to perform in cas eof cache miss """
    new_item = self.retrieve_item( **kwargs )
##    match_list.append( new_item )
    if new_item is not None:
      self.cache.append( new_item )
      with gzip.open( self.cache_path, 'wt', encoding="utf8"  ) as f:
        f.write( json.dumps( self.cache, indent=2 ) )
    return new_item

  def retrieve_item( self, **kwargs):
    """ retrieve the object when a cache miss occurs """
    return None

  def get_all( self, **kwargs  ) -> list:
    """ perform local and remote lookup in case of cache miss """
    match_list = self.cache_read_all( **kwargs )
    if len( match_list ) == 0:
      return [ self.cache_miss( **kwargs ) ]
    return match_list

  def get_first( self, **kwargs ):
    match_item = self.cache_read_first( **kwargs )
    if match_item is None :
      return self.cache_miss( **kwargs )
    return match_item




class JCacheList( JCache ):
  """ implements a cache which is a list of JSON objects. """
##  def __init__(self, cache_path:str ):
##    super().__init__( cache_path )

  def empty_cache( self ):
    """ returns the empty structure of teh cache """
    return []

  def cache_read_first( self, **kwargs) :
    """ returns the first object of the cache list where all key, value match.

    When a cache miss occurs, a specific action is performed.
    A typical specific action includes retrieving the object from the
    internet and cache it for further use.
    Because only the first match is returned, this is useful when we know the
    key value guarantee uniqueness of the object or that objects that match
    are equivalent.
    """
    match_item = None
    for item in self.cache:
      for k,v in kwargs.items():
        try:
          if item[ k ] != v:
            break
        except KeyError:
          break
      else: ## all k,v matches, and no break
        match_item = item
        ## first match
        break
      continue ## if break occurs in the inner loop this blocks tells to continue
    return match_item

  def cache_read_all( self, **kwargs ):
    """ return all objects of the cache that match all key values.
        When a cache miss occurs no further actions are performed.

    """
    match_list = []
##    print(" cache_read_all : len( self.cache) %s"%len( self.cache) )
    for item in self.cache:
      for k,v in kwargs.items():
        try:
          if item[ k ] != v:
            break ## we want to go to next item
        except KeyError:
          break
      else: ## all k,v matches, and no break, this block is executed
        match_list.append( item )
      continue ## if break occurs in the inner loop this blocks tells to continue
    return match_list

  def retrieve_item(self, **kwargs):
    """ returns a new value """
    pass

class JCacheDict( JCache ):
## for JCacheDict
#    except KeyError:
#      self.cache[ args ] = self.retrieve_new_value( *args )
#      with open( self.path, 'w', encoding="utf8" ) as f:
#         json.dumps( self.cache, indent=2 )
#    return self.cache[ args ]

  def empty_cache( self ):
    """ returns the empty structure of teh cache """
    return {}

  def kwarg_to_key( self, **kwargs ):
    pass

  def cache_read_all( self, **kwargs ) -> list:
    key = self.kwarg_to_key( **kwargs )
    try :
      match_list = [ self.cache[ key ] ]
    except :
      match_list = []
    return match_list

  def cache_miss( self, **kwargs):
    """ define action to perform in cas eof cache miss """
    new_item = self.retrieve_item( **kwargs )
    if new_item is not None:
      self.cache[ self.kwarg_to_key( **kwargs ) ] =  new_item
##      print("cache: %s"%self.cache )
      with gzip.open( self.cache_path, 'wt', encoding="utf8" ) as f:
        f.write( json.dumps( self.cache, indent=2 ) )
    return new_item

  def retrieve_item(self, **kwargs):
    """ returns a new value """
    pass
