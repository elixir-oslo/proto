from gold.result.GraphicsPresenter import GraphicsPresenter, LocalResultsGraphicsData
from quick.util.CommonFunctions import ensurePathExists
from gold.util.CommonFunctions import isNumber
import os
import numpy
#from proto.RSetup import r

class ScatterPresenter(LocalResultsGraphicsData, GraphicsPresenter):
    name = ('scatter','Scatter plot')
    dataPointLimits = (2,1e6) 
    
    def _checkCorrectData(self, resDictKey):
        resList = self._results.getAllValuesForResDictKey(resDictKey)
        return len(resList) > 0 and any(isNumber(x) for x in sum([y for y in a if y is not None],[]))
    
    def _getRawData(self, resDictKey, avoidNAs=True):
        rawData = [ [float(x[i]) for x in self._results.getAllValuesForResDictKey(resDictKey) if x is not None and not (avoidNAs and any(numpy.isnan(val) for val in x))] for i in [0,1] ]
        return rawData
    
    def _writeRawData(self, resDictKey, fn):
        ensurePathExists(fn)
        rawData = self._getRawData(resDictKey, False)
        outF = open(fn,'w')
        outF.write( 'Xs: ' + ','.join([ str(x) for x in rawData[0]]) + os.linesep )
        outF.write( 'Ys: ' + ','.join([ str(x) for x in rawData[1]]) + os.linesep )

    def _customRExecution(self, resDictKey, xlab, main):
        from proto.RSetup import r, robjects
        
        xs, ys = self._getRawData(resDictKey)
        xVec = robjects.FloatVector(xs)
        yVec = robjects.FloatVector(ys)

        rCode = 'plotFunc <- function(xVec, yVec, xlab, ylab, main) {plot(xVec, yVec, xlab=xlab, ylab=ylab, main=main); lines(lowess(xVec, yVec),col="red")}'
        
        #print (xs, ys, xlab, main)
        #print 'rawData: ',self._getRawData(resDictKey)
        xlab = 'Stat-values on track1' #rename x-lab for scatter-plot case..
        ylab = 'Stat-values on track2'
        r(rCode)(xVec, yVec, xlab, ylab, main)

        self._plotResultObject = r('dataFunc <- function(xVec, yVec) {list("x"=xVec, "y"=yVec)}')(xVec, yVec)
