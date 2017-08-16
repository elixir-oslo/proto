import ast
from quick.webtools.GeneralGuiTool import GeneralGuiTool
import urllib
from quick.util.CommonFunctions import getGeSource
from collections import OrderedDict

# This is a template prototyping GUI that comes together with a corresponding
# web page.

class ExtractIndividualTracksFromCategoryTrack(GeneralGuiTool):


    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Extract individual tracks from category-track"
    histChoice = 'From history'
    trackChoice = 'From track repository'

    @staticmethod
    def getInputBoxNames():

        return ['select genome','Select source for category-track', 'select history dataset', 'select track', 'hidden', 'use all or select categories?', 'select categories' ,'make seperate file for each category?'] #Alternatively: [ ('box1','1'), ('box2','2') ]

    @staticmethod
    def getOptionsBox1():
        return  '__genome__'

    @classmethod
    def getOptionsBox2(cls, prevChoices):
        return  ['-----  Select  -----', cls.histChoice, cls.trackChoice]

    @classmethod
    def getOptionsBox3(cls, prevChoices):
        if prevChoices[1] == cls.histChoice:
            return  '__history__', 'bed', 'category.bed', 'gtrack'

    @classmethod
    def getOptionsBox4(cls, prevChoices):
        if prevChoices[1] == cls.trackChoice:
            return  '__track__'

    @classmethod
    def getOptionsBox5(cls, prevChoices):
        if prevChoices[1] in [cls.trackChoice, cls.histChoice]:
            genome = prevChoices[0]
            if prevChoices[-1]:
                return  ('__hidden__', prevChoices[-1])
            if prevChoices[2] and prevChoices[2].split(':')[1] in ['category.bed','bed','gtrack']:
                track = prevChoices[2].split()
                geSource = getGeSource(prevChoices[2])
                tmp = set()
                for ge in geSource:
                    tmp.add(ge.val)
                return ('__hidden__', urllib.quote(repr(tmp)))

    @classmethod
    def getOptionsBox6(cls, prevChoices):
        if prevChoices[1] in [cls.trackChoice, cls.histChoice]:
            return  ['-----  Select  -----','get all categories','select categories']


    @classmethod
    def getOptionsBox7(cls, prevChoices):
        if prevChoices[-2] == 'select categories':
            return OrderedDict([(v,False) for v in ast.literal_eval(urllib.unquote(prevChoices[4]))])

    @classmethod
    def getOptionsBox8(cls, prevChoices):
        if prevChoices[5] == 'select categories':
            return ['Yes', 'No']


    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        utFil = open(galaxyFn, 'w')
        genome = choices[0]
        track = choices[2].split(':') if choices[1] == cls.histChoice else choices[3].split(':')
        categories = sorted(ast.literal_eval(urllib.unquote(choices[4]))) if choices[5] == 'get all categories' else sorted([k for k,v  in choices[6].items() if v])
        categoryFileDict = dict()
        if choices[5] == 'select categories' and choices[7] == 'Yes':
            for cat in categories:
                categoryFileDict[cat] = open(cls.makeHistElement(galaxyExt='bed', title=cat.replace('_','#')), 'w')
            singleCatFiles = True
        else:
            categoryFileDict = dict([(v,utFil)for v in categories])
            singleCatFiles = False



        geSource = getGeSource(track, genome)
        bedTemplate = '%s\t%i\t%i'
        catBedTemplate = '%s\t%i\t%i\t%s'
        for ge in geSource:
            if ge.val in categories:
                if singleCatFiles:
                     print>>categoryFileDict[ge.val], bedTemplate % (ge.chr, ge.start, ge.end)
                else:
                    print>>categoryFileDict[ge.val], catBedTemplate % (ge.chr, ge.start, ge.end, ge.val)

        for fileObj in set(categoryFileDict.values()):
            fileObj.close()



    @classmethod
    def validateAndReturnErrors(cls, choices):
        if choices[1] not in [cls.histChoice, cls.trackChoice]:
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
        return 'category.bed'
