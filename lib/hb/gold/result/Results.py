import re
from collections import OrderedDict

import numpy

from gold.description.ResultInfo import ResultInfo
from gold.track.TrackView import TrackView
from gold.util.CommonFunctions import isIter
from quick.application.SignatureDevianceLogging import returns
from quick.result.model.ResultTypes import GlobalVisualizationResultType, \
    LinePlotResultType, RawVisualizationResultType

"""This class is a specialized dict that stores data from an analysis run wich includes metadata, localresults and globalresult
    The keys for Results(dict) are GenomeRegion objects that represents the regions an analysis has been performed on.
    The values for Results(dict) are dicts containing local results
    
    Some noticable instance variables:
        _globalResult: is a dict that is returned from the compute method executed on global level
        _resDictKeys: contains a list of the keys that are available for each element of the Results object ie. the keys for the valueDict from Results object
        _resultInfo: is an object based on ResultInfoList.py that converts a resultkey to a textual representation used by the GUI
    
    some noticable methods:
        includeAdditionalResults(other): Fills in extra information on each value-element of the Results-object and also the Global results.
                                         other is a Results-dict with identical genomeRegions. Its a dict update operation on the values of the two Results dicts
                                         And also for Global results
        complementGlobalResult: does an dict update operation between golbalresults of two Results dicts
        getPresCollectionType:  return a presCollectionType based on what kind of data is contained in the Results-object
                                a presCollectionType  maps to which presenters are used for this type                                
"""
class Results(dict):
    '''
    A class holding the result of a run of a statistic (through AnalysisDefJob/StatJob).
    Can be visualized by sending in to ResultsViewer/ResultsViewerCollection and calling print on the resulting object
    '''
    
#friend: ResultsViewer
    FDR_KEY = 'fdr'
    FDR_THRESHOLD = 0.1
    PVALUE_THRESHOLD = 0.05

    def __init__(self, trackName1, trackName2, statClassName):
        self._errors = []
        self._globalResult = None # is a dict that is returned from the compute method executed on global level
        self._resDictKeys = None # contains a list of the keys that are available for each element of the Results object
        self._trackName1 = trackName1
        self._trackName2 = trackName2
        self._statClassName = statClassName
        #self._analysis = None        
        self._analysisText = None #not needed anymore..
        self._runDescription = None
        self._genome = None
        self._onlyGlobalResults = None
        self._isTwoSidedTest = None
        self._h0 = None
        self._h1 = None
        self._nullModel = None
        self._resultInfo = ResultInfo(trackName1, trackName2, statClassName)#is an object based on ResultInfoList.py that converts a resultkey to a textual representation used by the GUI
        dict.__init__(self)
    
    def setAnalysis(self, analysis): 
        #self._analysis = analysis
        self._genome = analysis.getGenome()
        self._onlyGlobalResults = (analysis is not None and analysis.getChoice('onlyGlobalResults') == 'true')
        self._isTwoSidedTest = (analysis is not None and analysis.isTwoSidedTest())
        self._h0 = analysis.getH0() if analysis is not None else None
        self._h1 = analysis.getH1() if analysis is not None else None
        self._nullModel = analysis.getNullModel() if analysis is not None else None
    
    def getGenome(self):
        return self._genome
    
    #probably obsolete
    def setAnalysisText(self, analysisText): 
        self._analysisText = analysisText
        
    def setRunDescription(self, descr):
        self._runDescription = descr
        
    def includeAdditionalResults(self, other, ensureAnalysisConsistency=True):
        if ensureAnalysisConsistency:
            raise NotImplementedError
        
        assert len( set(self.getResDictKeys()).intersection(other.getResDictKeys()) ) == 0
        
        if self._globalResult is None or len(self._globalResult) == 0:
            #What is this used for?
            resKeys = self.getResDictKeys()
            self._globalResult = OrderedDict(zip(resKeys, [None]*len(resKeys)))
        
        if len(self._globalResult) == 0:
            return
        
        if other._globalResult is not None:
            self._globalResult.update(other._globalResult)
        
        for key in self:
            self[key].update(other.get(key))
        
        self._errors += other._errors
        self._resDictKeys = None #reset..
        
    def setGlobalResult(self, result):
        self._globalResult = result

    def complementGlobalResult(self, result):        
        if result is None:
            return
        assert type(result) in [dict, OrderedDict]

        if self._globalResult is None:
            self._globalResult = {}
        assert len( set(self._globalResult.keys()).intersection(set(result.keys())) ) == 0
        self._globalResult.update(result)
    
    def addError(self, exception):
        self._errors.append(exception)
    
    def getAllValuesForResDictKey(self, resDictKey):
        return [ self[reg].get(resDictKey) for reg in self.getAllRegionKeys() ]
    
    def isEmpty(self):
        return self._globalResult is None and len(self.keys()) == 0
        
    def getResDictKeys(self):
        if self._resDictKeys is None:
            if self.isEmpty():
                if len(self._errors)>0:
                    #as the result has some errors set, these should be allowed to propagate even without resDictKeys
                    return []
                else:
                    raise Exception('Error: empty results and thus nothing to display')
            isOrdered = False
            if self._globalResult not in [None,{}]:
                isOrdered = (type(self._globalResult) == OrderedDict)
                keys = self._globalResult.keys()
                
            elif len(self.keys()) > 0:
                for val in self.values():
                    if val not in [None, {}]:
                        isOrdered = (type(self.values()[0]) == OrderedDict)
                        keys = val.keys()
                        break
                else:
                    keys = []
            else:
                keys = []
                
            ASSEMBLY_GAP_KEY = 'Assembly_gap_coverage'
            
            pairs = [(self._resultInfo.getColumnLabel(key),key) for key in keys if not key==ASSEMBLY_GAP_KEY]
            if not isOrdered:
                pairs = sorted(pairs)
                
            if ASSEMBLY_GAP_KEY in keys and len(keys) > 0:
                pairs.append( (self._resultInfo.getColumnLabel(ASSEMBLY_GAP_KEY),ASSEMBLY_GAP_KEY) ) 
            self._resDictKeys = [key for label,key in pairs]
        return self._resDictKeys
        
    def getAllRegionKeys(self):
        return sorted(self.keys())
    
    def getGlobalResult(self):
        return self._globalResult
        
    def getArbitraryLocalResult(self):
        if len(self)>0:
            return self.values()[0]
        else:
            #print self
            return None
    
    def getLabelHelpPair(self, resDictKey):
        return self._resultInfo.getColumnLabel(resDictKey), self._resultInfo.getHelpText(resDictKey)
    
    def getLabelHelpPairs(self):
        return [self.getLabelHelpPair(key) for key in self.getResDictKeys()]
        
    def getStatClassName(self):
        return self._statClassName
    
    #def getAnalysis(self):
    #    return self._analysis

    def getTrackNames(self):
        return self._trackName1, self._trackName2

    def getAllErrors(self):
        return self._errors

    def getPresCollectionType(self):
        #print 'self.getGlobalResult(): ',self.getGlobalResult()
        #print 'self.getArbitraryLocalResult():', self.getArbitraryLocalResult()
        if self.getStatClassName() == 'DataComparisonStat': #a bit ad hoc criterion. Also should check plotType...
            presCollectionType = 'scatter'
        elif self.getStatClassName() == 'VennDataStat':
            presCollectionType = 'venndata'

        elif 'BinScaled' in self.getStatClassName(): #a bit ad hoc criterion. Also should check plotType...
            presCollectionType = 'binscaled'
        elif self.getGlobalResult() not in [None,{}] and len(self.getGlobalResult())>0 and \
            isinstance(self.getGlobalResult().values()[0], LinePlotResultType):
                assert len(self.getGlobalResult().values()) == 1
                presCollectionType = 'lineplot'
        elif (self.getGlobalResult() not in [None,{}] and isinstance(self.getGlobalResult().values()[0], dict)):
            if self.getGlobalResult().values()[0].get('Matrix') is not None:
                presCollectionType = 'matrix'
            else:
                presCollectionType = 'dictofdicts'
        elif self.getGlobalResult() not in [None,{}] and len(self.getGlobalResult())>0 and \
            isinstance(self.getGlobalResult().values()[0], GlobalVisualizationResultType):
                assert len(self.getGlobalResult().values()) == 1, 'Should currently be one if this is visualization result'
                presCollectionType = 'visualization'
        elif self.getGlobalResult() not in [None,{}] and len(self.getGlobalResult())>0 and \
            isinstance(self.getGlobalResult().values()[0], RawVisualizationResultType):
                #assert len(self.getGlobalResult().values()) == 1, 'Should currently be one if this is visualization result'
                presCollectionType = 'rawDataVisualization'        #elif self.getGlobalResult() not in [None,{}] and len(self.getGlobalResult())==1 and \
        #    hasattr(self.getGlobalResult().values()[0], '__iter__'):
        elif self.getGlobalResult() not in [None,{}] and \
            isIter(self.getGlobalResult().values()[0]):#and len(self.getGlobalResult().values()[0])>1:
            #or type(self.getGlobalResult().values()[0])==numpy.ndarray):
                #print 'TYPE: ',type(self.getGlobalResult().values()[0])
                presCollectionType = 'distribution'
        elif (type(self.getArbitraryLocalResult()) is dict) and self.getArbitraryLocalResult().get('Result') and isinstance(self.getArbitraryLocalResult()['Result'], TrackView):
            presCollectionType = 'trackdata'
        #elif self._analysis is not None and self._analysis.getChoice('onlyGlobalResults') == 'true':
        elif  self._onlyGlobalResults == True:
            presCollectionType = 'global'
        else:
            presCollectionType = 'standard'
        #print 'presCollectionType: ',presCollectionType
        #print isinstance(self.getGlobalResult(), GlobalVisualizationResultType), type(self.getGlobalResult()), str(type(self.getGlobalResult().values()[0])).replace('<','')
        return presCollectionType

    def _getSignBins(self, pvals, threshold):        
        numSign = sum(1 for x in pvals if x <= threshold)
        numTested = sum(1 for x in pvals if not numpy.isnan(x))
        numIgnored = len(pvals) - numTested
        return numSign, numTested, numIgnored
       
    def _getSignBinsText(self, pvals, threshold):
        numSign, numTested, numIgnored = self._getSignBins(pvals, threshold)
        text = '%i significant bins out of %i, at %i' % (numSign, numTested, threshold*100) + '% FDR'
        if numIgnored > 0:
            text += ' (%i bin%s excluded)' % (numIgnored, ('' if numIgnored==1 else 's') )
        return text

    #The following methods help interprete data in results, and thus contains some definitions of semantics
    def isSignificanceTesting(self):
        return self.getPvalKey() is not None
    
    def getPvalKey(self):
        keys = self.getResDictKeys()
        if keys is not None:
            for key in keys:
                if re.search('p.*val',key.lower()) is not None:
                    return key
        return None

    def getTestStatisticKey(self):
        keys = self.getResDictKeys()
        if keys is not None:
            for key in keys:
                if re.search('test.?statistic',key.lower()) is not None or 'TSMC' in key:
                    return key
        return None

    def getExpectedValueOfTsKey(self):
        keys = self.getResDictKeys()
        if keys is not None:
            for key in keys:
                if re.search('e\(test.?statistic',key.lower()) is not None:
                    return key
        return None
    
    def inferAdjustedPvalues(self):
        pValKey = self.getPvalKey()                
        if pValKey is None or self.FDR_KEY in self.getResDictKeys():
            return

        regKeys = self.getAllRegionKeys()
        #regPVals = [ self[reg].get(pValKey) if (self[reg].get(pValKey) is not None) else numpy.nan for reg in regKeys]
        #
        #from gold.application.RSetup import r
        #regFdrVals = r('p.adjust')(r.unlist(regPVals), self.FDR_KEY)
        regPVals = [ self[reg].get(pValKey) for reg in regKeys]
        from quick.statistic.McFdr import McFdr
        McFdr._initMcFdr() #to load r libraries..
        regFdrVals = McFdr.adjustPvalues(regPVals, verbose=False)
        
        #if len(regPVals) == 1:
        #    regFdrVals = [regFdrVals]
        assert len(regFdrVals) == len(regKeys), 'fdr: ' + str(len(regFdrVals)) + ', regs: ' + str(len(regKeys))
        for i, reg in enumerate(regKeys):
            self[reg][self.FDR_KEY] = (regFdrVals[i] if regPVals[i] is not None else numpy.nan)
            
        
        if self._globalResult is None:
            keys = self.getResDictKeys()
            self._globalResult = OrderedDict(zip((keys), [None]*len(keys)))
        
        #self._globalResult[self.FDR_KEY] = self.getSignBinsText(regFdrVals, self.FDR_THRESHOLD)
        #if self._globalResult[pValKey] is None:
            #self._globalResult[pValKey] = self.getSignBinsText(regPVals, self.PVALUE_THRESHOLD)
        
        tempGlobalResult = self._globalResult
        self._globalResult = OrderedDict()
        
        self._globalResult.update([(pValKey, tempGlobalResult[pValKey])])    
        self._globalResult.update([(self.FDR_KEY, None)])
        self._globalResult.update([(key, tempGlobalResult[key]) for key in tempGlobalResult.keys() if key != pValKey])
        
        self._resDictKeys = None #resetting..
 
    def getLocalFdrValues(self):
        assert self.FDR_KEY in self.getResDictKeys()
        return [ self[reg][self.FDR_KEY] for reg in self.getAllRegionKeys()]

    @returns((int,int,int)) #numSign, numTested, numIgnored
    def getFdrSignBins(self, threshold=None):
        if threshold is None:
            threshold = self.FDR_THRESHOLD
            
        return self._getSignBins( self.getLocalFdrValues(), threshold)

    @returns(str) 
    def getFdrSignBinsText(self, threshold=None):
        if threshold is None:
            threshold = self.FDR_THRESHOLD
            
        return self._getSignBinsText( self.getLocalFdrValues(), threshold)
        
    def hasOnlyLocalPvals(self):
        pvalKey = self.getPvalKey()
        globalRes = self.getGlobalResult()
        return (pvalKey is not None) and (globalRes is None or globalRes.get(pvalKey) is None or type(globalRes.get(pvalKey)) is str) #remove last part..

    def getTestStatisticText(self):
        key = self.getTestStatisticKey()
        if key is not None:
            key
            testStatText = self._resultInfo.getHelpText(key)
            if testStatText == '':
                testStatText = self._resultInfo.getColumnLabel(key)
            return testStatText
        else:
            return None

    def __str__(self):
        return 'Global result: %s, Local results: %s' % (str(self.getGlobalResult()), dict.__str__(self) )
    
    #def getAdjustedPVals(self, resDictKey, adjustMethod):
    #    pValKey = 'p-value'
    #    if not resDictKey.lower() == pValKey:
    #        return None
    #    #if not pValKey in self.getResDictKeys():
    #        #return None        
    #    fdrVals = r('p.adjust')(r.unlist(self.getAllValuesForResDictKey(resDictKey)), adjustMethod)
    #    return fdrVals
        
    #def getNumSignificantAdjustedPVals(self, resDictKey, threshold, adjustMethod):
    #    fdrVals = self.getAdjustedPVals(resDictKey, adjustMethod)
    #    if fdrVals is None:
    #        return None
    #    return sum(1 for x in fdrVals if x <= threshold)

    
    #def items(self):
    #    return sorted(dict.items(self))
    
    #def addWarning(self):
    #    pass
    
