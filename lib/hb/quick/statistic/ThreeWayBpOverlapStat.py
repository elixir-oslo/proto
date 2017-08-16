from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import StatisticDictSumResSplittable, MultipleRawDataStatistic
from gold.track.TrackFormat import TrackFormatReq
import numpy
from quick.util.CommonFunctions import numAsPaddedBinary

class ThreeWayBpOverlapStat(MagicStatFactory):
    '''Computes the combined overlap of different subsets of supplied tracks.
    Note that coverage by subsets is not disjunct, so that e.g. result for '01',
    denoting coverage by track2 (for two track overlap) also includes bps covered by both tracks
    '''
    pass

class ThreeWayBpOverlapStatSplittable(StatisticDictSumResSplittable):
    pass

class ThreeWayBpOverlapStatUnsplittable(MultipleRawDataStatistic):
    #from gold.util.CommonFunctions import repackageException
    #from gold.util.CustomExceptions import ShouldNotOccurError
    #@repackageException(Exception, ShouldNotOccurError)
    def _compute(self):
        t = [child.getResult().getBinaryBpLevelArray() for child in self._children]
        binSize = len(t[0])
        res = {}
        #for i in range(3):
            #res['T%i coverage' % i] = sum(t[i])
        for comb in range(1,2**len(t)): #enumerate with binary number corresponding to all subsets
            #print 'COMB ',comb, 2**len(t)
            binary = numAsPaddedBinary(comb,len(t))
            trackIndicator = numpy.empty(binSize,dtype='bool')
            trackIndicator[:] = True
            for tIndex, doInclude in enumerate(binary):
                if doInclude == '1':
                    trackIndicator &= t[tIndex]
            res[binary] = trackIndicator.sum()
        return res

    def _getTrackFormatReq(self):
        return TrackFormatReq(dense=False)
