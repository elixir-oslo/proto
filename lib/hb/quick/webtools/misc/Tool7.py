import os
from cPickle import load
from collections import OrderedDict

import numpy

from gold.result.Results import Results
from proto.hyperbrowser.HtmlCore import HtmlCore
from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.application.SignatureDevianceLogging import returns
from quick.webtools.GeneralGuiTool import GeneralGuiTool


class ResultCollection(OrderedDict):
    def __setitem__(self, entryLabel, resultValue):
            
            
        if not entryLabel in self:
            OrderedDict.__setitem__(self, entryLabel, [])
        self[entryLabel].append(resultValue)

    #def getNumEntries(self):
     #   return len(self.keys())
    
    @returns(str)
    def getTabularStrRepresentation(self, columnLabels):
        
        allRows = [[entryLabel]+self[entryLabel] for entryLabel in self.keys()]

        if columnLabels not in [None,'']:
            allRows = [columnLabels] + allRows

        assert len(set([len(row) for row in allRows]))==1, [len(row) for row in allRows] #All rows must have same number of columns

        return '\n'.join(['\t'.join(['%s'%x for x in row]) for row in allRows])

class LocalResultCollection(ResultCollection):
    def __init__(self, chosenResDictKey, imputeNAs=False):
        self._chosenResDictKey = chosenResDictKey
        ResultCollection.__init__(self)
        self._imputeNAs = imputeNAs

    def __setitem__(self, entryLabel, resultObject):
        assert type(entryLabel) in [str, type(None)] #anyway ignored..
        assert type(resultObject)==Results, (type(resultObject), resultObject)
        if self._chosenResDictKey == 'fdr':
            resultObject.inferAdjustedPvalues()
        for localResultKey in resultObject:
            if self._imputeNAs:
                resultValue = resultObject[localResultKey].get(self._chosenResDictKey)
            else:
                resultValue = resultObject[localResultKey][self._chosenResDictKey]
            ResultCollection.__setitem__(self, localResultKey, resultValue)
        

class GlobalResultCollection(ResultCollection):
    def __init__(self, chosenResDictKey, imputeNAs=False):#, labelSource):
        self._chosenResDictKey = chosenResDictKey
        #self._labelSource = labelSource
        self._imputeNAs = imputeNAs
        ResultCollection.__init__(self)

    def __setitem__(self, entryLabel, resultObject):
        'sets item, not directly to the passed value (which is resultDict), but to a subResult given by self._chosenResDictKey'
        assert isinstance(entryLabel, basestring)
        assert type(resultObject)==Results, (type(resultObject), resultObject)
        try:
            resultValue = resultObject.getGlobalResult()[self._chosenResDictKey]
        except:
            if self._imputeNAs:
                resultValue = numpy.nan
            else:
                raise
        ResultCollection.__setitem__(self, entryLabel, resultValue)
        
    
class Tool7(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Concatenate results of multiple history items (v2)"

    @staticmethod
    def getInputBoxNames():
        "Returns a list of names for input boxes, implicitly also the number of input boxes to display on page. Each such box will call function getOptionsBoxK, where K is in the range of 1 to the number of boxes"
        #can have two syntaxes: either a list of stings or a list of tuples where each tuple has two items(Name of box on webPage, name of getOptionsBox)
        return ['Select Histories','List ResDictKeys','ResDictKey', 'Local or Global','Num columns for line wrapping (leave blank for no wrapping)','Impute missing values', 'Column labels (comma-separated if multiple), or leave blank'] #,'Ensure validity'

    @staticmethod    
    def getOptionsBox1():
        '''Returns a list of options to be displayed in the first options box
        Alternatively, the following have special meaning:
        '__genome__'
        '__track__'
        ('__history__','bed','wig','...')
        '''
        return '__multihistory__',
    

    @staticmethod
    def getOptionsBox2(prevChoices):
        return ['Yes', 'No']
        
    @classmethod    
    def getOptionsBox3(cls, prevChoices):
        if prevChoices[1]=='No':
            return ''
        elif prevChoices[1]=='Yes':
            rsl = cls._getResultsLists(prevChoices[0])[0]
            #return rsl
            return cls._getResDictAndLocalKeys(rsl)[0]
        else:
            raise

    @staticmethod    
    def getOptionsBox4(prevChoices):
        return ['Global results', 'Local results']

    @staticmethod    
    def getOptionsBox5(prevChoices):
        return ''

    @staticmethod    
    def getOptionsBox6(prevChoices):
        return ['No','Yes (put in NA for missing results)']

    @staticmethod    
    def getOptionsBox7(prevChoices):
        return ''

    #@staticmethod    
    #def getOptionsBox5(prevChoices):
    #    return ['Take any errors at time of execute','Check validity as choices are made']

    #@staticmethod
    #def getDemoSelections():
    #    return ['testChoice1','..']
        
    @classmethod    
    def execute(cls, choices, galaxyFn=None, username=''):
        '''Is called when execute-button is pushed by web-user.
        Should print output as HTML to standard out, which will be directed to a results page in Galaxy history.
        If getOutputFormat is anything else than HTML, the output should be written to the file with path galaxyFn.
        If needed, StaticFile can be used to get a path where additional files can be put (e.g. generated image files).
        choices is a list of selections made by web-user in each options box.
        '''
        
        #print 'Executing...'
        HtmlCore().begin()
        core = HtmlCore()
        histChoices = choices[0]
        chosenResDictKey = choices[2] #this box needs to find relevant resDictKeys probably.. or could be a simple string input..
        if choices[3] == 'Global results':
            useGlobal = True
        elif choices[3] == 'Local results':
            useGlobal = False
        else:
            raise
        
        #lineWrapping = int(choices[4]) if choices[4] != '' else None
        if choices[5] == 'No':
            imputeNAs = False
        elif choices[5] == 'Yes (put in NA for missing results)':
            imputeNAs = True
        else:
            raise
        
        
        resultsLists, historyNames = cls._getResultsLists(histChoices)
        resDictKeys, localKeys  = cls._getResDictAndLocalKeys(resultsLists, imputeNAs)

        if choices[6]=='historyNames':
            columnLabels = ['RowHeader']
            for histName,resultList in zip(historyNames,resultsLists):
                columnLabels += [histName + '-%05i' % i for i in range(len(resultList))]
                    
                
            
        else:
            columnLabels = choices[6].split('|') if choices[6]!='' else None

        if useGlobal:
            resColl = GlobalResultCollection(chosenResDictKey, imputeNAs)
        else:
            resColl = LocalResultCollection(chosenResDictKey, imputeNAs)
        
        labelSource='firstTrack'
        
        
        for i,resultList in enumerate(resultsLists):
            for j,oneResult in enumerate(resultList):
                if labelSource == 'firstTrack':
                    label = oneResult.getTrackNames()[0][-1] #last part of first track name
                else:
                    raise
                resColl[label] = oneResult
                    
        entryLabels = None #from GUI
        if entryLabels != None:
            assert len(entryLabels)==len(allUnstructuredResults)
            allUnstructuredResults = zip(entryLabels, [res for generatedLabel, res in allUnstructuredResults])
                
        open(galaxyFn, 'w').write(resColl.getTabularStrRepresentation(columnLabels))
        
        
                
    @staticmethod
    def _getResultsLists(histChoices):
        if len([x for x in histChoices.values() if x!=None])==0:
            return [],[]
        galaxyTNs = [x.split(':') for x in histChoices.values() if x!=None]
                
        galaxyFns = [ExternalTrackManager.extractFnFromGalaxyTN(tn) for tn in galaxyTNs]
        historyNames= [ExternalTrackManager.extractNameFromHistoryTN(tn) for tn in galaxyTNs]
        staticFiles = [GalaxyRunSpecificFile(['results.pickle'], gfn) for gfn in galaxyFns]
        fileSpecificFile = [GalaxyRunSpecificFile([], gfn) for gfn in galaxyFns]        
        
        
        paths = [x.getDiskPath()+'/0' for x in fileSpecificFile]
        pngList = [[v for v in x[2] if v.find('.png')>0] for x in os.walk(paths[0])]
        resultsLists = [load(sf.getFile('r')) for sf in staticFiles]
        return resultsLists, historyNames
    
    @staticmethod
    def _getResDictAndLocalKeys(resultsLists, imputeNAs=False):
        if len(resultsLists)==0:
            return [], []
        firstResultsObject = resultsLists[0][0]
        resDictKeys = firstResultsObject.getResDictKeys()
        if imputeNAs and len(resDictKeys)==0:
            resDictKeys = resultsLists[0][1].getResDictKeys() #very ad hoc extension..
        localKeys = firstResultsObject.keys()
        return resDictKeys, localKeys

    @classmethod
    def validateAndReturnErrors(cls, choices):
        '''
        Should validate the selected input parameters. If the parameters are not valid,
        an error text explaining the problem should be returned. The GUI then shows this text
        to the user (if not empty) and greys out the execute button (even if the text is empty).
        If all parameters are valid, the method should return None, which enables the execute button.
        '''
        #if choices[4] == 'Take any errors at time of execute':
        #    return None
        #elif choices[4] == 'Check validity as choices are made':
        #    pass
        #else:
        #    raise
        #
        #if len(cls._getResultsLists(choices[0])[0]) == 0:
        if len([x for x in choices[0].values() if x!=None])==0:
            return 'At least one history element must be selected!'
        
        if choices[2] in [None,'']:
            return 'A ResDictKey must be selected!'
        
        return None
    
    @staticmethod
    def isPublic():
        return True
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
    @staticmethod    
    def getOutputFormat(choices):
        '''The format of the history element with the output of the tool.
        Note that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.
        '''
        return 'tabular'
        #return 'html'
    
