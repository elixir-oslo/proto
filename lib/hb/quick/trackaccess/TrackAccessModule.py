#import os
#import sqlite3

from gold.util.CustomExceptions import AbstractClassError
#from proto.hyperbrowser.StaticFile import StaticFile
#from quick.util.CommonFunctions import ensurePathExists
from collections import namedtuple
#from itertools import chain

class TrackAccessModule(object):
    def getValueListWithCounts(self, attribute, prevSelected):
        raise AbstractClassError()

    #def buildStructuredIndex(self):
    #    fullIndex = dict([(el.uniqueFileId, el.tagDict) \
    #        for el in self._structIndexElementIterator()])
    #
    #    allTags = list(set(chain(*(tagDict.keys() for tagDict in fullIndex.values()))))
    #    assert len(allTags) > 0
    #
    #    c = self._getStructuredIndexConnection()
    #
    #    c.execute("DROP TABLE idx")
    #
    #    c.execute("CREATE TABLE idx (file_id text, %s)" % \
    #               ', '.join(['%s text' % x for x in allTags]))
    #
    #    for uniqueFileId,tagDict in fullIndex.iteritems():
    #        rowVals = ["'%s'" % tagDict[tag] if tag in tagDict else "NULL" for tag in allTags]
    #        c.execute("INSERT INTO idx VALUES ('%s', %s)" % (uniqueFileId, ', '.join(rowVals)))
    #
    #    c.commit()
    #    c.close()
    #
    #def getAllTags(self):
    #    c = self._getStructuredIndexConnection()
    #
    #    res = c.execute("PRAGMA table_info('idx')").fetchall()
    #    res = [str(x[1]) for x in res]
    #    c.close()
    #
    #    return res
    #
    #def getAllValues(self, tag):
    #    assert isinstance(tag, basestring)
    #
    #    if len(tag) == 0:
    #        return []
    #
    #    c = self._getStructuredIndexConnection()
    #
    #    res = c.execute("SELECT %s from idx WHERE %s IS NOT NULL" % (tag,tag)).fetchall()
    #    res = [str(x[0]) for x in res]
    #
    #    c.close()
    #
    #    return res
    #
    #def searchStructured(self, searchQueryDict):
    #    assert all(isinstance(key, basestring) & isinstance(val, basestring) for key,val in searchQueryDict.iteritems())
    #    if len(searchQueryDict) == 0:
    #        return []
    #
    #    c = self._getStructuredIndexConnection()
    #
    #    queryStr = ' AND '.join('%s == %s' % (tag, val) for tag,val in searchQueryDict.iteritems())
    #    res = c.execute("SELECT file_id from idx WHERE %s" % queryStr).fetchall()
    #    res = [str(x[0]) for x in res]
    #
    #    c.close()
    #
    #    return res
    #
    #def _structIndexElementIterator(self):
    #    raise AbstractClassError
    #
    #def _getModuleIndexDirectory(self):
    #    return StaticFile(self.STATIC_FILE_PREFIX + [self.TRACK_ACCESS_MODULE_ID]).getDiskPath()

StructIndexElement = namedtuple('StructIndexElement', ['uniqueFileId', 'tagDict'])
