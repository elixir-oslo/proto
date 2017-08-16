from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic, OnlyGloballySplittable, StatisticSplittable
from gold.origdata.PreProcessTracksJob import PreProcessCustomTrackJob
from gold.origdata.FunctionSliceGenomeElementSource import FunctionSliceGenomeElementSource
from gold.util.CommonFunctions import isIter

class CreateFunctionTrackStat(MagicStatFactory):
    pass
    
class CreateFunctionTrackStatBase(object):
    IS_MEMOIZABLE = False
    
    def _init(self, outTrackName='', username='', valDataType='float64', **kwArgs):
        self._outTrackName = outTrackName.split('^')
        self._username = username
        self._valDataType = valDataType

class CreateFunctionTrackStatSplittable(CreateFunctionTrackStatBase, StatisticSplittable, OnlyGloballySplittable):
    def _getGESource(self, genome, trackName, region):
        return FunctionSliceGenomeElementSource(genome, trackName, region, None, self._valDataType)
    
    def _combineResults(self):
        if False in self._childResults:
            return False

        assert isIter(self._region)
        regionList = list(self._region)
        genome = regionList[0].genome
        
        job = PreProcessCustomTrackJob(genome, self._outTrackName, regionList, self._getGESource, \
                                       username=self._username, preProcess=False, finalize=True)
        job.process()
                
        return True

class CreateFunctionTrackStatUnsplittable(CreateFunctionTrackStatBase, Statistic):
    def _getGESource(self, genome, trackName, region):
        slice = self._children[0].getResult()
        return FunctionSliceGenomeElementSource(genome, trackName, region, slice, self._valDataType)
    
    def _compute(self):
        if self._kwArgs.get('minimal') == True:
            return False
        
        job = PreProcessCustomTrackJob(self._region.genome, self._outTrackName, [self._region], \
                                       self._getGESource, username=self._username, preProcess=True, finalize=False)
        job.process()

        #To reduce memory consumption
        self._children = []

        return True
        
    def _createChildren(self):
        from gold.statistic.AllStatistics import STAT_CLASS_DICT
        self._addChild( STAT_CLASS_DICT[self._kwArgs['dataStat']](self._region, self._track, self._track2 if hasattr(self,'_track2') else None, **self._kwArgs) )
