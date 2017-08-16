import copy
import csv
import itertools
import math
import numpy as np
import operator
import os
import urllib
import urllib2
from collections import OrderedDict
from collections import defaultdict
from urllib import quote

from proto.hyperbrowser.HtmlCore import HtmlCore
from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile

from gold.application.HBAPI import GlobalBinSource, PlainTrack
from gold.application.HBAPI import doAnalysis
from gold.description.AnalysisDefHandler import AnalysisSpec
from gold.gsuite import GSuiteComposer
from gold.gsuite import GSuiteConstants
from gold.gsuite.GSuite import GSuite
from gold.gsuite.GSuiteConstants import TITLE_COL
from gold.gsuite.GSuiteTrack import GSuiteTrack, GalaxyGSuiteTrack
from gold.result.MatrixGlobalValuePresenter import \
    MatrixGlobalValueFromTableDataPresenter
from gold.track.Track import Track
from gold.util import CommonConstants
from gold.util.CommonFunctions import strWithStdFormatting
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.application.GalaxyInterface import GalaxyInterface
from quick.application.UserBinSource import UserBinSource
from quick.gsuite.GSuiteUtils import getAllTracksWithAttributes
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.statistic.GSuiteVsGSuiteWrapperStat import GSuiteVsGSuiteWrapperStat
from quick.statistic.MaxElementValueStat import MaxElementValueStat
from quick.statistic.RawOverlapToSelfStat import RawOverlapToSelfStat
from quick.statistic.RipleysKStat import RipleysKStat
from quick.statistic.SumTrackPointsStat import SumTrackPointsStat
from quick.util.CommonFunctions import ensurePathExists, silenceRWarnings
from quick.util.GenomeInfo import GenomeInfo
from quick.util.TrackReportCommon import STAT_OVERLAP_COUNT_BPS, \
    STAT_OVERLAP_RATIO, STAT_FACTOR_OBSERVED_VS_EXPECTED, processRawResults, processResult, \
    STAT_COVERAGE_RATIO_VS_REF_TRACK, STAT_COVERAGE_RATIO_VS_QUERY_TRACK, \
    STAT_LIST_INDEX
from quick.webtools.GeneralGuiTool import MultiGeneralGuiTool, GeneralGuiTool, HistElement
from quick.webtools.mixin.DebugMixin import DebugMixin
from quick.webtools.mixin.GenomeMixin import GenomeMixin
from quick.webtools.mixin.UserBinMixin import UserBinMixin
from quick.webtools.restricted.visualization.visualizationGraphs import visualizationGraphs


####
##
##


# alt + enter
# cmd + shift + O
# double shift
# cmd + B
# ctrl + space (shortcut for complit the sentence)
# alt + slash



####
##
##




class DianasTool(MultiGeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Diana's tool"

    @staticmethod
    def isPublic():
        '''
        Specifies whether the tool is accessible to all users. If False, the
        tool is only accessible to a restricted set of users as defined in
        LocalOSConfig.py.
        '''
        return True

    @staticmethod
    def getSubToolClasses():
        return [GenerateRipleysK, GenerateTwoLevelOverlapPreferenceStat, DivideBedFileForChosenPhrase, \
                KseniagSuite, gSuiteName, divideGSuite, removeStringFromGSuite, VisTrackFrequency, \
                VisTrackFrequencyBetweenTwoTracks, gSuiteInverse, showGSuiteResultsInTable, \
                divideBedFile, divideBedFileV2, removeFromBedFile, GenerateRipleysKForEachChromosomeSeparately, \
                rainfallPlots, makeRainfallPlots, rainfallPlotsGSuite, miRNAPrecursors, rankingTFtracks,
                rankingTFtracks2, mRNATool, \
                divideBedFileTool, driverGeneIdentification, rankingTFtracks3, \
                geneExpressionV4, geneExpressionCutOff, geneExpressionCutOffTrack, geneExpressionHist, \
                geneExpressionMaxValue, kmerGSuite, rainfallBuildNewFile, analyseDeepGsuite, analyseDeepGsuiteV2, \
                examTool1, statGSuite, kmers, kmersAddMut, kmersTab, bedIntoRFile, justCutOffValue, trfFromFasta,
                trfFromGSuite, \
                workflow10, workflow11, workflow12, workflow13, workflowAllInOne, rainfallPlotsSynthetic,
                createRainfallPlot, createRainfallPlotWithRegions, \
                createRainfallPlotWithRegionsGsuite, intersectionGSuite, mergeTracksFromGSuite,
                createRainfallPlotWithBinRegions]


# geneExpression, geneExpressionV2, geneExpressionV3,


class workflowAllInOne(GeneralGuiTool):
    PATH_BOWTIE = "/software/VERSIONS/bowtie-0.12.7/bowtie"
    SELECT = '--- Select ---'

    # Select boxes
    SELECT_OPERATION = 'Select operation'
    SELECT_DATASET = 'Do you want to use only file in your history'
    SELECT_SPECIES = 'Select species (group number 0)'
    SELECT_GSUITE_1 = 'Select gsuite 1'
    SELECT_GROUP_GSUITE_1 = 'Select group for gsuite 1'
    SELECT_GSUITE_2 = 'Select gsuite 2'
    SELECT_GROUP_GSUITE_2 = 'Select group for gsuite 2'
    SELECT_GSUITE_3 = 'Select gsuite 3'
    SELECT_GROUP_GSUITE_3 = 'Select group for gsuite 3'
    SELECT_GROUPED_GSUITE = 'Select grouped gsuite'
    SELECT_GENOME_FILE = 'Select genome file'
    SELECT_SAM_GSUITE = 'Select sam gsuite'
    SELECT_MS_FILE = 'Select mature/star file'
    SELECT_MIN_NUMBER_OF_NUCLEOTIDES = 'Select minimal number of nucleotides'
    SELECT_MS_GSUITE = 'Select ms gsuite'
    CHANGE_GSUITE_GROUP = 'Your group number is equal: '
    CHANGE_GSUITE_GROUP1 = 'Change group for gsuite'
    CHANGE_GROUP1 = 'Change group'
    CHANGE_GSUITE_GROUP2 = 'Change group for gsuite'
    CHANGE_GROUP2 = 'Change group'
    CHANGE_GSUITE_GROUP3 = 'Change group for gsuite'
    CHANGE_GROUP3 = 'Change group'

    SELECT = ' -- Select --'
    FILE_SELECTOR = '-----'

    # Options
    SPECIES_LIST = ['Human', 'Mouse']

    # Operations
    OPERATION_GROUP = 'Choose groups'
    OPERATION_SAM = 'Samfiles'
    OPERATION_MS = 'Count mature/star files'
    OPERATION_CLUST = 'Cluster'
    OPERATION_GENE_EXPRESSION = 'Gene expression'

    # Output files
    HIST_GROUPED_GSUITE = 'grouped Gsuite'
    HIST_SAM_GSUITE = 'SAM Gsuite'
    HIST_MS_GSUITE = 'MS Gsuite'

    # Output table
    TABLE_HEADER_CLUST = 'Clustering images'
    TABLE_HEADER_GE = 'Gene expression images'
    SHOW_FILE = 'Show file '

    cacheGroupNumber = []
    cacheGroupTable = []

    @staticmethod
    def getToolName():
        return "Workflow all in one"

    @staticmethod
    def getInputBoxNames():

        return [
            (workflowAllInOne.SELECT_OPERATION, 'operation'),
            (workflowAllInOne.SELECT_DATASET, 'dataset'),
            (workflowAllInOne.SELECT_SPECIES, 'speciesList'),
            (workflowAllInOne.SELECT_GSUITE_1, 'gsuite1'),
            (workflowAllInOne.SELECT_GROUP_GSUITE_1, 'group1'),
            (workflowAllInOne.SELECT_GSUITE_2, 'gsuite2'),
            (workflowAllInOne.SELECT_GROUP_GSUITE_2, 'group2'),
            (workflowAllInOne.SELECT_GSUITE_3, 'gsuite3'),
            (workflowAllInOne.SELECT_GROUP_GSUITE_3, 'group3'),
            (workflowAllInOne.SELECT_GROUPED_GSUITE, 'groupedFile'),
            (workflowAllInOne.SELECT_GENOME_FILE, 'hsaFas'),
            (workflowAllInOne.SELECT_SAM_GSUITE, 'samFile'),
            (workflowAllInOne.SELECT_MS_FILE, 'file'),
            (workflowAllInOne.SELECT_MIN_NUMBER_OF_NUCLEOTIDES, 'number'),
            (workflowAllInOne.SELECT_MS_GSUITE, 'msFile'),
            (workflowAllInOne.CHANGE_GSUITE_GROUP, 'changeGroup'),
            (workflowAllInOne.CHANGE_GSUITE_GROUP1, 'changeGsuiteGroup1'),
            (workflowAllInOne.CHANGE_GROUP1, 'changeGroup1'),
            (workflowAllInOne.CHANGE_GSUITE_GROUP2, 'changeGsuiteGroup2'),
            (workflowAllInOne.CHANGE_GROUP2, 'changeGroup2'),
            (workflowAllInOne.CHANGE_GSUITE_GROUP3, 'changeGsuiteGroup3'),
            (workflowAllInOne.CHANGE_GROUP3, 'changeGroup3'),
        ]

    @staticmethod
    def getOptionsBoxOperation():
        return OrderedDict([(workflowAllInOne.OPERATION_GROUP, False),
                            (workflowAllInOne.OPERATION_SAM, False),
                            (workflowAllInOne.OPERATION_MS, False),
                            (workflowAllInOne.OPERATION_CLUST, False),
                            (workflowAllInOne.OPERATION_GENE_EXPRESSION, False)
                            ])

    @staticmethod
    def getOptionsBoxDataset(prevChoices):
        oper = prevChoices.operation
        for val in oper.values():
            if val == True:
                return ['yes', 'no']

    @staticmethod
    def getOptionsBoxSpeciesList(prevChoices):
        oper = prevChoices.operation
        for val in oper.values():
            if val == True and prevChoices.dataset == 'no':
                return workflowAllInOne.SPECIES_LIST

    @staticmethod
    def getOptionsBoxQuestion1(prevChoices):
        if prevChoices.dataset == 'yes' and prevChoices.operation[workflowAllInOne.OPERATION_GROUP] == True:
            return ['yes', 'no']

    @staticmethod
    def getOptionsBoxGsuite1(prevChoices):
        if prevChoices.dataset == 'yes' and prevChoices.operation[workflowAllInOne.OPERATION_GROUP] == True:
            return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @staticmethod
    def getOptionsBoxGroup1(prevChoices):
        if prevChoices.dataset == 'yes' and prevChoices.operation[workflowAllInOne.OPERATION_GROUP] == True:
            return ['1', '2', '3']

    @staticmethod
    def getOptionsBoxGsuite2(prevChoices):
        if prevChoices.dataset == 'yes' and prevChoices.operation[workflowAllInOne.OPERATION_GROUP] == True:
            if prevChoices.gsuite1:
                return GeneralGuiTool.getHistorySelectionElement('gsuite')
            else:
                return

    @staticmethod
    def getOptionsBoxGroup2(prevChoices):
        if prevChoices.dataset == 'yes' and prevChoices.operation[workflowAllInOne.OPERATION_GROUP] == True:
            if prevChoices.gsuite1:
                return ['1', '2', '3']
            else:
                return

    @staticmethod
    def getOptionsBoxGsuite3(prevChoices):
        if prevChoices.dataset == 'yes' and prevChoices.operation[workflowAllInOne.OPERATION_GROUP] == True:
            if prevChoices.gsuite2:
                return GeneralGuiTool.getHistorySelectionElement('gsuite')
            else:
                return

    @staticmethod
    def getOptionsBoxGroup3(prevChoices):
        if prevChoices.dataset == 'yes' and prevChoices.operation[workflowAllInOne.OPERATION_GROUP] == True:
            if prevChoices.gsuite2:
                return ['1', '2', '3']
            else:
                return

    @staticmethod
    def getOptionsBoxGroupedFile(prevChoices):
        if prevChoices.operation[workflowAllInOne.OPERATION_GROUP] == False:
            if prevChoices.operation[workflowAllInOne.OPERATION_SAM] == True:
                return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @staticmethod
    def getOptionsBoxHsaFas(prevChoices):
        oper = prevChoices.operation
        for val in oper.values():
            if val == True:
                if prevChoices.dataset == 'yes':
                    if prevChoices.operation[workflowAllInOne.OPERATION_SAM] == True:
                        return GeneralGuiTool.getHistorySelectionElement('fa', 'fasta', 'fas')

    @staticmethod
    def getOptionsBoxSamFile(prevChoices):
        if prevChoices.operation[workflowAllInOne.OPERATION_SAM] == False:
            if prevChoices.operation[workflowAllInOne.OPERATION_MS] == True:
                return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @staticmethod
    def getOptionsBoxFile(prevChoices):
        if prevChoices.dataset == 'yes' and prevChoices.operation[workflowAllInOne.OPERATION_MS] == True:
            return GeneralGuiTool.getHistorySelectionElement()

    @staticmethod
    def getOptionsBoxNumber(prevChoices):
        if prevChoices.operation[workflowAllInOne.OPERATION_MS] == True:
            return '0'

    @staticmethod
    def getOptionsBoxMsFile(prevChoices):
        if prevChoices.operation[workflowAllInOne.OPERATION_MS] == False:
            if prevChoices.operation[workflowAllInOne.OPERATION_CLUST] == True or prevChoices.operation[
                workflowAllInOne.OPERATION_GENE_EXPRESSION] == True:
                return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @staticmethod
    def getOptionsBoxChangeGroup(prevChoices):
        if prevChoices.operation[workflowAllInOne.OPERATION_MS] == False:
            if prevChoices.operation[workflowAllInOne.OPERATION_GENE_EXPRESSION] == True:
                if prevChoices.msFile:
                    gsuiteMS = getGSuiteFromGalaxyTN(prevChoices.msFile)
                    workflowAllInOne.cacheGroupNumber, workflowAllInOne.cacheGroupTable = workflowAllInOne.checkGroups(
                        gsuiteMS)

                    if workflowAllInOne.cacheGroupNumber != 2:
                        return [str(len(workflowAllInOne.cacheGroupNumber))]

    @staticmethod
    def getOptionsBoxChangeGsuiteGroup1(prevChoices):
        return workflowAllInOne.returnGsuiteGroup(prevChoices, 1)

    @staticmethod
    def getOptionsBoxChangeGroup1(prevChoices):
        return workflowAllInOne.returnGroup(prevChoices, 1)

    @staticmethod
    def getOptionsBoxChangeGsuiteGroup2(prevChoices):
        return workflowAllInOne.returnGsuiteGroup(prevChoices, 2)

    @staticmethod
    def getOptionsBoxChangeGroup2(prevChoices):
        return workflowAllInOne.returnGroup(prevChoices, 2)

    @staticmethod
    def getOptionsBoxChangeGsuiteGroup3(prevChoices):
        return workflowAllInOne.returnGsuiteGroup(prevChoices, 3)

    @staticmethod
    def getOptionsBoxChangeGroup3(prevChoices):
        return workflowAllInOne.returnGroup(prevChoices, 3)

    @staticmethod
    def returnGsuiteGroup(prevChoices, number):
        if prevChoices.operation[workflowAllInOne.OPERATION_MS] == False and prevChoices.operation[workflowAllInOne.OPERATION_GENE_EXPRESSION] == True and prevChoices.msFile:
            if int(prevChoices.changeGroup) != 2:
                if int(len(workflowAllInOne.cacheGroupNumber)) != 2:
                    if len(workflowAllInOne.cacheGroupTable)!=0:
                        cgs = map(list, zip(*workflowAllInOne.cacheGroupTable))
                        gsuiteUnique = list(set(cgs[1][1:]))
                        if len(gsuiteUnique) >= int(number):
                            return gsuiteUnique

    @staticmethod
    def returnGroup(prevChoices, number):
        if prevChoices.operation[workflowAllInOne.OPERATION_MS] == False and prevChoices.operation[
            workflowAllInOne.OPERATION_GENE_EXPRESSION] == True and prevChoices.msFile:
            if int(prevChoices.changeGroup) != 2:
                if int(len(workflowAllInOne.cacheGroupNumber)) != 2:
                    if '0' in workflowAllInOne.cacheGroupNumber:
                        return [workflowAllInOne.SELECT, '0', '1']
                    else:
                        return [workflowAllInOne.SELECT, '1', '2']

    @classmethod
    def checkGroups(cls, gsuiteMS):

        groupEl = []

        i = 0
        for gsTrack in gsuiteMS.allTracks():
            if i == 0:
                filename = gsTrack.title
                with open(gsTrack.path, 'rb') as f:
                    readCsv = csv.reader(f, delimiter='\t', quotechar='|')
                    j = 0
                    lineList = []
                    for line in readCsv:
                        if j == 0:
                            lineListNew = []
                            u = 0
                            for el in line:
                                if u == 0:
                                    lineListNew.append([el] + ['gsuite name'])
                                else:
                                    lineListNew.append(el.split(workflowAllInOne.FILE_SELECTOR))
                                u += 1
                        elif j == 1:
                            u = 0
                            for el in line:
                                if u >= 1:
                                    if not el in groupEl:
                                        groupEl.append(el)
                                lineListNew[u].append(el)
                                u += 1
                            lineList.append(line)
                        j += 1
            i += 1

        return groupEl, lineListNew

    @classmethod
    def getExtraHistElements(cls, prevChoices):

        outputList = []
        if prevChoices.operation[workflowAllInOne.OPERATION_GROUP] == True:
            outputList.append(HistElement(workflowAllInOne.HIST_GROUPED_GSUITE, 'gsuite'))
        if prevChoices.operation[workflowAllInOne.OPERATION_SAM] == True:
            outputList.append(HistElement(workflowAllInOne.HIST_SAM_GSUITE, 'gsuite'))
        if prevChoices.changeGroup != None and int(prevChoices.changeGroup) != 2:
            outputList.append(HistElement(workflowAllInOne.HIST_MS_GSUITE, 'gsuite'))
        if prevChoices.operation[workflowAllInOne.OPERATION_MS] == True:
            outputList.append(HistElement(workflowAllInOne.HIST_MS_GSUITE, 'gsuite'))

        return outputList

    @classmethod
    def validateAndReturnErrors(cls, choices):

        if len(workflowAllInOne.cacheGroupNumber) != 0 and len(workflowAllInOne.cacheGroupNumber) != 2:

            htmlCore = HtmlCore()

            groupUnique = []
            groupNumberNew = 0
            if choices.changeGroup1 and choices.changeGroup1 != workflowAllInOne.SELECT:
                groupNumberNew += 1
                if not choices.changeGroup1 in groupUnique:
                    groupUnique.append(choices.changeGroup1)
            if choices.changeGroup2 and choices.changeGroup2 != workflowAllInOne.SELECT:
                groupNumberNew += 1
                if not choices.changeGroup2 in groupUnique:
                    groupUnique.append(choices.changeGroup2)
            if choices.changeGroup3 and choices.changeGroup3 != workflowAllInOne.SELECT:
                groupNumberNew += 1
                if not choices.changeGroup3 in groupUnique:
                    groupUnique.append(choices.changeGroup3)

            if len(workflowAllInOne.returnGsuiteGroup(choices, 1)) - int(groupNumberNew) < 2:
                if len(groupUnique) != 2:
                    htmlCore.line('You need to have at least two gsuites with groups which have different number.')
                    return htmlCore
                else:
                    return
            else:
                htmlCore.line('You need to change groups for at least two gsuites. They need to be unique')
                htmlCore.line('Yor number of unchosen groups is equal: ' + str(
                    len(workflowAllInOne.returnGsuiteGroup(choices, 1)) - int(groupNumberNew)))

                return htmlCore

            if int(len(workflowAllInOne.cacheGroupNumber)) > 2:

                htmlCore.line('To draw Vulcano plot you can have only two groups.')
                gsuiteMS = getGSuiteFromGalaxyTN(choices.msFile)

                i = 0
                htmlCore.line('Your group number is equal: ' + str(len(workflowAllInOne.cacheGroupNumber)))
                for line in workflowAllInOne.cacheGroupTable:
                    if i == 0:
                        htmlCore.tableHeader(line, sortable=True, tableId='groupTable')
                    else:
                        htmlCore.tableLine(line)
                    i += 1
                htmlCore.tableFooter()

            htmlCore.end()

            return htmlCore

        else:
            return

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        silenceRWarnings()

        htmlCore = HtmlCore()

        if choices.operation[workflowAllInOne.OPERATION_GROUP] == 'True':
            gsuiteList = []
            gsuiteGroup = []
            gsuiteName = []

            if choices.dataset == 'no':
                species = choices.speciesList
                # build the gsuite from fasta files according to parameters and then give a link to that gsuite
                # link to species gsuite Human

                # gsuite1 = getGSuiteFromGalaxyTN(choices.gsuite1)
                # group1 = int(choices.group1)
                # gsuiteList.append(gsuite1)
                # gsuiteGroup.append('0')

            if choices.gsuite1:
                gsuite1 = getGSuiteFromGalaxyTN(choices.gsuite1)
                group1 = int(choices.group1)
                gsuiteList.append(gsuite1)
                gsuiteGroup.append(group1)
                gsuiteName.append(choices.gsuite1)

            if choices.gsuite2:
                gsuite2 = getGSuiteFromGalaxyTN(choices.gsuite2)
                group2 = int(choices.group2)
                gsuiteList.append(gsuite2)
                gsuiteGroup.append(group2)
                gsuiteName.append(choices.gsuite2)

            if choices.gsuite3:
                gsuite3 = getGSuiteFromGalaxyTN(choices.gsuite3)
                group3 = int(choices.group3)
                gsuiteList.append(gsuite3)
                gsuiteGroup.append(group3)
                gsuiteName.append(choices.gsuite3)

            groupedFile = workflowAllInOne.groupGsuite(gsuiteList, gsuiteGroup, gsuiteName)

            htmlCore.line(
                'You created group for every gSuite. The file called "grouped gsuite" and you can find it in the history.')

        if choices.operation[workflowAllInOne.OPERATION_SAM] == 'True':

            if choices.groupedFile:
                groupedFile = getGSuiteFromGalaxyTN(choices.groupedFile)

            if choices.dataset == 'yes':
                hsaFasName = choices.hsaFas
                hsaFas = ExternalTrackManager.extractFnFromGalaxyTN(hsaFasName.split(':'))
            else:
                # add path to human
                hsaFas = ''

            samFile = workflowAllInOne.buildSamGsuite(groupedFile, galaxyFn, hsaFas)
            GSuiteComposer.composeToFile(samFile, cls.extraGalaxyFn[workflowAllInOne.HIST_SAM_GSUITE])

            htmlCore.line(
                'You created sam files with your parameter. The file called "sam gsuite" and you can find it in the history.')

        if choices.operation[workflowAllInOne.OPERATION_MS] == 'True':

            if choices.samFile:
                samFile = getGSuiteFromGalaxyTN(choices.samFile)

            number = int(choices.number)

            if choices.dataset == 'no':
                species = choices.speciesList
                # give link to Human mature file

            if choices.file:
                fileMature = choices.file

            msFile = workflowAllInOne.countMS(samFile, number, fileMature, galaxyFn)
            GSuiteComposer.composeToFile(msFile, cls.extraGalaxyFn[workflowAllInOne.HIST_MS_GSUITE])

        htmlCore.begin()
        htmlCore.divBegin('resultsDiv')

        header = []
        imageLinksCL = OrderedDict()
        if choices.operation[workflowAllInOne.OPERATION_CLUST] == 'True':
            header.append(workflowAllInOne.TABLE_HEADER_CLUST)

            if choices.msFile:
                msFile = getGSuiteFromGalaxyTN(choices.msFile)

            imageName = 'clust'
            imageLinksCL = workflowAllInOne.showClusterOutput(htmlCore, msFile, galaxyFn, imageName)



        imageLinksGEI = OrderedDict()
        if choices.operation[workflowAllInOne.OPERATION_GENE_EXPRESSION] == 'True':
            header.append(workflowAllInOne.TABLE_HEADER_GE)

            if choices.msFile:
                msFile = getGSuiteFromGalaxyTN(choices.msFile)

            imageName = 'vulcano'

            if int(choices.changeGroup) != 2:
                print 'The msFile was counted one more time'

                changeGroup = {}
                if choices.changeGroup1 != workflowAllInOne.SELECT:
                    if not choices.changeGsuiteGroup1 in changeGroup:
                        changeGroup[choices.changeGsuiteGroup1] = choices.changeGroup1

                if choices.changeGroup2 != workflowAllInOne.SELECT:
                    if not choices.changeGsuiteGroup2 in changeGroup:
                        changeGroup[choices.changeGsuiteGroup2] = choices.changeGroup2

                if choices.changeGroup3 != workflowAllInOne.SELECT:
                    if not choices.changeGsuiteGroup3 in changeGroup:
                        changeGroup[choices.changeGsuiteGroup3] = choices.changeGroup3

                msFile = workflowAllInOne.doChangeMSFile(msFile, galaxyFn, changeGroup)
                GSuiteComposer.composeToFile(msFile, cls.extraGalaxyFn[workflowAllInOne.HIST_MS_GSUITE])


            imageLinksGEI = workflowAllInOne.showClusterOutput(htmlCore, msFile, galaxyFn, imageName)

        if len(header) > 0:
            htmlCore.tableHeader(header, sortable=False, tableId='resultsTable')

            if len(imageLinksCL.keys()) > 0 and len(imageLinksGEI.keys()) > 0:
                i = 0
                for key1, it1 in imageLinksCL.iteritems():
                    htmlCore.tableLine([it1.getLink(workflowAllInOne.SHOW_FILE + str(key1))] +
                                       [imageLinksGEI.values()[i].getLink(
                                           workflowAllInOne.SHOW_FILE + str(imageLinksGEI.keys()[i]))])
                    i += 1
            else:
                if len(imageLinksCL) > 0:
                    for filename in imageLinksCL:
                        htmlCore.tableLine([imageLinksCL[filename].getLink(workflowAllInOne.SHOW_FILE + str(filename))])
                if len(imageLinksGEI) > 0:
                    for filename in imageLinksGEI:
                        htmlCore.tableLine(
                            [imageLinksGEI[filename].getLink(workflowAllInOne.SHOW_FILE + str(filename))])

            htmlCore.tableFooter()

        htmlCore.end()

        print htmlCore


    @classmethod
    def doChangeMSFile(cls, msFile, galaxyFn, changeGroup):

        outGSuite = GSuite()
        for gsTrack in msFile.allTracks():

            uri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn,
                                                extraFileName=gsTrack.title,
                                                suffix='tabular')

            gSuiteTrack = GSuiteTrack(uri)
            outFn = gSuiteTrack.path
            ensurePathExists(outFn)

            workflowAllInOne.openGsuiteMS(gsTrack, outFn, changeGroup)


            outGSuite.addTrack(GSuiteTrack(uri, title=''.join(gsTrack.title), genome=None))
        return outGSuite


    @classmethod
    def buildFile(cls, outFn, content):
        with open(outFn, 'w') as contentF:
            contentF.write(content)
        contentF.close()




    @classmethod
    def openGsuiteMS(cls, gsTrack, uri, changeGroup):

        filename = gsTrack.title
        with open(gsTrack.path, 'rb') as f:
            readCsv = csv.reader(f, delimiter='\t', quotechar='|')
            j = 0
            strReadCsv = ''
            for line in readCsv:
                if j == 0:
                    lineListNew = []
                    u = 0
                    for el in line:
                        if u == 0:
                            lineListNew.append([el] + ['gsuite name'])
                        else:
                            lineListNew.append(el.split(workflowAllInOne.FILE_SELECTOR))
                        u += 1
                elif j == 1:
                    u = 0
                    for el in line:
                        lineListNew[u].append(el)
                        u += 1
                else:
                    strReadCsv += str('\t'.join(line)+'\n')

                j += 1

        header = workflowAllInOne.countHeader(lineListNew, changeGroup)

        workflowAllInOne.buildFile(uri, header + '\n' + strReadCsv)

        return True

    @classmethod
    def countHeader(cls, lineListNew, changeGroup):
        headerLine1 = 'gene\t'
        headerLine2 = 'group\t'

        for elNum1 in range(1, len(lineListNew)):
            gsuite = lineListNew[elNum1][1]
            group = changeGroup[gsuite]
            sample = lineListNew[elNum1][0]
            headerLine1 += str(sample) + '-----' + str(gsuite)
            headerLine2 += str(group)
            if elNum1 < len(lineListNew)-1:
                headerLine1 +='\t'
                headerLine2 += '\t'


        return headerLine1 + '\n' + headerLine2

    @classmethod
    def showClusterOutput(cls, htmlCore, gsuite, galaxyFn, imageName):

        imageLinks = OrderedDict()
        lenGsuitePart = gsuite.numTracks() / 2

        i = 0
        for gsTrack in gsuite.allTracks():

            filename = gsTrack.title
            pathInput = gsTrack.path

            if imageName == 'clust':
                if i < lenGsuitePart:
                    fileOutput = GalaxyRunSpecificFile([imageName, filename, filename + '.png'], galaxyFn)
                    ensurePathExists(fileOutput.getDiskPath())
                    workflowAllInOne.doClust(pathInput, fileOutput.getDiskPath())

                    imageLinks[filename] = fileOutput
            if imageName == 'vulcano':
                if i >= lenGsuitePart:
                    fileOutput = GalaxyRunSpecificFile([imageName, filename, filename + '.png'], galaxyFn)
                    ensurePathExists(fileOutput.getDiskPath())
                    workflowAllInOne.doVulcanoPlot(pathInput, fileOutput.getDiskPath())

                    imageLinks[filename] = fileOutput
            i += 1

        return imageLinks

    @classmethod
    def doVulcanoPlot(self, pathInput, pathOutput):
        from proto.RSetup import r

        rCode = """

                        suppressMessages(library(DESeq2));
                        suppressMessages(library(MASS));
                        suppressMessages(library(calibrate));

                        myGeneExpression <- function(pathInput, pathOutput){



                          data1 <- read.csv(pathInput, header=TRUE, sep = '\t')
                          colNames <- colnames(data1)
                          colNames <- sapply(strsplit(colNames, '.....', fixed=TRUE), function(x) (x[1]))
                          colnames(data1) <- colNames

                          rownamesData1 <- data1[,1]
                          data1 <- data1[,-1]

                          condition <- unlist(data1[1,])
                          condition <- factor(as.vector(condition))

                          data1 <- data1[-c(1),]
                          data1 <- as.matrix(data1)

                          dds <- DESeqDataSetFromMatrix(data1, DataFrame(condition), ~ condition)
                          dds <- DESeq(dds)
                          res <- results(dds)

                          png(pathOutput,
                              width = 400,
                              height = 400,
                              pointsize = 10)

                          with(res, plot(log2FoldChange, -log10(pvalue), pch=20, main="Volcano plot", xlim=c(-2.5,2)))

                          # Add colored points: red if padj<0.05, orange of log2FC>1, green if both)
                          with(subset(res, padj<.05 ), points(log2FoldChange, -log10(pvalue), pch=20, col="red"))
                          with(subset(res, abs(log2FoldChange)>1), points(log2FoldChange, -log10(pvalue), pch=20, col="orange"))
                          with(subset(res, padj<.05 & abs(log2FoldChange)>1), points(log2FoldChange, -log10(pvalue), pch=20, col="green"))


                          # Label points with the textxy function from the calibrate plot

                          with(subset(res, padj<.05 & abs(log2FoldChange)>1), textxy(log2FoldChange, -log10(pvalue), labs=rownamesData1[2:length(rownamesData1)], cex=.8))

                          dev.off()
                        }


                        """
        r(rCode)(pathInput, pathOutput)

        return 1

    @classmethod
    def doClust(self, pathInput, pathOutput):
        from proto.RSetup import r

        rCode = """

                    suppressMessages(library(DESeq));
                    suppressMessages(library(gplots));
                    suppressMessages(library(limma));
                    suppressMessages(library(edgeR));

                    myClust <- function(pathInput, pathOutput){


                      data1 <- read.csv(pathInput, header=TRUE, sep = '\t')

                      colNames <- colnames(data1)
                      colNames <- sapply(strsplit(colNames, '.....', fixed=TRUE), function(x) (x[1]))
                      colnames(data1) <- colNames

                      rownames <- data1[,1] #group
                      data1 <- data1[,-1] #411X3, 412X3

                      dataGroup <- data1[1,]
                      data1 <- data1[-c(1),] #410X3

                      mat_data1 <- as.matrix(na.omit(data1))
                      mat_data1<-as.matrix(data1)
                      mat_data1[is.na(mat_data1)] <- 0.000000001

                      nameGR = 'genes-'
                      mat_data1<- mat_data1
                      CName1 <- colnames(mat_data1)

                      sampleCondition1<-c()
                      colors<-c()

                      possibleColors = c('#7cb5ec', '#FCE9A1', '#E7DEC5', '#B58AA5', '#fdd07c', '#C3C3E5', '#C8CF78', '#4a6c8d', '#ffe063', '#C4B387', '#84596B', '#ffb037', '#443266', '#a6ab5b', '#6699FF', '#91e8e1', '#7A991F', '#525266', '#1A334C', '#334C80', '#292900', '#142900', '#99993D', '#009999', '#1A1A0A', '#5C85AD', '#804C4C', '#1A0F0F', '#A3A3CC', '#660033', '#3D4C0F', '#fde720', '#554e44', '#1ce1ce', '#dedbbb', '#facade', '#baff1e', '#aba5ed', '#f2b3b3', '#f9e0e0', '#abcdef', '#f9dcd3', '#eb9180', '#c2dde5', '#008B8B', '#B8860B', '#A9A9A9', '#006400', '#BDB76B', '#8B008B', '#556B2F', '#FF8C00', '#9932CC', '#8B0000', '#E9967A', '#8FBC8F', '#483D8B', '#2F4F4F', '#00CED1', '#9400D3', '#FF1493', '#00BFFF', '#696969', '#1E90FF', '#B22222', '#FFFAF0', '#228B22', '#FF00FF', '#DCDCDC', '#F8F8FF', '#FFD700', '#DAA520', '#808080', '#008000', '#ADFF2F', '#F0FFF0', '#FF69B4', '#CD5C5C', '#4B0082', '#FFFFF0', '#F0E68C', '#E6E6FA', '#FFF0F5', '#7CFC00', '#FFFACD', '#ADD8E6', '#F08080', '#E0FFFF', '#FAFAD2', '#D3D3D3', '#90EE90', '#FFB6C1', '#FFA07A', '#20B2AA', '#87CEFA', '#778899', '#B0C4DE', '#FFFFE0', '#00FF00', '#32CD32', '#FAF0E6', '#FF00FF', '#800000', '#66CDAA', '#0000CD', '#BA55D3', '#9370DB', '#3CB371', '#7B68EE', '#00FA9A', '#48D1CC', '#C71585', '#191970', '#F5FFFA', '#FFE4E1', '#FFE4B5', '#FFDEAD', '#000080', '#FDF5E6', '#808000', '#6B8E23', '#FFA500', '#FF4500', '#DA70D6', '#EEE8AA')
                      possibleGroupName = c()

                      i=1
                      for (cn in CName1)
                      {
                        group = unlist(dataGroup[CName1[i]])
                        sampleCondition1[i] = group
                        colors[i] = possibleColors[unlist(group)]

                        if (group %in% possibleGroupName == FALSE)
                        {
                          possibleGroupName <- append(possibleGroupName, unlist(group))
                        }

                        i=i+1
                      }


                      cnf1 <- DGEList(counts=mat_data1)
                      cnf1 <- calcNormFactors(cnf1,method="TMM")
                      normfac1 <- cnf1$samples[,3]
                      libsize1 <- colSums(mat_data1)
                      rellibsize1 <- libsize1/exp(mean(log(libsize1)))
                      exp(mean(log(libsize1)))
                      nf1 <- normfac1 * rellibsize1

                      mat_data1 = round(sweep(mat_data1, 2, nf1, "/"))
                      mat_data1[mat_data1 == 0] <- NA
                      mat_data1=log2(mat_data1)
                      mat_data1[is.na(mat_data1)] <- 0.000000001

                      row_distance1 = dist(mat_data1, method = "euclidean")
                      row_cluster1 = hclust(row_distance1, method = "ward.D2")
                      col_distance1 = dist(t(mat_data1), method = "euclidean")
                      col_cluster1 = hclust(col_distance1, method = "ward.D2")

                      mat_data1 <- apply(as.matrix(mat_data1),2,as.numeric)

                      png(pathOutput,
                          width = ncol(mat_data1)*200,
                          height = 500,
                          pointsize = 10)


                      heatmap.2(
                        mat_data1,
                        ColSideColors=colors,
                        margins = c(20+length(colnames(data1)[2]), 10),
                        Rowv = as.dendrogram(row_cluster1),
                        Colv = as.dendrogram(col_cluster1),
                        scale="row",
                        trace="none",
                        density.info="none",
                        keysize=0.8,
                        col=redblue(256),
                        dendrogram="column",
                        labRow = "",
                      )
                      par(lend = 1)
                      legend("topright",
                             legend = possibleGroupName,
                             col = possibleColors[1:i-1],
                             lty= 1,
                             lwd = 10
                      )
                      dev.off()
                    }


                    """
        r(rCode)(pathInput, pathOutput)

        return 1

    @classmethod
    def countMS(cls, gsuite, number, fileMature, galaxyFn):

        percentage = 0.2  # the number how many reads is smaller/higher then mature/star
        startNumber = 30
        types = ['mature', 'matureWithMismatch', 'star', 'starWithMismatch', 'maturestar', 'maturestarWithMismatch']

        fileMS = workflowAllInOne.readMature(fileMature, startNumber)
        readsDict, fileTotal, fileGroup, fileReadTimes = workflowAllInOne.readFiles(gsuite, fileMS, percentage, number)

        # normalise all files
        readsDictOutputNormalise = workflowAllInOne.normaliseFiles(readsDict, fileTotal, fileReadTimes, normalise=True)

        # raw files
        readsDictOutput = workflowAllInOne.normaliseFiles(readsDict, fileTotal, fileReadTimes, normalise=False)

        header = [['gene', 'group']]
        for sample, group in fileGroup.iteritems():
            header.append([sample] + [group])

        headerReverse = map(list, zip(*header))

        fileLineNormalise = workflowAllInOne.countFiles(types, readsDictOutputNormalise)
        fileLine = workflowAllInOne.countFiles(types, readsDictOutput)

        outGSuite = GSuite()

        workflowAllInOne.buildGSuite(gsuite, outGSuite, types, fileLineNormalise, headerReverse, galaxyFn,
                                     extraFN='normalised')
        workflowAllInOne.buildGSuite(gsuite, outGSuite, types, fileLine, headerReverse, galaxyFn, extraFN='raw')

        return outGSuite

    @classmethod
    def buildGSuite(cls, gsuite, outGSuite, types, fileLine, headerReverse, galaxyFn, extraFN):
        for fileName in types:
            uri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn,
                                                extraFileName=fileName + '--' + extraFN,
                                                suffix='tabular')
            gSuiteTrack = GSuiteTrack(uri)
            outFn = gSuiteTrack.path
            ensurePathExists(outFn)

            lFile = ''
            for l in fileLine[fileName]:
                lFile += str('\t'.join([str(i) for i in l])) + '\n'

            with open(outFn, 'w') as contentFile:
                contentFile.write(str(''.join(['\t'.join(hr) + '\n' for hr in headerReverse])))
                contentFile.writelines(lFile)
            contentFile.close()

            outGSuite.addTrack(GSuiteTrack(uri, title=''.join(fileName + '--' + extraFN), genome=gsuite.genome))

        return outGSuite

    @classmethod
    def normaliseFiles(self, readsDict, fileTotal, fileReadTimes, normalise):
        readsDictOutput = OrderedDict()

        for name in readsDict.keys():
            if not name in readsDictOutput.keys():
                readsDictOutput[name] = OrderedDict()
            for whichMS in readsDict[name].keys():
                if not whichMS in readsDictOutput[name].keys():
                    readsDictOutput[name][whichMS] = OrderedDict()
                for read in readsDict[name][whichMS].keys():

                    for s in readsDict[name][whichMS][read].keys():

                        if not s in readsDictOutput[name][whichMS].keys():
                            readsDictOutput[name][whichMS][s] = 0

                        if normalise == True:
                            readsDictOutput[name][whichMS][s] += (float(readsDict[name][whichMS][read][s]) / float(
                                fileReadTimes[read])) / (float(fileTotal[s]) / float(1000000))
                        if normalise == False:
                            readsDictOutput[name][whichMS][s] += int(float(readsDict[name][whichMS][read][s]) / float(
                                fileReadTimes[read]))

        return readsDictOutput

    @classmethod
    def readMature(self, fileMature, startNumber):
        fileMS = {}
        with open(ExternalTrackManager.extractFnFromGalaxyTN(fileMature.split(':')), 'r') as f:
            readCsv = csv.reader(f, delimiter='\t', quotechar='|')
            for line in readCsv:

                name = line[0].replace('_3p*', '').replace('_5p*', '').replace('3p*', '').replace('5p*', '').replace(
                    '_3p', '').replace('_5p', '').replace('3p', '').replace('5p', '')
                if not name in fileMS.keys():
                    fileMS[name] = {}

                whichFirst = 0
                if 's' in line[1]:
                    elM = 'star'
                    if not elM in fileMS[name].keys():
                        fileMS[name][elM] = [int(line[2]) + startNumber, int(line[3]) + startNumber]
                elif 'm' in line[1] or 'c' in line[1]:
                    if whichFirst == 0:
                        whichFirst = 2
                    elM = 'mature'
                    if not 'star' in fileMS[name].keys():
                        if 'mature' in fileMS[name].keys():
                            elM = 'co-mature'
                    if not elM in fileMS[name].keys():
                        fileMS[name][elM] = [int(line[2]) + startNumber, int(line[3]) + startNumber]
        f.close()
        return fileMS

    @classmethod
    def readFiles(self, gsuite, fileMS, percentage, number):
        readsDict = OrderedDict()
        fileTotal = OrderedDict()
        fileGroup = OrderedDict()
        fileReadTimes = OrderedDict()  # how many times which read are in samples

        for gsTrack in gsuite.allTracks():
            sample = gsTrack.title
            fileGroup[str(sample) + workflowAllInOne.FILE_SELECTOR + str(
                gsTrack.getAttribute('gsuite name'))] = gsTrack.getAttribute('group')
            fileTotal[sample] = 0

        for gsTrack in gsuite.allTracks():
            sample = gsTrack.title

            with open(gsTrack.path, 'rb') as f:
                readCsv = csv.reader(f, delimiter='\t', quotechar='|')

                for line in readCsv:
                    if line[0] != '@PG' and line[0] != '@SQ' and line[0] != '@HD' and line[2] != '*':

                        name = line[2].replace('_pri', '')  # gene
                        read = line[9]  # read ACTGTTT

                        mismatch = 0
                        if len(line) == 14:
                            mismatch = int(line[13].replace('NM:i:', '').replace('NL:i:', ''))
                            if mismatch != 0:
                                mismatch = 1

                        stRead = int(line[3]) - 1
                        enRead = int(line[3]) + len(read) - 2

                        elMS = ''
                        for elM in fileMS[name].keys():
                            st = fileMS[name][elM][0]
                            en = fileMS[name][elM][1]

                            st = st - int(percentage * st)
                            en = en + int(percentage * en)

                            if stRead > st and enRead < en:
                                elMS = elM

                        if mismatch == 0:
                            if elMS == 'star':
                                whichMS = 'star'
                            else:
                                whichMS = 'mature'
                        else:
                            if elMS == 'star':
                                whichMS = 'starOnlyMismatch'
                            else:
                                whichMS = 'matureOnlyMismatch'

                        if line[2] != '*' and len(line[9]) >= number:
                            findStrVal = workflow12.findStringValue(line[0])

                            if not name in readsDict.keys():
                                readsDict[name] = {}
                            if not whichMS in readsDict[name].keys():
                                readsDict[name][whichMS] = {}
                            if not read in readsDict[name][whichMS].keys():
                                readsDict[name][whichMS][read] = {}
                                for s in fileTotal.keys():
                                    readsDict[name][whichMS][read][s] = 0
                            if not read in fileReadTimes.keys():
                                fileReadTimes[read] = 0
                            fileReadTimes[read] += 1

                            readsDict[name][whichMS][read][sample] += findStrVal
                            fileTotal[sample] += findStrVal
            f.close()

        return readsDict, fileTotal, fileGroup, fileReadTimes

    @classmethod
    def countFiles(self, types, readsDict):
        fileLine = OrderedDict()

        for t in types:
            fileLine[t] = []

        for whichMS in ['mature', 'matureOnlyMismatch', 'star', 'starOnlyMismatch']:
            for name in readsDict.keys():  # name -> gene
                if whichMS in readsDict[name].keys():
                    if whichMS == 'mature':
                        fileLine['mature'].append([name] + [val for key, val in readsDict[name][whichMS].iteritems()])
                        fileLine['matureWithMismatch'].append(
                            [name] + [val for key, val in readsDict[name][whichMS].iteritems()])
                        fileLine['maturestar'].append(
                            [name] + [val for key, val in readsDict[name][whichMS].iteritems()])
                        fileLine['maturestarWithMismatch'].append(
                            [name] + [val for key, val in readsDict[name][whichMS].iteritems()])
                    if whichMS == 'matureOnlyMismatch':
                        fileLine['matureWithMismatch'].append(
                            [name] + [val for key, val in readsDict[name][whichMS].iteritems()])
                        fileLine['maturestarWithMismatch'].append(
                            [name] + [val for key, val in readsDict[name][whichMS].iteritems()])
                    if whichMS == 'star':
                        fileLine['star'].append([name] + [val for key, val in readsDict[name][whichMS].iteritems()])
                        fileLine['starWithMismatch'].append(
                            [name] + [val for key, val in readsDict[name][whichMS].iteritems()])
                        fileLine['maturestar'].append(
                            [name] + [val for key, val in readsDict[name][whichMS].iteritems()])
                        fileLine['maturestarWithMismatch'].append(
                            [name] + [val for key, val in readsDict[name][whichMS].iteritems()])
                    if whichMS == 'starOnlyMismatch':
                        fileLine['starWithMismatch'].append(
                            [name] + [val for key, val in readsDict[name][whichMS].iteritems()])
                        fileLine['maturestarWithMismatch'].append(
                            [name] + [val for key, val in readsDict[name][whichMS].iteritems()])
        return fileLine

    @classmethod
    def findStringValue(self, sign):
        if '_x' in sign:
            try:
                return int(sign.split('_x')[1])
            except csv.Error, e:
                pass

        if 'x' in sign:
            try:
                return int(sign.split('x')[1])
            except csv.Error, e:
                pass

        if '#' in sign:
            try:
                return int(sign.split('#')[1])
            except csv.Error, e:
                pass

        if '-' in sign:
            try:
                return int(sign.split('-')[1])
            except csv.Error, e:
                pass

    @classmethod
    def groupGsuite(cls, gsuiteList, gsuiteGroup, gsuiteName):
        from quick.gsuite import GSuiteStatUtils

        concatenatedGSuite = GSuite()
        results = {}

        group = []
        gsName = []
        i = 0
        for gsuite in gsuiteList:
            for track in gsuite.allTracks():
                gs = gsuiteName[i].split(':')
                group.append(gsuiteGroup[i])
                gsName.append(urllib.unquote(gs[len(gs) - 1]))
                concatenatedGSuite.addTrack(track)
            i += 1

        i = 0
        for gsTrack in concatenatedGSuite.allTracks():
            results[gsTrack.title] = [int(group[i]), gsName[i]]
            i += 1

        GSuiteStatUtils.addResultsToInputGSuite(concatenatedGSuite, results, ['group', 'gsuite name'],
                                                cls.extraGalaxyFn[workflowAllInOne.HIST_GROUPED_GSUITE])

        return concatenatedGSuite

    @classmethod
    def buildSamGsuite(self, gsuite, galaxyFn, hsaFas):

        import os, subprocess
        outGSuite = GSuite()

        for gsTrack in gsuite.allTracks():
            title = gsTrack.title

            title = title.replace(' ', '')
            resFile = GalaxyRunSpecificFile(['workflow', title, title + '.sam'], galaxyFn)
            ensurePathExists(resFile.getDiskPath())

            trackDirName = os.path.dirname(os.path.realpath(resFile.getDiskPath()))
            ensurePathExists(str(trackDirName))

            command = """
                    module load bowtie
                    bowtie-build """ + str(hsaFas) + """ """ + str(trackDirName) + str('genome') + """
                    bowtie -f -l 18 -n 0 """ + str(trackDirName) + str('genome') + """ -S  """ + str(
                gsTrack.path) + " " + str(trackDirName) + str('mappingsam') + """
                    module load samtools
                    samtools view -b -S """ + str(trackDirName) + str('mappingsam') + """ > """ + str(
                trackDirName) + str(
                'mappingbam') + """
                    samtools sort """ + str(trackDirName) + str('mappingbam') + " " + str(trackDirName) + str(
                'mappingsorted') + """
                    samtools index """ + str(trackDirName) + str('mappingsorted.bam') + """
                    samtools view -h -o """ + str(resFile.getDiskPath()) + " " + str(trackDirName) + str(
                'mappingsorted.bam')

            process = subprocess.Popen([command], shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)

            results, errors = process.communicate()

            fileName = trackDirName.split('/')[-1].replace('fasta', '').replace('fas', '').replace('fa', '') + 'sam'

            uri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn,
                                                extraFileName=fileName,
                                                suffix='sam')

            gSuiteTrack = GSuiteTrack(uri)
            outFn = gSuiteTrack.path
            ensurePathExists(outFn)

            with open(resFile.getDiskPath(), 'r') as content_file:
                content = content_file.read()
            content_file.close()

            with open(outFn, 'w') as outputFile:
                outputFile.write(content)
            outputFile.close()

            outGSuite.addTrack(
                GSuiteTrack(uri, title=''.join(fileName), genome=gsuite.genome, attributes=gsTrack.attributes))

        return outGSuite

    @staticmethod
    def isPublic():
        return True


class workflow13(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Workflow 13 - cluster"

    @staticmethod
    def getInputBoxNames():
        return [('Select gsuite', 'gsuite')
                ]

    @staticmethod
    def getOptionsBoxGsuite():
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        gsuite = getGSuiteFromGalaxyTN(choices.gsuite)

        imageLinks = OrderedDict()

        for gsTrack in gsuite.allTracks():
            filename = gsTrack.title
            pathInput = gsTrack.path

            fileOutput = GalaxyRunSpecificFile(['image', filename, filename + '.png'], galaxyFn)
            ensurePathExists(fileOutput.getDiskPath())

            workflow13.doClust(pathInput, fileOutput.getDiskPath())

            imageLinks[filename] = fileOutput

        htmlCore = HtmlCore()
        htmlCore.begin()
        htmlCore.divBegin('resultsDiv')
        htmlCore.tableHeader(['Clustering images'], sortable=False, tableId='resultsTable')

        for filename in imageLinks:
            htmlCore.tableLine([imageLinks[filename].getLink('Show file ' + str(filename))])

        htmlCore.tableFooter()

        htmlCore.end()
        print htmlCore

    @classmethod
    def doClust(self, pathInput, pathOutput):

        from proto.RSetup import r

        rCode = """

            suppressMessages(library(DESeq));
            suppressMessages(library(gplots));
            suppressMessages(library(limma));
            suppressMessages(library(edgeR));

            myClust <- function(pathInput, pathOutput){



              data1 <- read.csv(pathInput, header=TRUE, sep = '\t')
              rownamesData1 <- data1[,1]
              data1 <- data1[,-1]



              dataGroup <- data1[1,]
              data1 <- data1[-c(1),]

              mat_data1 <- as.matrix(na.omit(data1))
              mat_data1<-as.matrix(data1)
              mat_data1[is.na(mat_data1)] <- 0.000000001

              nameGR = 'genes-'
              mat_data1<- mat_data1
              CName1 <- colnames(mat_data1)

              sampleCondition1<-c()
              colors<-c()

              possibleColors = c('#7cb5ec', '#FCE9A1', '#E7DEC5', '#B58AA5', '#fdd07c', '#C3C3E5', '#C8CF78', '#4a6c8d', '#ffe063', '#C4B387', '#84596B', '#ffb037', '#443266', '#a6ab5b', '#6699FF', '#91e8e1', '#7A991F', '#525266', '#1A334C', '#334C80', '#292900', '#142900', '#99993D', '#009999', '#1A1A0A', '#5C85AD', '#804C4C', '#1A0F0F', '#A3A3CC', '#660033', '#3D4C0F', '#fde720', '#554e44', '#1ce1ce', '#dedbbb', '#facade', '#baff1e', '#aba5ed', '#f2b3b3', '#f9e0e0', '#abcdef', '#f9dcd3', '#eb9180', '#c2dde5', '#008B8B', '#B8860B', '#A9A9A9', '#006400', '#BDB76B', '#8B008B', '#556B2F', '#FF8C00', '#9932CC', '#8B0000', '#E9967A', '#8FBC8F', '#483D8B', '#2F4F4F', '#00CED1', '#9400D3', '#FF1493', '#00BFFF', '#696969', '#1E90FF', '#B22222', '#FFFAF0', '#228B22', '#FF00FF', '#DCDCDC', '#F8F8FF', '#FFD700', '#DAA520', '#808080', '#008000', '#ADFF2F', '#F0FFF0', '#FF69B4', '#CD5C5C', '#4B0082', '#FFFFF0', '#F0E68C', '#E6E6FA', '#FFF0F5', '#7CFC00', '#FFFACD', '#ADD8E6', '#F08080', '#E0FFFF', '#FAFAD2', '#D3D3D3', '#90EE90', '#FFB6C1', '#FFA07A', '#20B2AA', '#87CEFA', '#778899', '#B0C4DE', '#FFFFE0', '#00FF00', '#32CD32', '#FAF0E6', '#FF00FF', '#800000', '#66CDAA', '#0000CD', '#BA55D3', '#9370DB', '#3CB371', '#7B68EE', '#00FA9A', '#48D1CC', '#C71585', '#191970', '#F5FFFA', '#FFE4E1', '#FFE4B5', '#FFDEAD', '#000080', '#FDF5E6', '#808000', '#6B8E23', '#FFA500', '#FF4500', '#DA70D6', '#EEE8AA')
              possibleGroupName = c()


              i=1
              for (cn in CName1)
              {
                group = unlist(dataGroup[CName1[i]])
                sampleCondition1[i] = group
                colors[i] = possibleColors[unlist(group)]

                if (group %in% possibleGroupName == FALSE)
                {
                  possibleGroupName <- append(possibleGroupName, unlist(group))
                }

                i=i+1
              }


              cnf1 <- DGEList(counts=mat_data1)
              cnf1 <- calcNormFactors(cnf1,method="TMM")
              normfac1 <- cnf1$samples[,3]
              libsize1 <- colSums(mat_data1)
              rellibsize1 <- libsize1/exp(mean(log(libsize1)))
              exp(mean(log(libsize1)))
              nf1 <- normfac1 * rellibsize1

              mat_data1 = round(sweep(mat_data1, 2, nf1, "/"))
              mat_data1[mat_data1 == 0] <- NA
              mat_data1=log2(mat_data1)
              mat_data1[is.na(mat_data1)] <- 0.000000001

              row_distance1 = dist(mat_data1, method = "euclidean")
              row_cluster1 = hclust(row_distance1, method = "ward.D2")
              col_distance1 = dist(t(mat_data1), method = "euclidean")
              col_cluster1 = hclust(col_distance1, method = "ward.D2")

              mat_data1 <- apply(as.matrix(mat_data1),2,as.numeric)

              png(pathOutput,
                  width = ncol(mat_data1)*200,
                  height = 500,
                  pointsize = 10)
              heatmap.2(
                mat_data1,
                ColSideColors=colors,
                margins = c(20, 10),
                Rowv = as.dendrogram(row_cluster1),
                Colv = as.dendrogram(col_cluster1),
                scale="row",
                trace="none",
                density.info="none",
                keysize=0.8,
                col=redblue(256),
                dendrogram="column",
                labRow = "",
              )
              par(lend = 1)
              legend("topright",
                     legend = possibleGroupName,
                     col = possibleColors[1:i-1],
                     lty= 1,
                     lwd = 10
              )
              dev.off()
            }


            """
        #
        # # rCode = """ myClust <- function(pathInput, pathOutput){
        # #
        # # filename <- unlist(strsplit(pathInput, '/'))
        # # filename <- filename[length(filename)]
        # #
        # # png(pathOutput,
        # #           width = 200,
        # #           height = 500,
        # #           pointsize = 10)
        # #
        # # plot(c(1,2,3))
        # #
        # # dev.off()
        # #
        # # }
        # #
        # # """
        #
        #
        r(rCode)(pathInput, pathOutput)

        return 1

    @staticmethod
    def validateAndReturnErrors(choices):
        return None

    @staticmethod
    def isPublic():
        return True

    @staticmethod
    def getOutputFormat(choices):
        return 'customhtml'


class workflow12(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Workflow 12 - create files for clustering"

    @staticmethod
    def getInputBoxNames():
        return [('Select gsuite', 'gsuite'),
                ('Select mature/star file', 'file'),
                ('Select minimal number of nucleotides', 'number')
                ]

    @staticmethod
    def getOptionsBoxGsuite():
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @staticmethod
    def getOptionsBoxFile(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement()

    @staticmethod
    def getOptionsBoxNumber(prevChoices):
        return ''

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        gsuite = getGSuiteFromGalaxyTN(choices.gsuite)
        number = int(choices.number)
        fileMature = choices.file
        percentage = 0.2  # the number how many reads is smaller/higher then mature/star
        startNumber = 30
        types = ['mature', 'matureWithMismatch', 'star', 'starWithMismatch', 'maturestar', 'maturestarWithMismatch']

        fileMS = workflow12.readMature(fileMature, startNumber)
        readsDict, fileTotal, fileGroup, fileReadTimes = workflow12.readFiles(gsuite, fileMS, percentage, number)
        readsDictOutput = workflow12.normaliseFiles(readsDict, fileTotal, fileGroup, fileReadTimes)

        fileLineHeader2 = ['group']
        fileLineHeader1 = ['gene']
        for group in fileGroup.keys():
            fileLineHeader2.append(str(fileGroup[group]))
            fileLineHeader1.append(str(group))

        fileLine = workflow12.countFiles(types, readsDictOutput)

        htmlCore = HtmlCore()
        htmlCore.begin()
        htmlCore.divBegin('resultsDiv')
        # htmlCore.tableHeader(['Files', 'Clustering images'], sortable=True, tableId='resultsTable')

        outGSuite = GSuite()

        htmlCore.line(
            'In the history you can find an element called: ' + 'Clustering Gsuite' + ', which contains following data: ')

        for t in types:

            fileName = t

            uri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn,
                                                extraFileName=fileName,
                                                suffix='tabular')

            gSuiteTrack = GSuiteTrack(uri)
            outFn = gSuiteTrack.path
            ensurePathExists(outFn)

            # resFile = GalaxyRunSpecificFile(['workflow', t, t + '.txt'], galaxyFn)
            # ensurePathExists(resFile.getDiskPath())
            # trackDirName = os.path.dirname(os.path.realpath(resFile.getDiskPath()))
            # ensurePathExists(str(trackDirName))
            #
            # htmlCore.tableLine([resFile.getLink('Show file ' + str(t))])

            lFile = '\t'.join(fileLineHeader1) + '\n'
            lFile += '\t'.join(fileLineHeader2) + '\n'
            for l in fileLine[t]:
                lFile += str('\t'.join([str(i) for i in l])) + '\n'

            # with open(resFile.getDiskPath(), 'w') as contentFile:
            #     contentFile.writelines(lFile)
            # contentFile.close()

            with open(outFn, 'w') as contentFile:
                contentFile.writelines(lFile)
            contentFile.close()

            outGSuite.addTrack(
                GSuiteTrack(uri, title=''.join(fileName), genome=gsuite.genome))

            htmlCore.line(t)

        GSuiteComposer.composeToFile(outGSuite, cls.extraGalaxyFn['Clustering Gsuite'])

        htmlCore.tableFooter()

        htmlCore.end()
        print htmlCore

    @classmethod
    def normaliseFiles(self, readsDict, fileTotal, fileGroup, fileReadTimes):

        readsDictOutput = OrderedDict()

        for name in readsDict.keys():
            if not name in readsDictOutput.keys():
                readsDictOutput[name] = OrderedDict()
            for whichMS in readsDict[name].keys():
                if not whichMS in readsDictOutput[name].keys():
                    readsDictOutput[name][whichMS] = OrderedDict()
                for read in readsDict[name][whichMS].keys():

                    for s in readsDict[name][whichMS][read].keys():

                        if not s in readsDictOutput[name][whichMS].keys():
                            readsDictOutput[name][whichMS][s] = 0

                        readsDictOutput[name][whichMS][s] += (float(readsDict[name][whichMS][read][s]) / float(
                            fileReadTimes[read])) / (float(fileTotal[s]) / float(1000000))

        return readsDictOutput

    @classmethod
    def readMature(self, fileMature, startNumber):
        fileMS = {}
        with open(ExternalTrackManager.extractFnFromGalaxyTN(fileMature.split(':')), 'r') as f:
            readCsv = csv.reader(f, delimiter='\t', quotechar='|')
            for line in readCsv:

                name = line[0].replace('_3p*', '').replace('_5p*', '').replace('3p*', '').replace('5p*', '').replace(
                    '_3p', '').replace('_5p', '').replace('3p', '').replace('5p', '')
                if not name in fileMS.keys():
                    fileMS[name] = {}

                whichFirst = 0
                if 's' in line[1]:
                    elM = 'star'
                    if not elM in fileMS[name].keys():
                        fileMS[name][elM] = [int(line[2]) + startNumber, int(line[3]) + startNumber]
                elif 'm' in line[1] or 'c' in line[1]:
                    if whichFirst == 0:
                        whichFirst = 2
                    elM = 'mature'
                    if not 'star' in fileMS[name].keys():
                        if 'mature' in fileMS[name].keys():
                            elM = 'co-mature'
                    if not elM in fileMS[name].keys():
                        fileMS[name][elM] = [int(line[2]) + startNumber, int(line[3]) + startNumber]
        f.close()
        return fileMS

    @classmethod
    def readFiles(self, gsuite, fileMS, percentage, number):

        readsDict = OrderedDict()
        fileTotal = OrderedDict()
        fileGroup = OrderedDict()
        fileReadTimes = OrderedDict()  # how many times which read are in samples

        for gsTrack in gsuite.allTracks():
            sample = gsTrack.title
            fileGroup[sample] = gsTrack.getAttribute('group')
            fileTotal[sample] = 0

        for gsTrack in gsuite.allTracks():
            sample = gsTrack.title

            with open(gsTrack.path, 'rb') as f:
                readCsv = csv.reader(f, delimiter='\t', quotechar='|')

                for line in readCsv:
                    if line[0] != '@PG' and line[0] != '@SQ' and line[0] != '@HD' and line[2] != '*':

                        name = line[2].replace('_pri', '')  # gene
                        read = line[9]  # read ACTGTTT

                        mismatch = 0
                        if len(line) == 14:
                            mismatch = int(line[13].replace('NM:i:', '').replace('NL:i:', ''))
                            if mismatch != 0:
                                mismatch = 1

                        stRead = int(line[3]) - 1
                        enRead = int(line[3]) + len(read) - 2

                        elMS = ''
                        for elM in fileMS[name].keys():
                            st = fileMS[name][elM][0]
                            en = fileMS[name][elM][1]

                            st = st - int(percentage * st)
                            en = en + int(percentage * en)

                            if stRead > st and enRead < en:
                                elMS = elM

                        if mismatch == 0:
                            if elMS == 'star':
                                whichMS = 'star'
                            else:
                                whichMS = 'mature'
                        else:
                            if elMS == 'star':
                                whichMS = 'starOnlyMismatch'
                            else:
                                whichMS = 'matureOnlyMismatch'

                        if line[2] != '*' and len(line[9]) >= number:
                            findStrVal = workflow12.findStringValue(line[0])

                            if not name in readsDict.keys():
                                readsDict[name] = {}
                            if not whichMS in readsDict[name].keys():
                                readsDict[name][whichMS] = {}
                            if not read in readsDict[name][whichMS].keys():
                                readsDict[name][whichMS][read] = {}
                                for s in fileGroup.keys():
                                    readsDict[name][whichMS][read][s] = 0
                            if not read in fileReadTimes.keys():
                                fileReadTimes[read] = 0
                            fileReadTimes[read] += 1

                            readsDict[name][whichMS][read][sample] += findStrVal
                            fileTotal[sample] += findStrVal
            f.close()

        return readsDict, fileTotal, fileGroup, fileReadTimes

    @classmethod
    def countFiles(self, types, readsDict):

        fileLine = OrderedDict()

        for t in types:
            fileLine[t] = []

        for whichMS in ['mature', 'matureOnlyMismatch', 'star', 'starOnlyMismatch']:
            for name in readsDict.keys():  # name -> gene
                if whichMS in readsDict[name].keys():
                    if whichMS == 'mature':
                        fileLine['mature'].append([name] + [val for key, val in readsDict[name][whichMS].iteritems()])
                        fileLine['matureWithMismatch'].append(
                            [name] + [val for key, val in readsDict[name][whichMS].iteritems()])
                        fileLine['maturestar'].append(
                            [name] + [val for key, val in readsDict[name][whichMS].iteritems()])
                        fileLine['maturestarWithMismatch'].append(
                            [name] + [val for key, val in readsDict[name][whichMS].iteritems()])
                    if whichMS == 'matureOnlyMismatch':
                        fileLine['matureWithMismatch'].append(
                            [name] + [val for key, val in readsDict[name][whichMS].iteritems()])
                        fileLine['maturestarWithMismatch'].append(
                            [name] + [val for key, val in readsDict[name][whichMS].iteritems()])
                    if whichMS == 'star':
                        fileLine['star'].append([name] + [val for key, val in readsDict[name][whichMS].iteritems()])
                        fileLine['starWithMismatch'].append(
                            [name] + [val for key, val in readsDict[name][whichMS].iteritems()])
                        fileLine['maturestar'].append(
                            [name] + [val for key, val in readsDict[name][whichMS].iteritems()])
                        fileLine['maturestarWithMismatch'].append(
                            [name] + [val for key, val in readsDict[name][whichMS].iteritems()])
                    if whichMS == 'starOnlyMismatch':
                        fileLine['starWithMismatch'].append(
                            [name] + [val for key, val in readsDict[name][whichMS].iteritems()])
                        fileLine['maturestarWithMismatch'].append(
                            [name] + [val for key, val in readsDict[name][whichMS].iteritems()])

                        # if whichMS == 'mature':
                        #     for read in readsDict[name][whichMS]:
                        #         fileLine['mature'].append(
                        #             [name] + [read] + [val for key, val in readsDict[name][whichMS][read].iteritems()])
                        #         fileLine['matureWithMismatch'].append(
                        #             [name] + [read] + [val for key, val in readsDict[name][whichMS][read].iteritems()])
                        #         fileLine['maturestar'].append(
                        #             [name] + [read] + [val for key, val in readsDict[name][whichMS][read].iteritems()])
                        # if whichMS == 'matureOnlyMismatch':
                        #     for read in readsDict[name][whichMS]:
                        #         fileLine['matureWithMismatch'].append(
                        #             [name] + [read] + [val for key, val in readsDict[name][whichMS][read].iteritems()])
                        # if whichMS == 'star':
                        #     for read in readsDict[name][whichMS]:
                        #         fileLine['star'].append(
                        #             [name] + [read] + [val for key, val in readsDict[name][whichMS][read].iteritems()])
                        #         fileLine['starWithMismatch'].append(
                        #             [name] + [read] + [val for key, val in readsDict[name][whichMS][read].iteritems()])
                        #         fileLine['maturestar'].append(
                        #             [name] + [read] + [val for key, val in readsDict[name][whichMS][read].iteritems()])
                        # if whichMS == 'starOnlyMismatch':
                        #     for read in readsDict[name][whichMS]:
                        #         fileLine['starWithMismatch'].append(
                        #             [name] + [read] + [val for key, val in readsDict[name][whichMS][read].iteritems()])
        return fileLine

    @classmethod
    def findStringValue(self, sign):

        if '_x' in sign:
            try:
                return int(sign.split('_x')[1])
            except csv.Error, e:
                pass

        if 'x' in sign:
            try:
                return int(sign.split('x')[1])
            except csv.Error, e:
                pass

        if '#' in sign:
            try:
                return int(sign.split('#')[1])
            except csv.Error, e:
                pass

        if '-' in sign:
            try:
                return int(sign.split('-')[1])
            except csv.Error, e:
                pass

    @staticmethod
    def validateAndReturnErrors(choices):
        return None

    @staticmethod
    def isPublic():
        return True

    @classmethod
    def getExtraHistElements(cls, choices):
        return [HistElement('Clustering Gsuite', 'gsuite')]


class workflow11(GeneralGuiTool):
    PATH_BOWTIE = "/software/VERSIONS/bowtie-0.12.7/bowtie"

    @staticmethod
    def getToolName():
        return "Workflow 11 - create samfiles"

    @staticmethod
    def getInputBoxNames():
        return [('Select gsuite', 'gsuite'),
                ('Select genome file', 'hsaFas')
                ]

    @staticmethod
    def getOptionsBoxGsuite():
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @staticmethod
    def getOptionsBoxHsaFas(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement('fas', 'fasta')

    @classmethod
    def getOptionsBoxGroup(cls, prevChoices):
        return ''

    @classmethod
    def getExtraHistElements(cls, choices):
        return [HistElement('samFiles', 'gsuite')]

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        gsuiteName = choices.gsuite
        gsuite = getGSuiteFromGalaxyTN(gsuiteName)

        hsaFasName = choices.hsaFas
        hsaFas = ExternalTrackManager.extractFnFromGalaxyTN(hsaFasName.split(':'))

        import os, subprocess

        outGSuite = GSuite()

        for gsTrack in gsuite.allTracks():

            print '\n\n\n', gsTrack.title, '<br \>'

            title = gsTrack.title
            title = title.replace(' ', '')
            resFile = GalaxyRunSpecificFile(['workflow', title, title + '.sam'], galaxyFn)
            ensurePathExists(resFile.getDiskPath())

            trackDirName = os.path.dirname(os.path.realpath(resFile.getDiskPath()))
            ensurePathExists(str(trackDirName))

            command = """
                module load bowtie
                bowtie-build """ + str(hsaFas) + """ """ + str(trackDirName) + str('genome') + """
                bowtie -f -l 18 -n 0 """ + str(trackDirName) + str('genome') + """ -S  """ + str(
                gsTrack.path) + " " + str(trackDirName) + str('mappingsam') + """
                module load samtools
                samtools view -b -S """ + str(trackDirName) + str('mappingsam') + """ > """ + str(trackDirName) + str(
                'mappingbam') + """
                samtools sort """ + str(trackDirName) + str('mappingbam') + " " + str(trackDirName) + str(
                'mappingsorted') + """
                samtools index """ + str(trackDirName) + str('mappingsorted.bam') + """
                samtools view -h -o """ + str(resFile.getDiskPath()) + " " + str(trackDirName) + str(
                'mappingsorted.bam')

            process = subprocess.Popen([command], shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)

            results, errors = process.communicate()

            for fileDN in os.listdir(trackDirName):
                print fileDN

            fileName = trackDirName.split('/')[-1].replace('fasta', '').replace('fas', '').replace('fa', '') + 'sam'

            uri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn,
                                                extraFileName=fileName,
                                                suffix='sam')

            gSuiteTrack = GSuiteTrack(uri)
            outFn = gSuiteTrack.path
            ensurePathExists(outFn)

            with open(resFile.getDiskPath(), 'r') as content_file:
                content = content_file.read()
            content_file.close()

            with open(outFn, 'w') as outputFile:
                outputFile.write(content)
            outputFile.close()

            outGSuite.addTrack(
                GSuiteTrack(uri, title=''.join(fileName), genome=gsuite.genome, attributes=gsTrack.attributes))

        GSuiteComposer.composeToFile(outGSuite, cls.extraGalaxyFn['SAM Gsuite'])

    @staticmethod
    def validateAndReturnErrors(choices):
        return None

    @staticmethod
    def isPublic():
        return True

    @classmethod
    def getExtraHistElements(cls, choices):
        return [HistElement('SAM Gsuite', 'gsuite')]


class workflow10(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Workflow 10 - grouped files"

    @staticmethod
    def getInputBoxNames():
        return [('Select gsuite', 'gsuite'),
                ('Group number', 'group'),
                ]

    @staticmethod
    def getOptionsBoxGsuite():
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @classmethod
    def getOptionsBoxGroup(cls, prevChoices):
        return ''

    @classmethod
    def getExtraHistElements(cls, choices):
        return [HistElement('groupGsuite', 'gsuite')]

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        from quick.gsuite import GSuiteStatUtils

        # add group into gsuite
        results = {}

        gsuite = choices.gsuite
        gsuite = getGSuiteFromGalaxyTN(gsuite)

        group = choices.group
        for gsTrack in gsuite.allTracks():
            results[gsTrack.title] = int(group)

        GSuiteStatUtils.addResultsToInputGSuite(gsuite, results, ['Group'], cls.extraGalaxyFn['groupGsuite'])

        print 'In the history you can find a gSuite with the following group'

    @staticmethod
    def validateAndReturnErrors(choices):
        return None

    @staticmethod
    def getOutputFormat(choices):
        return 'customhtml'


class trfFromGSuite(GeneralGuiTool):
    TRF_PATH = "/software/VERSIONS/trf-4.0.4/bin/trf404.linux64"

    @staticmethod
    def getToolName():
        return "Trf from gSuite"

    @staticmethod
    def getInputBoxNames():
        return [('Select gsuite', 'gsuite'),
                ('Match', 'match'),
                ('Mismatch', 'mismatch'),
                ('Delta', 'delta'),
                ('Matching probability (Pm)', 'pm'),
                ('Indel probability (Pi)', 'pi'),
                ('Min score', 'minscore'),
                ('Max period', 'maxperiod'),
                ('Min consensus length', 'minconsensus'),
                ('Max consensus length', 'maxconsensus')
                ]

    @staticmethod
    def getOptionsBoxGsuite():
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @staticmethod
    def getOptionsBoxMatch(prevChoices):
        return '2'

    @staticmethod
    def getOptionsBoxMismatch(prevChoices):
        return '5'

    @staticmethod
    def getOptionsBoxDelta(prevChoices):
        return '7'

    @staticmethod
    def getOptionsBoxPm(prevChoices):
        return '80'

    @staticmethod
    def getOptionsBoxPi(prevChoices):
        return '10'

    @staticmethod
    def getOptionsBoxMinscore(prevChoices):
        return '50'

    @staticmethod
    def getOptionsBoxMaxperiod(prevChoices):
        return '300'

    @staticmethod
    def getOptionsBoxMinconsensus(prevChoices):
        return '190'

    @staticmethod
    def getOptionsBoxMaxconsensus(prevChoices):
        return '240'

    @staticmethod
    def takePromotersFromFile(fileNamePath, minConsensusLength, maxConsensusLength):
        inputFile = open(fileNamePath, 'r')

        resultDict = {}

        with inputFile as f:
            i = 0
            j = -1
            for line in f.readlines():
                splitLine = line.split(' ')
                # print 'i' + str(i) + ' jj ' + str(j) + ' x' + str(splitLine)

                if splitLine[0] == 'Sequence:':
                    name = splitLine[1] + ':' + splitLine[2]
                    chr = splitLine[1]
                    posSt = int(splitLine[2].split('-')[0])
                    posEnd = int(splitLine[2].split('-')[1])

                if splitLine[0] == 'Parameters:':
                    j = i + 3

                if j >= 0 and len(splitLine) >= 13:
                    # print 'j' + str(j) + 'x' + str(splitLine)
                    # posStart, posEnd, copyNumber, consensus
                    # if len(splitLine[13]) >= 190 and len(splitLine[13]) <= 240:
                    if len(splitLine[13]) >= minConsensusLength and len(splitLine[13]) <= maxConsensusLength:
                        if not name in resultDict:
                            resultDict[name] = []
                        repeats = int(math.floor(float(splitLine[3])))  # copyNumber

                        # for now I am not using posEnd



                        # Madeline wanted to have separate monomer but then she changed mind
                        # for numRep in range(0, repeats):
                        #     resultDict[name].append([chr, \
                        #                              int(splitLine[0]) + (numRep) * int(len(splitLine[13])) + posSt, \
                        #                              int(splitLine[0]) + (numRep+1) * int(len(splitLine[13])) + posSt, \
                        #                              str(splitLine[13]) + '-' + str(numRep) + '-' + str(name)
                        #                              ])

                        resultDict[name].append([chr, \
                                                 int(splitLine[0]) + posSt - 1, \
                                                 int(splitLine[0]) + (repeats) * int(len(splitLine[13])) + posSt - 2, \
                                                 str(splitLine[13]) + '-' + str(repeats) + '-' + str(name)
                                                 ])

                i += 1
        return resultDict

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        import os, subprocess

        match = int(choices.match)
        mismatch = int(choices.mismatch)
        delta = int(choices.delta)
        pm = int(choices.pm)
        pi = int(choices.pi)
        minscore = int(choices.minscore)
        maxperiod = int(choices.maxperiod)
        minConsensusLength = int(choices.minconsensus)
        maxConsensusLength = int(choices.maxconsensus)

        gsuite = getGSuiteFromGalaxyTN(choices.gsuite)

        outGSuite = GSuite()

        for gsTrack in gsuite.allTracks():

            print '\n\n\n', gsTrack.title
            fastaFilepath = gsTrack.path
            print 'fasta file path: ', fastaFilepath
            print 'cur dir: ', os.getcwd()
            print 'fasta file dir: ', os.path.dirname(fastaFilepath)
            print 'galaxyFn dir: ', os.path.dirname(os.path.realpath(galaxyFn))
            resFile = GalaxyRunSpecificFile(['trf', gsTrack.title, gsTrack.title + '.tmp'], galaxyFn)
            ensurePathExists(resFile.getDiskPath())
            print 'resFile: ', resFile.getDiskPath()
            trackDirName = os.path.dirname(os.path.realpath(resFile.getDiskPath()))
            print 'resFile dir: ', trackDirName
            # parameters = ["2", "5", "7", "80", "10", "50", "300"] #Madeleine suggestion
            parameters = [str(match), str(mismatch), str(delta), str(pm), str(pi), str(minscore), str(maxperiod)]
            instruction = [cls.TRF_PATH, gsTrack.path] + parameters + ["-d"]
            pipe = subprocess.Popen(instruction, cwd=trackDirName, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            results, errors = pipe.communicate()

            fileName = fastaFilepath.split('/')[-1]
            fileParameters = ('.').join(parameters)
            fileExtension = 'dat'

            # we need to take the newest version of .dat file

            # print fileName
            # print fileParameters
            # print fileExtension



            for fileDN in os.listdir(trackDirName):
                # print fileDN
                if fileName in fileDN and fileParameters in fileDN and fileExtension in fileDN.split('.')[-1]:

                    print 'counting results ...'

                    result = trfFromGSuite.takePromotersFromFile(trackDirName + '/' + fileDN, minConsensusLength,
                                                                 maxConsensusLength)

                    if len(result) != 0:

                        bedFileName = trackDirName.split('/')[-1]

                        uri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn,
                                                            extraFileName=bedFileName,
                                                            suffix='bed')

                        gSuiteTrack = GSuiteTrack(uri)
                        outFn = gSuiteTrack.path
                        ensurePathExists(outFn)

                        with open(outFn, 'w') as outputFile:
                            headerFirst = 'track name="' + str(bedFileName) + '" description="' + str(
                                bedFileName) + '" priority=1'
                            outputFile.write(headerFirst + os.linesep)

                            for keyRes, itRes in result.items():
                                for elItRes in itRes:
                                    outputFile.write('\t'.join(str(x) for x in elItRes) + os.linesep)

                        outputFile.close()

                        outGSuite.addTrack(GSuiteTrack(uri, title=''.join(bedFileName), genome=gsuite.genome))

            GSuiteComposer.composeToFile(outGSuite, cls.extraGalaxyFn['MRS Gsuite'])

        print 'MRS - done'

    @staticmethod
    def validateAndReturnErrors(choices):
        return None

    @classmethod
    def getExtraHistElements(cls, choices):
        return [HistElement('MRS Gsuite', 'gsuite')]


class trfFromFasta(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Trf from fasta files"

    @staticmethod
    def getInputBoxNames():
        return [('Select fasta track', 'track')
                ]

    @staticmethod
    def getOptionsBoxTrack():
        return GeneralGuiTool.getHistorySelectionElement('fas', 'fasta')

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        # working instruction
        # /software/VERSIONS/trf-4.0.4/bin/trf404.linux64 /software/galaxy/galaxy-dist-hg-gsuite-submit/database/files/121/dataset_121396.dat 2 6 6 80 10 50 500 -f -d -m

        import os, subprocess
        import shutil

        # track with fasta file inside
        track = choices.track
        sequence = ExternalTrackManager.extractFnFromGalaxyTN(track.split(':'))

        # path to track
        path = sequence.split('/')

        # name of file
        name = path[-1]

        # path with copied file
        path = ('/').join(path[:-1])

        # print sequence
        # print os.getcwd()

        # path to program
        dir = "/software/VERSIONS/trf-4.0.4/bin/trf404.linux64"

        parameters = ["2", "5", "7", "80", "10", "50", "300"]
        instruction = [dir, sequence] + parameters + ["-d"]

        ensurePathExists(path + "/trfData/")

        pipe = subprocess.Popen(instruction, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        results, errors = pipe.communicate()

        # files to copy
        filename = []
        filename.append(name + '.' + '.'.join(parameters) + '.dat')

        # print 'results: \n' + str(results)
        # print 'errors: \n' + str(errors)

        for fN in filename:
            shutil.copy2(os.getcwd() + "/" + fN, path + "/trfData/" + fN)

        inputFile = open(path + "/trfData/" + filename[0], 'r')

        resultDict = {}

        with inputFile as f:
            i = 0
            j = -1
            for line in f.readlines():
                splitLine = line.split(' ')
                # print 'i' + str(i) + ' jj ' + str(j) + ' x' + str(splitLine)

                if splitLine[0] == 'Sequence:':
                    name = splitLine[1] + ' ' + splitLine[2]
                    posSt = splitLine[2].split('-')[0]
                    posEnd = splitLine[2].split('-')[1]

                if splitLine[0] == 'Parameters:':
                    j = i + 3

                if j >= 0 and len(splitLine) >= 13:
                    # print 'j' + str(j) + 'x' + str(splitLine)
                    # posStart, posEnd, copyNumber, consensus
                    if len(splitLine[13]) >= 190 and len(splitLine[13]) <= 240:
                        if not name in resultDict:
                            resultDict[name] = []
                        repeats = math.floor(splitLine[3])  # copyNumber
                        resultDict[name].append(
                            [splitLine[0] + posSt, (repeats * splitLine[1]) + posEnd, splitLine[13]])
                i += 1

        print resultDict

        print 'Files are in the directory: ' + path + "/trfData/"

    @staticmethod
    def validateAndReturnErrors(choices):
        return None

    @staticmethod
    def getOutputFormat(choices):
        return 'html'


class justCutOffValue(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Gene expression - select just cutoff value for track"

    @staticmethod
    def getInputBoxNames():
        return [('Select track collection GSuite', 'bedFile'),
                ('If one line header', 'header')
                ]

    @staticmethod
    def getOptionsBoxBedFile():
        return GeneralGuiTool.getHistorySelectionElement('bed', 'tabular', 'gtf')

    @staticmethod
    def getOptionsBoxHeader(prevChoices):
        return ['Yes', 'No']

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        header = choices.header
        if header == 'Yes':
            indexHeader = 1
        else:
            indexHeader = 0

        listCol = []
        inputFile = open(ExternalTrackManager.extractFnFromGalaxyTN(choices.bedFile.split(':')), 'r')

        data = OrderedDict()
        i = 0
        strr = ''
        with inputFile as f:
            for x in f.readlines():
                if i == 0:
                    header = x
                if i >= indexHeader:
                    ee = x.strip('\n').split('\t')
                    if i == indexHeader:
                        lenEl = len(ee)
                    if lenEl == len(ee):
                        if float(ee[5]) > 0.8:
                            minusOne = int(ee[1]) - 1
                            strr += 'chr' + str(ee[0]) + '\t' + str(minusOne) + '\t' + str(ee[2]) + '\t' + str(
                                ee[3]) + '\n'

                i += 1
        f.closed

        open(galaxyFn, 'w').writelines(strr)

    @staticmethod
    def validateAndReturnErrors(choices):
        return None

    @staticmethod
    def getOutputFormat(choices):
        return 'bed'


class bedIntoRFile(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Divide bed file into bed files for R mutations"

    @staticmethod
    def getInputBoxNames():
        return [('Select track collection GSuite', 'bedFile'),
                ('If one line header', 'header')
                ]

    @staticmethod
    def getOptionsBoxBedFile():
        return GeneralGuiTool.getHistorySelectionElement('bed')

    @staticmethod
    def getOptionsBoxHeader(prevChoices):
        return ['Yes', 'No']

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        header = choices.header
        if header == 'Yes':
            indexHeader = 1
        else:
            indexHeader = 0

        listCol = []
        inputFile = open(ExternalTrackManager.extractFnFromGalaxyTN(choices.bedFile.split(':')), 'r')

        data = OrderedDict()
        i = 0
        with inputFile as f:
            for x in f.readlines():
                if i == 0:
                    header = 'Sample' + '\t' + 'chr' + '\t' + 'pos' + '\t' + 'ref' + '\t' + 'alt' + '\n'
                if i >= indexHeader:
                    ee = x.strip('\n').split('\t')
                    if i == indexHeader:
                        lenEl = len(ee)
                    if lenEl == len(ee):
                        fileName = ee[3].split('_')[0]
                        mut = list(ee[3].split('_')[1])

                        if not fileName in data:
                            data[fileName] = ''
                            strr = '1' + '\t' + str(ee[0]) + '\t' + str(ee[2]) + '\t' + str(mut[0]) + '\t' + str(
                                mut[1]) + '\n'
                        data[fileName] += strr
                i += 1
        f.closed

        htmlCore = HtmlCore()
        htmlCore.begin()

        for fN in data:
            outputFile = open(cls.makeHistElement(galaxyExt='tabular', title=str(fN)), 'w')
            outputFile.write(header + data[fN])
            outputFile.close()
            htmlCore.line('File ' + str(fN) + ' is in the history.')

        htmlCore.end()

        htmlCore.hideToggle(styleClass='debug')

        print htmlCore

    @staticmethod
    def validateAndReturnErrors(choices):
        return None

    @staticmethod
    def getOutputFormat(choices):
        return 'html'


class kmersTab(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Change format for k-mers"

    @staticmethod
    def getInputBoxNames():
        return [('Select file', 'file')
                ]

    @staticmethod
    def getOptionsBoxFile():
        return GeneralGuiTool.getHistorySelectionElement('tabular')

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        # Track.trackname
        # store pickle

        strr = ''
        with open(ExternalTrackManager.extractFnFromGalaxyTN(choices.file.split(':')), 'r') as f:
            for x in f.readlines():
                e = x.strip('\n').split('\t')
                strr += str(e[0]) + '[' + str(e[3]) + '>' + str(e[4]) + ']' + str(e[2]) + '\t' + str(
                    int(float(e[5]))) + '\n'
        f.closed

        open(galaxyFn, 'w').writelines(strr)

    @staticmethod
    def validateAndReturnErrors(choices):
        return None

    @staticmethod
    def getOutputFormat(choices):
        return 'tabular'
        # return 'customhtml'


class kmersAddMut(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Divide gSuite and add mutation for k-mers"

    @staticmethod
    def getInputBoxNames():
        return [('Select file', 'track'),
                ('Gsuite name', 'gSuiteName'),
                ('Expression', 'param')
                ]

    @staticmethod
    def getOptionsBoxTrack():
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @staticmethod
    def getOptionsBoxGSuiteName(prevChoices):
        return ''

    @staticmethod
    def getOptionsBoxParam(prevChoices):
        return ''

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        # Track.trackname
        # store pickle

        with open(ExternalTrackManager.extractFnFromGalaxyTN(choices.track.split(':')), 'r') as f:
            data = [x.strip('\n') for x in f.readlines()]
        f.closed

        htmlCore = HtmlCore()
        htmlCore.begin()

        dataCopy = data[:]
        if choices.param != '':
            for el in choices.param.split(','):

                newlC = str(el)

                outputFile = open(
                    cls.makeHistElement(galaxyExt='gsuite', title=str(choices.gSuiteName) + ' (' + str(el) + ')'), 'w')
                output = ''
                for d in range(0, len(data)):
                    if d < 4:
                        output += data[d]
                        output += '\n'
                    elif d == 4:
                        output += data[d]
                        output += '\t' + 'dir_level1' + '\t' + 'dir_level2'
                        output += '\n'
                    else:
                        newData = data[d].split("\t")
                        if str(el) in newData[1]:
                            mut = list(newData[1])[-2:]
                            tit = newData[1].split(' (')[1]
                            newData[1] = tit

                            output += '\t'.join(newData) + '\t'
                            output += '\t'.join(mut)
                            output += '\n'
                            dataCopy.remove(data[d])

                outputFile.write(output)
                outputFile.close()

                data = dataCopy[:]

                htmlCore.line('File ' + str(newlC) + ' is in the history.')

        htmlCore.end()

        htmlCore.hideToggle(styleClass='debug')

        print htmlCore

    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''

        return None

    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'customhtml'


class kmers(GeneralGuiTool):
    ALLOW_UNKNOWN_GENOME = True

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "K-mers mutation sum up (cleaning)"
        # Plot tabular values

    @staticmethod
    def getInputBoxNames():
        return [
            ('Select tabular file', 'file'),
        ]

    @staticmethod
    def getOptionsBoxFile():
        return GeneralGuiTool.getHistorySelectionElement('txt', 'tabular')

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):

        file = choices.file

        i = 0
        with open(ExternalTrackManager.extractFnFromGalaxyTN(file.split(':')), 'r') as f:
            dataX = []
            for x in f.readlines():

                el = x.strip('\n').split('\t')
                nr = 0

                l = []
                for e in el:
                    if e != '':
                        try:
                            l.append(float(e))
                        except:
                            l.append(e)
                        nr += 1
                dataX.append(l)
                i += 1
        f.closed

        dataX = sorted(dataX, key=operator.itemgetter(3, 4, 1, 0, 2), reverse=False)
        columnFiltered = [3, 4]

        final = OrderedDict()

        strand = [['A', 'T', 'G', 'C'], ['T', 'A', 'C', 'G']]

        for dNum in range(0, len(dataX)):

            if dataX[dNum][3] == 'C' or dataX[dNum][3] == 'T':
                pass
            else:
                inx1 = strand[0].index(dataX[dNum][3])  # A -> T
                inx2 = strand[0].index(dataX[dNum][4])  # T -> A

                # AC -> TG czy GT (to pierwsze)
                # AT -> TA czy AT
                # TA -> AT czy TA


                # return strand
                dataX[dNum][3] = strand[1][inx1]
                dataX[dNum][4] = strand[1][inx2]

        for dNum in range(0, len(dataX)):

            columnFilteredList = ''
            for eNum in columnFiltered:
                columnFilteredList += str(dataX[dNum][int(eNum)]) + '-'

            if not columnFilteredList in final:
                final[columnFilteredList] = OrderedDict()

            # remove zeros
            # if dataX[dNum][5] != 0:

            if dataX[dNum][1] == 'T' or dataX[dNum][1] == 'C':
                ifexist = ''.join(dataX[dNum][:3])  # right strand ACA
                ifexist = ifexist
            else:
                inx1 = strand[0].index(dataX[dNum][0])
                inx2 = strand[0].index(dataX[dNum][1])
                inx3 = strand[0].index(dataX[dNum][2])

                inx = [strand[1][inx3], strand[1][inx2], strand[1][inx1]]
                ifexist2 = ''.join(inx)  # left strand TGT

                # return strand
                dataX[dNum][0] = strand[1][inx3]
                dataX[dNum][1] = strand[1][inx2]
                dataX[dNum][2] = strand[1][inx1]

                ifexist = ifexist2

            # double cleaning
            if dataX[dNum][1] == dataX[dNum][3]:

                ifexistTF = False

                if ifexist in final[columnFilteredList].keys():
                    ifexistTF = True

                if ifexistTF == False:
                    final[columnFilteredList][ifexist] = dataX[dNum]

                if ifexistTF == True:
                    final[columnFilteredList][ifexist][5] += dataX[dNum][5]

        strr = ''
        for k, v in final.iteritems():
            for rr in v.values():
                for r in rr:
                    strr += str(r) + '\t'
                strr += '\n'

        open(galaxyFn, 'w').writelines([strr])

    #         leftStrand = ['CA', 'CG', 'CT', 'TA', 'TC', 'TG']
    #         rightStrand = ['GT', 'GC', 'GA', 'AT', 'AG', 'AC']



    @staticmethod
    def getOutputFormat(choices):
        #         return 'customhtml'
        return 'tabular'


class statGSuite(GeneralGuiTool, UserBinMixin, GenomeMixin, DebugMixin):
    ALLOW_UNKNOWN_GENOME = False
    ALLOW_GENOME_OVERRIDE = False

    RAW_OVERLAP_TABLE_RESULT_KEY = 'Raw_overlap_table'
    SIMILARITY_SCORE_TABLE_RESULT_KEY = 'Similarity_score_table'

    GSUITE_FILE_OPTIONS_BOX_KEYS = ['gSuite1', 'gSuite2']

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Analysis between two gSuites"
        # Plot tabular values

    @classmethod
    def getInputBoxNames(cls):
        return [('Select GSuite (eg. SNPs)', 'gSuite1'), \
                ('Select GSuite (eg. miRNAs)', 'gSuite2')] + \
               cls.getInputBoxNamesForGenomeSelection() + \
               [
                   ('Select statistic', 'stat')
               ] + \
               cls.getInputBoxNamesForUserBinSelection() + \
               cls.getInputBoxNamesForDebug()

    @staticmethod
    def getOptionsBoxGSuite1():  # refTrack
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @staticmethod
    def getOptionsBoxGSuite2(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @staticmethod
    def getOptionsBoxStat(prevChoices):
        # relative position of snps per segment
        return ['Count relative positions of first gSuite per second gSuite']

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        cls._setDebugModeIfSelected(choices)

        queryGSuite = getGSuiteFromGalaxyTN(choices.gSuite1)
        refGSuite = getGSuiteFromGalaxyTN(choices.gSuite2)

        if choices.stat == 'Count relative positions of first gSuite per second gSuite':
            stat = 'PointPositionsInSegsStat'

        genome = choices.genome

        regSpec, binSpec = UserBinMixin.getRegsAndBinsSpec(choices)
        analysisBins = GalaxyInterface._getUserBinSource(regSpec, binSpec, genome=genome)

        queryTrackList = [Track(x.trackName, x.title) for x in queryGSuite.allTracks()]
        refTrackList = [Track(x.trackName, x.title) for x in refGSuite.allTracks()]

        queryTrackTitles = CommonConstants.TRACK_TITLES_SEPARATOR.join(
            [quote(x.title, safe='') for x in queryGSuite.allTracks()])
        refTrackTitles = CommonConstants.TRACK_TITLES_SEPARATOR.join(
            [quote(x.title, safe='') for x in refGSuite.allTracks()])

        analysisSpec = AnalysisSpec(GSuiteVsGSuiteWrapperStat)
        analysisSpec.addParameter('queryTracksNum', str(len(queryTrackList)))
        analysisSpec.addParameter('refTracksNum', str(len(refTrackList)))
        analysisSpec.addParameter('queryTrackTitleList', queryTrackTitles)
        analysisSpec.addParameter('refTrackTitleList', refTrackTitles)
        #         from quick.statistic.StatFacades import ObservedVsExpectedStat

        # using .__name__ is better than make it as a string
        analysisSpec.addParameter('similarityStatClassName', str(stat))
        # analysisSpec.addParameter('addSegmentLengths', 'False')
        analysisSpec.addParameter('scaledPositions ', 'False')

        resultsObj = doAnalysis(analysisSpec, analysisBins, queryTrackList + refTrackList)
        results = resultsObj.getGlobalResult()

        baseDir = GalaxyRunSpecificFile([], galaxyFn=galaxyFn).getDiskPath()
        tablePresenter = MatrixGlobalValueFromTableDataPresenter(resultsObj, baseDir=baseDir,
                                                                 header='Table of ' + str(choices.stat))

        core = HtmlCore()
        core.begin()
        core.divBegin(divId='results-page')
        core.divBegin(divClass='results-section')
        core.line(tablePresenter.getReference(statGSuite.SIMILARITY_SCORE_TABLE_RESULT_KEY))

        core.divEnd()
        core.divEnd()
        core.end()

        print str(core)

    @staticmethod
    def isDebugMode():
        '''
        Specifies whether the debug mode is turned on.
        '''
        return True

    @staticmethod
    def getOutputFormat(choices):
        return 'customhtml'


class examTool1(GeneralGuiTool):
    ALLOW_UNKNOWN_GENOME = True

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Exam tool"
        # Plot tabular values

    @staticmethod
    def getInputBoxNames():
        return [
            ('Select GSuite', 'gSuite'),
            #('Select file cintains examiners name', examName)
        ]

    @staticmethod
    def getOptionsBoxGSuite():
        return GeneralGuiTool.getHistorySelectionElement('gsuite')


    #
    # check if file format is correct
    #


    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        gSuite = choices.gSuite

        gSuite = getGSuiteFromGalaxyTN(gSuite)

        data = OrderedDict()
        data['internal'] = {}
        data['external'] = {}

        header = []
        j = 0
        for title in gSuite.allTrackTitles():
            gSuiteTrack = gSuite.getTrackFromTitle(title)

            i = 0
            with open(gSuiteTrack.path) as f:
                for x in f.readlines():
                    el = x.strip('\n').split('\t')
                    if i >= 2:
                        key = el[0]

                        if key in data['internal'].keys():
                            data['external'][key] = ('\t').join(el) + '\n'
                        else:
                            data['internal'][key] = ('\t').join(el) + '\n'
                    else:
                        if j == 0:
                            header.append(('\t').join(el) + '\n')

                    i += 1
            j += 1

        # first students internal
        outputFile = open(cls.makeHistElement(galaxyExt='tabular', title='Internal'), 'w')

        d = sorted(data['internal'].values())
        res = ('').join(header) + ('').join(d)

        outputFile.write(res)
        outputFile.close()

        # second students external
        outputFile = open(cls.makeHistElement(galaxyExt='tabular', title='External'), 'w')

        d = sorted(data['external'].values())
        res = ('').join(header) + ('').join(d)

        outputFile.write(res)
        outputFile.close()

    @staticmethod
    def getOutputFormat(choices):
        return 'tabular'
        # return 'customhtml'


class analyseDeepGsuiteV2(GeneralGuiTool, UserBinMixin):
    GSUITE_FILE_OPTIONS_BOX_KEYS = ['firstGSuite', 'secondGSuite']

    MERGE_INTRA_OVERLAPS = 'Merge any overlapping points/segments within the same track'
    ALLOW_MULTIPLE_OVERLAP = 'Allow multiple overlapping points/segments within the same track'

    @classmethod
    def summarizeTable(cls, flat, operations):
        for i, op in reversed(list(enumerate(operations))):
            if op >= 0:
                flat = [x[:i] + x[i + 1:] for x in flat if x[i] == op]
            elif op == -1:
                flat = [x[:i] + x[i + 1:] for x in flat]
                d = defaultdict(int)
                for x in flat:
                    if x[-1] != None:
                        d[tuple(x[:-1])] += x[-1]
                flat = [list(x) + [d[x]] for x in d]
        return flat

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Analyse between two gSuites with any level (js)"

    @classmethod
    def getInputBoxNames(cls):
        return [
                   ('Select first GSuite', 'firstGSuite'),
                   ('Test', 'test'),
                   ('Select column', 'firstGSuiteColumn'),
                   ('Select second GSuite', 'secondGSuite'),
                   ('Select column', 'secondGSuiteColumn'),
                   ('Check genome or select column with multi genome', 'genome'),
                   ('Select statistic type', 'type'),
                   ('Select statistic', 'statistic'),
                   ('Select overlap handling', 'intraOverlap')
               ] + cls.getInputBoxNamesForUserBinSelection()

    @staticmethod
    def getOptionsBoxFirstGSuite():
        return GeneralGuiTool.getHistorySelectionElement('gsuite', 'txt', 'tabular')

    @staticmethod
    def getOptionsBoxTest(prevChoices):
        return ['2 level output', '3 level output', '4 level output', '5 level output']

    @staticmethod
    def getOptionsBoxFirstGSuiteColumn(prevChoices):
        if prevChoices.firstGSuite:
            first = getGSuiteFromGalaxyTN(prevChoices.firstGSuite)
            attributeList = [None] + first.attributes
            return attributeList
        else:
            return

    @staticmethod
    def getOptionsBoxSecondGSuite(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement('gsuite', 'txt', 'tabular')

    @staticmethod
    def getOptionsBoxSecondGSuiteColumn(prevChoices):
        if prevChoices.secondGSuite:
            second = getGSuiteFromGalaxyTN(prevChoices.secondGSuite)
            attributeList = [None] + second.attributes
            return attributeList
        else:
            return

    @staticmethod
    def getOptionsBoxGenome(prevChoices):
        if not prevChoices.firstGSuite:
            return
        if not prevChoices.secondGSuite:
            return

        # it will be good to have box with selected genome instead of text

        if prevChoices.firstGSuite and prevChoices.secondGSuite:
            first = getGSuiteFromGalaxyTN(prevChoices.firstGSuite)
            second = getGSuiteFromGalaxyTN(prevChoices.secondGSuite)
            if first.genome or second.genome:
                return first.genome
            else:
                attributeList1 = first.attributes
                attributeList2 = second.attributes
                retDict = OrderedDict()

                for et in attributeList1:
                    retDict[et + ' (first GSuite)'] = False

                for et in attributeList2:
                    retDict[et + ' (second GSuite)'] = False

                return retDict
        else:
            return
            # genome = 'multi' #then should be taken from one column

    @staticmethod
    def getOptionsBoxType(prevChoices):
        return ['basic', 'advanced']

    @staticmethod
    def getOptionsBoxStatistic(prevChoices):
        if prevChoices.type == 'basic':
            return [STAT_OVERLAP_COUNT_BPS,
                    STAT_OVERLAP_RATIO,
                    STAT_FACTOR_OBSERVED_VS_EXPECTED,
                    STAT_COVERAGE_RATIO_VS_QUERY_TRACK,
                    STAT_COVERAGE_RATIO_VS_REF_TRACK
                    ]
        else:
            return ['Number of touched segments']

    @staticmethod
    def getOptionsBoxIntraOverlap(prevChoices):
        return [analyseDeepGsuiteV2.MERGE_INTRA_OVERLAPS,
                analyseDeepGsuiteV2.ALLOW_MULTIPLE_OVERLAP]

    @classmethod
    def returnGSuiteLevelDepth(cls, gSuite):
        gSuite = getGSuiteFromGalaxyTN(gSuite)
        attributeList = gSuite.attributes

        attributeList = [TITLE_COL] + attributeList
        attributeValuesList = getAllTracksWithAttributes(gSuite)

        return attributeList, attributeValuesList

    @classmethod
    def makeAnalysis(cls, gSuite1, gSuite2, columnsForStat, galaxyFn, choices):

        genomeType = 'single'

        # if True then none of column in both gsuite are equal then for example, for gSUite 2 dim and 3 dim we have 5 dim
        # in the other case (when some columns are equal we have 4 dim)
        checkWhichDimension = False
        for el in columnsForStat:
            if el == None:
                checkWhichDimension = True
                break

        if choices.type == 'basic':
            stat = choices.statistic
            statIndex = STAT_LIST_INDEX[stat]
        else:
            stat = '0'
            statIndex = 0

        if choices.intraOverlap == analyseDeepGsuiteV2.MERGE_INTRA_OVERLAPS:
            analysisDef = 'dummy -> RawOverlapStat'
        else:
            analysisDef = 'dummy [withOverlaps=yes] -> RawOverlapAllowSingleTrackOverlapsStat'

        regSpec, binSpec = UserBinMixin.getRegsAndBinsSpec(choices)

        listResults = []
        for el1 in gSuite1:
            for el2 in gSuite2:
                if genomeType == 'single':

                    listPartResults = []
                    if el1[columnsForStat[0]] == el2[columnsForStat[1]]:
                        gSuite1Path = el1[0]  # path for track1
                        gSuite2Path = el2[0]  # path for track2

                        result = GalaxyInterface.runManual([gSuite1Path, gSuite2Path],
                                                           analysisDef, regSpec, binSpec, choices.genome, galaxyFn,
                                                           printRunDescription=False,
                                                           printResults=False)

                        resVal = processResult(result.getGlobalResult())[statIndex]
                    else:
                        resVal = None

                    if checkWhichDimension == False:
                        listPartResults = el1[1:] + el2[1:] + [resVal]
                    else:
                        shorterEl2 = []
                        for eN in range(0, len(el2[1:])):
                            if el2[1:][eN] != columnsForStat[1] - 1:
                                shorterEl2.append(el2[1:][eN])
                        listPartResults = el1[1:] + shorterEl2 + [resVal]

                    listResults.append(listPartResults)

                if genomeType == 'multi':
                    # count only values with the same genome
                    pass

        return listResults

    @staticmethod
    def fillFirstSelect(firstSelectTitle, idNum, listOfColumns, listResult):
        js = firstSelectTitle + '''

        <script>

        var plotDiv = document.getElementById('container1');
        plotDiv.setAttribute('class', 'hidden');


        var listOfColumns = ''' + str(listOfColumns) + ''';
        var resultsTableOryginal = ''' + str(listResult) + ''';
        </script>

        <select name="dimensions''' + str(idNum) + '''" id="dimensions''' + str(
            idNum) + '''" size="1" onClick="onClickChoices(listOfColumns)" onChange="updateChoices''' + str(idNum) + '''(this.selectedIndex)" style="width: 150px">
        <option value="0">---Select---</option>
        <option value="1">Select one value</option>
        <option value="-2">Show results for each value</option>
        <option value="-1">Sum across this dimension</option>
        </select>
        '''
        return js

    @staticmethod
    def fillSecondSelect(secondSelectTitle, idNum):
        js = '''
        <select name="choices''' + str(idNum) + '''" id="choices''' + str(idNum) + '''" size="1" style="width: 100px"  onClick="onClickChoices(listOfColumns)">
        </select>'''
        return js

    @staticmethod
    def addSecondSelectInfo(idNum):
        js = '''document.getElementById("choices''' + str(idNum) + '''").style.visibility = "hidden";
        var dimensionslist''' + str(idNum) + '''=document.classic.dimensions''' + str(idNum) + ''';
        var choiceslist''' + str(idNum) + '''=document.classic.choices''' + str(idNum) + ''';

        '''
        return js

    @staticmethod
    def fillSecondSelectOption(idNum, data):
        js = '''
        var choices''' + str(idNum) + '''=new Array()
        choices''' + str(idNum) + '''[1]=''' + data
        return js

    @staticmethod
    def updateChoices(idNum):
        js = '''



        function updateChoices''' + str(idNum) + '''(selectedChoicesGroup)
        {
            hideTable()
            document.getElementById("choices''' + str(idNum) + '''").style.visibility = "hidden";
            if(selectedChoicesGroup  == 1)
            {
                document.getElementById("choices''' + str(idNum) + '''").style.visibility = "visible";

                choiceslist''' + str(idNum) + '''.options.length=0
                if (selectedChoicesGroup>0)
                {
                    for (i=0; i<choices''' + str(idNum) + '''[selectedChoicesGroup].length; i++)
                    {
                        choiceslist''' + str(idNum) + '''.options[choiceslist''' + str(
            idNum) + '''.options.length]=new Option(choices''' + str(
            idNum) + '''[selectedChoicesGroup][i].split("|")[0], choices''' + str(idNum) + '''[selectedChoicesGroup][i].split("|")[1])
                    }
                }
                var dimensions''' + str(idNum) + ''' = document.getElementById("dimensions''' + str(idNum) + '''");
                dimensions''' + str(idNum) + '''.options[selectedChoicesGroup].setAttribute("selected", "selected");
            }
        }
        '''
        return js

    @staticmethod
    def addLevelOptionList(listOfColumns, listResult):

        js = """
        <form name="classic">
        """
        for locNum in range(0, len(listOfColumns)):
            js += analyseDeepGsuiteV2.fillFirstSelect("How to treat " + str(locNum), locNum, listOfColumns, listResult)
            js += analyseDeepGsuiteV2.fillSecondSelect("Selected value", locNum)
            js += "<br \><br \>"

        js += """
        </form>

        <script type="text/javascript">
        """

        for locNum in range(0, len(listOfColumns)):
            js += analyseDeepGsuiteV2.addSecondSelectInfo(locNum)

            js += """ folderValue""" + str(locNum) + """ =""" + str(listOfColumns[locNum]) + ";"
            js += """
                    var fol""" + str(locNum) + """ = new Array(folderValue""" + str(locNum) + """.length)
                    fol""" + str(locNum) + """[0] = "Select value|0"
                    for(i=0;i<folderValue""" + str(locNum) + """.length;i++)
                    {
                        j=i+1
                        fol""" + str(locNum) + """[j] = folderValue""" + str(locNum) + """[i] +'|' + j
                    }
                    j=j+1
            """

        js += """

        var chocieslistRowColumn=document.classic.choicesRowColumn
        """

        for locNum in range(0, len(listOfColumns)):
            js += analyseDeepGsuiteV2.fillSecondSelectOption(locNum, """fol""" + str(locNum))
            js += analyseDeepGsuiteV2.updateChoices(locNum)

        js += """
        function updateChoicesRowColumn(selectedChoicesGroupRowColumn, selDim)
        {
            hideTable()

            var ch = document.getElementById("choices1");
            var selCh = ch.selectedIndex
            selDim=selDim-1

            if(selCh != 0 && selCh != 3)
            {
                document.getElementById("choicesRowColumn").style.visibility = "visible";

                chocieslistRowColumn.options.length=0
                if (selectedChoicesGroupRowColumn>0)
                {
                    for (j=0; j<choicesRowColumn.length; j++)
                    {
                        if(j == selDim)
                        {
                            for (i=0; i<choicesRowColumn[selDim][selectedChoicesGroupRowColumn].length; i++)
                            {
                                chocieslistRowColumn.options[chocieslistRowColumn.options.length]=new Option(choicesRowColumn[j][selectedChoicesGroupRowColumn][i].split("|")[0], choicesRowColumn[j][selectedChoicesGroupRowColumn][i].split("|")[1])
                            }
                        }
                    }
                }
            }
            else
            {
                document.getElementById("choicesRowColumn").style.visibility = "hidden";
                if(selCh == 3)
                {
                    showAllTables(selDim)
                }
            }
        }

        function hideTable()
        {
            var childDivs = document.getElementById('results').getElementsByTagName('div');
            for( i=0; i< childDivs.length; i++ )
            {
                var childDiv = childDivs[i];

                //console.log('childDiv', childDiv);

                 if ( childDiv.id=='')
                 {
                 }
                 else
                 {
                    var resultsDiv = document.getElementById(childDiv.id);
                    resultsDiv.setAttribute('class', 'hidden');
                }
            }
        }
        function showAllTables(selDim)
        {
            selDim = selDim +1
            var childDivs = document.getElementById('results').getElementsByTagName('div');
            for( i=0; i< childDivs.length; i++ )
            {
                var childDiv = childDivs[i];
                temp = childDiv.id
                temp = temp.replace("[", "");
                temp = temp.replace("]", "");
                var tab = new Array();
                tab = temp.split(",");

                if(tab[0] == selDim)
                {
                    var resultsDiv = document.getElementById(childDiv.id);
                    resultsDiv.setAttribute('class', 'visible');
                }
            }
        }
        function showAllRowsColumn(selDim, selCh)
        {
            var childDivs = document.getElementById('results').getElementsByTagName('div');
            for( i=0; i< childDivs.length; i++ )
            {
                var childDiv = childDivs[i];
                temp = childDiv.id
                temp = temp.replace("[", "");
                temp = temp.replace("]", "");
                var tab = new Array();
                tab = temp.split(",");


                if(tab[0] == selDim && tab[1] == selCh)
                {
                    var resultsDiv = document.getElementById(childDiv.id);
                    resultsDiv.setAttribute('class', 'visible');
                }
            }
        }


        function summarizeTable(flat, operations)
        {
            //console.log(operations);
            for (var i = operations.length-1; i>=0; i--)
            {
                op = operations[i];
                //console.log('op',op);
                //console.log('i',i);

                if (op>=0 || typeof op == 'string')
                {
                    //console.log('jeden');

                    var flatTemp = [];
                    for(var xL=0; xL<flat.length;xL++)
                    {
                        var x = flat[xL];
                        if(x[i]==op)
                        {
                            //console.log('x', x);
                            var arrayA  = x.slice(0, parseInt(i));
                            var arrayB  = x.slice(parseInt(i)+1, parseInt(x.length));
                            flatTemp.push(arrayA.concat(arrayB));

                            //console.log('arrayA', arrayA, 'arrayB', arrayB, 'flatTemp', flatTemp);

                        }
                    }
                    flat = flatTemp;
                    //console.log('flat jeden ', flat);
                }
                else if (op == -1)
                {
                    var flatTemp = [];
                    for(var xL=0; xL<flat.length;xL++)
                    {
                        var x = flat[xL];
                        ////console.log(x);
                        var arrayA  = x.slice(0, parseInt(i));
                        var arrayB  = x.slice(parseInt(i)+1, parseInt(x.length));
                        flatTemp.push(arrayA.concat(arrayB));
                    }
                    flat = flatTemp;
                    d={}
                    for(var xL=0; xL<flat.length;xL++)
                    {
                        ////console.log('jestem1');
                        var x = flat[xL];

                        ////console.log('x[-1]',x.slice(-1).pop());
                        if (x.slice(-1).pop() != undefined)
                        {
                            var y = x.slice(0, parseInt(x.length)-1);

                            var tuple = y.join("---");

                            if(!(tuple in d))
                            {
                                d[tuple]=0;
                            }

                            d[tuple] += x.slice(-1).pop();
                            ////console.log(d);
                        }
                    }

                    var flat = [];
                    ////console.log("jestem2", d.length);
                    for(var w in d)
                    {

                        ////console.log('w', w, w.split("---"), 'd[w]', d[w]);

                        var arrayA = w.split("---");
                        ////console.log();
                        var arrayB = [d[w]];
                        ////console.log();
                        var n = arrayA.concat(arrayB);
                        //console.log('first', arrayA, 'second', arrayB, 'n --- ', n);
                        flat.push(n);
                    }
                    //console.log('flat ---- ', flat);
                }
            }
            return flat;
        }

        function remove_duplicates_safe(arr) {
            var obj = {};
            var arr2 = [];
            for (var i = 0; i < arr.length; i++) {
                if (!(arr[i] in obj)) {
                    arr2.push(arr[i]);
                    obj[arr[i]] = true;
                }
            }
            return arr2;

        }
        function arr_diff(a1, a2)
{
  var a=[], diff=[];
  for(var i=0;i<a1.length;i++)
    a[a1[i]]=a1[i];
  for(var i=0;i<a2.length;i++)
    if(a[a2[i]]) delete a[a2[i]];
    else a[a2[i]]=a2[i];
  for(var k in a)
  {
    if (!(k == 'alphanumSort'))
                        {
   diff.push(a[k]);
   }
   }
  return diff;
}
        function groupVal(tableDiv, aa)
        {

            //console.log('aa', aa);

            lenAA = aa[0].length;
            newAA={};

            //console.log('lenAA', lenAA);

            for (var el in aa)
            {
                nn = aa[el][1];
                ////console.log(nn);

                if (lenAA == 3)
                {
                    if (!(0 in newAA))
                    {
                        newAA[0] = [];
                    }
                    ////console.log(aa[el]);
                    newAA[0].push(aa[el]);
                }
                if (lenAA >= 4)
                {
                    for (var elN=4; elN < el.length; elN++)
                    {
                        nn += '---'+aa[el][elN-2];
                    }

                    if (!(nn in newAA))
                    {
                        newAA[nn] =[];
                    }
                    newAA[nn].push(aa[el]);
                }
            }

            ////console.log('newAA', newAA);


            var headerList=[];
            for (var key in newAA)
            {
                var resPartList = [];
                var headerPart = [];

                var it = newAA[key];

                for (elN=0; elN < it.length; elN++)
                {
                    var nn='';
                    for (elN1 = 0; elN1 < it[elN].length-2; elN1++)
                    {
                        nn += it[elN][elN1]+'---';
                    }
                    ////console.log('headerPart', nn,  headerPart, headerPart[nn]);

                    if (headerPart.indexOf(nn) <= -1 && nn.length>=1)
                    {
                        headerPart.push(nn);
                    }
                }
                headerList.push(headerPart);
            }


            var resList=[]

            for (var key in newAA)
            {
                var it = newAA[key];

                var resPartList={};

                for (h1 in headerList)
                {
                    for (h3 in headerList[h1])
                    {
                        var h2 = headerList[h1][h3];
                        for (elN=0; elN < it.length; elN++)
                        {
                            var nn='';
                            for (elN1=0; elN1 < it[elN].length-2; elN1++)
                            {
                                nn += it[elN][elN1]+'---';
                            }
                            if (nn == h2)
                            {
                                var e = it[elN][it[elN].length-2];
                                //console.log(resPartList, e);

                                if (!(e in resPartList))
                                {
                                    resPartList[e]={};
                                }

                                if (!(nn in resPartList[e]))
                                {
                                    resPartList[e][nn]=null;
                                }

                                resPartList[e][nn]=it[elN][it[elN].length-1];
                            }
                        }
                    }
                }
                resList.push(resPartList)
            }



            var finalList=[];
            for (elNum2=0; elNum2< resList.length; elNum2++)
            {
                var finalListPart=[];
                for (k in resList[elNum2])
                {
                    var finalListPart2=[k];
                    for (var elNum1=0; elNum1< headerList[elNum2].length; elNum1++)
                    {
                        try
                        {
                            finalListPart2.push(resList[elNum2][k][headerList[elNum2][elNum1]]);
                        }
                        catch(e)
                        {
                            finalListPart2.push(null);
                        }
                    }
                    finalListPart.push(finalListPart2)
                }
                finalList.push(finalListPart)
            }


            var headerCol=[];

            var headerTable = [];
            for (hl1 in headerList)
            {
                ////console.log('hl', hl1, hl1.length);
                if (!(hl1 == 'alphanumSort'))
                {
                    var headerTablePart=[];
                    hl = headerList[hl1];

                    ////console.log('hl', hl, hl.length);
                    if(hl.length > 0)
                    {
                        if (hl.length >=2)
                        {
                            for (h in hl)
                            {
                                //console.log('hl[h]', hl[h], h);
                                if (!(h == 'alphanumSort'))
                                {
                                    var r = headerTablePart.concat(hl[h].split('---'));
                                    headerTablePart = r;
                                }
                            }


                            ////console.log('headerTablePart', headerTablePart);

                            noDuplicate = remove_duplicates_safe(headerTablePart);
                            for (el1=0; el1 < parseInt(headerTablePart.length/2); el1++)
                            {
                                for (el2 = parseInt(headerTablePart.length/2); el2 < headerTablePart.length; el2++)
                                {
                                    if (headerTablePart[el1] == headerTablePart[el2])
                                    {
                                        headerTablePart[el2] = '';
                                        headerTablePart[el1] = '';
                                    }
                                }
                            }

                            ////console.log('headerTablePart', headerTablePart);

                            var htp=[]
                            for (el in headerTablePart)
                            {
                                if (!(headerTablePart[el]==""))
                                {
                                    if (!(el == 'alphanumSort'))
                                    {
                                        htp.push(headerTablePart[el]);
                                    }
                                }
                            }


                            //console.log('htp', htp);
                            //console.log('noDuplicate',noDuplicate);

                            var header = arr_diff(noDuplicate, htp );
                            //console.log('header', header);

                            //header = list(set(noDuplicate) - set(htp))

                        }
                        else if(hl.length == 1)
                        {
                            //console.log('dddddd', hl, hl[0]);
                            h = hl[0].split('---');
                            var header=[];
                            for (var e = 0; e < h.length-2; e++)
                            {
                                header.push(h[e]);
                            }
                            htp=[h[h.length-2]];
                        }

                        headerTable.push(header.join(" "))
                        headerCol.push(htp)
                    }
                }
            }


            // var res=[tableDiv, tableHeader, tableColumn, tableRow];

            //console.log(tableDiv, finalList, headerCol, headerTable);

            row=[];
            row.push(tableDiv);
            row.push(finalList);
            row.push(headerCol);
            row.push(headerTable);


            return row;
        }

        function isNumber(n) { return /^-?[\d.]+(?:e-?\d+)?$/.test(n); }



        function onClickChoices(listOfColumns)
        {
            hideTable();



            //which index, method


            //index
            //-1 - nothing selected
            // 0 - nothing selected
            //index start from 1

            //method
            // 0 - non selected
            // 1 - select one value
            //-1 - show each value
            //-2 - show sum across dimension


            tabEl = parseInt(listOfColumns.length);


            tableIndex=[]
            for (var i =0 ; i< tabEl; i++)
            {
                var c = "choices" + i;
                if (document.getElementById(c) != null)
                {
                    var ch0 = document.getElementById(c);
                    var selCh0 = ch0.value;

                    var dim0 = document.getElementById("dimensions"+i);
                    var selDim0 = dim0.value;

                    //tableIndex.push('choicesIndex'+selCh0);
                    //tableIndex.push('dimensions'+selDim0);

                    if (selDim0!=0)
                    {
                        if (selDim0 != -2 && selDim0 != -1)
                        {
                            if (selCh0 !=0)
                            {
                                tableIndex.push(listOfColumns[i][selCh0-1]);
                                ////console.log('a');
                            }
                            else
                            {
                                ////console.log('b');
                                //tableIndex.push(selCh0);
                            }
                        }
                        else
                        {
                            ////console.log('c');
                            //tableIndex.push(selCh0);
                            tableIndex.push(parseInt(selDim0));
                        }
                    }
                }
            }

            if(listOfColumns.length == tableIndex.length)
            {


                var divName = '';

                if ( tabEl == parseInt(tableIndex.length) )
                {
                  divName += '[';
                  for (var i =0 ; i< tabEl; i++)
                  {
                      if (i < tabEl-1)
                      {
                          if ( Number.isInteger(tableIndex[i]) )
                          {
                              divName += tableIndex[i] + ', ';
                          }
                          else
                          {
                              divName += "'" + tableIndex[i] + "'" + ", ";
                          }
                      }
                      else
                      {
                          if ( Number.isInteger(tableIndex[i]) )
                          {
                              divName += tableIndex[i];
                          }
                          else
                          {
                              divName += "'" + tableIndex[i] + "'";
                          }
                      }
                  }
                  divName += ']';
                  //////console.log(divName);
                }

                //console.log('tableIndex', tableIndex, 'divName', divName);

                //////console.log('res', typeof summarizeTable(resultsTableOryginal, tableIndex));

                var elementExists = document.getElementById(divName);


                if (elementExists == null)
                {
                    ////console.log(divName);
                    var ni = document.getElementById('results');
                    var newdiv = document.createElement('div');
                    var divIdName = divName;
                    newdiv.setAttribute('id', divIdName);
                    //newdiv.innerHTML = 'div';





                    var listRes = summarizeTable(resultsTableOryginal, tableIndex);

                    data=[]
                    categories=[]
                    for(var elK1=0; elK1<listRes.length;elK1++)
                    {
                        var cat = '';
                        for(var elK2=0; elK2<listRes[elK1].length-1;elK2++)
                        {
                            cat += listRes[elK1][elK2]+ ' ';
                        }
                        categories.push(cat);
                        data.push(listRes[elK1][listRes[elK1].length-1]);
                    }
                    console.log(categories, data);

                    var chart = $('#container1').highcharts();

                    chart.series[0].setData(data);
                    chart.xAxis[0].update({categories:categories},true);


                    //console.log(listRes);

                    var multiSingleTab=1;
                    var tableDiv = divName;
                    var tableHeader = ''
                    var tableColumn = ''
                    var tableRow = ''

                    if (listRes[0].length == undefined)
                    {
                        table.innerHTML = 'No results for that combination.';
                    }
                    else if (listRes[0].length == 1)
                    {
                        tableHeader = '';
                        tableColumn = ['Value'];
                        tableRow = listRes;
                    }
                    else if (listRes[0].length == 2)
                    {
                        tableHeader = '';
                        tableColumn = ['Name', 'Value'];
                        tableRow = listRes;
                    }
                    else
                    {
                        multiSingleTab=2;
                        res = groupVal(tableDiv, listRes);
                    }

                    ////console.log('multiSingleTab', multiSingleTab, 'tableColumn', tableColumn, 'listRes[0].length', listRes[0].length);

                    if (multiSingleTab == 1)
                    {
                        var res=[tableDiv, tableHeader, tableColumn, tableRow];

                        var headerDiv = document.createElement('div');
                        headerDiv.innerHTML = tableHeader;
                        newdiv.appendChild(headerDiv);

                        var table = document.createElement('table');
                        table.setAttribute('id', divName+'-');
                        table.setAttribute('class', 'colored bordered sortable');
                        table.setAttribute('width', '100%');
                        table.setAttribute('style', "table-layout:auto; word-wrap:break-word;");
                        newdiv.appendChild(table);

                        for (var i=0; i<tableRow.length; i++)
                        {
                           if (i==0)
                           {

                            var tableBody = document.createElement('THEAD');
                            table.appendChild(tableBody);

                            var tr = document.createElement('TR');
                            tableBody.appendChild(tr);

                            for (var h=0; h<tableColumn.length; h++)
                            {
                               var td = document.createElement('TH');

                               td.setAttribute('class', 'header');
                               td.appendChild(document.createTextNode(tableColumn[h]));
                               tr.appendChild(td);
                            }

                            var tableBody = document.createElement('TBODY');
                            table.appendChild(tableBody);

                           }



                           var tr = document.createElement('TR');
                           tableBody.appendChild(tr);

                           for (var j=0; j<tableColumn.length; j++)
                           {
                               var td = document.createElement('TD');



                               td.appendChild(document.createTextNode(tableRow[i][j]));
                               tr.appendChild(td);
                           }
                        }

                        ni.appendChild(newdiv);

                        var newTableObject = document.getElementById(divName+'-');
                        sorttable.makeSortable(newTableObject);
                    }

                    else if (multiSingleTab == 2)
                    {
                        //var res=[tableDiv, tableHeader, tableColumn, tableRow];

                        for (var el=0; el< res[2].length; el++)
                        {

                            var tableDiv = row[0];
                            var tableHeader = res[3][el];
                            var tableColumn = res[2][el];
                            var tableRow = res[1][el];

                            var headerDiv = document.createElement('div');
                            headerDiv.innerHTML = tableHeader;
                            newdiv.appendChild(headerDiv);

                            var table = document.createElement('table');
                            table.setAttribute('id', divName+'-'+el);
                            table.setAttribute('class', 'colored bordered sortable');
                            table.setAttribute('width', '100%');
                            table.setAttribute('style', "table-layout:auto; word-wrap:break-word;");
                            newdiv.appendChild(table);



                            for (var i=0; i<tableRow.length; i++)
                            {

                               if (i==0)
                               {

                                var tableBody = document.createElement('THEAD');
                                table.appendChild(tableBody);

                                var tr = document.createElement('TR');
                                tableBody.appendChild(tr);

                                var td = document.createElement('TH');
                                td.setAttribute('class', 'header');
                                td.appendChild(document.createTextNode('Name'));
                                tr.appendChild(td);

                                for (var h=0; h<tableColumn.length; h++)
                                {
                                   var td = document.createElement('TH');
                                   td.setAttribute('class', 'header');
                                   td.appendChild(document.createTextNode(tableColumn[h]));
                                   tr.appendChild(td);
                                }

                                var tableBody = document.createElement('TBODY');
                                table.appendChild(tableBody);

                               }

                               var tr = document.createElement('TR');
                               tableBody.appendChild(tr);

                               for (var j=0; j<tableColumn.length+1; j++)
                               {
                                   var td = document.createElement('TD');
                                   if (tableRow[i][j] == undefined)
                                   {
                                       tableRow[i][j]='-';
                                   }
                                   td.appendChild(document.createTextNode(tableRow[i][j]));
                                   tr.appendChild(td);
                               }
                            }

                            ni.appendChild(newdiv);

                            var newTableObject = document.getElementById(divName+'-'+el);
                            sorttable.makeSortable(newTableObject);
                        }
                    }
                }


                if (divName != '')
                {
                    ////console.log('divName', divName);
                    var resultsDiv = document.getElementById(divName);
                    resultsDiv.setAttribute('class', 'visible');

                    var plotDiv = document.getElementById('container1');
                    plotDiv.setAttribute('class', 'visible');
                    var plotDiv = document.getElementById('highcharts-0');
                    plotDiv.setAttribute('class', 'visible');

                }
            }
        }

        function onClickChoicesRowColumn(dimensions, choices, choicesRowColumnIndex)
        {
            if(choicesRowColumnIndex>0)
            {
                numEl=choicesRowColumn[dimensions-1][choices].length;
                numEl=numEl-1

                if(choicesRowColumnIndex!=numEl)
                {
                    choicesRowColumnIndex = choicesRowColumnIndex - 1
                    var divName = '[' + dimensions + ', ' + choices + ', ' + choicesRowColumnIndex + ']'
                    var resultsDiv = document.getElementById(divName);
                    resultsDiv.setAttribute('class', 'visible');

                    var childDivs = document.getElementById('results').getElementsByTagName('div');
                    for( i=0; i< childDivs.length; i++ )
                    {
                        var childDiv = childDivs[i];
                        if(childDiv.id != divName)
                        {
                            var resultsDiv = document.getElementById(childDiv.id);

                            resultsDiv.setAttribute('class', 'hidden');
                        }
                    }
                }
                else
                {
                    showAllRowsColumn(dimensions, choices)
                }
            }
        }

        </script>
        """
        return js

    @staticmethod
    def groupVal(aa):

        #         outDict = {}
        #
        #         for path in listRes:
        #             current_level = outDict
        #             for part in path:
        #                 if part not in current_level:
        #                     current_level[part] = {}
        #                 current_level = current_level[part]
        #
        #         print outDict


        lenAA = len(aa[0])

        newAA = {}
        for el in aa:
            nn = str(el[1])
            if lenAA == 3:
                if not 0 in newAA:
                    newAA[0] = []
                newAA[0].append(el)
            if lenAA >= 4:
                for elN in range(4, len(el)):
                    nn += '---' + str(el[elN - 2])

                if not nn in newAA:
                    newAA[nn] = []
                newAA[nn].append(el)

        resList = []
        headerList = []
        for key, it in newAA.iteritems():
            resPartList = []
            headerPart = []
            for elN in range(0, len(it)):
                nn = ''
                for elN1 in range(0, len(it[elN]) - 2):
                    nn += str(it[elN][elN1]) + '---'
                if not nn in headerPart:
                    headerPart.append(nn)
            headerList.append(headerPart)

        resList = []
        for key, it in newAA.iteritems():
            resPartList = {}
            for h1 in headerList:
                for h2 in h1:
                    for elN in range(0, len(it)):
                        nn = ''
                        for elN1 in range(0, len(it[elN]) - 2):
                            nn += str(it[elN][elN1]) + '---'
                        if nn == h2:
                            if not it[elN][len(it[elN]) - 2] in resPartList:
                                resPartList[it[elN][len(it[elN]) - 2]] = OrderedDict()
                            if not nn in resPartList[it[elN][len(it[elN]) - 2]]:
                                resPartList[it[elN][len(it[elN]) - 2]][nn] = None
                            resPartList[it[elN][len(it[elN]) - 2]][nn] = it[elN][len(it[elN]) - 1]
            resList.append(resPartList)

        finalList = []
        for elNum2 in range(0, len(resList)):
            finalListPart = []
            for k in resList[elNum2].keys():
                finalListPart2 = [k]
                for elNum1 in range(0, len(headerList[elNum2])):  # 3 elementy
                    try:
                        finalListPart2.append(resList[elNum2][k][headerList[elNum2][elNum1]])
                    except:
                        finalListPart2.append(None)
                finalListPart.append(finalListPart2)
            finalList.append(finalListPart)

        headerCol = []
        headerTable = []
        for hl in headerList:
            headerTablePart = []

            if len(hl) >= 2:
                for h in hl:
                    headerTablePart += h.split('---')

                noDuplicate = list(set(headerTablePart))
                for el1 in range(0, int(len(headerTablePart) / 2)):
                    for el2 in range(int(len(headerTablePart) / 2), len(headerTablePart)):
                        if headerTablePart[el1] == headerTablePart[el2]:
                            headerTablePart[el2] = ''
                            headerTablePart[el1] = ''

                htp = []
                for el in headerTablePart:
                    if el != '':
                        htp.append(el)

                header = list(set(noDuplicate) - set(htp))

            else:
                h = hl[0].split('---')
                header = h[0:len(h) - 2]
                htp = [h[len(h) - 2]]

            headerTable.append((' ').join(header))
            headerCol.append(htp)

        return finalList, headerCol, headerTable

    @staticmethod
    def designTable(tableNum, listRes):

        tableDiv = tableNum
        tableHeader = ''
        tableColumn = ''
        tableRow = ''

        multiSingleTab = 1

        if len(listRes[0]) == 1:
            tableHeader = ''
            tableColumn = ['Value']
            tableRow = listRes
        elif len(listRes[0]) == 2:
            tableHeader = ''
            tableColumn = ['Name', 'Value']
            tableRow = listRes
        else:
            multiSingleTab = 2
            # tableColumn = ['Name' for x in range(0, len(listRes[0])-1)] + ['Value']
            # tableRow = listRes


            tableRow, tableColumn, tableHeader = analyseDeepGsuiteV2.groupVal(listRes)

        res = [tableDiv, tableHeader, tableColumn, tableRow]

        return res, multiSingleTab

    @staticmethod
    def createResTable(op, listRes):

        core = HtmlCore()

        tableNum = []
        for opNum in range(0, len(op)):
            # tableNum.append(opNum+1)
            tableNum.append(op[opNum])

        core.divBegin(tableNum, 'hidden')

        if len(listRes) != 0:
            res, multiSingleTab = analyseDeepGsuiteV2.designTable(tableNum, listRes)

            if multiSingleTab == 1:
                core.header(res[1])
                core.tableHeader(res[2], sortable=True, tableId=res[0])
                for r in res[3]:
                    core.tableLine(r)
                core.tableFooter()
            else:

                for nrN in range(0, len(res[3])):
                    core.header(res[1][nrN])
                    core.tableHeader(['Name'] + res[2][nrN], sortable=True, tableId=res[0])
                    for r in res[3][nrN]:
                        core.tableLine(r)
                    core.tableFooter()

        else:
            core.line('There is no results for that combination.')

        core.divEnd()

        return core

    @staticmethod
    def addStyle():
        return """
            <style type="text/css">
            .hidden {
                 display: none;
            {
            .visible {
                 display: block;
            }
            </style>
            """

    @classmethod
    def createTable(cls, listResult, listOfColumns):

        core = HtmlCore()
        core.begin()

        #         core.header("")
        #         core.divBegin('resultsDiv')
        #         core.tableHeader(['val'], sortable=True, tableId='resultsTable')
        #         for line in [[20, 10], [40, 70]]:
        #             core.tableLine(line)
        #         core.tableFooter()
        #         core.divEnd()



        core.line(analyseDeepGsuiteV2.addStyle())

        core.divBegin('results')

        vg = visualizationGraphs()
        plot = vg.drawColumnChart(
            [1],
            categories=['long first column label for plot'],
            showInLegend=False,
            height=300
        )
        core.line(plot)

        core.line(analyseDeepGsuiteV2.addLevelOptionList(listOfColumns, listResult))

        #         listResultBack = analyseDeepGsuiteV2.summarizeTable(listResult)
        #         core.paragraph(str(analyseDeepGsuiteV2.createResTable(op, listResultBack)))

        core.divEnd()

        core.end()

        return core

    @classmethod
    def createOperations(cls, listResult):

        operations = []

        finalDimensionsNum = len(listResult[0]) - 1
        # build list of possibilities for every column

        listOfColumns = []
        for elfd in range(0, finalDimensionsNum):
            listOfColumnsPart = []
            for fd in range(0, len(listResult)):
                if not listResult[fd][elfd] in listOfColumnsPart:
                    listOfColumnsPart.append(listResult[fd][elfd])
            listOfColumns.append(listOfColumnsPart)

        possibilities = [-2, -1]  # sum, select for each

        possibilitiesWithLen = []

        for p in possibilities:
            for fd in range(0, finalDimensionsNum):
                possibilitiesWithLen.append(p)

        for opN1 in range(0, len(listOfColumns)):
            for opN2 in range(0, len(listOfColumns[opN1])):
                possibilitiesWithLen.append(listOfColumns[opN1][opN2])

        for pp in [x for x in itertools.permutations(possibilitiesWithLen, finalDimensionsNum)]:
            operationsPart = []
            for p in pp:
                operationsPart.append(p)

            checkTF = False
            if not operationsPart in operations:
                for oN in range(0, len(operationsPart)):
                    if operationsPart[oN] != -1 and operationsPart[oN] != -2 and operationsPart[oN] not in \
                            listOfColumns[oN]:
                        checkTF = True
            if checkTF == False:
                operations.append(operationsPart)

        operations.sort()
        operations = list(operations for operations, _ in itertools.groupby(operations))

        return operations, listOfColumns

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):

        firstGSuite = choices.firstGSuite
        secondGSuite = choices.secondGSuite

        # for now support only with the same genome
        # later check if Ordered Dict or if string



        attributeListG1, attributeValuesListG1 = analyseDeepGsuiteV2.returnGSuiteLevelDepth(firstGSuite)
        attributeListG2, attributeValuesListG2 = analyseDeepGsuiteV2.returnGSuiteLevelDepth(secondGSuite)

        # counting for column start from zero, zero is reserved for title
        columnsForStat = [attributeListG1.index(choices.firstGSuiteColumn),
                          attributeListG2.index(choices.secondGSuiteColumn)]

        #         print columnsForStat

        #         listResult = analyseDeepGsuiteV2.makeAnalysis(attributeValuesListG1, attributeValuesListG2, columnsForStat, galaxyFn, choices)





        if choices.test == '2 level output':
            listResult = [
                ['A1', 'C2', 10],
                ['A1', 'D2', None],
                ['A1', 'E2', 30],
                ['B1', 'C2', 40],
                ['B1', 'E2', 50],
            ]
        if choices.test == '3 level output':
            listResult = [
                ['A1', 'C2', 'H3', 10],
                ['A1', 'C2', 'G3', 20],
                ['A1', 'D2', 'H3', 30],
                ['B1', 'C2', 'H3', 40],
                ['B1', 'E2', 'G3', 50],
            ]
        if choices.test == '4 level output':
            listResult = [
                ['A1', 'C2', 'H3', 'F4', 10],
                ['A1', 'C2', 'H3', 'K4', 20],
                ['A1', 'C2', 'G3', 'L4', 30],
                ['A1', 'D2', 'H3', 'F4', 40],
                ['B1', 'C2', 'H3', 'K4', 50],
                ['B1', 'E2', 'G3', 'L4', 60],
            ]
        if choices.test == '5 level output':
            listResult = [
                ['A1', 'C2', 'H3', 'F4', 'O5', 10],
                ['A1', 'C2', 'H3', 'F4', 'P5', 20],
                ['A1', 'C2', 'H3', 'K4', 'O5', 30],
                ['A1', 'C2', 'H3', 'K4', 'O5', 40],
                ['A1', 'C2', 'G3', 'L4', 'R5', 50],
                ['A1', 'D2', 'H3', 'F4', 'T5', 60],
                ['B1', 'C2', 'H3', 'K4', 'O5', 70],
                ['B1', 'C2', 'H3', 'K4', 'P5', 80],
                ['B1', 'E2', 'G3', 'L4', 'O5', 90],
            ]

        finalDimensionsNum = len(listResult[0]) - 1
        # build list of possibilities for every column



        # print 'Original values: ' + str(listResult) + '<br \>'

        # operations, listOfColumns = analyseDeepGsuiteV2.createOperations(listResult)

        listOfColumns = []
        for elfd in range(0, finalDimensionsNum):
            listOfColumnsPart = []
            for fd in range(0, len(listResult)):
                if not listResult[fd][elfd] in listOfColumnsPart:
                    listOfColumnsPart.append(listResult[fd][elfd])
            listOfColumns.append(listOfColumnsPart)

        print analyseDeepGsuiteV2.createTable(listResult, listOfColumns)

    @classmethod
    def getToolDescription(cls):
        return ''

    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'customhtml'


class analyseDeepGsuite(GeneralGuiTool, UserBinMixin):
    GSUITE_FILE_OPTIONS_BOX_KEYS = ['firstGSuite', 'secondGSuite']

    MERGE_INTRA_OVERLAPS = 'Merge any overlapping points/segments within the same track'
    ALLOW_MULTIPLE_OVERLAP = 'Allow multiple overlapping points/segments within the same track'

    @classmethod
    def summarizeTable(cls, flat, operations):
        for i, op in reversed(list(enumerate(operations))):
            if op >= 0:
                flat = [x[:i] + x[i + 1:] for x in flat if x[i] == op]
            elif op == -1:
                flat = [x[:i] + x[i + 1:] for x in flat]
                d = defaultdict(int)
                for x in flat:
                    if x[-1] != None:
                        d[tuple(x[:-1])] += x[-1]
                flat = [list(x) + [d[x]] for x in d]
        return flat

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Analyse between two gSuites with any level"

    @classmethod
    def getInputBoxNames(cls):
        return [
                   ('Select first GSuite', 'firstGSuite'),
                   #                 ('Test', 'test'),
                   ('Select column', 'firstGSuiteColumn'),
                   ('Select second GSuite', 'secondGSuite'),
                   ('Select column', 'secondGSuiteColumn'),
                   ('Check genome or select column with multi genome', 'genome'),
                   ('Select statistic type', 'type'),
                   ('Select statistic', 'statistic'),
                   ('Select overlap handling', 'intraOverlap')
               ] + cls.getInputBoxNamesForUserBinSelection()

    @staticmethod
    def getOptionsBoxFirstGSuite():
        return GeneralGuiTool.getHistorySelectionElement('gsuite', 'txt', 'tabular')

    #     @staticmethod
    #     def getOptionsBoxTest(prevChoices):
    #         return ['2 level output', '3 level output', '4 level output', '5 level output']
    #
    @staticmethod
    def getOptionsBoxFirstGSuiteColumn(prevChoices):
        if prevChoices.firstGSuite:
            first = getGSuiteFromGalaxyTN(prevChoices.firstGSuite)
            attributeList = [None] + first.attributes
            return attributeList
        else:
            return

    @staticmethod
    def getOptionsBoxSecondGSuite(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement('gsuite', 'txt', 'tabular')

    @staticmethod
    def getOptionsBoxSecondGSuiteColumn(prevChoices):
        if prevChoices.secondGSuite:
            second = getGSuiteFromGalaxyTN(prevChoices.secondGSuite)
            attributeList = [None] + second.attributes
            return attributeList
        else:
            return

    @staticmethod
    def getOptionsBoxGenome(prevChoices):
        if not prevChoices.firstGSuite:
            return
        if not prevChoices.secondGSuite:
            return

        # it will be good to have box with selected genome instead of text

        if prevChoices.firstGSuite and prevChoices.secondGSuite:
            first = getGSuiteFromGalaxyTN(prevChoices.firstGSuite)
            second = getGSuiteFromGalaxyTN(prevChoices.secondGSuite)
            if first.genome or second.genome:
                return first.genome
            else:
                attributeList1 = first.attributes
                attributeList2 = second.attributes
                retDict = OrderedDict()

                for et in attributeList1:
                    retDict[et + ' (first GSuite)'] = False

                for et in attributeList2:
                    retDict[et + ' (second GSuite)'] = False

                return retDict
        else:
            return
            # genome = 'multi' #then should be taken from one column

    @staticmethod
    def getOptionsBoxType(prevChoices):
        return ['basic', 'advanced']

    @staticmethod
    def getOptionsBoxStatistic(prevChoices):
        if prevChoices.type == 'basic':
            return [STAT_OVERLAP_COUNT_BPS,
                    STAT_OVERLAP_RATIO,
                    STAT_FACTOR_OBSERVED_VS_EXPECTED,
                    STAT_COVERAGE_RATIO_VS_QUERY_TRACK,
                    STAT_COVERAGE_RATIO_VS_REF_TRACK
                    ]
        else:
            return ['Number of touched segments']

    @staticmethod
    def getOptionsBoxIntraOverlap(prevChoices):
        return [analyseDeepGsuite.MERGE_INTRA_OVERLAPS,
                analyseDeepGsuite.ALLOW_MULTIPLE_OVERLAP]

    @classmethod
    def returnGSuiteLevelDepth(cls, gSuite):
        gSuite = getGSuiteFromGalaxyTN(gSuite)
        attributeList = gSuite.attributes

        attributeList = [TITLE_COL] + attributeList
        attributeValuesList = getAllTracksWithAttributes(gSuite)

        return attributeList, attributeValuesList

    @classmethod
    def makeAnalysis(cls, gSuite1, gSuite2, columnsForStat, galaxyFn, choices):

        genomeType = 'single'

        # if True then none of column in both gsuite are equal then for example, for gSUite 2 dim and 3 dim we have 5 dim
        # in the other case (when some columns are equal we have 4 dim)
        checkWhichDimension = False
        for el in columnsForStat:
            if el == None:
                checkWhichDimension = True
                break

        if choices.type == 'basic':
            stat = choices.statistic
            statIndex = STAT_LIST_INDEX[stat]
        else:
            stat = '0'
            statIndex = 0

        if choices.intraOverlap == analyseDeepGsuite.MERGE_INTRA_OVERLAPS:
            analysisDef = 'dummy -> RawOverlapStat'
        else:
            analysisDef = 'dummy [withOverlaps=yes] -> RawOverlapAllowSingleTrackOverlapsStat'

        regSpec, binSpec = UserBinMixin.getRegsAndBinsSpec(choices)

        listResults = []
        for el1 in gSuite1:
            for el2 in gSuite2:
                if genomeType == 'single':

                    listPartResults = []
                    if el1[columnsForStat[0]] == el2[columnsForStat[1]]:
                        gSuite1Path = el1[0]  # path for track1
                        gSuite2Path = el2[0]  # path for track2

                        #                         gSuite1Path = ['external', 'dev2', '066', '66851', '21 - Dianas tool (ung-CT)']
                        #                         gSuite2Path = ['external', 'dev2', '066', '66849', '19 - Dianas tool (ung-CA)']
                        #                         print gSuite1Path
                        #                         print gSuite2Path
                        #
                        #                         print choices.genome
                        #
                        result = GalaxyInterface.runManual([gSuite1Path, gSuite2Path],
                                                           analysisDef, regSpec, binSpec, choices.genome, galaxyFn,
                                                           printRunDescription=False,
                                                           printResults=False)

                        resVal = processResult(result.getGlobalResult())[statIndex]
                    else:
                        resVal = None

                    if checkWhichDimension == False:
                        listPartResults = el1[1:] + el2[1:] + [resVal]
                    else:
                        shorterEl2 = []
                        for eN in range(0, len(el2[1:])):
                            if el2[1:][eN] != columnsForStat[1] - 1:
                                shorterEl2.append(el2[1:][eN])
                        listPartResults = el1[1:] + shorterEl2 + [resVal]

                    listResults.append(listPartResults)

                if genomeType == 'multi':
                    # count only values with the same genome
                    pass

        return listResults

    @staticmethod
    def fillFirstSelect(firstSelectTitle, idNum, listOfColumns):
        js = firstSelectTitle + '''

        <script>
        var listOfColumns = ''' + str(listOfColumns) + ''';
        </script>

        <select name="dimensions''' + str(idNum) + '''" id="dimensions''' + str(
            idNum) + '''" size="1" onClick="onClickChoices(listOfColumns)" onChange="updateChoices''' + str(idNum) + '''(this.selectedIndex)" style="width: 150px">
        <option value="0">---Select---</option>
        <option value="1">Select one value</option>
        <option value="-2">Show results for each value</option>
        <option value="-1">Sum across this dimension</option>
        </select>
        '''
        return js

    @staticmethod
    def fillSecondSelect(secondSelectTitle, idNum):
        js = '''
        <select name="choices''' + str(idNum) + '''" id="choices''' + str(idNum) + '''" size="1" style="width: 100px"  onClick="onClickChoices(listOfColumns)">
        </select>'''
        return js

    @staticmethod
    def addSecondSelectInfo(idNum):
        js = '''document.getElementById("choices''' + str(idNum) + '''").style.visibility = "hidden";
        var dimensionslist''' + str(idNum) + '''=document.classic.dimensions''' + str(idNum) + ''';
        var choiceslist''' + str(idNum) + '''=document.classic.choices''' + str(idNum) + ''';

        '''
        return js

    @staticmethod
    def fillSecondSelectOption(idNum, data):
        js = '''
        var choices''' + str(idNum) + '''=new Array()
        choices''' + str(idNum) + '''[1]=''' + data
        return js

    @staticmethod
    def updateChoices(idNum):
        js = '''
        function updateChoices''' + str(idNum) + '''(selectedChoicesGroup)
        {
            hideTable()
            document.getElementById("choices''' + str(idNum) + '''").style.visibility = "hidden";
            if(selectedChoicesGroup  == 1)
            {
                document.getElementById("choices''' + str(idNum) + '''").style.visibility = "visible";

                choiceslist''' + str(idNum) + '''.options.length=0
                if (selectedChoicesGroup>0)
                {
                    for (i=0; i<choices''' + str(idNum) + '''[selectedChoicesGroup].length; i++)
                    {
                        choiceslist''' + str(idNum) + '''.options[choiceslist''' + str(
            idNum) + '''.options.length]=new Option(choices''' + str(
            idNum) + '''[selectedChoicesGroup][i].split("|")[0], choices''' + str(idNum) + '''[selectedChoicesGroup][i].split("|")[1])
                    }
                }
                var dimensions''' + str(idNum) + ''' = document.getElementById("dimensions''' + str(idNum) + '''");
                dimensions''' + str(idNum) + '''.options[selectedChoicesGroup].setAttribute("selected", "selected");
            }
        }
        '''
        return js

    @staticmethod
    def addLevelOptionList(listOfColumns):

        js = """
        <form name="classic">
        """
        for locNum in range(0, len(listOfColumns)):
            js += analyseDeepGsuite.fillFirstSelect("How to treat " + str(locNum), locNum, listOfColumns)
            js += analyseDeepGsuite.fillSecondSelect("Selected value", locNum)
            js += "<br \><br \>"

        js += """
        </form>

        <script type="text/javascript">
        """

        for locNum in range(0, len(listOfColumns)):
            js += analyseDeepGsuite.addSecondSelectInfo(locNum)

            js += """ folderValue""" + str(locNum) + """ =""" + str(listOfColumns[locNum]) + ";"
            js += """
                    var fol""" + str(locNum) + """ = new Array(folderValue""" + str(locNum) + """.length)
                    fol""" + str(locNum) + """[0] = "Select value|0"
                    for(i=0;i<folderValue""" + str(locNum) + """.length;i++)
                    {
                        j=i+1
                        fol""" + str(locNum) + """[j] = folderValue""" + str(locNum) + """[i] +'|' + j
                    }
                    j=j+1
            """

        js += """

        var chocieslistRowColumn=document.classic.choicesRowColumn
        """

        for locNum in range(0, len(listOfColumns)):
            js += analyseDeepGsuite.fillSecondSelectOption(locNum, """fol""" + str(locNum))
            js += analyseDeepGsuite.updateChoices(locNum)

        js += """
        function updateChoicesRowColumn(selectedChoicesGroupRowColumn, selDim)
        {
            hideTable()

            var ch = document.getElementById("choices1");
            var selCh = ch.selectedIndex
            selDim=selDim-1

            if(selCh != 0 && selCh != 3)
            {
                document.getElementById("choicesRowColumn").style.visibility = "visible";

                chocieslistRowColumn.options.length=0
                if (selectedChoicesGroupRowColumn>0)
                {
                    for (j=0; j<choicesRowColumn.length; j++)
                    {
                        if(j == selDim)
                        {
                            for (i=0; i<choicesRowColumn[selDim][selectedChoicesGroupRowColumn].length; i++)
                            {
                                chocieslistRowColumn.options[chocieslistRowColumn.options.length]=new Option(choicesRowColumn[j][selectedChoicesGroupRowColumn][i].split("|")[0], choicesRowColumn[j][selectedChoicesGroupRowColumn][i].split("|")[1])
                            }
                        }
                    }
                }
            }
            else
            {
                document.getElementById("choicesRowColumn").style.visibility = "hidden";
                if(selCh == 3)
                {
                    showAllTables(selDim)
                }
            }
        }

        function hideTable()
        {
            var childDivs = document.getElementById('results').getElementsByTagName('div');
            for( i=0; i< childDivs.length; i++ )
            {
                var childDiv = childDivs[i];
                var resultsDiv = document.getElementById(childDiv.id);
                resultsDiv.setAttribute('class', 'hidden');
            }
        }
        function showAllTables(selDim)
        {
            selDim = selDim +1
            var childDivs = document.getElementById('results').getElementsByTagName('div');
            for( i=0; i< childDivs.length; i++ )
            {
                var childDiv = childDivs[i];
                temp = childDiv.id
                temp = temp.replace("[", "");
                temp = temp.replace("]", "");
                var tab = new Array();
                tab = temp.split(",");

                if(tab[0] == selDim)
                {
                    var resultsDiv = document.getElementById(childDiv.id);
                    resultsDiv.setAttribute('class', 'visible');
                }
            }
        }
        function showAllRowsColumn(selDim, selCh)
        {
            var childDivs = document.getElementById('results').getElementsByTagName('div');
            for( i=0; i< childDivs.length; i++ )
            {
                var childDiv = childDivs[i];
                temp = childDiv.id
                temp = temp.replace("[", "");
                temp = temp.replace("]", "");
                var tab = new Array();
                tab = temp.split(",");


                if(tab[0] == selDim && tab[1] == selCh)
                {
                    var resultsDiv = document.getElementById(childDiv.id);
                    resultsDiv.setAttribute('class', 'visible');
                }
            }
        }
        function onClickChoices(listOfColumns)
        {
            hideTable();


            //which index, method


            //index
            //-1 - nothing selected
            // 0 - nothing selected
            //index start from 1

            //method
            // 0 - non selected
            // 1 - select one value
            //-1 - show each value
            //-2 - show sum across dimension


            tabEl = parseInt(listOfColumns.length);


            tableIndex=[]
            for (var i =0 ; i< tabEl; i++)
            {
                var c = "choices" + i;
                if (document.getElementById(c) != null)
                {
                    var ch0 = document.getElementById(c);
                    var selCh0 = ch0.value;

                    var dim0 = document.getElementById("dimensions"+i);
                    var selDim0 = dim0.value;

                    //tableIndex.push('choicesIndex'+selCh0);
                    //tableIndex.push('dimensions'+selDim0);

                    if (selDim0!=0)
                    {
                        if (selDim0 != -2 && selDim0 != -1)
                        {
                            if (selCh0 !=0)
                            {
                                tableIndex.push(listOfColumns[i][selCh0-1]);
                                ////console.log('a');
                            }
                            else
                            {
                                ////console.log('b');
                                //tableIndex.push(selCh0);
                            }
                        }
                        else
                        {
                            ////console.log('c');
                            //tableIndex.push(selCh0);
                            tableIndex.push(parseInt(selDim0));
                        }
                    }
                }
            }

            ////console.log(tableIndex);

            var divName = '';

            if ( tabEl == parseInt(tableIndex.length) )
            {
              divName += '[';
              for (var i =0 ; i< tabEl; i++)
              {
                  if (i < tabEl-1)
                  {
                      if ( Number.isInteger(tableIndex[i]) )
                      {
                          divName += tableIndex[i] + ', ';
                      }
                      else
                      {
                          divName += "'" + tableIndex[i] + "'" + ", ";
                      }
                  }
                  else
                  {
                      if ( Number.isInteger(tableIndex[i]) )
                      {
                          divName += tableIndex[i];
                      }
                      else
                      {
                          divName += "'" + tableIndex[i] + "'";
                      }
                  }
              }
              divName += ']';
              ////console.log(divName);
            }

            if (divName != '')
            {
                var resultsDiv = document.getElementById(divName);
                resultsDiv.setAttribute('class', 'visible');
            }

        }

        function onClickChoicesRowColumn(dimensions, choices, choicesRowColumnIndex)
        {
            if(choicesRowColumnIndex>0)
            {
                numEl=choicesRowColumn[dimensions-1][choices].length;
                numEl=numEl-1

                if(choicesRowColumnIndex!=numEl)
                {
                    choicesRowColumnIndex = choicesRowColumnIndex - 1
                    var divName = '[' + dimensions + ', ' + choices + ', ' + choicesRowColumnIndex + ']'
                    var resultsDiv = document.getElementById(divName);
                    resultsDiv.setAttribute('class', 'visible');

                    var childDivs = document.getElementById('results').getElementsByTagName('div');
                    for( i=0; i< childDivs.length; i++ )
                    {
                        var childDiv = childDivs[i];
                        if(childDiv.id != divName)
                        {
                            var resultsDiv = document.getElementById(childDiv.id);
                            resultsDiv.setAttribute('class', 'hidden');
                        }
                    }
                }
                else
                {
                    showAllRowsColumn(dimensions, choices)
                }
            }
        }

        </script>
        """
        return js

    @staticmethod
    def groupVal(aa):

        #         outDict = {}
        #
        #         for path in listRes:
        #             current_level = outDict
        #             for part in path:
        #                 if part not in current_level:
        #                     current_level[part] = {}
        #                 current_level = current_level[part]
        #
        #         print outDict


        lenAA = len(aa[0])

        newAA = {}
        for el in aa:
            nn = str(el[1])
            if lenAA == 3:
                if not 0 in newAA:
                    newAA[0] = []
                newAA[0].append(el)
            if lenAA >= 4:
                for elN in range(4, len(el)):
                    nn += '---' + str(el[elN - 2])

                if not nn in newAA:
                    newAA[nn] = []
                newAA[nn].append(el)

        resList = []
        headerList = []
        for key, it in newAA.iteritems():
            resPartList = []
            headerPart = []
            for elN in range(0, len(it)):
                nn = ''
                for elN1 in range(0, len(it[elN]) - 2):
                    nn += str(it[elN][elN1]) + '---'
                if not nn in headerPart:
                    headerPart.append(nn)
            headerList.append(headerPart)

        resList = []
        for key, it in newAA.iteritems():
            resPartList = {}
            for h1 in headerList:
                for h2 in h1:
                    for elN in range(0, len(it)):
                        nn = ''
                        for elN1 in range(0, len(it[elN]) - 2):
                            nn += str(it[elN][elN1]) + '---'
                        if nn == h2:
                            if not it[elN][len(it[elN]) - 2] in resPartList:
                                resPartList[it[elN][len(it[elN]) - 2]] = OrderedDict()
                            if not nn in resPartList[it[elN][len(it[elN]) - 2]]:
                                resPartList[it[elN][len(it[elN]) - 2]][nn] = None
                            resPartList[it[elN][len(it[elN]) - 2]][nn] = it[elN][len(it[elN]) - 1]
            resList.append(resPartList)

        finalList = []
        for elNum2 in range(0, len(resList)):
            finalListPart = []
            for k in resList[elNum2].keys():
                finalListPart2 = [k]
                for elNum1 in range(0, len(headerList[elNum2])):  # 3 elementy
                    try:
                        finalListPart2.append(resList[elNum2][k][headerList[elNum2][elNum1]])
                    except:
                        finalListPart2.append(None)
                finalListPart.append(finalListPart2)
            finalList.append(finalListPart)

        headerCol = []
        headerTable = []
        for hl in headerList:
            headerTablePart = []

            if len(hl) >= 2:
                for h in hl:
                    headerTablePart += h.split('---')

                noDuplicate = list(set(headerTablePart))
                for el1 in range(0, int(len(headerTablePart) / 2)):
                    for el2 in range(int(len(headerTablePart) / 2), len(headerTablePart)):
                        if headerTablePart[el1] == headerTablePart[el2]:
                            headerTablePart[el2] = ''
                            headerTablePart[el1] = ''

                htp = []
                for el in headerTablePart:
                    if el != '':
                        htp.append(el)

                header = list(set(noDuplicate) - set(htp))

            else:
                h = hl[0].split('---')
                header = h[0:len(h) - 2]
                htp = [h[len(h) - 2]]

            headerTable.append((' ').join(header))
            headerCol.append(htp)

        return finalList, headerCol, headerTable

    @staticmethod
    def designTable(tableNum, listRes):

        tableDiv = tableNum
        tableHeader = ''
        tableColumn = ''
        tableRow = ''

        multiSingleTab = 1

        if len(listRes[0]) == 1:
            tableHeader = ''
            tableColumn = ['Value']
            tableRow = listRes
        elif len(listRes[0]) == 2:
            tableHeader = ''
            tableColumn = ['Name', 'Value']
            tableRow = listRes
        else:
            multiSingleTab = 2
            # tableColumn = ['Name' for x in range(0, len(listRes[0])-1)] + ['Value']
            # tableRow = listRes


            tableRow, tableColumn, tableHeader = analyseDeepGsuite.groupVal(listRes)

        res = [tableDiv, tableHeader, tableColumn, tableRow]

        return res, multiSingleTab

    @staticmethod
    def createResTable(op, listRes):

        core = HtmlCore()

        tableNum = []
        for opNum in range(0, len(op)):
            # tableNum.append(opNum+1)
            tableNum.append(op[opNum])

        core.divBegin(tableNum, 'hidden')

        if len(listRes) != 0:
            res, multiSingleTab = analyseDeepGsuite.designTable(tableNum, listRes)

            if multiSingleTab == 1:
                core.header(res[1])
                core.tableHeader(res[2], sortable=True, tableId=res[0])
                for r in res[3]:
                    core.tableLine(r)
                core.tableFooter()
            else:

                for nrN in range(0, len(res[3])):
                    core.header(res[1][nrN])
                    core.tableHeader(['Name'] + res[2][nrN], sortable=True, tableId=res[0])
                    for r in res[3][nrN]:
                        core.tableLine(r)
                    core.tableFooter()

        else:
            core.line('There is no results for that combination.')

        core.divEnd()

        return core

    @staticmethod
    def addStyle():
        return """
            <style type="text/css">
            .hidden {
                 display: none;
            {
            .visible {
                 display: block;
            }
            </style>
            """

    @classmethod
    def createTable(cls, listResult, operation, listOfColumns):

        core = HtmlCore()
        core.begin()

        core.line(analyseDeepGsuite.addStyle())
        core.line(analyseDeepGsuite.addLevelOptionList(listOfColumns))

        core.divBegin('results')

        for op in operation:
            # print 'operation: ' + str(op) + ' '
            listResultBack = analyseDeepGsuite.summarizeTable(listResult, op)
            # print 'listResult: ' + str(listResultBack)
            # print '<br \>'

            core.paragraph(str(analyseDeepGsuite.createResTable(op, listResultBack)))

        core.divEnd()

        core.end()

        return core

    @classmethod
    def createOperations(cls, listResult):

        operations = []

        finalDimensionsNum = len(listResult[0]) - 1
        # build list of possibilities for every column

        listOfColumns = []
        for elfd in range(0, finalDimensionsNum):
            listOfColumnsPart = []
            for fd in range(0, len(listResult)):
                if not listResult[fd][elfd] in listOfColumnsPart:
                    listOfColumnsPart.append(listResult[fd][elfd])
            listOfColumns.append(listOfColumnsPart)

        possibilities = [-2, -1]  # sum, select for each

        possibilitiesWithLen = []

        for p in possibilities:
            for fd in range(0, finalDimensionsNum):
                possibilitiesWithLen.append(p)

        for opN1 in range(0, len(listOfColumns)):
            for opN2 in range(0, len(listOfColumns[opN1])):
                possibilitiesWithLen.append(listOfColumns[opN1][opN2])

        for pp in [x for x in itertools.permutations(possibilitiesWithLen, finalDimensionsNum)]:
            operationsPart = []
            for p in pp:
                operationsPart.append(p)

            checkTF = False
            if not operationsPart in operations:
                for oN in range(0, len(operationsPart)):
                    if operationsPart[oN] != -1 and operationsPart[oN] != -2 and operationsPart[oN] not in \
                            listOfColumns[oN]:
                        checkTF = True
            if checkTF == False:
                operations.append(operationsPart)

        operations.sort()
        operations = list(operations for operations, _ in itertools.groupby(operations))

        return operations, listOfColumns

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):

        firstGSuite = choices.firstGSuite
        secondGSuite = choices.secondGSuite

        # for now support only with the same genome
        # later check if Ordered Dict or if string



        attributeListG1, attributeValuesListG1 = analyseDeepGsuite.returnGSuiteLevelDepth(firstGSuite)
        attributeListG2, attributeValuesListG2 = analyseDeepGsuite.returnGSuiteLevelDepth(secondGSuite)

        # counting for column start from zero, zero is reserved for title
        columnsForStat = [attributeListG1.index(choices.firstGSuiteColumn),
                          attributeListG2.index(choices.secondGSuiteColumn)]

        #         print columnsForStat

        listResult = analyseDeepGsuite.makeAnalysis(attributeValuesListG1, attributeValuesListG2, columnsForStat,
                                                    galaxyFn, choices)

        print listResult

        #
        #         if choices.test == '2 level output':
        #             listResult=[
        #                     ['A1', 'C2', 10],
        #                     ['A1', 'D2', 20],
        #                     ['A1', 'E2', 30],
        #                     ['B1', 'C2', 40],
        #                     ['B1', 'E2', 50],
        #                     ]
        #         if choices.test == '3 level output':
        #             listResult=[
        #                     ['A1', 'C2', 'H3', 10],
        #                     ['A1', 'C2', 'G3', 20],
        #                     ['A1', 'D2', 'H3', 30],
        #                     ['B1', 'C2', 'H3', 40],
        #                     ['B1', 'E2', 'G3', 50],
        #                     ]
        #         if choices.test == '4 level output':
        #             listResult=[
        #                     ['A1', 'C2', 'H3', 'F4', 10],
        #                     ['A1', 'C2', 'H3', 'K4', 20],
        #                     ['A1', 'C2', 'G3', 'L4', 30],
        #                     ['A1', 'D2', 'H3', 'F4', 40],
        #                     ['B1', 'C2', 'H3', 'K4', 50],
        #                     ['B1', 'E2', 'G3', 'L4', 60],
        #                     ]
        #         if choices.test == '5 level output':
        #             listResult=[
        #                     ['A1', 'C2', 'H3', 'F4', 'O5', 10],
        #                     ['A1', 'C2', 'H3', 'F4', 'P5', 20],
        #                     ['A1', 'C2', 'H3', 'K4', 'O5', 30],
        #                     ['A1', 'C2', 'H3', 'K4', 'O5', 40],
        #                     ['A1', 'C2', 'G3', 'L4', 'R5', 50],
        #                     ['A1', 'D2', 'H3', 'F4', 'T5', 60],
        #                     ['B1', 'C2', 'H3', 'K4', 'O5', 70],
        #                     ['B1', 'C2', 'H3', 'K4', 'P5', 80],
        #                     ['B1', 'E2', 'G3', 'L4', 'O5', 90],
        #                     ]


        finalDimensionsNum = len(listResult[0]) - 1
        # build list of possibilities for every column

        listOfColumns = []
        for elfd in range(0, finalDimensionsNum - 1):
            listOfColumnsPart = []
            for fd in range(0, len(listResult)):
                if not listResult[fd][elfd] in listOfColumnsPart:
                    listOfColumnsPart.append(listResult[fd][elfd])
            listOfColumns.append(listOfColumnsPart)

        # print 'Original values: ' + str(listResult) + '<br \>'

        operations, listOfColumns = analyseDeepGsuite.createOperations(listResult)

        print analyseDeepGsuite.createTable(listResult, operations, listOfColumns)

    @classmethod
    def getToolDescription(cls):
        return ''

    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'customhtml'


class geneExpressionMaxValue(GeneralGuiTool, UserBinMixin):
    GSUITE_FILE_OPTIONS_BOX_KEYS = ['gSuiteFirst']

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Gene expression heatmap with option"

    @classmethod
    def getInputBoxNames(cls):
        return [
                   ('Select target track collection GSuite', 'gSuiteFirst')
               ] + cls.getInputBoxNamesForUserBinSelection()

    @staticmethod
    def getOptionsBoxGSuiteFirst():
        return GeneralGuiTool.getHistorySelectionElement('gsuite', 'txt', 'tabular')

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):

        targetGSuite = getGSuiteFromGalaxyTN(choices.gSuiteFirst)
        regSpec, binSpec = UserBinMixin.getRegsAndBinsSpec(choices)

        analysis = AnalysisSpec(MaxElementValueStat)

        resultsList = []
        trackList = []

        globalRes = []

        i = 0

        avgTrack = []

        for x in targetGSuite.allTracks():
            analysisBins = GalaxyInterface._getUserBinSource(regSpec, binSpec, x.genome)
            results = doAnalysis(analysis, analysisBins, [PlainTrack(x.trackName)])

            tn = x.trackName
            globRes = results.getGlobalResult()
            globalRes.append([i, urllib2.unquote(tn[-1]), float(globRes['Result'])])
            trackList.append(urllib2.unquote(tn[-1]))

            resultsListPart = []
            resultsListPartToSum = []
            for el in results.getAllValuesForResDictKey('Result'):
                if el is None:
                    el = 0
                    el1 = 0
                else:
                    if el == 0 or math.isnan(el):
                        el = 0
                        el1 = 0
                    else:
                        el1 = float(el)
                        el = math.log(float(el), 10)
                resultsListPart.append(el)
                resultsListPartToSum.append(el1)

            avgTrack.append([urllib2.unquote(tn[-1]), sum(resultsListPartToSum) / float(len(resultsListPartToSum))])

            resultsList.append(resultsListPart)

            if i == 0:
                categories = []
                for el in results.getAllRegionKeys():
                    categories.append(str(el))
            i += 1

        htmlCore = HtmlCore()
        htmlCore.begin()

        htmlCore.header("")
        htmlCore.divBegin('resultsDiv')
        #         htmlCore.tableHeader(['Number', 'Track name', 'Max value'], sortable=True, tableId='resultsTable')
        htmlCore.tableHeader(['Track name', 'Avg(from max) value'], sortable=True, tableId='resultsTable')
        #         for line in globalRes:
        #             htmlCore.tableLine(line)
        for line in avgTrack:
            htmlCore.tableLine(line)
        htmlCore.tableFooter()
        htmlCore.divEnd()

        vg = visualizationGraphs()
        res = vg.drawHeatmapLargeChart(resultsList,
                                       categories=categories,
                                       categoriesY=trackList,
                                       xAxisRotation=90,
                                       xAxisTitle='',
                                       yAxisTitle='log10 scale',
                                       )

        htmlCore.line(res)
        htmlCore.end()

        print htmlCore


        # resultDict = results.getGlobalResult()

    @classmethod
    def getToolDescription(cls):
        return ''

    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'customhtml'


class rainfallBuildNewFile(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Filter columns in bed files (rainfall paper filtering)"

    @staticmethod
    def getInputBoxNames():
        return [('Select genome', 'genome'),
                ('Select tracks', 'bedFile'),
                ('Select column which should have chromosome number (from 0)', 'chrNum'),
                ('Select the rest column (,)', 'column'),
                ('Select option', 'option'),
                ('Select column for option', 'optionVal')
                ]

    @staticmethod
    def getOptionsBoxGenome():
        return '__genome__'

    @staticmethod
    def getOptionsBoxBedFile(prevChoices):
        return ('__multihistory__', 'tabular')

    @staticmethod
    def getOptionsBoxChrNum(prevChoices):
        return ''

    @staticmethod
    def getOptionsBoxColumn(prevChoices):
        return ''

    @staticmethod
    def getOptionsBoxOption(prevChoices):
        return ['single mutations in two columns', 'all mutation']

    @staticmethod
    def getOptionsBoxOptionVal(prevChoices):
        return ''

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        bedFiles = choices.bedFile
        chrNum = int(choices.chrNum)
        column = choices.column
        column = column.replace(' ', '')
        column = column.split(',')
        option = choices.option
        optionVal = choices.optionVal
        optionVal = optionVal.replace(' ', '')
        optionVal = optionVal.split(',')

        mutList = ['CA', 'CG', 'CT', 'TA', 'TC', 'TG']
        mutListReverse = ['GT', 'GC', 'GA', 'AT', 'AG', 'AC']

        mut = []
        for elN in range(0, len(mutList)):
            mut.append([mutList[elN], mutListReverse[elN]])

        for key, bedFile in bedFiles.items():
            # print bedfile

            outGSuite = GSuite()

            inputFile = open(ExternalTrackManager.extractFnFromGalaxyTN(bedFile.split(':')), 'r')
            with inputFile as f:
                data = [x.strip('\n') for x in f.readlines()]
            f.closed
            inputFile.close()

            name = bedFile.split(':')
            name = urllib2.unquote(name[-1])

            # maxelementvaluestat

            if option == 'single mutations in two columns':
                for m in mut:

                    print galaxyFn

                    trackName = str(name) + '-' + str(m[0])
                    uri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn,
                                                        extraFileName=trackName,
                                                        suffix='bed')

                    gSuiteTrack = GSuiteTrack(uri)
                    outFn = gSuiteTrack.path
                    ensurePathExists(outFn)

                    headerFirst = 'track name="' + str(name) + '" description="' + str(m[0]) + '" priority=1'
                    # outputFile =  open(cls.makeHistElement(galaxyExt='bed',title=str(name)+'-'+str(m[0]), label=str(name)+'-'+str(m[0])), 'w')
                    with open(outFn, 'w') as outputFile:
                        outputFile.write(headerFirst + '\n')
                        for d in data:
                            row = d.split('\t')
                            if option == 'single mutations in two columns':
                                if len(row[int(optionVal[0])]) == 1 and len(row[int(optionVal[1])]) == 1:
                                    stM1 = list(m[0])
                                    stM2 = list(m[1])
                                    if (row[int(optionVal[0])] == stM1[0] and row[int(optionVal[1])] == stM1[1]) or (
                                            row[int(optionVal[0])] == stM2[0] and row[int(optionVal[1])] == stM2[1]):
                                        line = ''
                                        ic = 0
                                        if len(column) == 1:
                                            aa = int(row[int(column[0])]) - 1
                                            line += str(aa) + '\t'
                                            bb = int(row[int(column[0])])
                                            line += str(bb) + '\t'

                                        else:
                                            for c in column:
                                                if ic == 0:
                                                    row[int(c)] = int(row[int(c)]) - 1
                                                line += str(row[int(c)]) + '\t'
                                                ic += 1

                                        outputFile.write('chr' + str(row[chrNum]) + '\t' + line + '\n')

                        outputFile.close()

                    outGSuite.addTrack(GSuiteTrack(uri, title=''.join(trackName), genome=choices.genome))

                GSuiteComposer.composeToFile(outGSuite, cls.extraGalaxyFn['Gsuite paper'])
            else:
                print galaxyFn

                trackName = str(name) + '-' + str('all')
                uri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn,
                                                    extraFileName=trackName,
                                                    suffix='bed')

                gSuiteTrack = GSuiteTrack(uri)
                outFn = gSuiteTrack.path
                ensurePathExists(outFn)

                headerFirst = 'track name="' + str(name) + '" description="' + str('all') + '" priority=1'
                # outputFile =  open(cls.makeHistElement(galaxyExt='bed',title=str(name)+'-'+str(m[0]), label=str(name)+'-'+str(m[0])), 'w')
                with open(outFn, 'w') as outputFile:
                    outputFile.write(headerFirst + '\n')
                    for d in data:
                        row = d.split('\t')

                        try:
                            line = ''
                            ic = 0
                            if len(column) == 1:
                                aa = int(row[int(column[0])]) - 1
                                line += str(aa) + '\t'
                                bb = int(row[int(column[0])])
                                line += str(bb) + '\t'

                            else:
                                for c in column:
                                    if ic == 0:
                                        row[int(c)] = int(row[int(c)]) - 1
                                    line += str(row[int(c)]) + '\t'
                                    ic += 1

                            outputFile.write('chr' + str(row[chrNum]) + '\t' + line + '\n')
                        except:
                            pass

                    outputFile.close()

                outGSuite.addTrack(GSuiteTrack(uri, title=''.join(trackName), genome=choices.genome))

            GSuiteComposer.composeToFile(outGSuite, cls.extraGalaxyFn['Gsuite paper'])

        print 'GSuiteComposer - done'

    @staticmethod
    def validateAndReturnErrors(choices):
        return None

    @classmethod
    def getExtraHistElements(cls, choices):
        return [HistElement('Gsuite paper', 'gsuite')]


class kmerGSuite(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "k-mer build 3-level gsuite"

    @staticmethod
    def getInputBoxNames():
        return [('Select genome', 'genome'),
                ('Select GSuite', 'gSuite'),
                ]

    @staticmethod
    def getOptionsBoxGenome():
        return '__genome__'

    @staticmethod
    def getOptionsBoxGSuite(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        with open(ExternalTrackManager.extractFnFromGalaxyTN(choices.gSuite.split(':')), 'r') as f:
            data = [x.strip('\n') for x in f.readlines()]
        f.closed

        genome = choices.genome

        header = '##location: local\n##file format: primary\n##track type: unknown\n###uri\ttitle\tdir_level_2\tdir_level_3\tdir_level_4\n####genome=mm9\n'

        output = ''
        for d in range(0, len(data)):
            if d < 4:
                pass
            elif d == 4:
                output += header
            else:
                newData = data[d].split("\t")

                kmer = list(newData[1])
                j = 0
                for elKmer in kmer:
                    if j == 1:
                        newData.append(str(genome) + '-' + str(elKmer.upper()))
                    else:
                        newData.append(elKmer.upper())
                    j += 1

                output += '\t'.join(newData)

                output += '\n'

        open(galaxyFn, 'w').write(output)

        print 'GSuite - done'

    @staticmethod
    def validateAndReturnErrors(choices):
        return None

    @staticmethod
    def getOutputFormat(choices):
        return 'gsuite'


class geneExpressionCutOff(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Gene expression - select cutoff value for gSuite"

    @staticmethod
    def getInputBoxNames():
        return [
            ('Select genome', 'genome'),
            ('Select GSuite', 'gSuite'),
            ('Select cutoff value', 'cutoff')
        ]

    @staticmethod
    def getOptionsBoxGenome():
        return '__genome__'

    @staticmethod
    def getOptionsBoxGSuite(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @staticmethod
    def getOptionsBoxCutoff(prevChoices):
        return ''

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        gSuiteName = choices.gSuite
        cutoff = choices.cutoff
        dataDict = {}

        gSuite = getGSuiteFromGalaxyTN(gSuiteName)
        # parse the tracks!
        for track in gSuite.allTrackTitles():
            gSuiteTrack = gSuite.getTrackFromTitle(track)
            trackName = track

            if not trackName in dataDict:
                dataDict[trackName] = []  # dictOfTissue
            with open(gSuiteTrack.path, 'r') as f:
                for x in f.readlines():
                    el = x.strip('\n').split('\t')

                    geneNameCuttOffVal = el[3].split('---')
                    geneName = geneNameCuttOffVal[0]
                    cuttOffVale = geneNameCuttOffVal[1]

                    if float(cuttOffVale) >= float(cutoff):
                        x = x.replace('---', '\t')
                        el2 = x.strip('\n').split('\t')

                        x = str(el2[0]) + '\t' + str(int(el2[1])) + '\t' + str(int(el2[2])) + '\t' + str(
                            float(el2[4])) + '\t' + str(el2[3]) + '\n'
                        dataDict[trackName].append(x)

        outGSuite = GSuite()
        for trackName, it0 in dataDict.items():
            uri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn,
                                                extraFileName=trackName,
                                                suffix='gtrack')
            gSuiteTrack = GSuiteTrack(uri)
            outFn = gSuiteTrack.path
            ensurePathExists(outFn)

            header = '##Track type: valued segments\n###seqid\tstart\tend\tvalue\tgene\n####genome=hg19\n'

            print str(trackName) + '-' + str(len(it0))
            with open(outFn, 'w') as outFile:
                outFile.write(header)
                for el in it0:
                    outFile.write(str(el))

            print 'done with' + str(trackName)

            outGSuite.addTrack(GSuiteTrack(uri, title=''.join(trackName), genome=choices.genome))

        GSuiteComposer.composeToFile(outGSuite, cls.extraGalaxyFn['GE gsuite with cutoff value'])

        print 'GSuiteComposer - done'

    @staticmethod
    def validateAndReturnErrors(choices):
        return None

    @classmethod
    def getExtraHistElements(cls, choices):
        return [HistElement('GE gsuite with cutoff value', 'gsuite')]


class geneExpressionCutOffTrack(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Gene expression - select cutoff value for track"

    @staticmethod
    def getInputBoxNames():
        return [
            ('Select genome', 'genome'),
            ('Select track', 'track'),
            ('Select cutoff value', 'cutoff')
        ]

    @staticmethod
    def getOptionsBoxGenome():
        return '__genome__'

    @staticmethod
    def getOptionsBoxTrack(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement()

    @staticmethod
    def getOptionsBoxCutoff(prevChoices):
        return ''

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        trackName = choices.track
        cutoff = choices.cutoff

        wholeFile = {}

        i = 0
        with open(ExternalTrackManager.extractFnFromGalaxyTN(trackName.split(':')), 'r') as f:
            for x in f.readlines():
                if i > 0:
                    lVal = x.strip('\n').split('\t')

                    if float(lVal[5]) >= float(cutoff):
                        if not lVal[0] in wholeFile:
                            wholeFile[lVal[0]] = {}
                        if not lVal[4] in wholeFile[lVal[0]]:
                            wholeFile[lVal[0]][lVal[4]] = {}
                            wholeFile[lVal[0]][lVal[4]]['start'] = []
                            wholeFile[lVal[0]][lVal[4]]['end'] = []

                        wholeFile[lVal[0]][lVal[4]]['start'].append(int(lVal[1]))
                        wholeFile[lVal[0]][lVal[4]]['end'].append(int(lVal[2]))

                i += 1

        outputFile = open(cls.makeHistElement(galaxyExt='bed', title=str('File with cutoff ' + str(cutoff))), 'w')

        output = ''
        for key0, it0 in wholeFile.items():
            minV = 0
            maxV = 0
            for key1, it1 in it0.items():
                minV = int(min(it1['start'])) - 1
                maxV = max(it1['end'])
                output += 'chr' + str(key0) + '\t' + str(minV) + '\t' + str(maxV) + '\t' + str(key1) + '\n'

        outputFile.write(output)
        outputFile.close()

        print 'Track cut - done'

    @staticmethod
    def validateAndReturnErrors(choices):
        return None

    @staticmethod
    def getOutputFormat(choices):
        return 'bed'


class geneExpressionHist(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Gene expression histogram"

    @staticmethod
    def getInputBoxNames():
        return [
            ('Select annotatations', 'annotations'),
            ('Select tissue type', 'type'),
            ('Select RNA-Seq Data', 'rnaSeqData'),
            ('Select reference', 'reference'),
            ('Select breaks for clustering', 'breaks'),
            ('Select max value for clustering', 'maxVal')
        ]

    @staticmethod
    def getOptionsBoxAnnotations():
        return GeneralGuiTool.getHistorySelectionElement()

    @staticmethod
    def getOptionsBoxType(prevChoices):
        return ['SMTS', 'SMTSD']

    # @classmethod
    # def asDict(cls, vector):
    #     """Convert an RPy2 ListVector to a Python dict"""
    #     from rpy2 import robjects
    #     import types
    #     result = {}
    #     for i, name in enumerate(vector.names):
    #         if isinstance(vector[i], robjects.ListVector):
    #             result[name] = as_dict(vector[i])
    #         elif type(vector[i]) != types.BooleanType and len(vector[i]) == 1:
    #             result[name] = vector[i][0]
    #         else:
    #             result[name] = vector[i]
    #     return result

    @staticmethod
    def getOptionsBoxRnaSeqData(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement()

    @staticmethod
    def getOptionsBoxReference(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement()

    @staticmethod
    def getOptionsBoxBreaks(prevChoices):
        return ''

    @staticmethod
    def getOptionsBoxMaxVal(prevChoices):
        return ''

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        annotation = choices.annotations
        type = choices.type
        rnaSeqData = choices.rnaSeqData
        breaks = choices.breaks
        maxVal = choices.maxVal
        reference = choices.reference

        if type == 'SMTSD':
            nrType = 6
        if type == 'SMTS':
            nrType = 5

        annotationDict = {}

        i = 0
        with open(ExternalTrackManager.extractFnFromGalaxyTN(annotation.split(':')), 'r') as f:
            for x in f.readlines():
                if i > 0:
                    el = x.strip('\n').split('\t')
                    if not el[nrType] in annotationDict:
                        annotationDict[el[nrType]] = []
                    if not el[0] in annotationDict[el[nrType]]:
                        annotationDict[el[nrType]].append(el[0])
                i += 1
        i = 0

        print 'done annotationDict'

        i = 0
        rnaSeqDataDict = {}
        with open(ExternalTrackManager.extractFnFromGalaxyTN(rnaSeqData.split(':')), 'r') as f:
            for x in f.readlines():
                if i == 2:
                    el = x.strip('\n').split('\t')
                    header = []
                    for elN in range(2, len(el)):
                        header.append(el[elN])
                        rnaSeqDataDict[el[elN]] = {}
                if i > 2:
                    el = x.strip('\n').split('\t')
                    for elN in range(2, len(el)):
                        if el[elN] != '0':
                            if not el[0] in rnaSeqDataDict[header[elN - 2]]:
                                rnaSeqDataDict[header[elN - 2]][el[0]] = 10
                            rnaSeqDataDict[header[elN - 2]][el[0]] = float(el[elN])
                i += 1

        print 'done rnaSeqDataDict'

        # print rnaSeqDataDict


        finalResults = {}
        for key0, it0 in annotationDict.iteritems():
            if key0 not in finalResults:
                finalResults[key0] = {}
            for it00 in it0:
                if it00 in rnaSeqDataDict.keys():
                    for key1, it1 in rnaSeqDataDict[it00].iteritems():
                        if not key1 in finalResults[key0]:
                            finalResults[key0][key1] = {}
                            finalResults[key0][key1]['num'] = 0
                            finalResults[key0][key1]['div'] = 0
                        finalResults[key0][key1]['num'] += float(it1)
                        finalResults[key0][key1]['div'] += 1.0

        # print finalResults



        vg = visualizationGraphs()

        print finalResults

        outputFile = open(cls.makeHistElement(galaxyExt='tabular', title='List of tissue'), 'w')
        res = ''
        for tissue in finalResults.keys():
            if finalResults[tissue]:
                res += str(tissue) + '\n'
        outputFile.write(res)
        outputFile.close()

        print 'done finalResults'

        i = 0
        geneList = []
        with open(ExternalTrackManager.extractFnFromGalaxyTN(reference.split(':')), 'r') as f:
            for x in f.readlines():

                if i > 4:

                    el = x.strip('\n').split(' ')
                    geneID = el[1].replace('"', '').replace(';', '')
                    elNewDiv = x.strip('\n').split('\t')

                    if elNewDiv[2] == 'transcript':
                        geneList.append(geneID)

                i += 1

        print 'gene len' + str(len(geneList))

        tissueDict = {}
        for tissue, it0 in finalResults.iteritems():
            if len(it0) != 0:
                if not tissue in tissueDict:
                    tissueDict[tissue] = {}
                for gene, it1 in it0.iteritems():
                    if gene in geneList:
                        if not gene in tissueDict[tissue]:
                            tissueDict[tissue][gene] = 0
                        tissueDict[tissue][gene] = float(it1['num'] / it1['div'])

                tissueDict[tissue] = OrderedDict(sorted(tissueDict[tissue].items(), key=lambda t: t[1], reverse=True))

                outputFile = open(cls.makeHistElement(galaxyExt='html', title=str(tissue)), 'w')

                vg.countFromStart()

                res = vg.drawColumnChart(
                    tissueDict[tissue].values(),
                    xAxisRotation=90,
                    categories=tissueDict[tissue].keys(),
                    showInLegend=False,
                    titleText=str(tissue),
                    yAxisTitle='linear scale',
                    height=400,
                    addTable=True,
                    # extraScriptButton=[OrderedDict({'Use linear scale':'linear','Use log10 scale':'logarithmic'}), 'yAxisType']
                )

                res += vg.drawColumnChart(
                    [math.log10(v) for v in tissueDict[tissue].values()],
                    xAxisRotation=90,
                    categories=tissueDict[tissue].keys(),
                    showInLegend=False,
                    titleText=str(tissue),
                    yAxisTitle='log10 scale',
                    height=400,
                    addTable=True,
                    # extraScriptButton=[OrderedDict({'Use linear scale':'linear','Use log10 scale':'logarithmic'}), 'yAxisType']
                )

                outputFile.write(res)
                outputFile.close()

        htmlCore = HtmlCore()
        htmlCore.begin()

        htmlCore.line('Done')

        htmlCore.end()

        print htmlCore

    @staticmethod
    def validateAndReturnErrors(choices):
        return None

    @staticmethod
    def getOutputFormat(choices):
        return 'customhtml'


class geneExpression(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Gene expression"

    @staticmethod
    def getInputBoxNames():
        return [
            ('Select genome', 'genome'),
            ('Select annotatations', 'annotations'),
            ('Select RNA-Seq Data', 'rnaSeqData'),
            # ('RNA-Seq Data Histogram', 'rnaSeqDataPlot'),
            ('Select reference', 'reference'),
            ('Select cutoff value', 'cutOff'),
            ('Select tissue type', 'type')
        ]

    @staticmethod
    def getOptionsBoxGenome():
        return '__genome__'

    @staticmethod
    def getOptionsBoxAnnotations(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement()

    @staticmethod
    def getOptionsBoxRnaSeqData(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement()

    # @classmethod
    # def asDict(cls, vector):
    #     """Convert an RPy2 ListVector to a Python dict"""
    #     from rpy2 import robjects
    #     import types
    #     result = {}
    #     for i, name in enumerate(vector.names):
    #         if isinstance(vector[i], robjects.ListVector):
    #             result[name] = as_dict(vector[i])
    #         elif type(vector[i]) != types.BooleanType and len(vector[i]) == 1:
    #             result[name] = vector[i][0]
    #         else:
    #             result[name] = vector[i]
    #     return result

    # @staticmethod
    # def getOptionsBoxRnaSeqDataPlot(prevChoices):
    #
    #     htmlCore = HtmlCore()
    #     htmlCore.begin()
    #
    #     vg = visualizationGraphs()
    #     rnaSeqDataPlot=[]
    #     i=0
    #     if prevChoices.rnaSeqData:
    #
    #
    #
    #         f = open(ExternalTrackManager.extractFnFromGalaxyTN(prevChoices.rnaSeqData.split(':')), 'r')
    #         data = f.readlines()
    #         colLen = data[2]
    #         colLen = len(colLen.strip('\n').split('\t'))
    #
    #         col = [w for w in range(2, colLen)]
    #
    #         # #rnaSeqDataPlot = pd.read_csv(ExternalTrackManager.extractFnFromGalaxyTN(prevChoices.rnaSeqData.split(':')), sep='\t', skiprows=2, header=2)
    #
    #         # # with open(ExternalTrackManager.extractFnFromGalaxyTN(prevChoices.rnaSeqData.split(':')), 'r') as f:
    #         # #     for x in f.readlines():
    #         # #         if i > 2:
    #         # #             el = x.strip('\n').split('\t')
    #         # #             rnaSeqDataPlot.append(el[2:len(el)])
    #         # #         i+=1
    #         #
    #         # #
    #
    #
    #
    #         #count histoggram
    #         rCode = 'ourHist <- function(vec) {hist(vec, plot=FALSE)}'
    #         dd=robjects.FloatVector(list(itertools.chain.from_iterable(np.loadtxt(ExternalTrackManager.extractFnFromGalaxyTN(prevChoices.rnaSeqData.split(':')), skiprows=3, usecols=col))))
    #         simpleHist = r(rCode)(dd)
    #         simpleHistDict = geneExpression.asDict(simpleHist)
    #
    #
    #         res = vg.drawColumnChart(list(simpleHistDict['counts']),
    #                                 xAxisRotation=90,
    #                                 categories=list(simpleHistDict['breaks']),
    #                                 showInLegend=False,
    #                                 histogram=True,
    #                                 height=400
    #                                 )
    #         htmlCore.line(res)
    #
    #     htmlCore.end()
    #
    #     return '', str(res)


    @staticmethod
    def getOptionsBoxReference(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement()

    @staticmethod
    def getOptionsBoxCutOff(prevChoices):
        return ''

    @staticmethod
    def getOptionsBoxType(prevChoices):
        return ['SMTS', 'SMTSD']

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        annotation = choices.annotations
        rnaSeqData = choices.rnaSeqData
        reference = choices.reference

        cutoff = choices.cutOff
        type = choices.type

        if type == 'SMTSD':
            nrType = 6
        if type == 'SMTS':
            nrType = 5

        annotationDict = {}

        i = 0
        with open(ExternalTrackManager.extractFnFromGalaxyTN(annotation.split(':')), 'r') as f:
            for x in f.readlines():
                if i > 0:
                    el = x.strip('\n').split('\t')
                    if not el[nrType] in annotationDict:
                        annotationDict[el[nrType]] = []
                    if not el[0] in annotationDict[el[nrType]]:
                        annotationDict[el[nrType]].append(el[0])
                i += 1
        i = 0

        rnaSeqDataDict = {}
        with open(ExternalTrackManager.extractFnFromGalaxyTN(rnaSeqData.split(':')), 'r') as f:
            for x in f.readlines():
                if i == 2:
                    el = x.strip('\n').split('\t')
                    header = []
                    for elN in range(2, len(el)):
                        header.append(el[elN])
                        rnaSeqDataDict[el[elN]] = []
                if i > 2:
                    el = x.strip('\n').split('\t')
                    for elN in range(2, len(el)):
                        if el[elN] >= cutoff:
                            if not el[0] in rnaSeqDataDict[header[elN - 2]]:
                                rnaSeqDataDict[header[elN - 2]].append(el[0])
                i += 1

        rnaSeqDataDictList = list(itertools.chain.from_iterable(rnaSeqDataDict.values()))
        rnaSeqDataDictList = list(set(rnaSeqDataDictList))

        i = 0
        filesReferenceDict = {}
        referenceDict = {}

        header = []
        with open(ExternalTrackManager.extractFnFromGalaxyTN(reference.split(':')), 'r') as f:
            for x in f.readlines():

                if i > 4:

                    el = x.strip('\n').split(' ')
                    geneID = el[1].replace('"', '').replace(';', '')

                    elNewDiv = x.strip('\n').split('\t')

                    j = 0
                    xNew = []
                    for elND in elNewDiv:
                        if j == 0:
                            xNew.append('chr' + str(elNewDiv[0]))
                        else:
                            xNew.append(elND)
                        j += 1

                    if elNewDiv[2] == 'transcript':
                        if geneID in rnaSeqDataDictList:
                            if not geneID in referenceDict:
                                referenceDict[geneID] = []
                            referenceDict[geneID].append(i)

                            if i not in filesReferenceDict:
                                filesReferenceDict[i] = []
                            filesReferenceDict[i].append('\t'.join(xNew))

                            # print referenceDict
                            # print '\n' + '<br \>'
                else:
                    header.append(x)
                i += 1

        # print '\n' + '<br \>'
        # print '\n' + '<br \>'
        # print referenceDict

        # build files and then gSuite

        outGSuite = GSuite()
        for trackName, it0 in annotationDict.items():
            uri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn,
                                                extraFileName=trackName,
                                                suffix='gff')
            gSuiteTrack = GSuiteTrack(uri)
            outFn = gSuiteTrack.path
            ensurePathExists(outFn)

            with open(outFn, 'w') as outFile:
                outFile.write(''.join(header))

                for it00 in it0:
                    if it00 in rnaSeqDataDict:
                        for it1 in rnaSeqDataDict[it00]:
                            if it1 in referenceDict.keys():
                                for it2 in referenceDict[it1]:
                                    outFile.write(filesReferenceDict[it2][0] + '\n')

            outGSuite.addTrack(GSuiteTrack(uri, title=''.join(trackName), genome=choices.genome))

        GSuiteComposer.composeToFile(outGSuite, cls.extraGalaxyFn['gene expression GSuite'])

        # trackNameList = [ 'tissue', 'blood']
        #
        # for trackName in trackNameList:
        #     uri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn, extraFileName=trackName)
        #     gSuiteTrack = GSuiteTrack(uri)
        #     outFn = gSuiteTrack.path
        #     ensurePathExists(outFn)
        #     line = ['chr1', '10', '200']
        #     with open(outFn, 'w') as outFile:
        #         outFile.write('\t'.join(line) + '\n')
        #
        #
        #
        #     #staticFile = HbGSuiteTrack.generateURI(trackName=[trackName])
        #     #from quick.util.CommonFunctions import ensurePathExists
        #
        #     #ensurePathExists(fn)
        #
        #
        #
        #     #trackType = TrackInfo(choices.genome, trackName).trackFormatName.lower()
        #
        #     trackType = 'segments'
        #     #hbUri = HbGSuiteTrack.generateURI(trackName=trackName)
        #
        #
        #     outGSuite.addTrack(GSuiteTrack(uri, title=''.join(trackName), trackType=trackType, genome=choices.genome))
        #
        # GSuiteComposer.composeToFile(outGSuite, cls.extraGalaxyFn['gene eGSuite'])

    # @staticmethod
    # def getOutputFormat(choices):
    #     return 'customhtml'

    @staticmethod
    def validateAndReturnErrors(choices):
        return None

    @classmethod
    def getExtraHistElements(cls, choices):
        return [HistElement('gene expression GSuite', 'gsuite')]

    # @staticmethod
    # def getToolName():
    #     return "Gene expression"
    #
    # @staticmethod
    # def getInputBoxNames():
    #     return [
    #             ('Select genome', 'genome'),
    #             ('Select annotatations', 'annotations'),
    #             ('Select RNA-Seq Data', 'rnaSeqData'),
    #             #('RNA-Seq Data Histogram', 'rnaSeqDataPlot'),
    #             ('Select reference', 'reference'),
    #             ('Select cutoff value', 'cutOff'),
    #             ('Select tissue type', 'type')
    #             ]
    #
    # @staticmethod
    # def getOptionsBoxGenome():
    #     return '__genome__'
    #
    # @staticmethod
    # def getOptionsBoxAnnotations(prevChoices):
    #     return GeneralGuiTool.getHistorySelectionElement()
    #
    # @staticmethod
    # def getOptionsBoxRnaSeqData(prevChoices):
    #     return GeneralGuiTool.getHistorySelectionElement()
    #
    # # @classmethod
    # # def asDict(cls, vector):
    # #     """Convert an RPy2 ListVector to a Python dict"""
    # #     from rpy2 import robjects
    # #     import types
    # #     result = {}
    # #     for i, name in enumerate(vector.names):
    # #         if isinstance(vector[i], robjects.ListVector):
    # #             result[name] = as_dict(vector[i])
    # #         elif type(vector[i]) != types.BooleanType and len(vector[i]) == 1:
    # #             result[name] = vector[i][0]
    # #         else:
    # #             result[name] = vector[i]
    # #     return result
    #
    # # @staticmethod
    # # def getOptionsBoxRnaSeqDataPlot(prevChoices):
    # #
    # #     htmlCore = HtmlCore()
    # #     htmlCore.begin()
    # #
    # #     vg = visualizationGraphs()
    # #     rnaSeqDataPlot=[]
    # #     i=0
    # #     if prevChoices.rnaSeqData:
    # #
    # #
    # #
    # #         f = open(ExternalTrackManager.extractFnFromGalaxyTN(prevChoices.rnaSeqData.split(':')), 'r')
    # #         data = f.readlines()
    # #         colLen = data[2]
    # #         colLen = len(colLen.strip('\n').split('\t'))
    # #
    # #         col = [w for w in range(2, colLen)]
    # #
    # #         # #rnaSeqDataPlot = pd.read_csv(ExternalTrackManager.extractFnFromGalaxyTN(prevChoices.rnaSeqData.split(':')), sep='\t', skiprows=2, header=2)
    # #
    # #         # # with open(ExternalTrackManager.extractFnFromGalaxyTN(prevChoices.rnaSeqData.split(':')), 'r') as f:
    # #         # #     for x in f.readlines():
    # #         # #         if i > 2:
    # #         # #             el = x.strip('\n').split('\t')
    # #         # #             rnaSeqDataPlot.append(el[2:len(el)])
    # #         # #         i+=1
    # #         #
    # #         # #
    # #
    # #
    # #
    # #         #count histoggram
    # #         rCode = 'ourHist <- function(vec) {hist(vec, plot=FALSE)}'
    # #         dd=robjects.FloatVector(list(itertools.chain.from_iterable(np.loadtxt(ExternalTrackManager.extractFnFromGalaxyTN(prevChoices.rnaSeqData.split(':')), skiprows=3, usecols=col))))
    # #         simpleHist = r(rCode)(dd)
    # #         simpleHistDict = geneExpression.asDict(simpleHist)
    # #
    # #
    # #         res = vg.drawColumnChart(list(simpleHistDict['counts']),
    # #                                 xAxisRotation=90,
    # #                                 categories=list(simpleHistDict['breaks']),
    # #                                 showInLegend=False,
    # #                                 histogram=True,
    # #                                 height=400
    # #                                 )
    # #         htmlCore.line(res)
    # #
    # #     htmlCore.end()
    # #
    # #     return '', str(res)
    #
    #
    # @staticmethod
    # def getOptionsBoxReference(prevChoices):
    #     return GeneralGuiTool.getHistorySelectionElement()
    #
    # @staticmethod
    # def getOptionsBoxCutOff(prevChoices):
    #     return GeneralGuiTool.getHistorySelectionElement()
    #
    # @staticmethod
    # def getOptionsBoxType(prevChoices):
    #     return ['SMTS', 'SMTSD']

    # @classmethod
    # def execute(cls, choices, galaxyFn=None, username=''):
    #
    #     annotation = choices.annotations
    #     rnaSeqData = choices.rnaSeqData
    #     reference = choices.reference
    #
    #     cutoff = choices.cutOff
    #     type = choices.type
    #
    #     if type == 'SMTSD':
    #         nrType = 6
    #     if type == 'SMTS':
    #         nrType = 5
    #
    #
    #     cutoffDict={}
    #     with open(ExternalTrackManager.extractFnFromGalaxyTN(cutoff.split(':')), 'r') as f:
    #         for x in f.readlines():
    #             el = x.strip('\n').split('\t')
    #             cutoffDict[el[0]] = el[1]
    #
    #
    #     print cutoffDict
    #
    #     annotationDict = {}
    #     i=0
    #     with open(ExternalTrackManager.extractFnFromGalaxyTN(annotation.split(':')), 'r') as f:
    #         for x in f.readlines():
    #             if i > 0:
    #                 el = x.strip('\n').split('\t')
    #                 if not el[nrType] in annotationDict:
    #                     annotationDict[el[nrType]]=[]
    #                 if not el[0] in annotationDict[el[nrType]]:
    #                     annotationDict[el[nrType]].append(el[0])
    #             i+=1
    #     i=0
    #
    #     print annotationDict
    #
    #     rnaSeqDataDictList=[]
    #     rnaSeqDataDict={}
    #     with open(ExternalTrackManager.extractFnFromGalaxyTN(rnaSeqData.split(':')), 'r') as f:
    #         for x in f.readlines():
    #             if i == 2:
    #                 el = x.strip('\n').split('\t')
    #                 header=[]
    #                 for elN in range(2, len(el)):
    #                     header.append(el[elN])
    #                     rnaSeqDataDict[el[elN]]={}
    #                     # for key1 in annotationDict.keys():
    #                     #     rnaSeqDataDict[el[elN]][key1]=[]
    #             if i > 2:
    #                 el = x.strip('\n').split('\t')
    #                 if not el[0] in rnaSeqDataDictList:
    #                     rnaSeqDataDictList.append(el[0])
    #                 for elN in range(2, len(el)):
    #                     for key1, it1 in annotationDict.iteritems():
    #                         for it11 in it1:
    #                             if it11 == header[elN-2]:
    #                                 if key1 not in rnaSeqDataDict[header[elN-2]]:
    #                                     rnaSeqDataDict[header[elN-2]][key1]=[]
    #                                 #if key1 in cutoffDict.keys() and el[elN] >= cutoffDict[key1]:
    #                                 rnaSeqDataDict[header[elN-2]][key1].append(el[0])
    #
    #             i+=1
    #
    #     #rnaSeqDataDictList = list(itertools.chain.from_iterable(rnaSeqDataDict.values()))
    #     #rnaSeqDataDictList = list(set(rnaSeqDataDictList))
    #
    #
    #     i=0
    #     filesReferenceDict={}
    #     referenceDict={}
    #
    #     header=[]
    #     with open(ExternalTrackManager.extractFnFromGalaxyTN(reference.split(':')), 'r') as f:
    #         for x in f.readlines():
    #
    #             if i > 4:
    #
    #                 el = x.strip('\n').split(' ')
    #                 geneID = el[1].replace('"', '').replace(';','')
    #
    #                 elNewDiv = x.strip('\n').split('\t')
    #
    #                 j=0
    #                 xNew=[]
    #                 for elND in elNewDiv:
    #                     if j==0:
    #                         xNew.append('chr' + str(elNewDiv[0]))
    #                     else:
    #                         xNew.append(elND)
    #                     j+=1
    #
    #
    #                 if geneID in rnaSeqDataDictList:
    #                     if not geneID in referenceDict:
    #                         referenceDict[geneID] = []
    #                     referenceDict[geneID].append(i)
    #
    #                     if i not in filesReferenceDict:
    #                         filesReferenceDict[i]=[]
    #                     filesReferenceDict[i].append('\t'.join(xNew))
    #
    #                 # print referenceDict
    #                 # print '\n' + '<br \>'
    #             else:
    #                 header.append(x)
    #             i+=1
    #
    #     # print '\n' + '<br \>'
    #     # print '\n' + '<br \>'
    #     # print referenceDict
    #
    #     #build files and then gSuite
    #
    #     outGSuite = GSuite()
    #     for trackName, it0 in annotationDict.items():
    #         uri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn,
    #                                             extraFileName=trackName,
    #                                             suffix='gff')
    #         gSuiteTrack = GSuiteTrack(uri)
    #         outFn = gSuiteTrack.path
    #         ensurePathExists(outFn)
    #
    #
    #         with open(outFn, 'w') as outFile:
    #             outFile.write(''.join(header))
    #
    #             for it00 in it0:
    #                 if it00 in rnaSeqDataDict:
    #                     for it1 in rnaSeqDataDict[it00][trackName]:
    #                         for it2 in referenceDict[it1]:
    #                             outFile.write(filesReferenceDict[it2][0] + '\n')
    #
    #         outGSuite.addTrack(GSuiteTrack(uri, title=''.join(trackName), genome=choices.genome))
    #
    #     GSuiteComposer.composeToFile(outGSuite, cls.extraGalaxyFn['gene expression GSuite'])
    #
    #     # trackNameList = [ 'tissue', 'blood']
    #     #
    #     # for trackName in trackNameList:
    #     #     uri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn, extraFileName=trackName)
    #     #     gSuiteTrack = GSuiteTrack(uri)
    #     #     outFn = gSuiteTrack.path
    #     #     ensurePathExists(outFn)
    #     #     line = ['chr1', '10', '200']
    #     #     with open(outFn, 'w') as outFile:
    #     #         outFile.write('\t'.join(line) + '\n')
    #     #
    #     #
    #     #
    #     #     #staticFile = HbGSuiteTrack.generateURI(trackName=[trackName])
    #     #     #from quick.util.CommonFunctions import ensurePathExists
    #     #
    #     #     #ensurePathExists(fn)
    #     #
    #     #
    #     #
    #     #     #trackType = TrackInfo(choices.genome, trackName).trackFormatName.lower()
    #     #
    #     #     trackType = 'segments'
    #     #     #hbUri = HbGSuiteTrack.generateURI(trackName=trackName)
    #     #
    #     #
    #     #     outGSuite.addTrack(GSuiteTrack(uri, title=''.join(trackName), trackType=trackType, genome=choices.genome))
    #     #
    #     # GSuiteComposer.composeToFile(outGSuite, cls.extraGalaxyFn['gene eGSuite'])
    #
    # # @staticmethod
    # # def getOutputFormat(choices):
    # #     return 'customhtml'

    @staticmethod
    def validateAndReturnErrors(choices):
        return None

    @classmethod
    def getExtraHistElements(cls, choices):
        return [HistElement('gene expression GSuite', 'gsuite')]


class geneExpressionV2(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Gene expression per tissue"

    @staticmethod
    def getInputBoxNames():
        return [
            ('Select genome', 'genome'),
            ('Select annotatations', 'annotations'),
            ('Select RNA-Seq Data', 'rnaSeqData'),
            # ('RNA-Seq Data Histogram', 'rnaSeqDataPlot'),
            ('Select reference', 'reference'),
            ('Select file with tissue', 'fileTypeTissue'),
            ('List of possible tissue', 'typeTissue'),
            ('Select cutoff value', 'cutOff'),
            ('Select tissue type', 'type')
        ]

    @staticmethod
    def getOptionsBoxGenome():
        return '__genome__'

    @staticmethod
    def getOptionsBoxAnnotations(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement()

    @staticmethod
    def getOptionsBoxRnaSeqData(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement()

    @staticmethod
    def getOptionsBoxReference(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement()

    @staticmethod
    def getOptionsBoxFileTypeTissue(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement()

    @staticmethod
    def getOptionsBoxTypeTissue(prevChoices):
        listAnswer = []
        if prevChoices.fileTypeTissue:
            fileTissue = prevChoices.fileTypeTissue
            # listAnswer.append(fileTissue)
            with open(ExternalTrackManager.extractFnFromGalaxyTN(fileTissue.split(':')), 'r') as f:
                for x in f.readlines():
                    tissueName = x.replace('\t', '').replace('\n', '')
                    listAnswer.append(tissueName)
        return listAnswer

    @staticmethod
    def getOptionsBoxCutOff(prevChoices):
        return ''

    @staticmethod
    def getOptionsBoxType(prevChoices):
        return ['SMTS', 'SMTSD']

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        annotation = choices.annotations
        rnaSeqData = choices.rnaSeqData
        reference = choices.reference
        typeTissue = choices.typeTissue
        cutoff = choices.cutOff
        type = choices.type

        if type == 'SMTSD':
            nrType = 6
        if type == 'SMTS':
            nrType = 5

        annotationDict = {}  # tissue -> list of samID

        print typeTissue

        # typeTissue = 'Brain - Cortex'

        i = 0
        with open(ExternalTrackManager.extractFnFromGalaxyTN(annotation.split(':')), 'r') as f:
            for x in f.readlines():
                if i > 0:
                    el = x.strip('\n').split('\t')
                    if el[nrType] == typeTissue:
                        if not el[nrType] in annotationDict:
                            annotationDict[el[nrType]] = []
                        if not el[0] in annotationDict[el[nrType]]:
                            annotationDict[el[nrType]].append(el[0])
                i += 1
        i = 0

        print 'annotationDict - done'

        rnaSeqDataDict = {}
        with open(ExternalTrackManager.extractFnFromGalaxyTN(rnaSeqData.split(':')), 'r') as f:
            for x in f.readlines():
                if i % 1000 == 0:
                    print i
                if i == 2:
                    el = x.strip('\n').split('\t')
                    header = []
                    for elN in range(2, len(el)):
                        header.append(el[elN])
                        # rnaSeqDataDict[el[elN]]=[]
                if i > 2:
                    el = x.strip('\n').split('\t')
                    for elN in range(2, len(el)):
                        if el[elN] >= cutoff:
                            if header[elN - 2] in annotationDict[typeTissue]:
                                if not header[elN - 2] in rnaSeqDataDict:
                                    rnaSeqDataDict[header[elN - 2]] = []
                                if not el[0] in rnaSeqDataDict[header[elN - 2]]:
                                    rnaSeqDataDict[header[elN - 2]].append(el[0])
                i += 1

        print 'rnaSeqDataDict - done'

        rnaSeqDataDictList = list(itertools.chain.from_iterable(rnaSeqDataDict.values()))
        rnaSeqDataDictList = list(set(rnaSeqDataDictList))

        print 'rnaSeqDataDictList - done'

        i = 0
        filesReferenceDict = {}
        referenceDict = {}

        header = []
        with open(ExternalTrackManager.extractFnFromGalaxyTN(reference.split(':')), 'r') as f:
            for x in f.readlines():
                if i % 10000 == 0:
                    print i
                if i > 4:

                    el = x.strip('\n').split(' ')
                    geneID = el[1].replace('"', '').replace(';', '')

                    elNewDiv = x.strip('\n').split('\t')

                    j = 0
                    xNew = []
                    for elND in elNewDiv:
                        if j == 0:
                            xNew.append('chr' + str(elNewDiv[0]))
                        else:
                            xNew.append(elND)
                        j += 1

                    if geneID in rnaSeqDataDictList:
                        if elNewDiv[2] == 'transcript':
                            if geneID in rnaSeqDataDictList:
                                if not geneID in referenceDict:
                                    referenceDict[geneID] = []
                                referenceDict[geneID].append(i)

                                if i not in filesReferenceDict:
                                    filesReferenceDict[i] = []
                                filesReferenceDict[i].append('\t'.join(xNew))

                                # print referenceDict
                                # print '\n' + '<br \>'
                else:
                    header.append(x)
                i += 1

        # print '\n' + '<br \>'
        # print '\n' + '<br \>'
        # print referenceDict

        print 'reference - done'

        # build files and then gSuite

        outGSuite = GSuite()
        for trackName, it0 in annotationDict.items():
            uri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn,
                                                extraFileName=trackName,
                                                suffix='gff')
            gSuiteTrack = GSuiteTrack(uri)
            outFn = gSuiteTrack.path
            ensurePathExists(outFn)

            print str(trackName) + '-' + str(len(it0))
            with open(outFn, 'w') as outFile:
                outFile.write(''.join(header))

                for it00 in it0:
                    if it00 in rnaSeqDataDict:
                        for it1 in rnaSeqDataDict[it00]:
                            if it1 in referenceDict.keys():
                                for it2 in referenceDict[it1]:
                                    outFile.write(filesReferenceDict[it2][0] + '\n')

            print 'done with' + str(trackName)
            annotationDict[trackName] = []

            outGSuite.addTrack(GSuiteTrack(uri, title=''.join(trackName), genome=choices.genome))

        GSuiteComposer.composeToFile(outGSuite, cls.extraGalaxyFn['gene expression GSuite'])

        print 'GSuiteComposer - done'

    @staticmethod
    def validateAndReturnErrors(choices):
        return None

    @classmethod
    def getExtraHistElements(cls, choices):
        return [HistElement('gene expression GSuite', 'gsuite')]

    # @staticmethod
    # def getToolName():
    #     return "Gene expression"
    #
    # @staticmethod
    # def getInputBoxNames():
    #     return [
    #             ('Select genome', 'genome'),
    #             ('Select annotatations', 'annotations'),
    #             ('Select RNA-Seq Data', 'rnaSeqData'),
    #             #('RNA-Seq Data Histogram', 'rnaSeqDataPlot'),
    #             ('Select reference', 'reference'),
    #             ('Select cutoff value', 'cutOff'),
    #             ('Select tissue type', 'type')
    #             ]
    #
    # @staticmethod
    # def getOptionsBoxGenome():
    #     return '__genome__'
    #
    # @staticmethod
    # def getOptionsBoxAnnotations(prevChoices):
    #     return GeneralGuiTool.getHistorySelectionElement()
    #
    # @staticmethod
    # def getOptionsBoxRnaSeqData(prevChoices):
    #     return GeneralGuiTool.getHistorySelectionElement()
    #
    # # @classmethod
    # # def asDict(cls, vector):
    # #     """Convert an RPy2 ListVector to a Python dict"""
    # #     from rpy2 import robjects
    # #     import types
    # #     result = {}
    # #     for i, name in enumerate(vector.names):
    # #         if isinstance(vector[i], robjects.ListVector):
    # #             result[name] = as_dict(vector[i])
    # #         elif type(vector[i]) != types.BooleanType and len(vector[i]) == 1:
    # #             result[name] = vector[i][0]
    # #         else:
    # #             result[name] = vector[i]
    # #     return result
    #
    # # @staticmethod
    # # def getOptionsBoxRnaSeqDataPlot(prevChoices):
    # #
    # #     htmlCore = HtmlCore()
    # #     htmlCore.begin()
    # #
    # #     vg = visualizationGraphs()
    # #     rnaSeqDataPlot=[]
    # #     i=0
    # #     if prevChoices.rnaSeqData:
    # #
    # #
    # #
    # #         f = open(ExternalTrackManager.extractFnFromGalaxyTN(prevChoices.rnaSeqData.split(':')), 'r')
    # #         data = f.readlines()
    # #         colLen = data[2]
    # #         colLen = len(colLen.strip('\n').split('\t'))
    # #
    # #         col = [w for w in range(2, colLen)]
    # #
    # #         # #rnaSeqDataPlot = pd.read_csv(ExternalTrackManager.extractFnFromGalaxyTN(prevChoices.rnaSeqData.split(':')), sep='\t', skiprows=2, header=2)
    # #
    # #         # # with open(ExternalTrackManager.extractFnFromGalaxyTN(prevChoices.rnaSeqData.split(':')), 'r') as f:
    # #         # #     for x in f.readlines():
    # #         # #         if i > 2:
    # #         # #             el = x.strip('\n').split('\t')
    # #         # #             rnaSeqDataPlot.append(el[2:len(el)])
    # #         # #         i+=1
    # #         #
    # #         # #
    # #
    # #
    # #
    # #         #count histoggram
    # #         rCode = 'ourHist <- function(vec) {hist(vec, plot=FALSE)}'
    # #         dd=robjects.FloatVector(list(itertools.chain.from_iterable(np.loadtxt(ExternalTrackManager.extractFnFromGalaxyTN(prevChoices.rnaSeqData.split(':')), skiprows=3, usecols=col))))
    # #         simpleHist = r(rCode)(dd)
    # #         simpleHistDict = geneExpression.asDict(simpleHist)
    # #
    # #
    # #         res = vg.drawColumnChart(list(simpleHistDict['counts']),
    # #                                 xAxisRotation=90,
    # #                                 categories=list(simpleHistDict['breaks']),
    # #                                 showInLegend=False,
    # #                                 histogram=True,
    # #                                 height=400
    # #                                 )
    # #         htmlCore.line(res)
    # #
    # #     htmlCore.end()
    # #
    # #     return '', str(res)
    #
    #
    # @staticmethod
    # def getOptionsBoxReference(prevChoices):
    #     return GeneralGuiTool.getHistorySelectionElement()
    #
    # @staticmethod
    # def getOptionsBoxCutOff(prevChoices):
    #     return GeneralGuiTool.getHistorySelectionElement()
    #
    # @staticmethod
    # def getOptionsBoxType(prevChoices):
    #     return ['SMTS', 'SMTSD']

    # @classmethod
    # def execute(cls, choices, galaxyFn=None, username=''):
    #
    #     annotation = choices.annotations
    #     rnaSeqData = choices.rnaSeqData
    #     reference = choices.reference
    #
    #     cutoff = choices.cutOff
    #     type = choices.type
    #
    #     if type == 'SMTSD':
    #         nrType = 6
    #     if type == 'SMTS':
    #         nrType = 5
    #
    #
    #     cutoffDict={}
    #     with open(ExternalTrackManager.extractFnFromGalaxyTN(cutoff.split(':')), 'r') as f:
    #         for x in f.readlines():
    #             el = x.strip('\n').split('\t')
    #             cutoffDict[el[0]] = el[1]
    #
    #
    #     print cutoffDict
    #
    #     annotationDict = {}
    #     i=0
    #     with open(ExternalTrackManager.extractFnFromGalaxyTN(annotation.split(':')), 'r') as f:
    #         for x in f.readlines():
    #             if i > 0:
    #                 el = x.strip('\n').split('\t')
    #                 if not el[nrType] in annotationDict:
    #                     annotationDict[el[nrType]]=[]
    #                 if not el[0] in annotationDict[el[nrType]]:
    #                     annotationDict[el[nrType]].append(el[0])
    #             i+=1
    #     i=0
    #
    #     print annotationDict
    #
    #     rnaSeqDataDictList=[]
    #     rnaSeqDataDict={}
    #     with open(ExternalTrackManager.extractFnFromGalaxyTN(rnaSeqData.split(':')), 'r') as f:
    #         for x in f.readlines():
    #             if i == 2:
    #                 el = x.strip('\n').split('\t')
    #                 header=[]
    #                 for elN in range(2, len(el)):
    #                     header.append(el[elN])
    #                     rnaSeqDataDict[el[elN]]={}
    #                     # for key1 in annotationDict.keys():
    #                     #     rnaSeqDataDict[el[elN]][key1]=[]
    #             if i > 2:
    #                 el = x.strip('\n').split('\t')
    #                 if not el[0] in rnaSeqDataDictList:
    #                     rnaSeqDataDictList.append(el[0])
    #                 for elN in range(2, len(el)):
    #                     for key1, it1 in annotationDict.iteritems():
    #                         for it11 in it1:
    #                             if it11 == header[elN-2]:
    #                                 if key1 not in rnaSeqDataDict[header[elN-2]]:
    #                                     rnaSeqDataDict[header[elN-2]][key1]=[]
    #                                 #if key1 in cutoffDict.keys() and el[elN] >= cutoffDict[key1]:
    #                                 rnaSeqDataDict[header[elN-2]][key1].append(el[0])
    #
    #             i+=1
    #
    #     #rnaSeqDataDictList = list(itertools.chain.from_iterable(rnaSeqDataDict.values()))
    #     #rnaSeqDataDictList = list(set(rnaSeqDataDictList))
    #
    #
    #     i=0
    #     filesReferenceDict={}
    #     referenceDict={}
    #
    #     header=[]
    #     with open(ExternalTrackManager.extractFnFromGalaxyTN(reference.split(':')), 'r') as f:
    #         for x in f.readlines():
    #
    #             if i > 4:
    #
    #                 el = x.strip('\n').split(' ')
    #                 geneID = el[1].replace('"', '').replace(';','')
    #
    #                 elNewDiv = x.strip('\n').split('\t')
    #
    #                 j=0
    #                 xNew=[]
    #                 for elND in elNewDiv:
    #                     if j==0:
    #                         xNew.append('chr' + str(elNewDiv[0]))
    #                     else:
    #                         xNew.append(elND)
    #                     j+=1
    #
    #
    #                 if geneID in rnaSeqDataDictList:
    #                     if not geneID in referenceDict:
    #                         referenceDict[geneID] = []
    #                     referenceDict[geneID].append(i)
    #
    #                     if i not in filesReferenceDict:
    #                         filesReferenceDict[i]=[]
    #                     filesReferenceDict[i].append('\t'.join(xNew))
    #
    #                 # print referenceDict
    #                 # print '\n' + '<br \>'
    #             else:
    #                 header.append(x)
    #             i+=1
    #
    #     # print '\n' + '<br \>'
    #     # print '\n' + '<br \>'
    #     # print referenceDict
    #
    #     #build files and then gSuite
    #
    #     outGSuite = GSuite()
    #     for trackName, it0 in annotationDict.items():
    #         uri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn,
    #                                             extraFileName=trackName,
    #                                             suffix='gff')
    #         gSuiteTrack = GSuiteTrack(uri)
    #         outFn = gSuiteTrack.path
    #         ensurePathExists(outFn)
    #
    #
    #         with open(outFn, 'w') as outFile:
    #             outFile.write(''.join(header))
    #
    #             for it00 in it0:
    #                 if it00 in rnaSeqDataDict:
    #                     for it1 in rnaSeqDataDict[it00][trackName]:
    #                         for it2 in referenceDict[it1]:
    #                             outFile.write(filesReferenceDict[it2][0] + '\n')
    #
    #         outGSuite.addTrack(GSuiteTrack(uri, title=''.join(trackName), genome=choices.genome))
    #
    #     GSuiteComposer.composeToFile(outGSuite, cls.extraGalaxyFn['gene expression GSuite'])
    #
    #     # trackNameList = [ 'tissue', 'blood']
    #     #
    #     # for trackName in trackNameList:
    #     #     uri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn, extraFileName=trackName)
    #     #     gSuiteTrack = GSuiteTrack(uri)
    #     #     outFn = gSuiteTrack.path
    #     #     ensurePathExists(outFn)
    #     #     line = ['chr1', '10', '200']
    #     #     with open(outFn, 'w') as outFile:
    #     #         outFile.write('\t'.join(line) + '\n')
    #     #
    #     #
    #     #
    #     #     #staticFile = HbGSuiteTrack.generateURI(trackName=[trackName])
    #     #     #from quick.util.CommonFunctions import ensurePathExists
    #     #
    #     #     #ensurePathExists(fn)
    #     #
    #     #
    #     #
    #     #     #trackType = TrackInfo(choices.genome, trackName).trackFormatName.lower()
    #     #
    #     #     trackType = 'segments'
    #     #     #hbUri = HbGSuiteTrack.generateURI(trackName=trackName)
    #     #
    #     #
    #     #     outGSuite.addTrack(GSuiteTrack(uri, title=''.join(trackName), trackType=trackType, genome=choices.genome))
    #     #
    #     # GSuiteComposer.composeToFile(outGSuite, cls.extraGalaxyFn['gene eGSuite'])
    #
    # # @staticmethod
    # # def getOutputFormat(choices):
    # #     return 'customhtml'

    @staticmethod
    def validateAndReturnErrors(choices):
        return None

    @classmethod
    def getExtraHistElements(cls, choices):
        return [HistElement('gene expression GSuite', 'gsuite')]


class geneExpressionV3(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Gene expression per tissue (new)"

    @staticmethod
    def getInputBoxNames():
        return [
            ('Select genome', 'genome'),
            ('Select annotatations', 'annotations'),
            ('Select RNA-Seq Data', 'rnaSeqData'),
            # ('RNA-Seq Data Histogram', 'rnaSeqDataPlot'),
            ('Select reference', 'reference'),
            ('Select file with tissue', 'fileTypeTissue'),
            ('List of possible tissue', 'typeTissue'),
            ('Select cutoff value', 'cutOff'),
            ('Select tissue type', 'type')
        ]

    @staticmethod
    def getOptionsBoxGenome():
        return '__genome__'

    @staticmethod
    def getOptionsBoxAnnotations(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement()

    @staticmethod
    def getOptionsBoxRnaSeqData(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement()

    @staticmethod
    def getOptionsBoxReference(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement()

    @staticmethod
    def getOptionsBoxFileTypeTissue(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement()

    @staticmethod
    def getOptionsBoxTypeTissue(prevChoices):
        listAnswer = OrderedDict()
        if prevChoices.fileTypeTissue:
            fileTissue = prevChoices.fileTypeTissue
            # listAnswer.append(fileTissue)
            with open(ExternalTrackManager.extractFnFromGalaxyTN(fileTissue.split(':')), 'r') as f:
                for x in f.readlines():
                    tissueName = x.replace('\t', '').replace('\n', '')
                    if not tissueName in listAnswer:
                        listAnswer[tissueName] = False
        return listAnswer

    @staticmethod
    def getOptionsBoxCutOff(prevChoices):
        return ''

    @staticmethod
    def getOptionsBoxType(prevChoices):
        return ['SMTS', 'SMTSD']

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        annotation = choices.annotations
        rnaSeqData = choices.rnaSeqData
        reference = choices.reference
        typeTissueList = choices.typeTissue
        cutoff = choices.cutOff
        type = choices.type

        if type == 'SMTSD':
            nrType = 6
        if type == 'SMTS':
            nrType = 5

        # typeTissue = 'Brain - Cortex'


        outGSuite = GSuite()

        for typeTissue, ans in typeTissueList.items():

            if ans == 'True':

                print typeTissue

                annotationDict = {}  # tissue -> list of samID
                annotationDict.clear()

                i = 0
                with open(ExternalTrackManager.extractFnFromGalaxyTN(annotation.split(':')), 'r') as f:
                    for x in f.readlines():
                        if i > 0:
                            el = x.strip('\n').split('\t')
                            if el[nrType] == typeTissue:
                                if not el[nrType] in annotationDict:
                                    annotationDict[el[nrType]] = []
                                if not el[0] in annotationDict[el[nrType]]:
                                    annotationDict[el[nrType]].append(el[0])
                        i += 1
                i = 0

                print 'annotationDict - done'

                rnaSeqDataDict = {}
                rnaSeqDataDict.clear()

                with open(ExternalTrackManager.extractFnFromGalaxyTN(rnaSeqData.split(':')), 'r') as f:
                    for x in f.readlines():
                        if i % 1000 == 0:
                            print i
                        if i == 2:
                            el = x.strip('\n').split('\t')
                            header = []
                            for elN in range(2, len(el)):
                                header.append(el[elN])
                                # rnaSeqDataDict[el[elN]]=[]
                        if i > 2:
                            el = x.strip('\n').split('\t')
                            for elN in range(2, len(el)):
                                if header[elN - 2] in annotationDict[typeTissue]:
                                    if el[elN] >= cutoff:
                                        if not header[elN - 2] in rnaSeqDataDict:
                                            rnaSeqDataDict[header[elN - 2]] = []
                                        if not el[0] in rnaSeqDataDict[header[elN - 2]]:
                                            rnaSeqDataDict[header[elN - 2]].append(el[0])
                        i += 1

                print 'rnaSeqDataDict - done'

                rnaSeqDataDictList = list(itertools.chain.from_iterable(rnaSeqDataDict.values()))
                rnaSeqDataDictList = list(set(rnaSeqDataDictList))

                print rnaSeqDataDictList

                print 'rnaSeqDataDictList - done'

                i = 0
                filesReferenceDict = {}
                filesReferenceDict.clear()
                # referenceDict={}
                # referenceDict.clear()

                header = []
                with open(ExternalTrackManager.extractFnFromGalaxyTN(reference.split(':')), 'r') as f:
                    for x in f.readlines():
                        if i % 10000 == 0:
                            print i
                        if i > 4:

                            el = x.strip('\n').split(' ')
                            geneID = el[1].replace('"', '').replace(';', '')

                            elNewDiv = x.strip('\n').split('\t')

                            j = 0
                            xNew = []
                            for elND in elNewDiv:
                                if j == 0:
                                    xNew.append('chr' + str(elNewDiv[0]))
                                else:
                                    xNew.append(elND)
                                j += 1

                            if geneID in rnaSeqDataDictList:
                                if elNewDiv[2] == 'transcript':
                                    # if not geneID in referenceDict:
                                    #     referenceDict[geneID] = []
                                    # referenceDict[geneID].append(i)

                                    if i not in filesReferenceDict:
                                        filesReferenceDict[i] = []
                                    filesReferenceDict[i].append('\t'.join(xNew))

                                    # print referenceDict
                        else:
                            header.append(x)
                        i += 1

                # print '\n' + '<br \>'
                # print '\n' + '<br \>'

                print 'reference - done'

                # build files and then gSuite


                for trackName, it0 in annotationDict.items():
                    uri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn,
                                                        extraFileName=trackName,
                                                        suffix='gff')
                    gSuiteTrack = GSuiteTrack(uri)
                    outFn = gSuiteTrack.path
                    ensurePathExists(outFn)

                    print str(trackName) + '-' + str(len(it0))
                    with open(outFn, 'w') as outFile:
                        outFile.write(''.join(header))

                        for el in filesReferenceDict:
                            outFile.write(filesReferenceDict[el][0] + '\n')

                    print 'done with' + str(trackName)
                    annotationDict[trackName] = []

                    outGSuite.addTrack(GSuiteTrack(uri, title=''.join(trackName), genome=choices.genome))

        GSuiteComposer.composeToFile(outGSuite, cls.extraGalaxyFn['gene expression GSuite'])

        print 'GSuiteComposer - done'

    @staticmethod
    def validateAndReturnErrors(choices):
        return None

    @classmethod
    def getExtraHistElements(cls, choices):
        return [HistElement('gene expression GSuite', 'gsuite')]

    # @staticmethod
    # def getToolName():
    #     return "Gene expression"
    #
    # @staticmethod
    # def getInputBoxNames():
    #     return [
    #             ('Select genome', 'genome'),
    #             ('Select annotatations', 'annotations'),
    #             ('Select RNA-Seq Data', 'rnaSeqData'),
    #             #('RNA-Seq Data Histogram', 'rnaSeqDataPlot'),
    #             ('Select reference', 'reference'),
    #             ('Select cutoff value', 'cutOff'),
    #             ('Select tissue type', 'type')
    #             ]
    #
    # @staticmethod
    # def getOptionsBoxGenome():
    #     return '__genome__'
    #
    # @staticmethod
    # def getOptionsBoxAnnotations(prevChoices):
    #     return GeneralGuiTool.getHistorySelectionElement()
    #
    # @staticmethod
    # def getOptionsBoxRnaSeqData(prevChoices):
    #     return GeneralGuiTool.getHistorySelectionElement()
    #
    # # @classmethod
    # # def asDict(cls, vector):
    # #     """Convert an RPy2 ListVector to a Python dict"""
    # #     from rpy2 import robjects
    # #     import types
    # #     result = {}
    # #     for i, name in enumerate(vector.names):
    # #         if isinstance(vector[i], robjects.ListVector):
    # #             result[name] = as_dict(vector[i])
    # #         elif type(vector[i]) != types.BooleanType and len(vector[i]) == 1:
    # #             result[name] = vector[i][0]
    # #         else:
    # #             result[name] = vector[i]
    # #     return result
    #
    # # @staticmethod
    # # def getOptionsBoxRnaSeqDataPlot(prevChoices):
    # #
    # #     htmlCore = HtmlCore()
    # #     htmlCore.begin()
    # #
    # #     vg = visualizationGraphs()
    # #     rnaSeqDataPlot=[]
    # #     i=0
    # #     if prevChoices.rnaSeqData:
    # #
    # #
    # #
    # #         f = open(ExternalTrackManager.extractFnFromGalaxyTN(prevChoices.rnaSeqData.split(':')), 'r')
    # #         data = f.readlines()
    # #         colLen = data[2]
    # #         colLen = len(colLen.strip('\n').split('\t'))
    # #
    # #         col = [w for w in range(2, colLen)]
    # #
    # #         # #rnaSeqDataPlot = pd.read_csv(ExternalTrackManager.extractFnFromGalaxyTN(prevChoices.rnaSeqData.split(':')), sep='\t', skiprows=2, header=2)
    # #
    # #         # # with open(ExternalTrackManager.extractFnFromGalaxyTN(prevChoices.rnaSeqData.split(':')), 'r') as f:
    # #         # #     for x in f.readlines():
    # #         # #         if i > 2:
    # #         # #             el = x.strip('\n').split('\t')
    # #         # #             rnaSeqDataPlot.append(el[2:len(el)])
    # #         # #         i+=1
    # #         #
    # #         # #
    # #
    # #
    # #
    # #         #count histoggram
    # #         rCode = 'ourHist <- function(vec) {hist(vec, plot=FALSE)}'
    # #         dd=robjects.FloatVector(list(itertools.chain.from_iterable(np.loadtxt(ExternalTrackManager.extractFnFromGalaxyTN(prevChoices.rnaSeqData.split(':')), skiprows=3, usecols=col))))
    # #         simpleHist = r(rCode)(dd)
    # #         simpleHistDict = geneExpression.asDict(simpleHist)
    # #
    # #
    # #         res = vg.drawColumnChart(list(simpleHistDict['counts']),
    # #                                 xAxisRotation=90,
    # #                                 categories=list(simpleHistDict['breaks']),
    # #                                 showInLegend=False,
    # #                                 histogram=True,
    # #                                 height=400
    # #                                 )
    # #         htmlCore.line(res)
    # #
    # #     htmlCore.end()
    # #
    # #     return '', str(res)
    #
    #
    # @staticmethod
    # def getOptionsBoxReference(prevChoices):
    #     return GeneralGuiTool.getHistorySelectionElement()
    #
    # @staticmethod
    # def getOptionsBoxCutOff(prevChoices):
    #     return GeneralGuiTool.getHistorySelectionElement()
    #
    # @staticmethod
    # def getOptionsBoxType(prevChoices):
    #     return ['SMTS', 'SMTSD']

    # @classmethod
    # def execute(cls, choices, galaxyFn=None, username=''):
    #
    #     annotation = choices.annotations
    #     rnaSeqData = choices.rnaSeqData
    #     reference = choices.reference
    #
    #     cutoff = choices.cutOff
    #     type = choices.type
    #
    #     if type == 'SMTSD':
    #         nrType = 6
    #     if type == 'SMTS':
    #         nrType = 5
    #
    #
    #     cutoffDict={}
    #     with open(ExternalTrackManager.extractFnFromGalaxyTN(cutoff.split(':')), 'r') as f:
    #         for x in f.readlines():
    #             el = x.strip('\n').split('\t')
    #             cutoffDict[el[0]] = el[1]
    #
    #
    #     print cutoffDict
    #
    #     annotationDict = {}
    #     i=0
    #     with open(ExternalTrackManager.extractFnFromGalaxyTN(annotation.split(':')), 'r') as f:
    #         for x in f.readlines():
    #             if i > 0:
    #                 el = x.strip('\n').split('\t')
    #                 if not el[nrType] in annotationDict:
    #                     annotationDict[el[nrType]]=[]
    #                 if not el[0] in annotationDict[el[nrType]]:
    #                     annotationDict[el[nrType]].append(el[0])
    #             i+=1
    #     i=0
    #
    #     print annotationDict
    #
    #     rnaSeqDataDictList=[]
    #     rnaSeqDataDict={}
    #     with open(ExternalTrackManager.extractFnFromGalaxyTN(rnaSeqData.split(':')), 'r') as f:
    #         for x in f.readlines():
    #             if i == 2:
    #                 el = x.strip('\n').split('\t')
    #                 header=[]
    #                 for elN in range(2, len(el)):
    #                     header.append(el[elN])
    #                     rnaSeqDataDict[el[elN]]={}
    #                     # for key1 in annotationDict.keys():
    #                     #     rnaSeqDataDict[el[elN]][key1]=[]
    #             if i > 2:
    #                 el = x.strip('\n').split('\t')
    #                 if not el[0] in rnaSeqDataDictList:
    #                     rnaSeqDataDictList.append(el[0])
    #                 for elN in range(2, len(el)):
    #                     for key1, it1 in annotationDict.iteritems():
    #                         for it11 in it1:
    #                             if it11 == header[elN-2]:
    #                                 if key1 not in rnaSeqDataDict[header[elN-2]]:
    #                                     rnaSeqDataDict[header[elN-2]][key1]=[]
    #                                 #if key1 in cutoffDict.keys() and el[elN] >= cutoffDict[key1]:
    #                                 rnaSeqDataDict[header[elN-2]][key1].append(el[0])
    #
    #             i+=1
    #
    #     #rnaSeqDataDictList = list(itertools.chain.from_iterable(rnaSeqDataDict.values()))
    #     #rnaSeqDataDictList = list(set(rnaSeqDataDictList))
    #
    #
    #     i=0
    #     filesReferenceDict={}
    #     referenceDict={}
    #
    #     header=[]
    #     with open(ExternalTrackManager.extractFnFromGalaxyTN(reference.split(':')), 'r') as f:
    #         for x in f.readlines():
    #
    #             if i > 4:
    #
    #                 el = x.strip('\n').split(' ')
    #                 geneID = el[1].replace('"', '').replace(';','')
    #
    #                 elNewDiv = x.strip('\n').split('\t')
    #
    #                 j=0
    #                 xNew=[]
    #                 for elND in elNewDiv:
    #                     if j==0:
    #                         xNew.append('chr' + str(elNewDiv[0]))
    #                     else:
    #                         xNew.append(elND)
    #                     j+=1
    #
    #
    #                 if geneID in rnaSeqDataDictList:
    #                     if not geneID in referenceDict:
    #                         referenceDict[geneID] = []
    #                     referenceDict[geneID].append(i)
    #
    #                     if i not in filesReferenceDict:
    #                         filesReferenceDict[i]=[]
    #                     filesReferenceDict[i].append('\t'.join(xNew))
    #
    #                 # print referenceDict
    #                 # print '\n' + '<br \>'
    #             else:
    #                 header.append(x)
    #             i+=1
    #
    #     # print '\n' + '<br \>'
    #     # print '\n' + '<br \>'
    #     # print referenceDict
    #
    #     #build files and then gSuite
    #
    #     outGSuite = GSuite()
    #     for trackName, it0 in annotationDict.items():
    #         uri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn,
    #                                             extraFileName=trackName,
    #                                             suffix='gff')
    #         gSuiteTrack = GSuiteTrack(uri)
    #         outFn = gSuiteTrack.path
    #         ensurePathExists(outFn)
    #
    #
    #         with open(outFn, 'w') as outFile:
    #             outFile.write(''.join(header))
    #
    #             for it00 in it0:
    #                 if it00 in rnaSeqDataDict:
    #                     for it1 in rnaSeqDataDict[it00][trackName]:
    #                         for it2 in referenceDict[it1]:
    #                             outFile.write(filesReferenceDict[it2][0] + '\n')
    #
    #         outGSuite.addTrack(GSuiteTrack(uri, title=''.join(trackName), genome=choices.genome))
    #
    #     GSuiteComposer.composeToFile(outGSuite, cls.extraGalaxyFn['gene expression GSuite'])
    #
    #     # trackNameList = [ 'tissue', 'blood']
    #     #
    #     # for trackName in trackNameList:
    #     #     uri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn, extraFileName=trackName)
    #     #     gSuiteTrack = GSuiteTrack(uri)
    #     #     outFn = gSuiteTrack.path
    #     #     ensurePathExists(outFn)
    #     #     line = ['chr1', '10', '200']
    #     #     with open(outFn, 'w') as outFile:
    #     #         outFile.write('\t'.join(line) + '\n')
    #     #
    #     #
    #     #
    #     #     #staticFile = HbGSuiteTrack.generateURI(trackName=[trackName])
    #     #     #from quick.util.CommonFunctions import ensurePathExists
    #     #
    #     #     #ensurePathExists(fn)
    #     #
    #     #
    #     #
    #     #     #trackType = TrackInfo(choices.genome, trackName).trackFormatName.lower()
    #     #
    #     #     trackType = 'segments'
    #     #     #hbUri = HbGSuiteTrack.generateURI(trackName=trackName)
    #     #
    #     #
    #     #     outGSuite.addTrack(GSuiteTrack(uri, title=''.join(trackName), trackType=trackType, genome=choices.genome))
    #     #
    #     # GSuiteComposer.composeToFile(outGSuite, cls.extraGalaxyFn['gene eGSuite'])
    #
    # # @staticmethod
    # # def getOutputFormat(choices):
    # #     return 'customhtml'

    @staticmethod
    def validateAndReturnErrors(choices):
        return None

    @classmethod
    def getExtraHistElements(cls, choices):
        return [HistElement('gene expression GSuite', 'gsuite')]


# gSuite of bed files without coutoff value
class geneExpressionV4(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Gene expression per tissue (gSuite)"

    @staticmethod
    def getInputBoxNames():
        return [
            ('Select genome', 'genome'),
            ('Select annotatations', 'annotations'),
            ('Select RNA-Seq Data', 'rnaSeqData'),
            ('Select reference', 'reference'),
            ('Select file with tissue', 'fileTypeTissue'),
            ('List of possible tissue', 'typeTissue'),
            ('Select tissue type', 'type')
        ]

    @staticmethod
    def getOptionsBoxGenome():
        return '__genome__'

    @staticmethod
    def getOptionsBoxAnnotations(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement()

    @staticmethod
    def getOptionsBoxRnaSeqData(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement()

    @staticmethod
    def getOptionsBoxReference(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement()

    @staticmethod
    def getOptionsBoxFileTypeTissue(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement()

    @staticmethod
    def getOptionsBoxTypeTissue(prevChoices):
        listAnswer = OrderedDict()
        if prevChoices.fileTypeTissue:
            fileTissue = prevChoices.fileTypeTissue
            # listAnswer.append(fileTissue)
            with open(ExternalTrackManager.extractFnFromGalaxyTN(fileTissue.split(':')), 'r') as f:
                for x in f.readlines():
                    tissueName = x.replace('\t', '').replace('\n', '')
                    if not tissueName in listAnswer:
                        listAnswer[tissueName] = False
        return listAnswer

    @staticmethod
    def getOptionsBoxCutOff(prevChoices):
        return ''

    @staticmethod
    def getOptionsBoxType(prevChoices):
        return ['SMTS', 'SMTSD']

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        annotation = choices.annotations
        rnaSeqData = choices.rnaSeqData
        reference = choices.reference
        typeTissueList = choices.typeTissue
        type = choices.type

        if type == 'SMTSD':
            nrType = 6
        if type == 'SMTS':
            nrType = 5

        # typeTissue = 'Brain - Cortex'


        outGSuite = GSuite()

        for typeTissue, ans in typeTissueList.items():

            if ans == 'True':

                print typeTissue

                annotationDict = {}  # tissue -> list of samID
                annotationDict.clear()

                i = 0
                with open(ExternalTrackManager.extractFnFromGalaxyTN(annotation.split(':')), 'r') as f:
                    for x in f.readlines():
                        if i > 0:
                            el = x.strip('\n').split('\t')
                            if el[nrType] == typeTissue:
                                if not el[nrType] in annotationDict:
                                    annotationDict[el[nrType]] = []
                                if not el[0] in annotationDict[el[nrType]]:
                                    annotationDict[el[nrType]].append(el[0])
                        i += 1
                i = 0

                print 'annotationDict - done'

                # print annotationDict

                rnaSeqDataDictList = []
                rnaSeqDataDict = {}
                rnaSeqDataDict.clear()

                with open(ExternalTrackManager.extractFnFromGalaxyTN(rnaSeqData.split(':')), 'r') as f:
                    for x in f.readlines():
                        if i % 1000 == 0:
                            print i
                        if i == 2:
                            el = x.strip('\n').split('\t')
                            header = []
                            for elN in range(2, len(el)):
                                header.append(el[elN])
                                # rnaSeqDataDict[el[elN]]=[]
                        if i > 2:
                            el = x.strip('\n').split('\t')
                            for elN in range(2, len(el)):
                                if header[elN - 2] in annotationDict[typeTissue]:
                                    # if el[elN] >= cutoff:
                                    if not el[0] in rnaSeqDataDict:
                                        rnaSeqDataDict[el[0]] = []
                                        rnaSeqDataDictList.append(el[0])

                                    rnaSeqDataDict[el[0]].append(float(el[elN]))


                                #                                     if not header[elN-2] in rnaSeqDataDict:
                                #                                         rnaSeqDataDict[header[elN-2]]=[]
                                #
                                #                                     if not el[0] in rnaSeqDataDict[header[elN-2]]:
                                #                                         rnaSeqDataDict[header[elN-2]].append([el[0], el[elN]])
                                #                                         rnaSeqDataDictList.append(el[0])
                        i += 1

                print 'rnaSeqDataDict - done'
                # print rnaSeqDataDict


                # rnaSeqDataDictList = list(itertools.chain.from_iterable(rnaSeqDataDict.values()))
                # rnaSeqDataDictList = list(set(rnaSeqDataDictList))

                # print rnaSeqDataDictList

                print 'rnaSeqDataDictList - done'

                i = 0
                filesReferenceDict = {}
                filesReferenceDict.clear()
                # referenceDict={}
                # referenceDict.clear()

                header = []
                with open(ExternalTrackManager.extractFnFromGalaxyTN(reference.split(':')), 'r') as f:
                    for x in f.readlines():
                        if i % 10000 == 0:
                            print i
                        if i > 4:

                            el = x.strip('\n').split(' ')
                            geneID = el[1].replace('"', '').replace(';', '')

                            elNewDiv = x.strip('\n').split('\t')

                            xNew = []

                            xNew.append('chr' + str(elNewDiv[0]))
                            xNew.append(int(elNewDiv[3]))
                            xNew.append(int(elNewDiv[4]))

                            avgVal = float(sum(rnaSeqDataDict[geneID]) / float(len(rnaSeqDataDict[geneID])))
                            xNew.append(str(geneID) + '---' + str(avgVal))

                            if geneID in rnaSeqDataDictList:
                                if elNewDiv[2] == 'transcript':
                                    # if not geneID in referenceDict:
                                    #     referenceDict[geneID] = []
                                    # referenceDict[geneID].append(i)

                                    if i not in filesReferenceDict:
                                        filesReferenceDict[i] = []
                                    filesReferenceDict[i].append('\t'.join(xNew))

                                    # print referenceDict
                        else:
                            pass
                            # header.append(x)
                        i += 1

                # print '\n' + '<br \>'
                # print '\n' + '<br \>'

                print 'reference - done'

                # build files and then gSuite


                for trackName, it0 in annotationDict.items():
                    uri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn,
                                                        extraFileName=trackName,
                                                        suffix='bed')
                    gSuiteTrack = GSuiteTrack(uri)
                    outFn = gSuiteTrack.path
                    ensurePathExists(outFn)

                    print str(trackName) + '-' + str(len(it0))
                    with open(outFn, 'w') as outFile:
                        outFile.write(''.join(header))

                        for el in filesReferenceDict:
                            outFile.write(filesReferenceDict[el][0] + '\n')

                    print 'done with' + str(trackName)
                    annotationDict[trackName] = []

                    outGSuite.addTrack(GSuiteTrack(uri, title=''.join(trackName), genome=choices.genome))

        GSuiteComposer.composeToFile(outGSuite, cls.extraGalaxyFn['gene expression GSuite'])

        print 'GSuiteComposer - done'

    @staticmethod
    def validateAndReturnErrors(choices):
        return None

    @classmethod
    def getExtraHistElements(cls, choices):
        return [HistElement('gene expression GSuite', 'gsuite')]

    # @staticmethod
    # def getToolName():
    #     return "Gene expression"
    #
    # @staticmethod
    # def getInputBoxNames():
    #     return [
    #             ('Select genome', 'genome'),
    #             ('Select annotatations', 'annotations'),
    #             ('Select RNA-Seq Data', 'rnaSeqData'),
    #             #('RNA-Seq Data Histogram', 'rnaSeqDataPlot'),
    #             ('Select reference', 'reference'),
    #             ('Select cutoff value', 'cutOff'),
    #             ('Select tissue type', 'type')
    #             ]
    #
    # @staticmethod
    # def getOptionsBoxGenome():
    #     return '__genome__'
    #
    # @staticmethod
    # def getOptionsBoxAnnotations(prevChoices):
    #     return GeneralGuiTool.getHistorySelectionElement()
    #
    # @staticmethod
    # def getOptionsBoxRnaSeqData(prevChoices):
    #     return GeneralGuiTool.getHistorySelectionElement()
    #
    # # @classmethod
    # # def asDict(cls, vector):
    # #     """Convert an RPy2 ListVector to a Python dict"""
    # #     from rpy2 import robjects
    # #     import types
    # #     result = {}
    # #     for i, name in enumerate(vector.names):
    # #         if isinstance(vector[i], robjects.ListVector):
    # #             result[name] = as_dict(vector[i])
    # #         elif type(vector[i]) != types.BooleanType and len(vector[i]) == 1:
    # #             result[name] = vector[i][0]
    # #         else:
    # #             result[name] = vector[i]
    # #     return result
    #
    # # @staticmethod
    # # def getOptionsBoxRnaSeqDataPlot(prevChoices):
    # #
    # #     htmlCore = HtmlCore()
    # #     htmlCore.begin()
    # #
    # #     vg = visualizationGraphs()
    # #     rnaSeqDataPlot=[]
    # #     i=0
    # #     if prevChoices.rnaSeqData:
    # #
    # #
    # #
    # #         f = open(ExternalTrackManager.extractFnFromGalaxyTN(prevChoices.rnaSeqData.split(':')), 'r')
    # #         data = f.readlines()
    # #         colLen = data[2]
    # #         colLen = len(colLen.strip('\n').split('\t'))
    # #
    # #         col = [w for w in range(2, colLen)]
    # #
    # #         # #rnaSeqDataPlot = pd.read_csv(ExternalTrackManager.extractFnFromGalaxyTN(prevChoices.rnaSeqData.split(':')), sep='\t', skiprows=2, header=2)
    # #
    # #         # # with open(ExternalTrackManager.extractFnFromGalaxyTN(prevChoices.rnaSeqData.split(':')), 'r') as f:
    # #         # #     for x in f.readlines():
    # #         # #         if i > 2:
    # #         # #             el = x.strip('\n').split('\t')
    # #         # #             rnaSeqDataPlot.append(el[2:len(el)])
    # #         # #         i+=1
    # #         #
    # #         # #
    # #
    # #
    # #
    # #         #count histoggram
    # #         rCode = 'ourHist <- function(vec) {hist(vec, plot=FALSE)}'
    # #         dd=robjects.FloatVector(list(itertools.chain.from_iterable(np.loadtxt(ExternalTrackManager.extractFnFromGalaxyTN(prevChoices.rnaSeqData.split(':')), skiprows=3, usecols=col))))
    # #         simpleHist = r(rCode)(dd)
    # #         simpleHistDict = geneExpression.asDict(simpleHist)
    # #
    # #
    # #         res = vg.drawColumnChart(list(simpleHistDict['counts']),
    # #                                 xAxisRotation=90,
    # #                                 categories=list(simpleHistDict['breaks']),
    # #                                 showInLegend=False,
    # #                                 histogram=True,
    # #                                 height=400
    # #                                 )
    # #         htmlCore.line(res)
    # #
    # #     htmlCore.end()
    # #
    # #     return '', str(res)
    #
    #
    # @staticmethod
    # def getOptionsBoxReference(prevChoices):
    #     return GeneralGuiTool.getHistorySelectionElement()
    #
    # @staticmethod
    # def getOptionsBoxCutOff(prevChoices):
    #     return GeneralGuiTool.getHistorySelectionElement()
    #
    # @staticmethod
    # def getOptionsBoxType(prevChoices):
    #     return ['SMTS', 'SMTSD']

    # @classmethod
    # def execute(cls, choices, galaxyFn=None, username=''):
    #
    #     annotation = choices.annotations
    #     rnaSeqData = choices.rnaSeqData
    #     reference = choices.reference
    #
    #     cutoff = choices.cutOff
    #     type = choices.type
    #
    #     if type == 'SMTSD':
    #         nrType = 6
    #     if type == 'SMTS':
    #         nrType = 5
    #
    #
    #     cutoffDict={}
    #     with open(ExternalTrackManager.extractFnFromGalaxyTN(cutoff.split(':')), 'r') as f:
    #         for x in f.readlines():
    #             el = x.strip('\n').split('\t')
    #             cutoffDict[el[0]] = el[1]
    #
    #
    #     print cutoffDict
    #
    #     annotationDict = {}
    #     i=0
    #     with open(ExternalTrackManager.extractFnFromGalaxyTN(annotation.split(':')), 'r') as f:
    #         for x in f.readlines():
    #             if i > 0:
    #                 el = x.strip('\n').split('\t')
    #                 if not el[nrType] in annotationDict:
    #                     annotationDict[el[nrType]]=[]
    #                 if not el[0] in annotationDict[el[nrType]]:
    #                     annotationDict[elGene expression - select cutoff value for gSuite[nrType]].append(el[0])
    #             i+=1
    #     i=0
    #
    #     print annotationDict
    #
    #     rnaSeqDataDictList=[]
    #     rnaSeqDataDict={}
    #     with open(ExternalTrackManager.extractFnFromGalaxyTN(rnaSeqData.split(':')), 'r') as f:
    #         for x in f.readlines():
    #             if i == 2:
    #                 el = x.strip('\n').split('\t')
    #                 header=[]
    #                 for elN in range(2, len(el)):
    #                     header.append(el[elN])
    #                     rnaSeqDataDict[el[elN]]={}
    #                     # for key1 in annotationDict.keys():
    #                     #     rnaSeqDataDict[el[elN]][key1]=[]
    #             if i > 2:
    #                 el = x.strip('\n').split('\t')
    #                 if not el[0] in rnaSeqDataDictList:
    #                     rnaSeqDataDictList.append(el[0])
    #                 for elN in range(2, len(el)):
    #                     for key1, it1 in annotationDict.iteritems():
    #                         for it11 in it1:
    #                             if it11 == header[elN-2]:
    #                                 if key1 not in rnaSeqDataDict[header[elN-2]]:
    #                                     rnaSeqDataDict[header[elN-2]][key1]=[]
    #                                 #if key1 in cutoffDict.keys() and el[elN] >= cutoffDict[key1]:
    #                                 rnaSeqDataDict[header[elN-2]][key1].append(el[0])
    #
    #             i+=1
    #
    #     #rnaSeqDataDictList = list(itertools.chain.from_iterable(rnaSeqDataDict.values()))
    #     #rnaSeqDataDictList = list(set(rnaSeqDataDictList))
    #
    #
    #     i=0
    #     filesReferenceDict={}
    #     referenceDict={}
    #
    #     header=[]
    #     with open(ExternalTrackManager.extractFnFromGalaxyTN(reference.split(':')), 'r') as f:
    #         for x in f.readlines():
    #
    #             if i > 4:
    #
    #                 el = x.strip('\n').split(' ')
    #                 geneID = el[1].replace('"', '').replace(';','')
    #
    #                 elNewDiv = x.strip('\n').split('\t')
    #
    #                 j=0
    #                 xNew=[]
    #                 for elND in elNewDiv:
    #                     if j==0:
    #                         xNew.append('chr' + str(elNewDiv[0]))
    #                     else:
    #                         xNew.append(elND)
    #                     j+=1
    #
    #
    #                 if geneID in rnaSeqDataDictList:
    #                     if not geneID in referenceDict:
    #                         referenceDict[geneID] = []
    #                     referenceDict[geneID].append(i)
    #
    #                     if i not in filesReferenceDict:
    #                         filesReferenceDict[i]=[]
    #                     filesReferenceDict[i].append('\t'.join(xNew))
    #
    #                 # print referenceDict
    #                 # print '\n' + '<br \>'
    #             else:
    #                 header.append(x)
    #             i+=1
    #
    #     # print '\n' + '<br \>'
    #     # print '\n' + '<br \>'
    #     # print referenceDict
    #
    #     #build files and then gSuite
    #
    #     outGSuite = GSuite()
    #     for trackName, it0 in annotationDict.items():
    #         uri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn,
    #                                             extraFileName=trackName,
    #                                             suffix='gff')
    #         gSuiteTrack = GSuiteTrack(uri)
    #         outFn = gSuiteTrack.path
    #         ensurePathExists(outFn)
    #
    #
    #         with open(outFn, 'w') as outFile:
    #             outFile.write(''.join(header))
    #
    #             for it00 in it0:
    #                 if it00 in rnaSeqDataDict:
    #                     for it1 in rnaSeqDataDict[it00][trackName]:
    #                         for it2 in referenceDict[it1]:
    #                             outFile.write(filesReferenceDict[it2][0] + '\n')
    #
    #         outGSuite.addTrack(GSuiteTrack(uri, title=''.join(trackName), genome=choices.genome))
    #
    #     GSuiteComposer.composeToFile(outGSuite, cls.extraGalaxyFn['gene expression GSuite'])
    #
    #     # trackNameList = [ 'tissue', 'blood']
    #     #
    #     # for trackName in trackNameList:
    #     #     uri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn, extraFileName=trackName)
    #     #     gSuiteTrack = GSuiteTrack(uri)
    #     #     outFn = gSuiteTrack.path
    #     #     ensurePathExists(outFn)
    #     #     line = ['chr1', '10', '200']
    #     #     with open(outFn, 'w') as outFile:
    #     #         outFile.write('\t'.join(line) + '\n')
    #     #
    #     #
    #     #
    #     #     #staticFile = HbGSuiteTrack.generateURI(trackName=[trackName])
    #     #     #from quick.util.CommonFunctions import ensurePathExists
    #     #
    #     #     #ensurePathExists(fn)
    #     #
    #     #
    #     #
    #     #     #trackType = TrackInfo(choices.genome, trackName).trackFormatName.lower()
    #     #
    #     #     trackType = 'segments'
    #     #     #hbUri = HbGSuiteTrack.generateURI(trackName=trackName)
    #     #
    #     #
    #     #     outGSuite.addTrack(GSuiteTrack(uri, title=''.join(trackName), trackType=trackType, genome=choices.genome))
    #     #
    #     # GSuiteComposer.composeToFile(outGSuite, cls.extraGalaxyFn['gene eGSuite'])
    #
    # # @staticmethod
    # # def getOutputFormat(choices):
    # #     return 'customhtml'

    @staticmethod
    def validateAndReturnErrors(choices):
        return None

    @classmethod
    def getExtraHistElements(cls, choices):
        return [HistElement('gene expression GSuite', 'gsuite')]


class rankingTFtracks2(GeneralGuiTool, UserBinMixin):
    GSUITE_FILE_OPTIONS_BOX_KEYS = ['gSuiteFirst']

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Make ranking for TFs using permutation test"

    @classmethod
    def getInputBoxNames(cls):
        return [
                   ('Select target track collection GSuite', 'gSuiteFirst')
               ] + cls.getInputBoxNamesForUserBinSelection()

    @staticmethod
    def getOptionsBoxGSuiteFirst():
        return GeneralGuiTool.getHistorySelectionElement('gsuite', 'txt', 'tabular')

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):

        targetGSuite = getGSuiteFromGalaxyTN(choices.gSuiteFirst)
        regSpec, binSpec = UserBinMixin.getRegsAndBinsSpec(choices)

        i = 0
        for x in targetGSuite.allTracks():
            if i == 0:
                analysisBins = GlobalBinSource(x.genome)
            #                 analysisBins = GalaxyInterface._getUserBinSource(regSpec, binSpec, x.genome)

        tracks = [Track(x.trackName) for x in targetGSuite.allTracks()]
        results = doAnalysis(AnalysisSpec(SumTrackPointsStat), analysisBins, tracks)
        print results

        # resultDict = results.getGlobalResult()

    @classmethod
    def getToolDescription(cls):
        return ''

    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'customhtml'


class mRNATool(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Show heatmap with correlation"

    @staticmethod
    def getInputBoxNames():
        return [
            ('Select matures', 'mature'),
            ('Select precursor', 'precursor'),
            ('Select files', 'files')
        ]

    @staticmethod
    def getOptionsBoxMature():
        return GeneralGuiTool.getHistorySelectionElement('txt')

    @staticmethod
    def getOptionsBoxPrecursor(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement('txt')

    @staticmethod
    def getOptionsBoxFiles(prevChoices):
        return ('__multihistory__', 'sam')

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        from quick.webtools.restricted.DianasTool2 import calculationPS

        print choices.files
        print choices.mature
        print choices.precursor

        cps = calculationPS(choices.files, choices.mature, choices.precursor)

        cps.calcRes()

    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''

        return None

    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'html'


class rankingTFtracks2(GeneralGuiTool, UserBinMixin):
    GSUITE_FILE_OPTIONS_BOX_KEYS = ['gSuiteFirst']

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Make ranking for TFs using permutation test"

    @classmethod
    def getInputBoxNames(cls):
        return [
                   ('Select target track collection GSuite', 'gSuiteFirst')
               ] + cls.getInputBoxNamesForUserBinSelection()

    @staticmethod
    def getOptionsBoxGSuiteFirst():
        return GeneralGuiTool.getHistorySelectionElement('gsuite', 'txt', 'tabular')

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):

        targetGSuite = getGSuiteFromGalaxyTN(choices.gSuiteFirst)
        regSpec, binSpec = UserBinMixin.getRegsAndBinsSpec(choices)

        i = 0
        for x in targetGSuite.allTracks():
            if i == 0:
                analysisBins = GlobalBinSource(x.genome)
            #                 analysisBins = GalaxyInterface._getUserBinSource(regSpec, binSpec, x.genome)

        tracks = [Track(x.trackName) for x in targetGSuite.allTracks()]
        results = doAnalysis(AnalysisSpec(SumTrackPointsStat), analysisBins, tracks)
        print results

        # resultDict = results.getGlobalResult()

    @classmethod
    def getToolDescription(cls):
        return ''

    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'customhtml'


class rankingTFtracks(GeneralGuiTool, UserBinMixin):
    GSUITE_FILE_OPTIONS_BOX_KEYS = ['gSuiteFirst', 'gSuiteSecond']

    MERGE_INTRA_OVERLAPS = 'Merge any overlapping points/segments within the same track'
    ALLOW_MULTIPLE_OVERLAP = 'Allow multiple overlapping points/segments within the same track'
    GSUITE_ALLOWED_FILE_FORMATS = [GSuiteConstants.PREPROCESSED]
    GSUITE_ALLOWED_LOCATIONS = [GSuiteConstants.LOCAL]
    GSUITE_ALLOWED_TRACK_TYPES = [GSuiteConstants.POINTS,
                                  GSuiteConstants.VALUED_POINTS,
                                  GSuiteConstants.SEGMENTS,
                                  GSuiteConstants.VALUED_SEGMENTS]

    GSUITE_DISALLOWED_GENOMES = [GSuiteConstants.UNKNOWN,
                                 GSuiteConstants.MULTIPLE]

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Make ranking for all possibilities"

    @classmethod
    def getInputBoxNames(cls):
        return [
                   ('Select target track collection GSuite', 'gSuiteFirst'),
                   ('Select reference track collection GSuite', 'gSuiteSecond'),
                   ('Select statistic', 'statistic'),
                   ('Select overlap handling', 'intraOverlap')
               ] + cls.getInputBoxNamesForUserBinSelection()

    @staticmethod
    def getOptionsBoxGSuiteFirst():
        return GeneralGuiTool.getHistorySelectionElement('gsuite', 'txt', 'tabular')

    @staticmethod
    def getOptionsBoxGSuiteSecond(prevChoices):  # Alternatively: getOptionsBox2()
        return GeneralGuiTool.getHistorySelectionElement('gsuite', 'txt', 'tabular')

    @staticmethod
    def getOptionsBoxStatistic(prevChoices):
        return [
            #                 STAT_OVERLAP_COUNT_BPS,
            #                 STAT_OVERLAP_RATIO,
            #                 STAT_FACTOR_OBSERVED_VS_EXPECTED,
            #                 STAT_COVERAGE_RATIO_VS_QUERY_TRACK,
            STAT_COVERAGE_RATIO_VS_REF_TRACK
        ]

    @staticmethod
    def getOptionsBoxIntraOverlap(prevChoices):
        return [rankingTFtracks.MERGE_INTRA_OVERLAPS,
                rankingTFtracks.ALLOW_MULTIPLE_OVERLAP]

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):

        targetGSuite = getGSuiteFromGalaxyTN(choices.gSuiteFirst)
        refGSuite = getGSuiteFromGalaxyTN(choices.gSuiteSecond)

        regSpec, binSpec = UserBinMixin.getRegsAndBinsSpec(choices)

        if choices.intraOverlap == rankingTFtracks.MERGE_INTRA_OVERLAPS:
            analysisDef = 'dummy -> RawOverlapStat'
        else:
            analysisDef = 'dummy [withOverlaps=yes] -> RawOverlapAllowSingleTrackOverlapsStat'
        results = OrderedDict()
        for targetTrack in targetGSuite.allTracks():
            targetTrackName = targetTrack.title
            for refTrack in refGSuite.allTracks():
                refTrackName = refTrack.title
                if targetTrack.trackName == refTrack.trackName:
                    result = rankingTFtracks.handleSameTrack(targetTrack.trackName, regSpec, binSpec,
                                                             targetGSuite.genome, galaxyFn)
                else:
                    result = GalaxyInterface.runManual([targetTrack.trackName, refTrack.trackName],
                                                       analysisDef, regSpec, binSpec,
                                                       targetGSuite.genome, galaxyFn,
                                                       printRunDescription=False,
                                                       printResults=False).getGlobalResult()
                if targetTrackName not in results:
                    results[targetTrackName] = OrderedDict()
                results[targetTrackName][refTrackName] = result

        stat = choices.statistic
        statIndex = STAT_LIST_INDEX[stat]
        title = 'Ranking for  (' + stat + ')'

        processedResults = []
        headerColumn = []
        for targetTrackName in targetGSuite.allTrackTitles():
            resultRowDict = processRawResults(results[targetTrackName])
            resultColumn = []
            headerColumn = []
            for refTrackName, statList in resultRowDict.iteritems():
                resultColumn.append(statList[statIndex])
                headerColumn.append(refTrackName)
            processedResults.append(resultColumn)

        transposedProcessedResults = [list(x) for x in zip(*processedResults)]

        input = targetGSuite.allTrackTitles()
        ref = transposedProcessedResults

        from itertools import combinations

        #         #header = ['Track', 'Track number', 'Ranking']
        #         #outputRes=[]
        #         writeFile = open(galaxyFn,'w')
        #         writeFile.write('Track' + '\t' + 'Track number'  + '\t' +  'Ranking'  + '\n')
        #
        #         for i in range(len(input) + 1):
        #             output =  map(list, combinations(input, i))
        #             for el in output:
        #                 if len(el)!=0:
        #                     outputResPart = 1
        #                     outputTrackNum = ''
        #                     outputHeaderPart = ''
        #                     for elN in range(0, len(el)):
        #                         outputHeaderPart += str(el[elN]) + ', '
        #                         outputTrackNum += str(input.index(el[elN])) + ', '
        #                         outputResPart *= ref[0][input.index(el[elN])]
        #                     #outputRes.append([outputHeaderPart, outputTrackNum, outputResPart])
        #                     writeFile.write(str(outputHeaderPart) + '\t' +  str(outputTrackNum) + '\t' + str(outputResPart) + '\n')

        outputHeaderPart1 = ''
        outputTrackNum1 = ''
        outputResPart1 = -100

        writeFile = open(galaxyFn, 'w')
        writeFile.write('Track' + '\t' + 'Track number' + '\t' + 'Ranking' + '\n')
        for i in range(len(input) + 1):
            output = map(list, combinations(input, i))
            for el in output:
                if len(el) != 0:
                    outputResPart = 1
                    outputTrackNum = ''
                    outputHeaderPart = ''
                    for elN in range(0, len(el)):
                        outputHeaderPart += str(el[elN]) + ', '
                        outputTrackNum += str(input.index(el[elN])) + ', '
                        outputResPart *= ref[0][input.index(el[elN])]

                    if outputResPart1 < outputResPart:
                        outputResPart1 = outputResPart
                        outputTrackNum1 = outputTrackNum
                        outputHeaderPart1 = outputHeaderPart

        # outputRes.append([outputHeaderPart1, outputTrackNum1, outputResPart1])
        writeFile.write(str(outputHeaderPart1) + '\t' + str(outputTrackNum1) + '\t' + str(outputResPart1) + '\n')

    #         htmlCore = HtmlCore()
    #         htmlCore.begin()
    #         htmlCore.header(title)
    #         htmlCore.divBegin('resultsDiv')
    #         htmlCore.tableHeader(header, sortable=True, tableId='resultsTable')
    #         for line in outputRes:
    #             htmlCore.tableLine(line)
    #         htmlCore.tableFooter()
    #         htmlCore.divEnd()

    # hicharts can't handle strings that contain ' or " as input for series names
    #         targetTrackNames = [x.replace('\'', '').replace('"','') for x in targetGSuite.allTrackTitles()]
    #         refTrackNames = [x.replace('\'', '').replace('"','') for x in refGSuite.allTrackTitles()]





    #         from quick.webtools.restricted.visualization.visualizationGraphs import visualizationGraphs
    #         vg = visualizationGraphs()
    #         result = vg.drawColumnChart(processedResults,
    #                       height=600,
    #                       yAxisTitle=stat,
    #                       categories=refTrackNames,
    #                       xAxisRotation=90,
    #                       seriesName=targetTrackNames,
    #                       shared=False,
    #                       titleText=title + ' plot',
    #                       overMouseAxisX=True,
    #                       overMouseLabelX = ' + this.value.substring(0, 10) +')
    #         htmlCore.line(vg.visualizeResults(result, htmlCore))
    #
    #         htmlCore.hideToggle(styleClass='debug')
    #         htmlCore.end()

    #         htmlCore.hideToggle(styleClass='debug')
    #         htmlCore.end()
    #
    #         print htmlCore

    @classmethod
    def getToolDescription(cls):
        return ''

    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'txt'

    @classmethod
    def handleSameTrack(cls, trackName, regSpec, binSpec, genome, galaxyFn):

        analysisSpec = AnalysisSpec(RawOverlapToSelfStat)
        analysisBins = GalaxyInterface._getUserBinSource(regSpec, binSpec, genome)

        return doAnalysis(analysisSpec, analysisBins, [Track(trackName)]).getGlobalResult()


class rankingTFtracks3(GeneralGuiTool, UserBinMixin):
    GSUITE_FILE_OPTIONS_BOX_KEYS = ['gSuiteFirst', 'gSuiteSecond']

    MERGE_INTRA_OVERLAPS = 'Merge any overlapping points/segments within the same track'
    ALLOW_MULTIPLE_OVERLAP = 'Allow multiple overlapping points/segments within the same track'
    GSUITE_ALLOWED_FILE_FORMATS = [GSuiteConstants.PREPROCESSED]
    GSUITE_ALLOWED_LOCATIONS = [GSuiteConstants.LOCAL]
    GSUITE_ALLOWED_TRACK_TYPES = [GSuiteConstants.POINTS,
                                  GSuiteConstants.VALUED_POINTS,
                                  GSuiteConstants.SEGMENTS,
                                  GSuiteConstants.VALUED_SEGMENTS]

    GSUITE_DISALLOWED_GENOMES = [GSuiteConstants.UNKNOWN,
                                 GSuiteConstants.MULTIPLE]

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Make TF bp overlapping"

    @classmethod
    def getInputBoxNames(cls):
        return [
                   ('Select target track collection GSuite', 'gSuiteFirst'),
                   ('Select reference track collection GSuite', 'gSuiteSecond'),
                   ('Select statistic', 'statistic'),
                   ('Select overlap handling', 'intraOverlap')
               ] + cls.getInputBoxNamesForUserBinSelection()

    @staticmethod
    def getOptionsBoxGSuiteFirst():
        return GeneralGuiTool.getHistorySelectionElement('gsuite', 'txt', 'tabular')

    @staticmethod
    def getOptionsBoxGSuiteSecond(prevChoices):  # Alternatively: getOptionsBox2()
        return GeneralGuiTool.getHistorySelectionElement('gsuite', 'txt', 'tabular')

    @staticmethod
    def getOptionsBoxStatistic(prevChoices):
        return [
            #                 STAT_OVERLAP_COUNT_BPS,
            #                 STAT_OVERLAP_RATIO,
            #                 STAT_FACTOR_OBSERVED_VS_EXPECTED,
            #                 STAT_COVERAGE_RATIO_VS_QUERY_TRACK,
            STAT_COVERAGE_RATIO_VS_REF_TRACK
        ]

    @staticmethod
    def getOptionsBoxIntraOverlap(prevChoices):
        return [rankingTFtracks.MERGE_INTRA_OVERLAPS,
                rankingTFtracks.ALLOW_MULTIPLE_OVERLAP]

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):

        targetGSuite = getGSuiteFromGalaxyTN(choices.gSuiteFirst)
        refGSuite = getGSuiteFromGalaxyTN(choices.gSuiteSecond)

        regSpec, binSpec = UserBinMixin.getRegsAndBinsSpec(choices)

        if choices.intraOverlap == rankingTFtracks.MERGE_INTRA_OVERLAPS:
            analysisDef = 'dummy -> RawOverlapStat'
        else:
            analysisDef = 'dummy [withOverlaps=yes] -> RawOverlapAllowSingleTrackOverlapsStat'
        results = OrderedDict()
        for targetTrack in targetGSuite.allTracks():
            targetTrackName = targetTrack.title
            for refTrack in refGSuite.allTracks():
                refTrackName = refTrack.title
                if targetTrack.trackName == refTrack.trackName:
                    result = rankingTFtracks.handleSameTrack(targetTrack.trackName, regSpec, binSpec,
                                                             targetGSuite.genome, galaxyFn)
                else:
                    result = GalaxyInterface.runManual([targetTrack.trackName, refTrack.trackName],
                                                       analysisDef, regSpec, binSpec,
                                                       targetGSuite.genome, galaxyFn,
                                                       printRunDescription=False,
                                                       printResults=False).getGlobalResult()
                if targetTrackName not in results:
                    results[targetTrackName] = OrderedDict()
                results[targetTrackName][refTrackName] = result

        stat = choices.statistic
        statIndex = STAT_LIST_INDEX[stat]
        title = 'Ranking for  (' + stat + ')'

        processedResults = []
        headerColumn = []
        for targetTrackName in targetGSuite.allTrackTitles():
            resultRowDict = processRawResults(results[targetTrackName])
            resultColumn = []
            headerColumn = []
            for refTrackName, statList in resultRowDict.iteritems():
                resultColumn.append(statList[statIndex])
                headerColumn.append(refTrackName)
            processedResults.append(resultColumn)

        transposedProcessedResults = [list(x) for x in zip(*processedResults)]

        input = targetGSuite.allTrackTitles()
        ref = transposedProcessedResults

        from itertools import combinations

        #         #header = ['Track', 'Track number', 'Ranking']
        #         #outputRes=[]
        #         writeFile = open(galaxyFn,'w')
        #         writeFile.write('Track' + '\t' + 'Track number'  + '\t' +  'Ranking'  + '\n')
        #
        #         for i in range(len(input) + 1):
        #             output =  map(list, combinations(input, i))
        #             for el in output:
        #                 if len(el)!=0:
        #                     outputResPart = 1
        #                     outputTrackNum = ''
        #                     outputHeaderPart = ''
        #                     for elN in range(0, len(el)):
        #                         outputHeaderPart += str(el[elN]) + ', '
        #                         outputTrackNum += str(input.index(el[elN])) + ', '
        #                         outputResPart *= ref[0][input.index(el[elN])]
        #                     #outputRes.append([outputHeaderPart, outputTrackNum, outputResPart])
        #                     writeFile.write(str(outputHeaderPart) + '\t' +  str(outputTrackNum) + '\t' + str(outputResPart) + '\n')

        outputHeaderPart1 = ''
        outputTrackNum1 = ''
        outputResPart1 = -100

        writeFile = open(galaxyFn, 'w')
        writeFile.write('Track' + '\t' + 'Track number' + '\t' + 'Ranking' + '\n')
        for i in range(len(input) + 1):
            output = map(list, combinations(input, i))
            for el in output:
                if len(el) != 0:
                    outputResPart = 1
                    outputTrackNum = ''
                    outputHeaderPart = ''
                    for elN in range(0, len(el)):
                        outputHeaderPart += str(el[elN]) + ', '
                        outputTrackNum += str(input.index(el[elN])) + ', '
                        outputResPart *= ref[0][input.index(el[elN])]

                    if outputResPart1 < outputResPart:
                        outputResPart1 = outputResPart
                        outputTrackNum1 = outputTrackNum
                        outputHeaderPart1 = outputHeaderPart

        # outputRes.append([outputHeaderPart1, outputTrackNum1, outputResPart1])
        writeFile.write(str(outputHeaderPart1) + '\t' + str(outputTrackNum1) + '\t' + str(outputResPart1) + '\n')

    #         htmlCore = HtmlCore()
    #         htmlCore.begin()
    #         htmlCore.header(title)
    #         htmlCore.divBegin('resultsDiv')
    #         htmlCore.tableHeader(header, sortable=True, tableId='resultsTable')
    #         for line in outputRes:
    #             htmlCore.tableLine(line)
    #         htmlCore.tableFooter()
    #         htmlCore.divEnd()

    # hicharts can't handle strings that contain ' or " as input for series names
    #         targetTrackNames = [x.replace('\'', '').replace('"','') for x in targetGSuite.allTrackTitles()]
    #         refTrackNames = [x.replace('\'', '').replace('"','') for x in refGSuite.allTrackTitles()]





    #         from quick.webtools.restricted.visualization.visualizationGraphs import visualizationGraphs
    #         vg = visualizationGraphs()
    #         result = vg.drawColumnChart(processedResults,
    #                       height=600,
    #                       yAxisTitle=stat,
    #                       categories=refTrackNames,
    #                       xAxisRotation=90,
    #                       seriesName=targetTrackNames,
    #                       shared=False,
    #                       titleText=title + ' plot',
    #                       overMouseAxisX=True,
    #                       overMouseLabelX = ' + this.value.substring(0, 10) +')
    #         htmlCore.line(vg.visualizeResults(result, htmlCore))
    #
    #         htmlCore.hideToggle(styleClass='debug')
    #         htmlCore.end()

    #         htmlCore.hideToggle(styleClass='debug')
    #         htmlCore.end()
    #
    #         print htmlCore

    @classmethod
    def getToolDescription(cls):
        return ''

    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'txt'

    @classmethod
    def handleSameTrack(cls, trackName, regSpec, binSpec, genome, galaxyFn):

        analysisSpec = AnalysisSpec(RawOverlapToSelfStat)
        analysisBins = GalaxyInterface._getUserBinSource(regSpec, binSpec, genome)

        return doAnalysis(analysisSpec, analysisBins, [Track(trackName)]).getGlobalResult()


class miRNAPrecursors(GeneralGuiTool, UserBinMixin):
    GSUITE_FILE_OPTIONS_BOX_KEYS = ['gSuiteFirst', 'gSuiteSecond']

    MERGE_INTRA_OVERLAPS = 'Merge any overlapping points/segments within the same track'
    ALLOW_MULTIPLE_OVERLAP = 'Allow multiple overlapping points/segments within the same track'
    GSUITE_ALLOWED_FILE_FORMATS = [GSuiteConstants.PREPROCESSED]
    GSUITE_ALLOWED_LOCATIONS = [GSuiteConstants.LOCAL]
    GSUITE_ALLOWED_TRACK_TYPES = [GSuiteConstants.POINTS,
                                  GSuiteConstants.VALUED_POINTS,
                                  GSuiteConstants.SEGMENTS,
                                  GSuiteConstants.VALUED_SEGMENTS]

    GSUITE_DISALLOWED_GENOMES = [GSuiteConstants.UNKNOWN,
                                 GSuiteConstants.MULTIPLE]

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Screen two track collections (precursors)"

    @classmethod
    def getInputBoxNames(cls):
        return [
                   ('Select target track collection GSuite', 'gSuiteFirst'),
                   ('Select reference track collection GSuite', 'gSuiteSecond'),
                   ('Select statistic', 'statistic'),
                   ('Select overlap handling', 'intraOverlap')
               ] + cls.getInputBoxNamesForUserBinSelection()

    @staticmethod
    def getOptionsBoxGSuiteFirst():
        return GeneralGuiTool.getHistorySelectionElement('gsuite', 'txt', 'tabular')

    @staticmethod
    def getOptionsBoxGSuiteSecond(prevChoices):  # Alternatively: getOptionsBox2()
        return GeneralGuiTool.getHistorySelectionElement('gsuite', 'txt', 'tabular')

    @staticmethod
    def getOptionsBoxStatistic(prevChoices):
        return [STAT_OVERLAP_COUNT_BPS,
                STAT_OVERLAP_RATIO,
                STAT_FACTOR_OBSERVED_VS_EXPECTED,
                STAT_COVERAGE_RATIO_VS_QUERY_TRACK,
                STAT_COVERAGE_RATIO_VS_REF_TRACK
                ]

    @staticmethod
    def getOptionsBoxIntraOverlap(prevChoices):
        return [miRNAPrecursors.MERGE_INTRA_OVERLAPS,
                miRNAPrecursors.ALLOW_MULTIPLE_OVERLAP]

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):

        targetGSuite = getGSuiteFromGalaxyTN(choices.gSuiteFirst)
        refGSuite = getGSuiteFromGalaxyTN(choices.gSuiteSecond)

        regSpec, binSpec = UserBinMixin.getRegsAndBinsSpec(choices)

        if choices.intraOverlap == miRNAPrecursors.MERGE_INTRA_OVERLAPS:
            analysisDef = 'dummy -> RawOverlapStat'
        else:
            analysisDef = 'dummy [withOverlaps=yes] -> RawOverlapAllowSingleTrackOverlapsStat'
        results = OrderedDict()
        for targetTrack in targetGSuite.allTracks():
            targetTrackName = targetTrack.title
            for refTrack in refGSuite.allTracks():
                refTrackName = refTrack.title
                if targetTrack.trackName == refTrack.trackName:
                    result = miRNAPrecursors.handleSameTrack(targetTrack.trackName, regSpec, binSpec,
                                                             targetGSuite.genome, galaxyFn)
                else:
                    result = GalaxyInterface.runManual([targetTrack.trackName, refTrack.trackName],
                                                       analysisDef, regSpec, binSpec,
                                                       targetGSuite.genome, galaxyFn,
                                                       printRunDescription=False,
                                                       printResults=False).getGlobalResult()
                if targetTrackName not in results:
                    results[targetTrackName] = OrderedDict()
                results[targetTrackName][refTrackName] = result

        stat = choices.statistic
        statIndex = STAT_LIST_INDEX[stat]
        title = 'Screening track collections  (' + stat + ')'

        processedResults = []
        headerColumn = []
        for targetTrackName in targetGSuite.allTrackTitles():
            resultRowDict = processRawResults(results[targetTrackName])
            resultColumn = []
            headerColumn = []
            for refTrackName, statList in resultRowDict.iteritems():
                resultColumn.append(statList[statIndex])
                headerColumn.append(refTrackName)
            processedResults.append(resultColumn)

        transposedProcessedResults = [list(x) for x in zip(*processedResults)]

        tableHeader = ['Track names'] + targetGSuite.allTrackTitles()
        htmlCore = HtmlCore()
        htmlCore.begin()
        htmlCore.header(title)
        htmlCore.divBegin('resultsDiv')
        htmlCore.tableHeader(tableHeader, sortable=True, tableId='resultsTable')
        for i, row in enumerate(transposedProcessedResults):
            line = [headerColumn[i]] + [strWithStdFormatting(x) for x in row]
            htmlCore.tableLine(line)
        htmlCore.tableFooter()
        htmlCore.divEnd()

        # hicharts can't handle strings that contain ' or " as input for series names
        targetTrackNames = [x.replace('\'', '').replace('"', '') for x in targetGSuite.allTrackTitles()]
        refTrackNames = [x.replace('\'', '').replace('"', '') for x in refGSuite.allTrackTitles()]

        '''
        addColumnPlotToHtmlCore(htmlCore, targetTrackNames, refTrackNames,
                                stat, title + ' plot',
                                processedResults, xAxisRotation = -45, height=800)
        '''
        '''
        addPlotToHtmlCore(htmlCore, targetTrackNames, refTrackNames,
                                stat, title + ' plot',
                                processedResults, xAxisRotation = -45, height=400)
        '''

        from quick.webtools.restricted.visualization.visualizationGraphs import visualizationGraphs
        vg = visualizationGraphs()
        result = vg.drawColumnChart(processedResults,
                                    height=600,
                                    yAxisTitle=stat,
                                    categories=refTrackNames,
                                    xAxisRotation=90,
                                    seriesName=targetTrackNames,
                                    shared=False,
                                    titleText=title + ' plot',
                                    overMouseAxisX=True,
                                    overMouseLabelX=' + this.value.substring(0, 10) +')
        htmlCore.line(vg.visualizeResults(result, htmlCore))

        htmlCore.hideToggle(styleClass='debug')
        htmlCore.end()

        print htmlCore

    @classmethod
    def getToolDescription(cls):
        core = HtmlCore()

        core.paragraph('The tool provides screening of two track collections '
                       '(GSuite files) against each other. The input for the tool are '
                       'two GSuite files, a target and a reference one, that contain '
                       'one or more tracks each.')

        core.paragraph('To run the tool, follow these steps:')

        core.orderedList(['Select two track collections (GSuite files) from history.'
                          'Select the desired statistic that you want to be calculated '
                          'for each track pair.'
                          'Select the genome region for the anaysis',
                          'Click "Execute"'])

        core.paragraph('The results are presented in a sortable table and an interactive chart.')

        cls._addGSuiteFileDescription(core,
                                      allowedLocations=cls.GSUITE_ALLOWED_LOCATIONS,
                                      allowedFileFormats=cls.GSUITE_ALLOWED_FILE_FORMATS,
                                      allowedTrackTypes=cls.GSUITE_ALLOWED_TRACK_TYPES,
                                      disallowedGenomes=cls.GSUITE_DISALLOWED_GENOMES)

        return str(core)

    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'customhtml'

    @classmethod
    def handleSameTrack(cls, trackName, regSpec, binSpec, genome, galaxyFn):

        analysisSpec = AnalysisSpec(RawOverlapToSelfStat)
        analysisBins = GalaxyInterface._getUserBinSource(regSpec, binSpec, genome)

        return doAnalysis(analysisSpec, analysisBins, [Track(trackName)]).getGlobalResult()


class createRainfallPlotWithRegions(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Create density of distribution [RP manuscript tool]"

    @staticmethod
    def getInputBoxNames():
        return [
            ('Select gsuite with data', 'gsuite'),
            ('Select bed file with regions', 'bedRegions'),
            # ('Select type of plotting', 'multiPlot'),
            # ('Select scale for bps value', 'scale'),
            # ('Select bps (10000)', 'bps')
        ]

    @staticmethod
    def getOptionsBoxGsuite():
        return '__history__', 'gsuite'

    @staticmethod
    def getOptionsBoxBedRegions(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement('bed')

    # @staticmethod
    # def getOptionsBoxMultiPlot(prevChoices):
    #     return ['Single', 'Multi']
    #
    # @staticmethod
    # def getOptionsBoxScale(prevChoices):
    #     return ['Linear', 'Log']
    #
    # @staticmethod
    # def getOptionsBoxBps(prevChoices):
    #     return '10000'

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        gsuite = getGSuiteFromGalaxyTN(choices.gsuite)
        gSuiteTracksNum = gsuite.numTracks()

        bedFile = ExternalTrackManager.extractFnFromGalaxyTN(choices.bedRegions.split(':'))
        with open(bedFile, 'r') as f:
            lines = f.readlines()

        bedData = OrderedDict()
        for l in lines:
            l = l.strip('\n').split('\t')
            strL = l[0] + '-' + l[1] + '-' + l[2]
            if not strL in bedData.keys():
                bedData[strL] = []

        # multiPlot = choices.multiPlot
        # scale = choices.scale
        # bps = int(choices.bps)

        # print 'start'

        chrOrder, chrLength = createRainfallPlot.sortChrDict(GenomeInfo.getStdChrLengthDict(gsuite.genome))

        chrList = {}
        chrStPos = []
        sumChr = 0
        for chrLen in chrOrder.values():
            sumChr += chrLen
            chrStPos.append(sumChr)

        dataDict, dataDictLine, elementOrder, listResCopy, newDictRegions = createRainfallPlotWithRegions.countMutations(
            gsuite, chrLength, bedData)

        vg = visualizationGraphs()

        tName = gsuite.allTrackTitles()

        seriesType = []
        newSeriesNameRes = []
        newSeriesNameResOE = []
        yAxisMultiVal = []
        for el in elementOrder:
            newSeriesNameRes.append(tName[el])
            seriesType.append('scatter')
            yAxisMultiVal.append(0)
            newSeriesNameResOE.append(tName[el])

        for el in elementOrder:
            newSeriesNameRes.append(str(tName[el]) + '-- point')
            seriesType.append('line')
            yAxisMultiVal.append(1)
            newSeriesNameResOE.append(str(tName[el]) + '-- distribution')

        res = ''

        uniformDictList = OrderedDict()  # expected values
        observedDictList = OrderedDict()  # observed values
        xAxisMultiVal = OrderedDict()
        seriesNameRegionUDL = OrderedDict()
        seriesNameRegionODL = OrderedDict()
        seriesNameRegion = OrderedDict()
        titleRegion = bedData.keys()

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
                    createRainfallPlotWithRegions.countPoissonDistribution(numMut, intervalLen))
                seriesNameRegionUDL[regChr].append(str(tName[regKey]) + ' - ' + 'expected')

                observedDictList[regChr].append(createRainfallPlotWithRegions.countHist(regList))
                seriesNameRegionODL[regChr].append(
                    str(tName[regKey]) + ' - ' + 'observed dist num:' + str(len(regList)))

        for elK in uniformDictList.keys():

            ww = elK.split('-')
            nELK = str(elK) + ' region size:  ' + str(int(ww[2]) - int(ww[1]))

            seriesNameRegion[elK] = seriesNameRegionUDL[elK] + seriesNameRegionODL[elK]

            # remove the list which are empty



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
                    udl = np.delete(udl, indexListEmpty).tolist()

                    odl = np.delete(odl, indexListEmpty).tolist()

                    # double number of indexes (because of udl + odl)
                    indexListEmpty = indexListEmpty + [n + len(uniformDictList[elK]) for n in indexListEmpty]

                    snl = np.delete(snl, indexListEmpty).tolist()

                res += vg.drawLineChart(
                    udl + odl,
                    # categories=newResBinSizeListSorted.keys(),
                    # seriesName = ['all points', 'all point bin avg'],
                    seriesName=snl,
                    height=300,
                    titleText=nELK,
                    yAxisTitle='[log10]',
                    # plotLines = chrLength.values(),
                    # plotLinesName = chrLength.keys()
                )

                res += '<div style="clear:both;"> </div>'

        htmlCore = HtmlCore()
        htmlCore.begin()
        htmlCore.line(res)
        htmlCore.end()
        htmlCore.hideToggle(styleClass='debug')
        print htmlCore

    @classmethod
    def countMutations(cls, gsuite, chrLength, bedData):

        # print 'chrLnegth' + str(chrLength)
        # print 'bps' + str(bps)

        dataDict = OrderedDict()
        dataDictLine = OrderedDict()

        elementOrder = []

        listOfBinSumPerTrack = []

        # countAverageDistance = {}
        # countAverageDistance['distance'] = 0
        # countAverageDistance['elNum'] = 0
        # countAverageDistancePerTrack = {}



        # problem z powtarzalnoscia regionow ... naprawic to

        newDictRegions = OrderedDict()
        tracRegions = 0
        for trackN in gsuite.allTrackTitles():
            if not tracRegions in newDictRegions.keys():
                newDictRegions[tracRegions] = OrderedDict()
            for kit in bedData.keys():
                if not kit in newDictRegions[tracRegions].keys():
                    newDictRegions[tracRegions][kit] = []
            tracRegions += 1

        tracRegions = 0
        for track in gsuite.allTrackTitles():

            # count one track
            gSuiteTrack = gsuite.getTrackFromTitle(track)
            trackName = track

            dataDict[trackName] = OrderedDict()
            dataDictLine[trackName] = OrderedDict()

            # read from file
            newDict = {}
            with open(gSuiteTrack.path, 'r') as f:
                i = 0
                for x in f.readlines():
                    el = x.strip('\n').split('\t')
                    if len(el) >= 2:
                        try:
                            st = int(el[1])
                            if not el[0] in newDict:
                                newDict[el[0]] = []
                            newDict[el[0]].append([el[0], st, int(el[2])])
                        except:
                            pass
                i += 1

            # sort file according to start position
            newDict2 = OrderedDict()
            for key, it in chrLength.items():
                if key in newDict:
                    newDict2[key] = sorted(newDict[key], key=lambda x: x[1])

            for key, it in newDict2.items():
                if i == 0:
                    chr = key
                i = 0
                prevEnd = 0
                label = 0

                for el in it:

                    if len(el) >= 2:

                        if not int(el[1]) in dataDictLine[trackName]:
                            dataDictLine[trackName][int(el[1])] = 1
                        start = int(el[1])
                        if prevEnd != 0:
                            if not label in dataDict[trackName]:
                                dataDict[trackName][label] = OrderedDict()
                                dataDict[trackName][label]['val'] = 0
                                dataDict[trackName][label]['tot'] = 0

                            for elReg in newDictRegions[tracRegions].keys():

                                chrReg = elReg.split('-')[0]
                                startReg = elReg.split('-')[1]
                                endReg = elReg.split('-')[2]

                                if prevEnd > int(startReg) and start <= int(endReg) and chrReg == key:
                                    # print tracRegions
                                    # print elReg
                                    # print 'was'
                                    newDictRegions[tracRegions][elReg].append(start - prevEnd)
                                    break

                            # print str(trackName) + ' chrReg ' + str(elReg)   +   ' ' + str(newDictRegions)


                            if start - prevEnd != 0:
                                dataDict[trackName][label]['val'] += math.log(start - prevEnd, 10)
                            else:
                                dataDict[trackName][label]['val'] += start - prevEnd
                                # countAverageDistance['distance'] += start - prevEnd

                            dataDict[trackName][label]['tot'] += 1

                        label = int(el[1]) + int(chrLength[el[0]])

                        prevEnd = int(el[1])
                        i += 1

            elementOrder.append(i)

            tracRegions += 1

        listResCopy = []
        for key0, it0 in dataDict.iteritems():
            listResPart = []
            for key2 in sorted(it0):
                listResPart.append([key2, it0[key2]['val']])
            listResCopy.append(listResPart)

        elementOrder = sorted(range(len(elementOrder)), key=lambda k: elementOrder[k])

        # lengthOfLastChromosome = GenomeInfo.getChrLen(gsuite.genome, chrLength.keys()[-1])

        # howManyIntervalsPerBin = int((chrLength.values()[-1] + lengthOfLastChromosome) / bps) + 1

        # listOfBinSumPerTrack = []
        # for interval in range(0, howManyIntervalsPerBin):
        #     listOfBin = (interval * bps, (interval + 1) * bps)
        #     listOfBinSumPerTrack.append(listOfBin)
        #
        #     newResBinSizeListSum = {}
        #
        #
        # listDataCountPerBin = []
        # for el in listResCopy:
        #
        #
        #     data = filter(None, [filter(lambda l: t[0] <= int(l[0]) < t[1], el) for t in listOfBinSumPerTrack])
        #
        #
        #     listData = []
        #
        #     for d in data:
        #
        #         countD = int(d[0][0] / bps) * bps + bps / 2
        #         lenD = len(d)
        #
        #         listData.append([countD, lenD])
        #
        #         if not countD in newResBinSizeListSum.keys():
        #             newResBinSizeListSum[countD] = lenD
        #         else:
        #             newResBinSizeListSum[countD] += lenD
        #
        #     listDataCountPerBin.append(listData)


        return dataDict, dataDictLine, elementOrder, listResCopy, newDictRegions

    @classmethod
    def countPoissonDistribution(cls, numMut, intervalLen):
        # rCode = 'dataRPois <- function(vec) {hist(rpois(vec[1], vec[2]))}'
        # dd = robjects.FloatVector(
        #     [countAverageDistance['elNum'], countAverageDistance['distance'] / countAverageDistance['elNum']])
        # dataFromRPois = r(rCode)(dd)

        # rCode = 'dataRPois <- function(vec) {' \
        #         'data=sort(runif(vec[1], 0, vec[2]));' \
        #         'histData=data[2:vec[1]]-data[1:vec[1]-1];' \
        #         'hist(histData);' \
        #         '}'

        poissonListMean = []

        if numMut != 0:

            from proto.RSetup import r, robjects
            # number of mutation/ length of interval
            rCode = 'dataRPois <- function(vec) {' \
                    'vecNew = log10(rexp(10000, vec[1]/vec[2])); ' \
                    'data=hist(vecNew, prob=T)' \
                    '}'
            dd = robjects.FloatVector(
                [numMut, intervalLen])
            dataFromRPois = r(rCode)(dd)

            # print '<br >mean' + str(countAverageDistance['distance']/countAverageDistance['elNum'])
            # print '<br >counts' + str(countAverageDistance['elNum'])
            #
            # print '<br >dataFromRPois' + str(list(dataFromRPois.rx2('counts')))
            # print '<br >dataFromRPois' + str(list(dataFromRPois.rx2('breaks')))

            # distance (time) - gamma, exp
            # event(number of events) - poisson

            breaks = list(dataFromRPois.rx2('breaks'))
            counts = list(dataFromRPois.rx2('density'))
            for elN in range(0, len(counts)):
                # if scale == 'Log':
                #     if counts[elN] != 0:
                #         counts[elN] = math.log(counts[elN], 10)
                #     else:
                #         counts[elN] = 0


                br = (breaks[elN] + breaks[elN + 1]) / 2

                # brLog = math.pow(10, br)



                ct = counts[elN]

                # if br == 0:
                #     br = 0
                # else:
                #     br = math.log(br, 10)

                # if ct == 0:
                #     ct = 0
                # else:
                #     ct = math.log(ct, 10)


                poissonListMean.append([br, ct])

        # print 'poissonListMean' + str(poissonListMean)


        return poissonListMean

    @classmethod
    def countHist(cls, newResList):

        poissonListMean = []
        if len(newResList) != 0:

            from proto.RSetup import r, robjects

            newResListLog = []
            for el in newResList:
                if el == 0:
                    newResListLog.append(0)
                else:
                    newResListLog.append(math.log(el, 10))

            # , breaks=ceiling(max(vec)) - floor((min(vec)))
            rCode = 'dataRPois <- function(vec) {' \
                    'hist(vec, prob=T)' \
                    '}'
            dd = robjects.FloatVector(newResListLog)
            dataFromRPois = r(rCode)(dd)

            breaks = list(dataFromRPois.rx2('breaks'))

            try:
                counts = list(dataFromRPois.rx2('density'))
            except:
                counts = [dataFromRPois.rx2('density')]

            for elN in range(0, len(counts)):
                br = (breaks[elN] + breaks[elN + 1]) / 2

                # br = math.pow(10, br)

                ct = counts[elN]

                # if br == 0:
                #     br = 0
                # else:
                #     br = math.log(br, 10)

                # if ct ==0:
                #     ct = 0
                # else:
                #     ct = math.log(ct, 10)


                poissonListMean.append([br, ct])

        # print 'histListMean' + str(poissonListMean)


        return poissonListMean

    @staticmethod
    def getOutputFormat(choices):
        return 'customhtml'


class createRainfallPlotWithRegionsGsuite(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Create distribution for rainfall plots (using gsuite)"

    @staticmethod
    def getInputBoxNames():
        return [
            ('Select gsuite with data', 'gsuite'),
            ('Select gsuite with regions', 'gsuiteRegions'),
            ('Select type of plotting', 'multiPlot'),
            ('Select scale for bps value', 'scale'),
            ('Select bps (10000)', 'bps')
        ]

    @staticmethod
    def getOptionsBoxGsuite():
        return '__history__', 'gsuite'

    @staticmethod
    def getOptionsBoxGsuiteRegions(prevChoices):
        return '__history__', 'gsuite'

    @staticmethod
    def getOptionsBoxMultiPlot(prevChoices):
        return ['Single', 'Multi']

    @staticmethod
    def getOptionsBoxScale(prevChoices):
        return ['Linear', 'Log']

    @staticmethod
    def getOptionsBoxBps(prevChoices):
        return '10000'

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        gsuite = getGSuiteFromGalaxyTN(choices.gsuite)
        gSuiteTracksNum = gsuite.numTracks()

        gsuiteRegions = getGSuiteFromGalaxyTN(choices.gsuiteRegions)
        gsuiteRegionsTracksNum = gsuiteRegions.numTracks()

        multiPlot = choices.multiPlot
        scale = choices.scale
        bps = int(choices.bps)

        print 'start'

        chrOrder, chrLength = createRainfallPlot.sortChrDict(GenomeInfo.getStdChrLengthDict(gsuite.genome))

        chrList = {}
        chrStPos = []
        sumChr = 0
        for chrLen in chrOrder.values():
            sumChr += chrLen
            chrStPos.append(sumChr)

        dataDict, dataDictLine, elementOrder, listResCopy, listDataCountPerBin, newResBinSizeListSum, newDictRegions = createRainfallPlotWithRegionsGsuite.countMutations(
            gsuite, chrLength, bps, gsuiteRegions)

        vg = visualizationGraphs()

        tName = gsuite.allTrackTitles()

        seriesType = []
        newSeriesNameRes = []
        newSeriesNameResOE = []
        yAxisMultiVal = []
        for el in elementOrder:
            newSeriesNameRes.append(tName[el])
            seriesType.append('scatter')
            yAxisMultiVal.append(0)
            newSeriesNameResOE.append(tName[el])

        for el in elementOrder:
            newSeriesNameRes.append(str(tName[el]) + '-- point')
            seriesType.append('line')
            yAxisMultiVal.append(1)
            newSeriesNameResOE.append(str(tName[el]) + '-- distribution')

        #
        # newResList = []
        # newResBinSizeList = []
        # for el in elementOrder:
        #     newResList.append(listResCopy[el])
        #     newResBinSizeList.append(listDataCountPerBin[el])
        #
        #
        res = ''
        #
        # newResBinSizeListSorted = OrderedDict(sorted(newResBinSizeListSum.items()))
        #
        # # print 'newResBinSizeListSorted' + str(newResBinSizeListSorted)
        #
        #
        #
        # newResBinSizeListSortedList = []
        # for key, value in newResBinSizeListSorted.iteritems():
        #     newResBinSizeListSortedList.append([key, value])



        # print 'newResList' + str(newResList)
        #
        # print 'newResBinSizeListSortedList' + str(newResBinSizeListSortedList)
        #
        # print len(newSeriesNameRes)
        # print len(newResList)
        #

        for regKey in newDictRegions.keys():
            # counting uniform distribution
            uniformList = []  # expected values
            observedList = []  # observed values
            xAxisMultiVal = []

            seriesNameRegion = []
            uo = 0
            for regChr, regList in newDictRegions[regKey].items():
                numMut = len(regList)

                stChr = regChr.split('-')[1]
                endChr = regChr.split('-')[2]
                intervalLen = int(endChr) - int(stChr)

                uniformList.append(createRainfallPlotWithRegionsGsuite.countPoissonDistribution(numMut, intervalLen))
                xAxisMultiVal.append(uo)
                seriesNameRegion.append(str(regChr) + ' - ' + 'expected')

                observedList.append(createRainfallPlotWithRegionsGsuite.countHist(regList))
                xAxisMultiVal.append(uo)
                seriesNameRegion.append(str(regChr) + ' - ' + 'observed')

                uo += 1

            print xAxisMultiVal

            res += vg.drawLineChartMultiXAxis(
                uniformList + observedList,
                # categories=newResBinSizeListSorted.keys(),
                # seriesName = ['all points', 'all point bin avg'],
                seriesName=seriesNameRegion,
                height=300,
                xAxisTitle='',
                yAxisTitle='',
                minY=0,
                xAxisMulti=xAxisMultiVal,
                # plotLines = chrLength.values(),
                # plotLinesName = chrLength.keys()
            )

            res += '<div style="clear:both;"> </div>'

        # for nsnr in range(0, len(newSeriesNameRes)/2):
        #     numMut = len(newResList[nsnr])
        #     chrHowMany = newResList[nsnr][len(newResList[nsnr]) - 1][0]
        #     uniformList.append(createRainfallPlotWithRegions.countPoissonDistribution(numMut, chrHowMany))
        #     observedList.append(createRainfallPlotWithRegions.countHist(newResList[nsnr]))


        # print 'mutation'
        # print newResList
        # print observedList




        # res += vg.drawLineChart(
        #     [newResBinSizeListSortedList],
        #     # categories=newResBinSizeListSorted.keys(),
        #     # seriesName = ['all points', 'all point bin avg'],
        #     seriesName=['sum per bin'],
        #     height=300,
        #     xAxisTitle='chr start pos',
        #     yAxisTitle='points per bin (' + str(scale) + ')',
        #     minY=0,
        #     plotLines=chrLength.values(),
        #     plotLinesName=chrLength.keys()
        # )

        # res += '<div style="clear:both;"> </div>'
        #
        # res += vg.drawLineChartMultiYAxis(
        #     newResList + newResBinSizeList,
        #     seriesName=newSeriesNameRes,
        #     seriesType=seriesType,
        #     height=500,
        #     reversed=False,
        #     markerRadius=1,
        #     xAxisTitle='chr start pos',
        #     yAxisTitle=['distance(log10)', 'points per bin (' + str(scale) + ')'],
        #     yAxisMulti=yAxisMultiVal,
        #     minY=0,
        #     plotLines=chrLength.values(),
        #     plotLinesName=chrLength.keys()
        # )

        res += '<div style="clear:both;"> </div>'

        htmlCore = HtmlCore()
        htmlCore.begin()
        htmlCore.line('Bin size: ' + str(bps))
        htmlCore.line(res)
        htmlCore.end()
        htmlCore.hideToggle(styleClass='debug')
        print htmlCore

    @classmethod
    def countMutations(cls, gsuite, chrLength, bps, gsuiteRegions):

        # print 'chrLnegth' + str(chrLength)
        # print 'bps' + str(bps)

        dataDict = OrderedDict()
        dataDictLine = OrderedDict()

        elementOrder = []

        listOfBinSumPerTrack = []

        # countAverageDistance = {}
        # countAverageDistance['distance'] = 0
        # countAverageDistance['elNum'] = 0
        # countAverageDistancePerTrack = {}

        tracRegions = 0
        newDictRegions = OrderedDict()
        for track in gsuiteRegions.allTrackTitles():
            gSuiteTrack = gsuiteRegions.getTrackFromTitle(track)
            # trackName = track
            trackName = tracRegions
            with open(gSuiteTrack.path, 'r') as f:
                i = 0
                for x in f.readlines():
                    el = x.strip('\n').split('\t')
                    if len(el) >= 2:
                        if not trackName in newDictRegions:
                            newDictRegions[trackName] = OrderedDict()
                        if (el[1]).isdigit() == True:
                            newDictRegions[trackName][el[0] + '-' + str(int(el[1])) + '-' + str(int(el[2]))] = []
                i += 1
            tracRegions += 1

        tracRegions = 0
        for track in gsuite.allTrackTitles():

            # count one track
            gSuiteTrack = gsuite.getTrackFromTitle(track)
            trackName = track

            dataDict[trackName] = OrderedDict()
            dataDictLine[trackName] = OrderedDict()

            # read from file
            newDict = {}
            with open(gSuiteTrack.path, 'r') as f:
                i = 0
                for x in f.readlines():
                    el = x.strip('\n').split('\t')
                    if len(el) >= 2:
                        if not el[0] in newDict:
                            newDict[el[0]] = []
                        newDict[el[0]].append([el[0], int(el[1]), int(el[2])])
                i += 1

            # sort file according to start position
            newDict2 = OrderedDict()
            for key, it in chrLength.items():
                if key in newDict:
                    newDict2[key] = sorted(newDict[key], key=lambda x: x[1])

            for key, it in newDict2.items():
                if i == 0:
                    chr = key
                i = 0
                prevEnd = 0
                label = 0

                for el in it:

                    if len(el) >= 2:

                        if not int(el[1]) in dataDictLine[trackName]:
                            dataDictLine[trackName][int(el[1])] = 1
                        start = int(el[1])
                        if prevEnd != 0:
                            if not label in dataDict[trackName]:
                                dataDict[trackName][label] = OrderedDict()
                                dataDict[trackName][label]['val'] = 0
                                dataDict[trackName][label]['tot'] = 0

                            for elReg in newDictRegions[tracRegions].keys():

                                chrReg = elReg.split('-')[0]
                                startReg = elReg.split('-')[1]
                                endReg = elReg.split('-')[2]

                                if prevEnd > int(startReg) and start <= int(endReg) and chrReg == key:
                                    newDictRegions[tracRegions][elReg].append(start - prevEnd)
                                    # print newDictRegions[tracRegions][elReg]
                                    break

                            if start - prevEnd != 0:
                                dataDict[trackName][label]['val'] += math.log(start - prevEnd, 10)
                            else:
                                dataDict[trackName][label]['val'] += start - prevEnd
                                # countAverageDistance['distance'] += start - prevEnd

                            dataDict[trackName][label]['tot'] += 1

                        label = int(el[1]) + int(chrLength[el[0]])

                        prevEnd = int(el[1])
                        i += 1

            elementOrder.append(i)

            # # #endPosition of the first element, val-which is startPosition of the second minus end Position of the first one,
            # print 'dataDict'
            # print dataDict
            # print '<br><br><br><br>'
            #
            # #endPosition of the first element, tot
            # print 'dataDictLine'
            # print dataDictLine
            #
            # print '<br><br><br><br>'
            # print 'elementOrder'
            # print elementOrder

            tracRegions += 1

        # print dataDict

        # print newDictRegions

        # for regKey in newDictRegions.keys():
        #     for regChr, regList in newDictRegions[regKey].items():
        #         print regChr
        #         print regList


        listResCopy = []
        for key0, it0 in dataDict.iteritems():
            listResPart = []
            for key2 in sorted(it0):
                listResPart.append([key2, it0[key2]['val']])
            listResCopy.append(listResPart)

        elementOrder = sorted(range(len(elementOrder)), key=lambda k: elementOrder[k])

        # print '<br><br><br><br>'
        # print 'listResCopy'
        # print listResCopy
        #
        # print '<br><br><br><br>'
        # print 'elementOrder'
        # print elementOrder


        lengthOfLastChromosome = GenomeInfo.getChrLen(gsuite.genome, chrLength.keys()[-1])

        howManyIntervalsPerBin = int((chrLength.values()[-1] + lengthOfLastChromosome) / bps) + 1

        listOfBinSumPerTrack = []
        for interval in range(0, howManyIntervalsPerBin):
            listOfBin = (interval * bps, (interval + 1) * bps)
            listOfBinSumPerTrack.append(listOfBin)

            newResBinSizeListSum = {}

        listDataCountPerBin = []
        # for el in listResCopy:
        #
        #
        #     data = filter(None, [filter(lambda l: t[0] <= int(l[0]) < t[1], el) for t in listOfBinSumPerTrack])
        #
        #
        #     listData = []
        #
        #     for d in data:
        #
        #         countD = int(d[0][0] / bps) * bps + bps / 2
        #         lenD = len(d)
        #
        #         listData.append([countD, lenD])
        #
        #         if not countD in newResBinSizeListSum.keys():
        #             newResBinSizeListSum[countD] = lenD
        #         else:
        #             newResBinSizeListSum[countD] += lenD
        #
        #     listDataCountPerBin.append(listData)


        return dataDict, dataDictLine, elementOrder, listResCopy, listDataCountPerBin, newResBinSizeListSum, newDictRegions

    @classmethod
    def countPoissonDistribution(cls, numMut, intervalLen):
        from proto.RSetup import r, robjects
        # rCode = 'dataRPois <- function(vec) {hist(rpois(vec[1], vec[2]))}'
        # dd = robjects.FloatVector(
        #     [countAverageDistance['elNum'], countAverageDistance['distance'] / countAverageDistance['elNum']])
        # dataFromRPois = r(rCode)(dd)

        # rCode = 'dataRPois <- function(vec) {' \
        #         'data=sort(runif(vec[1], 0, vec[2]));' \
        #         'histData=data[2:vec[1]]-data[1:vec[1]-1];' \
        #         'hist(histData);' \
        #         '}'

        # number of mutation/ length of interval
        rCode = 'dataRPois <- function(vec) {' \
                'data=hist(rexp(10000, vec[1]/vec[2]), prob=T)' \
                '}'
        dd = robjects.FloatVector(
            [numMut, intervalLen])
        dataFromRPois = r(rCode)(dd)

        # print '<br >mean' + str(countAverageDistance['distance']/countAverageDistance['elNum'])
        # print '<br >counts' + str(countAverageDistance['elNum'])
        #
        # print '<br >dataFromRPois' + str(list(dataFromRPois.rx2('counts')))
        # print '<br >dataFromRPois' + str(list(dataFromRPois.rx2('breaks')))

        # distance (time) - gamma, exp
        # event(number of events) - poisson

        poissonListMean = []
        breaks = list(dataFromRPois.rx2('breaks'))
        counts = list(dataFromRPois.rx2('density'))
        for elN in range(0, len(counts)):
            # if scale == 'Log':
            #     if counts[elN] != 0:
            #         counts[elN] = math.log(counts[elN], 10)
            #     else:
            #         counts[elN] = 0
            poissonListMean.append([(breaks[elN] + breaks[elN + 1]) / 2, counts[elN]])

            # print 'poissonListMean' + str(poissonListMean)

        return poissonListMean

    @classmethod
    def countHist(cls, newResList):
        from proto.RSetup import r, robjects

        rCode = 'dataRPois <- function(vec) {' \
                'hist(vec, prob=T)' \
                '}'
        dd = robjects.FloatVector(newResList)
        dataFromRPois = r(rCode)(dd)

        poissonListMean = []
        breaks = list(dataFromRPois.rx2('breaks'))
        counts = list(dataFromRPois.rx2('density'))
        for elN in range(0, len(counts)):
            poissonListMean.append([(breaks[elN] + breaks[elN + 1]) / 2, counts[elN]])

        return poissonListMean

    @staticmethod
    def getOutputFormat(choices):
        return 'customhtml'


class createRainfallPlotWithBinRegions(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Create other version of rainfall plot [RP manuscript2 tool]"

    @staticmethod
    def getInputBoxNames():
        return [
            ('Select gsuite', 'gsuite'),
            ('Select type of plotting', 'multiPlot'),
            ('Select scale for bps value', 'scale'),
            ('Select bps (100000)', 'bps')
        ]

    @staticmethod
    def getOptionsBoxGsuite():
        return '__history__', 'gsuite'

    @staticmethod
    def getOptionsBoxMultiPlot(prevChoices):
        return ['Single']

    @staticmethod
    def getOptionsBoxScale(prevChoices):
        return ['Linear', 'Log']

    @staticmethod
    def getOptionsBoxBps(prevChoices):
        return '100000'

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        gsuite = getGSuiteFromGalaxyTN(choices.gsuite)

        gSuiteTracksNum = gsuite.numTracks()

        multiPlot = choices.multiPlot
        scale = choices.scale
        bps = int(choices.bps)

        chrOrder, chrLength = createRainfallPlotWithBinRegions.sortChrDict(
            GenomeInfo.getStdChrLengthDict(gsuite.genome))

        chrList = {}
        chrStPos = []
        sumChr = 0
        for chrLen in chrOrder.values():
            sumChr += chrLen
            chrStPos.append(sumChr)

        dataDict, dataDictLine, elementOrder, listResCopy, listDataCountPerBin, newResBinSizeListSum = createRainfallPlotWithBinRegions.countMutations(
            gsuite, chrLength, bps)

        vg = visualizationGraphs()

        tName = gsuite.allTrackTitles()

        seriesType = []
        newSeriesNameRes = []
        newSeriesNameResOE = []
        yAxisMultiVal = []
        for el in elementOrder:
            newSeriesNameRes.append(tName[el])
            seriesType.append('scatter')
            yAxisMultiVal.append(0)
            newSeriesNameResOE.append(tName[el])

        for el in elementOrder:
            newSeriesNameRes.append(str(tName[el]) + '-- point')
            seriesType.append('line')
            yAxisMultiVal.append(1)
            newSeriesNameResOE.append(str(tName[el]) + '-- distribution')

        # listDataCountPerBin, newResBinSizeListSum


        newResList = []
        newResBinSizeListAll = []
        # newResBinSizeList=[]
        seriesNumber = []




        for el in elementOrder:
            newResList.append(listResCopy[el])

            howManyFor = len(listDataCountPerBin[el][0][1])

            for i in range(0, howManyFor):

                newResBinSizeList1 = []

                sumList = 0

                for elNum1 in range(0, len(listDataCountPerBin[el])):
                    sumList += listDataCountPerBin[el][elNum1][1][i]
                    newResBinSizeList1.append(
                        [listDataCountPerBin[el][elNum1][0], listDataCountPerBin[el][elNum1][1][i]])

                if sumList != 0:
                    newResBinSizeListAll.append(newResBinSizeList1)
                    seriesNumber.append(' # (' + str(i) + ', ' + str(i + 1) + '] --- ' + str(tName[el]) + '')



                    # newResBinSizeList.append(listDataCountPerBin[el])

        #
        # newResBinSizeListSorted = OrderedDict(sorted(newResBinSizeListSum.items()))
        #
        # # print 'newResBinSizeListSorted' + str(newResBinSizeListSorted)
        #
        #
        res = ''
        #
        # newResBinSizeListSortedList = []
        # for key, value in newResBinSizeListSorted.iteritems():
        #     newResBinSizeListSortedList.append([key, value])
        #
        if multiPlot == 'Single':
            #
            #
            #     res += vg.drawLineChart(
            #         [newResBinSizeListSortedList],
            #         seriesName=['sum per bin'],
            #         height=300,
            #         xAxisTitle='chr start pos',
            #         yAxisTitle='points per bin (' + str(scale) + ')',
            #         minY=0,
            #         plotLines=chrLength.values(),
            #         plotLinesName=chrLength.keys()
            #     )

            res += vg.drawColumnChart(
                newResBinSizeListAll,
                seriesName=seriesNumber,
                height=300,
                xAxisTitle='chr start pos',
                yAxisTitle='points per bin (' + str(scale) + ')',
                minY=0,
                stacking=True
                # plotLines=chrLength.values(),
                # plotLinesName=chrLength.keys()
            )

            res += '<div style="clear:both;"> </div>'

            res += vg.drawLineChartMultiYAxis(
                newResList,  # + newResBinSizeList,
                seriesName=newSeriesNameRes,
                seriesType=seriesType,
                height=400,
                reversed=False,
                markerRadius=2,
                xAxisTitle='chr start pos',
                yAxisTitle=['distance(log10)', 'points per bin (' + str(scale) + ')'],
                yAxisMulti=yAxisMultiVal,
                minY=0,
                plotLines=chrLength.values(),
                plotLinesName=chrLength.keys()
            )

            res += '<div style="clear:both;"> </div>'

        else:

            for nrNum in range(1, len(newResList)):
                for nrNum1 in range(0, len(newResList[nrNum])):
                    newResList[nrNum][nrNum1][0] = newResList[nrNum][nrNum1][0] + chrLength.values()[-1] * nrNum
                for nrNum1 in range(0, len(newResBinSizeList[nrNum])):
                    newResBinSizeList[nrNum][nrNum1][0] = newResBinSizeList[nrNum][nrNum1][0] + chrLength.values()[
                                                                                                    -1] * nrNum

            res = ''
            res += vg.drawLineChartMultiYAxis(
                newResList + newResBinSizeList,
                seriesName=newSeriesNameRes,
                seriesType=seriesType,
                height=500,
                reversed=False,
                markerRadius=1,
                xAxisTitle='chr start pos',
                yAxisTitle=['distance(log10)', 'points per bin (' + str(scale) + ')'],
                yAxisMulti=yAxisMultiVal,
                minY=0,
                # plotLines=chrLength.values(),
                # plotLinesName=chrLength.keys()
            )

            res += '<div style="clear:both;"> </div>'

        htmlCore = HtmlCore()
        htmlCore.begin()
        htmlCore.line('Bin size: ' + str(bps))
        htmlCore.line(res)
        htmlCore.end()
        htmlCore.hideToggle(styleClass='debug')
        print htmlCore

    @classmethod
    def countPoissonDistribution(cls, numMut, chrLength):
        from proto.RSetup import r, robjects
        # rCode = 'dataRPois <- function(vec) {hist(rpois(vec[1], vec[2]))}'
        # dd = robjects.FloatVector(
        #     [countAverageDistance['elNum'], countAverageDistance['distance'] / countAverageDistance['elNum']])
        # dataFromRPois = r(rCode)(dd)

        rCode = 'dataRPois <- function(vec) {' \
                'data=sort(runif(vec[1], 0, vec[2]));' \
                'histData=data[2:vec[1]]-data[1:vec[1]-1];' \
                'hist(histData);' \
                '}'
        dd = robjects.FloatVector(
            [numMut, chrLength])
        dataFromRPois = r(rCode)(dd)

        # print '<br >mean' + str(countAverageDistance['distance']/countAverageDistance['elNum'])
        # print '<br >counts' + str(countAverageDistance['elNum'])
        #
        # print '<br >dataFromRPois' + str(list(dataFromRPois.rx2('counts')))
        # print '<br >dataFromRPois' + str(list(dataFromRPois.rx2('breaks')))

        # distance (time) - gamma, exp
        # event(number of events) - poisson

        poissonListMean = []
        breaks = list(dataFromRPois.rx2('breaks'))
        counts = list(dataFromRPois.rx2('counts'))
        for elN in range(0, len(counts)):
            # if scale == 'Log':
            #     if counts[elN] != 0:
            #         counts[elN] = math.log(counts[elN], 10)
            #     else:
            #         counts[elN] = 0
            poissonListMean.append([(breaks[elN] + breaks[elN + 1]) / 2, counts[elN]])

            # print 'poissonListMean' + str(poissonListMean)

        return poissonListMean

    @classmethod
    def countHist(cls, newResList):
        from proto.RSetup import r, robjects

        rCode = 'dataRPois <- function(vec) {' \
                'hist(vec)' \
                '}'
        dd = robjects.FloatVector(
            [int(math.pow(10, n[1])) for n in newResList])
        dataFromRPois = r(rCode)(dd)

        poissonListMean = []
        breaks = list(dataFromRPois.rx2('breaks'))
        counts = list(dataFromRPois.rx2('counts'))
        for elN in range(0, len(counts)):
            poissonListMean.append([(breaks[elN] + breaks[elN + 1]) / 2, counts[elN]])

        return poissonListMean

    @classmethod
    def countMutations(cls, gsuite, chrLength, bps):

        dataDict = OrderedDict()
        dataDictLine = OrderedDict()

        elementOrder = []

        # parse the tracks
        for track in gsuite.allTrackTitles():

            # count one track
            gSuiteTrack = gsuite.getTrackFromTitle(track)
            trackName = track

            # if not trackName in countAverageDistancePerTrack:
            #     countAverageDistancePerTrack[trackName] = 0

            dataDict[trackName] = OrderedDict()
            dataDictLine[trackName] = OrderedDict()

            # read from file
            newDict = {}
            with open(gSuiteTrack.path, 'r') as f:
                i = 0
                for x in f.readlines():
                    el = x.strip('\n').split('\t')
                    if len(el) >= 2:
                        if not el[0] in newDict:
                            newDict[el[0]] = []
                        newDict[el[0]].append([el[0], int(el[1]), int(el[2])])
                i += 1

            # sort file according to start position
            newDict2 = OrderedDict()
            for key, it in chrLength.items():
                if key in newDict:
                    newDict2[key] = sorted(newDict[key], key=lambda x: x[1])

            for key, it in newDict2.items():
                if i == 0:
                    chr = key
                i = 0
                prevEnd = 0
                label = 0

                for el in it:
                    if len(el) >= 2:

                        if not int(el[1]) in dataDictLine[trackName]:
                            dataDictLine[trackName][int(el[1])] = 1
                        start = int(el[1])
                        if prevEnd != 0:
                            if not label in dataDict[trackName]:
                                dataDict[trackName][label] = OrderedDict()
                                dataDict[trackName][label]['val'] = 0
                                dataDict[trackName][label]['tot'] = 0

                            # print str(start) + '-' + str(prevEnd)

                            if start - prevEnd != 0:
                                dataDict[trackName][label]['val'] += math.log(start - prevEnd, 10)
                            else:
                                dataDict[trackName][label]['val'] += start - prevEnd

                            dataDict[trackName][label]['tot'] += 1

                        label = int(el[1]) + int(chrLength[el[0]])

                        prevEnd = int(el[1])  # not anymore prevEnd
                        i += 1

            elementOrder.append(i)

        listResCopy = []
        for key0, it0 in dataDict.iteritems():
            listResPart = []
            for key2 in sorted(it0):
                listResPart.append([key2, it0[key2]['val']])
            listResCopy.append(listResPart)

        elementOrder = sorted(range(len(elementOrder)), key=lambda k: elementOrder[k])

        lengthOfLastChromosome = GenomeInfo.getChrLen(gsuite.genome, chrLength.keys()[-1])

        howManyIntervalsPerBin = int((chrLength.values()[-1] + lengthOfLastChromosome) / bps) + 1

        listOfBinSumPerTrack = []
        for interval in range(0, howManyIntervalsPerBin):
            listOfBin = (interval * bps, (interval + 1) * bps)
            listOfBinSumPerTrack.append(listOfBin)

            newResBinSizeListSum = {}

        listDataCountPerBin = []
        for el in listResCopy:
            data = filter(None, [filter(lambda l: t[0] <= int(l[0]) < t[1], el) for t in listOfBinSumPerTrack])
            listData = []

            for d in data:

                logBin = [0 for x in range(0, 10)]

                countD = int(d[0][0] / bps) * bps + bps / 2

                # print 'ddd', d, countD, '<br \>'

                for elD in d:
                    for i in range(0, 10):
                        if elD[1] < i + 1 and elD[1] >= i:
                            logBin[i] += 1

                # print 'countD', countD, 'logBin', logBin, '<br \>'


                w = 0
                listData.append([countD, logBin])

                # print 'listData', listData, '<br \><br \>'

                if not countD in newResBinSizeListSum.keys():
                    newResBinSizeListSum[countD] = logBin
                else:
                    for ellb in range(0, len(logBin)):
                        newResBinSizeListSum[countD][ellb] += logBin[ellb]

            listDataCountPerBin.append(listData)

        return dataDict, dataDictLine, elementOrder, listResCopy, listDataCountPerBin, newResBinSizeListSum

    @classmethod
    def sortChrDict(cls, chr):

        remeberString = []
        keysList = []
        for el in chr.keys():
            try:
                elC = int(el.replace('chr', ''))
                keysList.append(elC)
            except:
                remeberString.append(el.replace('chr', ''))

        sChr = sorted(keysList) + sorted(remeberString)

        chrDict = OrderedDict()
        chrLength = OrderedDict()
        val = 0
        for elChr in sChr:
            el = 'chr' + str(elChr)
            chrDict[el] = chr[el]
            chrLength[el] = val
            val += chr[el]

        return chrDict, chrLength

    @staticmethod
    def getOutputFormat(choices):
        return 'customhtml'


class createRainfallPlot(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Create rainfall plot [RP manuscript tool]"

    @staticmethod
    def getInputBoxNames():
        return [
            ('Select gsuite', 'gsuite'),
            ('Select type of plotting', 'multiPlot'),
            ('Select scale for bps value', 'scale'),
            ('Overlap', 'overlap'),
            ('Get image', 'image'),
            ('Select bps (100000)', 'bps')
        ]

    @staticmethod
    def getOptionsBoxGsuite():
        return '__history__', 'gsuite'

    @staticmethod
    def getOptionsBoxMultiPlot(prevChoices):
        return ['Single', 'Multi']

    @staticmethod
    def getOptionsBoxScale(prevChoices):
        return ['Linear', 'Log']

    @staticmethod
    def getOptionsBoxOverlap(prevChoices):
        return ['no', 'yes']

    @staticmethod
    def getOptionsBoxImage(prevChoices):
        return ['yes', 'no']

    @staticmethod
    def getOptionsBoxBps(prevChoices):
        return '100000'

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        gsuite = getGSuiteFromGalaxyTN(choices.gsuite)

        gSuiteTracksNum = gsuite.numTracks()

        multiPlot = choices.multiPlot
        scale = choices.scale
        image = choices.image

        overlap = choices.overlap
        bps = int(choices.bps)

        chrItems = GenomeInfo.getStdChrLengthDict(gsuite.genome)
        chrOrder, chrLength = createRainfallPlot.sortChrDict(chrItems)

        chrList = {}
        chrStPos = []
        sumChr = 0
        for chrLen in chrOrder.values():
            sumChr += chrLen
            chrStPos.append(sumChr)

        dataDict, dataDictLine, elementOrder, listResCopy, listDataCountPerBin, newResBinSizeListSum, chrList = createRainfallPlot.countMutations(
            gsuite, chrLength, bps)

        vg = visualizationGraphs()

        tName = gsuite.allTrackTitles()

        seriesType = []
        newSeriesNameRes = []
        newSeriesNameResOE = []
        yAxisMultiVal = []
        for el in elementOrder:
            newSeriesNameRes.append(tName[el])
            seriesType.append('scatter')
            yAxisMultiVal.append(0)
            newSeriesNameResOE.append(tName[el])

        for el in elementOrder:
            newSeriesNameRes.append(str(tName[el]) + '-- point')
            seriesType.append('line')
            yAxisMultiVal.append(1)
            newSeriesNameResOE.append(str(tName[el]) + '-- distribution')

        newResList = []
        newResBinSizeList = []
        for el in elementOrder:
            newResList.append(listResCopy[el])
            newResBinSizeList.append(listDataCountPerBin[el])

        newResBinSizeListSorted = OrderedDict(sorted(newResBinSizeListSum.items()))

        # print 'newResBinSizeListSorted' + str(newResBinSizeListSorted)



        newResBinSizeListSortedList = []
        for key, value in newResBinSizeListSorted.iteritems():
            newResBinSizeListSortedList.append([key, value])

        if multiPlot == 'Single':
            res = ''

            if image == 'yes':
                res += """

                <button id='save_btn1' style="display: none;">Save Chart1</button>
                <button id='save_btn2' style="display: none;">Save Chart2</button>
                <script>

                EXPORT_WIDTH = 1350;
                EXPORT_HEIGHT = 700;
                function download(data, filename)
                {
                  var a = document.createElement('a');
                  a.download = filename;
                  a.href = data
                  document.body.appendChild(a);
                  a.click();
                  a.remove();
                }

                function save_chart(chart)
                {
                    render_width = EXPORT_WIDTH;
                    render_height = EXPORT_HEIGHT; //render_width * chart.chartHeight / chart.chartWidth

                    // Get the carts SVG code
                    var svg = chart.getSVG(
                    {
                        exporting:
                        {
                            sourceWidth: chart.chartWidth,
                            sourceHeight: chart.chartHeight
                        }
                    });

                    // Create a canvas
                    var canvas = document.createElement('canvas');
                    canvas.height = render_height;
                    canvas.width = render_width;
                    document.body.appendChild(canvas);

                    // Create an image and draw the SVG onto the canvas
                    var image = new Image;
                    image.onload = function() {
                    canvas.getContext('2d').drawImage(this, 0, 0, render_width, render_height);

                    var data = canvas.toDataURL("image/png")
                    download(data, 'aa' + '.png')
                    };

                    image.src = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svg)));
                }


                </script>
                """

            res += vg.drawLineChart(
                [newResBinSizeListSortedList],
                seriesName=['sum per bin'],
                height=300,
                xAxisTitle='Genomic position',
                yAxisTitle='values',
                minY=0,
                plotLines=chrLength.values(),
                plotLinesName=chrLength.keys()
            )

            if image == 'yes':
                res += """
                    <script>
                    $( function() {
                        $('#save_btn1').click(function() {
                        save_chart($('#container1').highcharts());
                    });
                    setTimeout(function() {
                        $('#save_btn1').trigger('click'); }, 0);
                    });
                    </script>
                """

            res += '<div style="clear:both;"> </div>'

            # ww=' x = c('
            # ll = ' y = c('
            #
            # i=0
            # for el in newResList[0]:
            #     if i< len(newResList[0])-1:
            #         ww += str(el[0]) + ', '
            #         ll += str(round(el[1],2)) + ', '
            #     else:
            #         ww += str(el[0])
            #         ll += str(round(el[1], 2))
            #     i+=1
            #
            #
            #
            # ww += ')'
            # ll += ')'
            #
            # print ww
            # print '<br />'
            # print ll
            #
            # exit()
            for nrNum in range(0, len(newResList)):
                newSeriesNameRes[nrNum] = newSeriesNameRes[nrNum] + ' -- ' + str(len(newResList[nrNum]))

            data = newResList + newResBinSizeList

            if overlap == 'yes':

                listElAll = []
                for l in newResList:
                    listElAll += [[ll[0], round(ll[1], 1)] for ll in l]

                epsilonTF = True

                if epsilonTF == False:

                    z = []
                    y = []
                    for i in listElAll:
                        if i not in z:
                            z.append(i)
                        else:
                            y.append(i)
                else:
                    pass

                # #too slow
                #     # y=[]
                #     # epsilon = 0.1
                #     # for iN in range(0, len(listElAll)):
                #     #     for jN in range(iN + 1, len(listElAll)):
                #     #         if listElAll[iN][1] + epsilon > listElAll[jN][1] and listElAll[iN][1] - epsilon <= listElAll[jN][1]:
                #     #             if not listElAll[iN] in y:
                #     #                 y.append(listElAll[iN])
                #     #             y.append(listElAll[jN])
                #
                #     listElAll = sorted(listElAll, key=lambda x: x[1])
                #
                #     minX = 0
                #     minY = 0
                #     maxY = 530
                #     maxX = 1260
                #
                #     res += "<button id='up'> update </button> <script> var listElAll =  " + str(listElAll) + "; </script>"
                #
                #
                #     listElAllNorm = []
                #     for elN in range(1, len(listElAll)):
                #         listElAllNorm.append(
                #             [(listElAll[elN][0] - minX) / (maxX - minX), (listElAll[elN][1] - minY) / (maxY - minY)])
                #
                #     z = []
                #     yy = []
                #     index = 0
                #     for i in listElAllNorm:
                #         if i not in z:
                #             z.append(i)
                #         else:
                #             yy.append(index)
                #         index+=1
                #
                #
                #
                #     y = []
                #     for yEl in yy:
                #         y.append(listElAll[yEl])
                #
                #
                #
                #
                #         #epsilon of points
                #     # y = []
                #     # epsilon = 0.2
                #     # tempY = listElAll[0]
                #     # for elN in range(1, len(listElAll)):
                #     #     #print tempY, tempY + epsilon, tempY - epsilon, listElAll[elN][1], '<br \>'
                #     #     if tempY[1] + epsilon >= listElAll[elN][1] and \
                #     #                             tempY[1] - epsilon < listElAll[elN][1] and \
                #     #                             tempY[0] + epsilon*1000 >= listElAll[elN][0] and \
                #     #                             tempY[0] - epsilon*1000 < listElAll[elN][0]:
                #     #         y.append(listElAll[elN])
                #     #         y.append(listElAll[elN - 1])
                #     #     tempY = listElAll[elN]
                #
                #
                #
                # newResListV2 = []
                #
                # for nrNum in range(0, len(newResList)):
                #     newResListV2.append([x for x in newResList[nrNum] if not x in y])
                #     print len(newResListV2[nrNum])
                #
                #
                #
                # newResList = newResListV2
                #
                # newSeriesNameRes.append('overlapped points')
                # seriesType.append('scatter')
                # yAxisMultiVal.append(0)
                # data = newResList + newResBinSizeList + [y]


                res += "<button id='up'> update </button> <script> var listElAll =  " + str(listElAll) + "; </script>"

            # heightWhichIgave = 400
            # widthWhichIgave = 1000
            # realHeight = 322
            # realWidth =  873
            #
            # addExtraH = heightWhichIgave - realHeight
            # addExtraW = widthWhichIgave - realWidth
            #
            # newHeight = 351+addExtraH
            # #it is because the first rainfal plot took 70% on the screen



            # print newHeight

            # res += '<div style="width:' + str(1000+addExtraW) + 'px;height:' + str(newHeight) + 'px;background-color:blue">'
            res += vg.drawLineChartMultiYAxis(
                data,
                seriesName=newSeriesNameRes,
                seriesType=seriesType,
                height=400,  # newHeight + 0.3*newHeight,
                reversed=False,
                markerRadius=2,
                xAxisTitle='Genomic position',
                yAxisTitle=['Genomic distance', 'values'],
                yAxisMulti=yAxisMultiVal,
                minY=0,
                plotLines=chrLength.values(),
                plotLinesName=chrLength.keys()
            )
            # res+='</div>'

            res += """
            <script>

            function round(number, decimals)
            {
            return +(Math.round(number + "e+" + decimals) + "e-" + decimals);
            }

            function decNum(num)
            {
              return num.toString().length;
            }


            function arrayMinMax(arr) {
              var len = arr.length,
              maxX = -Infinity;
              minX = Infinity;
              maxY = -Infinity;
              minY = Infinity;

              maxArr = []

              while (len--)
              {
                if (arr[len][0] < minX)
                {
                  minX = arr[len][0];
                }
                if (arr[len][0] > maxX)
                {
                  maxX = arr[len][0];
                }

                if (arr[len][1] < minY)
                {
                  minY = arr[len][1];
                }
                if (arr[len][1] > maxY)
                {
                  maxY = arr[len][1];
                }



              }

              maxArr.push(minX);
              maxArr.push(maxX);
              maxArr.push(minY);
              maxArr.push(maxY);

              return maxArr;
            }








            $('#up').click(function () {

                chart2  = $('#container2').highcharts();




            var minX = 0;
            var maxX = chart2.plotSizeX;
            var minY = 0;
            var maxY = chart2.plotSizeY * 0.7;



            console.log(minX, minY, maxX, maxY);


            decNumX = decNum(maxX);
            decNumY = decNum(maxY);

            minmaxArr = arrayMinMax(listElAll);

            var minXval = minmaxArr[0];
            var maxXval = minmaxArr[1];
            var minYval = minmaxArr[2];
            var maxYval = minmaxArr[3];

            var xx=0;
            var yy=0;
            var listElAllNorm = [];

            //to improve because 1 dot is 4 piksels - not 1, so it means that it will not find piksels which are partially
            //covered, need to be fully covered

            for (var elN =0; elN< listElAll.length; elN++)
            {
                //listElAllNorm.push([round((listElAll[elN][0] - minX) / (maxX - minX), decNumX-3), round((listElAll[elN][1] - minY) / (maxY - minY), decNumY-3)]);
                xx = round((listElAll[elN][0] - minXval) / (maxXval - minXval), decNumX);
                xx = xx * (maxX-minX) + minX;
                yy = round((listElAll[elN][1] - minYval) / (maxYval - minYval), decNumY);
                yy = yy * (maxY-minY) + minY;
                listElAllNorm.push([xx, yy]);
            }


            //console.log(listElAllNorm);



            var z = []
            var yy = [] //unique elements
            var index = 0
            for (i in listElAllNorm)
            {
                //trick with changing list into string , because there is no simple method for array of arrays
                //console.log(index, listElAllNorm[i], z, z.indexOf(listElAllNorm[i].toString()), yy);
                if (z.indexOf(listElAllNorm[i].toString()) == -1)
                {
                   z.push(listElAllNorm[i].toString());
                }
                else
                {
                   yy.push(index);
                }
                index+=1;
            }

            //console.log(yy);


            y = []
            for (yEl in yy)
            {
                y.push(listElAll[yy[yEl]])
            }



            var seriesLength = chart2.series.length;
            for(var i = seriesLength - 1; i > -1; i--)
            {

            if(chart2.series[i].name == 'overlap')
               chart2.series[i].remove();
            }

            chart2.addSeries({
                type: 'scatter',
                name: 'overlap',
                data: y.slice(0,y.length-1),
                color: "#000000",
                marker: { radius: 2, symbol: 'circle', },
                 yAxis: 0
            });

            //chart2.redraw();


            //console.log(chart2);




                        })
                        </script>

            """

            if image == 'yes':
                res += """
                <script>
                $( function() {
                    $('#save_btn2').click(function() {
                    save_chart($('#container2').highcharts());
                });
                setTimeout(function() {
                    $('#save_btn2').trigger('click'); }, 0);
                });
                </script>
                """

            res += '<div style="clear:both;"> </div>'

        else:

            maxLength = -10000
            for nrNum in range(1, len(newResList)):
                if maxLength < newResList[nrNum][-1][0]:
                    maxLength = newResList[nrNum][-1][0]

            # for el in chrList:
            #     maxLength += chrItems[el]

            # if maxLength = chrLength.values()[-1]


            newSeriesNameRes[0] = newSeriesNameRes[0] + ' -- ' + str(len(newResList[0]))
            for nrNum in range(1, len(newResList)):
                for nrNum1 in range(0, len(newResList[nrNum])):
                    newResList[nrNum][nrNum1][0] = newResList[nrNum][nrNum1][0] + maxLength * nrNum
                for nrNum1 in range(0, len(newResBinSizeList[nrNum])):
                    newResBinSizeList[nrNum][nrNum1][0] = newResBinSizeList[nrNum][nrNum1][0] + maxLength * nrNum
                newSeriesNameRes[nrNum] = newSeriesNameRes[nrNum] + ' -- ' + str(len(newResList[nrNum]))

            res = ''
            res += vg.drawLineChartMultiYAxis(
                newResList + newResBinSizeList,
                seriesName=newSeriesNameRes,
                seriesType=seriesType,
                height=500,
                reversed=False,
                markerRadius=1,
                label='<b>{series.name}: </b>{point.x}, {point.y} <br \>',
                xAxisTitle='chr start pos',
                yAxisTitle=['distance(log10)', 'points per bin (' + str(scale) + ')'],
                yAxisMulti=yAxisMultiVal,
                minY=0,
                # plotLines=chrLength.values(),
                # plotLinesName=chrLength.keys()
            )
            if image == 'yes':
                res += """
                    <script>
                    $( function() {
                        $('#save_btn1').click(function() {
                        save_chart($('#container1').highcharts());
                    });
                    setTimeout(function() {
                        $('#save_btn1').trigger('click'); }, 0);
                    });
                    </script>
                """

            res += '<div style="clear:both;"> </div>'

        htmlCore = HtmlCore()
        htmlCore.begin()
        htmlCore.line('Bin size: ' + str(bps))
        htmlCore.line(res)
        htmlCore.end()
        htmlCore.hideToggle(styleClass='debug')
        print htmlCore

    @classmethod
    def countPoissonDistribution(cls, numMut, chrLength):
        from proto.RSetup import r, robjects
        # rCode = 'dataRPois <- function(vec) {hist(rpois(vec[1], vec[2]))}'
        # dd = robjects.FloatVector(
        #     [countAverageDistance['elNum'], countAverageDistance['distance'] / countAverageDistance['elNum']])
        # dataFromRPois = r(rCode)(dd)

        rCode = 'dataRPois <- function(vec) {' \
                'data=sort(runif(vec[1], 0, vec[2]));' \
                'histData=data[2:vec[1]]-data[1:vec[1]-1];' \
                'hist(histData);' \
                '}'
        dd = robjects.FloatVector(
            [numMut, chrLength])
        dataFromRPois = r(rCode)(dd)

        # print '<br >mean' + str(countAverageDistance['distance']/countAverageDistance['elNum'])
        # print '<br >counts' + str(countAverageDistance['elNum'])
        #
        # print '<br >dataFromRPois' + str(list(dataFromRPois.rx2('counts')))
        # print '<br >dataFromRPois' + str(list(dataFromRPois.rx2('breaks')))

        # distance (time) - gamma, exp
        # event(number of events) - poisson

        poissonListMean = []
        breaks = list(dataFromRPois.rx2('breaks'))
        counts = list(dataFromRPois.rx2('counts'))
        for elN in range(0, len(counts)):
            # if scale == 'Log':
            #     if counts[elN] != 0:
            #         counts[elN] = math.log(counts[elN], 10)
            #     else:
            #         counts[elN] = 0
            poissonListMean.append([(breaks[elN] + breaks[elN + 1]) / 2, counts[elN]])

            # print 'poissonListMean' + str(poissonListMean)

        return poissonListMean

    @classmethod
    def countHist(cls, newResList):
        from proto.RSetup import r, robjects

        rCode = 'dataRPois <- function(vec) {' \
                'hist(vec)' \
                '}'
        dd = robjects.FloatVector(
            [int(math.pow(10, n[1])) for n in newResList])
        dataFromRPois = r(rCode)(dd)

        poissonListMean = []
        breaks = list(dataFromRPois.rx2('breaks'))
        counts = list(dataFromRPois.rx2('counts'))
        for elN in range(0, len(counts)):
            poissonListMean.append([(breaks[elN] + breaks[elN + 1]) / 2, counts[elN]])

        return poissonListMean

    @classmethod
    def countMutations(cls, gsuite, chrLength, bps):

        dataDict = OrderedDict()
        dataDictLine = OrderedDict()

        chrList = []

        elementOrder = []

        # parse the tracks
        for track in gsuite.allTrackTitles():

            # count one track
            gSuiteTrack = gsuite.getTrackFromTitle(track)
            trackName = track

            # if not trackName in countAverageDistancePerTrack:
            #     countAverageDistancePerTrack[trackName] = 0

            dataDict[trackName] = OrderedDict()
            dataDictLine[trackName] = OrderedDict()

            # read from file
            newDict = OrderedDict()
            with open(gSuiteTrack.path, 'r') as f:
                i = 0
                for x in f.readlines():
                    el = x.strip('\n').split('\t')
                    if len(el) >= 2:
                        try:
                            st = int(el[1])
                            if not el[0] in newDict:
                                newDict[el[0]] = []
                            if not el[0] in chrList:
                                chrList.append(el[0])
                            newDict[el[0]].append([el[0], st, int(el[2])])
                        except:
                            pass
                i += 1

            # sort file according to start position
            newDict2 = OrderedDict()
            for key, it in chrLength.items():
                if key in newDict:
                    newDict2[key] = sorted(newDict[key], key=lambda x: x[1])

            for key, it in newDict2.items():
                if i == 0:
                    chr = key
                i = 0
                prevEnd = 0
                label = 0

                for el in it:
                    if len(el) >= 2:

                        if not int(el[1]) in dataDictLine[trackName]:
                            dataDictLine[trackName][int(el[1])] = 1
                        start = int(el[1])
                        if prevEnd != 0:
                            if not label in dataDict[trackName]:
                                dataDict[trackName][label] = OrderedDict()
                                dataDict[trackName][label]['val'] = 0
                                dataDict[trackName][label]['tot'] = 0

                            # print str(start) + '-' + str(prevEnd)

                            if start - prevEnd != 0:
                                dataDict[trackName][label]['val'] += math.log(start - prevEnd, 10)
                            else:
                                dataDict[trackName][label]['val'] += start - prevEnd

                            dataDict[trackName][label]['tot'] += 1

                        label = int(el[1]) + int(chrLength[el[0]])

                        prevEnd = int(el[1])  # not anymore prevEnd
                        i += 1

            elementOrder.append(i)

        listResCopy = []
        for key0, it0 in dataDict.iteritems():
            listResPart = []
            for key2 in sorted(it0):
                listResPart.append([key2, it0[key2]['val']])
            listResCopy.append(listResPart)

        # if there is no need to have ordering
        # elementOrder = sorted(range(len(elementOrder)), key=lambda k: elementOrder[k], reverse=True)
        # then
        elementOrder = [k for k in range(0, len(elementOrder))]

        lengthOfLastChromosome = GenomeInfo.getChrLen(gsuite.genome, chrLength.keys()[-1])

        howManyIntervalsPerBin = int((chrLength.values()[-1] + lengthOfLastChromosome) / bps) + 1

        listOfBinSumPerTrack = []
        for interval in range(0, howManyIntervalsPerBin):
            listOfBin = (interval * bps, (interval + 1) * bps)
            listOfBinSumPerTrack.append(listOfBin)

            newResBinSizeListSum = {}

        listDataCountPerBin = []
        for el in listResCopy:
            data = filter(None, [filter(lambda l: t[0] <= int(l[0]) < t[1], el) for t in listOfBinSumPerTrack])
            listData = []
            for d in data:

                countD = int(d[0][0] / bps) * bps + bps / 2
                lenD = len(d)

                w = 0
                listData.append([countD, lenD])

                if not countD in newResBinSizeListSum.keys():
                    newResBinSizeListSum[countD] = lenD
                else:
                    newResBinSizeListSum[countD] += lenD

            listDataCountPerBin.append(listData)

        return dataDict, dataDictLine, elementOrder, listResCopy, listDataCountPerBin, newResBinSizeListSum, chrList

    @classmethod
    def sortChrDict(cls, chr):

        remeberString = []
        keysList = []
        for el in chr.keys():
            try:
                elC = int(el.replace('chr', ''))
                keysList.append(elC)
            except:
                remeberString.append(el.replace('chr', ''))

        sChr = sorted(keysList) + sorted(remeberString)

        chrDict = OrderedDict()
        chrLength = OrderedDict()
        val = 0
        for elChr in sChr:
            el = 'chr' + str(elChr)
            chrDict[el] = chr[el]
            chrLength[el] = val
            val += chr[el]

        return chrDict, chrLength

    @staticmethod
    def getOutputFormat(choices):
        return 'customhtml'


class makeRainfallPlots(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Make rainfall plots based on gSuite"

    @staticmethod
    def getInputBoxNames():
        return [
            ('Select gsuite', 'gSuite'),
            ('Select option', 'color'),
            ('Select type of results', 'interactive'),
            ('Select type of plotting', 'multiPlot'),
            ('Select scale for bps value', 'scale'),
            ('Select bps (10000)', 'bps')
        ]

    @staticmethod
    def getOptionsBoxGSuite():
        return '__history__', 'gsuite'

    @staticmethod
    def getOptionsBoxColor(prevChoices):
        return ['Single color', 'Various colors']

    @staticmethod
    def getOptionsBoxInteractive(prevChoices):
        # return ['Interactive', 'Figure']
        return ['Interactive']

    @staticmethod
    def getOptionsBoxMultiPlot(prevChoices):
        return ['Single', 'Multi']

    @staticmethod
    def getOptionsBoxScale(prevChoices):
        return ['Linear', 'Log']

    @staticmethod
    def getOptionsBoxBps(prevChoices):
        return ''

    @classmethod
    def drawInteractiveSingle(cls, seriesNameRes, listRes, listResLine, listResBubble):
        vg = visualizationGraphs()
        res = vg.drawScatterChart(
            [listRes],
            seriesName=['All Series'],
            # titleText = ['Scatter plot'],
            label='<b>{series.name}</b>: {point.x} {point.y}',
            height=300,

            markerRadius=1,
            xAxisTitle='chr start pos',
            yAxisTitle='distance',
            marginTop=30
        )
        res += vg.drawLineChart(
            listResLine,
            seriesName=seriesNameRes,
            # label = '<b>{series.name}</b>: X:{point.x} Y:{point.y} value: {point.z}',
            height=300,
            xAxisTitle='chr start pos',
            yAxisTitle='values',
            marginTop=30
        )
        res += vg.drawBubbleChart(
            [listResBubble],
            seriesName=['All Series'],
            label='<b>{series.name}</b>: X:{point.x} Y:{point.y} value: {point.z}',
            height=300,
            xAxisTitle='chr start pos',
            yAxisTitle='distance',
            marginTop=30
        )
        return res

    @classmethod
    def drawInteractiveVariousColor(cls, seriesNameRes, listRes, listResLine, listResBubble):
        vg = visualizationGraphs()
        res = vg.drawScatterChart(
            listRes,
            seriesName=seriesNameRes,
            # titleText = ['Scatter plot'],
            label='<b>{series.name}</b>: {point.x} {point.y}',
            height=300,

            markerRadius=1,
            xAxisTitle='chr start pos',
            yAxisTitle='distance',
            marginTop=30
        )

        res += vg.drawLineChart(
            listResLine,
            seriesName=seriesNameRes,
            # label = '<b>{series.name}</b>: X:{point.x} Y:{point.y} value: {point.z}',
            height=300,
            xAxisTitle='chr start pos',
            yAxisTitle='values',
            marginTop=30
        )

        res += vg.drawBubbleChart(
            listResBubble,
            seriesName=seriesNameRes,
            label='<b>{series.name}</b>: X:{point.x} Y:{point.y} value: {point.z}',
            height=300,
            xAxisTitle='chr start pos',
            yAxisTitle='distance',
            marginTop=30
        )
        return res

    @classmethod
    def drawInteractiveMulti(cls, listResLine, elementOrder, listResCopy, seriesNameRes, listResBubble, bps, scale,
                             chrStPos):
        vg = visualizationGraphs()
        percentagePlot = str(int(float(100) / float(len(listResLine)))) + '%'
        # percentagePlot = '800px'

        res = ''

        # elementOrder=[0,1,2,3]

        listMaxVal = []
        for elCount in elementOrder:
            lmax = -10000
            lmin = 10000000000000000
            for elN in range(0, len(listResCopy[elCount])):
                if listResCopy[elCount][elN][0] > lmax:
                    lmax = listResCopy[elCount][elN][0]
                if listResCopy[elCount][elN][0] < lmin:
                    lmin = listResCopy[elCount][elN][0]
            listMaxVal.append([lmin, lmax])

        # print listMaxVal
        # print '========'
        # print listResCopy[0]
        #
        # print '----'

        # print str(listMaxVal)+ '<br \>'

        listResBubbleX = {}
        howManyPerBin = OrderedDict()
        j = 0
        for elCount in elementOrder:
            listResBubbleX[elCount] = {}

            for elN in range(0, len(listResCopy[elCount])):
                if not listResCopy[elCount][elN][0] in listResBubbleX[elCount]:
                    listResBubbleX[elCount][listResCopy[elCount][elN][0]] = 0
                listResBubbleX[elCount][listResCopy[elCount][elN][0]] += 1

            if not elCount in howManyPerBin:
                howManyPerBin[elCount] = []

            lmin = int(math.floor(listMaxVal[j][0]) / bps)
            lmax = int(math.ceil(listMaxVal[j][1]) / bps) + 1

            addValue = 0
            if elCount != 0:
                for elM in range(0, elCount):
                    addValue += listMaxVal[elM][1]

            for vv in range(lmin, lmax):

                binStart = vv * bps
                binEnd = vv * bps + bps
                endCount = binEnd - 1

                valueCount = 0
                # print 'binStart: ' + str(binStart) + '<br \>'
                # print 'binEnd: ' + str(binEnd) + '<br \>'
                # print 'valueCount1: ' + str(valueCount) + '<br \>'



                for elN in range(0, len(listResCopy[elCount])):

                    val = listResCopy[elCount][elN][0]
                    if val >= binStart and val < binEnd:
                        # print 'val: ' + str(binStart) + '<br \>'
                        valueCount += 1

                # print 'valueCount2: ' + str(valueCount) + '<br \>'
                howManyPerBin[elCount].append([binStart + addValue, valueCount])
                howManyPerBin[elCount].append([endCount + addValue, valueCount])
                valueCount = 0
            j += 1

        listResBubble = OrderedDict()
        for elCount in elementOrder:
            listResBubble[elCount] = []
            for elN in range(0, len(listResCopy[elCount])):

                addValue = 0
                if elCount != 0:
                    for elM in range(0, elCount):
                        addValue += listMaxVal[elM][1]
                vLog = 0
                if listResCopy[elCount][elN][1] > 0:
                    vLog = math.log(listResCopy[elCount][elN][1], 10)
                listResBubble[elCount].append([listResCopy[elCount][elN][0] + addValue, vLog,
                                               listResBubbleX[elCount][listResCopy[elCount][elN][0]]])

        #
        # howManyPerBin2=OrderedDict()
        # j=0
        # for elCount in elementOrder:
        #     if not elCount in howManyPerBin2:
        #         howManyPerBin2[elCount]=[]
        #
        #     lmin = int(math.floor(listMaxVal[j][0]))
        #     lmax = int(math.ceil(listMaxVal[j][1])) + 1
        #
        #     print 'lmin: ' + str(lmin) + '<br \>'
        #     print 'lmax: ' + str(lmax) + '<br \>'
        #
        #     for vv in range(lmin, lmax):
        #
        #
        #         binStart = vv #1mln - 1mln+1
        #         binEnd =  vv + bps #1mln + 1 - 1mln+2
        #         endCount = binEnd-1
        #
        #         addValue=0
        #         if len(listMaxVal) > elCount and elCount!=0:
        #             addValue = listMaxVal[elCount-1][1]+1
        #
        #         valueCount = 0
        #         # print 'binStart: ' + str(binStart) + '<br \>'
        #         # print 'binEnd: ' + str(binEnd) + '<br \>'
        #         # print 'valueCount1: ' + str(valueCount) + '<br \>'
        #
        #
        #
        #         for elN in range(0, len(listResCopy[elCount])):
        #             val = listResCopy[elCount][elN][0]
        #             if val >= binStart and val < binEnd:
        #                 # print 'val: ' + str(binStart) + '<br \>'
        #                 valueCount += 1
        #
        #         # print 'valueCount2: ' + str(valueCount) + '<br \>'
        #         howManyPerBin2[elCount].append([binStart+addValue, valueCount])
        #         howManyPerBin2[elCount].append([endCount+addValue, valueCount])
        #         valueCount = 0
        #     j+=1


        # print howManyPerBin[0]

        newListResCopy = []
        for elCount in elementOrder:

            addValue = 0
            if elCount != 0:
                for elM in range(0, elCount):
                    addValue += listMaxVal[elM][1]

            for elN in range(0, len(listResCopy[elCount])):
                vLog = 0
                if listResCopy[elCount][elN][1] > 0:
                    vLog = math.log(listResCopy[elCount][elN][1], 10)
                listResCopy[elCount][elN][1] = vLog
                listResCopy[elCount][elN][0] = listResCopy[elCount][elN][0] + addValue

            newListResCopy.append(listResCopy[elCount])

        for elCount in howManyPerBin:
            newhowManyPerBin = []

            ik = True
            for elN in range(0, len(howManyPerBin[elCount])):
                if elN % 2 == 0:
                    ik = True
                else:
                    if howManyPerBin[elCount][elN][1] != 0:
                        st = (howManyPerBin[elCount][elN][0] + howManyPerBin[elCount][elN - 1][0]) / 2
                        end = howManyPerBin[elCount][elN][1]
                        if scale == 'Log':
                            if end != 0:
                                end = math.log(end, 10)
                        newhowManyPerBin.append([st, end])
                    else:
                        st = (howManyPerBin[elCount][elN][0] + howManyPerBin[elCount][elN - 1][0]) / 2
                        end = None
                        newhowManyPerBin.append([st, end])
                    ik = False
            if ik == False:
                st = howManyPerBin[elCount][elN][0]
                end = howManyPerBin[elCount][elN][1]
                if scale == 'Log':
                    if end != 0:
                        end = math.log(end, 10)
                newhowManyPerBin.append([st, end])

            newListResCopy.append(newhowManyPerBin)

            # newListResCopy.append(howManyPerBin[elCount])
        #
        # for elCount in howManyPerBin2:
        #     newListResCopy.append(howManyPerBin2[elCount])

        seriesType = []
        newSeriesNameRes = []
        yAxisMultiVal = []
        for sn in seriesNameRes:
            newSeriesNameRes.append(sn)
            seriesType.append('scatter')
            yAxisMultiVal.append(0)

        for sn in seriesNameRes:
            newSeriesNameRes.append(str(sn) + '-- point')
            seriesType.append('line')
            yAxisMultiVal.append(1)
        #
        # for sn in seriesNameRes:
        #     newSeriesNameRes.append(str(sn) + '--bin')
        #     seriesType.append('line')
        #     yAxisMultiVal.append(2)




        # for elCount in elementOrder:
        res += vg.drawLineChartMultiYAxis(
            newListResCopy,
            seriesName=newSeriesNameRes,
            seriesType=seriesType,
            # label = '<b>{series.name}</b>: [endElement0] {point.x} [startElement1-endElement0] {point.y}',
            height=500,
            reversed=False,
            markerRadius=1,
            xAxisTitle='chr start pos',
            yAxisTitle=['distance(log10)', 'points per bin (' + str(scale) + ')'],
            yAxisMulti=yAxisMultiVal,
            minY=0,
            # plotLines=chrStPos
            # marginTop=30,
            # addOptions='float:left;width:' + str(percentagePlot)
        )
        #
        # res += '<div style="clear:both;"> </div>'
        #
        # for elCount in elementOrder:
        #     res += vg.drawLineChart(
        #          [listResLine[elCount]],
        #          seriesName = [seriesNameRes[elCount]],
        #          label = '<b>{series.name}</b>: [endElement0] {point.x} [value] {point.y}',
        #          height = 300,
        #          xAxisTitle = 'chr start pos',
        #          yAxisTitle = 'values',
        #          marginTop=30,
        #          addOptions='float:left;width:' + str(percentagePlot)
        #          )
        #




        # for elN in range(0, len(listResBubble)):
        #     listResBubble[elN][1] = math.log(listResBubble[elN][1], 10)


        # odpada
        #         res += vg.drawBubbleChart(
        #              listResBubble.values(),
        #              seriesName = seriesNameRes,
        #              #label = '<b>{series.name}</b>:  [endElement0] {point.x} [startElement1-endElement0] {point.y} [value] {point.z}',
        #              height = 400,
        #              xAxisTitle = 'chr start pos',
        #              yAxisTitle = 'distance',
        #              marginTop=30
        #              )

        res += '<div style="clear:both;"> </div>'

        return res

    @classmethod
    def drawInteractiveSingleV2(cls, listResLine, elementOrder, listResCopy, seriesNameRes, listResBubble, bps, scale,
                                chrLength):
        vg = visualizationGraphs()
        percentagePlot = str(int(float(100) / float(len(listResLine)))) + '%'
        # percentagePlot = '800px'

        res = ''

        # elementOrder=[0,1,2,3]




        listMaxVal = []
        for elCount in elementOrder:
            lmax = -10000
            lmin = 10000000000000000
            for elN in range(0, len(listResCopy[elCount])):
                if listResCopy[elCount][elN][0] > lmax:
                    lmax = listResCopy[elCount][elN][0]
                if listResCopy[elCount][elN][0] < lmin:
                    lmin = listResCopy[elCount][elN][0]
            listMaxVal.append([0, lmax])

        # print listMaxVal
        # print '========'
        # print listResCopy[0]
        #
        # print '----'

        # print str(listMaxVal)+ '<br \>'

        listResBubbleX = {}
        howManyPerBin = OrderedDict()
        j = 0

        for elCount in elementOrder:
            listResBubbleX[elCount] = {}

            for elN in range(0, len(listResCopy[elCount])):
                if not listResCopy[elCount][elN][0] in listResBubbleX[elCount]:
                    listResBubbleX[elCount][listResCopy[elCount][elN][0]] = 0
                listResBubbleX[elCount][listResCopy[elCount][elN][0]] += 1
            #                 if not listResCopy[elCount][elN][0] in listResBubbleX:
            #                     listResBubbleX[listResCopy[elCount][elN][0]]=[listResCopy[elCount][elN][0],y,0]
            #                 listResBubbleX[listResCopy[elCount][elN][0]]+=1

            if not elCount in howManyPerBin:
                howManyPerBin[elCount] = []

            lmin = int(math.floor(listMaxVal[j][0]) / bps)
            lmax = int(math.ceil(listMaxVal[j][1]) / bps) + 1

            addValue = 0
            # if elCount!=0:
            #     for elM in range(0, elCount):
            #         addValue += listMaxVal[elM][1]

            for vv in range(lmin, lmax):

                binStart = vv * bps
                binEnd = vv * bps + bps
                endCount = binEnd - 1

                valueCount = 0
                # print 'binStart: ' + str(binStart) + '<br \>'
                # print 'binEnd: ' + str(binEnd) + '<br \>'
                # print 'valueCount1: ' + str(valueCount) + '<br \>'



                for elN in range(0, len(listResCopy[elCount])):

                    val = listResCopy[elCount][elN][0]
                    if val >= binStart and val < binEnd:
                        # print 'val: ' + str(binStart) + '<br \>'
                        valueCount += 1

                # print 'valueCount2: ' + str(valueCount) + '<br \>'
                howManyPerBin[elCount].append([binStart + addValue, valueCount])
                howManyPerBin[elCount].append([endCount + addValue, valueCount])
                valueCount = 0
            j += 1

        # listResBubble=OrderedDict()
        # for elCount in elementOrder:
        #     listResBubble[elCount]=[]
        #     for elN in range(0, len(listResCopy[elCount])):
        #
        #         addValue=0
        #         # if elCount!=0:
        #         #     for elM in range(0, elCount):
        #         #         addValue += listMaxVal[elM][1]
        #         vLog = 0
        #         if listResCopy[elCount][elN][1]> 0:
        #             vLog = math.log(listResCopy[elCount][elN][1],10)
        #         listResBubble[elCount].append([listResCopy[elCount][elN][0]+addValue, vLog, listResBubbleX[elCount][listResCopy[elCount][elN][0]]])


        #
        # howManyPerBin2=OrderedDict()
        # j=0
        # for elCount in elementOrder:
        #     if not elCount in howManyPerBin2:
        #         howManyPerBin2[elCount]=[]
        #
        #     lmin = int(math.floor(listMaxVal[j][0]))
        #     lmax = int(math.ceil(listMaxVal[j][1])) + 1
        #
        #     print 'lmin: ' + str(lmin) + '<br \>'
        #     print 'lmax: ' + str(lmax) + '<br \>'
        #
        #     for vv in range(lmin, lmax):
        #
        #
        #         binStart = vv #1mln - 1mln+1
        #         binEnd =  vv + bps #1mln + 1 - 1mln+2
        #         endCount = binEnd-1
        #
        #         addValue=0
        #         if len(listMaxVal) > elCount and elCount!=0:
        #             addValue = listMaxVal[elCount-1][1]+1
        #
        #         valueCount = 0
        #         # print 'binStart: ' + str(binStart) + '<br \>'
        #         # print 'binEnd: ' + str(binEnd) + '<br \>'
        #         # print 'valueCount1: ' + str(valueCount) + '<br \>'
        #
        #
        #
        #         for elN in range(0, len(listResCopy[elCount])):
        #             val = listResCopy[elCount][elN][0]
        #             if val >= binStart and val < binEnd:
        #                 # print 'val: ' + str(binStart) + '<br \>'
        #                 valueCount += 1
        #
        #         # print 'valueCount2: ' + str(valueCount) + '<br \>'
        #         howManyPerBin2[elCount].append([binStart+addValue, valueCount])
        #         howManyPerBin2[elCount].append([endCount+addValue, valueCount])
        #         valueCount = 0
        #     j+=1


        # print howManyPerBin[0]

        bubbleVal = {}

        newListResCopy = []
        for elCount in elementOrder:

            addValue = 0
            # if elCount!=0:
            #     for elM in range(0, elCount):
            #         addValue += listMaxVal[elM][1]

            for elN in range(0, len(listResCopy[elCount])):
                vLog = 0
                if listResCopy[elCount][elN][1] > 0:
                    vLog = math.log(listResCopy[elCount][elN][1], 10)
                listResCopy[elCount][elN][1] = vLog
                listResCopy[elCount][elN][0] = listResCopy[elCount][elN][0] + addValue
                if not listResCopy[elCount][elN][0] in bubbleVal:
                    bubbleVal[listResCopy[elCount][elN][0]] = {}
                if not listResCopy[elCount][elN][1] in bubbleVal[listResCopy[elCount][elN][0]]:
                    bubbleVal[listResCopy[elCount][elN][0]][listResCopy[elCount][elN][1]] = 0
                bubbleVal[listResCopy[elCount][elN][0]][listResCopy[elCount][elN][1]] += 1

            newListResCopy.append(listResCopy[elCount])

        listResBubble = []
        for x, it0 in bubbleVal.items():
            for y, v in it0.items():
                listResBubble.append([x, y, v])

        # print listResBubble

        # print '<br \>'+'<br \>'+'<br \>'+'-1111--'+'<br \>'+'<br \>'+'<br \>'+'<br \>'
        # print howManyPerBin
        # print '<br \>'+'<br \>'+'<br \>'+'-2222--'+'<br \>'+'<br \>'+'<br \>'+'<br \>'


        maxVVP = -100
        for elCount in elementOrder:
            if maxVVP < len(howManyPerBin[elCount]):
                maxVVP = len(howManyPerBin[elCount])

            newhowManyPerBin = []

            ik = True
            for elN in range(0, len(howManyPerBin[elCount])):
                if elN % 2 == 0:
                    ik = True
                else:
                    if howManyPerBin[elCount][elN][1] != 0:
                        st = (howManyPerBin[elCount][elN][0] + howManyPerBin[elCount][elN - 1][0]) / 2
                        end = howManyPerBin[elCount][elN][1]
                        if scale == 'Log':
                            if end != 0:
                                end = math.log(end, 10)
                        newhowManyPerBin.append([st, end])
                    else:
                        st = (howManyPerBin[elCount][elN][0] + howManyPerBin[elCount][elN - 1][0]) / 2
                        end = None
                        newhowManyPerBin.append([st, end])
                    ik = False
            if ik == False:
                st = howManyPerBin[elCount][elN][0]
                end = howManyPerBin[elCount][elN][1]
                if scale == 'Log':
                    if end != 0:
                        end = math.log(end, 10)
                newhowManyPerBin.append([st, end])

            newListResCopy.append(newhowManyPerBin)


        #         print newListResCopy
        #         print '<br \>'+'<br \>'+'<br \>'+'-3333--'+'<br \>'+'<br \>'+'<br \>'+'<br \>'

        seriesType = []
        newSeriesNameRes = []
        yAxisMultiVal = []
        for sn in seriesNameRes:
            newSeriesNameRes.append(sn)
            seriesType.append('scatter')
            yAxisMultiVal.append(0)

        for sn in seriesNameRes:
            newSeriesNameRes.append(str(sn) + '-- point')
            seriesType.append('line')
            yAxisMultiVal.append(1)

        allSeriesPoints = []

        howManyPerBinC = copy.deepcopy(howManyPerBin)

        for elN in range(0, maxVVP):
            i = 0
            for elCount in howManyPerBinC:
                if elN < len(howManyPerBinC[elCount]):
                    if i == 0:
                        allSeriesPoints.append(howManyPerBinC[elCount][elN])
                    else:
                        allSeriesPoints[elN][1] += howManyPerBinC[elCount][elN][1]
                    i += 1
                    # print str(elCount) + '   ' + str(len(howManyPerBinC[elCount])) + ' - ' + str(maxVVP) + '   ' + str(elN) +  '    ' + str(howManyPerBinC[elCount][elN])+ '===' + str(allSeriesPoints[elN]) + '<br \>'
                    # print '------' + '<br \>'
        newSeriesNameRes.append('all points')
        seriesType.append('line')
        yAxisMultiVal.append(1)

        newSeriesNameResAvg = []

        ik = True
        for elN in range(0, len(allSeriesPoints)):
            if elN % 2 == 0:
                ik = True
            else:
                if allSeriesPoints[elN][1] != 0:
                    st = (allSeriesPoints[elN][0] + allSeriesPoints[elN - 1][0]) / 2
                    end = allSeriesPoints[elN][1]
                    if scale == 'Log':
                        if end != 0:
                            end = math.log(end, 10)
                    newSeriesNameResAvg.append([st, end])
                else:
                    st = (allSeriesPoints[elN][0] + allSeriesPoints[elN - 1][0]) / 2
                    end = None
                    newSeriesNameResAvg.append([st, end])
                ik = False
        if ik == False:
            st = allSeriesPoints[elN][0]
            end = allSeriesPoints[elN][1]
            if scale == 'Log':
                if end != 0:
                    end = math.log(end, 10)
            newSeriesNameResAvg.append([st, end])



        #         print allSeriesPoints

        #
        # for sn in seriesNameRes:
        #     newSeriesNameRes.append(str(sn) + '--bin')
        #     seriesType.append('line')
        #     yAxisMultiVal.append(2)


        # print '<br \>'
        # print '<br \>'
        # print '<br \>'
        #
        # print allSeriesPoints
        #
        # print '<br \>'
        # print '<br \>'
        # print '<br \>'
        # print '<br \>'
        # print newListResCopy

        # print allSeriesPoints
        # print '<br \>'
        # print '<br \>'
        # print '<br \>'
        # print '<br \>'
        #
        # print newSeriesNameResAvg


        lineHtml = OrderedDict()

        ij = 0
        for key, it0 in howManyPerBin.iteritems():
            for it1 in it0:
                if ij % 2 == 1:
                    if not str(preV) + '-' + str(it1[0]) in lineHtml:
                        lineHtml[str(preV) + '-' + str(it1[0])] = []
                    lineHtml[str(preV) + '-' + str(it1[0])].append(it1[1])
                preV = it1[0]
                ij += 1

        res += vg.drawLineChart(
            # [allSeriesPoints]+[newSeriesNameResAvg],
            [newSeriesNameResAvg],
            # seriesName = ['all points', 'all point bin avg'],
            seriesName=['all point bin avg'],
            height=300,
            xAxisTitle='chr start pos',
            yAxisTitle='points per bin (' + str(scale) + ')',
            minY=0,
            plotLines=chrLength.values(),
            plotLinesName=chrLength.keys()
        )

        # for elCount in elementOrder:
        res += vg.drawLineChartMultiYAxis(
            newListResCopy,  # +[newSeriesNameResAvg],
            seriesName=newSeriesNameRes,
            seriesType=seriesType,
            # label = '<b>{series.name}</b>: [endElement0] {point.x} [startElement1-endElement0] {point.y}',
            height=500,
            reversed=False,
            markerRadius=1,
            xAxisTitle='chr start pos',
            yAxisTitle=['distance(log10)', 'points per bin (' + str(scale) + ')'],
            yAxisMulti=yAxisMultiVal,
            minY=0,
            plotLines=chrLength.values(),
            plotLinesName=chrLength.keys()
            # marginTop=30,
            # addOptions='float:left;width:' + str(percentagePlot)
        )
        #
        # res += '<div style="clear:both;"> </div>'
        #
        # for elCount in elementOrder:
        #     res += vg.drawLineChart(
        #          [listResLine[elCount]],
        #          seriesName = [seriesNameRes[elCount]],
        #          label = '<b>{series.name}</b>: [endElement0] {point.x} [value] {point.y}',
        #          height = 300,
        #          xAxisTitle = 'chr start pos',
        #          yAxisTitle = 'values',
        #          marginTop=30,
        #          addOptions='float:left;width:' + str(percentagePlot)
        #          )
        #




        # for elN in range(0, len(listResBubble)):
        #     listResBubble[elN][1] = math.log(listResBubble[elN][1], 10)



        res += vg.drawBubbleChart(
            [listResBubble],
            seriesName=['all series'],
            label='<b>{series.name}</b>:  [endElement0] {point.x} [startElement1-endElement0] {point.y} [value] {point.z}',
            height=400,
            xAxisTitle='chr start pos',
            yAxisTitle='distance log',
            marginTop=30,
            minY=0,
            plotLines=chrLength.values(),
            plotLinesName=chrLength.keys()
        )

        res += '<div style="clear:both;"> </div>'

        return res, lineHtml

    @classmethod
    def sortChrDict(cls, chr):

        remeberString = []
        keysList = []
        for el in chr.keys():
            try:
                elC = int(el.replace('chr', ''))
                keysList.append(elC)
            except:
                remeberString.append(el.replace('chr', ''))

        sChr = sorted(keysList) + sorted(remeberString)

        chrDict = OrderedDict()
        chrLength = OrderedDict()
        val = 0
        for elChr in sChr:
            el = 'chr' + str(elChr)
            chrDict[el] = chr[el]
            chrLength[el] = val
            val += chr[el]

        return chrDict, chrLength

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        dataDict = OrderedDict()
        dataDictLine = OrderedDict()
        elementOrder = []

        scale = choices.scale

        bps = choices.bps
        if bps == '':
            bps = 10000
        else:
            bps = int(bps)

        # dataDict {endPosition: {val: end-start, tot: howMany} ...}

        gSuite = getGSuiteFromGalaxyTN(choices.gSuite)
        chrOrder, chrLength = makeRainfallPlots.sortChrDict(GenomeInfo.getStdChrLengthDict(gSuite.genome))

        chrList = {}
        chrStPos = []
        sumChr = 0
        for chrLen in chrOrder.values():
            sumChr += chrLen
            chrStPos.append(sumChr)

        # parse the tracks!
        for track in gSuite.allTrackTitles():
            gSuiteTrack = gSuite.getTrackFromTitle(track)
            trackName = track

            dataDict[trackName] = OrderedDict()
            dataDictLine[trackName] = OrderedDict()

            newDict = {}
            with open(gSuiteTrack.path, 'r') as f:
                i = 0
                for x in f.readlines():
                    el = x.strip('\n').split('\t')
                    if len(el) >= 2:
                        if not el[0] in newDict:
                            newDict[el[0]] = []

                        try:
                            newDict[el[0]].append([el[0], int(el[1]), int(el[2])])
                        except:
                            pass
                i += 1

            newDict2 = OrderedDict()
            for key, it in chrLength.items():
                if key in newDict:
                    newDict2[key] = sorted(newDict[key], key=lambda x: x[1])

            for key, it in newDict2.items():
                if i == 0:
                    chr = key
                i = 0
                prevEnd = 0
                label = 0

                for el in it:
                    if len(el) >= 2:

                        if not int(el[1]) in dataDictLine[trackName]:
                            dataDictLine[trackName][int(el[1])] = 1
                        start = int(el[1])
                        if prevEnd != 0:
                            if not label in dataDict[trackName]:
                                dataDict[trackName][label] = OrderedDict()
                                dataDict[trackName][label]['val'] = 0
                                dataDict[trackName][label]['tot'] = 0
                            dataDict[trackName][label]['val'] += start - prevEnd
                            dataDict[trackName][label]['tot'] += 1

                        label = int(el[1]) + int(chrLength[el[0]])
                        prevEnd = int(el[1])
                        i += 1

            elementOrder.append(i)

        listResCopy = []
        for key0, it0 in dataDict.iteritems():
            listResPart = []
            for key2 in sorted(it0):
                listResPart.append([key2, it0[key2]['val']])
            listResCopy.append(listResPart)

        elementOrder = sorted(range(len(elementOrder)), key=lambda k: elementOrder[k])

        if choices.color == 'Single color':

            seriesNameRes = []
            listRes = []
            listResBubble = []
            listResLine = []

            # counting part
            for key0, it0 in dataDictLine.iteritems():
                listResLinePart = []
                i = 0
                for key2 in sorted(it0):
                    en = key2
                    if i == 0:
                        for elK in range(key2 - 2, key2):
                            listResLinePart.append([elK, 0])
                        st = key2 + 1
                    else:
                        for elK in range(en - 2, en):
                            listResLinePart.append([elK, 0])
                        st = en
                    listResLinePart.append([key2, it0[key2]])
                    i += 1
                for elK in range(key2 + 1, key2 + 2):
                    listResLinePart.append([elK, 0])

                listResLine.append(listResLinePart)

            for key0, it0 in dataDict.iteritems():
                seriesNameRes.append(key0)

                for key2 in sorted(it0):
                    if not [key2, it0[key2]['val']] in listRes:
                        listRes.append([key2, it0[key2]['val']])
                        listResBubble.append([key2, it0[key2]['val'], it0[key2]['tot']])
                    else:
                        for elN in range(0, len(listResBubble)):
                            if listResBubble[elN][0] == key2 and listResBubble[elN][1] == it0[key2]['val']:
                                listResBubble[elN][2] += it0[key2]['tot']

            if choices.interactive == 'Interactive':

                lineHtml = ''
                if choices.multiPlot == 'Single':
                    # res = makeRainfallPlots.drawInteractiveSingle(seriesNameRes, listRes, listResLine, listResBubble)
                    res, lineHtml = makeRainfallPlots.drawInteractiveSingleV2(listResLine, elementOrder, listResCopy,
                                                                              seriesNameRes, listResBubble, bps, scale,
                                                                              chrLength)

                if choices.multiPlot == 'Multi':
                    res = makeRainfallPlots.drawInteractiveMulti(listResLine, elementOrder, listResCopy, seriesNameRes,
                                                                 listResBubble, bps, scale, chrStPos)

                htmlCore = HtmlCore()
                htmlCore.begin()
                htmlCore.line('Bin size: ' + str(bps))

                if lineHtml != '':
                    sumLine = []
                    for sN in seriesNameRes:
                        sumLine.append(0)
                    htmlCore.tableHeader(['Bins'] + seriesNameRes, sortable=True, tableId=1)
                    for key, it0 in lineHtml.iteritems():
                        htmlCore.tableLine([key] + it0)
                        for iN in range(0, len(it0)):
                            sumLine[iN] += it0[iN]
                    htmlCore.tableLine(['<b>Sum</b>'] + sumLine)

                htmlCore.line(res)
                htmlCore.end()
                htmlCore.hideToggle(styleClass='debug')
                print htmlCore

                # if choices.interactive == 'Figure':
                #     fig = plt.figure()
                #
                #     #scatter plot
                #     plotOutput = GalaxyRunSpecificFile(['Scatter', 'scatter.png'], galaxyFn)
                #     xListRes = []
                #     yListRes = []
                #     for el in listRes:
                #         xListRes.append(el[0])
                #         yListRes.append(el[1])
                #
                #     for i in range(0,1):
                #         x = np.array(xListRes)
                #         y = np.array(yListRes)
                #         scale = 20
                #         plt.scatter(x, y,  s=scale)
                #     plt.grid(True)
                #     plt.savefig(plotOutput.getDiskPath(ensurePath=True))
                #
                #     core = HtmlCore()
                #     core.begin()
                #     core.divBegin(divId='plot')
                #     core.image(plotOutput.getURL())
                #     core.divEnd()
                #     core.end()
                #     print core

        if choices.color == 'Various colors':

            seriesNameRes = []
            listRes = []
            listResBubble = []
            listResLine = []

            for key0, it0 in dataDictLine.iteritems():
                listResLinePart = []
                i = 0
                for key2 in sorted(it0):
                    listResLinePart.append([key2, it0[key2]])
                    i += 1

                listResLine.append(listResLinePart)

            listResBubbleTemp = []
            listResBubble1 = []
            for key0, it0 in dataDict.iteritems():
                seriesNameRes.append(key0)
                listResPart = []
                listResBubblePart = []
                for key2 in sorted(it0):
                    listResPart.append([key2, it0[key2]['val']])
                    listResBubblePart.append([key2, it0[key2]['val'], it0[key2]['tot']])
                    if [key2, it0[key2]['val']] not in listResBubbleTemp:
                        listResBubbleTemp.append([key2, it0[key2]['val']])
                        listResBubble1.append([key2, it0[key2]['val'], it0[key2]['tot']])
                    else:
                        for elN in range(0, len(listResBubble1)):
                            if listResBubble1[elN][0] == key2 and listResBubble1[elN][1] == it0[key2]['val']:
                                listResBubble1[elN][2] += it0[key2]['tot']
                listRes.append(listResPart)
                listResBubble.append(listResBubblePart)

            if choices.interactive == 'Interactive':
                res = makeRainfallPlots.drawInteractiveVariousColor(seriesNameRes, listRes, listResLine, listResBubble)

                htmlCore = HtmlCore()
                htmlCore.begin()
                htmlCore.line('Bin size: ' + str(bps))
                htmlCore.line(res)
                htmlCore.end()
                htmlCore.hideToggle(styleClass='debug')
                print htmlCore

                # if choices.interactive == 'Figure':
                #     f, (ax1, ax2, ax3) = plt.subplots(3, sharex=True, sharey=False, figsize=(15,10))
                #
                #     #scatter plot
                #     plotOutput = GalaxyRunSpecificFile(['plotsGroup', 'plot.png'], galaxyFn)
                #
                #     colList = [
                #           '#7cb5ec',
                #           '#434348',
                #           '#99D6D6',
                #           '#005C5C',
                #           '#292933',
                #           '#336699',
                #           '#8085e9',
                #           '#B2CCFF',
                #           '#90ed7d',
                #           '#f7a35c',
                #           '#f15c80',
                #           '#e4d354',
                #           '#8085e8',
                #           '#8d4653',
                #           '#6699FF',
                #           '#91e8e1',
                #           '#7A991F',
                #           '#525266',
                #           '#1A334C',
                #           '#334C80',
                #           '#292900',
                #           '#142900',
                #           '#99993D',
                #           '#009999',
                #           '#1A1A0A',
                #           '#5C85AD',
                #           '#804C4C',
                #           '#1A0F0F',
                #           '#A3A3CC',
                #           '#660033',
                #           '#3D4C0F',
                #           '#fde720',
                #           '#554e44',
                #           '#1ce1ce',
                #           '#dedbbb',
                #           '#facade',
                #           '#baff1e',
                #           '#aba5ed',
                #           '#f2b3b3',
                #           '#f9e0e0',
                #           '#abcdef',
                #           '#f9dcd3',
                #           '#eb9180',
                #           '#c2dde5',
                #            '#008B8B',
                #         '#B8860B',
                #         '#A9A9A9',
                #         '#006400',
                #         '#BDB76B',
                #         '#8B008B',
                #         '#556B2F',
                #         '#FF8C00',
                #         '#9932CC',
                #         '#8B0000',
                #         '#E9967A',
                #         '#8FBC8F',
                #         '#483D8B',
                #         '#2F4F4F',
                #         '#00CED1',
                #         '#9400D3',
                #         '#FF1493',
                #         '#00BFFF',
                #         '#696969',
                #         '#1E90FF',
                #         '#B22222',
                #         '#FFFAF0',
                #         '#228B22',
                #         '#FF00FF',
                #         '#DCDCDC',
                #         '#F8F8FF',
                #         '#FFD700',
                #         '#DAA520',
                #             '#808080',
                #             '#008000',
                #             '#ADFF2F',
                #             '#F0FFF0',
                #             '#FF69B4',
                #             '#CD5C5C',
                #             '#4B0082',
                #             '#FFFFF0',
                #             '#F0E68C',
                #             '#E6E6FA',
                #             '#FFF0F5',
                #             '#7CFC00',
                #             '#FFFACD',
                #             '#ADD8E6',
                #             '#F08080',
                #             '#E0FFFF',
                #             '#FAFAD2',
                #             '#D3D3D3',
                #             '#90EE90',
                #             '#FFB6C1',
                #             '#FFA07A',
                #             '#20B2AA',
                #             '#87CEFA',
                #             '#778899',
                #             '#B0C4DE',
                #             '#FFFFE0',
                #             '#00FF00',
                #             '#32CD32',
                #             '#FAF0E6',
                #             '#FF00FF',
                #             '#800000',
                #             '#66CDAA',
                #             '#0000CD',
                #             '#BA55D3',
                #             '#9370DB',
                #             '#3CB371',
                #             '#7B68EE',
                #             '#00FA9A',
                #             '#48D1CC',
                #             '#C71585',
                #             '#191970',
                #             '#F5FFFA',
                #             '#FFE4E1',
                #             '#FFE4B5',
                #             '#FFDEAD',
                #             '#000080',
                #             '#FDF5E6',
                #             '#808000',
                #             '#6B8E23',
                #             '#FFA500',
                #             '#FF4500',
                #             '#DA70D6',
                #             '#EEE8AA',
                #             '#98FB98',
                #             '#AFEEEE',
                #             '#DB7093',
                #             '#FFEFD5',
                #             '#FFDAB9',
                #             '#CD853F',
                #             '#FFC0CB',
                #             '#DDA0DD',
                #             '#B0E0E6',
                #             '#800080',
                #             '#663399',
                #             '#FF0000',
                #             '#BC8F8F',
                #             '#4169E1',
                #             '#8B4513',
                #             '#FA8072',
                #             '#F4A460',
                #             '#2E8B57',
                #             '#FFF5EE',
                #             '#A0522D',
                #             '#C0C0C0',
                #             '#87CEEB',
                #             '#6A5ACD',
                #             '#708090',
                #             '#FFFAFA',
                #             '#00FF7F',
                #             '#4682B4'
                #           ];
                #
                #
                #     #line plot
                #     i=0
                #     for elList in listResLine:
                #         xListRes = []
                #         yListRes = []
                #         wListRes=[]
                #         sizes=[]
                #         scale=10
                #
                #         num = ((float(i)/float(len(listResLine))) - 0.0)/(1.0 - 0.0) * (0.9  - 0.1) + 0.1
                #         print num
                #         for el in elList:
                #             xListRes.append(el[0])
                #             yListRes.append(el[1])
                #             wListRes.append(num)
                #
                #         x = np.array(xListRes)
                #         y = np.array(yListRes)
                #         w = np.array(wListRes)
                #
                #
                #         ax1.plot(x,w, c=colList[i], label=dataDictLine.keys()[i], linewidth=4.0)
                #         i+=1
                #
                #
                #     #scatter plot
                #     i=0
                #     for elList in listRes:
                #         xListRes = []
                #         yListRes = []
                #         sizes=[]
                #         scale=10
                #         for el in elList:
                #             xListRes.append(el[0])
                #             yListRes.append(el[1])
                #
                #         x = np.array(xListRes)
                #         y = np.array(yListRes)
                #
                #
                #         ax3.scatter(x, y, s=scale, c=colList[i], label=dataDictLine.keys()[i])
                #         i+=1
                #
                #     i=0
                #
                #     #bubble plot
                #     xListRes = []
                #     yListRes = []
                #     sizes=[]
                #     scale=100
                #     #sizeUnique=[]
                #     for el in listResBubble1:
                #         xListRes.append(el[0])
                #         yListRes.append(el[1])
                #         sizes.append(el[2]*scale)
                #
                #
                #     x = np.array(xListRes)
                #     y = np.array(yListRes)
                #
                #     ax2.scatter(x, y , s=sizes, c=colList[i], label=dataDictLine.keys()[i], linewidths=1, edgecolor='g')
                #     i+=1
                #
                #
                #     ax1.grid(True)
                #     ax2.grid(True)
                #     ax3.grid(True)
                #
                #     ax1.legend(loc='upper left', fontsize=8)
                #
                #
                #     plt.savefig(plotOutput.getDiskPath(ensurePath=True))
                #
                #     core = HtmlCore()
                #     core.begin()
                #     core.divBegin(divId='plot')
                #     core.image(plotOutput.getURL())
                #     core.divEnd()
                #     core.end()
                #     print core
                #

    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'customhtml'


class rainfallPlotsGSuite(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Rainfall plots gSuite"

    @staticmethod
    def getInputBoxNames():
        return [

            ('Select files', 'files'),
            ('Select option', 'color'),
            ('Select type of results', 'interactive'),
            ('Select type of plotting', 'multiPlot'),
            ('Select bps', 'bps')
        ]

    @staticmethod
    def getOptionsBoxFiles():
        return ('__multihistory__', 'bed')

    @staticmethod
    def getOptionsBoxColor(prevChoices):
        return ['Single color', 'Various colors']

    @staticmethod
    def getOptionsBoxInteractive(prevChoices):
        return ['Interactive', 'Figure']

    @staticmethod
    def getOptionsBoxMultiPlot(prevChoices):
        return ['Single', 'Multi']

    @staticmethod
    def getOptionsBoxBps(prevChoices):
        return ''

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        from quick.webtools.restricted.visualization.visualizationGraphs import visualizationGraphs
        import numpy as np
        import matplotlib.pyplot as plt

        tf = choices.files
        trackList = tf.values()

        dataDict = OrderedDict()
        dataDictLine = OrderedDict()

        elementOrder = []
        # dataDict {endPosition: {val: end-start, tot: howMany} ...}

        # parse the tracks!
        for track in trackList:
            trackName = track.split(':')[len(track.split(':')) - 1].replace('%20', '-')
            dataDict[trackName] = OrderedDict()
            dataDictLine[trackName] = OrderedDict()
            with open(ExternalTrackManager.extractFnFromGalaxyTN(track.split(':')), 'r') as f:
                i = 0
                prevEnd = 0
                label = 0

                for x in f.readlines():
                    el = x.strip('\n').split('\t')
                    if not int(el[1]) in dataDictLine[trackName]:
                        dataDictLine[trackName][int(el[1])] = 1
                    start = int(el[1])
                    if prevEnd != 0:
                        if not label in dataDict[trackName]:
                            dataDict[trackName][label] = OrderedDict()
                            dataDict[trackName][label]['val'] = 0
                            dataDict[trackName][label]['tot'] = 0
                        dataDict[trackName][label]['val'] += start - prevEnd
                        dataDict[trackName][label]['tot'] += 1
                    label = int(el[1])
                    prevEnd = int(el[1])
                    i += 1

                elementOrder.append(i)

            f.closed

        listResCopy = []
        for key0, it0 in dataDict.iteritems():
            listResPart = []
            for key2 in sorted(it0):
                listResPart.append([key2, it0[key2]['val']])
            listResCopy.append(listResPart)

        elementOrder = sorted(range(len(elementOrder)), key=lambda k: elementOrder[k])

        if choices.color == 'Various colors':

            seriesNameRes = []
            listRes = []
            listResBubble = []
            listResLine = []

            for key0, it0 in dataDictLine.iteritems():
                listResLinePart = []
                i = 0
                for key2 in sorted(it0):
                    listResLinePart.append([key2, it0[key2]])
                    i += 1

                listResLine.append(listResLinePart)

            listResBubbleTemp = []
            listResBubble1 = []
            for key0, it0 in dataDict.iteritems():
                seriesNameRes.append(key0)
                listResPart = []
                listResBubblePart = []
                for key2 in sorted(it0):
                    listResPart.append([key2, it0[key2]['val']])
                    listResBubblePart.append([key2, it0[key2]['val'], it0[key2]['tot']])
                    if [key2, it0[key2]['val']] not in listResBubbleTemp:
                        listResBubbleTemp.append([key2, it0[key2]['val']])
                        listResBubble1.append([key2, it0[key2]['val'], it0[key2]['tot']])
                    else:
                        for elN in range(0, len(listResBubble1)):
                            if listResBubble1[elN][0] == key2 and listResBubble1[elN][1] == it0[key2]['val']:
                                listResBubble1[elN][2] += it0[key2]['tot']
                listRes.append(listResPart)
                listResBubble.append(listResBubblePart)

            if choices.interactive == 'Interactive':
                vg = visualizationGraphs()
                res = vg.drawScatterChart(
                    listRes,
                    seriesName=seriesNameRes,
                    # titleText = ['Scatter plot'],
                    label='<b>{series.name}</b>: {point.x} {point.y}',
                    height=300,
                    xAxisTitle='chr start pos',
                    yAxisTitle='distance',
                    marginTop=30
                )

                res += vg.drawLineChart(
                    listResLine,
                    seriesName=seriesNameRes,
                    # label = '<b>{series.name}</b>: X:{point.x} Y:{point.y} value: {point.z}',
                    height=300,
                    xAxisTitle='chr start pos',
                    yAxisTitle='values',
                    marginTop=30
                )

                res += vg.drawBubbleChart(
                    listResBubble,
                    seriesName=seriesNameRes,
                    label='<b>{series.name}</b>: X:{point.x} Y:{point.y} value: {point.z}',
                    height=300,
                    xAxisTitle='chr start pos',
                    yAxisTitle='distance',
                    marginTop=30
                )

                htmlCore = HtmlCore()
                htmlCore.begin()
                htmlCore.line(res)
                htmlCore.end()
                htmlCore.hideToggle(styleClass='debug')
                print htmlCore

            if choices.interactive == 'Figure':
                f, (ax1, ax2, ax3) = plt.subplots(3, sharex=True, sharey=False, figsize=(15, 10))

                # scatter plot
                plotOutput = GalaxyRunSpecificFile(['plotsGroup', 'plot.png'], galaxyFn)

                colList = [
                    '#7cb5ec',
                    '#434348',
                    '#99D6D6',
                    '#005C5C',
                    '#292933',
                    '#336699',
                    '#8085e9',
                    '#B2CCFF',
                    '#90ed7d',
                    '#f7a35c',
                    '#f15c80',
                    '#e4d354',
                    '#8085e8',
                    '#8d4653',
                    '#6699FF',
                    '#91e8e1',
                    '#7A991F',
                    '#525266',
                    '#1A334C',
                    '#334C80',
                    '#292900',
                    '#142900',
                    '#99993D',
                    '#009999',
                    '#1A1A0A',
                    '#5C85AD',
                    '#804C4C',
                    '#1A0F0F',
                    '#A3A3CC',
                    '#660033',
                    '#3D4C0F',
                    '#fde720',
                    '#554e44',
                    '#1ce1ce',
                    '#dedbbb',
                    '#facade',
                    '#baff1e',
                    '#aba5ed',
                    '#f2b3b3',
                    '#f9e0e0',
                    '#abcdef',
                    '#f9dcd3',
                    '#eb9180',
                    '#c2dde5',
                    '#008B8B',
                    '#B8860B',
                    '#A9A9A9',
                    '#006400',
                    '#BDB76B',
                    '#8B008B',
                    '#556B2F',
                    '#FF8C00',
                    '#9932CC',
                    '#8B0000',
                    '#E9967A',
                    '#8FBC8F',
                    '#483D8B',
                    '#2F4F4F',
                    '#00CED1',
                    '#9400D3',
                    '#FF1493',
                    '#00BFFF',
                    '#696969',
                    '#1E90FF',
                    '#B22222',
                    '#FFFAF0',
                    '#228B22',
                    '#FF00FF',
                    '#DCDCDC',
                    '#F8F8FF',
                    '#FFD700',
                    '#DAA520',
                    '#808080',
                    '#008000',
                    '#ADFF2F',
                    '#F0FFF0',
                    '#FF69B4',
                    '#CD5C5C',
                    '#4B0082',
                    '#FFFFF0',
                    '#F0E68C',
                    '#E6E6FA',
                    '#FFF0F5',
                    '#7CFC00',
                    '#FFFACD',
                    '#ADD8E6',
                    '#F08080',
                    '#E0FFFF',
                    '#FAFAD2',
                    '#D3D3D3',
                    '#90EE90',
                    '#FFB6C1',
                    '#FFA07A',
                    '#20B2AA',
                    '#87CEFA',
                    '#778899',
                    '#B0C4DE',
                    '#FFFFE0',
                    '#00FF00',
                    '#32CD32',
                    '#FAF0E6',
                    '#FF00FF',
                    '#800000',
                    '#66CDAA',
                    '#0000CD',
                    '#BA55D3',
                    '#9370DB',
                    '#3CB371',
                    '#7B68EE',
                    '#00FA9A',
                    '#48D1CC',
                    '#C71585',
                    '#191970',
                    '#F5FFFA',
                    '#FFE4E1',
                    '#FFE4B5',
                    '#FFDEAD',
                    '#000080',
                    '#FDF5E6',
                    '#808000',
                    '#6B8E23',
                    '#FFA500',
                    '#FF4500',
                    '#DA70D6',
                    '#EEE8AA',
                    '#98FB98',
                    '#AFEEEE',
                    '#DB7093',
                    '#FFEFD5',
                    '#FFDAB9',
                    '#CD853F',
                    '#FFC0CB',
                    '#DDA0DD',
                    '#B0E0E6',
                    '#800080',
                    '#663399',
                    '#FF0000',
                    '#BC8F8F',
                    '#4169E1',
                    '#8B4513',
                    '#FA8072',
                    '#F4A460',
                    '#2E8B57',
                    '#FFF5EE',
                    '#A0522D',
                    '#C0C0C0',
                    '#87CEEB',
                    '#6A5ACD',
                    '#708090',
                    '#FFFAFA',
                    '#00FF7F',
                    '#4682B4'
                ];

                # line plot
                i = 0
                for elList in listResLine:
                    xListRes = []
                    yListRes = []
                    wListRes = []
                    sizes = []
                    scale = 10

                    num = ((float(i) / float(len(listResLine))) - 0.0) / (1.0 - 0.0) * (0.9 - 0.1) + 0.1
                    print num
                    for el in elList:
                        xListRes.append(el[0])
                        yListRes.append(el[1])
                        wListRes.append(num)

                    x = np.array(xListRes)
                    y = np.array(yListRes)
                    w = np.array(wListRes)

                    ax1.plot(x, w, c=colList[i], label=dataDictLine.keys()[i], linewidth=4.0)
                    i += 1

                # scatter plot
                i = 0
                for elList in listRes:
                    xListRes = []
                    yListRes = []
                    sizes = []
                    scale = 10
                    for el in elList:
                        xListRes.append(el[0])
                        yListRes.append(el[1])

                    x = np.array(xListRes)
                    y = np.array(yListRes)

                    ax3.scatter(x, y, s=scale, c=colList[i], label=dataDictLine.keys()[i])
                    i += 1

                i = 0

                # bubble plot
                xListRes = []
                yListRes = []
                sizes = []
                scale = 100
                # sizeUnique=[]
                for el in listResBubble1:
                    xListRes.append(el[0])
                    yListRes.append(el[1])
                    sizes.append(el[2] * scale)

                x = np.array(xListRes)
                y = np.array(yListRes)

                ax2.scatter(x, y, s=sizes, c=colList[i], label=dataDictLine.keys()[i], linewidths=1, edgecolor='g')
                i += 1

                ax1.grid(True)
                ax2.grid(True)
                ax3.grid(True)

                ax1.legend(loc='upper left', fontsize=8)

                plt.savefig(plotOutput.getDiskPath(ensurePath=True))

                core = HtmlCore()
                core.begin()
                core.divBegin(divId='plot')
                core.image(plotOutput.getURL())
                core.divEnd()
                core.end()
                print core

        if choices.color == 'Single color':

            seriesNameRes = []
            listRes = []
            listResBubble = []
            listResLine = []
            #         maxVal=0
            #         for key0, it0 in dataDictLine.iteritems():
            #             if maxVal < max(sorted(it0)):
            #                 maxVal = max(sorted(it0))

            # counting part
            for key0, it0 in dataDictLine.iteritems():
                listResLinePart = []
                i = 0
                for key2 in sorted(it0):
                    en = key2
                    if i == 0:
                        for elK in range(key2 - 2, key2):
                            listResLinePart.append([elK, 0])
                        st = key2 + 1
                    else:
                        for elK in range(en - 2, en):
                            listResLinePart.append([elK, 0])
                        st = en
                    listResLinePart.append([key2, it0[key2]])
                    i += 1
                for elK in range(key2 + 1, key2 + 2):
                    listResLinePart.append([elK, 0])

                listResLine.append(listResLinePart)

            for key0, it0 in dataDict.iteritems():
                seriesNameRes.append(key0)

                for key2 in sorted(it0):
                    if not [key2, it0[key2]['val']] in listRes:
                        listRes.append([key2, it0[key2]['val']])
                        listResBubble.append([key2, it0[key2]['val'], it0[key2]['tot']])
                    else:
                        for elN in range(0, len(listResBubble)):
                            if listResBubble[elN][0] == key2 and listResBubble[elN][1] == it0[key2]['val']:
                                listResBubble[elN][2] += it0[key2]['tot']

            if choices.interactive == 'Figure':
                fig = plt.figure()

                # scatter plot
                plotOutput = GalaxyRunSpecificFile(['Scatter', 'scatter.png'], galaxyFn)
                xListRes = []
                yListRes = []
                for el in listRes:
                    xListRes.append(el[0])
                    yListRes.append(el[1])

                for i in range(0, 1):
                    x = np.array(xListRes)
                    y = np.array(yListRes)
                    scale = 20
                    plt.scatter(x, y, s=scale)
                plt.grid(True)
                plt.savefig(plotOutput.getDiskPath(ensurePath=True))

                core = HtmlCore()
                core.begin()
                core.divBegin(divId='plot')
                core.image(plotOutput.getURL())
                core.divEnd()
                core.end()
                print core

            if choices.interactive == 'Interactive':

                vg = visualizationGraphs()
                if choices.multiPlot == 'Single':
                    res = vg.drawScatterChart(
                        [listRes],
                        seriesName=['All Series'],
                        # titleText = ['Scatter plot'],
                        label='<b>{series.name}</b>: {point.x} {point.y}',
                        height=300,
                        xAxisTitle='chr start pos',
                        yAxisTitle='distance',
                        marginTop=30
                    )
                    res += vg.drawLineChart(
                        listResLine,
                        seriesName=seriesNameRes,
                        # label = '<b>{series.name}</b>: X:{point.x} Y:{point.y} value: {point.z}',
                        height=300,
                        xAxisTitle='chr start pos',
                        yAxisTitle='values',
                        marginTop=30
                    )
                    res += vg.drawBubbleChart(
                        [listResBubble],
                        seriesName=['All Series'],
                        label='<b>{series.name}</b>: X:{point.x} Y:{point.y} value: {point.z}',
                        height=300,
                        xAxisTitle='chr start pos',
                        yAxisTitle='distance',
                        marginTop=30
                    )

                if choices.multiPlot == 'Multi':

                    percentagePlot = str(int(float(100) / float(len(listResLine)))) + '%'
                    # percentagePlot = '800px'




                    res = ''

                    for elCount in elementOrder:

                        for elN in range(0, len(listResCopy[elCount])):
                            listResCopy[elCount][elN][1] = math.log(listResCopy[elCount][elN][1], 10)

                        res += vg.drawScatterChart(
                            [listResCopy[elCount]],
                            seriesName=[seriesNameRes[elCount]],
                            # titleText = ['Scatter plot'],
                            label='<b>{series.name}</b>: [endElement0] {point.x} [startElement1-endElement0] {point.y}',
                            height=300,
                            xAxisTitle='chr start pos',
                            yAxisTitle='distance (log)',
                            marginTop=30,
                            addOptions='float:left;width:' + str(percentagePlot)
                        )

                    res += '<div style="clear:both;"> </div>'

                    for elCount in elementOrder:
                        res += vg.drawLineChart(
                            [listResLine[elCount]],
                            seriesName=[seriesNameRes[elCount]],
                            label='<b>{series.name}</b>: [endElement0] {point.x} [value] {point.y}',
                            height=300,
                            xAxisTitle='chr start pos',
                            yAxisTitle='values',
                            marginTop=30,
                            addOptions='float:left;width:' + str(percentagePlot)
                        )

                    res += '<div style="clear:both;"> </div>'

                # for elN in range(0, len(listResBubble)):
                #     listResBubble[elN][1] = math.log(listResBubble[elN][1], 10)
                #
                # res += vg.drawBubbleChart(
                #      [listResBubble],
                #      seriesName = ['All Series'],
                #      label = '<b>{series.name}</b>:  [endElement0] {point.x} [startElement1-endElement0] {point.y} [value] {point.z}',
                #      height = 300,
                #      xAxisTitle = 'chr start pos',
                #      yAxisTitle = 'distance',
                #      marginTop=30
                #      )


                htmlCore = HtmlCore()
                htmlCore.begin()
                htmlCore.line(res)
                htmlCore.end()
                htmlCore.hideToggle(styleClass='debug')
                print htmlCore

                # code for R which WORKS!
                # openRfigure from quick.util.static
                # GalaxyRunSpecificFile
                # use rPlot
                # closeRfigure
                # getLink or getEmbeddedImage

            #         from proto.RSetup import robjects, r
            #         rPlot = robjects.r.plot
            #         rPlot([1,2,3], [4,5,6], type='p', xlim=[0,2], ylim=[0,2], main = 'tit', xlab='xlab', ylab='ylab')
            # #         print RPlotUtil.drawXYPlot([1,2,3], [4,5,6], plotType='p', xLim=[0,2], yLim=[0,2], mainTitle='tit', xTitle='xTit', yTitle='yTit')
            # #         res = RPlotUtil.drawXYPlot([1,2,3], [4,5,6], plotType='p', xLim=[0,2], yLim=[0,2], mainTitle='tit', xTitle='xTit', yTitle='yTit')
            # #
            #
            #
            #         core = HtmlCore()
            #         core.begin()
            #         core.divBegin(divId='plot')
            #         core.image(plotOutput.getURL())
            #         core.divEnd()
            #         core.end()
            #         print core

    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'customhtml'


class rainfallPlotsSynthetic(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Generate synthetics track with Poisson distribution using file [RP manuscript tool]"

    @staticmethod
    def getInputBoxNames():
        return [
            ('Select genome:', 'genome'),
            # ('Select interRate (default 0.0000001):','paramInterRate'),
            # ('Select intraRate (default 0.0000001):','paramIntraRate'),
            # ('Select interProb (default 1):','paramInterProb')
            ('Select file with parameters:', 'parameters')
        ]

    @staticmethod
    def getOptionsBoxGenome():
        return '__genome__'

    # @staticmethod
    # def getOptionsBoxParamInterRate(prevChoices):
    #     return ''
    #
    # @staticmethod
    # def getOptionsBoxParamIntraRate(prevChoices):
    #     return ''
    #
    # @staticmethod
    # def getOptionsBoxParamInterProb(prevChoices):
    #     return ''

    @staticmethod
    def getOptionsBoxParameters(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement('gtrack')

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        from quick.extra.SimulationTools import PointIter, SimulationPointIter

        genome = choices.genome
        parameters = choices.parameters

        dataOut = []
        with open(ExternalTrackManager.extractFnFromGalaxyTN(choices.parameters.split(':')), 'r') as f:
            for x in f.readlines():
                xx = x.strip('\n')
                if not '#' in xx:
                    data = xx.split('\t')
                    if len(data) == 6:
                        dataOut.append(data)
                        # chr = data[0]
                        # st = chr[1]
                        # end = chr[2]
                        # inter = chr[3]
                        # intra = chr[4]
                        # prob = chr[5]

        f.closed

        fileName = 'syn-rainfall'
        #
        # uri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn,
        #                                     extraFileName=fileName,
        #                                     suffix='bed')


        outGSuite = GSuite()
        g = SimulationPointIter()

        newData = ''
        chrNum = 0

        for chr in dataOut:

            fileName = 'syn-chr' + 'iInterR-' + str(chr[0]) + 'st-' + str(chr[1]) + 'end-' + str(
                chr[2]) + 'iInterR-' + str(chr[3]) + 'iIntraR-' + str(chr[4]) + 'prob-' + str(chr[5]) + '--' + str(
                chrNum)

            uri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn,
                                                extraFileName=fileName,
                                                suffix='bed')

            gSuiteTrack = GSuiteTrack(uri)
            outFn = gSuiteTrack.path
            ensurePathExists(outFn)

            g.createChrTrack(genome, chr[0], PointIter, outFn, chr[3], chr[4], chr[5], chr[1], chr[2])

            j = 0
            k = 0

            # print str(chr[1]) + '-' + str(chr[2])

            with open(outFn, 'r') as outputFile:
                for line in outputFile.readlines():
                    xx = line.strip('\n')
                    ll = xx.split('\t')
                    j += 1

                    print str(ll) + ' ' + str(chr[1]) + '-' + str(chr[2])

                    if int(ll[1]) >= int(chr[1]) and int(ll[2]) <= int(chr[2]):
                        k += 1
                        newData += line

            # print j
            # print k

            # print chrNum
            # print len(dataOut)

            chrNum += 1

            if chrNum == len(dataOut):
                with open(outFn, 'w') as outputFile:
                    outputFile.write(newData)
                outGSuite.addTrack(GSuiteTrack(uri, title=''.join(fileName), genome=genome))

        GSuiteComposer.composeToFile(outGSuite, cls.extraGalaxyFn['synthetic GSuite'])

        print 'Done'

    @staticmethod
    def validateAndReturnErrors(choices):
        return None

    @classmethod
    def getExtraHistElements(cls, choices):
        return [HistElement('synthetic GSuite', 'gsuite')]


class rainfallPlots(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Generate synthetics tracks with Poisson distribution"

    @staticmethod
    def getInputBoxNames():
        return [
            ('Select genome:', 'genome'),
            ('Select interRate (default 0.0000001):', 'paramInterRate'),
            ('Select intraRate (default 0.0000001):', 'paramIntraRate'),
            ('Select interProb (default 1):', 'paramInterProb')
        ]

    @staticmethod
    def getOptionsBoxGenome():
        return '__genome__'

    @staticmethod
    def getOptionsBoxParamInterRate(prevChoices):
        return ''

    @staticmethod
    def getOptionsBoxParamIntraRate(prevChoices):
        return ''

    @staticmethod
    def getOptionsBoxParamInterProb(prevChoices):
        return ''

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        from quick.extra.SimulationTools import PointIter, SimulationPointIter

        genome = choices.genome

        if choices.paramInterRate == '':
            paramInterRate = [0.0000001]
        else:
            paramInterRate = choices.paramInterRate
            paramInterRate = paramInterRate.replace(' ', '')
            paramInterRate = paramInterRate.split(",")

        if choices.paramIntraRate == '':
            paramIntraRate = [0.0000001]
        else:
            paramIntraRate = choices.paramIntraRate
            paramIntraRate = paramIntraRate.replace(' ', '')
            paramIntraRate = paramIntraRate.split(",")

        if choices.paramInterProb == '':
            paramInterProb = [0.0000001]
        else:
            paramInterProb = choices.paramInterProb
            paramInterProb = paramInterProb.replace(' ', '')
            paramInterProb = paramInterProb.split(",")

        if len(paramInterProb) == len(paramIntraRate) and len(paramIntraRate) == len(paramInterRate):

            g = SimulationPointIter()
            outGSuite = GSuite()
            for trackNameEl in range(0, len(paramIntraRate)):
                fileName = 'syn-' + 'iInterR-' + str(paramInterRate[trackNameEl]) + 'iIntraR-' + str(
                    paramIntraRate[trackNameEl]) + 'prob-' + str(paramInterProb[trackNameEl]) + '--' + str(trackNameEl)

                uri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn,
                                                    extraFileName=fileName,
                                                    suffix='bed')

                gSuiteTrack = GSuiteTrack(uri)
                outFn = gSuiteTrack.path
                ensurePathExists(outFn)

                g.createChrTrack(genome, 'chr1', PointIter, outFn, paramInterRate[trackNameEl],
                                 paramIntraRate[trackNameEl], paramInterProb[trackNameEl])

                outGSuite.addTrack(GSuiteTrack(uri, title=''.join(fileName), genome=genome))

            GSuiteComposer.composeToFile(outGSuite, cls.extraGalaxyFn['synthetic GSuite'])

    @staticmethod
    def validateAndReturnErrors(choices):
        genome = choices.genome

        if choices.paramInterRate == '':
            paramInterRate = [0.0000001]
        else:
            paramInterRate = choices.paramInterRate
            paramInterRate = paramInterRate.replace(' ', '')
            paramInterRate = paramInterRate.split(",")

        if choices.paramIntraRate == '':
            paramIntraRate = [0.0000001]
        else:
            paramIntraRate = choices.paramIntraRate
            paramIntraRate = paramIntraRate.replace(' ', '')
            paramIntraRate = paramIntraRate.split(",")

        if choices.paramInterProb == '':
            paramInterProb = [0.0000001]
        else:
            paramInterProb = choices.paramInterProb
            paramInterProb = paramInterProb.replace(' ', '')
            paramInterProb = paramInterProb.split(",")

        if len(paramInterProb) != len(paramIntraRate) or len(paramIntraRate) != len(paramInterRate):
            return 'Number of parameters are not equal'

        return None

    @staticmethod
    def getToolDescription():

        htmlCore = HtmlCore()
        htmlCore.begin()

        htmlCore.header('Example 1:')
        htmlCore.line('Tool with the default values generate GSuite with one track')
        htmlCore.header('Example 2:')
        htmlCore.line('Tool with the following values:')
        htmlCore.line('- interRate: 0.0000001,0.0000001')
        htmlCore.line('- intraRate: 0.000001,0.000001')
        htmlCore.line('- interProb: 0.3, 0.2')
        htmlCore.line('generate GSuite with two tracks')

        htmlCore.end()

        return htmlCore

    @classmethod
    def getExtraHistElements(cls, choices):
        return [HistElement('synthetic GSuite', 'gsuite')]


class divideGSuite(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Divide gSuite"

    @staticmethod
    def getInputBoxNames():
        return [('Select file', 'track'),
                ('Gsuite name', 'gSuiteName'),
                ('Expression', 'param')
                ]

    @staticmethod
    def getOptionsBoxTrack():
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @staticmethod
    def getOptionsBoxGSuiteName(prevChoices):
        return ''

    @staticmethod
    def getOptionsBoxParam(prevChoices):
        return ''

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        # Track.trackname
        # store pickle

        with open(ExternalTrackManager.extractFnFromGalaxyTN(choices.track.split(':')), 'r') as f:
            data = [x.strip('\n') for x in f.readlines()]
        f.closed

        htmlCore = HtmlCore()
        htmlCore.begin()

        dataCopy = data[:]
        if choices.param != '':
            for el in choices.param.split(','):

                newlC = str(el)

                outputFile = open(
                    cls.makeHistElement(galaxyExt='gsuite', title=str(choices.gSuiteName) + ' (' + str(el) + ')'), 'w')
                output = ''
                for d in range(0, len(data)):
                    if d < 5:
                        output += data[d]
                        output += '\n'
                    else:
                        newData = data[d].split("\t")
                        if str(el) in newData[1]:
                            output += '\t'.join(newData)
                            output += '\n'
                            dataCopy.remove(data[d])

                outputFile.write(output)
                outputFile.close()

                data = dataCopy[:]

                htmlCore.line('File ' + str(newlC) + ' is in the history.')

        htmlCore.end()

        htmlCore.hideToggle(styleClass='debug')

        print htmlCore

    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''

        return None

    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'bed'


class removeStringFromGSuite(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Remove string from gSuite"

    @staticmethod
    def getInputBoxNames():
        return [('Select file', 'track'),
                ('Expression', 'param')
                ]

    @staticmethod
    def getOptionsBoxTrack():
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @staticmethod
    def getOptionsBoxParam(prevChoices):
        return ''

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):

        with open(ExternalTrackManager.extractFnFromGalaxyTN(choices.track.split(':')), 'r') as f:
            data = [x.strip('\n') for x in f.readlines()]
        f.closed

        output = ''
        for d in range(0, len(data)):
            if d < 5:
                output += data[d]
            else:
                newData = data[d].split("\t")
                newData[1] = newData[1].replace(str(choices.param), '')

                output += '\t'.join(newData)
            output += '\n'

        open(galaxyFn, 'w').write(output)

    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''

        return None

    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'gsuite'


class removeFromBedFile(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Remove string from bed files"

    @staticmethod
    def getInputBoxNames():
        return [('Select track collection GSuite', 'bedFile'),
                ('Name', 'nameBox'),
                ('Parameter', 'par')
                ]

    @staticmethod
    def getOptionsBoxBedFile():
        return GeneralGuiTool.getHistorySelectionElement('bed')

    @staticmethod
    def getOptionsBoxNameBox(prevChoices):
        return ''

    @staticmethod
    def getOptionsBoxPar(prevChoices):
        return ''

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):

        inputFile = open(ExternalTrackManager.extractFnFromGalaxyTN(choices.bedFile.split(':')), 'r')
        with inputFile as f:
            data = [x.strip('\n') for x in f.readlines()]
        f.closed

        headerFirst = 'track name="' + str(choices.nameBox) + '" description="' + str(choices.nameBox) + '" priority=1'

        outputFile = open(galaxyFn, "w")
        outputFile.write(headerFirst + '\n')

        for d in range(0, len(data)):
            if not choices.par in data[d]:
                outputFile.write(data[d] + '\n')

        inputFile.close()
        outputFile.close()

    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''

        return None

    # @staticmethod
    # def getSubToolClasses():
    #    '''
    #    Specifies a list of classes for subtools of the main tool. These
    #    subtools will be selectable from a selection box at the top of the page.
    #    The input boxes will change according to which subtool is selected.
    #    '''
    #    return None
    #
    # @staticmethod
    # def isPublic():
    #    '''
    #    Specifies whether the tool is accessible to all users. If False, the
    #    tool is only accessible to a restricted set of users as defined in
    #    LocalOSConfig.py.
    #    '''
    #    return False
    #
    # @staticmethod
    # def isRedirectTool():
    #    '''
    #    Specifies whether the tool should redirect to an URL when the Execute
    #    button is clicked.
    #    '''
    #    return False
    #
    # @staticmethod
    # def getRedirectURL(choices):
    #    '''
    #    This method is called to return an URL if the isRedirectTool method
    #    returns True.
    #    '''
    #    return ''
    #
    # @staticmethod
    # def isHistoryTool():
    #    '''
    #    Specifies if a History item should be created when the Execute button is
    #    clicked.
    #    '''
    #    return True
    #
    # @staticmethod
    # def isDynamic():
    #    '''
    #    Specifies whether changing the content of texboxes causes the page to
    #    reload.
    #    '''
    #    return True
    #
    # @staticmethod
    # def getResetBoxes():
    #    '''
    #    Specifies a list of input boxes which resets the subsequent stored
    #    choices previously made. The input boxes are specified by index
    #    (starting with 1) or by key.
    #    '''
    #    return []
    #
    # @staticmethod
    # def getToolDescription():
    #    '''
    #    Specifies a help text in HTML that is displayed below the tool.
    #    '''
    #    return ''
    #
    # @staticmethod
    # def getToolIllustration():
    #    '''
    #    Specifies an id used by StaticFile.py to reference an illustration file
    #    on disk. The id is a list of optional directory names followed by a file
    #    name. The base directory is STATIC_PATH as defined by Config.py. The
    #    full path is created from the base directory followed by the id.
    #    '''
    #    return None
    #
    # @staticmethod
    # def getFullExampleURL():
    #    return None
    #
    # @classmethod
    # def isBatchTool(cls):
    #    '''
    #    Specifies if this tool could be run from batch using the batch. The
    #    batch run line can be fetched from the info box at the bottom of the
    #    tool.
    #    '''
    #    return cls.isHistoryTool()
    #
    # @staticmethod
    # def isDebugMode():
    #    '''
    #    Specifies whether debug messages are printed.
    #    '''
    #    return False
    #
    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'bed'


class divideBedFileTool(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Divide bed file through columns"

    @staticmethod
    def getInputBoxNames():
        return [('Select file', 'bedFile'),
                ('Select name of columns', 'cols')
                ]

    @staticmethod
    def getOptionsBoxBedFile():
        return GeneralGuiTool.getHistorySelectionElement()

    @staticmethod
    def getOptionsBoxCols(prevChoices):

        listCol = []
        if prevChoices.bedFile:
            inputFile = open(ExternalTrackManager.extractFnFromGalaxyTN(prevChoices.bedFile.split(':')), 'r')
            with inputFile as f:
                data = [x.strip('\n') for x in f.readlines()]
            f.closed
            inputFile.close()

            return data[0].split("\t")  # 4

        return listCol

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        listCol = []
        inputFile = open(ExternalTrackManager.extractFnFromGalaxyTN(choices.bedFile.split(':')), 'r')
        with inputFile as f:
            data = [x.strip('\n') for x in f.readlines()]
        f.closed
        inputFile.close()

        countLineNum = 6
        countHeaderLine = 0  # 4

        num = 0
        lenDD = 0
        for d in range(0, len(data)):
            dd = data[d].split("\t")
            if d == countHeaderLine:
                lenDD = len(dd)
                num = data[countHeaderLine].split("\t").index(choices.cols)
            if d >= countLineNum and len(dd) == lenDD:
                if dd[num] not in listCol:
                    listCol.append(dd[num])



                #         from gold.gsuite.GSuite import GSuite
                #         from gold.description.TrackInfo import TrackInfo
                #         from gold.gsuite.GSuiteTrack import HbGSuiteTrack, GSuiteTrack, GalaxyGSuiteTrack, HttpGSuiteTrack
                #         from gold.gsuite import GSuiteComposer
                #
                #         outGSuite = GSuite()

        print 'Start making history elements'

        i = 0
        for lC in listCol:
            if i < 700:
                newlC = str(lC).replace('_', '-').replace('--', '-')

                outputFile = open(cls.makeHistElement(galaxyExt='gtrack', title=str(newlC)), 'w')
                lenDD = 0
                for d in range(0, len(data)):
                    dd = data[d].split("\t")
                    if d < countLineNum:
                        outputFile.write(data[d] + '\n')
                    if d == countHeaderLine:
                        lenDD = len(dd)
                    if d >= countLineNum and len(dd) == lenDD:
                        if dd[num] == str(lC):
                            outputFile.write(data[d] + '\n')

                outputFile.close()
                print 'File: ' + str(newlC) + ' is in the history' + '<br\>'

            #                 outputFile=''
            #                 outStaticFile = GalaxyRunSpecificFile([md5(str(newlC)).hexdigest() + '.gtrack'], galaxyFn)
            #                 f = outStaticFile.getFile('w')
            #                 lenDD=0
            #                 for d in range(0, len(data)):
            #                     dd = data[d].split("\t")
            #                     if d < countLineNum:
            #                         outputFile += data[d] + '\n'
            #                     if d == countHeaderLine:
            #                         lenDD = len(dd)
            #                     if d>=countLineNum and len(dd) == lenDD:
            #                         if dd[num] == str(lC):
            #                             outputFile += data[d] + '\n'
            #
            #                 f.write(outputFile)
            #                 f.close()
            #
            #                 trackName = str(newlC)
            #                 uri = HbGSuiteTrack.generateURI(trackName=trackName)
            #                 outGSuite.addTrack(GSuiteTrack(uri, trackType='points', genome='hg19'))

            i += 1

        #         GSuiteComposer.composeToFile(outGSuite, galaxyFn)

    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'customhtml'


class divideBedFile(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Divide bed file"

    @staticmethod
    def getInputBoxNames():
        return [('Select track collection GSuite', 'bedFile'),
                ('Select name of columns', 'rows')
                ]

    @staticmethod
    def getOptionsBoxBedFile():
        return GeneralGuiTool.getHistorySelectionElement('bed')

    @staticmethod
    def getOptionsBoxRows(prevChoices):

        listCol = []
        if prevChoices.bedFile:
            with open(ExternalTrackManager.extractFnFromGalaxyTN(prevChoices.bedFile.split(':')), 'r') as f:
                data = [x.strip('\n') for x in f.readlines()]
            f.closed

            lenDD = 0
            for d in range(0, len(data)):
                dd = data[d].split("\t")
                if d == 1:
                    lenDD = len(dd)
                if len(dd) == lenDD:
                    if dd[3] not in listCol:
                        listCol.append(dd[3])

        return listCol

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):

        inputFile = open(ExternalTrackManager.extractFnFromGalaxyTN(choices.bedFile.split(':')), 'r')
        with inputFile as f:
            data = [x.strip('\n') for x in f.readlines()]
        f.closed

        headerFirst = 'track name="' + str(choices.rows) + '" description="' + str(choices.rows) + '" priority=1'

        outputFile = open(galaxyFn, "w")
        outputFile.write(headerFirst + '\n')
        lenDD = 0
        for d in range(0, len(data)):
            dd = data[d].split("\t")
            if d == 1:
                lenDD = len(dd)
            if len(dd) == lenDD:
                if dd[3] == str(choices.rows):
                    outputFile.write(data[d] + '\n')

        inputFile.close()
        outputFile.close()

    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''

        return None

    # @staticmethod
    # def getSubToolClasses():
    #    '''
    #    Specifies a list of classes for subtools of the main tool. These
    #    subtools will be selectable from a selection box at the top of the page.
    #    The input boxes will change according to which subtool is selected.
    #    '''
    #    return None
    #
    # @staticmethod
    # def isPublic():
    #    '''
    #    Specifies whether the tool is accessible to all users. If False, the
    #    tool is only accessible to a restricted set of users as defined in
    #    LocalOSConfig.py.
    #    '''
    #    return False
    #
    # @staticmethod
    # def isRedirectTool():
    #    '''
    #    Specifies whether the tool should redirect to an URL when the Execute
    #    button is clicked.
    #    '''
    #    return False
    #
    # @staticmethod
    # def getRedirectURL(choices):
    #    '''
    #    This method is called to return an URL if the isRedirectTool method
    #    returns True.
    #    '''
    #    return ''
    #
    # @staticmethod
    # def isHistoryTool():
    #    '''
    #    Specifies if a History item should be created when the Execute button is
    #    clicked.
    #    '''
    #    return True
    #
    # @staticmethod
    # def isDynamic():
    #    '''
    #    Specifies whether changing the content of texboxes causes the page to
    #    reload.
    #    '''
    #    return True
    #
    # @staticmethod
    # def getResetBoxes():
    #    '''
    #    Specifies a list of input boxes which resets the subsequent stored
    #    choices previously made. The input boxes are specified by index
    #    (starting with 1) or by key.
    #    '''
    #    return []
    #
    # @staticmethod
    # def getToolDescription():
    #    '''
    #    Specifies a help text in HTML that is displayed below the tool.
    #    '''
    #    return ''
    #
    # @staticmethod
    # def getToolIllustration():
    #    '''
    #    Specifies an id used by StaticFile.py to reference an illustration file
    #    on disk. The id is a list of optional directory names followed by a file
    #    name. The base directory is STATIC_PATH as defined by Config.py. The
    #    full path is created from the base directory followed by the id.
    #    '''
    #    return None
    #
    # @staticmethod
    # def getFullExampleURL():
    #    return None
    #
    # @classmethod
    # def isBatchTool(cls):
    #    '''
    #    Specifies if this tool could be run from batch using the batch. The
    #    batch run line can be fetched from the info box at the bottom of the
    #    tool.
    #    '''
    #    return cls.isHistoryTool()
    #
    # @staticmethod
    # def isDebugMode():
    #    '''
    #    Specifies whether debug messages are printed.
    #    '''
    #    return False
    #
    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'bed'


class divideBedFileV2(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Divide bed file into bed files"

    @staticmethod
    def getInputBoxNames():
        return [('Select track collection GSuite', 'bedFile'),
                ('Which column', 'colNumber'),
                ('Expression', 'param'),
                ('Contain', 'paramString')
                ]

    @staticmethod
    def getOptionsBoxBedFile():
        return GeneralGuiTool.getHistorySelectionElement('bed', 'gtrack')

    @staticmethod
    def getOptionsBoxColNumber(prevChoices):
        return ''

    @staticmethod
    def getOptionsBoxParam(prevChoices):
        return ''

    @staticmethod
    def getOptionsBoxParamString(prevChoices):
        return ['Full string', 'Part string']

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        colNumber = int(choices.colNumber)

        listCol = []
        inputFile = open(ExternalTrackManager.extractFnFromGalaxyTN(choices.bedFile.split(':')), 'r')
        with inputFile as f:
            data = [x.strip('\n') for x in f.readlines()]
        f.closed

        lenDD = 0
        indexHeader = 0
        for d in range(0, len(data)):
            dd = data[d].split("\t")
            try:
                el = int(dd[1])
                if dd[colNumber] not in listCol:
                    listCol.append(dd[colNumber])
            except:
                indexHeader += 1
                pass

        htmlCore = HtmlCore()
        htmlCore.begin()

        if choices.param == '':

            for lC in listCol:
                newlC = str(lC).replace('_', '-').replace('--', '-')
                # headerFirst = 'track name="' + str(newlC) + '" description="' + str(newlC) + '" priority=1'

                # outStaticFile = GalaxyRunSpecificFile([md5(str(lC)).hexdigest() + '.bed'], galaxyFn)
                # outputFile = outStaticFile.getFile('w')

                outputFile = open(cls.makeHistElement(galaxyExt='bed', title=str(newlC)), 'w')

                # outputFile.write(headerFirst + '\n')
                lenDD = 0
                for d in range(0, len(data)):
                    dd = data[d].split("\t")
                    if d == indexHeader:
                        lenDD = len(dd)
                    if len(dd) == lenDD:
                        if dd[colNumber] == str(lC):
                            # outputFile.write(data[d] + '\n')
                            outputFile.write('\t'.join(dd[0:3]) + '\n')

                inputFile.close()

                outputFile.close()
                htmlCore.line('File ' + str(newlC) + ' is in the history.')

        else:
            if choices.paramString == 'Full string':
                for el in choices.param.split(','):
                    newlC = str(el)
                    outputFile = open(cls.makeHistElement(galaxyExt='bed', title=str(newlC)), 'w')

                    for lC in listCol:
                        if el in lC:
                            lenDD = 0
                            for d in range(0, len(data)):
                                dd = data[d].split("\t")
                                if d == indexHeader:
                                    lenDD = len(dd)
                                if len(dd) == lenDD:
                                    if dd[colNumber] == str(lC):
                                        outputFile.write('\t'.join(dd[0:3]) + '\n')

                    outputFile.close()

                    htmlCore.line('File ' + str(newlC) + ' is in the history.')

            elif choices.paramString == 'Part string':
                for el in choices.param.split(','):
                    newlC = str(el)
                    # headerFirst = 'track name="' + str(newlC) + '" description="' + str(newlC) + '" priority=1'
                    outputFile = open(cls.makeHistElement(galaxyExt='bed', title=str(newlC)), 'w')
                    # outStaticFile = GalaxyRunSpecificFile([md5(str(lC)).hexdigest() + '.bed'], galaxyFn)
                    # outputFile = outStaticFile.getFile('w')
                    # outputFile.write(headerFirst + '\n')
                    for lC in listCol:
                        if el in lC:
                            lenDD = 0
                            for d in range(0, len(data)):
                                if len(data[d]) > 1:
                                    dd = data[d].split("\t")
                                    if d == indexHeader:
                                        lenDD = len(dd)
                                    if len(dd) == lenDD:
                                        if str(lC) in dd[colNumber]:
                                            # outputFile.write(data[d] + '\n')
                                            outputFile.write('\t'.join(dd[0:3]) + '\n')
                                            data[d] = []

                    outputFile.close()

                    htmlCore.line('File ' + str(newlC) + ' is in the history.')

        htmlCore.end()

        htmlCore.hideToggle(styleClass='debug')

        print htmlCore

    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''

        return None

    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'html'


class showGSuiteResultsInTable(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Show gSuite results in table"

    @staticmethod
    def getInputBoxNames():
        return [('Select track collection GSuite', 'gSuite'),
                ('Select name of columns', 'rows'),
                ('Select name of rows', 'columns')
                ]

    @staticmethod
    def getOptionsBoxGSuite():
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @staticmethod
    def getOptionsBoxRows(prevChoices):
        return ''

    @staticmethod
    def getOptionsBoxColumns(prevChoices):
        return ''

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):

        with open(ExternalTrackManager.extractFnFromGalaxyTN(choices.gSuite.split(':')), 'r') as f:
            data = [x.strip('\n') for x in f.readlines()]
        f.closed

        for d in range(0, 5):
            del data[0]

        nRows = []
        for el in choices.rows.split(','):
            nRows.append([el.replace(' ', ''), len(el)])

        from operator import itemgetter
        nRows.sort(key=itemgetter(1), reverse=True)

        output = []
        inx = []
        for el in nRows:
            for iEl in inx:
                del data[data.index(iEl)]
                inx = []

            for d in range(0, len(data)):
                dd = data[d].split("\t")
                if dd[1].find(el[0]) != -1:
                    for elCol in choices.columns.split(','):
                        if dd[1].find(elCol.replace(' ', '')) != -1:
                            output.append([el[0], elCol, dd[2]])
                            inx.append(data[d])

        output.sort(key=itemgetter(1, 0))

        res = []
        resTab = []
        el = output[0][1]
        res.append(el)
        firstEl = False
        header = ['Tracks']
        for inEl in range(0, len(output)):
            if output[inEl][0] not in header:
                header.append(output[inEl][0])
            if el == output[inEl][1]:
                res.append(output[inEl][2])
            else:
                resTab.append(res)
                res = []
                res.append(output[inEl][1])
                res.append(output[inEl][2])
                el = output[inEl][1]
        resTab.append(res)

        htmlCore = HtmlCore()
        htmlCore.begin()
        htmlCore.header('Results')
        htmlCore.tableHeader(header, sortable=True, tableId=1)
        for el in resTab:
            htmlCore.tableLine(el)
        htmlCore.end()

        htmlCore.hideToggle(styleClass='debug')

        print htmlCore

    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''

        from gold.gsuite.GSuiteConstants import UNKNOWN, MULTIPLE

        errorStr = GeneralGuiTool._checkGSuiteFile(choices.gSuite)
        if errorStr:
            return errorStr

        from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
        gSuite = getGSuiteFromGalaxyTN(choices.gSuite)
        if gSuite.numTracks() == 0:
            return 'Please select a GSuite file with at least one track'

        if not gSuite.isPreprocessed():
            return 'Selected GSuite file is not preprocess. Please preprocess ' \
                   'the GSuite file before continuing the analysis.'

        if gSuite.trackType in [UNKNOWN]:
            return 'The track type of the GSuite file is not known. The track type ' \
                   'is needed for doing analysis.'

        if gSuite.trackType in [MULTIPLE]:
            return 'All tracks in the GSuite file needs to be of the same track ' \
                   'type. Multiple track types are not supported.'

        return None

    # @staticmethod
    # def getSubToolClasses():
    #    '''
    #    Specifies a list of classes for subtools of the main tool. These
    #    subtools will be selectable from a selection box at the top of the page.
    #    The input boxes will change according to which subtool is selected.
    #    '''
    #    return None
    #
    # @staticmethod
    # def isPublic():
    #    '''
    #    Specifies whether the tool is accessible to all users. If False, the
    #    tool is only accessible to a restricted set of users as defined in
    #    LocalOSConfig.py.
    #    '''
    #    return False
    #
    # @staticmethod
    # def isRedirectTool():
    #    '''
    #    Specifies whether the tool should redirect to an URL when the Execute
    #    button is clicked.
    #    '''
    #    return False
    #
    # @staticmethod
    # def getRedirectURL(choices):
    #    '''
    #    This method is called to return an URL if the isRedirectTool method
    #    returns True.
    #    '''
    #    return ''
    #
    # @staticmethod
    # def isHistoryTool():
    #    '''
    #    Specifies if a History item should be created when the Execute button is
    #    clicked.
    #    '''
    #    return True
    #
    # @staticmethod
    # def isDynamic():
    #    '''
    #    Specifies whether changing the content of texboxes causes the page to
    #    reload.
    #    '''
    #    return True
    #
    # @staticmethod
    # def getResetBoxes():
    #    '''
    #    Specifies a list of input boxes which resets the subsequent stored
    #    choices previously made. The input boxes are specified by index
    #    (starting with 1) or by key.
    #    '''
    #    return []
    #
    # @staticmethod
    # def getToolDescription():
    #    '''
    #    Specifies a help text in HTML that is displayed below the tool.
    #    '''
    #    return ''
    #
    # @staticmethod
    # def getToolIllustration():
    #    '''
    #    Specifies an id used by StaticFile.py to reference an illustration file
    #    on disk. The id is a list of optional directory names followed by a file
    #    name. The base directory is STATIC_PATH as defined by Config.py. The
    #    full path is created from the base directory followed by the id.
    #    '''
    #    return None
    #
    # @staticmethod
    # def getFullExampleURL():
    #    return None
    #
    # @classmethod
    # def isBatchTool(cls):
    #    '''
    #    Specifies if this tool could be run from batch using the batch. The
    #    batch run line can be fetched from the info box at the bottom of the
    #    tool.
    #    '''
    #    return cls.isHistoryTool()
    #
    # @staticmethod
    # def isDebugMode():
    #    '''
    #    Specifies whether debug messages are printed.
    #    '''
    #    return False
    #
    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'html'


class gSuiteInverse(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Do inverse for gSuite"

    @staticmethod
    def getInputBoxNames():
        return [('Select track collection GSuite', 'gSuite')
                ]

    @staticmethod
    def getOptionsBoxGSuite():
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):

        # use gSuite from option
        gSuite = getGSuiteFromGalaxyTN(choices.gSuite)
        tracks = list(gSuite.allTracks())

        for track in tracks:
            tr = ('/').join(track.trackName)
            print ExternalTrackManager.extractFnFromGalaxyTN("hb:/Private/GK/Hilde/Mutations/eta-")
            with open(ExternalTrackManager.extractFnFromGalaxyTN("hb:/Private/GK/Hilde/Mutations/eta-"), 'r') as f:
                data = [x.strip('\n') for x in f.readlines()]
            f.closed
            print data

    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''

        from gold.gsuite.GSuiteConstants import UNKNOWN, MULTIPLE

        errorStr = GeneralGuiTool._checkGSuiteFile(choices.gSuite)
        if errorStr:
            return errorStr

        from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
        gSuite = getGSuiteFromGalaxyTN(choices.gSuite)
        if gSuite.numTracks() == 0:
            return 'Please select a GSuite file with at least one track'

        if not gSuite.isPreprocessed():
            return 'Selected GSuite file is not preprocess. Please preprocess ' \
                   'the GSuite file before continuing the analysis.'

        if gSuite.trackType in [UNKNOWN]:
            return 'The track type of the GSuite file is not known. The track type ' \
                   'is needed for doing analysis.'

        if gSuite.trackType in [MULTIPLE]:
            return 'All tracks in the GSuite file needs to be of the same track ' \
                   'type. Multiple track types are not supported.'

        return None

    # @staticmethod
    # def getSubToolClasses():
    #    '''
    #    Specifies a list of classes for subtools of the main tool. These
    #    subtools will be selectable from a selection box at the top of the page.
    #    The input boxes will change according to which subtool is selected.
    #    '''
    #    return None
    #
    # @staticmethod
    # def isPublic():
    #    '''
    #    Specifies whether the tool is accessible to all users. If False, the
    #    tool is only accessible to a restricted set of users as defined in
    #    LocalOSConfig.py.
    #    '''
    #    return False
    #
    # @staticmethod
    # def isRedirectTool():
    #    '''
    #    Specifies whether the tool should redirect to an URL when the Execute
    #    button is clicked.
    #    '''
    #    return False
    #
    # @staticmethod
    # def getRedirectURL(choices):
    #    '''
    #    This method is called to return an URL if the isRedirectTool method
    #    returns True.
    #    '''
    #    return ''
    #
    # @staticmethod
    # def isHistoryTool():
    #    '''
    #    Specifies if a History item should be created when the Execute button is
    #    clicked.
    #    '''
    #    return True
    #
    # @staticmethod
    # def isDynamic():
    #    '''
    #    Specifies whether changing the content of texboxes causes the page to
    #    reload.
    #    '''
    #    return True
    #
    # @staticmethod
    # def getResetBoxes():
    #    '''
    #    Specifies a list of input boxes which resets the subsequent stored
    #    choices previously made. The input boxes are specified by index
    #    (starting with 1) or by key.
    #    '''
    #    return []
    #
    # @staticmethod
    # def getToolDescription():
    #    '''
    #    Specifies a help text in HTML that is displayed below the tool.
    #    '''
    #    return ''
    #
    # @staticmethod
    # def getToolIllustration():
    #    '''
    #    Specifies an id used by StaticFile.py to reference an illustration file
    #    on disk. The id is a list of optional directory names followed by a file
    #    name. The base directory is STATIC_PATH as defined by Config.py. The
    #    full path is created from the base directory followed by the id.
    #    '''
    #    return None
    #
    # @staticmethod
    # def getFullExampleURL():
    #    return None
    #
    # @classmethod
    # def isBatchTool(cls):
    #    '''
    #    Specifies if this tool could be run from batch using the batch. The
    #    batch run line can be fetched from the info box at the bottom of the
    #    tool.
    #    '''
    #    return cls.isHistoryTool()
    #
    # @staticmethod
    # def isDebugMode():
    #    '''
    #    Specifies whether debug messages are printed.
    #    '''
    #    return False
    #
    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'html'


class VisTrackFrequencyBetweenTwoTracks(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Plot frequency of mutation alonge the chromosomes for each pair separately in gSuite"

    @staticmethod
    def getInputBoxNames():
        return [('Select track collection GSuite', 'gSuite1'),
                ('Select statistic', 'statistic1'),
                ('Select track collection GSuite', 'gSuite2'),
                ('Select statistic', 'statistic2'),
                ('User bin source', 'binSourceParam')
                ]

    @staticmethod
    def getOptionsBoxGSuite1():
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @staticmethod
    def getOptionsBoxStatistic1(prevChoices):
        return ['Count Point', 'Count Segment']

    @staticmethod
    def getOptionsBoxGSuite2(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @staticmethod
    def getOptionsBoxStatistic2(prevChoices):
        return ['Count Point', 'Count Segment', 'Count Proportion']

    @staticmethod
    def getOptionsBoxBinSourceParam(prevChoices):
        return ''

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):

        from gold.statistic.CountPointStat import CountPointStat
        from gold.statistic.CountSegmentStat import CountSegmentStat
        from quick.statistic.ProportionCountPerBinAvgStat import ProportionCountPerBinAvgStat

        if choices.statistic1 == 'Count Point':
            analysisSpec1 = AnalysisSpec(CountPointStat)
        elif choices.statistic1 == 'Count Segment':
            analysisSpec1 = AnalysisSpec(CountSegmentStat)
        elif choices.statistic1 == 'Count Proportion':
            analysisSpec1 = AnalysisSpec(ProportionCountPerBinAvgStat)

        # use gSuite from option
        gSuite1 = getGSuiteFromGalaxyTN(choices.gSuite1)
        tracks = list(gSuite1.allTracks())

        if choices.binSourceParam:
            binSourceParam = choices.binSourceParam
        else:
            binSourceParam = '1M'

        from quick.webtools.restricted.visualization.visualizationGraphs import visualizationGraphs
        htmlCore = HtmlCore()
        htmlCore.begin()
        htmlCore.divBegin('plotDiv')

        from operator import itemgetter

        title1 = choices.gSuite1
        title2 = choices.gSuite2

        import urllib2
        title1 = urllib2.unquote(title1.split('/')[-1])
        title2 = urllib2.unquote(title2.split('/')[-1])

        if choices.statistic2 == 'Count Point':
            analysisSpec2 = AnalysisSpec(CountPointStat)
        elif choices.statistic2 == 'Count Segment':
            analysisSpec2 = AnalysisSpec(CountSegmentStat)
        elif choices.statistic2 == 'Count Proportion':
            analysisSpec2 = AnalysisSpec(ProportionCountPerBinAvgStat)

        # use gSuite from option
        gSuite2 = getGSuiteFromGalaxyTN(choices.gSuite2)

        tracks2 = list(gSuite2.allTracks())

        # visResgSuiteY1=[]
        # visResgSuiteY2=[]

        seriesNameRes = []
        listResRes = []
        title1Res = []
        title2Res = []
        titleText = []

        visRes1All = OrderedDict()
        visRes2All = OrderedDict()

        countChr = 0
        for chr in GenomeInfo.getChrList(gSuite1.genome):

            titleText.append('Visualization for the ' + str(chr))
            categories = []
            seriesName1 = []
            seriesType1 = []
            analysisBins = UserBinSource(chr, binSourceParam, genome=gSuite1.genome)
            # results = doAnalysisSupportingGsuite(analysisSpec, analysisBins, [gSuite])#not working
            inx = 0
            visRes1 = []
            plotBandsMax = 0

            for track in tracks:
                visResTrack = []
                dataY = []
                results = doAnalysis(analysisSpec1, analysisBins, [PlainTrack(track.trackName)])
                for index, track1 in enumerate(results):
                    visResTrack.append(results[track1]['Result'])
                    # print str(inx) + " " + str(index) + " " + str(results[track1]) + " " + str(track1) + " " + str(track.trackName)
                    dataY.append([track1.start, track1.end, results[track1]['Result']])
                dataY.sort(key=itemgetter(0))
                visResTrack = [elDataY[2] for elDataY in dataY]
                if inx == 0:
                    categories = [str(elDataY[0]) + "-" + str(elDataY[1]) for elDataY in dataY]

                if max(dataY, key=itemgetter(2))[2] >= plotBandsMax:
                    plotBandsMax = max(dataY, key=itemgetter(2))[2]

                seriesName1.append(track.trackName[-1].replace("'", ''))
                seriesType1.append('bubble')
                visRes1.append(visResTrack)
                inx += 1

            # visResgSuiteY1.append(visRes)

            seriesName2 = []
            seriesType2 = []
            analysisBins = UserBinSource(chr, binSourceParam, genome=gSuite2.genome)
            # results = doAnalysisSupportingGsuite(analysisSpec, analysisBins, [gSuite])#not working
            inx = 0
            visRes2 = []
            plotBandsMax = 0
            for track in tracks2:
                visResTrack = []
                dataY = []
                results = doAnalysis(analysisSpec2, analysisBins, [PlainTrack(track.trackName)])
                for index, track1 in enumerate(results):
                    visResTrack.append(results[track1]['Result'])
                    # print str(inx) + " " + str(index) + " " + str(results[track1]) + " " + str(track1) + " " + str(track.trackName)
                    dataY.append([track1.start, track1.end, results[track1]['Result']])
                dataY.sort(key=itemgetter(0))
                visResTrack = [elDataY[2] for elDataY in dataY]
                # if inx ==0:
                #    categories2=[str(elDataY[0])+"-"+str(elDataY[1]) for elDataY in dataY]

                if max(dataY, key=itemgetter(2))[2] >= plotBandsMax:
                    plotBandsMax = max(dataY, key=itemgetter(2))[2]

                seriesName2.append(track.trackName[-1].replace("'", ''))
                seriesType2.append('bubble')
                visRes2.append(visResTrack)
                inx += 1

            dictTemp = OrderedDict()
            for numElY1 in range(0, len(visRes1)):
                if countChr == 0:
                    visRes1All[numElY1] = visRes1[numElY1]
                else:
                    visRes1All[numElY1] += visRes1[numElY1]
                if not numElY1 in dictTemp.keys():
                    dictTemp[numElY1] = OrderedDict()
                for numElY2 in range(0, len(visRes2)):
                    if countChr == 0:
                        visRes2All[numElY2] = visRes2[numElY2]
                    else:
                        visRes2All[numElY2] += visRes2[numElY2]
                    if not numElY2 in dictTemp[numElY1].keys():
                        dictTemp[numElY1][numElY2] = OrderedDict()
                    pair = zip(visRes1[numElY1], visRes2[numElY2])
                    for el in pair:
                        if not el in dictTemp[numElY1][numElY2].keys():
                            dictTemp[numElY1][numElY2][el] = 1
                        else:
                            dictTemp[numElY1][numElY2][el] += 1

            listRes = []
            seriesName = []

            for key1, item1 in dictTemp.items():
                for key2, item2 in item1.items():
                    listResPart = []
                    for key3, item3 in item2.items():
                        listResPart.append(list(key3) + [item3])
                    listRes.append(listResPart)
                    seriesName.append(seriesName1[key1] + ' X ' + seriesName2[key2])
            seriesNameRes.append(seriesName)
            listResRes.append(listRes)

            countChr += 1

        dictTemp = OrderedDict()
        for numElY1 in range(0, len(visRes1All)):
            if not numElY1 in dictTemp.keys():
                dictTemp[numElY1] = OrderedDict()
            for numElY2 in range(0, len(visRes2All)):
                if not numElY2 in dictTemp[numElY1].keys():
                    dictTemp[numElY1][numElY2] = OrderedDict()
                pair = zip(visRes1All[numElY1], visRes2All[numElY2])
                for el in pair:
                    if not el in dictTemp[numElY1][numElY2].keys():
                        dictTemp[numElY1][numElY2][el] = 1
                    else:
                        dictTemp[numElY1][numElY2][el] += 1

        listRes = []
        seriesName = []
        for key1, item1 in dictTemp.items():
            for key2, item2 in item1.items():
                listResPart = []
                for key3, item3 in item2.items():
                    listResPart.append(list(key3) + [item3])
                listRes.append(listResPart)
                seriesName.append(seriesName1[key1] + ' X ' + seriesName2[key2])
        seriesNameRes.append(seriesName)
        listResRes.append(listRes)

        vg = visualizationGraphs()
        res = vg.drawBubbleCharts(
            listResRes,
            seriesName=seriesNameRes,
            titleText=titleText + ['Visualization through all chromosomes'],
            label='<b>{series.name}</b>: {point.x} {point.y} value: {point.z}',
            height=400,
            xAxisTitle=title1,
            yAxisTitle=title2,
            visible=False,
            marginTop=30,
            addTable=True
        )
        htmlCore.line(res)

        #                 print title1
        #                 print title2
        #                 print "categories=" + str(categories)
        #                 print "dataY1=" + str(visRes1)
        #                 print "dataY2=" + str(visRes2)
        #                 print "seriesName1=" + str(seriesName1)
        #                 print "seriesName2=" + str(seriesName2)
        #                 print "seriesType1=" + str(seriesType1)
        #                 print "seriesType2=" + str(seriesType2)




        htmlCore.divEnd()
        htmlCore.end()

        htmlCore.hideToggle(styleClass='debug')

        print htmlCore

    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''

        from gold.gsuite.GSuiteConstants import UNKNOWN, MULTIPLE

        errorStr = GeneralGuiTool._checkGSuiteFile(choices.gSuite1)
        if errorStr:
            return errorStr

        from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
        gSuite1 = getGSuiteFromGalaxyTN(choices.gSuite1)
        if gSuite1.numTracks() == 0:
            return 'Please select a GSuite file with at least one track'

        if not gSuite1.isPreprocessed():
            return 'Selected GSuite file is not preprocess. Please preprocess ' \
                   'the GSuite file before continuing the analysis.'

        if gSuite1.trackType in [UNKNOWN]:
            return 'The track type of the GSuite file is not known. The track type ' \
                   'is needed for doing analysis.'

        if gSuite1.trackType in [MULTIPLE]:
            return 'All tracks in the GSuite file needs to be of the same track ' \
                   'type. Multiple track types are not supported.'

        return None

    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'html'


class VisTrackFrequency(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Plot frequency of mutation alonge the chromosomes in gSuite"

    @staticmethod
    def getInputBoxNames():
        return [('Select way of plotting', 'showResults'),
                ('Select track collection GSuite', 'gSuite1'),
                ('Select statistic', 'statistic1'),
                ('Select track collection GSuite', 'gSuite2'),
                ('Select statistic', 'statistic2'),
                ('Show on plot % the highest values', 'visParam'),
                ('User bin source', 'binSourceParam')
                ]

    @staticmethod
    def getOptionsBoxShowResults():
        return ['Show results separately', 'Show results on one plot']

    @staticmethod
    def getOptionsBoxGSuite1(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @staticmethod
    def getOptionsBoxStatistic1(prevChoices):
        return ['Count Point', 'Count Segment']

    @staticmethod
    def getOptionsBoxGSuite2(prevChoices):
        if prevChoices.showResults == 'Show results on one plot':
            return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @staticmethod
    def getOptionsBoxStatistic2(prevChoices):
        if prevChoices.showResults == 'Show results on one plot':
            return ['Count Point', 'Count Segment', 'Count Proportion']

    @staticmethod
    def getOptionsBoxVisParam(prevChoices):
        if prevChoices.showResults != 'Show results on one plot':
            return ['0', '10', '15', '20', '30', '40', '50']

    @staticmethod
    def getOptionsBoxBinSourceParam(prevChoices):
        return ''

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):

        from gold.statistic.CountPointStat import CountPointStat
        from gold.statistic.CountSegmentStat import CountSegmentStat
        from quick.statistic.ProportionCountPerBinAvgStat import ProportionCountPerBinAvgStat

        if choices.statistic1 == 'Count Point':
            analysisSpec1 = AnalysisSpec(CountPointStat)
        elif choices.statistic1 == 'Count Segment':
            analysisSpec1 = AnalysisSpec(CountSegmentStat)
        elif choices.statistic1 == 'Count Proportion':
            analysisSpec1 = AnalysisSpec(ProportionCountPerBinAvgStat)

        # use gSuite from option
        gSuite1 = getGSuiteFromGalaxyTN(choices.gSuite1)
        tracks = list(gSuite1.allTracks())

        if choices.binSourceParam:
            binSourceParam = choices.binSourceParam
        else:
            binSourceParam = '1M'

        import quick.webtools.restricted.visualization.visualizationPlots as vp
        htmlCore = HtmlCore()
        htmlCore.begin()
        htmlCore.divBegin('plotDiv')
        htmlCore.line(vp.addJSlibs())
        htmlCore.line(vp.addJSlibsExport())
        htmlCore.line(vp.axaddJSlibsOverMouseAxisisPopup())

        plotNumber = 0

        from operator import itemgetter

        if choices.showResults == 'Show results separately':

            for chr in GenomeInfo.getChrList(gSuite1.genome):
                categories = []
                seriesName = []
                seriesType = []
                analysisBins = UserBinSource(chr, binSourceParam, genome=gSuite1.genome)
                # results = doAnalysisSupportingGsuite(analysisSpec, analysisBins, [gSuite])#not working
                inx = 0
                visRes = []
                plotBandsMax = 0
                for track in tracks:
                    visResTrack = []
                    dataY = []
                    results = doAnalysis(analysisSpec1, analysisBins, [PlainTrack(track.trackName)])
                    for index, track1 in enumerate(results):
                        visResTrack.append(results[track1]['Result'])
                        # print str(inx) + " " + str(index) + " " + str(results[track1]) + " " + str(track1) + " " + str(track.trackName)
                        dataY.append([track1.start, track1.end, results[track1]['Result']])
                    dataY.sort(key=itemgetter(0))
                    visResTrack = [elDataY[2] for elDataY in dataY]
                    if inx == 0:
                        categories = [str(elDataY[0]) + "-" + str(elDataY[1]) for elDataY in dataY]

                    if max(dataY, key=itemgetter(2))[2] >= plotBandsMax:
                        plotBandsMax = max(dataY, key=itemgetter(2))[2]

                    seriesName.append(track.trackName[-1].replace("'", ''))
                    seriesType.append('line')
                    visRes.append(visResTrack)
                    inx += 1

                htmlCore.line(vp.drawChartMulti([visRes],
                                                plotNumber=plotNumber,
                                                seriesType=[seriesType],
                                                legend=False,
                                                minWidth=300,
                                                height=700,
                                                lineWidth=1,
                                                titleText='Visualization for frequency of mutation along the ' + str(
                                                    chr),
                                                yAxisTitle=['Value'],
                                                seriesName=seriesName,
                                                enabled=True,
                                                categories=categories,
                                                interaction=False,
                                                plotBandsY=[
                                                    int(plotBandsMax - float(choices.visParam) / 100 * plotBandsMax),
                                                    plotBandsMax, '#FDFD96',
                                                    str(choices.visParam) + '% the highest values']
                                                ))
                plotNumber += 1

        if choices.showResults == 'Show results on one plot':

            title1 = choices.gSuite1
            title2 = choices.gSuite2

            import urllib2
            title1 = urllib2.unquote(title1.split('/')[-1])
            title2 = urllib2.unquote(title2.split('/')[-1])

            if choices.statistic2 == 'Count Point':
                analysisSpec2 = AnalysisSpec(CountPointStat)
            elif choices.statistic2 == 'Count Segment':
                analysisSpec2 = AnalysisSpec(CountSegmentStat)
            elif choices.statistic2 == 'Count Proportion':
                analysisSpec2 = AnalysisSpec(ProportionCountPerBinAvgStat)

            # use gSuite from option
            gSuite2 = getGSuiteFromGalaxyTN(choices.gSuite2)

            tracks2 = list(gSuite2.allTracks())

            # visResgSuiteY1=[]
            # visResgSuiteY2=[]

            for chr in GenomeInfo.getChrList(gSuite1.genome):
                categories = []
                seriesName1 = []
                seriesType1 = []
                analysisBins = UserBinSource(chr, binSourceParam, genome=gSuite1.genome)
                # results = doAnalysisSupportingGsuite(analysisSpec, analysisBins, [gSuite])#not working
                inx = 0
                visRes1 = []
                plotBandsMax = 0

                for track in tracks:
                    visResTrack = []
                    dataY = []
                    results = doAnalysis(analysisSpec1, analysisBins, [PlainTrack(track.trackName)])
                    for index, track1 in enumerate(results):
                        visResTrack.append(results[track1]['Result'])
                        # print str(inx) + " " + str(index) + " " + str(results[track1]) + " " + str(track1) + " " + str(track.trackName)
                        dataY.append([track1.start, track1.end, results[track1]['Result']])
                    dataY.sort(key=itemgetter(0))
                    visResTrack = [elDataY[2] for elDataY in dataY]
                    if inx == 0:
                        categories = [str(elDataY[0]) + "-" + str(elDataY[1]) for elDataY in dataY]

                    if max(dataY, key=itemgetter(2))[2] >= plotBandsMax:
                        plotBandsMax = max(dataY, key=itemgetter(2))[2]

                    seriesName1.append(track.trackName[-1].replace("'", ''))
                    seriesType1.append('line')
                    visRes1.append(visResTrack)
                    inx += 1

                # visResgSuiteY1.append(visRes)

                seriesName2 = []
                seriesType2 = []
                analysisBins = UserBinSource(chr, binSourceParam, genome=gSuite2.genome)
                # results = doAnalysisSupportingGsuite(analysisSpec, analysisBins, [gSuite])#not working
                inx = 0
                visRes2 = []
                plotBandsMax = 0
                for track in tracks2:
                    visResTrack = []
                    dataY = []
                    results = doAnalysis(analysisSpec2, analysisBins, [PlainTrack(track.trackName)])
                    for index, track1 in enumerate(results):
                        visResTrack.append(results[track1]['Result'])
                        # print str(inx) + " " + str(index) + " " + str(results[track1]) + " " + str(track1) + " " + str(track.trackName)
                        dataY.append([track1.start, track1.end, results[track1]['Result']])
                    dataY.sort(key=itemgetter(0))
                    visResTrack = [elDataY[2] for elDataY in dataY]
                    # if inx ==0:
                    #    categories2=[str(elDataY[0])+"-"+str(elDataY[1]) for elDataY in dataY]

                    if max(dataY, key=itemgetter(2))[2] >= plotBandsMax:
                        plotBandsMax = max(dataY, key=itemgetter(2))[2]

                    seriesName2.append(track.trackName[-1].replace("'", ''))
                    seriesType2.append('line')
                    visRes2.append(visResTrack)
                    inx += 1

                htmlCore.line(vp.drawMultiYAxis(
                    dataY1=visRes1,
                    dataY2=visRes2,
                    categories=categories,
                    titleText='Visualization for the ' + str(chr),
                    minWidth=300,
                    height=700,
                    title1=title1,
                    title2=title2,
                    seriesType1=seriesType1,
                    seriesName1=seriesName1,
                    seriesType2=seriesType2,
                    seriesName2=seriesName2,
                    plotNumber=plotNumber
                ))

                '''
                print title1
                print title2
                print "categories=" + str(categories)
                print "dataY1=" + str(visRes1)
                print "dataY2=" + str(visRes2)
                print "seriesName1=" + str(seriesName1)
                print "seriesName2=" + str(seriesName2)
                print "seriesType1=" + str(seriesType1)
                print "seriesType2=" + str(seriesType2)
                '''

                plotNumber += 1

        htmlCore.divEnd()
        htmlCore.end()

        htmlCore.hideToggle(styleClass='debug')

        print htmlCore

    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''

        from gold.gsuite.GSuiteConstants import UNKNOWN, MULTIPLE

        errorStr = GeneralGuiTool._checkGSuiteFile(choices.gSuite1)
        if errorStr:
            return errorStr

        from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
        gSuite1 = getGSuiteFromGalaxyTN(choices.gSuite1)
        if gSuite1.numTracks() == 0:
            return 'Please select a GSuite file with at least one track'

        if not gSuite1.isPreprocessed():
            return 'Selected GSuite file is not preprocess. Please preprocess ' \
                   'the GSuite file before continuing the analysis.'

        if gSuite1.trackType in [UNKNOWN]:
            return 'The track type of the GSuite file is not known. The track type ' \
                   'is needed for doing analysis.'

        if gSuite1.trackType in [MULTIPLE]:
            return 'All tracks in the GSuite file needs to be of the same track ' \
                   'type. Multiple track types are not supported.'

        return None

    # @staticmethod
    # def getSubToolClasses():
    #    '''
    #    Specifies a list of classes for subtools of the main tool. These
    #    subtools will be selectable from a selection box at the top of the page.
    #    The input boxes will change according to which subtool is selected.
    #    '''
    #    return None
    #
    # @staticmethod
    # def isPublic():
    #    '''
    #    Specifies whether the tool is accessible to all users. If False, the
    #    tool is only accessible to a restricted set of users as defined in
    #    LocalOSConfig.py.
    #    '''
    #    return False
    #
    # @staticmethod
    # def isRedirectTool():
    #    '''
    #    Specifies whether the tool should redirect to an URL when the Execute
    #    button is clicked.
    #    '''
    #    return False
    #
    # @staticmethod
    # def getRedirectURL(choices):
    #    '''
    #    This method is called to return an URL if the isRedirectTool method
    #    returns True.
    #    '''
    #    return ''
    #
    # @staticmethod
    # def isHistoryTool():
    #    '''
    #    Specifies if a History item should be created when the Execute button is
    #    clicked.
    #    '''
    #    return True
    #
    # @staticmethod
    # def isDynamic():
    #    '''
    #    Specifies whether changing the content of texboxes causes the page to
    #    reload.
    #    '''
    #    return True
    #
    # @staticmethod
    # def getResetBoxes():
    #    '''
    #    Specifies a list of input boxes which resets the subsequent stored
    #    choices previously made. The input boxes are specified by index
    #    (starting with 1) or by key.
    #    '''
    #    return []
    #
    # @staticmethod
    # def getToolDescription():
    #    '''
    #    Specifies a help text in HTML that is displayed below the tool.
    #    '''
    #    return ''
    #
    # @staticmethod
    # def getToolIllustration():
    #    '''
    #    Specifies an id used by StaticFile.py to reference an illustration file
    #    on disk. The id is a list of optional directory names followed by a file
    #    name. The base directory is STATIC_PATH as defined by Config.py. The
    #    full path is created from the base directory followed by the id.
    #    '''
    #    return None
    #
    # @staticmethod
    # def getFullExampleURL():
    #    return None
    #
    # @classmethod
    # def isBatchTool(cls):
    #    '''
    #    Specifies if this tool could be run from batch using the batch. The
    #    batch run line can be fetched from the info box at the bottom of the
    #    tool.
    #    '''
    #    return cls.isHistoryTool()
    #
    # @staticmethod
    # def isDebugMode():
    #    '''
    #    Specifies whether debug messages are printed.
    #    '''
    #    return False
    #
    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'html'


class gSuiteName(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "gSuite for 4D"

    @staticmethod
    def getInputBoxNames():
        return [('Select file', 'track')
                ]

    @staticmethod
    def getOptionsBoxTrack():
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @staticmethod
    def getOptionsBoxParam(prevChoices):
        return ''

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):

        with open(ExternalTrackManager.extractFnFromGalaxyTN(choices.track.split(':')), 'r') as f:
            data = [x.strip('\n') for x in f.readlines()]
        f.closed

        output = ''
        for d in range(0, len(data)):
            if d < 5:
                output += data[d]
            else:
                newData = data[d].split("\t")
                if len(newData) == 7:
                    newData[1] = str(newData[2]) + ' ' + str(newData[3]) + ' ' + str(newData[4])
                else:
                    newData[1] = str(newData[2]) + ' ' + str(newData[3])
                output += '\t'.join(newData)
            output += '\n'

        open(galaxyFn, 'w').write(output)

    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''

        return None

    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'gsuite'


class KseniagSuite(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Ksenia gSuite for 3D"

    @staticmethod
    def getInputBoxNames():
        return [('Select file', 'track')
                ]

    @staticmethod
    def getOptionsBoxTrack():
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @staticmethod
    def getOptionsBoxParam(prevChoices):
        return ''

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):

        with open(ExternalTrackManager.extractFnFromGalaxyTN(choices.track.split(':')), 'r') as f:
            data = [x.strip('\n') for x in f.readlines()]
        f.closed

        ll = []
        for i in data:
            new = [x for x in i.split()]
            ll.append(new)

        targetTracksDict = []
        d = []
        i = 0
        for l in ll:
            if i > 4:
                if i == 5:
                    fv1 = l[2]
                if fv1 != l[2]:
                    dd = {'folderName1': fv1, 'data': d}
                    targetTracksDict.append(dd)
                    fv1 = l[2]
                    dd = {}
                    d = []
                path = l[0].split('/')
                path.pop(0)
                d.append({'folderName2': l[1], 'trackName': 'file.bed', 'trackPath': path})

                if len(ll) - 1 == i:
                    dd = {'folderName1': fv1, 'data': d}
                    targetTracksDict.append(dd)
            i += 1

        print 'targetTracksDict=' + str(targetTracksDict)

    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''

        return None

    # @staticmethod
    # def getSubToolClasses():
    #    '''
    #    Specifies a list of classes for subtools of the main tool. These
    #    subtools will be selectable from a selection box at the top of the page.
    #    The input boxes will change according to which subtool is selected.
    #    '''
    #    return None
    #
    # @staticmethod
    # def isPublic():
    #    '''
    #    Specifies whether the tool is accessible to all users. If False, the
    #    tool is only accessible to a restricted set of users as defined in
    #    LocalOSConfig.py.
    #    '''
    #    return False
    #
    # @staticmethod
    # def isRedirectTool():
    #    '''
    #    Specifies whether the tool should redirect to an URL when the Execute
    #    button is clicked.
    #    '''
    #    return False
    #
    # @staticmethod
    # def getRedirectURL(choices):
    #    '''
    #    This method is called to return an URL if the isRedirectTool method
    #    returns True.
    #    '''
    #    return ''
    #
    # @staticmethod
    # def isHistoryTool():
    #    '''
    #    Specifies if a History item should be created when the Execute button is
    #    clicked.
    #    '''
    #    return True
    #
    # @staticmethod
    # def isDynamic():
    #    '''
    #    Specifies whether changing the content of texboxes causes the page to
    #    reload.
    #    '''
    #    return True
    #
    # @staticmethod
    # def getResetBoxes():
    #    '''
    #    Specifies a list of input boxes which resets the subsequent stored
    #    choices previously made. The input boxes are specified by index
    #    (starting with 1) or by key.
    #    '''
    #    return []
    #
    # @staticmethod
    # def getToolDescription():
    #    '''
    #    Specifies a help text in HTML that is displayed below the tool.
    #    '''
    #    return ''
    #
    # @staticmethod
    # def getToolIllustration():
    #    '''
    #    Specifies an id used by StaticFile.py to reference an illustration file
    #    on disk. The id is a list of optional directory names followed by a file
    #    name. The base directory is STATIC_PATH as defined by Config.py. The
    #    full path is created from the base directory followed by the id.
    #    '''
    #    return None
    #
    # @staticmethod
    # def getFullExampleURL():
    #    return None
    #
    # @classmethod
    # def isBatchTool(cls):
    #    '''
    #    Specifies if this tool could be run from batch using the batch. The
    #    batch run line can be fetched from the info box at the bottom of the
    #    tool.
    #    '''
    #    return cls.isHistoryTool()
    #
    # @staticmethod
    # def isDebugMode():
    #    '''
    #    Specifies whether debug messages are printed.
    #    '''
    #    return False
    #
    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'html'


class DivideBedFileForChosenPhrase(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Divide bed file according to some string"

    @staticmethod
    def getInputBoxNames():
        return [('Select track', 'track'), \
                ('Parametr', 'param')
                ]

    @staticmethod
    def getOptionsBoxTrack():
        return GeneralGuiTool.getHistorySelectionElement('bed')

    @staticmethod
    def getOptionsBoxParam(prevChoices):
        return ''

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):

        outputFile = open(galaxyFn, "w")
        inputFile = open(ExternalTrackManager.extractFnFromGalaxyTN(choices.track.split(':')), 'r')

        resMutList = []
        i = 0
        for line in inputFile:
            for l in line.split():
                if l.find("".join(choices.param)) != -1:
                    resMutList.append(line)

        for res in resMutList:
            outputFile.write(res)

        inputFile.close()
        outputFile.close()

    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''

        return None

    # @staticmethod
    # def getSubToolClasses():
    #    '''
    #    Specifies a list of classes for subtools of the main tool. These
    #    subtools will be selectable from a selection box at the top of the page.
    #    The input boxes will change according to which subtool is selected.
    #    '''
    #    return None
    #
    # @staticmethod
    # def isPublic():
    #    '''
    #    Specifies whether the tool is accessible to all users. If False, the
    #    tool is only accessible to a restricted set of users as defined in
    #    LocalOSConfig.py.
    #    '''
    #    return False
    #
    # @staticmethod
    # def isRedirectTool():
    #    '''
    #    Specifies whether the tool should redirect to an URL when the Execute
    #    button is clicked.
    #    '''
    #    return False
    #
    # @staticmethod
    # def getRedirectURL(choices):
    #    '''
    #    This method is called to return an URL if the isRedirectTool method
    #    returns True.
    #    '''
    #    return ''
    #
    # @staticmethod
    # def isHistoryTool():
    #    '''
    #    Specifies if a History item should be created when the Execute button is
    #    clicked.
    #    '''
    #    return True
    #
    # @staticmethod
    # def isDynamic():
    #    '''
    #    Specifies whether changing the content of texboxes causes the page to
    #    reload.
    #    '''
    #    return True
    #
    # @staticmethod
    # def getResetBoxes():
    #    '''
    #    Specifies a list of input boxes which resets the subsequent stored
    #    choices previously made. The input boxes are specified by index
    #    (starting with 1) or by key.
    #    '''
    #    return []
    #
    # @staticmethod
    # def getToolDescription():
    #    '''
    #    Specifies a help text in HTML that is displayed below the tool.
    #    '''
    #    return ''
    #
    # @staticmethod
    # def getToolIllustration():
    #    '''
    #    Specifies an id used by StaticFile.py to reference an illustration file
    #    on disk. The id is a list of optional directory names followed by a file
    #    name. The base directory is STATIC_PATH as defined by Config.py. The
    #    full path is created from the base directory followed by the id.
    #    '''
    #    return None
    #
    # @staticmethod
    # def getFullExampleURL():
    #    return None
    #
    # @classmethod
    # def isBatchTool(cls):
    #    '''
    #    Specifies if this tool could be run from batch using the batch. The
    #    batch run line can be fetched from the info box at the bottom of the
    #    tool.
    #    '''
    #    return cls.isHistoryTool()
    #
    # @staticmethod
    # def isDebugMode():
    #    '''
    #    Specifies whether debug messages are printed.
    #    '''
    #    return False
    #
    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'bed'


class GenerateRipleysK(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Compute RipleysK for gSuite"

    @staticmethod
    def getInputBoxNames():
        return [('Select track collection GSuite', 'gSuite'),
                ('Bp window', 'param'),
                ('if only in regions in gSuite', 'chParam'),
                ('Select track from history (Accepted formats: bed)', 'track'),
                ('Show results', 'showResults')
                ]

    @staticmethod
    def getOptionsBoxGSuite():
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @staticmethod
    def getOptionsBoxParam(prevChoices):
        if prevChoices.gSuite:
            gSuite = getGSuiteFromGalaxyTN(prevChoices.gSuite)
            tracks = list(gSuite.allTracks())

            if len(tracks) > 0 and gSuite.isPreprocessed():
                return OrderedDict([
                    ('2', False),
                    ('5', False),
                    ('10', False),
                    ('100', True),
                    ('1000', False),
                    ('10000', False),
                    ('100000', False),
                    ('1000000', False)
                ])

    @staticmethod
    def getOptionsBoxChParam(prevChoices):
        if prevChoices.gSuite:
            gSuite = getGSuiteFromGalaxyTN(prevChoices.gSuite)
            tracks = list(gSuite.allTracks())

            if len(tracks) > 0 and gSuite.isPreprocessed():
                return OrderedDict([
                    ('Yes', True),
                    ('No', False)
                ])

    @staticmethod
    def getOptionsBoxTrack(prevChoices):
        if prevChoices.gSuite:
            gSuite = getGSuiteFromGalaxyTN(prevChoices.gSuite)
            tracks = list(gSuite.allTracks())

            return GeneralGuiTool.getHistorySelectionElement('category.bed', 'bed')

    @staticmethod
    def getOptionsBoxShowResults(prevChoices):
        if prevChoices.param:
            return ['Show results per table', 'Show results in one table']

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        analysisSpec = AnalysisSpec(RipleysKStat)

        # one table per bpW

        print choices.showResults

        if choices.showResults == 'Show results per table':

            htmlCore = HtmlCore()
            htmlCore.begin()
            htmlCore.divBegin('resDiv')
            selectedBpWindow = [key for key, val in choices.param.iteritems() if val == 'True']
            for bpW in selectedBpWindow:
                htmlCore.header('Compute RipleysK for bp window: ' + str(bpW))
                htmlCore.tableHeader(['Track names'] + ['Value'] + ['Ranking'], sortable=True,
                                     tableId='resultsTable_' + str(bpW))
                analysisSpec.addParameter("bpWindow", str(bpW))

                # use gSuite from option
                gSuite = getGSuiteFromGalaxyTN(choices.gSuite)
                tracks = list(gSuite.allTracks())

                import scipy.stats as statRank

                row = []
                elChParam = [key for key, val in choices.param.iteritems() if val == 'True']
                for track in tracks:
                    # analysisBins = GlobalBinSource(gSuite.genome)

                    if str(elChParam[0]) == 'Yes':
                        binFn = ExternalTrackManager.extractFnFromGalaxyTN(choices.track.split(':'))
                        analysisBins = UserBinSource('bed', binFn, genome=gSuite.genome)

                    else:
                        analysisBins = UserBinSource('*', '10m', genome=gSuite.genome)

                    result = doAnalysis(analysisSpec, analysisBins, [PlainTrack(track.trackName)])
                    resultDict = result.getGlobalResult()
                    row.append(resultDict['Result'])

                rank = len(row) + 1 - statRank.rankdata(row)

                for i in range(0, len(tracks)):
                    htmlCore.tableLine([tracks[i].trackName] + [row[i]] + [int(rank[i])])
                htmlCore.tableFooter()

            htmlCore.divEnd()
            htmlCore.end()
        else:
            # one table for everything
            htmlCore = HtmlCore()
            htmlCore.begin()
            htmlCore.divBegin('resDiv')
            selectedBpWindow = [key for key, val in choices.param.iteritems() if val == 'True']

            htmlCore.header('Compute RipleysK for bp window')
            htmlCore.tableHeader(
                ['Track names'] + ['Values for bp window: ' + str(bpW) + ' (Ranking)' for bpW in selectedBpWindow],
                sortable=True, tableId='resultsTable_' + str(bpW))

            rowVisRes = []
            rowCol = []
            for bpW in selectedBpWindow:

                analysisSpec.addParameter("bpWindow", str(bpW))

                # use gSuite from option
                gSuite = getGSuiteFromGalaxyTN(choices.gSuite)
                tracks = list(gSuite.allTracks())

                import scipy.stats as statRank

                row = []
                countI = 0
                elChParam = [key for key, val in choices.chParam.iteritems() if val == 'True']
                for track in tracks:
                    # analysisBins = GlobalBinSource(gSuite.genome)

                    if str(elChParam[0]) == 'Yes':
                        binFn = ExternalTrackManager.extractFnFromGalaxyTN(choices.track.split(':'))
                        analysisBins = UserBinSource('bed', binFn, genome=gSuite.genome)

                    else:
                        analysisBins = UserBinSource('*', '10m', genome=gSuite.genome)

                    result = doAnalysis(analysisSpec, analysisBins, [PlainTrack(track.trackName)])

                    resultDict = result.getGlobalResult()
                    row.append(resultDict['Result'])

                rank = len(row) + 1 - statRank.rankdata(row)

                rowVis = []
                rowC = []
                for i in range(0, len(tracks)):
                    rowC.append(str(row[i]) + " (" + str(int(rank[i])) + ")")
                    rowVis.append(row[i])
                rowCol.append(rowC)
                rowVisRes.append(rowVis)

            nRowColT = zip(*rowCol)
            nRowVisRes = map(list, (zip(*rowVisRes)))
            seriesName = []

            for i in range(0, len(nRowColT)):
                tN = tracks[i].trackName
                seriesName.append(tN[len(tN) - 1])
                newList = [tracks[i].trackName] + [el for el in list(nRowColT[i])]
                htmlCore.tableLine(el for el in newList)
            htmlCore.tableFooter()

            categories = [bpW for bpW in selectedBpWindow]

            from quick.webtools.restricted.visualization.visualizationGraphs import visualizationGraphs
            vg = visualizationGraphs()
            result = vg.drawLineChart(nRowVisRes,
                                      seriesName=seriesName,
                                      categories=categories,
                                      extraScriptButton=[
                                          OrderedDict({'Use linear scale': 'linear', 'Use log10 scale': 'logarithmic'}),
                                          'yAxisType']
                                      )
            htmlCore.line(result)

            htmlCore.divEnd()
            htmlCore.end()

        htmlCore.hideToggle(styleClass='debug')

        print htmlCore

    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''

        from gold.gsuite.GSuiteConstants import UNKNOWN, MULTIPLE

        errorStr = GeneralGuiTool._checkGSuiteFile(choices.gSuite)
        if errorStr:
            return errorStr

        from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
        gSuite = getGSuiteFromGalaxyTN(choices.gSuite)
        if gSuite.numTracks() == 0:
            return 'Please select a GSuite file with at least one track'

        if not gSuite.isPreprocessed():
            return 'Selected GSuite file is not preprocess. Please preprocess ' \
                   'the GSuite file before continuing the analysis.'

        if gSuite.trackType in [UNKNOWN]:
            return 'The track type of the GSuite file is not known. The track type ' \
                   'is needed for doing analysis.'

        if gSuite.trackType in [MULTIPLE]:
            return 'All tracks in the GSuite file needs to be of the same track ' \
                   'type. Multiple track types are not supported.'

        return None

    # @staticmethod
    # def getSubToolClasses():
    #    '''
    #    Specifies a list of classes for subtools of the main tool. These
    #    subtools will be selectable from a selection box at the top of the page.
    #    The input boxes will change according to which subtool is selected.
    #    '''
    #    return None
    #
    # @staticmethod
    # def isPublic():
    #    '''
    #    Specifies whether the tool is accessible to all users. If False, the
    #    tool is only accessible to a restricted set of users as defined in
    #    LocalOSConfig.py.
    #    '''
    #    return False
    #
    # @staticmethod
    # def isRedirectTool():
    #    '''
    #    Specifies whether the tool should redirect to an URL when the Execute
    #    button is clicked.
    #    '''
    #    return False
    #
    # @staticmethod
    # def getRedirectURL(choices):
    #    '''
    #    This method is called to return an URL if the isRedirectTool method
    #    returns True.
    #    '''
    #    return ''
    #
    # @staticmethod
    # def isHistoryTool():
    #    '''
    #    Specifies if a History item should be created when the Execute button is
    #    clicked.
    #    '''
    #    return True
    #
    # @staticmethod
    # def isDynamic():
    #    '''
    #    Specifies whether changing the content of texboxes causes the page to
    #    reload.
    #    '''
    #    return True
    #
    # @staticmethod
    # def getResetBoxes():
    #    '''
    #    Specifies a list of input boxes which resets the subsequent stored
    #    choices previously made. The input boxes are specified by index
    #    (starting with 1) or by key.
    #    '''
    #    return []
    #
    # @staticmethod
    # def getToolDescription():
    #    '''
    #    Specifies a help text in HTML that is displayed below the tool.
    #    '''
    #    return ''
    #
    # @staticmethod
    # def getToolIllustration():
    #    '''
    #    Specifies an id used by StaticFile.py to reference an illustration file
    #    on disk. The id is a list of optional directory names followed by a file
    #    name. The base directory is STATIC_PATH as defined by Config.py. The
    #    full path is created from the base directory followed by the id.
    #    '''
    #    return None
    #
    # @staticmethod
    # def getFullExampleURL():
    #    return None
    #
    # @classmethod
    # def isBatchTool(cls):
    #    '''
    #    Specifies if this tool could be run from batch using the batch. The
    #    batch run line can be fetched from the info box at the bottom of the
    #    tool.
    #    '''
    #    return cls.isHistoryTool()
    #
    # @staticmethod
    # def isDebugMode():
    #    '''
    #    Specifies whether debug messages are printed.
    #    '''
    #    return False
    #
    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'html'


class GenerateRipleysKForEachChromosomeSeparately(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Compute RipleysK for  for each chromosome separately"

    @staticmethod
    def getInputBoxNames():
        return [('Select track collection GSuite', 'gSuite'),
                ('Bp window', 'param'),
                ('if only in regions in gSuite', 'chParam'),
                ('Select track from history (Accepted formats: bed)', 'track')
                ]

    @staticmethod
    def getOptionsBoxGSuite():
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @staticmethod
    def getOptionsBoxParam(prevChoices):
        if prevChoices.gSuite:
            gSuite = getGSuiteFromGalaxyTN(prevChoices.gSuite)
            tracks = list(gSuite.allTracks())

            if len(tracks) > 0 and gSuite.isPreprocessed():
                return OrderedDict([
                    ('10', False),
                    ('100', True),
                    ('1000', False),
                    ('10000', False),
                    ('100000', False),
                    ('1000000', False)
                ])

    @staticmethod
    def getOptionsBoxChParam(prevChoices):
        if prevChoices.gSuite:
            gSuite = getGSuiteFromGalaxyTN(prevChoices.gSuite)
            tracks = list(gSuite.allTracks())

            if len(tracks) > 0 and gSuite.isPreprocessed():
                return OrderedDict([
                    ('Yes', True),
                    ('No', False)
                ])

    @staticmethod
    def getOptionsBoxTrack(prevChoices):
        if prevChoices.gSuite:
            gSuite = getGSuiteFromGalaxyTN(prevChoices.gSuite)
            tracks = list(gSuite.allTracks())

            return GeneralGuiTool.getHistorySelectionElement('category.bed', 'bed')

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        analysisSpec = AnalysisSpec(RipleysKStat)

        # one table per bpW
        htmlCore = HtmlCore()
        htmlCore.begin()
        htmlCore.divBegin('resDiv')
        selectedBpWindow = [key for key, val in choices.param.iteritems() if val == 'True']

        rowCol = []
        for bpW in selectedBpWindow:

            analysisSpec.addParameter("bpWindow", str(bpW))

            # use gSuite from option
            gSuite = getGSuiteFromGalaxyTN(choices.gSuite)
            tracks = list(gSuite.allTracks())

            nameTracks = []

            row = []
            countI = 0
            elChParam = [key for key, val in choices.chParam.iteritems() if val == 'True']
            i = 0
            for track in tracks:
                # analysisBins = GlobalBinSource(gSuite.genome)
                for chr in GenomeInfo.getChrList(gSuite.genome):
                    if str(elChParam[0]) == 'Yes':
                        binFn = ExternalTrackManager.extractFnFromGalaxyTN(choices.track.split(':'))
                        analysisBins = UserBinSource('bed', binFn, genome=gSuite.genome)

                    else:
                        analysisBins = UserBinSource(chr, '10m', genome=gSuite.genome)

                    nameTracks.append([str(tracks[i].trackName), str(chr)])
                    result = doAnalysis(analysisSpec, analysisBins, [PlainTrack(track.trackName)])

                    resultDict = result.getGlobalResult()

                    if len(resultDict) == 0:
                        row.append('No results')
                    else:
                        row.append(resultDict['Result'])
                i += 1

                # rank = len(row)+1 - statRank.rankdata(row)

            rowC = []
            for i in range(0, len(tracks) * len(GenomeInfo.getChrList(gSuite.genome))):
                rowC.append(str(row[i]))  # + " (" + str(int(rank[i])) + ")")
            rowCol.append(rowC)

        nRowColT = zip(*rowCol)

        nT = nameTracks[0][0]
        htmlCore.header('Compute RipleysK for bp window for' + str(nameTracks[0][0]))
        htmlCore.tableHeader(['Chr'] + ['Values for bp window: ' + str(bpW) + ' (Ranking)' for bpW in selectedBpWindow],
                             sortable=True, tableId='resultsTable_' + str(bpW))
        for j in range(0, len(nameTracks)):
            if nT == nameTracks[j][0]:
                newList = [nameTracks[j][1]] + [el for el in list(nRowColT[j])]
                htmlCore.tableLine(el for el in newList)
            elif j == len(nameTracks) - 1:
                newList = [nameTracks[j][1]] + [el for el in list(nRowColT[j])]
                htmlCore.tableFooter()
            else:
                htmlCore.tableFooter()
                htmlCore.header('Compute RipleysK for bp window for' + str(nameTracks[j][0]))
                htmlCore.tableHeader(
                    ['Chr'] + ['Values for bp window: ' + str(bpW) + ' (Ranking)' for bpW in selectedBpWindow],
                    sortable=True, tableId='resultsTable_' + str(bpW))
                newList = [nameTracks[j][1]] + [el for el in list(nRowColT[j])]
                nT = nameTracks[j][0]

        htmlCore.divEnd()
        htmlCore.end()

        htmlCore.hideToggle(styleClass='debug')

        print htmlCore

    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''

        from gold.gsuite.GSuiteConstants import UNKNOWN, MULTIPLE

        errorStr = GeneralGuiTool._checkGSuiteFile(choices.gSuite)
        if errorStr:
            return errorStr

        from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
        gSuite = getGSuiteFromGalaxyTN(choices.gSuite)
        if gSuite.numTracks() == 0:
            return 'Please select a GSuite file with at least one track'

        if not gSuite.isPreprocessed():
            return 'Selected GSuite file is not preprocess. Please preprocess ' \
                   'the GSuite file before continuing the analysis.'

        if gSuite.trackType in [UNKNOWN]:
            return 'The track type of the GSuite file is not known. The track type ' \
                   'is needed for doing analysis.'

        if gSuite.trackType in [MULTIPLE]:
            return 'All tracks in the GSuite file needs to be of the same track ' \
                   'type. Multiple track types are not supported.'

        return None

    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'html'


from quick.statistic.TwoLevelOverlapPreferenceStat import TwoLevelOverlapPreferenceStat


class GenerateTwoLevelOverlapPreferenceStat(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Compute Two level overlap preference"

    @staticmethod
    def getInputBoxNames():
        return [('Select track collection GSuite', 'gSuite'),
                ('Select track', 'track'),
                ('User bin source', 'binSourceParam')
                ]

    @staticmethod
    def getOptionsBoxGSuite():
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @staticmethod
    def getOptionsBoxTrack(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement('bed')

    @staticmethod
    def getOptionsBoxBinSourceParam(prevChoices):
        return ''

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        analysisSpec = AnalysisSpec(TwoLevelOverlapPreferenceStat)

        # use gSuite from option
        gSuite = getGSuiteFromGalaxyTN(choices.gSuite)
        tracks = list(gSuite.allTracks())

        trackComp = choices.track.split(':')

        trackName = ExternalTrackManager.getPreProcessedTrackFromGalaxyTN(gSuite.genome, trackComp)

        htmlCore = HtmlCore()
        htmlCore.begin()
        htmlCore.divBegin('resDiv')
        htmlCore.header('Compute two level overlap for: ' + str(trackName))
        htmlCore.tableHeader(['Track names'] + ['Individual coverage per bin correlation (Ranking)'] + [
            'Ratio Of Obs To Exp Given Individual Bin Coverages (Ranking)'] + [
                                 'Ratio Of Obs To Exp Given Global Coverages (Ranking)'], sortable=True,
                             tableId='resultsTable')

        import scipy.stats as statRank

        if choices.binSourceParam:
            binSourceParam = choices.binSourceParam
        else:
            binSourceParam = '10m'

        row = []
        for track in tracks:
            analysisBins = UserBinSource('*', binSourceParam, genome=gSuite.genome)
            result = doAnalysis(analysisSpec, analysisBins, [PlainTrack(track.trackName), PlainTrack(trackName)])
            resultDict = result.getGlobalResult()
            row.append([resultDict['IndividualCoveragePerBinCorrelation'],
                        resultDict['RatioOfObsToExpGivenIndividualBinCoverages'],
                        resultDict['RatioOfObsToExpGivenGlobalCoverages']])

        newRow = zip(*row)
        rank = []
        for nr in range(0, len(newRow)):
            rank.append(len(newRow[nr]) + 1 - statRank.rankdata(newRow[nr]))

        rankRes = zip(*rank)
        buildRow = []
        for i in range(0, len(row)):
            partEl = []
            for j in range(0, len(row[i])):
                partEl += [str(row[i][j]) + " (" + str(int(rankRes[i][j])) + ")"]
            buildRow.append(partEl)

        for i in range(0, len(tracks)):
            htmlCore.tableLine([tracks[i].trackName] + buildRow[i])
        htmlCore.tableFooter()

        htmlCore.divEnd()
        htmlCore.end()

        htmlCore.hideToggle(styleClass='debug')

        print htmlCore

    @staticmethod
    def validateAndReturnErrors(choices):
        '''-
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''

        from gold.gsuite.GSuiteConstants import UNKNOWN, MULTIPLE

        errorStr = GeneralGuiTool._checkGSuiteFile(choices.gSuite)
        if errorStr:
            return errorStr

        from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
        gSuite = getGSuiteFromGalaxyTN(choices.gSuite)
        if gSuite.numTracks() == 0:
            return 'Please select a GSuite file with at least one track'

        if not gSuite.isPreprocessed():
            return 'Selected GSuite file is not preprocess. Please preprocess ' \
                   'the GSuite file before continuing the analysis.'

        if gSuite.trackType in [UNKNOWN]:
            return 'The track type of the GSuite file is not known. The track type ' \
                   'is needed for doing analysis.'

        if gSuite.trackType in [MULTIPLE]:
            return 'All tracks in the GSuite file needs to be of the same track ' \
                   'type. Multiple track types are not supported.'

        return None

    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'html'


class driverGeneIdentification(GeneralGuiTool, UserBinMixin, DebugMixin):
    GSUITE_FILE_OPTIONS_BOX_KEYS = ['gSuiteFirst', 'gSuiteSecond']

    MERGE_INTRA_OVERLAPS = 'Merge any overlapping points/segments within the same track'
    ALLOW_MULTIPLE_OVERLAP = 'Allow multiple overlapping points/segments within the same track'
    GSUITE_ALLOWED_FILE_FORMATS = [GSuiteConstants.PREPROCESSED]
    GSUITE_ALLOWED_LOCATIONS = [GSuiteConstants.LOCAL]
    GSUITE_ALLOWED_TRACK_TYPES = [GSuiteConstants.POINTS,
                                  GSuiteConstants.VALUED_POINTS,
                                  GSuiteConstants.SEGMENTS,
                                  GSuiteConstants.VALUED_SEGMENTS]

    GSUITE_DISALLOWED_GENOMES = [GSuiteConstants.UNKNOWN,
                                 GSuiteConstants.MULTIPLE]

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Identification of genomic elements with high event recurrence "

    @classmethod
    def getInputBoxNames(cls):
        return [
                   ('Select target track collection GSuite', 'gSuiteFirst'),
                   ('Select reference track collection GSuite [rows]', 'gSuiteSecond'),
               ] + \
               cls.getInputBoxNamesForUserBinSelection() + \
               cls.getInputBoxNamesForDebug()

    @staticmethod
    def getOptionsBoxGSuiteFirst():
        return GeneralGuiTool.getHistorySelectionElement('gsuite', 'txt', 'tabular')

    @staticmethod
    def getOptionsBoxGSuiteSecond(prevChoices):  # Alternatively: getOptionsBox2()
        return GeneralGuiTool.getHistorySelectionElement('gsuite', 'txt', 'tabular')

    #     @staticmethod
    #     def getOptionsBoxStatistic(prevChoices):
    #         return [
    #                 STAT_OVERLAP_COUNT_BPS,
    # #                 STAT_OVERLAP_RATIO,
    # #                 STAT_FACTOR_OBSERVED_VS_EXPECTED,
    # #                 STAT_COVERAGE_RATIO_VS_QUERY_TRACK,
    # #                 STAT_COVERAGE_RATIO_VS_REF_TRACK
    #                 ]


    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        cls._setDebugModeIfSelected(choices)

        targetGSuite = getGSuiteFromGalaxyTN(choices.gSuiteFirst)
        refGSuite = getGSuiteFromGalaxyTN(choices.gSuiteSecond)

        regSpec, binSpec = UserBinMixin.getRegsAndBinsSpec(choices)

        #         from gold.statistic.RawOverlapStat import RawOverlapStat
        #
        #
        #         tab=[]
        #         tabName=[]


        #         for targetTrack in targetGSuite.allTracks():
        #             targetTrackName = targetTrack.title
        #             tabName.append(targetTrackName)
        #             tabPart=[]
        #             for refTrack in refGSuite.allTracks():
        #                 refTrackName = refTrack.title
        #                 analysisBins = GalaxyInterface._getUserBinSource(regSpec, binSpec, refTrack.genome)
        #                 results = doAnalysis(AnalysisSpec(RawOverlapStat), analysisBins, [PlainTrack(refTrack.trackName),PlainTrack(targetTrack.trackName)])
        #                 resultDict = results.getGlobalResult()
        #                 tabPart.append(resultDict)
        #             tab.append(tabPart)


        analysisDef = 'dummy -> RawOverlapStat'
        # analysisDef = 'dummy [withOverlaps=yes] -> RawOverlapAllowSingleTrackOverlapsStat'
        results = OrderedDict()

        for targetTrack in targetGSuite.allTracks():
            targetTrackName = targetTrack.title
            for refTrack in refGSuite.allTracks():
                refTrackName = refTrack.title
                if targetTrack.trackName == refTrack.trackName:
                    print targetTrack.title
                    print targetTrack.trackName
                    result = driverGeneIdentification.handleSameTrack(targetTrack.trackName, regSpec, binSpec,
                                                                      targetGSuite.genome, galaxyFn)
                else:
                    result = GalaxyInterface.runManual([targetTrack.trackName, refTrack.trackName],
                                                       analysisDef, regSpec, binSpec,
                                                       targetGSuite.genome, galaxyFn,
                                                       printRunDescription=False,
                                                       printResults=False, printProgress=False).getGlobalResult()
                if targetTrackName not in results:
                    results[targetTrackName] = OrderedDict()
                results[targetTrackName][refTrackName] = result

        stat = STAT_OVERLAP_COUNT_BPS
        statIndex = STAT_LIST_INDEX[stat]
        title = ''

        processedResults = []
        headerColumn = []
        for targetTrackName in targetGSuite.allTrackTitles():
            resultRowDict = processRawResults(results[targetTrackName])
            resultColumn = []
            headerColumn = []
            for refTrackName, statList in resultRowDict.iteritems():
                resultColumn.append(statList[statIndex])
                headerColumn.append(refTrackName)
            processedResults.append(resultColumn)

        outputTable = {}
        for elN in range(0, len(headerColumn)):
            outputTable[elN] = {}
            outputTable[elN]['id'] = headerColumn[elN]

        transposedProcessedResults = [list(x) for x in zip(*processedResults)]

        # second question sumSecondgSuite
        # first question numSecondgSuite
        # fifth question numSecondgSuitePercentage
        for i in range(0, len(transposedProcessedResults)):
            outputTable[i]['sumSecondgSuite'] = sum(transposedProcessedResults[i])
            if not 'numSecondgSuite' in outputTable[i]:
                outputTable[i]['numSecondgSuite'] = 0
            for j in range(0, len(transposedProcessedResults[i])):
                if transposedProcessedResults[i][j] >= 1:
                    outputTable[i]['numSecondgSuite'] += 1
                else:
                    outputTable[i]['numSecondgSuite'] += 0
            outputTable[i]['numSecondgSuitePercentage'] = float(outputTable[i]['numSecondgSuite']) / float(
                targetGSuite.numTracks()) * 100

        from gold.statistic.CountSegmentStat import CountSegmentStat
        from gold.statistic.CountPointStat import CountPointStat
        from gold.description.TrackInfo import TrackInfo

        # third question numPairBpSecondgSuite
        # fourth question numFreqBpSecondgSuite
        i = 0
        for refTrack in refGSuite.allTracks():
            formatName = TrackInfo(refTrack.genome, refTrack.trackName).trackFormatName
            analysisDef = CountSegmentStat if 'segments' in formatName else CountPointStat
            analysisBins = GalaxyInterface._getUserBinSource(regSpec, binSpec, refTrack.genome)
            results = doAnalysis(AnalysisSpec(analysisDef), analysisBins, [PlainTrack(refTrack.trackName)])
            resultDict = results.getGlobalResult()
            if len(resultDict) == 0:
                outputTable[i]['numPairBpSecondgSuite'] = None
                outputTable[i]['numFreqBpSecondgSuite'] = None
                outputTable[i]['numFreqUniqueBpSecondgSuite'] = None
            else:
                outputTable[i]['numPairBpSecondgSuite'] = resultDict['Result']
                if outputTable[i]['numPairBpSecondgSuite'] != 0:
                    outputTable[i]['numFreqBpSecondgSuite'] = float(outputTable[i]['sumSecondgSuite']) / float(
                        outputTable[i]['numPairBpSecondgSuite'])
                else:
                    outputTable[i]['numFreqBpSecondgSuite'] = None
                if outputTable[i]['sumSecondgSuite'] != 0:
                    outputTable[i]['numFreqUniqueBpSecondgSuite'] = float(
                        outputTable[i]['numPairBpSecondgSuite']) / float(outputTable[i]['sumSecondgSuite'])
                else:
                    outputTable[i]['numFreqUniqueBpSecondgSuite'] = None

            i += 1

        # sortTable
        outputTableLine = []
        for key, item in outputTable.iteritems():
            line = [
                item['id'],
                item['numSecondgSuite'],
                item['sumSecondgSuite'],
                item['numPairBpSecondgSuite'],
                item['numFreqBpSecondgSuite'],
                item['numFreqUniqueBpSecondgSuite'],
                item['numSecondgSuitePercentage']
            ]
            outputTableLine.append(line)

        import operator
        outputTableLineSort = sorted(outputTableLine, key=operator.itemgetter(1), reverse=True)

        tableHeader = ['Region ID ',
                       'Number of cases with at least one event ',
                       'Total number of events',
                       'Genome coverage (unique bp)',
                       'Number of events per unique bp',
                       'Number of unique bp per event',
                       'Percentage of cases with at least one event']
        htmlCore = HtmlCore()

        htmlCore.begin()

        htmlCore.line("<b>Identification of genomic elements with high event recurrence</b> ")

        htmlCore.header(title)
        htmlCore.divBegin('resultsDiv')
        htmlCore.tableHeader(tableHeader, sortable=True, tableId='resultsTable')

        for line in outputTableLineSort:
            htmlCore.tableLine(line)

        plotRes = []
        plotXAxis = []
        for lineInx in range(1, len(outputTableLineSort[0])):
            plotResPart = []
            plotXAxisPart = []
            for lineInxO in range(0, len(outputTableLineSort)):
                # if outputTableLineSort[lineInxO][lineInx]!=0 and
                # if outputTableLineSort[lineInxO][lineInx]!=None:
                plotResPart.append(outputTableLineSort[lineInxO][lineInx])
                plotXAxisPart.append(outputTableLineSort[lineInxO][0])
            plotRes.append(plotResPart)
            plotXAxis.append(plotXAxisPart)

        htmlCore.tableFooter()
        htmlCore.divEnd()

        htmlCore.divBegin('plot', style='padding-top:20px;margin-top:20px;')

        vg = visualizationGraphs()
        res = vg.drawColumnCharts(
            plotRes,
            titleText=tableHeader[1:],
            categories=plotXAxis,
            height=500,
            xAxisRotation=270,
            xAxisTitle='Ragion ID',
            yAxisTitle='Number of cases with at least one event',
            marginTop=30,
            addTable=True,
            sortableAccordingToTable=True,
            legend=False
        )
        htmlCore.line(res)
        htmlCore.divEnd()

        htmlCore.hideToggle(styleClass='debug')
        htmlCore.end()

        print htmlCore

    @classmethod
    def getToolDescription(cls):
        core = HtmlCore()

        core.paragraph('''

        <p>The tool provides screening of two track collections (GSuite files) against each other:</p>

        <p>- The target collection should corespond to a collection of cases (e.g. patients), each of which is defined by a set of events (e.g. somatic mutations). Any events sufficiently characterized by genomic locations/regions can be considered.</p>

        <p>- The reference collection should define genomic elements (e.g. genes) for which event recurrence should be calculated. Each genomic element can be composed of multiple subunits (e.g. exons in the case of genes), forming an individual track.</p>

        <p>To run the tool, follow these steps:</p>

        <p>Select the target and reference track collections (GSuite files) from your current history. Select genomic regions to which the analysis should be limited (or keep the default choice of chromosome arms).
        Click "Execute" in order to start the analysis.</p>''')

        core.paragraph('The results are presented in a sortable table and an interactive chart.')

        core.paragraph('''
        <p>Examples:</p>

        <p>- The tool can be used for identification of "cancer driver genes" (i.e. genes most frequently mutated in a patient cohort), with the reference collection serving for accurate description of a custom gene panel or, generally, the regions of any targeted sequencing study. Mutation frequencies are automatically normalized with respect to the total observed gene lengths.</p>

        <p>- Similarly, one could investigate the number of transcription factors (TFs) potentially binding to the intronic regions of genes. In this case, the target collection should map the binding sites of TFs (with one TF per track), while the reference collection should correspond to the intronic genomic regions (with each gene's introns occupying an own track). By default, both the total as well as the normalized counts of TFs (and TF binding sites) per gene would be included in the results.</p>
        ''')

        cls._addGSuiteFileDescription(core,
                                      allowedLocations=cls.GSUITE_ALLOWED_LOCATIONS,
                                      allowedFileFormats=cls.GSUITE_ALLOWED_FILE_FORMATS,
                                      allowedTrackTypes=cls.GSUITE_ALLOWED_TRACK_TYPES,
                                      disallowedGenomes=cls.GSUITE_DISALLOWED_GENOMES)

        return str(core)

    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'customhtml'

    @classmethod
    def handleSameTrack(cls, trackName, regSpec, binSpec, genome, galaxyFn):

        analysisSpec = AnalysisSpec(RawOverlapToSelfStat)
        analysisBins = GalaxyInterface._getUserBinSource(regSpec, binSpec, genome)

        return doAnalysis(analysisSpec, analysisBins, [Track(trackName)]).getGlobalResult()

    @staticmethod
    def isDebugMode():
        '''
        Specifies whether debug messages are printed.
        '''
        return False

    @staticmethod
    def isPublic():
        '''
       Specifies whether the tool is accessible to all users. If False, the
       tool is only accessible to a restricted set of users as defined in
       LocalOSConfig.py.
       '''
        return True


class mergeTracksFromGSuite(GeneralGuiTool):
    OUTPUT_TRACKS_SUFFIX = 'bed'

    @staticmethod
    def getToolName():
        return "Concatenate selected tracks from gSuite [RP manuscript tool]"

    @staticmethod
    def getInputBoxNames():
        return [('Select first gsuite', 'gsuite1'),
                ('Select tracks', 'tracksGSuite1'),
                ]

    @staticmethod
    def getOptionsBoxGsuite1():
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @staticmethod
    def getOptionsBoxTracksGSuite1(prevChoices):
        if not prevChoices.gsuite1:
            return

        gSuite = getGSuiteFromGalaxyTN(prevChoices.gsuite1)

        attrDict = {}
        for l in gSuite.allTrackTitles():
            attrDict[l] = False
        return attrDict

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        gsuiteName1 = choices.gsuite1
        gSuite1 = getGSuiteFromGalaxyTN(gsuiteName1)

        trackNamesDict = choices.tracksGSuite1

        bedFileName = 'merged'
        for title in gSuite1.allTrackTitles():
            if trackNamesDict[title] == 'True':
                bedFileName += '-' + title

        outGSuite = GSuite()

        uri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn,
                                            extraFileName=bedFileName,
                                            suffix='bed')

        gSuiteTrack1 = GSuiteTrack(uri)
        outFn1 = gSuiteTrack1.path
        ensurePathExists(outFn1)

        with open(outFn1, 'w') as outputFile:
            for title in gSuite1.allTrackTitles():
                if trackNamesDict[title] == 'True':

                    gSuiteTrack = gSuite1.getTrackFromTitle(title)

                    i = 0
                    with open(gSuiteTrack.path) as f:
                        for x in f.readlines():
                            outputFile.write(x)

        outputFile.close()

        outGSuite.addTrack(GSuiteTrack(uri, title=''.join(bedFileName), genome=gSuite1.genome))

        GSuiteComposer.composeToFile(outGSuite, cls.extraGalaxyFn['merged Gsuite'])

        print 'Gsuite is in the history'

    @staticmethod
    def validateAndReturnErrors(choices):
        return None

    @classmethod
    def getExtraHistElements(cls, choices):
        return [HistElement('merged Gsuite', 'gsuite')]


# tool for Pasquale
class intersectionGSuite(GeneralGuiTool):
    WITH_OVERLAPS = 'Allow multiple overlapping points/segments within the same track'
    NO_OVERLAPS = 'Merge any overlapping points/segments within the same track'

    GSUITE_OUTPUT_TRACK_TYPE = GSuiteConstants.SEGMENTS
    OUTPUT_TRACKS_SUFFIX = 'bed'

    @staticmethod
    def getToolName():
        return "Intersect two gsuites based on metadata column"

    @staticmethod
    def getInputBoxNames():
        return [('Select first gsuite', 'gsuite1'),
                ('Select column from metadata of first guiste', 'metadata1'),
                ('Select second gsuite', 'gsuite2'),
                ('Select column from metadata of second guiste', 'metadata2'),
                ('Overlap handling:', 'withOverlaps')
                ]

    @staticmethod
    def getOptionsBoxGsuite1():
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @staticmethod
    def getOptionsBoxMetadata1(prevChoices):
        if not prevChoices.gsuite1:
            return

        gSuite = getGSuiteFromGalaxyTN(prevChoices.gsuite1)

        attributeList = gSuite.attributes

        return [TITLE_COL] + attributeList

    @staticmethod
    def getOptionsBoxGsuite2(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @staticmethod
    def getOptionsBoxMetadata2(prevChoices):
        if not prevChoices.gsuite2:
            return

        gSuite = getGSuiteFromGalaxyTN(prevChoices.gsuite2)

        attributeList = gSuite.attributes

        return [TITLE_COL] + attributeList

    @classmethod
    def getOptionsBoxWithOverlaps(cls, prevChoices):
        return [cls.NO_OVERLAPS, cls.WITH_OVERLAPS]

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        from gold.origdata.TrackGenomeElementSource import TrackViewListGenomeElementSource
        from gold.origdata.FileFormatComposer import getComposerClsFromFileSuffix

        gsuiteName1 = choices.gsuite1
        gSuite1 = getGSuiteFromGalaxyTN(gsuiteName1)
        metaAtr1 = choices.metadata1
        keys1 = gSuite1.getAttributeValueList(metaAtr1)
        values1 = gSuite1.allTrackTitles()

        t = zip(values1, keys1)
        dictAttr1 = dict()
        for x, y in t:
            if (dictAttr1.has_key(y)):
                dictAttr1[y].append(x)
            else:
                dictAttr1[y] = [x]

        gsuiteName2 = choices.gsuite2
        gSuite2 = getGSuiteFromGalaxyTN(gsuiteName2)
        metaAtr2 = choices.metadata2
        keys2 = gSuite2.getAttributeValueList(metaAtr2)
        values2 = gSuite2.allTrackTitles()

        t = zip(values2, keys2)
        dictAttr2 = dict()
        for x, y in t:
            if (dictAttr2.has_key(y)):
                dictAttr2[y].append(x)
            else:
                dictAttr2[y] = [x]

        genome = gSuite1.genome

        outGSuite = GSuite()
        analysisDef = '-> TrackIntersectionStat'

        for key1, trackNameList1 in dictAttr1.iteritems():
            if key1 in dictAttr2.keys():
                for trackName2 in dictAttr2[key1]:
                    for trackName1 in trackNameList1:

                        track1 = gSuite1.getTrackFromTitle(trackName1)
                        track2 = gSuite2.getTrackFromTitle(trackName2)

                        name = track1.title + '--' + track2.title

                        # create a new temporary file
                        resFile = GalaxyRunSpecificFile([name + '.tmp'], galaxyFn)

                        pathToNewFile = os.path.dirname(os.path.realpath(resFile.getDiskPath())) + '/' + name

                        # create galaxyTN for preprocessed data

                        # if I do not want to have proeprocess track then uncomment it
                        uri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn,
                                                            extraFileName=name,
                                                            suffix=cls.OUTPUT_TRACKS_SUFFIX)

                        gSuiteTrack1 = GSuiteTrack(uri)
                        outFn1 = gSuiteTrack1.path
                        ensurePathExists(outFn1)

                        if choices.withOverlaps == cls.NO_OVERLAPS:
                            res = GalaxyInterface.runManual([track1.trackName, track2.trackName], analysisDef, '*', '*',
                                                            genome=genome, galaxyFn=galaxyFn, username=username)

                            trackViewList = [res[key]['Result'] for key in sorted(res.keys())]

                            # if I do not want to have proeprocess track then uncomment it
                            tvGeSource = TrackViewListGenomeElementSource(genome, trackViewList, [name])

                            # tvGeSource = TrackViewListGenomeElementSource(genome, trackViewList, galaxyTN)


                            composerCls = getComposerClsFromFileSuffix(cls.OUTPUT_TRACKS_SUFFIX)
                            composerCls(tvGeSource).composeToFile(pathToNewFile)

                        from gold.origdata.GenomeElementSource import GenomeElementSource
                        geSource = GenomeElementSource(pathToNewFile, genome=genome, suffix=cls.OUTPUT_TRACKS_SUFFIX)

                        try:
                            geSource.parseFirstDataLine()
                        except:  # Most likely empty file
                            continue

                        # stdTrackName = ExternalTrackManager.getPreProcessedTrackFromGalaxyTN(genome, galaxyTN)
                        # uri = HbGSuiteTrack.generateURI(trackName=stdTrackName)


                        # comment
                        # track1.attributes are only attributes from track1 , we need from both

                        # outGSuite.addTrack(
                        #     GSuiteTrack(uri, title=name, trackType=cls.GSUITE_OUTPUT_TRACK_TYPE,
                        #                 genome=genome, attributes=track1.attributes))

                        # if I do not want to have proeprocess track then uncomment it


                        attr1 = track1.attributes
                        attr2 = track2.attributes

                        alldict = [attr1, attr2]
                        allkey = reduce(set.union, map(set, map(dict.keys, alldict)))

                        allDictElements = OrderedDict()
                        for ka in allkey:
                            if ka in attr1.keys():
                                allDictElements[ka] = [attr1[ka]]
                            if ka in attr2.keys():
                                if ka in allDictElements.keys():
                                    if not attr2[ka] in allDictElements[ka]:
                                        allDictElements[ka].append(attr2[ka])
                                else:
                                    allDictElements[ka] = [attr2[ka]]

                        allDictElementsNew = OrderedDict()
                        for key, it in allDictElements.iteritems():
                            allDictElementsNew[key] = ', '.join(it)

                        outGSuite.addTrack(
                            GSuiteTrack(uri, title=name, genome=gSuite1.genome, attributes=allDictElementsNew))

        GSuiteComposer.composeToFile(outGSuite, cls.extraGalaxyFn['intersectedGSuite'])

        print 'Gsuite is in the history'

    @staticmethod
    def validateAndReturnErrors(choices):
        return None

    @classmethod
    def getExtraHistElements(cls, choices):
        return [HistElement('intersectedGSuite', 'gsuite')]




        # code for R which WORKS!
        # openRfigure from quick.util.static
        # GalaxyRunSpecificFile
        # use rPlot
        # closeRfigure
        # getLink or getEmbeddedImage

    #         from proto.RSetup import robjects, r
    #         rPlot = robjects.r.plot
    #         rPlot([1,2,3], [4,5,6], type='p', xlim=[0,2], ylim=[0,2], main = 'tit', xlab='xlab', ylab='ylab')
    # #         print RPlotUtil.drawXYPlot([1,2,3], [4,5,6], plotType='p', xLim=[0,2], yLim=[0,2], mainTitle='tit', xTitle='xTit', yTitle='yTit')
    # #         res = RPlotUtil.drawXYPlot([1,2,3], [4,5,6], plotType='p', xLim=[0,2], yLim=[0,2], mainTitle='tit', xTitle='xTit', yTitle='yTit')
    # #
    #
    #
    #         core = HtmlCore()
    #         core.begin()
    #         core.divBegin(divId='plot')
    #         core.image(plotOutput.getURL())
    #         core.divEnd()
    #         core.end()
    #         print core
    # @staticmethod
    # def isPublic():
    #    '''
    #    Specifies whether the tool is accessible to all users. If False, the
    #    tool is only accessible to a restricted set of users as defined in
    #    LocalOSConfig.py.
    #    '''
    #    return False
