from gold.result.GraphicsPresenter import GraphicsPresenter, LocalResultsGraphicsData, GlobalResultGraphicsData
from gold.util.CustomExceptions import SilentError
from math import log
import os

class PixelBasedLocalResultsPresenter(LocalResultsGraphicsData, GraphicsPresenter):
    name = ('pixel', 'Plot: pixel-colored local results')
    dataPointLimits = (2,None)
    maxRawDataPoints = 5e5
    
    #def _checkCorrectData(self, resDictKey):
    #    try:
    #        data = self._getRawData(resDictKey)
    #        if len(data) > 0:            
    #            data[0] + 1
    #    except:
    #        return False
    #    return True
        
    def _customRExecution(self, resDictKey, xlab, main):
        from proto.RSetup import r, robjects
        #rCode = 'ourHist <- function(ourList, xlab, main, numBins) {vec <- unlist(ourList); hist(vec, col="blue", breaks=numBins, xlab=xlab, main=main)}'
        rCode = '''
        plot(2,2)
        '''
        
        rawData = self._getRawData(resDictKey) #A python list of values..
        #rawData = [float(x) for x in self._getRawData(resDictKey)]        
        self._plotResultObject = r(rCode) #()

#class HistogramGlobalListPresenter(GlobalResultGraphicsData, HistogramPresenter):
#    dataPointLimits = (2, None)
#
#class LogHistogramGlobalListPresenter(HistogramGlobalListPresenter):
#    name = ('hist_log', 'Plot: histogram of log-transposed values')
#    
#    def _getRawData(self, resDictKey, avoidNAs=True):
#        return [log(x) for x in HistogramGlobalListPresenter._getRawData(self, resDictKey) if x>0]
#        
#    def _customRExecution(self, resDictKey, xlab, main):
#        HistogramGlobalListPresenter._customRExecution(self, resDictKey, xlab + ' (log-transposed)', main)
