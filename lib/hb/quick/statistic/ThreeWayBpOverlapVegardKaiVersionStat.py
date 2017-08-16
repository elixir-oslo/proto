from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import MultipleRawDataStatistic
from gold.track.TrackFormat import TrackFormatReq
from quick.statistic.VennDataStat import VennDataStatUnsplittable, VennDataStatSplittable
from collections import defaultdict

class ThreeWayBpOverlapVegardKaiVersionStat(MagicStatFactory):
    '''Computes the combined overlap of different subsets of supplied tracks.
    Note that coverage by subsets is not disjunct, so that e.g. result for '01',
    denoting coverage by track2 (for two track overlap) also includes bps covered by both tracks
    '''
    pass

#class ThreeWayBpOverlapVegardKaiVersionStatSplittable(StatisticDictSumResSplittable):
#    pass

class ThreeWayBpOverlapVegardKaiVersionStatSplittable(VennDataStatSplittable):
    pass
    
class ThreeWayBpOverlapVegardKaiVersionStatUnsplittable(MultipleRawDataStatistic):
    #from gold.util.CommonFunctions import repackageException
    #from gold.util.CustomExceptions import ShouldNotOccurError
    #@repackageException(Exception, ShouldNotOccurError)
    def _compute(self):
        
        tvs = [child.getResult() for child in self._children]
        categoryBedList = defaultdict(list)
        categoryNames = ['t'+str(i) for i in range(len(tvs))]

        for tv,cat in zip(tvs, categoryNames):        
            rawData = tv
            ends = list(rawData.endsAsNumpyArray())
            starts = list(rawData.startsAsNumpyArray())
            for i in range(len(starts)):
                categoryBedList[chr].append((starts[i], ends[i], cat))
        
        
        return VennDataStatUnsplittable._calculateIntersections(categoryBedList, categoryNames, 'dummyTNforNow')
        


    def _getTrackFormatReq(self):
        return TrackFormatReq(dense=False)
