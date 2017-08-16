import ast
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.application.ExternalTrackManager import ExternalTrackManager
import math
#This is a template prototyping GUI that comes together with a corresponding web page.
#
from functools import partial
from urllib import unquote
from gold.origdata.BedGraphComposer import BedGraphComposer
from gold.origdata.TrackGenomeElementSource import TrackGenomeElementSource
from gold.track.GenomeRegion import GenomeRegion
from quick.util.GenomeInfo import GenomeInfo

class CreateCategoricalTrackTool(GeneralGuiTool):
    NUM_CATEGORY_FIELDS = 215

    @staticmethod
    def getToolName():
        return "Merge multiple BED files into single categorical track"

    @classmethod
    def getInputBoxNames(cls):
        "Returns a list of names for input boxes, implicitly also the number of input boxes to display on page. Each such box will call function getOptionsBoxK, where K is in the range of 1 to the number of boxes"
        return ['Select genome build: ', 'Select history items: ', 'Hidden'] + \
                ['History item selected: ', 'Type in category: '] * cls.NUM_CATEGORY_FIELDS

    @staticmethod
    def getOptionsBox1():
        return '__genome__'

    @staticmethod
    def getOptionsBox2(prevChoices):
        return '__multihistory__','bed','point.bed','category.bed','valued.bed','bedgraph'


    @staticmethod
    def getOptionsBox3(prevChoices):
        prevDict = ast.literal_eval(prevChoices[-1]) if prevChoices[-1] else {}
        index2name = prevDict

        selectedHists = [ExternalTrackManager.extractNameFromHistoryTN(unquote(val).split(':')) \
                         for id,val in prevChoices[1].iteritems() if val]
        newlySelected = list(set(selectedHists) - set(prevDict.values()))
        oldCount = len(index2name)
        for i, name in enumerate(newlySelected):
            index2name[i + oldCount] = name

        newlyRemovedList = list(set(prevDict.values()) - set(selectedHists))
        for name in newlyRemovedList:
            for idx, val in index2name.iteritems():
                if val == name and idx >= 0:
                    index2name[idx] = None

        return '__hidden__', repr(index2name)

    @classmethod
    def _getSelectedValue(cls, prevChoices, index):
        index2name = ast.literal_eval(prevChoices[2])
        return index2name.get(index)

    @classmethod
    def _getCategoryValueField(cls, prevChoices, index):
        return cls._getSelectedValue(prevChoices, index)

    @classmethod
    def _getHistoryNameField(cls, prevChoices, index):
        val = cls._getSelectedValue(prevChoices, index)
        if val:
            return [[val]]

    @classmethod
    def setupCategoryFields(cls):
        for i in xrange(cls.NUM_CATEGORY_FIELDS):
            setattr(cls, 'getOptionsBox%i' % (2*i+4), partial(cls._getHistoryNameField, index=i))
            setattr(cls, 'getOptionsBox%i' % (2*i+5), partial(cls._getCategoryValueField, index=i))

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        genome = choices[0]
        outputFile=open(galaxyFn,"w")

        index2name = ast.literal_eval(choices[2])
        name2index = dict([(name, idx) for idx,name in index2name.iteritems()])
        galaxyTnList = [tn.split(':') for tn in choices[1].values() if tn]
        #print>>outputFile,'\n'.join([str(i)+':\t'+str(v) for i, v in enumerate(choices)])
        #trackIndexStart = cls.NUM_CATEGORY_FIELDS*2 + 2
        for ind, galaxyTn in enumerate(galaxyTnList):
            name = ExternalTrackManager.extractNameFromHistoryTN(galaxyTn)
            fnSource = ExternalTrackManager.extractFnFromGalaxyTN(galaxyTn)
            category = choices[2*name2index[name]+4]

            for i in open(fnSource,'r'):
                if any(i.startswith(x) for x in ['#', 'track']):
                    continue

                linetab = i.strip().split('\t')
                linetab.insert(3, category)
                if len(linetab)>4:
                    linetab.pop(4)
                print>>outputFile, '\t'.join(linetab)

        outputFile.close()

    @staticmethod
    def validateAndReturnErrors(choices):
        genome = choices[0]
        if genome in [None, '']:
                return 'Please select a genome build'

        if not choices[1] or not any(choices[1].values()):
            return 'Please select one ore more BED files from history'

        galaxyTnList = [v.split(':') for v in choices[1].values() if v]
        for galaxyTN in galaxyTnList:
            errorStr = CreateCategoricalTrackTool._validateFirstLine(galaxyTN, genome, fileStr='BED file')
            if errorStr:
                return errorStr

        catList = []
        for ind, name in ast.literal_eval(choices[2]).iteritems():
            if name is not None:
                index = ind*2 + 4
                if choices[index] == '':
                    return 'All categories must be specified'
                else:
                    if any([x in choices[index] for x in ['\t']]):
                        return 'Tab characters are not allowed in categories: ' + choices[index]
                    catList.append(choices[index])
        return None

    @staticmethod
    def isPublic():
        return True

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
    #@staticmethod
    #def getResetBoxes():
    #    return []
    #
    @staticmethod
    def getToolDescription():
        return '''
This tool combines elements from multiple data sets into a single track, where
each line is denoted with a category that reflects their source. The exact
categories can be changed as needed.'''
    #
    #@staticmethod
    #def getToolIllustration():
    #    return None
    #
    @staticmethod
    def getFullExampleURL():
        return 'u/hb-superuser/p/merge-multiple-bed-files-into-single-categorical-track'

    #@staticmethod
    #def isDebugMode():
    #    return True
    #
    @staticmethod
    def getOutputFormat(inputFormat):
        return 'category.bed'

CreateCategoricalTrackTool.setupCategoryFields()
