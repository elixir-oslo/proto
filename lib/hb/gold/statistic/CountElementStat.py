from gold.statistic.MagicStatFactory import MagicStatFactory
#from gold.statistic.CountStat import CountStatSplittable, CountStatUnsplittable
from gold.statistic.OverlapAgnosticCountElementStat import OverlapAgnosticCountElementStatSplittable, OverlapAgnosticCountElementStatUnsplittable

#Similar to CountPointStat, except it doesn't require interval=False
class CountElementStat(MagicStatFactory):
    pass

class CountElementStatSplittable(OverlapAgnosticCountElementStatSplittable):
    pass
            
class CountElementStatUnsplittable(OverlapAgnosticCountElementStatUnsplittable):
    ALLOW_OVERLAPS = False
