from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic, OnlyGloballySplittable, StatisticNumpyMatrixSplittable
from gold.statistic.CategoryPointCountInSegsMatrixStat import CategoryPointCountInSegsMatrixStat
import numpy
from collections import OrderedDict

class CategoryBinaryPointCountInSegsMatrixStat(MagicStatFactory):
    pass

class CategoryBinaryPointCountInSegsMatrixStatSplittable(StatisticNumpyMatrixSplittable, OnlyGloballySplittable):
    pass
            
class CategoryBinaryPointCountInSegsMatrixStatUnsplittable(Statistic):
    def _compute(self):
        resDict = self._children[0].getResult().get('Result')
        assert resDict is not None
                                                    
        matrix = resDict.get('Matrix')
        assert matrix is not None
        
        matrix = numpy.array(matrix > 0, dtype='int32') 
        
        return {'Result': OrderedDict([('Matrix', matrix), ('Rows', resDict.get('Rows')), ('Cols', resDict.get('Cols'))])}

    
    def _createChildren(self):
        self._addChild(CategoryPointCountInSegsMatrixStat(self._region, self._track, self._track2, **self._kwArgs))

