from config.Config import HB_SOURCE_CODE_BASE_DIR
from gold.result.GraphicsPresenter import GraphicsPresenter, LocalResultsGraphicsData
#from proto.RSetup import r
from quick.util.CommonFunctions import silenceRWarnings
import shutil
import os.path

#class GwPlotPresenter(LocalResultsGraphicsData, GraphicsPresenter):
class GwPlotPresenter(GraphicsPresenter):
    name = ('gwplot', 'Plot: values per bin')
    dataPointLimits = (2,None)

    def __init__(self, results, baseDir, header, historyFilePresenter):
        GraphicsPresenter.__init__(self, results, baseDir, header)
        self._historyFilePresenter = historyFilePresenter
        silenceRWarnings()

    #def _getRawData(self, resDictKey, avoidNAs=True):
    #    return self._results.getAllValuesForResDictKey(resDictKey)
    
    #def _customRExecution(self, resDictKey, xlab, main):
    def _writeContent(self, resDictKey, fn):
        #rCode = 'ourHist <- function(ourList, xlab, main, numBins) {vec <- unlist(ourList); hist(vec, col="blue", breaks=numBins, xlab=xlab, main=main)}'
        #print (self._results.getAllValuesForResDictKey(resDictKey), xlab, main)
        PLOT_BED_FN = os.sep.join([HB_SOURCE_CODE_BASE_DIR, 'rCode', 'plotBed.r'])
        PLOT_CHR_FN = os.sep.join([HB_SOURCE_CODE_BASE_DIR, 'rCode', 'ChromosomePlot.r'])        
        forHistoryFn = self._historyFilePresenter._getFn(resDictKey)
        #outDir = self._baseDir
        outDir = os.path.split(fn)[0]
        from proto.RSetup import r
        r('source("%s")' % PLOT_BED_FN)
        r('source("%s")' % PLOT_CHR_FN)
        r('loadedBedData <- plot.bed("%s")' % forHistoryFn)
        resultLabel = self._results.getLabelHelpPair(resDictKey)[0]
        r('plot.chrom(segments=loadedBedData, unit="bp", dir.print="%s", ylab="%s")' % (outDir,resultLabel))
        shutil.move(outDir+ os.sep + '.pdf', fn)
        #rawData = self._getRawData(resDictKey)
        #r(rCode)(rawData, xlab, main, numBins)
        
    def _checkCorrectData(self, resDictKey):
        
        forHistoryFn = self._historyFilePresenter._getFn(resDictKey)
        #print 'forHistoryFn (_checkCorrectData i GwPlotPresenter)', forHistoryFn
        return os.path.exists(forHistoryFn)
        
    def _getFns(self, resDictKey):
        figFn = os.sep.join([self._baseDir, self._results.getStatClassName() + '_' + resDictKey +'_' + self.__class__.name[0]+'.pdf'])
        rawFn = self._historyFilePresenter._getFn(resDictKey)
        return [figFn, rawFn]
        #res = GraphicsPresenter._getFns(self, resDictKey)
        #res[0] = res[0].replace('.png', '.pdf')
        #return res

    #def _getRawData(self, resDictKey, avoidNAs=True):
    #    return [x for x in self._results.getAllValuesForResDictKey(resDictKey) if x is not None and (type(x) is not list) and not (avoidNAs and numpy.isnan(x))]

    def _writeRawData(self, resDictKey, fn):
        pass #since it uses raw data from a file that already exists
    
    def _getDataPointCount(self, resDictKey, avoidNAs=True):
        fn = self._historyFilePresenter._getFn(resDictKey)
        return sum(1 for line in open(fn))
