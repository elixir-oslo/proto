import os
import traceback

import numpy

from gold.application.LogSetup import logging, HB_LOGGER
from gold.result.Presenter import Presenter
from gold.util.CommonFunctions import isNumber
from gold.util.CustomExceptions import AbstractClassError, ShouldNotOccurError,\
                                       SilentError
from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.result.model.TableData import TableData
from quick.util.CommonFunctions import ensurePathExists, silenceRWarnings


#from rpy import r, RException
#from proto.RSetup import r
#from rpy import RException


class GraphicsPresenter(Presenter):
    HIGH_DEF_COLORS = False
    POINT_SIZE = 12
    # LINE_HEIGHT = POINT_SIZE
    maxRawDataPoints = None
    #GraphicsPresenter is abstract class, the following vars will be declared in ancestors..
    #name = ('abstract','Abstract')
    #dataPointLimits = (None,None)
    #rCode = ''

    def __init__(self, results, baseDir, header):
        Presenter.__init__(self, results, baseDir)
        self._header = header
        self._plotResultObject = None #could be set by subclasses, but not guaranteed

    def getDescription(self):
        return self.__class__.name[1]

    def _getDataPointCount(self, resDictKey):
        raise AbstractClassError

    def _checkCorrectData(self, resDictKey):
        return True

    def getReference(self, resDictKey, imageLink=False, fullImage=False):
        try:
            fns = self._getFns(resDictKey)
            if len(fns) == 2:
                figFnPng = None
                figFnPdf, dataFn = fns
            elif len(fns) == 3:
                figFnPng, figFnPdf, dataFn = fns
            else:
                raise ShouldNotOccurError

            robjFn = self._getResultObjectFn(resDictKey)
            if not self._checkCorrectData(resDictKey):
                return HtmlCore().textWithHelp('N/A', self.__class__.name[1] + ' is not available for this type of data.')

            dataPointCount = self._getDataPointCount(resDictKey)
            minPoints = self.__class__.dataPointLimits[0]
            maxPoints = self.__class__.dataPointLimits[1]
            if type(dataPointCount) not in [list, tuple]:
                dataPointCount = [dataPointCount]
            if minPoints != None and min(dataPointCount) < minPoints:
                return HtmlCore().textWithHelp('N/A', self.__class__.name[1] + ' is not available because there were '\
                                               +'too few data points (< %d).' % minPoints)
            elif maxPoints != None and max(dataPointCount) > maxPoints:
                return HtmlCore().textWithHelp('N/A', self.__class__.name[1] + ' is not available because there were '\
                                               +'too many data points (> %d).' % maxPoints)
            else:
                if figFnPng:
                    self._writeContent(resDictKey, figFnPng)
                    figUrlPng = self._getRelativeURL(figFnPng)
                    if imageLink:
                        imgTemplate = '<img src="%s" alt="Figure" width="200"/>' if fullImage == False else '<img src="%s" alt="Figure"/>'
                        figLinkPng=imgTemplate % figUrlPng
                    else:
                        figLinkPng='PNG'
                if figFnPdf:
                    self._writeContent(resDictKey, figFnPdf)
                    figUrlPdf = self._getRelativeURL(figFnPdf)
                    figLinkPdf='PDF'

                self._writeResultObject(resDictKey, robjFn)
                self._writeRawData(resDictKey, dataFn)

                return (str(HtmlCore().link(figLinkPng, figUrlPng)) + '&nbsp;/&nbsp;' if figFnPng else '') +\
                       (str(HtmlCore().link(figLinkPdf, figUrlPdf)) + '&nbsp;/&nbsp;' if figFnPdf else '') +\
                       (str(HtmlCore().link('R&nbsp;object', self._getRelativeURL(robjFn))) + '&nbsp;/&nbsp;' if self._plotResultObject is not None else '') +\
                       str(HtmlCore().link('Raw&nbsp;data', self._getRelativeURL(dataFn)))

        except (Exception), e: #,RException
        #except None,e:
            logging.getLogger(HB_LOGGER).warning('Error in figure generation: ' + str(e))
            logging.getLogger(HB_LOGGER).debug(traceback.format_exc())

            from config.Config import DebugConfig
            if DebugConfig.PASS_ON_FIGURE_EXCEPTIONS:
                raise
        
        return 'Error in figure generation'

    def getPlotDimensions(self, resDictKey):
        return (600, 800)

    def _setOutputDevice(self, fn, height, width):
        from proto.RSetup import r
        if fn.endswith('.pdf'):
            # self.LINE_HEIGHT = self.POINT_SIZE
            r.pdf(fn, height=height*1.0/72, width=width*1.0/72, pointsize=self.POINT_SIZE)
        elif fn.endswith('.png'):
            # if any(x > 800 for x in [width, height]):
            #     if self.HIGH_DEF_COLORS:
            #         picType = 'png16m'
            #     else:
            #         picType = 'png256'
            #
            #     # self.LINE_HEIGHT = self.POINT_SIZE
            #     r.bitmap(fn, height=height, width=width, units='px', type=picType, pointsize=self.POINT_SIZE)
            # else:
            # self.LINE_HEIGHT = self.POINT_SIZE * 1.38 # for r.png(). Don't know why
            r.png(filename=fn, height=height, width=width, units='px',
                  pointsize=self.POINT_SIZE, res=72, type='cairo')
        else:
            raise ShouldNotOccurError
        
    def _writeContent(self, resDictKey, fn):
        from proto.RSetup import r
        ensurePathExists(fn)
        silenceRWarnings()

        self._setOutputDevice(fn, height=100, width=100)
        width, height = self.getPlotDimensions(resDictKey)
        r('dev.off()')

        self._setOutputDevice(fn, height=height, width=width)

        if resDictKey is not None:
            xlab = self._results.getLabelHelpPair(resDictKey)[0]
        else:
            xlab = None

        main = self._header
        self._customRExecution(resDictKey, xlab, main)
        r('dev.off()')

    def _writeResultObject(self, resDictKey, fn):
        if self._plotResultObject is not None:
            ensurePathExists(fn)
            from proto.RSetup import r
            r('function(x, fn) {dput(x, fn)}')(self._plotResultObject, fn)
            #outF = open(fn,'w')
            #outF.write(str(self._plotResultObject) + os.linesep)
            #outF.close()

    def _writeRawData(self, resDictKey, fn):
        ensurePathExists(fn)
        outF = open(fn,'w')

        rawData = self._getRawData(resDictKey, False)
        if self.maxRawDataPoints is None or len(rawData) <= self.maxRawDataPoints:
            if type(rawData) in [list, tuple, numpy.ndarray] and len(rawData)>0 and type(rawData[0]) in [int,float,numpy.int32,numpy.float,numpy.float32, numpy.float64, numpy.float128, numpy.ndarray]:
                if type(rawData) == tuple:
                    for npArr in rawData:
                        print>>outF, ','.join([str(x) for x in npArr])
                else:
                    outF.write( os.linesep.join([str(x) for x in rawData]) )
            else:
                outF.write( str(rawData) )
        outF.close()

    def _getRawData(self, resDictKey, avoidNAs=True):
        raise AbstractClassError

    def _customRExecution(self, resDictKey, xlab, main):
        raise AbstractClassError
        #r('')(self._results.getAllValuesForResDictKey(resDictKey), xlab, main)

    def _getBaseFn(self, resDictKey):
        return os.sep.join([self._baseDir, self._results.getStatClassName() + '_' +\
                              (resDictKey + '_' if not resDictKey is None else '') + self.__class__.name[0]])

    def _getFns(self, resDictKey):
        baseFn = self._getBaseFn(resDictKey)
        return [baseFn + '.png', baseFn + '.pdf', baseFn + '.txt']

    def _getResultObjectFn(self, resDictKey):
        return self._getBaseFn(resDictKey) + '.robj'


class GlobalResultGraphicsData(object):
    def _getRawData(self, resDictKey, avoidNAs=True):
        if self._results.getGlobalResult() is not None and self._results.getGlobalResult().get(resDictKey) is not None:
            return [x for x in self._results.getGlobalResult().get(resDictKey) if x is not None and not (avoidNAs and numpy.isnan(x))]
        else:
            return None

    def _getDataPointCount(self, resDictKey, avoidNAs=True):
        if self._results.getGlobalResult() is not None and self._results.getGlobalResult().get(resDictKey) is not None:
            return len(self._getRawData(resDictKey, avoidNAs))
        else:
            return 0


# class GlobalResultGraphicsMatrixData(object):
#     def _getRawData(self, resDictKey, avoidNAs=False):
#         assert resDictKey is None
#         assert avoidNAs == False
#         if self._results.getGlobalResult() is not None and
#                self._results.getGlobalResult().get(resDictKey) is not None:
#             return [x for x in self._results.getGlobalResult().get(resDictKey)
#                     if x is not None and not (avoidNAs and numpy.isnan(x))]
#         else:
#             return None

class GlobalValueMixin(object):
    def _getDataPointCount(self, resDictKey, avoidNAs=False):
        assert avoidNAs is False
        globalResDict = self._results.getGlobalResult()\

        if resDictKey is not None:
            globalRes = globalResDict.get(resDictKey)
        else:
            globalRes = globalResDict

        if globalRes is not None:
            matrix = self._getRawData(resDictKey, avoidNAs).numpyMatrix
            return len(matrix), len(matrix[0])
        else:
            return 0, 0


class GlobalResultGraphicsMatrixDataFromDictOfDicts(GlobalValueMixin):
    def _getRawData(self, resDictKey, avoidNAs=False):
        if not hasattr(self, '_rawData'):
            assert resDictKey is None
            assert avoidNAs is False

            globalRes = self._results.getGlobalResult()
            resDictKeys = self._results.getResDictKeys()

            if globalRes is not None and \
                    any([type(x) == dict for x in globalRes.values()]):
                tableData = TableData()

                for resDictKey in resDictKeys:
                    if globalRes[resDictKey] is not None:
                        for key in globalRes[resDictKey].keys():
                            tableData[resDictKey][key] = \
                                globalRes[resDictKey].get(key)

                self._rawData = tableData
            else:
                self._rawData = None
        return self._rawData

    def _getDataPointCount(self, resDictKey, avoidNAs=False):
        assert resDictKey is None
        return GlobalValueMixin._getDataPointCount(resDictKey, avoidNAs=avoidNAs)

    def getSingleReference(self):
        return self.getReference(None)



class GlobalResultGraphicsMatrixDataFromNumpy(GlobalValueMixin):
    def _getRawData(self, resDictKey, avoidNAs=False):
        if not hasattr(self, '_rawData'):
            assert avoidNAs is False
            globalRes = self._results.getGlobalResult()

            if globalRes is not None and globalRes.get(resDictKey) is not None:
                matrixDict = globalRes.get(resDictKey)

                if self.MATRIX_VALUE_KEY not in matrixDict:
                    raise SilentError
                else:
                    tableData = TableData()
                    tableData.rowClust = matrixDict.get('RowClust')
                    tableData.colClust = matrixDict.get('ColClust')
                    tableData.rowOrder = matrixDict.get('RowOrder')
                    tableData.colOrder = matrixDict.get('ColOrder')

                    tableData.setByNumpyData(matrixDict[self.MATRIX_VALUE_KEY],
                                             matrixDict['Rows'],
                                             matrixDict['Cols'],
                                             matrixDict.get('Significance'))
                    self._rawData = tableData
            else:
                self._rawData = None
        return self._rawData


class GlobalResultGraphicsMatrixDataFromTableData(GlobalValueMixin):
    def _getRawData(self, resDictKey, avoidNAs=False):
        assert avoidNAs is False
        return self._results.getGlobalResult().get(resDictKey)


class LocalResultsGraphicsData(object):
    def _checkCorrectData(self, resDictKey):
        resList = self._results.getAllValuesForResDictKey(resDictKey)
        return len(resList) > 0 and any(isNumber(x) for x in resList)

    def _getRawData(self, resDictKey, avoidNAs=True):
        return [x for x in self._results.getAllValuesForResDictKey(resDictKey)
                if x is not None and (type(x) is not list)
                and not (avoidNAs and numpy.isnan(x))]

    def _getDataPointCount(self, resDictKey, avoidNAs=True):
        return len(self._getRawData(resDictKey, avoidNAs))
