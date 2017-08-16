from collections import OrderedDict
import math
import numpy as np

from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.util.GenomeInfo import GenomeInfo
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.restricted.visualization.visualizationGraphs import visualizationGraphs
from quick.webtools.plot.RainfallPlot import RP


# author DD


class GenerateDistributionOfPointsOfInterestTool(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Create density of distribution"

    @staticmethod
    def getInputBoxNames():
        return [
            ('Select GSuite with data', 'gsuite'),
            ('Select file with regions (bed)', 'bedRegions')
        ]

    @staticmethod
    def getOptionsBoxGsuite():
        return '__history__', 'gsuite'

    @staticmethod
    def getOptionsBoxBedRegions(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement('bed')

    @staticmethod
    def getOutputFormat(choices):
        return 'customhtml'

    @staticmethod
    def validateAndReturnErrors(choices):
        if not choices.gsuite:
            return "Please select a GSuite from history"
        if not choices.bedRegions:
            return "Please select a bed file with regions"
        return None

    @staticmethod
    def getToolDescription():

        htmlCore = HtmlCore()

        htmlCore.paragraph('The tool is used to generate density of distribution.')

        htmlCore.divider()

        htmlCore.paragraph('The input for tool is following:')
        htmlCore.line('- GSuite')
        htmlCore.line('- file with regions (bed format), which should be given by user')

        htmlCore.divider()

        htmlCore.paragraph('The output for tool is a plot.')

        return str(htmlCore)

    @staticmethod
    def isPublic():
        return True

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):

        gsuite = getGSuiteFromGalaxyTN(choices.gsuite)
        bedRegions = choices.bedRegions

        rp = RP(gsuite)
        bedData = rp.openBedFile(bedRegions)
        chrOrder, chrLength = rp.sortChrDict()
        dataDict, dataDictLine, elementOrder, listResCopy, newDictRegions = rp.countMutations(chrLength, bedData)

        vg = visualizationGraphs()
        tName = gsuite.allTrackTitles()


        uniformDictList = OrderedDict()  # expected values
        observedDictList = OrderedDict()  # observed values
        seriesNameRegionUDL = OrderedDict()
        seriesNameRegionODL = OrderedDict()
        seriesNameRegion = OrderedDict()

        GenerateDistributionOfPointsOfInterestTool.countRegionsForDistribution(newDictRegions, observedDictList, rp,
                                                                               seriesNameRegion, seriesNameRegionODL,
                                                                               seriesNameRegionUDL, tName,
                                                                               uniformDictList)
        res=''
        for elK in uniformDictList.keys():
            res += GenerateDistributionOfPointsOfInterestTool.drawDistribution(elK, observedDictList,
                                                                              seriesNameRegion, seriesNameRegionODL,
                                                                              seriesNameRegionUDL, uniformDictList, vg)

        htmlCore = HtmlCore()
        htmlCore.begin()
        htmlCore.line(res)
        htmlCore.end()
        htmlCore.hideToggle(styleClass='debug')
        print htmlCore

    @staticmethod
    def drawDistribution(elK, observedDictList, seriesNameRegion, seriesNameRegionODL, seriesNameRegionUDL,
                         uniformDictList, vg):
        res=''
        ww = elK.split('-')
        nELK = str(elK) + ' region size:  ' + str(int(ww[2]) - int(ww[1]))
        seriesNameRegion[elK] =  seriesNameRegionODL[elK] + seriesNameRegionUDL[elK]

        if len(uniformDictList[elK]) != 0 and len(observedDictList[elK]) != 0:

            udl = uniformDictList[elK]
            odl = observedDictList[elK]
            snl = seriesNameRegion[elK]

            indexListEmpty = []
            for elEmpty in range(0, len(udl)):
                if len(uniformDictList[elK][elEmpty]) == 0:
                    indexListEmpty.append(elEmpty)
            for elEmpty in range(0, len(observedDictList[elK])):
                if len(observedDictList[elK][elEmpty]) == 0 and elEmpty not in indexListEmpty:
                    indexListEmpty.append(elEmpty)

            if len(indexListEmpty) != 0:
                # udl = np.delete(udl, indexListEmpty).tolist()

                odl = np.delete(odl, indexListEmpty).tolist()

                # double number of indexes (because of udl + odl)
                indexListEmpty = indexListEmpty + [n + len(uniformDictList[elK]) for n in indexListEmpty]

                snl = np.delete(snl, indexListEmpty).tolist()

            res = GenerateDistributionOfPointsOfInterestTool.drawLineDistribution(nELK, odl, res, snl, udl, vg)

        return res

    @staticmethod
    def drawLineDistribution(nELK, odl, res, snl, udl, vg):
        res += vg.drawLineChart(
            #odl + udl,
            odl,
            seriesName=snl,
            height=300,
            titleText=nELK,
            yAxisTitle='[log10]',
        )
        res += '<div style="clear:both;"> </div>'
        return res

    @staticmethod
    def countRegionsForDistribution(newDictRegions, observedDictList, rp, seriesNameRegion, seriesNameRegionODL,
                                    seriesNameRegionUDL, tName, uniformDictList):
        for regKey in newDictRegions.keys():
            # counting uniform distribution

            for regChr, regList in newDictRegions[regKey].items():

                if not regChr in uniformDictList:
                    uniformDictList[regChr] = []
                    observedDictList[regChr] = []
                    seriesNameRegionUDL[regChr] = []
                    seriesNameRegionODL[regChr] = []
                    seriesNameRegion[regChr] = []

                numMut = len(regList)

                stChr = regChr.split('-')[1]
                endChr = regChr.split('-')[2]
                intervalLen = int(endChr) - int(stChr)

                uniformDictList[regChr].append(
                    rp.countPoissonDistribution(numMut, intervalLen))
                seriesNameRegionUDL[regChr].append(str(tName[regKey]) + ' - ' + 'expected')

                observedDictList[regChr].append(rp.countHist(regList))
                seriesNameRegionODL[regChr].append(
                    str(tName[regKey]) + ' - ' + 'observed dist num:' + str(len(regList)))



    #@staticmethod
    #def getSubToolClasses():
    #    '''
    #    Specifies a list of classes for subtools of the main tool. These
    #    subtools will be selectable from a selection box at the top of the page.
    #    The input boxes will change according to which subtool is selected.
    #    '''
    #    return None
    #
    #@staticmethod
    #def isPublic():
    #    '''
    #    Specifies whether the tool is accessible to all users. If False, the
    #    tool is only accessible to a restricted set of users as defined in
    #    LocalOSConfig.py.
    #    '''
    #    return False
    #
    #@staticmethod
    #def isRedirectTool():
    #    '''
    #    Specifies whether the tool should redirect to an URL when the Execute
    #    button is clicked.
    #    '''
    #    return False
    #
    #@staticmethod
    #def getRedirectURL(choices):
    #    '''
    #    This method is called to return an URL if the isRedirectTool method
    #    returns True.
    #    '''
    #    return ''
    #
    #@staticmethod
    #def isHistoryTool():
    #    '''
    #    Specifies if a History item should be created when the Execute button is
    #    clicked.
    #    '''
    #    return True
    #
    #@classmethod
    #def isBatchTool(cls):
    #    '''
    #    Specifies if this tool could be run from batch using the batch. The
    #    batch run line can be fetched from the info box at the bottom of the
    #    tool.
    #    '''
    #    return cls.isHistoryTool()
    #
    #@staticmethod
    #def isDynamic():
    #    '''
    #    Specifies whether changing the content of texboxes causes the page to
    #    reload.
    #    '''
    #    return True
    #
    #@staticmethod
    #def getResetBoxes():
    #    '''
    #    Specifies a list of input boxes which resets the subsequent stored
    #    choices previously made. The input boxes are specified by index
    #    (starting with 1) or by key.
    #    '''
    #    return []
    #
    #@staticmethod
    #def getToolDescription():
    #    '''
    #    Specifies a help text in HTML that is displayed below the tool.
    #    '''
    #    return ''
    #
    #@staticmethod
    #def getToolIllustration():
    #    '''
    #    Specifies an id used by StaticFile.py to reference an illustration file
    #    on disk. The id is a list of optional directory names followed by a file
    #    name. The base directory is STATIC_PATH as defined by AutoConfig.py. The
    #    full path is created from the base directory followed by the id.
    #    '''
    #    return None
    #
    #@staticmethod
    #def getFullExampleURL():
    #    return None
    #
    #@staticmethod
    #def isDebugMode():
    #    '''
    #    Specifies whether the debug mode is turned on.
    #    '''
    #    return False
    #
    #@staticmethod
    #def getOutputFormat(choices):
    #    '''
    #    The format of the history element with the output of the tool. Note
    #    that html output shows print statements, but that text-based output
    #    (e.g. bed) only shows text written to the galaxyFn file.In the latter
    #    case, all all print statements are redirected to the info field of the
    #    history item box.
    #    '''
    #    return 'html'
