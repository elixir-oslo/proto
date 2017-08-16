#Note: Not yet tested. Should have unit and intTest.
import numpy
from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic, StatisticSplittable, OnlyGloballySplittable
from gold.statistic.CountPointStat import CountPointStat
from collections import OrderedDict

class PropFreqOfTr1VsTr2Stat(MagicStatFactory):
    pass

class PropFreqOfTr1VsTr2StatSplittable(StatisticSplittable, OnlyGloballySplittable):
    "Not a ratio, but really the proportion of all points covered by track1 in each bin.."
    def _combineResults(self):
        c1 = sum([x['CountTrack1'] for x in self._childResults if x!=None ])
        c2 = sum([x['CountTrack2'] for x in self._childResults if x!=None ])
        if (c1+c2)>0:
            ratio = 1.0*c1/(c1+c2)
        else:
            ratio = numpy.nan
        variance = numpy.array([x['Track1Prop'] for x in self._childResults if x!=None and not numpy.isnan(x['Track1Prop'])]).var()
        self._result = OrderedDict([('Track1Prop', ratio), ('CountTrack1', c1), ('CountTrack2', c2), ('Variance', variance)])
        return self._result

class PropFreqOfTr1VsTr2StatUnsplittable(Statistic):
    def _createChildren(self):
        binCount1 = CountPointStat(self._region, self._track)
        binCount2 = CountPointStat(self._region, self._track2)

        self._addChild(binCount1)
        self._addChild(binCount2)

    def _compute(self):    
        c1 = self._children[0].getResult()
        c2 = self._children[1].getResult()
        ratio = 1.0*c1/(c1+c2)
        return OrderedDict([('Track1Prop', ratio), ('CountTrack1', c1), ('CountTrack2', c2), ('Variance', None)])
