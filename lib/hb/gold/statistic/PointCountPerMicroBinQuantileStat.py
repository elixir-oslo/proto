from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from quick.statistic.PointCountPerMicroBinV2Stat import PointCountPerMicroBinV2Stat


class PointCountPerMicroBinQuantileStat(MagicStatFactory):
    '''
    Computes a given quantile from the counts per microbin, both within user bins and at the global level
    '''
    pass

class PointCountPerMicroBinQuantileStatUnsplittable(Statistic):
    def _init(self, quantile, **kwArgs):
        self._quantile = quantile

    def _createChildren(self):
        self._addChild( PointCountPerMicroBinV2Stat(self._region, self._track, **self._kwArgs) )

    def _compute(self):
        counts = self._children[0].getResult()
        if self._quantile == 'avg':
            return sum(counts) / float(len(counts))
        else:
            quantIndex = int(round(float(self._quantile)/100*(len(counts)-1)) )
            return sorted(counts)[quantIndex]

