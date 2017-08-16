from gold.description.Analysis import Analysis
from gold.description.AnalysisDefHandler import AnalysisDefHandler
from gold.description.AnalysisList import ANALYSIS_SPECS
from config.Config import DebugConfig
from gold.application.LogSetup import logMessage, logException
from quick.application.SignatureDevianceLogging import takes,returns


class AnalysisManager:
    @staticmethod
    def getAnalysisDict():
        analyses = {}
        for category in ANALYSIS_SPECS.keys():
            analyses[category] = dict(zip(ANALYSIS_SPECS[category], [AnalysisDefHandler(q) for q in ANALYSIS_SPECS[category]]))
        return analyses

    @staticmethod
    def getAllCategoryNames():
        return ANALYSIS_SPECS.keys()

    @staticmethod
    @returns(list)
    def getMainCategoryNames():
        return sorted( set([ x.split(':')[0] for x in AnalysisManager.getAllCategoryNames() ]) )

    @staticmethod
    def getSubCategoryNames(mainCategory):
        return sorted( set([ x.split(':')[1] for x in AnalysisManager.getAllCategoryNames() \
                          if x.count(':')>0 and x.split(':')[0] == mainCategory]) )

    @staticmethod
    def combineMainAndSubCategories(mainCategory, subCategory):
        return mainCategory + ':' + subCategory
    
    @staticmethod
    def _tryAnalysisDefForValidity(analysisDef, genome, trackName1, trackName2, tryReversed=True):
        if DebugConfig.VERBOSE:
            logMessage('Trying analysisDef: ' + str(analysisDef) )
        try:
            for tnA, tnB, reversed in [(trackName1, trackName2, False)] + ([(trackName2, trackName1, True)] if tryReversed else []):
                #print "TEMP1: ", (analysisDef, genome, tnA, tnB)
                analysis = Analysis(analysisDef, genome, tnA, tnB, reversed)
                
        #analysis.setTracks(trackName1, trackName2)
        #analysis.setConverters(formatConverter1, formatConverter2)                
                if analysis.isValid():
                   return analysis, reversed
        except Exception, e:
            if DebugConfig.VERBOSE:
                logException(e)
            if DebugConfig.PASS_ON_VALIDSTAT_EXCEPTIONS:
                raise
        return None, False

    @staticmethod
    @takes(str, str, list, list)
    def getValidAnalysesInCategory(category, genome, trackName1, trackName2):#, formatConverter1=None, formatConverter2=None):
        #print 'AnalysisManager: ',trackName1
        validAnalyses = []
        for analysisDef in AnalysisManager.getAnalysisDict()[category].keys():
            #from time import time
            #t = time()
            analysis, reversed = AnalysisManager._tryAnalysisDefForValidity(analysisDef, genome, trackName1, trackName2)
            #logMessage(analysisDef)
            #logMessage('%s' % (time() - t))
            if analysis is not None:
                validAnalyses.append(analysis)
        return validAnalyses
        
    @staticmethod
    def getAllAnalyses():
        analyses = AnalysisManager.getAnalysisDict()
        return reduce( lambda x,y:x+y, [analyses[cat].values() for cat in analyses.keys()] )

    @staticmethod
    def _getAllAnalysisKeys():
        analyses = AnalysisManager.getAnalysisDict()
        return reduce( lambda x,y:x+y, [analyses[cat].keys() for cat in analyses.keys()] )

    @staticmethod
    def getAllAnalysisTuples():
        analyses = AnalysisManager.getAnalysisDict()
        return reduce( lambda x,y:x+y, [analyses[cat].items() for cat in analyses.keys()] )
    
    @staticmethod
    def getAnalysisFromId(id):
        matchingAnalyses = [x for x in AnalysisManager._getAllAnalysisKeys() if x==id]
        assert( len(matchingAnalyses) == 1)
        return matchingAnalyses[0]
    
    @staticmethod
    def getValidAnalysisDefFromTitle(analysisTitle, genome, trackName1, trackName2):
        matchingAnalyses = [x for x in AnalysisManager._getAllAnalysisKeys() if ':' in x and x[0:x.find(':')] == analysisTitle]
        validAnalyses = []
        validReversedAnalyses = []
        
        for analysis in matchingAnalyses:
            analysis, reversed = AnalysisManager._tryAnalysisDefForValidity(analysis, genome, trackName1, trackName2)
            if analysis is not None:
                if reversed:
                    validReversedAnalyses.append(analysis)
                else:
                    validAnalyses.append(analysis)
                    
        if len(validAnalyses) == 1:
            return validAnalyses[0].getDef()
        elif len(validReversedAnalyses) == 1:
            return validReversedAnalyses[0].getDef()
        
#        logMessage('No analysisDef chosen. validAnalyses: %s, validReversedAnalyses: %s' \
#                   % ([x.getDef() for x in validAnalyses], [x.getDef() for x in validReversedAnalyses]))
        return ''
