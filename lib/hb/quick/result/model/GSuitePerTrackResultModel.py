'''
Created on Jan 20, 2016

@author: boris
'''

from collections import OrderedDict

from gold.gsuite import GSuiteConstants


class GSuitePerTrackResultModel(object):
    '''
    Analysis that involve a GSuite usually present results for each track in the suite.
    This model allows combining the original results with additional 'one-per-track(-pair)' statistics and attribute values from the GSuite in a single dictionary,
    and provides a standardized input for the HtmlCore.tableFromDictionary() method.
    '''
    def __init__(self, resultsDict, mainResultTitles, additionalResultsDict=None, additionalAttributesDict=None):
        '''
        resultsDict - The result dict (Track title -> tuple/list of results).
        mainResultTitles - column titles for the main results, must be the same nr of elements.
        
        '''
        assert bool(resultsDict), 'No results in results dictionary. Result per track expected.'
        self._resultsDict = OrderedDict(resultsDict)
        self._additionalResultsDict = OrderedDict(additionalResultsDict) if additionalResultsDict else dict()
        self._additionalAttributesDict = OrderedDict(additionalAttributesDict) if additionalAttributesDict else dict()
        self._finalResultsDict = OrderedDict()
        self._mainResultTitles = mainResultTitles
        assert bool(mainResultTitles), 'There must be at least one main result column title.' 
        if len(mainResultTitles) == 1:
            if type(resultsDict.values()[0]) in [list, tuple]:
                assert len(resultsDict.values()[0]) == 1, 'More than one main result per track, please supply title column for each one'
        else: #>1
            assert (len(mainResultTitles) == len(resultsDict.values()[0])), 'Invalid number of main result column titles, %s. %s expected.' % (str(mainResultTitles), str(len(resultsDict.values()[0])))
        
    def generateColumnTitlesAndResultsDict(self, primaryAttributeName=None):
        '''The primary attribute name, is the attribute that you wish to have in the first column after the ranking index. 
        When None the default first column is the track titles. If set, the name must one of the keys in the additionalAttributesDict'''
        
        if primaryAttributeName:
            assert (self._additionalAttributesDict and primaryAttributeName in self._additionalAttributesDict.values()[0].keys()), \
            'The primary attribute name %s is neither the default None for the %s nor part of the additional attributes dictionary' % (primaryAttributeName, GSuiteConstants.TITLE_COL)
        trackRank = 0
        
        columnTitles = ['Rank']
        
        if primaryAttributeName:
            columnTitles.append(primaryAttributeName)
        columnTitles.append('Track title')
        columnTitles += self._mainResultTitles
        if self._additionalResultsDict:
            for key in self._additionalResultsDict.values()[0]:
                if key != primaryAttributeName:
                    columnTitles.append(key)
        if self._additionalAttributesDict:
            for key in self._additionalAttributesDict.values()[0]:
                if key != primaryAttributeName:
                    columnTitles.append(key)
                
        
        finalResults = OrderedDict()
        
        for trackTitle, mainResults in self._resultsDict.iteritems():
            mainResultsList = []
            if type(mainResults) in [list, tuple]:
                mainResultsList = list(mainResults)
            else:
                mainResultsList.append(mainResults)
            
            finalResultList = []
            trackRank += 1
            if primaryAttributeName:
                finalResultList += list([self._additionalAttributesDict[trackTitle][primaryAttributeName]]) 
            finalResultList += list([trackTitle]) + list(mainResultsList)
            if self._additionalResultsDict:
                for key, val in self._additionalResultsDict[trackTitle].iteritems():
                    if key != primaryAttributeName:
                        finalResultList += [val]
            if self._additionalAttributesDict:
                for key, val in self._additionalAttributesDict[trackTitle].iteritems():
                    if key != primaryAttributeName:
                        finalResultList += [val]
            
            finalResults[trackRank] = finalResultList
        return columnTitles, finalResults
                    
        
                
            
            
                
