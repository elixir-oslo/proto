from gold.result.GraphicsPresenter import GraphicsPresenter, LocalResultsGraphicsData, GlobalResultGraphicsData
from numpy import isnan
#from proto.RSetup import r
 
class DensityPresenter(LocalResultsGraphicsData, GraphicsPresenter):
    name = ('density','Density plot')
    dataPointLimits = (2,None)

    #def _getRawData(self, resDictKey, avoidNAs=True):
    #    return [x for x in self._results.getAllValuesForResDictKey(resDictKey) if not (avoidNAs and isnan(x))]
        ##if self._results.getGlobalResult() is not None:
        ##    return self._results.getGlobalResult().get(resDictKey)
        ##else:
        ##    return None

    def _customRExecution(self, resDictKey, xlab, main):
        fromTo = ',from=0,to=1' if resDictKey == 'p-value' else ''
        rCode = 'plotFunc <- function(ourList, xlab, main) {vec <- unlist(ourList); plot(density(vec'+fromTo+'), xlab=xlab, main=main)}'
        #print (self._getRawData(resDictKey), xlab, main)
        rawData = [float(x) for x in self._getRawData(resDictKey)]
        from proto.RSetup import r
        r(rCode)(rawData, xlab, main)
        
        
class DensityGlobalListPresenter(GlobalResultGraphicsData, DensityPresenter):
    dataPointLimits = (2,None)
    #def _getRawData(self, resDictKey, avoidNAs=True):
    #    if self._results.getGlobalResult() is not None:
    #        return self._results.getGlobalResult().get(resDictKey)
    #    else:
    #        return None
    #
    #def _getDataPointCount(self,resDictKey):
    #    if self._results.getGlobalResult() is not None:
    #        return len(self._results.getGlobalResult().get(resDictKey))
    #    else:
    #        return 0
    #
