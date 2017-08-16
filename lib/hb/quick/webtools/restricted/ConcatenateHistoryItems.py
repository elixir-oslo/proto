import os
from cPickle import load

from proto.hyperbrowser.HtmlCore import HtmlCore
from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.webtools.GeneralGuiTool import GeneralGuiTool


class ConcatenateHistoryItems(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Concatenate results of multiple history items"

    @staticmethod
    def getInputBoxNames():
        "Returns a list of names for input boxes, implicitly also the number of input boxes to display on page. Each such box will call function getOptionsBoxK, where K is in the range of 1 to the number of boxes"
        #can have two syntaxes: either a list of stings or a list of tuples where each tuple has two items(Name of box on webPage, name of getOptionsBox)
        return ['Select Histories','List ResDictKeys','ResDictKey', 'Local or Global','Num columns for line wrapping (leave blank for no wrapping)','Impute missing values', 'Row labels (comma-separated if multiple), or leave blank'] #,'Ensure validity'

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
        return ['No','Yes']
        
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
        
        lineWrapping = int(choices[4]) if choices[4] != '' else None
        if choices[5] == 'No':
            imputeNAs = False
        elif choices[5] == 'Yes (put in NA for missing results)':
            imputeNAs = True
        else:
            raise
        
        
        rowLabels = choices[6].split('|') if choices[6]!='' else None
        #print 'Use global results: ',useGlobal
        #print 'Linewrapping: ', lineWrapping
        #print 'Results dict key: ', chosenResDictKey
        resultsLists, historyNames = cls._getResultsLists(histChoices)
        resDictKeys, localKeys  = cls._getResDictAndLocalKeys(resultsLists, imputeNAs)
        #print resultsLists
        from collections import defaultdict
        matrix = defaultdict(dict)
        for i,resultList in enumerate(resultsLists):
            #print 'Num results in history element: ', len(resultList)
            for j,oneResult in enumerate(resultList):
                if not (imputeNAs and len(oneResult.getResDictKeys())==0):
                    assert set(oneResult.getResDictKeys()) == set(resDictKeys), (oneResult.getResDictKeys(), resDictKeys, [x.getResDictKeys() for x in resultList])
                #print oneResult.keys(), localKeys
                #assert oneResult.keys() == localKeys
                colName = historyNames[i] + '-%05i' % j# if j>0 else ''
                if useGlobal:
                    try:
                        matrix['Global result'][colName] = oneResult.getGlobalResult()[chosenResDictKey]                            
                    except:
                        if imputeNAs:
                            import numpy
                            matrix['Global result'][colName] = numpy.nan
                        else:
                            raise
                else:
                    for localKey in oneResult:
                        matrix[localKey][colName] = oneResult[localKey][chosenResDictKey]
        
        #temporarily turned off..
        #if chosenResDictKey=='P-value':
        #    from proto.RSetup import r
        #    origItems = matrix['Global result'].items()
        #    matrix['FDR'] = dict(zip([x[0] for x in origItems], r('p.adjust')([x[1] for x in origItems],'BH') ))
        
        seedRegion = matrix.items()[0]
        sortedColNames = sorted(seedRegion[1].keys())
        for regEntry, matVal in matrix.items():
            assert sorted(matVal.keys()) == sortedColNames, 'Incompatible resultKeys, found both %s and %s, for region entries %s and %s.' % (seedRegion[1].keys(), matVal.keys(), seedRegion[0], regEntry )
            
        #HTML VERSION
        #core.tableHeader([' ']+sortedColNames[:lineWrapping])
        #for localKey in matrix:
        #    if lineWrapping is None:
        #        curRowLabel = rowLabels.pop(0) if rowLabels is not None else str(localKey)
        #        core.tableLine([curRowLabel]+[str(matrix[localKey].get(historyName)) for historyName in sortedColNames])                
        #    else:
        #        numCols = len(sortedColNames)
        #        for rowNum in range(numCols/lineWrapping):
        #            curRowLabel = rowLabels.pop(0) if rowLabels is not None else str(localKey)
        #            colSubset = sortedColNames[rowNum*lineWrapping:(rowNum+1)*lineWrapping]
        #            core.tableLine([curRowLabel]+[str(matrix[localKey].get(historyName)) for historyName in colSubset])
        #core.tableFooter()
        #core.end()
        #print core
        
        #TABULAR VERSION
        sortedResultNames = sortedColNames
        numResults = len(sortedResultNames)

        assert len(matrix.keys())==1, matrix.keys()
        localKey = matrix.keys()[0]            
        if lineWrapping is None:
            lineWrapping = numResults
        numTabularCols = numResults/lineWrapping
        tabularColResults = [None] * numTabularCols
        for tabularColNum in range(numTabularCols):
            curRowLabel = rowLabels.pop(0) if rowLabels is not None else str(localKey)
            resultSubset = sortedResultNames[tabularColNum*lineWrapping:(tabularColNum+1)*lineWrapping]
            tabularColResults[tabularColNum] = [curRowLabel]+[str(matrix[localKey].get(historyName)) for historyName in resultSubset]
        assert len(set([len(x) for x in tabularColResults])) == 1 #all tabularCols have same length
        #else:
        #    assert lineWrapping is None #not supported to split both across history elements and based on fixed number of results per column
        #    tabularColResults = [None] * len(matrix.keys())
        #    for localKey in matrix:                
        #        curRowLabel = rowLabels.pop(0) if rowLabels is not None else str(localKey)
        #        tabularColResults[tabularColNum] = [curRowLabel]+[str(matrix[localKey].get(historyName)) for historyName in sortedResultNames]
            
        tabularRowResults = zip(*tabularColResults)
        
        open(galaxyFn, 'w').writelines( ['\t'.join(rowResult)+'\n' for rowResult in tabularRowResults ])
        
        
        
                
    @staticmethod
    def _getResultsLists(histChoices):
        if len([x for x in histChoices.values() if x!=None])==0:
            return [],[]
        #print 'histChoices',histChoices
        #return []        
        #print time.time()
        galaxyTNs = [x.split(':') for x in histChoices.values() if x!=None]
                
        galaxyFns = [ExternalTrackManager.extractFnFromGalaxyTN(tn) for tn in galaxyTNs]
        historyNames= [ExternalTrackManager.extractNameFromHistoryTN(tn) for tn in galaxyTNs]
        staticFiles = [GalaxyRunSpecificFile(['results.pickle'], gfn) for gfn in galaxyFns]
        fileSpecificFile = [GalaxyRunSpecificFile([], gfn) for gfn in galaxyFns]        
        #print 'Using pickles: ', [x.getDiskPath() for x in staticFiles]
        
        
        paths = [x.getDiskPath()+'/0' for x in fileSpecificFile]
        pngList = [[v for v in x[2] if v.find('.png')>0] for x in os.walk(paths[0])]
        #print time.time()
        resultsLists = [load(sf.getFile('r')) for sf in staticFiles]
        #print time.time()
        return resultsLists, historyNames
    
    @staticmethod
    def _getResDictAndLocalKeys(resultsLists, imputeNAs=False):
        if len(resultsLists)==0:
            return [], []
        #print time.time()
        firstResultsObject = resultsLists[0][0]
        resDictKeys = firstResultsObject.getResDictKeys()
        if imputeNAs and len(resDictKeys)==0:
            resDictKeys = resultsLists[0][1].getResDictKeys() #very ad hoc extension..
        localKeys = firstResultsObject.keys()
        #print time.time()
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
    @staticmethod    
    def getOutputFormat(choices):
        '''The format of the history element with the output of the tool.
        Note that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.
        '''
        return 'tabular'
    
