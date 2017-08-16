from gold.statistic.DiscreteMarksHistStat import DiscreteMarksHistStat
from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic


class SimpleDiscreteMarksIntensityStat(MagicStatFactory):
    pass

#class SimpleDiscreteMarksIntensityStatSplittable(StatisticSumResSplittable):
#    IS_MEMOIZABLE = False
            
class SimpleDiscreteMarksIntensityStatUnsplittable(Statistic):    
    PRIOR_FACTOR = 1.0
    IS_MEMOIZABLE = False

    def __init__(self, region, track, track2, numDiscreteVals=None, **kwArgs):
        self._numDiscreteVals = numDiscreteVals            
        Statistic.__init__(self, region, track, track2, numDiscreteVals=numDiscreteVals, **kwArgs)

    def _compute(self):
        allHist = self._children[0].getResult()
        inPointsHist = self._children[1].getResult()
        res = (inPointsHist.astype('float64') + self.PRIOR_FACTOR * float(inPointsHist.sum(dtype='float64'))/allHist.sum(dtype='float64') ) / (allHist + self.PRIOR_FACTOR)
        #if BpIntensityStatUnsplittable.VERBOSE_INTENSITY_CREATION or IS_EXPERIMENTAL_INSTALLATION:
            #print '<br>Intensity values for each discrete value of control track: ', ','.join([str(x) for x in res])
            #print '<br>With intensity based on point counts for each discrete value being: ', ','.join([str(x) for x in inPointsHist])
            #print '<br>And corresponding demoniator counts (num bps in corresponding value intervals): ', ','.join([str(x) for x in allHist])
            #print '<br>'
        from proto.hyperbrowser.HtmlCore import HtmlCore
        print HtmlCore().tableLine([str(self._region)] + ['%.1e (%i/%i)'%(p,i,d) for p,i,d in zip(res,inPointsHist,allHist)])

        return res
    
    def _createChildren(self):
        self._addChild( DiscreteMarksHistStat(self._region, self._track, self._track2, numDiscreteVals=self._numDiscreteVals) )
        self._addChild( DiscreteMarksHistStat(self._region, self._track, self._track2, numDiscreteVals=self._numDiscreteVals, marksStat='ExtractMarksStat') )
