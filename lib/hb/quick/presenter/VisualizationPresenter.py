from gold.result.GraphicsPresenter import GraphicsPresenter#, LocalResultsGraphicsData, GlobalResultGraphicsData
#from proto.RSetup import r
#import os

#class VisualizationPresenter(LocalResultsGraphicsData, GraphicsPresenter):
class VisualizationPresenter(GraphicsPresenter):
    def _getDataPointCount(self, resDictKey, avoidNAs=True):
        if self._results.getGlobalResult() is not None and self._results.getGlobalResult().get(resDictKey) is not None:
            return len(self._results.getGlobalResult().get(resDictKey).getXlist())
        else:
            return 0

    def _getRawData(self, resDictKey, avoidNAs=True):
        assert resDictKey=='Result' #temporarily..
        globRes = self._results.getGlobalResult()
        assert len(globRes)==1
        visRes = self._results.getGlobalResult().values()[0]
        return visRes.getXlist(), visRes.getYlists()

    def getReference(self, resDictKey):
        return GraphicsPresenter.getReference(self, resDictKey, imageLink=True)


class VisualizationPlotPresenter(VisualizationPresenter):
    name = ('ScaledPlotVisualization', 'Plot: Scaled prototypic plot')
    dataPointLimits = (2,None)
    maxRawDataPoints = 30000
            
    def scaleLines(self, yLists):
        'Very prototypic way of scaling.. Keeps first two lines as is, scales third according to these first two..'
        minY,maxY = [func([func(yl) for yl in yLists]) for func in [min,max]]
        return yLists[0:2] + [[(1.0*y*(maxY-minY)+minY) for y in yLists[2]]]

    def _customRExecution(self, resDictKey, xlab, main):
        #rCode = 'ourHist <- function(ourList, xlab, main, numBins) {vec <- unlist(ourList); hist(vec, col="blue", breaks=numBins, xlab=xlab, main=main)}'
        rCode = '''
        ourPlotter <- function(lx, l1,l2,l3,numericX) {
        v1 = unlist(l1)
        v2 = unlist(l2)
        v3 = unlist(l3)
        if (numericX) {
            vx = unlist(lx)
        } else {
            vx = 1:length(lx)
        }
        #genes2[genes2==0]=NaN
        plot(vx, v1,type='l',col='red',ylim=c(0,1))
        lines(vx, v2,col='green')
        lines(vx, v3,col='black')
        if (! numericX) {
            axis(1, at=1:length(lx),labels=lx,las=2)
        }
        legend('topleft',c('inside','outside','coverage'),col=c('red','green','black'),lty=1)
        }
        '''
        rawData = self._getRawData(resDictKey)
        xList = rawData[0]
        yLists = rawData[1]
        assert len(yLists) == 3
        scaledYLists = self.scaleLines(yLists)
        #print (self._results.getAllValuesForResDictKey(resDictKey), xlab, main)
        #rawData = [float(x) for x in self._getRawData(resDictKey)]
        ##numBins = max(10, self._getDataPointCount(resDictKey)/5)
        from proto.RSetup import r
        #print 'TYPES: ',(str(type(xList)) + str(type(yLists[0]))).replace('<','')
        numericX = (type(xList[0]) in [int,float])
        self._plotResultObject = r(rCode)(xList, list(scaledYLists[0]), list(scaledYLists[1]), list(scaledYLists[2]), numericX)

class VisualizationScaledScatterPresenter(VisualizationPresenter):
    name = ('ScaledScatterVisualization', 'Plot: Scaled prototypic scatter')
    dataPointLimits = (2,None)
    maxRawDataPoints = 30000
    
    def _customRExecution(self, resDictKey, xlab, main):
        #rCode = 'ourHist <- function(ourList, xlab, main, numBins) {vec <- unlist(ourList); hist(vec, col="blue", breaks=numBins, xlab=xlab, main=main)}'
        rCode = '''
        ourPlotter <- function(l1,l2,l3) {
        v1 = unlist(l1)
        v2 = unlist(l2)
        v3 = unlist(l3)
        #genes2[genes2==0]=NaN
        #par(mfrow=c(1,2))
        plot(v1, v2,xlim=c(0,1),col='red',ylim=c(0,1),xlab='Inside/Outside', ylab='Outside/Coverage',main='Comparison of scaled mean values inside and outside, as well as coverage')
        lines(c(0,1),c(0,1),lty='dashed')
        
        points(v1, v3,xlim=c(0,1),col='green',ylim=c(0,1))
        points(v2, v3,xlim=c(0,1),col='blue',ylim=c(0,1))

        #lines(c(0,1),c(0,1),lty='dashed')
        legend('topleft',c('Inside vs Outside','Inside vs Coverage','Outside vs Coverage'),col=c('red','green','blue'),lty=1)
        }
        '''
        rawData = self._getRawData(resDictKey)
        #xList = rawData[0]
        yLists = rawData[1]
        assert len(yLists) == 3
        scaledYLists = [None]*len(yLists)
        for i,yl in enumerate(yLists):
            minY,maxY = min(yl), max(yl)
            scaledYLists[i] = [(1.0*(y-minY)/(maxY-minY)) for y in yl]
        #print (self._results.getAllValuesForResDictKey(resDictKey), xlab, main)
        #rawData = [float(x) for x in self._getRawData(resDictKey)]
        ##numBins = max(10, self._getDataPointCount(resDictKey)/5)
        from proto.RSetup import r
        #print 'TYPES: ',(str(type(xList)) + str(type(yLists[0]))).replace('<','')
        self._plotResultObject = r(rCode)(list(yLists[0]), list(yLists[1]), list(yLists[2]))
        
class VisualizationScatterPresenter(VisualizationPresenter):
    name = ('UnscaledScatterVisualization', 'Plot: Unscaled prototypic scatter')
    dataPointLimits = (2,None)
    maxRawDataPoints = 30000
    
    def _customRExecution(self, resDictKey, xlab, main):
        #rCode = 'ourHist <- function(ourList, xlab, main, numBins) {vec <- unlist(ourList); hist(vec, col="blue", breaks=numBins, xlab=xlab, main=main)}'
        rCode = '''
        ourPlotter <- function(l1,l2,xlim,ylim) {
        v1 = unlist(l1)
        v2 = unlist(l2)
        xlim = unlist(xlim)
        ylim = unlist(ylim)
        #genes2[genes2==0]=NaN
        #par(mfrow=c(1,2))        
        plot(v1, v2,xlim=xlim,col='red',ylim=ylim,xlab='Inside', ylab='Outside',main='Comparison of mean values inside and outside')
        lines(xlim,ylim,lty='dashed')
        
        #lines(c(0,1),c(0,1),lty='dashed')
        legend('topleft',c('Inside vs Outside','Inside vs Coverage','Outside vs Coverage'),col=c('red','green','blue'),lty=1)
        }
        '''
        rawData = self._getRawData(resDictKey)
        #xList = rawData[0]
        yLists = rawData[1]
        assert len(yLists) == 3
        #for i,yl in enumerate(yLists):
        #    minY,maxY = min(yl), max(yl)
        #    yLists[i] = [(1.0*(y-minY)/(maxY-minY)) for y in yl]
        #print (self._results.getAllValuesForResDictKey(resDictKey), xlab, main)
        #rawData = [float(x) for x in self._getRawData(resDictKey)]
        ##numBins = max(10, self._getDataPointCount(resDictKey)/5)
        xlim = ylim = [ min(min(yLists[0]),min(yLists[1])), max(max(yLists[0]),max(yLists[1])) ]
        from proto.RSetup import r
        #print 'TYPES: ',(str(type(xList)) + str(type(yLists[0]))).replace('<','')
        self._plotResultObject = r(rCode)(list(yLists[0]), list(yLists[1]), xlim, ylim)
        
