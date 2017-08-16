from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.CountStat import CountStat
from gold.statistic.SumInsideStat import SumInsideStat
#from gold.statistic.SumStat import SumStat
from gold.statistic.SumOverCoveredBpsStat import SumOverCoveredBpsStat
from gold.statistic.FormatSpecStat import FormatSpecStat
from gold.track.TrackFormat import TrackFormatReq
#from rpy import *

class DiffOfMeanInsideOutsideStat(MagicStatFactory):
    pass

class DiffOfMeanInsideOutsideStatUnsplittable(Statistic):
    resultLabel = 'MeanInside-MeanOutside'
    
    def __init__(self, region, track, track2, **kwArgs):
        Statistic.__init__(self, region, track, track2, **kwArgs)

    def _compute(self):
        
        sumInside = self._children[0].getResult()
        cntInside = self._children[1].getResult()
        sumAll = self._children[2].getResult()
        cntAll = self._children[3].getResult()
        
        return 1.0*sumInside/cntInside - 1.0*(sumAll-sumInside)/(cntAll-cntInside)
         
    def _createChildren(self):
        #self._track provide intervals for inside vs outside, self._track2 provide values
        sumInsideStat = SumInsideStat(self._region, self._track, self._track2)
        countInsideStat = CountStat(self._region, self._track)
        #sumAllStat = SumStat(self._region, self._track2)
        sumAllStat = SumOverCoveredBpsStat(self._region, self._track2)
        countAllStat = CountStat(self._region, self._track2)
        
        self._addChild(sumInsideStat)
        self._addChild(countInsideStat)
        self._addChild(sumAllStat)
        self._addChild(countAllStat)
        from config.Config import IS_EXPERIMENTAL_INSTALLATION
        if not IS_EXPERIMENTAL_INSTALLATION:
            self._addChild( FormatSpecStat(self._region, self._track2, TrackFormatReq(dense=True) ) )
    #
    #def analyticalPValue(self):
    #    rawDataStat = RawDataStat(self._region, self._track, TrackFormatReq(interval=True, dense=False))
    #    rawDataStat2 = RawDataStat(self._region, self._track2, TrackFormatReq(dense=True, interval=False))
    #    segData = rawDataStat.getResult()
    #    numData = rawDataStat2.getResult()
    #    tot_inside = []
    #    tot_outside = [float(el.val()) for el in numData]
    #    for el in rawDataStat.getResult():
    #        inside = tot_outside[el.start():el.end()]
    #        tot_inside.extend(inside)
    #        for e in inside:
    #            tot_outside.remove(e)
    #    c=r.t_test(tot_inside, tot_outside, 'two.sided')
    #    return c['p.value']
