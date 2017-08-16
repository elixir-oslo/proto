from gold.application.HBAPI import doAnalysis, GlobalBinSource, AnalysisSpec, PlainTrack
from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.application.GalaxyInterface import GalaxyInterface
from quick.util.TrackReportCommon import STAT_OVERLAP_COUNT_BPS,\
    STAT_OVERLAP_RATIO, STAT_FACTOR_OBSERVED_VS_EXPECTED, processResult,\
    STAT_COVERAGE_RATIO_VS_REF_TRACK, STAT_COVERAGE_RATIO_VS_QUERY_TRACK, STAT_COVERAGE_REF_TRACK_BPS
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.mixin.UserBinMixin import UserBinMixin
from quick.webtools.restricted.ScreenTwoTrackCollectionsAgainstEachOther2LevelDepthCutCube import \
    preporcessResults3, addJS3levelOptionList


# This is a template prototyping GUI that comes together with a corresponding
# web page.

class ScreenTwoTrackCollectionsAgainstEachOther2LevelDepth\
            (GeneralGuiTool, UserBinMixin):
    GSUITE_FILE_OPTIONS_BOX_KEYS = ['gSuiteFirst', 'gSuiteSecond']

    MERGE_INTRA_OVERLAPS = 'Merge any overlapping points/segments within the same track'
    ALLOW_MULTIPLE_OVERLAP = 'Allow multiple overlapping points/segments within the same track'
    
    STAT_LIST_INDEX = [
                        STAT_OVERLAP_COUNT_BPS,
                        STAT_COVERAGE_REF_TRACK_BPS,
                        STAT_OVERLAP_RATIO,
                        STAT_FACTOR_OBSERVED_VS_EXPECTED,
                        STAT_COVERAGE_RATIO_VS_QUERY_TRACK,
                        STAT_COVERAGE_RATIO_VS_REF_TRACK
                        ] 
    
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Screen Two Track Collections Against Each Other 2 Level Depth"

    @classmethod
    def getInputBoxNames(cls):
        return [('Select track collection GSuite (2 level depth)','gSuiteFirst'),
                ('Select fetaures track collection GSuite', 'gSuiteSecond'),
                ('Select statistic type', 'type'),
                ('Select statistic', 'statistic'),
                ('Select overlap handling', 'intraOverlap')
                ] + cls.getInputBoxNamesForUserBinSelection()

    #@staticmethod
    #def getInputBoxOrder():
    #    '''
    #    Specifies the order in which the input boxes should be displayed, as a
    #    list. The input boxes are specified by index (starting with 1) or by
    #    key. If None, the order of the input boxes is in the order specified by
    #    getInputBoxNames.
    #    '''
    #    return None

    @staticmethod
    def getOptionsBoxGSuiteFirst(): # Alternatively: getOptionsBox1()
        '''
        Defines the type and contents of the input box. User selections are
        returned to the tools in the prevChoices and choices attributes to other
        methods. These are lists of results, one for each input box (in the
        order specified by getInputBoxOrder()).

        The input box is defined according to the following syntax:

        Selection box:          ['choice1','choice2']
        - Returns: string

        Text area:              'textbox' | ('textbox',1) | ('textbox',1,False)
        - Tuple syntax: (contents, height (#lines) = 1, read only flag = False)
        - The contents is the default value shown inside the text area
        - Returns: string

        Password field:         '__password__'
        - Returns: string

        Genome selection box:   '__genome__'
        - Returns: string

        Track selection box:    '__track__'
        - Requires genome selection box.
        - Returns: colon-separated string denoting track name

        History selection box:  ('__history__',) | ('__history__', 'bed', 'wig')
        - Only history items of specified types are shown.
        - Returns: colon-separated string denoting galaxy track name, as
                   specified in ExternalTrackManager.py.

        History check box list: ('__multihistory__', ) | ('__multihistory__', 'bed', 'wig')
        - Only history items of specified types are shown.
        - Returns: OrderedDict with galaxy id as key and galaxy track name
                   as value if checked, else None.

        Hidden field:           ('__hidden__', 'Hidden value')
        - Returns: string

        Table:                  [['header1','header2'], ['cell1_1','cell1_2'], ['cell2_1','cell2_2']]
        - Returns: None

        Check box list:         OrderedDict([('key1', True), ('key2', False), ('key3', False)])
        - Returns: OrderedDict from key to selection status (bool).
        '''
        return GeneralGuiTool.getHistorySelectionElement('gsuite', 'txt', 'tabular')

    @staticmethod
    def getOptionsBoxGSuiteSecond(prevChoices): # Alternatively: getOptionsBox2()
        '''
        See getOptionsBoxFirstKey().

        prevChoices is a namedtuple of selections made by the user in the
        previous input boxes (that is, a namedtuple containing only one element
        in this case). The elements can accessed either by index, e.g.
        prevChoices[0] for the result of input box 1, or by key, e.g.
        prevChoices.key (case 2).
        '''
        return GeneralGuiTool.getHistorySelectionElement('gsuite', 'txt', 'tabular')
    
    @staticmethod
    def getOptionsBoxType(prevChoices):
        return ['basic', 'advanced']
    
    @staticmethod
    def getOptionsBoxStatistic(prevChoices):
        if prevChoices.type == 'basic':
            return ScreenTwoTrackCollectionsAgainstEachOther2LevelDepth.STAT_LIST_INDEX
#             return [STAT_OVERLAP_COUNT_BPS,
#                 STAT_OVERLAP_RATIO,
#                 STAT_FACTOR_OBSERVED_VS_EXPECTED,
#                 STAT_COVERAGE_RATIO_VS_QUERY_TRACK,
#                 STAT_COVERAGE_RATIO_VS_REF_TRACK
#                 ]
        else:
            return ['Number of touched segments']
    
    @staticmethod
    def getOptionsBoxIntraOverlap(prevChoices):
        return [ScreenTwoTrackCollectionsAgainstEachOther2LevelDepth.MERGE_INTRA_OVERLAPS,
                 ScreenTwoTrackCollectionsAgainstEachOther2LevelDepth.ALLOW_MULTIPLE_OVERLAP]

    #@staticmethod
    #def getInfoForOptionsBoxKey(prevChoices):
    #    '''
    #    If not None, defines the string content of an clickable info box beside
    #    the corresponding input box. HTML is allowed.
    #    '''
    #    return None

    #@staticmethod
    #def getDemoSelections():
    #    return ['testChoice1','..']
    
    @staticmethod
    def returnGSuiteDict3LevelDept(par):
        from quick.application.ExternalTrackManager import ExternalTrackManager
        with open(ExternalTrackManager.extractFnFromGalaxyTN(par), 'r') as f:
            data=[x.strip('\n') for x in f.readlines()]
        f.closed
        
        ll=[]
        for i in data:
            new = [x for x in i.split('\t')]
            ll.append(new)
        
        
        i=0
        targetTracksDict = []
        ddList=[]
        dFv1List=[]
        for l in ll:
            if i>4:
                if i==5:
                    fv1 = l[2]  #genome
                    fv2 = l[3]  #dir_level_1
                
                dfV0={'folderName1':fv2, 'dataFolderValue1': dFv1List}
                if fv2 == l[3]:
                    path = l[0].split('/')
                    path.pop(0)
                    dFv1={'folderName2': l[4], 'trackName': l[1], 'trackPath' : path}
                    dFv1List.append(dFv1)
                else:
                    ddList.append(dfV0) 
                    fv2=l[3]
                    dFv1List=[]
                    path = l[0].split('/')
                    path.pop(0)
                    dFv1={'folderName2': l[4], 'trackName': l[1], 'trackPath' : path}
                    dFv1List.append(dFv1)
                            
                    
                        
                if fv1 != l[2]:            
                    dd={'genome':fv1, 'dataFolderValue0': ddList}
                    targetTracksDict.append(dd)
                    fv1=l[2]
                    ddList=[]
            if len(ll)-1 == i:
                ddList.append(dfV0) 
                dd={'genome':fv1, 'dataFolderValue0': ddList}
                targetTracksDict.append(dd)    
                
            i+=1
            
            
        return targetTracksDict
    
    @staticmethod
    def returnGSuiteDict2LevelDept(par):
        from quick.application.ExternalTrackManager import ExternalTrackManager
        with open(ExternalTrackManager.extractFnFromGalaxyTN(par), 'r') as f:
            data=[x.strip('\n') for x in f.readlines()]
        f.closed
        
        ll=[]
        for i in data:
            new = [x for x in i.split('\t')]
            ll.append(new)
        
        
        targetTracksDict = []
        d=[]
        i=0
        for l in ll:
            if i>4:
                if i== 5:
                    fv1=l[2] #genome
                if fv1 != l[2]:
                    dd={'genome':fv1, 'dataFolderValue0': d}
                    targetTracksDict.append(dd)
                    fv1 = l[2]
                    dd={}
                    d=[]
                path = l[0].split('/')
                path.pop(0)
                d.append({'folderName2': l[3], 'trackName': l[1], 'trackPath' : path})
                    
                if len(ll)-1 == i:
                    dd={'genome':fv1, 'dataFolderValue0': d}
                    targetTracksDict.append(dd)
            i+=1
        return targetTracksDict

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):

        #targetTrackNames, targetTrackCollection, targetTrackGenome = getGSuiteDataFromGalaxyTN(choices.gSuiteFirst)
        
        gFirst=choices.gSuiteFirst.split(':')
        firstGSuite = ScreenTwoTrackCollectionsAgainstEachOther2LevelDepth.returnGSuiteDict3LevelDept(gFirst)
        
        gSecond=choices.gSuiteSecond.split(':')
        secondGSuite = ScreenTwoTrackCollectionsAgainstEachOther2LevelDepth.returnGSuiteDict2LevelDept(gSecond)
        
        
        
        regSpec, binSpec = UserBinMixin.getRegsAndBinsSpec(choices)
        
        if choices.intraOverlap == ScreenTwoTrackCollectionsAgainstEachOther2LevelDepth.MERGE_INTRA_OVERLAPS:
            analysisDef = 'dummy -> RawOverlapStat'
        else:
            analysisDef = 'dummy [withOverlaps=yes] -> RawOverlapAllowSingleTrackOverlapsStat'
        
        
        if choices.type == 'basic':
            results=[]
            for elFG in firstGSuite:
                for elSG in secondGSuite:
                    if elFG['genome'] == elSG['genome']:
                        targetTrackGenome=elFG['genome']
                        resultPartList3=[]
                        for targetTrackDetailFolder1 in elFG['dataFolderValue0']:
                            resultPartList2=[]
                            for targetTrackDetail in targetTrackDetailFolder1['dataFolderValue1']:
                                resultPartList1=[]
                                for el in elSG['dataFolderValue0']:
                                    result = GalaxyInterface.runManual([targetTrackDetail['trackPath'], el['trackPath']],
                                                           analysisDef, regSpec, binSpec,
                                                           elFG['genome'].split('-')[0], galaxyFn,
                                                           printRunDescription=False,
                                                           printResults=False)
                                    resultPartList1.append({'refTrackName': el['trackName'].replace(targetTrackGenome,''), 'data':  processResult(result.getGlobalResult())})
                                resultPartList2.append({'folderName2': targetTrackDetail['folderName2'], 'targetTrackName' : targetTrackDetail['trackName'], 'dataFolderValue2': resultPartList1})
                            resultPartList3.append({'folderName1': targetTrackDetailFolder1['folderName1'], 'dataFolderValue1': resultPartList2})
                        results.append({'genome': targetTrackGenome, 'dataFolderValue0': resultPartList3})
        else:
            from quick.statistic.NumT2SegsTouchedByT1SegsStat import NumT2SegsTouchedByT1SegsStat
            results=[]
            for elFG in firstGSuite:
                for elSG in secondGSuite:
                    if elFG['genome'] == elSG['genome']:
                        if choices.statistic == 'Number of touched segments':
                            analysisSpec = AnalysisSpec(NumT2SegsTouchedByT1SegsStat)
                        #analysisBins = UserBinSource('*', '10m', genome=elFG['genome'].split('-')[0])
                        analysisBins = GlobalBinSource(elFG['genome'].split('-')[0])
                        targetTrackGenome=elFG['genome']
                        resultPartList3=[]
                        for targetTrackDetailFolder1 in elFG['dataFolderValue0']:
                            resultPartList2=[]
                            for targetTrackDetail in targetTrackDetailFolder1['dataFolderValue1']:
                                resultPartList1=[]
                                for el in elSG['dataFolderValue0']:
                                    res = doAnalysis(analysisSpec, analysisBins, [PlainTrack(targetTrackDetail['trackPath']), PlainTrack(el['trackPath'])])
                                    resultDict = res.getGlobalResult()
                                    resultPartList1.append({'refTrackName': el['trackName'].replace(targetTrackGenome,''), 'data':  [resultDict['Result']]})
                                resultPartList2.append({'folderName2': targetTrackDetail['folderName2'], 'targetTrackName' : targetTrackDetail['trackName'], 'dataFolderValue2': resultPartList1})
                            resultPartList3.append({'folderName1': targetTrackDetailFolder1['folderName1'], 'dataFolderValue1': resultPartList2})
                        results.append({'genome': targetTrackGenome, 'dataFolderValue0': resultPartList3})
        if choices.type == 'basic':        
            stat = choices.statistic
            #statIndex = STAT_LIST_INDEX[stat]
            statIndex = ScreenTwoTrackCollectionsAgainstEachOther2LevelDepth.STAT_LIST_INDEX
            statIndex = statIndex.index(stat)
        else:
            stat= '0'
            statIndex = 0

        
        
        htmlCore = HtmlCore()
        htmlCore.begin()
        
        htmlCore.line("""
                      <style type="text/css">
                        .hidden {
                             display: none;
                        {
                        .visible {
                             display: block;
                        }
                      </style>
                   """)        
        
        
        folderValue0Unique=[]
        folderValue1Unique=[]
        folderValue2Unique=[]
        targetTrackFeatureTitles=[]
        for dataDetail0 in results:
            if dataDetail0['genome'] not in folderValue0Unique:
                folderValue0Unique.append(dataDetail0['genome'])
            for dataDetail1 in dataDetail0['dataFolderValue0']:
                if dataDetail1['folderName1'] not in folderValue1Unique:
                    folderValue1Unique.append(dataDetail1['folderName1'])
                for dataDetail2 in dataDetail1['dataFolderValue1']:
                    if dataDetail2['folderName2'] not in folderValue2Unique:
                        folderValue2Unique.append(dataDetail2['folderName2'])
                    for dataDetail3 in dataDetail2['dataFolderValue2']:
                        if dataDetail3['refTrackName'] not in targetTrackFeatureTitles:
                            targetTrackFeatureTitles.append(dataDetail3['refTrackName'])
        
        #print 'folderValue0Unique=' + str(folderValue0Unique)
        #print 'folderValue1Unique=' + str(folderValue1Unique)
        #print 'folderValue2Unique=' + str(folderValue2Unique)
        #print 'targetTrackFeatureTitles=' + str(targetTrackFeatureTitles)
        
        
        
        targetTrackNameList=targetTrackFeatureTitles

        
        htmlCore.line('Statistic: ' + stat)
        htmlCore.line(addJS3levelOptionList(folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, targetTrackNameList, folderValue0Unique))
        
        
        htmlCore.divBegin('results')
        
        #htmlCore.paragraph(preporcessResults(results, folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, statIndex))
        htmlCore.paragraph(preporcessResults3(results, folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique, statIndex))
        htmlCore.divEnd()   
            
        htmlCore.hideToggle(styleClass='debug')
        htmlCore.end()
       
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
    def isPublic():
        '''
        Specifies whether the tool is accessible to all users. If False, the
        tool is only accessible to a restricted set of users as defined in
        LocalOSConfig.py.
        '''
        return True

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
    #    name. The base directory is STATIC_PATH as defined by Config.py. The
    #    full path is created from the base directory followed by the id.
    #    '''
    #    return None
    #
    #@staticmethod
    #def getFullExampleURL():
    #    return None
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
    #def isDebugMode():
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
        return 'customhtml'



'''
#temp for 3D
from quick.application.ExternalTrackManager import ExternalTrackManager
with open(ExternalTrackManager.extractFnFromGalaxyTN(choices.gSuiteFirst.split(':')), 'r') as f:
    data=[x.strip('\n') for x in f.readlines()]
f.closed

ll=[]
for i in data:
    new = [x for x in i.split()]
    ll.append(new)


targetTracksDict = []
d=[]
i=0
for l in ll:
    if i>4:
        if i== 5:
            fv1=l[2]
        if fv1 != l[2]:
            dd={'folderName1':fv1, 'data': d}
            targetTracksDict.append(dd)
            fv1 = l[2]
            dd={}
            d=[]
        path = l[0].split('/')
        path.pop(0)
        d.append({'folderName2': l[1], 'trackName': 'file.bed', 'trackPath' : path})
            
        if len(ll)-1 == i:
            dd={'folderName1':fv1, 'data': d}
            targetTracksDict.append(dd)
    i+=1
 
refTrackNames, refTrackCollection, refTrackCollectionGenome = getGSuiteDataFromGalaxyTN(choices.gSuiteSecond)
refTracksDict = OrderedDict(zip(refTrackNames, refTrackCollection))

targetTrackGenome=refTrackCollectionGenome

regSpec, binSpec = UserBinSelector.getRegsAndBinsSpec(choices)

if choices.intraOverlap == ScreenTwoTrackCollectionsAgainstEachOther2LevelDepth.MERGE_INTRA_OVERLAPS:
    analysisDef = 'dummy -> RawOverlapStat'
else:
    analysisDef = 'dummy [withOverlaps=yes] -> RawOverlapAllowSingleTrackOverlapsStat'

folderName1 =[]
results=[]
for targetTrackDetailFolder1 in targetTracksDict: #2
    resultPartList2=[]
    for targetTrackDetail in targetTrackDetailFolder1['data']:
        resultPartList1=[]
        for refTrackName, refTrack in refTracksDict.iteritems():
            result = GalaxyInterface.runManual([targetTrackDetail['trackPath'], refTrack],
                                               analysisDef, regSpec, binSpec,
                                               targetTrackGenome, galaxyFn,
                                               printRunDescription=False,
                                               printResults=False)
            resultPartList1.append({'refTrackName': refTrackName, 'data':  processResult(result.getGlobalResult())})
        resultPartList2.append({'folderName2': targetTrackDetail['folderName2'], 'targetTrackName' : targetTrackDetail['trackName'], 'dataFolderValue2': resultPartList1})    
    results.append({'folderName1': targetTrackDetailFolder1['folderName1'], 'dataFolderValue1': resultPartList2})
'''


'''
folderValue1Unique=[]
folderValue2Unique=[]
targetTrackFeatureTitles=[]
targetTrackNameList=[]
for dataDetail1 in results:
    if dataDetail1['folderName1'] not in folderValue1Unique:
        folderValue1Unique.append(dataDetail1['folderName1'])
    for dataDetail2 in dataDetail1['dataFolderValue1']:
        if dataDetail2['folderName2'] not in folderValue2Unique:
            folderValue2Unique.append(dataDetail2['folderName2'])
        if dataDetail2['targetTrackName'] not in targetTrackNameList:
            targetTrackNameList.append(dataDetail2['targetTrackName'])
        for dataDetail3 in dataDetail2['dataFolderValue2']:
            if dataDetail3['refTrackName'] not in targetTrackFeatureTitles:
                targetTrackFeatureTitles.append(dataDetail3['refTrackName'])
'''
        
'''
        results=[{
         'genome':'AA',
         'dataFolderValue0':
         [{
          'dataFolderValue1': 
          [
           {'targetTrackName': 'file.bed', 
            'folderName2': 'block_end', 
            'dataFolderValue2': [{'refTrackName': 'interspersed_repeats (B_cereus_MiSeq)', 
                                  'data': [7, 843, 283271, 0.00011515947256573169, 12.787334599418866, 0.7034400948991696, 0.0020934017248500554]},
                                 #{'refTrackName': 'low_complexity_regions (B_cereus_MiSeq)', 
                                 # 'data': [8, 843, 77212, 1.8112424002509598e-05, 7.9809486340361344, 0.11506524317912219, 0.001256281407035176]},
                                 {'refTrackName': 'tandem_repeats (B_cereus_MiSeq)', 
                                  'data': [9, 843, 35908, 6.0777387254240703e-05, 58.477240439552183, 0.38908659549228947, 0.009134454717611675]}
                                 ]
            }, 
           {'targetTrackName': 'file.bed', 
            'folderName2': 'deletion', 
            'dataFolderValue2': [{'refTrackName': 'interspersed_repeats (B_cereus_MiSeq)', 
                                  'data': [10, 3842, 283271, 8.5641361553942115e-05, 2.0865756718736446, 0.11478396668401875, 0.0015568130871144593]}, 
                                 {'refTrackName': 'low_complexity_regions (B_cereus_MiSeq)', 
                                  'data': [11, 3842, 77212, 2.894253319988647e-05, 2.798238281356713, 0.04034357105674128, 0.0020074599803139408]}, 
                                 {'refTrackName': 'tandem_repeats (B_cereus_MiSeq)', 
                                  'data': [12, 3842, 35908, 6.9856935959904717e-05, 14.747710051083756, 0.09812597605413848, 0.010499053135791468]}
                                 ]}], 
          'folderName1': 'abyss'}, 
          {
          'dataFolderValue1': 
          [
            #{'targetTrackName': 'file.bed', 
            #'folderName2': 'block_end', 
            #'dataFolderValue2': [{'refTrackName': 'interspersed_repeats (B_cereus_MiSeq)', 
            #                      'data': [0, 81, 283271, 1.2622876419515278e-05, 14.587512738641282, 0.8024691358024691, 0.00022946224640009037]}, 
            #                     {'refTrackName': 'low_complexity_regions (B_cereus_MiSeq)', 
            #                      'data': [1, 81, 77212, 0.0, 0.0, 0.0, 0.0]}, 
            #                     {'refTrackName': 'tandem_repeats (B_cereus_MiSeq)', 
            #                      'data': [2, 81, 35908, 0.0, 0.0, 0.0, 0.0]}]}, 
           {'targetTrackName': 'file.bed', 
            'folderName2': 'deletion', 
            'dataFolderValue2': [{'refTrackName': 'interspersed_repeats (B_cereus_MiSeq)', 
                                  'data': [3, 3056, 283271, 3.1071695801883762e-05, 0.9517426756584324, 0.05235602094240838, 0.0005648301449848378]}, 
                                 {'refTrackName': 'low_complexity_regions (B_cereus_MiSeq)', 
                                  'data': [4, 3056, 77212, 6.9088627638438673e-06, 0.83976685662891026, 0.012107329842931938, 0.00047920012433300526]}, 
                                 {'refTrackName': 'tandem_repeats (B_cereus_MiSeq)', 
                                  'data': [5, 3056, 35908, 2.6497458467550064e-05, 7.0327193782598574, 0.046793193717277484, 0.003982399465300212]}]}], 
          'folderName1': 'cabog'
          }]},
         {
         'genome':'BB',
         'dataFolderValue0':
         [{
          'dataFolderValue1': 
          [
           {'targetTrackName': 'file.bed', 
            'folderName2': 'block_end', 
            'dataFolderValue2': [{'refTrackName': 'interspersed_repeats (B_cereus_MiSeq)', 
                                  'data': [19, 843, 283271, 0.00011515947256573169, 12.787334599418866, 0.7034400948991696, 0.0020934017248500554]}, 
                                 {'refTrackName': 'low_complexity_regions (B_cereus_MiSeq)', 
                                  'data': [20, 843, 77212, 1.8112424002509598e-05, 7.9809486340361344, 0.11506524317912219, 0.001256281407035176]}, 
                                 {'refTrackName': 'tandem_repeats (B_cereus_MiSeq)', 
                                  'data': [21, 843, 35908, 6.0777387254240703e-05, 58.477240439552183, 0.38908659549228947, 0.009134454717611675]}
                                 ]
            }, 
           {'targetTrackName': 'file.bed', 
            'folderName2': 'deletion', 
            'dataFolderValue2': [{'refTrackName': 'interspersed_repeats (B_cereus_MiSeq)', 
                                  'data': [22, 3842, 283271, 8.5641361553942115e-05, 2.0865756718736446, 0.11478396668401875, 0.0015568130871144593]}, 
                                 {'refTrackName': 'low_complexity_regions (B_cereus_MiSeq)', 
                                  'data': [23, 3842, 77212, 2.894253319988647e-05, 2.798238281356713, 0.04034357105674128, 0.0020074599803139408]}, 
                                 {'refTrackName': 'tandem_repeats (B_cereus_MiSeq)', 
                                  'data': [24, 3842, 35908, 6.9856935959904717e-05, 14.747710051083756, 0.09812597605413848, 0.010499053135791468]}
                                 ]}], 
          'folderName1': 'abyss'}, 
          {
          'dataFolderValue1': 
          [{'targetTrackName': 'file.bed', 
            'folderName2': 'block_end', 
            'dataFolderValue2': [{'refTrackName': 'interspersed_repeats (B_cereus_MiSeq)', 
                                  'data': [13, 81, 283271, 1.2622876419515278e-05, 14.587512738641282, 0.8024691358024691, 0.00022946224640009037]}, 
                                 {'refTrackName': 'low_complexity_regions (B_cereus_MiSeq)', 
                                  'data': [14, 81, 77212, 0.0, 0.0, 0.0, 0.0]}, 
                                 {'refTrackName': 'tandem_repeats (B_cereus_MiSeq)', 
                                  'data': [15, 81, 35908, 0.0, 0.0, 0.0, 0.0]}]}, 
           {'targetTrackName': 'file.bed', 
            'folderName2': 'deletion', 
            'dataFolderValue2': [{'refTrackName': 'interspersed_repeats (B_cereus_MiSeq)', 
                                  'data': [16, 3056, 283271, 3.1071695801883762e-05, 0.9517426756584324, 0.05235602094240838, 0.0005648301449848378]}, 
                                 {'refTrackName': 'low_complexity_regions (B_cereus_MiSeq)', 
                                  'data': [17, 3056, 77212, 6.9088627638438673e-06, 0.83976685662891026, 0.012107329842931938, 0.00047920012433300526]}, 
                                 {'refTrackName': 'tandem_repeats (B_cereus_MiSeq)', 
                                  'data': [18, 3056, 35908, 2.6497458467550064e-05, 7.0327193782598574, 0.046793193717277484, 0.003982399465300212]}]}], 
          'folderName1': 'cabog'
          }]}
         ]
'''


#folderValue0Unique=['AA', 'BB']#genome  
#folderValue1Unique=['abyss', 'cabog']          
#folderValue2Unique=['block_end', 'deletion'] 
#targetTrackFeatureTitles=['interspersed_repeats (B_cereus_MiSeq)', 
#                      'low_complexity_regions (B_cereus_MiSeq)', 
#                  'tandem_repeats (B_cereus_MiSeq)']
        
#htmlCore.line(showCube(folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, targetTrackNameList))
#htmlCore.line(showExCube(folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, targetTrackNameList))

#htmlCore.line(addJS2levelOptionList(folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, targetTrackNameList))
