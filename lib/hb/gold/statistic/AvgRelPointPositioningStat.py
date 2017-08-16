import numpy
from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.PointPositionsInSegsStat import PointPositionsInSegsStat

class AvgRelPointPositioningStat(MagicStatFactory):
    pass

class AvgRelPointPositioningStatUnsplittable(Statistic):        
    def _compute(self):
        #try: #fixme: temp solution to handle NoneResultError
        relPositions = self._children[0].getResult()
        #except:
            #return 0.5
        
        if len(relPositions)==0:
            return 0.5 #fixme: temp solution 
            return numpy.nan            
        return sum(relPositions) / float(len(relPositions))
    
    def _createChildren(self):
        self._addChild( PointPositionsInSegsStat(self._region, self._track, self._track2) )
