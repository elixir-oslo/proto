'''
Created on Sep 24, 2015

@author: boris
'''


from config.Config import DebugConfig
from gold.application.LogSetup import logging, logMessage
from gold.statistic.ResultsMemoizer import ResultsMemoizer
from gold.statistic.Statistic import Statistic, StatisticSplittable
from gold.util.CommonFunctions import getClassName, isIter
from gold.util.CustomExceptions import ShouldNotOccurError, CentromerError, NoneResultError

class StatisticV2(Statistic):
    
    def __init__(self, region, trackStructure, *args, **kwArgs):
        from config.Config import IS_EXPERIMENTAL_INSTALLATION  # @UnresolvedImport
        if 'isExperimental' in kwArgs:
            x = kwArgs['isExperimental'].lower()
            if x not in ['false','true']:
                logMessage('isExperimental has value other than false/true', level=logging.WARN)
                raise ShouldNotOccurError('isExperimental has value other than false/true.')
            if x == 'true':
                assert IS_EXPERIMENTAL_INSTALLATION, IS_EXPERIMENTAL_INSTALLATION
        
        if 'assumptions' in kwArgs:
            self._checkAssumptions(kwArgs['assumptions'])

        self._region = region
        self._trackStructure = trackStructure
        
        #TODO:boris 20150924, Code for checking if query and reference (track and track2) are the same track.
        #We should decide if we will allow this in the future.
        
        self._kwArgs = kwArgs
        self._init(**kwArgs)

        self._trace('__init__')

    @property
    def _track(self):
        if not self._trackStructure.getQueryTrackList():
            raise ShouldNotOccurError('The query track list in the track structure must not be empty')
        return self._trackStructure.getQueryTrackList()[0]
    
    def getUniqueKey(self):
        return StatisticV2.constructUniqueKey(self.__class__, self._region, self._trackStructure, **self._kwArgs)
    
    # NOTE:
    # Keep in mind that the key has to be unique across interpreters and machines
    # Therefore each element used in the hash has to be portable - do not try to hash
    # magical objects like None, as the hash value is implementation specific
    # The same goes for hashing objects (like cls)
    @staticmethod
    def constructUniqueKey(cls, region, trackStructure, *args, **kwArgs):
        
        reg = id(region) if isIter(region) else region
        
        #TODO: boris 20150924, check if the caching works with this
        return (hash(str(cls)), Statistic._constructConfigKey(kwArgs), hash(reg), hash(trackStructure))
    
    def _getSingleResult(self, region):
        #print 'Kw Here: ', self._kwArgs, 'args here: ', self._args
        
        stat = self._statClass(region, self._trackStructure, *self._args, **self._kwArgs)
        try:
            res = stat.getResult()
        except (CentromerError, NoneResultError):
            res = None
            if DebugConfig.PASS_ON_NONERESULT_EXCEPTIONS:  # @UndefinedVariable
                raise
            
        #if not isinstance(res, dict):
        if not getClassName(res) in ['dict', 'OrderedDict']:
            res = {} if res is None else {self.GENERAL_RESDICTKEY : res}
            #res = {self.GENERAL_RESDICTKEY : res}

        ResultsMemoizer.flushStoredResults()
        return res, stat

    
class StatisticV2Splittable(StatisticV2, StatisticSplittable):
    
    def __init__(self, region, trackStructure, *args, **kwArgs):
        StatisticV2.__init__(self, region, trackStructure, *args, **kwArgs)
        self._args = args
        #self._kwArgs = kwArgs
        self._childResults = []
        self._bins = self._splitRegion()
        #self._binIndex = 0
        self._curChild = None
        
    def computeStep(self):
        StatisticSplittable.computeStep(self)
        
    def afterComputeCleanup(self):
        StatisticSplittable.afterComputeCleanup(self)
        
    def _getChildObject(self, binDef):
        childName = getClassName(self).replace('Splittable','')
        try:
            module = __import__('.'.join(['gold','statistic',childName]),globals(), locals(), [childName])
        except:
            module = __import__('.'.join(['quick','statistic',childName]),globals(), locals(), [childName])

        return getattr(module, childName)(binDef, self._trackStructure, *self._args, **self._kwArgs)
