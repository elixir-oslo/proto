from gold.statistic.MagicStatFactory import MagicStatFactory
from quick.statistic.GenericRelativeToGlobalStat import GenericRelativeToGlobalStat, GenericRelativeToGlobalStatUnsplittable
from quick.statistic.GenericRelativeToGlobalV2Stat import GenericRelativeToGlobalV2Stat, \
    GenericRelativeToGlobalV2StatUnsplittable
from quick.statistic.StatisticV2 import StatisticV2, StatisticV2Splittable
from gold.statistic.CountElementStat import CountElementStat
from quick.statistic.SummarizedStat import SummarizedStat
from gold.util.CustomExceptions import SplittableStatNotAvailableError


class GSuiteBinEnrichmentPValStat(MagicStatFactory):
    """
    Genertate p-values for each bin assuming binomial dist for now
    """
    pass



#class GSuiteBinEnrichmentPValStatSplittable(StatisticV2Splittable):
#    raise SplittableStatNotAvailableError


class GSuiteBinEnrichmentPValStatUnsplittable(StatisticV2):
    def __init__(self, region, track, **kwArgs):
        if hasattr(region, '__iter__'):
            raise SplittableStatNotAvailableError()
        super(self.__class__, self).__init__(region, track,  **kwArgs)


    def _init(self, globalSource=None, minimal=False, **kwArgs):

        assert globalSource is not None
        self._globalSource = GenericRelativeToGlobalStatUnsplittable.getGlobalSource(globalSource, self._region.genome, minimal)


    def _compute(self):
        Ois = self._countOfSegmentsInBin.getResult()
        globalOis = self._countOfSegmentsAcrossBins.getResult()
        binCoverageProportion = self._proportionOfAnalysisRegionInBin.getResult()
        #print self._region
        #print "<p>**** %d, %d, %f</p>" % (Ois, globalOis, binCoverageProportion)
        #Eis =float(globalOis)*binCoverageProportion
        from proto.RSetup import r
        return 1.0 - r.pbinom(Ois, globalOis, binCoverageProportion) #handle tails.. Do some trick to send in lower.tail..

    def _createChildren(self):
        self._countOfSegmentsInBin = self._addChild(SummarizedStat(self._region, self._trackStructure,
                                                                   pairwiseStatistic='CountElementStat',
                                                                   summaryFunc='sum'))
        self._countOfSegmentsAcrossBins = self._addChild(SummarizedStat(self._globalSource, self._trackStructure,
                                                                        pairwiseStatistic='CountElementStat',
                                                                        summaryFunc='sum'))
        #self._proportionOfAnalysisRegionInBin = self._addChild(GenericRelativeToGlobalStat(self._region, self._track, globalSource=self._kwArgs['globalSource']), rawStatistic = self._kwArgs['rawStatistic'])
        #self._proportionOfAnalysisRegionInBin = self._addChild(GenericRelativeToGlobalV2Stat(self._region, self._trackStructure, **self._kwArgs))
        self._proportionOfAnalysisRegionInBin = self._addChild(GenericRelativeToGlobalStat(self._region, self._track, **self._kwArgs))
