from gold.application.StatRunner import StatJob
from gold.track.TrackStructure import TrackStructure
from gold.util.CustomExceptions import ShouldNotOccurError, CentromerError,\
    NoneResultError
from config.Config import DebugConfig
from gold.util.CommonFunctions import getClassName
from gold.statistic.ResultsMemoizer import ResultsMemoizer
'''
Created on Sep 24, 2015

@author: boris
'''

class StatJobV2(StatJob):
    
    def __init__(self, userBinSource, trackStructure, statClass, *args, **kwArgs):
        StatJob.USER_BIN_SOURCE = userBinSource
        #if 'userBins' in kwArgs:
        #    logMessage('key "userBins" already found in kwArgs in StatJob.__init__')
        #else:
        #    kwArgs['userBins'] = userBinSource   
        self._userBinSource = userBinSource
        self._trackStructure = trackStructure
        self._statClass = statClass
        self._args = args
        self._kwArgs = kwArgs
        
        self._numUserBins = None
    
    @property
    def _track(self):
        if TrackStructure.QUERY_KEY not in self._trackStructure\
        or not self._trackStructure.getQueryTrackList():
            raise ShouldNotOccurError('Track structure must contain a query list of at least one track')
        return self._trackStructure.getQueryTrackList()[0]
    
    @property
    def _track2(self):
        if TrackStructure.REF_KEY in self._trackStructure\
        and self._trackStructure.getReferenceTrackList():
            return self._trackStructure.getReferenceTrackList()[0]
        
        return None
    
#     def _emptyResults(self):

    def _getSingleResult(self, region):
        stat = self._statClass(region, self._trackStructure, *self._args, **self._kwArgs)
        try:
            res = stat.getResult()
        except (CentromerError, NoneResultError),e:
            res = None
            if DebugConfig.PASS_ON_NONERESULT_EXCEPTIONS:
                raise
            
        #if not isinstance(res, dict):
        if not getClassName(res) in ['dict', 'OrderedDict']:
            res = {} if res is None else {self.GENERAL_RESDICTKEY : res}
            #res = {self.GENERAL_RESDICTKEY : res}

        ResultsMemoizer.flushStoredResults()
        return res, stat
     
# class AnalysisDefJobV2(StatJobV2):
#     
#     def __init__(self, analysisDef, trackStructure, userBinSource, genome=None, galaxyFn=None, *args, **kwArgs):
#         from gold.description.Analysis import Analysis
#     
#         #to be removed later.. Just for convenience with development now.. 
#         self._analysisDef = analysisDef
#         #self._trackName1 = trackName1
#         #self._trackName2 = trackName2
#         
#         if genome is None:
#             genome = userBinSource.genome
#             
#         self._galaxyFn = galaxyFn
#             
#         self._analysis = Analysis(analysisDef, genome, trackName1, trackName2)
#         
#         self._setRandomSeedIfNeeded()
#             
#         StatJobV2.__init__(self, userBinSource, trackStructure, self._analysis.getStat(), *args, **kwArgs)
    
