from gold.statistic.Statistic import Statistic
from numpy import concatenate, zeros, bincount

class AbstractHistStatUnsplittable(Statistic):
    IS_MEMOIZABLE = False

    def _compute(self):
        discreteMarks = self._children[0].getResult()
        if len(discreteMarks) == 0:
            return zeros(self._numHistBins, dtype='int32')
        hist = bincount(discreteMarks.astype('int32'))
        if len(hist) != self._numHistBins:
            zeros(self._numHistBins-len(hist), dtype='int32')
            hist = concatenate([hist, zeros(self._numHistBins-len(hist), dtype='int32')])
        return hist
