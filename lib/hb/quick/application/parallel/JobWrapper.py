from gold.statistic.MagicStatFactory import MagicStatFactory
from quick.util.GenomeInfo import GenomeInfo
from gold.description.TrackInfo import TrackInfo
import time
import math

from quick.application.parallel.PickleTools import StatisticArgumentPickleWrapper, RandomizationStatisticArgumentPickleWrapper, CustomTrackCreatorPickleWrapper
from gold.util.CustomExceptions import CentromerError, NoneResultError
from gold.statistic.ResultsMemoizer import ResultsMemoizer
from quick.application.parallel.TaskBatch import TaskBatchListCreator, ChunkGenerator
from config.Config import LOG_PATH

#From Steve Bethard. Used to handle function pointer pickling
def _pickle_method(method):
    func_name = method.im_func.__name__
    obj = method.im_self
    cls = method.im_class
    return _unpickle_method, (func_name, obj, cls)

def _unpickle_method(func_name, obj, cls):
    for cls in cls.mro():
        try:
            func = cls.__dict__[func_name]
        except KeyError:
            pass
        else:
            break
    return func.__get__(obj, cls)

import copy_reg
import types
copy_reg.pickle(types.MethodType, _pickle_method, _unpickle_method)

#Dummy class to "mock" Statistic objects, implements the Statistic "interface"
#Used to contain results from Statistics for easier pickling
class StatisticResultHolder(object):
    def __init__(self, result):
        self._result = result
        
    def getResult(self):
        return self._result
    
    def hasResult(self):
        return hasattr(self, '_result')
    
    def afterComputeCleanup(self):
        pass
    
    def createChildren(self):
        if self.hasResult():
            return

    def validateAndPossiblyResetLocalResults(self, stats):
        return True
 
 
class JobWrapperHelper(object):
    def getFullyQualifiedTaskWrapperClassName(self, wrapper):
        module = wrapper.__module__
        className = wrapper.__class__.__name__.replace("JobWrapper", "TaskWrapper", 1)
        fullyQualifiedWorkerJobWrapperClassName = module + "." + className
        return fullyQualifiedWorkerJobWrapperClassName
    
    def getConfigSettings(self, jobWrapper):
        #Certain statistics will need some non-standard configuration settings. This is a
        #workaround for that
        #Currently only required for jobs that require comp bin splitting
        import gold.util.CompBinManager
        settings = {"gold.util.CompBinManager":
                    {"CompBinManager":
                     {
                      "ALLOW_COMP_BIN_SPLITTING":gold.util.CompBinManager.CompBinManager.ALLOW_COMP_BIN_SPLITTING
                      }
                     }
                    }
        return settings  
    
#"Interface" for the wrapper around jobs on the server side
class JobWrapper(object):
    def __init__(self, job):
        self.job = job
    
    def __iter__(self):
        pass
    
    # Handle each result from a worker, called for each returned result
    def handleResult(self, result):
        pass
    
    # Handle all the results at the end of a run if necessary
    def handleResults(self):
        pass         

class StatisticJobWrapper(JobWrapper):    
    def __init__(self, statJob):
        JobWrapper.__init__(self, statJob)
        self.GENERAL_RESDICTKEY = "Result" #statistic.GENERAL_RESDICTKEY TODO: fix this
        self.referenceKeeper = []
        
    def __iter__(self):
        job = self.job
        for bin in job._userBinSource:
            stat = job._statClass(bin, job._track, job._track2, **job._kwArgs)
            ResultsMemoizer.loadResult(stat)
            if hasattr(stat, "resultLoadedFromDisk") and stat.resultLoadedFromDisk:
                continue
            
            yield StatisticArgumentPickleWrapper(job._statClass, bin, job._track, job._track2, **job._kwArgs)
          
    def handleResult(self, result):
        self.referenceKeeper.append(result)
        for key, res in result.iteritems():
            if key in MagicStatFactory._memoDict:
                MagicStatFactory._memoDict[key]._result = res._result
            else:
                MagicStatFactory._memoDict[key] = res
        
    def handleResults(self):  
        return []
        
class RandomizationManagerStatJobWrapper(JobWrapper):    
    def __init__(self, statistic, seed):
        JobWrapper.__init__(self, statistic)
        self._seed = seed
        self.results = []
        
    def __iter__(self):       
        chunkGenerator = ChunkGenerator(xrange(len(self.job._randResults), self.job._numResamplings), 100)
        for chunk in chunkGenerator:
            yield RandomizationStatisticArgumentPickleWrapper(self.job, chunk, seed=self._seed)
            
    def handleResults(self):             
        return self.results
    
    # Result is a list of results
    def handleResult(self, result):
        self.results.extend(result)
    
class TaskWrapper(object):
    def __init__(self):
        pass
    
    def handleTask(self):
        pass
    
    def initialize(self):
        pass
    
    def finalize(self):
        pass
    
    def reset(self):
        pass
    
class StatisticTaskWrapper(TaskWrapper):
    def __init__(self):
        TaskWrapper.__init__(self)
        self.GENERAL_RESDICTKEY = "Result"
        self.referenceKeeper = None
        
    def handleTask(self, task):  
        stat = task.toStatistic()
        
        try:
            res = stat.getResult()
        except (CentromerError, NoneResultError),e:
            res = None
            
        if not isinstance(res, dict):
            res = {} if res is None else {self.GENERAL_RESDICTKEY : res}

        ResultsMemoizer.flushStoredResults()
        self.referenceKeeper = stat #keeps statistic from being garbage collected
        stat.afterComputeCleanup()        
        
        return self._createResultsDictFromMemoDict()
             
    def _createResultsDictFromMemoDict(self):
        strongValueDict = {}
        for key, statistic in MagicStatFactory._memoDict.iteritems():
            if hasattr(statistic, "_result"):
                strongValueDict[key] = StatisticResultHolder(statistic._result)
            else:
                strongValueDict[key] = StatisticResultHolder(None)   
        
        return strongValueDict        
        
class RandomizationManagerStatTaskWrapper(TaskWrapper):
    def __init__(self):
        TaskWrapper.__init__(self)
        self.referenceKeeper = None
        self.resultHolder = []
            
    def handleTask(self, task):      
        for stat in task.toStatistic():     #A monte carlo statistic unpacks into a number of statistics       
            self.resultHolder.append(stat.getResult())
            self.referenceKeeper = stat
        
        stat.afterComputeCleanup()      
        
        return self.resultHolder
    
class CustomTrackCreatorJobWrapper(JobWrapper):
    def __init__(self, cls, genome, inTrackName, outTrackName, windowSize, func):
        self.cls = cls
        self.genome = genome
        self.inTrackName = inTrackName
        self.outTrackName = outTrackName
        self.windowSize = windowSize
        self.func = func
        
    def __iter__(self):
        for chr in GenomeInfo.getChrList(self.genome).__iter__():
            yield CustomTrackCreatorPickleWrapper(self, chr)

    def handleResult(self, result):
        pass
    
    def handleResults(self):
        pass    
    
class CustomTrackCreatorTaskWrapper(TaskWrapper):
    def handleTask(self, task):
        task.cls.createTrackChr(task.genome, task.inTrackName, task.outTrackName, task.windowSize, task.func, task.chr)
        #todo: rewrite to new preprocessor solution...
        TrackInfo.finalizeTrack(task.genome, task.outTrackName, ['val'], 'float64', 1)
    
class JobWrapperFactory(object):
    @classmethod
    def makeJobWrapper(cls, job, seed=None):
        if cls.isStatisticInChildren(job, "RandomizationManagerStat"):
            print "Making ServerRandomizationManagerStatWrapper"
            return RandomizationManagerStatJobWrapper(job, seed)
        else:
            print "Making ServerStatisticWrapper"
            return StatisticJobWrapper(job)  
        
    @classmethod
    def isStatisticInChildren(cls, job, statisticName):
        for region in job._userBinSource:
            stat = job._statClass(region, job._track, job._track2, *job._args, **job._kwArgs)
            break
        
        stat.createChildren()
        
        result = cls.searchForStatisticRecursively(stat, statisticName)
        MagicStatFactory.resetMemoDict()
        return result
        
    @classmethod
    def searchForStatisticRecursively(cls, statistic, statisticName):
        statisticStringRepresentation = statistic.__class__.__name__.replace("Unsplittable", "").replace("Splittable", "")
        
        if statisticStringRepresentation == statisticName:
            return True
        
        childrenResults = []
        if statistic.hasChildren():
            for child in statistic._children:
                if cls.searchForStatisticRecursively(child, statisticName):
                    return True
                
        return False
        
    
