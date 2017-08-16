from gold.result.GraphicsPresenter import GraphicsPresenter, LocalResultsGraphicsData, GlobalResultGraphicsData
from gold.util.CustomExceptions import SilentError
from math import log
import os

class HistogramPresenter(LocalResultsGraphicsData, GraphicsPresenter):
    name = ('hist', 'Plot: histogram')
    dataPointLimits = (2,None)
    maxRawDataPoints = 30000
    numCount=0 #to JS plots

    def _checkCorrectData(self, resDictKey):
        try:
            data = self._getRawData(resDictKey)
            if len(data) > 0:
                data[0] + 1
        except:
            return False
        return True

    def _customRExecution(self, resDictKey, xlab, main):
        from proto.RSetup import r, robjects
        #rCode = 'ourHist <- function(ourList, xlab, main, numBins) {vec <- unlist(ourList); hist(vec, col="blue", breaks=numBins, xlab=xlab, main=main)}'
        rCode = \
            '''ourHist <- function(vec, xlab, main, numBins)
               {main = paste(strwrap(main, width=60), collapse="\n");
                hist(vec, col="blue", breaks=numBins, xlab=xlab, main=main)}'''
        #print (self._results.getAllValuesForResDictKey(resDictKey), xlab, main)
        rawData = robjects.FloatVector(self._getRawData(resDictKey))
        #rawData = [float(x) for x in self._getRawData(resDictKey)]
        numBins = max(10, self._getDataPointCount(resDictKey)/5)
        
        '''
        import numpy
        data = numpy.bincount(self._getRawData(resDictKey))
        import quick.webtools.restricted.visualization.visualizationPlots as vp
        from proto.hyperbrowser.HtmlCore import HtmlCore
        self.__class__.numCount +=1
        if self.__class__.numCount==1:
            htmlCore = HtmlCore()
            htmlCore.begin()
            htmlCore.divBegin('plotDiv')
            htmlCore.line(vp.addJSlibs())
            htmlCore.line(vp.useThemePlot())
            htmlCore.line(vp.addJSlibsExport())
            htmlCore.line(vp.axaddJSlibsOverMouseAxisisPopup())
            seriesType = ['column' for x in list(data)]
            
            #linear scale
            """  
            htmlCore.line(vp.drawChart(list(data),
                                       tickInterval=None,
                                       type='column',
                                       label='x= {point.x} </br> y= {point.y}',
                                       seriesType=seriesType,
                                       height=400,
                                       titleText='Histogram',
                                       tickMinValue=1,
                                       legend=False,
                                       plotNumber=self.__class__.numCount
                                       ))
            """
            #log scale
            htmlCore.line(vp.drawChart(list(data),
                                       tickInterval=None,
                                       type='column',
                                       label='x= {point.x} </br> y= {point.y}',
                                       seriesType=seriesType,
                                       height=400,
                                       titleText='Histogram',
                                       typeAxisXScale = 'logarithmic',
                                       pointStartLog=1,
                                       legend=False,
                                       plotNumber=self.__class__.numCount
                                       ))    
            htmlCore.divEnd()
            htmlCore.end()
            print str(htmlCore)
            '''
        self._plotResultObject = r(rCode)(rawData, xlab, main, numBins)

class HistogramGlobalListPresenter(GlobalResultGraphicsData, HistogramPresenter):
    dataPointLimits = (2, None)

class LogHistogramGlobalListPresenter(HistogramGlobalListPresenter):
    name = ('hist_log', 'Plot: histogram of log-transposed values')

    def _getRawData(self, resDictKey, avoidNAs=True):
        return [log(x+1) for x in HistogramGlobalListPresenter._getRawData(self, resDictKey) if x>=0]

    def _customRExecution(self, resDictKey, xlab, main):
        HistogramGlobalListPresenter._customRExecution(self, resDictKey, xlab + ' (log-transposed)', main)
