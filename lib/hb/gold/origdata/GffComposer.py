from urllib import quote
from collections import OrderedDict, namedtuple
from gold.origdata.FileFormatComposer import FileFormatComposer, MatchResult
from gold.track.TrackFormat import TrackFormat
from gold.util.CommonFunctions import getStringFromStrand

ColumnInfo = namedtuple('ColumnInfo', ['colIdx', 'defaultVal'])

class GffComposer(FileFormatComposer):
    FILE_SUFFIXES = ['gff', 'gff3']
    FILE_FORMAT_NAME = 'GFF'

    _GFF_COLUMNS_LIST = [('chr', 0, ''), \
                         ('source', 1, '.'), \
                         ('type', 2, '.'), \
                         ('start', 3, '0'), \
                         ('end', 4, '0'), \
                         ('val', 5, '.'), \
                         ('strand', 6, '.'), \
                         ('phase', 7, '0'), \
                         ('attributes', 8, '.')]

    def __init__(self, geSource):
        FileFormatComposer.__init__(self, geSource)
        self._gffColumnsDict = OrderedDict([(colName, ColumnInfo(colIdx, defaultVal)) for \
                                            colName, colIdx, defaultVal in self._GFF_COLUMNS_LIST])

    @staticmethod
    def matchesTrackFormat(trackFormat):
        trackFormatName = ''
        if trackFormat.getValTypeName() in ['Number', 'Number (integer)']:
            trackFormatName += 'valued '

        trackFormatName += 'segments'

        return MatchResult(match=trackFormat.isInterval() and not trackFormat.isDense(), \
                           trackFormatName=trackFormatName)

    # Compose methods

    def _compose(self, out):
        print >>out, '##gff-version 3'

        gffColumnsList = list(self._gffColumnsDict.iteritems())

        numCols = 9
        for ge in self._geSource:
            cols = [''] * numCols
            for i in range(numCols):
                colName, colInfo = gffColumnsList[i]

                try:
                    value = getattr(ge, colName)
                except AttributeError:
                    value = None

                if colName == 'source':
                    if value is not None and '\t' in value: #from old source memmaps
                        value = '.'
                if colName == 'type':
                    value = self._composeTypeColumn(ge, value)
                if colName == 'start':
                    value = value + 1
                elif colName == 'val':
                    value = self._composeValColumn(ge, value)
                elif colName == 'strand':
                    value = getStringFromStrand(value)
                elif colName == 'attributes':
                    if value is None:
                        attrs = ''
                        if ge.id is not None:
                            attrs += 'ID=%s;' % quote(ge.id, safe=' |')
                        if hasattr(ge, 'name'):
                            attrs += 'Name=%s;' % quote(ge.name, safe=' |')
                        if attrs != '':
                            value = attrs

                cols[i] = value if value is not None else colInfo.defaultVal

            print >>out, '\t'.join([str(x) for x in cols])

    def _composeTypeColumn(self, ge, value):
        return value

    def _composeValColumn(self, ge, value):
        try:
            return self._commonFormatNumberVal(value)
        except:
            return '.'

class CategoryGffComposer(GffComposer):
    FILE_SUFFIXES = ['category.gff']
    FILE_FORMAT_NAME = 'Category GFF'

    @staticmethod
    def matchesTrackFormat(trackFormat):
        return MatchResult(match=trackFormat.isInterval() and not trackFormat.isDense() and
                                 trackFormat.isValued('category'), \
                           trackFormatName='valued segments')

    def _composeTypeColumn(self, ge, value):
        return ge.val

    def _composeValColumn(self, ge, value):
        try:
            return self._commonFormatNumberVal(float(ge.score))
        except:
            return '.'
