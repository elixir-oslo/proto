from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq

import numpy as np

class GcContentStat(MagicStatFactory):
    pass

#class GcContentStatSplittable(StatisticSumResSplittable):
#    pass
            
class GcContentStatUnsplittable(Statistic):    
    def _compute(self):
        tv = self._children[0].getResult()
        vals = tv.valsAsNumpyArray()
        #return vals == 'c'+ vals == 'C'
        #arr = np.logical_or(np.logical_or(vals == 'c', vals == 'C'), np.logical_or(vals == 'g', vals == 'G'))
    
        resList = [0]*vals.size
        gcVals = {'c':None, 'g':None, 'C':None, 'G':None}
        counter = 0
        for i in vals:
            if gcVals.has_key(i):
                resList[counter] = 1
            counter+=1
            
        res = np.array(resList, dtype='float64')
        return res
    
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(dense=True, val='char')) )
