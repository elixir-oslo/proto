from gold.result.Presenter import Presenter

class FDRSummaryPresenter(Presenter):
    def __init__(self, results, baseDir=None):
        Presenter.__init__(self, results, baseDir)

    def getDescription(self):
        return 'Significance at 20% FDR'
        
    def getReference(self, resDictKey):
        numTotal = len(self._results)
        numSign = self._results.getNumSignificantAdjustedPVals(resDictKey, 0.20, 'fdr')
        if numSign is None:
            return '' #'N/A'
        else:
            return str(numSign) + '/' + str(numTotal) + ' bins'
