from gold.result.GraphicsPresenter import GraphicsPresenter, LocalResultsGraphicsData
from quick.util.CommonFunctions import ensurePathExists
import os
import numpy
#from proto.RSetup import r

class LinePlotPresenter(LocalResultsGraphicsData, GraphicsPresenter):
    name = ('line','Line plot')
    dataPointLimits = (2,1e6)

    def _getRawData(self, resDictKey, avoidNAs=True):
        rawDict = self._results.getGlobalResult().get(resDictKey)
        xList = rawDict.keys()
        xList = sorted(x for x in xList if not (avoidNAs and numpy.isnan(rawDict[x])))
        yList = [rawDict[x] for x in xList]
        return xList, yList, rawDict.getXLabel(), rawDict.getYLabel()

    def _writeRawData(self, resDictKey, fn):
        ensurePathExists(fn)
        xList, yList, xLabel, yLabel = self._getRawData(resDictKey, False)
        outF = open(fn,'w')
        outF.write( xLabel +': ' + ','.join([ str(x) for x in xList]) + os.linesep )
        outF.write( yLabel + ': ' + ','.join([ str(x) for x in yList]) + os.linesep )

    def _customRExecution(self, resDictKey, xlab, main):
        from proto.RSetup import r, robjects
        
        xList, yList, xLabel, yLabel = self._getRawData(resDictKey)
        xVec = robjects.FloatVector(xList)
        yVec = robjects.FloatVector(yList)

        rCode = 'plotFunc <- function(xVec, yVec, xlab, ylab, main) {plot(xVec, yVec, type="l", xlab=xlab, ylab=ylab, main=main)}'
        
        #print (xs, ys, xlab, main)
        #print 'rawData: ',self._getRawData(resDictKey)
        r(rCode)(xVec, yVec, xLabel, yLabel, main)
        
        self._plotResultObject = r('dataFunc <- function(xVec, yVec) {list("x"=xVec, "y"=yVec)}')(xVec, yVec)
