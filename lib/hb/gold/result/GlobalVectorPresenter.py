from gold.result.GraphicsPresenter import GraphicsPresenter, GlobalResultGraphicsData
#from proto.RSetup import r
import numpy

class GlobalVectorPresenter(GlobalResultGraphicsData, GraphicsPresenter):
    name = ('vector','Global vector')
    dataPointLimits = (1,50000) #or maybe zero, since this is count of local values which are really ignored, and resDictKeys may in some cases change between local and global level..

    #def _getRawData(self, resDictKey,avoidNAs=True):
    #    return self._results.getGlobalResult().get(resDictKey)
    
    def _customRExecution(self, resDictKey, xlab, main):
        rCode = 'plotFunc <- function(ourList, xlab,ylab, main) {vec <- unlist(ourList); plot(vec, type="l", xlab=xlab, ylab=ylab,main=main)}'
        ylab = ''
        from proto.RSetup import r
        r(rCode)(self._getRawData(resDictKey), xlab, ylab,main)

class GlobalMeanSdVectorPresenter(GlobalVectorPresenter):
    name = ('msdvector','Global mean and sd-vector')

    def _getRawData(self, resDictKey,avoidNAs=True):
        res = self._results.getGlobalResult().get(resDictKey)
        mean = res['mean']
        sd = res['sdOfMean']
        return mean, mean+sd, mean-sd
    
    def _customRExecution(self, resDictKey, xlab, main):
        rCode = 'plotFunc <- function(meanList, plusSdList, minusSdList, xlab,ylab, main, ymin,ymax) {vec1 <- unlist(meanList); vec2 <- unlist(plusSdList); vec3 <- unlist(minusSdList); plot(vec1, type="l", xlab=xlab,ylab=ylab, main=main,ylim=c(ymin,ymax)); lines(vec2,type="l",lty="dashed"); lines(vec3,type="l",lty="dashed");}'
        mean,plus,minus = self._getRawData(resDictKey)
        ymin = numpy.concatenate((mean,plus,minus)).min()
        ymax = numpy.concatenate((mean,plus,minus)).max()
        xlab = 'Relative bin-position'
        ylab = self._results.getLabelHelpPair(resDictKey)[0]
        from proto.RSetup import r
        r(rCode)(mean,plus,minus, xlab, ylab, main,ymin,ymax)
