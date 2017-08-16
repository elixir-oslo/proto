from collections import OrderedDict

from quick.application.GalaxyInterface import GalaxyInterface
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.util.TrackReportCommon import STAT_OVERLAP_COUNT_BPS,\
    STAT_OVERLAP_RATIO, STAT_FACTOR_OBSERVED_VS_EXPECTED, processResult, \
    STAT_COVERAGE_RATIO_VS_REF_TRACK, STAT_COVERAGE_RATIO_VS_QUERY_TRACK, STAT_COVERAGE_REF_TRACK_BPS
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.mixin.UserBinMixin import UserBinMixin


class CountStatisticForCombinationsFromTwoLevelSuites(GeneralGuiTool, UserBinMixin):
    GSUITE_FILE_OPTIONS_BOX_KEYS = ['firstGSuite', 'secondGSuite']

    STAT_LIST_INDEX = [
                        STAT_OVERLAP_COUNT_BPS,
                        STAT_COVERAGE_REF_TRACK_BPS,
                        STAT_OVERLAP_RATIO,
                        STAT_FACTOR_OBSERVED_VS_EXPECTED,
                        STAT_COVERAGE_RATIO_VS_QUERY_TRACK,
                        STAT_COVERAGE_RATIO_VS_REF_TRACK
                        ] 
    
#     [
#                 STAT_OVERLAP_COUNT_BPS,
#                 STAT_OVERLAP_RATIO,
#                 STAT_FACTOR_OBSERVED_VS_EXPECTED,
#                 STAT_COVERAGE_RATIO_VS_QUERY_TRACK,
#                 STAT_COVERAGE_RATIO_VS_REF_TRACK
#                 ]
    
    
    
    MERGE_INTRA_OVERLAPS = 'Merge any overlapping points/segments within the same track'
    ALLOW_MULTIPLE_OVERLAP = 'Allow multiple overlapping points/segments within the same track'
    
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Count statistic for combinations from level gSuites"

    @classmethod
    def getInputBoxNames(cls):
        return [
                ('Select first GSuite','firstGSuite'),
                ('Select column','firstGSuiteColumn'),
                ('Select second GSuite','secondGSuite'),
                ('Select column','secondGSuiteColumn'),
                ('Check genome or select column with multi genome','genome'),
                ('Select statistic type', 'type'),
                ('Select statistic', 'statistic'),
                ('Select overlap handling', 'intraOverlap')
                ] + cls.getInputBoxNamesForUserBinSelection()
                

    @staticmethod
    def getOptionsBoxFirstGSuite():
        return GeneralGuiTool.getHistorySelectionElement('gsuite', 'txt', 'tabular')
    
     
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
        
        #it will be good to have box with selected genome instead of text
        
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
                    retDict[et+' (first GSuite)'] = False
                    
                for et in attributeList2:
                    retDict[et+' (second GSuite)'] = False
                
                return retDict
        else:
            return 
            #genome = 'multi' #then should be taken from one column


    @staticmethod
    def getOptionsBoxType(prevChoices):
        return ['basic', 'advanced']
    
    @staticmethod
    def getOptionsBoxStatistic(prevChoices):
        if prevChoices.type == 'basic':
            return CountStatisticForCombinationsFromTwoLevelSuites.STAT_LIST_INDEX
        else:
            return ['Number of touched segments']
    
    @staticmethod
    def getOptionsBoxIntraOverlap(prevChoices):
        return [CountStatisticForCombinationsFromTwoLevelSuites.MERGE_INTRA_OVERLAPS,
                 CountStatisticForCombinationsFromTwoLevelSuites.ALLOW_MULTIPLE_OVERLAP]


    @classmethod
    def returnGSuiteLevelDepth(cls, gSuite):
        gSuite = getGSuiteFromGalaxyTN(gSuite)
        attributeList = gSuite.attributes
        
        #attributeList = [TITLE_COL] + attributeList
        attributeList = ['None'] + attributeList
        from quick.gsuite.GSuiteUtils import getAllTracksWithAttributes
        attributeValuesList = getAllTracksWithAttributes(gSuite)
        
        return attributeList, attributeValuesList
    
    @classmethod
    def makeAnalysis(cls, gSuite1, gSuite2, columnsForStat, galaxyFn, choices):

        genomeType = 'single'
        
        #if True then none of column in both gsuite are equal then for example, for gSUite 2 dim and 3 dim we have 5 dim
        # in the other case (when some columns are equal we have 4 dim)
        checkWhichDimension = True 
        for el in columnsForStat:
            if el == 0:
                checkWhichDimension=False
                break
                
        
        if choices.type == 'basic':        
            stat = choices.statistic
            statIndex = CountStatisticForCombinationsFromTwoLevelSuites.STAT_LIST_INDEX
            statIndex = statIndex.index(stat)
        else:
            stat= '0'
            statIndex = 0
        
        if choices.intraOverlap == CountStatisticForCombinationsFromTwoLevelSuites.MERGE_INTRA_OVERLAPS:
            analysisDef = 'dummy -> RawOverlapStat'
        else:
            analysisDef = 'dummy [withOverlaps=yes] -> RawOverlapAllowSingleTrackOverlapsStat'
        
        regSpec, binSpec = UserBinMixin.getRegsAndBinsSpec(choices)
        
        listResults = []
        for el1 in gSuite1:
            for el2 in gSuite2:
                if genomeType == 'single':
                    
                    listPartResults=[]

                    if (checkWhichDimension == True and el1[columnsForStat[0]] == el2[columnsForStat[1]]) or (checkWhichDimension == False):
                        gSuite1Path = el1[0]#path for track1
                        gSuite2Path = el2[0]#path for track2
                        
                        #print [gSuite1Path, gSuite2Path]
                        
                        result = GalaxyInterface.runManual([gSuite1Path, gSuite2Path],
                                   analysisDef, regSpec, binSpec, choices.genome, galaxyFn,
                                   printRunDescription=False,
                                   printResults=False)
                        
                        
                        #print str(result) + '<br \>'

                        #print str(processResult(result.getGlobalResult())) + '<br \>'

                        resVal = processResult(result.getGlobalResult())[statIndex]
                        
                    else:
                        resVal = 0
                    
                    if checkWhichDimension == False:
                        listPartResults = el1[1:] + el2[1:] + [resVal]
                    else:
                        shorterEl2=[]
                        for eN in range(0, len(el2[1:])):
                            if el2[1:][eN] != el2[columnsForStat[1]]:
                                shorterEl2.append(el2[1:][eN])
                        #listPartResults = el1[1:] + shorterEl2 + [resVal]
                        listPartResults = el1[1:] + el2[1:] + [resVal]
                        
                    listResults.append(listPartResults)
        
                    
                if genomeType == 'multi':
                    #count only values with the same genome
                    pass
            
        return listResults

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        firstGSuite = choices.firstGSuite
        secondGSuite = choices.secondGSuite
        
        #for now support only with the same genome
        #later check if Ordered Dict or if string
        attributeListG1, attributeValuesListG1 = CountStatisticForCombinationsFromTwoLevelSuites.returnGSuiteLevelDepth(firstGSuite)
        attributeListG2, attributeValuesListG2 = CountStatisticForCombinationsFromTwoLevelSuites.returnGSuiteLevelDepth(secondGSuite)
           
        #counting for column start from zero, zero is reserved for title
        
        columnsForStat = [attributeListG1.index(str(choices.firstGSuiteColumn)), attributeListG2.index(str(choices.secondGSuiteColumn))]
        
        listResult = CountStatisticForCombinationsFromTwoLevelSuites.makeAnalysis(attributeValuesListG1, attributeValuesListG2, columnsForStat, galaxyFn, choices)
        
        strr = ''
        for row in listResult:
            for r in row:
                strr += str(r) + '\t'
            strr += '\n'

        #print strr

        open(galaxyFn, 'w').writelines( [strr] )
        
        
        
#         core = HtmlCore()
#         core.begin()
#         
#         for row in listResult:
#             strr = ''
#             for r in row:
#                 strr += str(r) + '\t'
#             strr += '\n'
#             
#         core.line(strr)
#         
#         core.end()
#         
#         core.hideToggle(styleClass='debug')
#         
#         print str(core)
         

    @staticmethod
    def validateAndReturnErrors(choices):
        return None

    #@staticmethod
    #def getSubToolClasses():
    #    '''
    #    Specifies a list of classes for subtools of the main tool. These
    #    subtools will be selectable from a selection box at the top of the page.
    #    The input boxes will change according to which subtool is selected.
    #    '''
    #    return None
    #
    @staticmethod
    def isPublic():
        return True
    
    @staticmethod
    def getOutputFormat(choices):
        return 'tabular'
        #return 'customhtml'
