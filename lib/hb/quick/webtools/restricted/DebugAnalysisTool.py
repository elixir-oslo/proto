import math
from inspect import getargspec
from os import sep

import third_party.safeshelve as safeshelve
from config.Config import DATA_FILES_PATH
from gold.application.StatRunner import StatJob
from gold.statistic.AllStatistics import STAT_CLASS_DICT
from gold.statistic.MagicStatFactory import MagicStatFactory
from quick.application.ProcTrackOptions import ProcTrackOptions
from quick.application.UserBinSource import UserBinSource
from quick.webtools.GeneralGuiTool import GeneralGuiTool


#This is a template prototyping GUI that comes together with a corresponding web page.
#

class DebugAnalysisTool(GeneralGuiTool):
    _extraParams = []
    SHELVE_FN = DATA_FILES_PATH + sep + 'DebugTool.shelve'
    STD_PREFIX_TN = ['Sample data', 'Track types']
    NO_TRACK_SHORTNAME = '-- No track --'
    _cacheDict = {}
    @staticmethod
    def getToolName():
        return "Debug statistic"

    @staticmethod
    def getInputBoxNames():
        "Returns a list of names for input boxes, implicitly also the number of input boxes to display on page. Each such box will call function getOptionsBoxK, where K is in the range of 1 to the number of boxes"
        return [('Select Statistic to debug','Statistic'),('Select genome','Genome'),('Show Track1 simplified','YesNoT1'),('Track1','Track1'),('Show Track2 simplified','YesNoT2'),('Track2','Track2'),('Extra parameter','S7'),('Value for parameter','S8'),('Extra parameter','S9'),('Value for parameter','S10'),('Extra parameter','S11'),('Value for parameter','S12'),('Extra parameter','S13'),('Value for parameter','S14'),('Extra parameter','S15'),('Value for parameter','S16'),('Extra parameter','S17'),('Value for parameter','S18'),('Extra parameter','S19'),('Value for parameter','S20'),('Extra parameter','S21'),('Value for parameter','S22'),('Extra parameter','S23'),('Value for parameter','S24'),('Extra parameter','S25'),('Value for parameter','S26')]# + UserBinSelector.getUserBinInputBoxNames()

    #@staticmethod
    #def getInputBoxOrder():
    #    return [1,2,4,3,6,5,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27]

    @classmethod
    def updateCacheDict(cls, stat):
        DebugInfoShelve = safeshelve.open(cls.SHELVE_FN, 'c')
        if stat in DebugInfoShelve and type(DebugInfoShelve[stat]).__name__=='dict':
            cls._cacheDict = DebugInfoShelve[stat]
        DebugInfoShelve.close()


    @staticmethod
    def getOptionsBoxStatistic():
        return sorted(STAT_CLASS_DICT.keys())

    @staticmethod
    def getOptionsBoxGenome(prevChoices):
        return '__genome__'


    @classmethod
    def getOptionsBoxYesNoT1(cls, prevChoices):
        return ['yes', 'no']


    @classmethod
    def getOptionsBoxTrack1(cls, prevChoices):
        if prevChoices[0]:
            cls.updateCacheDict(prevChoices[0])

        if prevChoices[2] =='yes' :
            genome = prevChoices[1]
            prefixTN = cls.STD_PREFIX_TN
            trackList = ProcTrackOptions.getSubtypes(genome, prefixTN, True)
            if cls._cacheDict.get('track1') in trackList:
                trackList.remove(cls._cacheDict.get('track1'))
                trackList.insert(0, cls._cacheDict.get('track1'))
            return [cls.NO_TRACK_SHORTNAME] + trackList
        else:
            return '__track__','history'

    @classmethod
    def getOptionsBoxYesNoT2(cls, prevChoices):
        return ['yes', 'no']


    @classmethod
    def getOptionsBoxTrack2(cls, prevChoices):
        if prevChoices[4]=='yes' :

            genome = prevChoices[1]
            prefixTN = cls.STD_PREFIX_TN
            trackList = ProcTrackOptions.getSubtypes(genome, prefixTN, True)
            if cls._cacheDict.get('track2') in trackList:
                trackList.remove(cls._cacheDict.get('track2'))
                trackList.insert(0, cls._cacheDict.get('track2'))
            return [cls.NO_TRACK_SHORTNAME] + trackList
        else:
            return '__track__','history'
        #return ['']


    @classmethod
    def _setExtraParams(cls, prevChoices):

        methodObj = getattr( MagicStatFactory._getClass(prevChoices[0], 'Unsplittable')  ,   '__init__')
        methodParams = ['Region','BinSpec']+[v for v in getargspec(methodObj).args if not v in ['self', 'track', 'track2', 'region']]
        defaultVals = ['','']+(list(getargspec(methodObj).defaults)  if  getargspec(methodObj).defaults and len(methodParams)>0   else [])

        lenDifference = len(methodParams)-len(defaultVals)
        defaultVals = ['']*(lenDifference)+ defaultVals if lenDifference>=0 else defaultVals[-lenDifference:]

        cls._extraParams = [value + ' (default: %s)' % defaultVals[index] for index, value in enumerate(methodParams)]


    FIRST_EXTRA_PARAM_BOX_NUMBER = 6

    @classmethod
    def _getColumnList(cls, prevChoices, index):
        if cls._extraParams == []:
            cls._setExtraParams(prevChoices)

        paramNum = int(math.floor((index - cls.FIRST_EXTRA_PARAM_BOX_NUMBER) / 2))

        if len(cls._extraParams) > paramNum:
            if index % 2 == 1:
                return '' if not cls._cacheDict.get(index) else cls._cacheDict.get(index)
            else:
                return[cls._extraParams[paramNum]]




    @classmethod
    def getOptionsBoxS7(cls, prevChoices):
        return cls._getColumnList(prevChoices, 6)

    @classmethod
    def getOptionsBoxS8(cls, prevChoices):
        return cls._getColumnList(prevChoices, 7)

    @classmethod
    def getOptionsBoxS9(cls, prevChoices):
        return cls._getColumnList(prevChoices, 8)

    @classmethod
    def getOptionsBoxS10(cls, prevChoices):
        return cls._getColumnList(prevChoices, 9)

    @classmethod
    def getOptionsBoxS11(cls, prevChoices):
        return cls._getColumnList(prevChoices, 10)
    @classmethod
    def getOptionsBoxS12(cls, prevChoices):
        return cls._getColumnList(prevChoices, 11)

    @classmethod
    def getOptionsBoxS13(cls, prevChoices):
        return cls._getColumnList(prevChoices, 12)

    @classmethod
    def getOptionsBoxS14(cls, prevChoices):
        return cls._getColumnList(prevChoices, 13)
    @classmethod
    def getOptionsBoxS15(cls, prevChoices):
        return cls._getColumnList(prevChoices, 14)

    @classmethod
    def getOptionsBoxS16(cls, prevChoices):
        return cls._getColumnList(prevChoices, 15)

    @classmethod
    def getOptionsBoxS17(cls, prevChoices):
        return cls._getColumnList(prevChoices, 16)

    @classmethod
    def getOptionsBoxS18(cls, prevChoices):
        return cls._getColumnList(prevChoices, 17)

    @classmethod
    def getOptionsBoxS19(cls, prevChoices):
        return cls._getColumnList(prevChoices, 18)

    @classmethod
    def getOptionsBoxS20(cls, prevChoices):
        return cls._getColumnList(prevChoices, 19)

    @classmethod
    def getOptionsBoxS21(cls, prevChoices):
        return cls._getColumnList(prevChoices, 20)

    @classmethod
    def getOptionsBoxS22(cls, prevChoices):
        return cls._getColumnList(prevChoices, 21)

    @classmethod
    def getOptionsBoxS23(cls, prevChoices):
        return cls._getColumnList(prevChoices, 22)

    @classmethod
    def getOptionsBoxS24(cls, prevChoices):
        return cls._getColumnList(prevChoices, 23)

    @classmethod
    def getOptionsBoxS25(cls, prevChoices):
        return cls._getColumnList(prevChoices, 24)

    @classmethod
    def getOptionsBoxS26(cls, prevChoices):
        return cls._getColumnList(prevChoices, 25)



    #@staticmethod
    #def getOptionsBox5(prevChoices):
    #    return ['']

    #@staticmethod
    #def getDemoSelections():
    #    return ['testChoice1','..']
        
    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        shelveDict = {'track1':choices[3] if choices[3]!=cls.NO_TRACK_SHORTNAME else None}
        shelveDict['track2'] = choices[5] if choices[5]!=cls.NO_TRACK_SHORTNAME else None
        print len(choices)
        print cls._extraParams
        for i in range(len(cls._extraParams)):
            index = i*2+cls.FIRST_EXTRA_PARAM_BOX_NUMBER+1
            shelveDict[index] = choices[index].strip()

        DebugInfoShelve = safeshelve.open(cls.SHELVE_FN)
        DebugInfoShelve[choices[0]] = shelveDict
        DebugInfoShelve.close()


        try:

            from gold.application.LogSetup import setupDebugModeAndLogging
            setupDebugModeAndLogging()

            print 'Getting Unsplittable statClass'
            statClassName = choices[0]
            #statClass = STAT_CLASS_DICT[statClassName]
            #try:



            print 'Preparing arguments to init'
            unsplittableStatClass = MagicStatFactory._getClass(statClassName, 'Unsplittable')
            genome = choices[1]

            from gold.track.Track import PlainTrack
            prefixTN1 = cls.STD_PREFIX_TN if choices[2] == 'yes' else []
            tn1 = prefixTN1 + choices[3].split(':')
            track1 = PlainTrack(tn1) if choices[3]!=cls.NO_TRACK_SHORTNAME else None
            prefixTN2 = cls.STD_PREFIX_TN if choices[4] == 'yes' else []
            tn2 = prefixTN2 + choices[5].split(':')
            track2 = PlainTrack(tn2) if choices[5]!=cls.NO_TRACK_SHORTNAME else None
            from gold.track.GenomeRegion import GenomeRegion
            #region = GenomeRegion(genome, 'chr1',1000,2000)
            #region2 = GenomeRegion(genome, 'chr1',5000,6000)

            kwArgs = {}
            regVal = choices[cls.FIRST_EXTRA_PARAM_BOX_NUMBER+1]
            binSpecVal = choices[cls.FIRST_EXTRA_PARAM_BOX_NUMBER+3]
            ubSource = UserBinSource(regVal, binSpecVal, genome=genome)
            region = list(ubSource)[0]

            if len(cls._extraParams)>3:
                for i in range(len(cls._extraParams)):
                    paramName = choices[i*2+cls.FIRST_EXTRA_PARAM_BOX_NUMBER]
                    param = paramName[:paramName.find('(')].strip()
                    val = choices[i*2+cls.FIRST_EXTRA_PARAM_BOX_NUMBER+1].strip()
                    if val !='':
                        kwArgs[param] = val
                        shelveDict[i*2+cls.FIRST_EXTRA_PARAM_BOX_NUMBER+1] = val


            print 'Calling __init__'
            #
            statObj = unsplittableStatClass(region, track1, track2, **kwArgs)

            print 'Calling createChildren'
            statObj.createChildren()

            print 'Calling getResult'
            statObj.getResult()

            #except:
            #    raise

            #print 'Preparing arguments to init'
            #genome = 'hg18'
            #prefixTN = ['DNA structure'] if choices[2] == 'yes' else []
            #from gold.track.Track import PlainTrack
            #tn1 = prefixTN + choices[3].split(':')
            #track1 = PlainTrack(tn1)
            #tn2 = prefixTN + choices[5].split(':')
            #track2 = PlainTrack(tn2)
            #from gold.track.GenomeRegion import GenomeRegion
            ##region = GenomeRegion(genome, 'chr1',1000,2000)
            ##region2 = GenomeRegion(genome, 'chr1',5000,6000)
            #
            #kwArgs = {}
            #regVal = choices[cls.FIRST_EXTRA_PARAM_BOX_NUMBER+1]
            #binSpecVal = choices[cls.FIRST_EXTRA_PARAM_BOX_NUMBER+3]
            #ubSource = UserBinSource(regVal, binSpecVal, genome=choices[1])
            #region = list(UserBinSource)[0]
            #
            #if len(cls._extraParams)>2:
            #    for i in range(2,len(cls._extraParams)):
            #        paramName = choices[i*2+cls.FIRST_EXTRA_PARAM_BOX_NUMBER]
            #        param = paramName[:paramName.find('(')].strip()
            #        val = choices[i*2+cls.FIRST_EXTRA_PARAM_BOX_NUMBER+1].strip()
            #        if val !='':
            #            kwArgs[param] = val
            #            shelveDict[i*2+cls.FIRST_EXTRA_PARAM_BOX_NUMBER+1] = val
            #
            #
            ##extraParams += [v.strip() for v in choices.kwArgs.split(',')] if choices.kwArgs.strip() != '' else []
            ##args = [region, track1, track2]
            #
            #print 'Calling __init__'
            ##
            #statObj = unsplittableStatClass(region, track1, track2, **kwArgs)
            #
            #print 'Calling createChildren'
            #statObj.createChildren()
            #
            #print 'Calling getResult'
            #statObj.getResult()

            print 'Running StatJob'
            magicStatClass = STAT_CLASS_DICT[statClassName]
            #res = StatJob([region,region2],track1,track2,magicStatClass,**kwArgs).run()
            res = StatJob(ubSource,track1,track2,magicStatClass,**kwArgs).run()
            from quick.application.GalaxyInterface import GalaxyInterface
            GalaxyInterface._viewResults([res],galaxyFn)

        except Exception, e:
            print 'Error: ',e
            raise

    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not valid,
        an error text explaining the problem should be returned. The GUI then shows this text
        to the user (if not empty) and greys out the execute button (even if the text is empty).
        If all parameters are valid, the method should return None, which enables the execute button.
        '''
        return None

    # @classmethod
    # def getTests(cls):
    #     choicesFormType = ['str', 'genome', 'str', 'track', 'str', 'track'] + ['str']*20
    #     testRunList = ["$Tool[hb_debug_analysis_tool]('RemoveOverlappingIntraTrackSegmentsStat'|'hg18'|'yes'|'Valued segments (category)'|'yes'|'-- No track --'|'Region (default: )'|'*'|'BinSpec (default: None)'|'*'|None|None|None|None|None|None|None|None|None|None|None|None|None|None|None|None|'Chromosomes'|'*'|None|None|None)"]
    #     return cls.formatTests(choicesFormType, testRunList)

    #@staticmethod
    #def isPublic():
    #    return False
    #
    #@staticmethod
    #def isRedirectTool():
    #    return False
    #
    #@staticmethod
    #def isHistoryTool():
    #    return True
    #
    #@staticmethod
    #def isDynamic():
    #    return True
    #
    @staticmethod
    def getResetBoxes():
        return [1]
    #
    #@staticmethod
    #def getToolDescription():
    #    return ''
    #
    #@staticmethod
    #def getToolIllustration():
    #    return None
    #
    #@staticmethod
    #def isDebugMode():
    #    return True
    #
    #@staticmethod
    #def getOutputFormat():
    #   '''The format of the history element with the output of the tool.
    #   Note that html output shows print statements, but that text-based output
    #   (e.g. bed) only shows text written to the galaxyFn file.
    #   '''
    #    return 'html'
    #
