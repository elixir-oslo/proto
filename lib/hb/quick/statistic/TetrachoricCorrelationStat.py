from gold.statistic.RawOverlapStat import RawOverlapStat
from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic


class TetrachoricCorrelationStat(MagicStatFactory):
    '''
    '''
    pass


class TetrachoricCorrelationStatUnsplittable(Statistic):
    def _compute(self):
        from proto.RSetup import r, robjects
        summaryStats = robjects.FloatVector([self._children[0].getResult()[key] for key in ['Neither','Only1','Only2','Both'] ])
        r('library("polycor")')
        tetraCor = r('function(vec){polychor(matrix(vec, nrow=2))}')
        return tetraCor(summaryStats)

    def _createChildren(self):
        self._addChild(RawOverlapStat(self._region, self._track, self._track2))
