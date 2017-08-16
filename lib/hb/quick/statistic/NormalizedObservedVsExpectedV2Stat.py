from gold.statistic.MagicStatFactory import MagicStatFactory
from quick.statistic.StatisticV2 import StatisticV2

#TODO: boris 20160404, implement V2
class NormalizedObservedVsExpectedV2Stat(MagicStatFactory):
    '''
    Calculate the normalized Forbes similarity measure for tracks in the query GSuite, normalized in relation to the reference GSuite 
    '''
    pass


#class NormalizedObservedVsExpectedV2StatSplittable(StatisticSumResSplittable):
#    pass

class NormalizedObservedVsExpectedV2StatUnsplittable(StatisticV2):

    def _init(self, reverse='No', **kwArgs):
        self._reversed = reverse == 'Yes'

    def _compute(self):
        pass

    def _createChildren(self):
        pass
