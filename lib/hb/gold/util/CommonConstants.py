from collections import OrderedDict

BINARY_MISSING_VAL = -1

RESERVED_PREFIXES = OrderedDict([(x, None) for x in ('start', 'end', 'val', 'strand', 'id', 'edges', 'weights')])

TRACK_TITLES_SEPARATOR = '|||'

STATISTIC_CLASS_NAME_TO_NATURAL_NAME_DICT = \
    dict(CountNumSegmentsStat='Nr. of segments in track',
         CountElementStat='Nr. of reference track elements',
         CountSegmentsOverlappingWithT2Stat='Nr. of overlapping segments with query track',
         CountStat='Genome coverage of track (bps)',
         SingleValueOverlapStat='Overlap between query and reference track (bps)')

BATCH_COL_SEPARATOR = '|'
MULTIPLE_EXTRA_TRACKS_SEPARATOR = '&'
