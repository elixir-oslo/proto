import os
from collections import Iterable

import numpy

from gold.result.GraphicsPresenter import GraphicsPresenter, GlobalResultGraphicsMatrixDataFromNumpy, GlobalResultGraphicsMatrixDataFromDictOfDicts, \
    GlobalResultGraphicsMatrixDataFromTableData
from quick.result.model.TableData import TableData
from quick.util.CommonFunctions import ensurePathExists


class HeatmapPresenter(GraphicsPresenter):
    name = ('heatmap', 'Plot: heatmap')
    dataPointLimits = (2,None)
    HIGH_DEF_COLORS = True
    POINT_SIZE = 12 #8
    LABEL_TEXT_SIZE = 18 #24
    FONT = 2
    BLOCK_SIZE = 30 #10
    DEND_PIXELS_PER_HEIGHT = 20
    RATIO_BOTTOM_RIGHT_MARGIN_ADJUST = 0.75
    RATIO_OF_TOP_LEFT_TO_SMALLEST_BR_MARGIN = 0.5
    MIN_TOP_LEFT_MARGIN = 150
    RATIO_OF_MAX_DEND_SIZE_TO_MAP = 0.25
    # MAX_RATIO_OF_HEATMAP_VS_BR_MARGIN = 1

    def __init__(self, results, baseDir, header, printDimensions=True):
        GraphicsPresenter.__init__(self, results, baseDir, header)
        self._cex = 0
        self._marginBottom = 0
        self._marginRight = 0
        self._marginLeft = 0
        self._marginTop = 0
        self._mapWidth = 0
        self._mapHeight = 0
        self._returnDict = {}
        self._printDimensions = printDimensions

    def _getLineHeigthInPixels(self):
        # from proto.RSetup import r
        # return r("par('mai')[1]/par('mar')[1]*72")
        #
        # For some mysterious reason, the above is not correct.
        # The following is the real line height in pixels.
        # (R moves in mysterious ways...)
        #
        return 179.0/15

    def _getMarginsInLineHeights(self):
        lineHeight = self._getLineHeigthInPixels()
        return 1.0 * self._marginBottom / lineHeight, \
               1.0 * self._marginRight / lineHeight

    def getPlotDimensions(self, resDictKey):
        tableData = self._getRawData(resDictKey)
        assert isinstance(tableData, TableData)

        colNames = tableData.columnNamesAsNumpyArray
        rowNames = tableData.rowNamesAsNumpyArray
        colClust = tableData.colClust
        rowClust = tableData.rowClust

        self._cex = 1.0 * self.LABEL_TEXT_SIZE / self.POINT_SIZE

        from proto.RSetup import r
        charWidthHeightRatio = r("par('cin')[1]/par('cin')[2]")
        marginBottom = int(colNames.dtype.itemsize * charWidthHeightRatio * self.LABEL_TEXT_SIZE)
        marginRight = int(rowNames.dtype.itemsize * charWidthHeightRatio * self.LABEL_TEXT_SIZE)

        self._marginBottom = self.RATIO_BOTTOM_RIGHT_MARGIN_ADJUST * marginBottom
        self._marginRight = self.RATIO_BOTTOM_RIGHT_MARGIN_ADJUST * marginRight

        blockSize = self.BLOCK_SIZE

        # maxRatio = self.MAX_RATIO_OF_HEATMAP_VS_BR_MARGIN
        # if blockSize * len(rowNames) < self._marginBottom * maxRatio:
        #     blockSize = 1.0 * self._marginBottom * maxRatio / len(rowNames)
        # if blockSize * len(colNames) < self._marginRight * maxRatio:
        #     blockSize = 1.0 * self._marginRight * maxRatio / len(colNames)

        self._mapHeight = blockSize * len(rowNames) + self._marginBottom
        self._mapWidth = blockSize * len(colNames) + self._marginRight

        smallestBottomRightMargin = min(self._marginBottom, self._marginRight)
        marginTop = self.RATIO_OF_TOP_LEFT_TO_SMALLEST_BR_MARGIN * smallestBottomRightMargin
        marginLeft = self.RATIO_OF_TOP_LEFT_TO_SMALLEST_BR_MARGIN * smallestBottomRightMargin

        marginTop = self._adjustMarginByDendSize(marginTop, colClust, self._mapHeight)
        marginLeft = self._adjustMarginByDendSize(marginLeft, rowClust, self._mapWidth)

        smallestTopLeftMargin = min(marginTop, marginLeft)
        topLeftMargin = max(smallestTopLeftMargin, self.MIN_TOP_LEFT_MARGIN)
        self._marginTop = topLeftMargin
        self._marginLeft = topLeftMargin

        ret = self._marginLeft + self._mapWidth, \
              self._marginTop + self._mapHeight

        if self._printDimensions:
            from proto.hyperbrowser.HtmlCore import HtmlCore
            print str(HtmlCore().styleInfoBegin(styleClass='debug'))

            print self._marginLeft, self._mapWidth, \
                  self._marginTop, self._mapHeight
            print ret

            print str(HtmlCore().styleInfoEnd())

        return ret

    def _getDendHeightInPixels(self, clust):
        maxDendHeight = clust.rx2('height')
        if isinstance(maxDendHeight, Iterable):
            maxDendHeight = max(maxDendHeight)
        return int(maxDendHeight * self.DEND_PIXELS_PER_HEIGHT)

    def _adjustMarginByDendSize(self, margin, clust, mapSize):
        if clust is not None:
            dendHeight = self._getDendHeightInPixels(clust)
            dendHeight = min(dendHeight, self.RATIO_OF_MAX_DEND_SIZE_TO_MAP * mapSize)
            margin = max(margin, dendHeight)
        return margin

    def _customRExecution(self, resDictKey, xlab, main):
        from proto.RSetup import r, robjects

        rCode = ('ourHeatmap <- function(matrix, rowNames, colNames, rowClust,'
                                        'colClust, dendrogram, marginLeft, '
                                        'marginTop, mapHeight, mapWidth, '
                                        'margins, cex, font, col, breaks, cellnote){'
                 'dimnames(matrix) <- list(rowNames, colNames); '
                 'sink(file("/dev/null", open="wt"), type="output"); '
                 'library(gplots); sink(); options(expressions=100000); '
                 'if (typeof(rowClust) != "logical") {'
                    'class(rowClust) = "hclust"; '
                    'rowClust = as.dendrogram(rowClust)}; '
                 'if (typeof(colClust) != "logical") {'
                    'class(colClust) = "hclust"; '
                    'colClust = as.dendrogram(colClust)}; '
                 'dim(cellnote) = rev(dim(matrix)); '
                 'cellnote = t(cellnote); '
                 'return(heatmap.2(matrix, trace="none", Rowv=rowClust, '
                                  'Colv=colClust, dendrogram=dendrogram, '
                                  'margins=margins, na.rm=TRUE, '
                                  'na.color="white", col=col, breaks=breaks, '
                                  'lhei=c(marginTop,mapHeight), '
                                  'lwid=c(marginLeft,mapWidth), '
                                  'cexRow=cex, cexCol=cex, font=font, '
                                  'key=(min(marginTop, marginLeft) >= 150), '
                                  'keysize=1, cellnote=cellnote, '
                                  'notecex=2, notecol="black"))}')

        tableData = self._getRawData(resDictKey)

        assert isinstance(tableData, TableData)
        matrix = tableData.numpyMatrix
        rowNames = tableData.rowNamesAsNumpyArray
        colNames = tableData.columnNamesAsNumpyArray
        significance = tableData.significanceMatrix
        rowClust = tableData.rowClust
        colClust = tableData.colClust

        rowClust, colClust = [x if x is not None else False for x in [rowClust, colClust]]
        dendrogram = [["both", "row"], ["column", "none"]][rowClust == False][colClust == False]

        hist = numpy.histogram(matrix, bins=[-numpy.Inf,-1-1e-9,0,1+1e-9,numpy.Inf])[0]
        if hist[0] + hist[1] + hist[3] == 0: #Only counts between 0 and 1
            col = r("colorRampPalette(c('black', 'red', 'yellow'))")
            breaks = 82
        elif hist[0] + hist[3] == 0: #Only counts between -1 and 1
            col = r("colorRampPalette(c('cyan', 'blue', 'black', 'red', 'yellow'))")
            breaks = 164
        #elif hist[0] == 0: #Assume unbalanced score, most values between -1 and 0
        #    col = r("colorRampPalette(c('blue', 'black', 'red', 'yellow'))")
        #    matmax = matrix.max()
        #    breaks = r("function(matmax) {c(seq(-1.02,0.98,length=51), seq(1.02,matmax,length=26))}")(matmax)
        elif hist[0] == 0: #Only positive counts
            col = r("colorRampPalette(c('black', 'red', 'yellow'))")
            breaks = 164
        else: #Assumes normal distribution
            col = r("c('#99FFFF',colorRampPalette(c('cyan','blue', 'black', 'red', 'yellow'))(161),'#FFFF66')")
            breaks = r("seq(-4.075,4.075,length=164)")
#        if numpy.argmax(hist) == 1: #Adjust color palette
#            matmax = matrix.max()
#            matmin = matrix.min()
#            if matmin < -1.0:
#                breaks = numpy.arange(matmin,-1.0,(-1.0-matmin)/20)
#                withBlack = True
#            else:
#                breaks = numpy.array([])
#                withBlack = False
#            breaks = numpy.concatenate((breaks, \
#                                       numpy.arange(-1,1,1.0/20)))
#            if matmax > 1.0:
#                breaks = numpy.concatenate((breaks, \
#                                           numpy.arange(1, matmax, (matmax-1.0)/20), \
#                                           numpy.array([matmax])))
#                withWhite = True
#            else:
#                breaks = numpy.concatenate((breaks, \
#                                           numpy.array([1.0])))
#                withWhite = False
#            rFunc = '''
#function(numCols, withBlack, withWhite) {
#    cols = c("red","orange","yellow")
#    if(withBlack) {
#        cols = c("black", cols)
#    }
#    if(withWhite) {
#        cols = c(cols, "white")
#    }
#    colorRampPalette(cols)(numCols)
#}'''
#            col = r(rFunc)(len(breaks)-1, withBlack, withWhite)
#else:
#            col = 'heat.colors'
#            breaks = 80

        cellnote = numpy.zeros(shape=matrix.shape, dtype='S1')
        if significance is not None:
            cellnote[significance] = 'o'

        self._returnDict[resDictKey] = \
            r(rCode)(matrix, [x for x in rowNames], [x for x in colNames], rowClust, colClust, dendrogram, \
                     self._marginLeft, self._marginTop, self._mapHeight, self._mapWidth, \
                     robjects.FloatVector(self._getMarginsInLineHeights()), \
                     self._cex, self.FONT, col, breaks, cellnote.flatten().tolist())

    def _writeRawData(self, resDictKey, fn):
        GraphicsPresenter._writeRawData(self, resDictKey, fn)
        if self._returnDict.get(resDictKey) is not None:
            ensurePathExists(fn)
            open(fn,'a').write(os.linesep + 'Return: ' + str(self._returnDict[resDictKey]))


class HeatmapFromNumpyPresenter(GlobalResultGraphicsMatrixDataFromNumpy, HeatmapPresenter):
    MATRIX_VALUE_KEY = 'Matrix'


class HeatmapFromTableDataPresenter(GlobalResultGraphicsMatrixDataFromTableData, HeatmapPresenter):
    pass


class HeatmapFromDictOfDictsPresenter(GlobalResultGraphicsMatrixDataFromDictOfDicts, HeatmapPresenter):
    def getSingleReference(self):
        return self.getReference(resDictKey=None)
