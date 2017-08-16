import os
from marisa_trie import Trie
from config.Config import DATA_FILES_PATH, URL_PREFIX
from quick.util.CommonFunctions import ensurePathExists
import third_party.safeshelve as safeshelve

class GSuiteTrackCache(object):
    CACHE_DIRECTORY = os.path.join(DATA_FILES_PATH, 'GSuiteTrackCache')
    URI_PREFIXES_FN = CACHE_DIRECTORY + os.sep + 'UriPrefixesToCache.txt'
    CACHE_SHELVE_FN = os.path.join(CACHE_DIRECTORY, \
                      (URL_PREFIX[1:] if URL_PREFIX.startswith(os.path.sep) else URL_PREFIX), \
                      'GSuiteTrackCache.shelve')
    
    PROTOCOL = 0

    def __init__(self):
        if not os.path.exists(self.URI_PREFIXES_FN):
            ensurePathExists(self.URI_PREFIXES_FN)
            open(self.URI_PREFIXES_FN, 'w')

        if not os.path.exists(self.CACHE_SHELVE_FN):
            ensurePathExists(self.CACHE_SHELVE_FN)

        cache = self._openShelve('c')
        cache.close()
        
        prefixList = [line.strip() for line in open(self.URI_PREFIXES_FN, 'r')]
        self._uriPrefixes = Trie(prefixList)

    def _openShelve(self, mode):
        return safeshelve.open(self.CACHE_SHELVE_FN, mode, protocol=self.PROTOCOL)
        
    def isCached(self, gSuiteTrack):
        cache = self._openShelve('r')
        isCached = gSuiteTrack.uri in cache
        cache.close()
        return isCached
        
    def getCachedGalaxyUri(self, gSuiteTrack):
        cache = self._openShelve('r')
        uri = cache[gSuiteTrack.uri]
        cache.close()
        return uri
        
    def shouldBeCached(self, gSuiteTrack):
        uri = unicode(gSuiteTrack.uri)
        return len(self._uriPrefixes.prefixes(uri)) > 0

    def cache(self, gSuiteTrack, galaxyUri):
        cache = self._openShelve('c')
        cache[gSuiteTrack.uri] = galaxyUri
        cache.close()

GSUITE_TRACK_CACHE = GSuiteTrackCache()
