#Untested, but deliberately gold as indirectly well tested and central code
import time
import datetime

from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.util.CustomExceptions import SplittableStatNotAvailableError
from gold.result.Results import Results
from config.Config import PRINT_PROGRESS, MAX_LOCAL_RESULTS_IN_TABLE, MAX_NUM_USER_BINS, USE_PARALLEL, DebugConfig
from gold.statistic.ResultsMemoizer import ResultsMemoizer
from quick.application.UserBinSource import UserBinSource
from gold.origdata.GenomeElementSource import GenomeElementSource
from gold.origdata.GECategoryFilter import GECategoryFilter
from gold.util.CustomExceptions import CentromerError, NoneResultError, InvalidFormatError
from quick.util.GenomeInfo import GenomeInfo
from gold.statistic.AssemblyGapCoverageStat import AssemblyGapCoverageStat
#from quick.statistic.CountPointBothTracksStat import CountPointBothTracksStat
from gold.statistic.Statistic import Statistic
from gold.track.Track import PlainTrack, Track
from gold.application.LogSetup import logException, logMessage, logging
from gold.util.CommonFunctions import getClassName
from quick.application.SignatureDevianceLogging import takes,returns
from gold.statistic.RandomizationManagerStat import RandomizationManagerStat

class StatJob(object):
    GENERAL_RESDICTKEY = 'Result'
    USER_BIN_SOURCE = None

    #@takes(StatJob, UserBinSource, Track, Track, Statistic)
    #statClass will typically be a functools.partial object
    def __init__(self, userBinSource, track, track2, statClass, *args, **kwArgs):
        #Not relevant, as minimal runs are anyway done
        #if StatJob.USER_BIN_SOURCE != None:
            #logMessage('USER_BIN_SOURCE already set in StatJob')
        
        StatJob.USER_BIN_SOURCE = userBinSource
        #if 'userBins' in kwArgs:
        #    logMessage('key "userBins" already found in kwArgs in StatJob.__init__')
        #else:
        #    kwArgs['userBins'] = userBinSource

        self._userBinSource = userBinSource
        self._track = track
        self._track2 = track2
        self._statClass = statClass
        self._args = args
        self._kwArgs = kwArgs
        self._numUserBins = None

    def _initProgress(self, printProgress):
        if hasattr(self._statClass, 'keywords'):
            #since kwArgs to Statistic usually has been wrapped in by functools.partial.
            statKwArgs = self._statClass.keywords
        else:
            statKwArgs = self._kwArgs
        
        from quick.statistic.McFdrSamplingStat import McFdrSamplingStat
        from quick.statistic.SequentialMcSamplingStat import SequentialMcSamplingStat
        #if self._kwArgs.get('minimal') == True or statKwArgs.get('silentProgress') == 'yes': #minimal is in kwArgs to StatJob
        if self._kwArgs.get('minimal') == True: #minimal is in kwArgs to StatJob
            progressClass = SilentProgress
        #elif self._kwArgs.get('numResamplings') < self._kwArgs.get('maxSamples'):
        #elif self._statClass.keywords.get('numResamplings') < self._statClass.keywords.get('maxSamples'): #since kwArgs to Statistic has been wrapped in by functools.partial.
        elif statKwArgs.get('mcSamplerClass') in ['McFdrSamplingStat', McFdrSamplingStat]:
            progressClass = McFdrProgress
        elif statKwArgs.get('mcSamplerClass') in ['SequentialMcSamplingStat', SequentialMcSamplingStat]:
            progressClass = SequentialMcProgress
        elif RandomizationManagerStat.getMcSamplingScheme(statKwArgs) == 'Sequential MC': 
            progressClass = SequentialMcProgress
        elif RandomizationManagerStat.getMcSamplingScheme(statKwArgs) == 'MCFDR': 
            progressClass = McFdrProgress
        else:
            #print 'KWARGS: ',self._kwArgs, self._args
            progressClass = StandardProgress
            
        #self._progress = progressClass(self.getNumUserBins(), printProgress, description=\
        #                    '<p><b>Analyzing ' + str(self._track.trackName) + \
        #                    (' vs ' + str(self._track2.trackName) if self._track2 is not None else '') + ' using statistic: ' + \
        #                    self._statClass.__name__ + '</b><br><br> Performing local analysis: <br>')
        if hasattr(self, '_analysis'):
            nspi = self._analysis.getChoice('numSamplesPerChunk')
        else:
            nspi = self._kwArgs.get('numSamplesPerChunk')
            
        self._progress = progressClass(self.getNumUserBins(), printProgress, description=\
                            '<b>Analyzing ' + str(self._track.trackName) + \
                            (' vs ' + str(self._track2.trackName) if self._track2 is not None else '') + ' using statistic: ' + \
                            self._statClass.__name__ + '</b>\n\nPerforming local analysis:',\
                            numSamplesPerIteration=nspi)
        self._progress.addCount(0)
        
    def run(self, reset=True, printProgress=PRINT_PROGRESS):
        if reset:
            MagicStatFactory.resetMemoDict()
            
        results = self._emptyResults()
        try:
            self._checkNumUserBinsIsValid()
        except Exception, e:
            results.addError(e)
            return results
        
        self._initProgress(printProgress)
        
        if USE_PARALLEL and not ('minimal' in self._kwArgs and self._kwArgs['minimal']):
            from quick.application.parallel.JobHandler import JobHandler
            from quick.application.parallel.JobWrapper import JobWrapperFactory
            jobWrapper = JobWrapperFactory.makeJobWrapper(self)
            #If we are using another statistic wrapper (i.e. monte carlo), the parallelization happens
            #"further down" due to how the HB works and we do not do anything here
            if jobWrapper.__class__.__name__ == "StatisticJobWrapper":
                if 'uniqueId' in self._kwArgs:
                    uniqueId = self._kwArgs["uniqueId"]
                else:
                    uniqueId = datetime.datetime.now().strftime('%Y%m%d-%H%M%S%f')
                jobHandler = JobHandler(uniqueId, True, restrictions=[])
                jobHandler.run(jobWrapper)
        
        startLocal = time.time()
        
        while True:
            stats = self._doLocalAnalysis(results, stats=[])
            #stats[0] is used to call class method
            if self._kwArgs.get('minimal') == True:
                break
            
            numNotDetermined = stats[0].validateAndPossiblyResetLocalResults(stats) if len(stats)>0 else 0            
            self._progress.addFullLocalAnalysisIteration(numNotDetermined)
            if len(stats) == 0 or numNotDetermined == 0:
                break
            #print 'Continuing McFdr'

            
        localAnalysisTime = time.time() - startLocal
        if USE_PARALLEL and not ('minimal' in self._kwArgs and self._kwArgs['minimal']): 
            print "local analysis took %f seconds" % localAnalysisTime
            
        #startGlobal = time.time()
        #import pdb
        #pdb.set_trace()
        self._progress.globalAnalysisStarted()
        self._progress.printMessage('\nPerforming global analysis...')
        while True:
            stat = self._doGlobalAnalysis(results, stats)
            if stat is None:                
                break
            nonDetermined, mValue, mThreshold, pValue, pThreshold = stat.validateAndPossiblyResetGlobalResult(stat)
            self._progress.addGlobalAnalysisIteration(mValue, mThreshold, pValue, pThreshold)

            if nonDetermined == 0:
                break
            
        self._progress.globalAnalysisEnded()
        #print "<br>global analysis took %f seconds" % (time.time() - startGlobal)
        self._endProgress()
        return results

    def _doLocalAnalysis(self, results, stats):
        for region in self._userBinSource:
            res, stat = self._getSingleResult(region)
            results[region] = res
            if not self._avoidUbStatMemoization():
                stats.append(stat)
            #Currently, just to ensure that rawdata is not memoized for all userbins..:
            stat.afterComputeCleanup()
            
            self._progress.addCount()
        return stats
            
    def _doGlobalAnalysis(self, results, stats):
        try:
            res,stat = self._getSingleResult(self._userBinSource)
            results.setGlobalResult( res )
            return stat
            #print results._globalResult
        except SplittableStatNotAvailableError:
            results.setGlobalResult( None )
            return None
            
        
    def _getSingleResult(self, region):
        #print 'Kw Here: ', self._kwArgs, 'args here: ', self._args
        stat = self._statClass(region, self._track, self._track2, *self._args, **self._kwArgs)
        try:
            res = stat.getResult()
        except (CentromerError, NoneResultError),e:
            res = None
            if DebugConfig.VERBOSE:
                logException(e, level=logging.DEBUG)
            if DebugConfig.PASS_ON_NONERESULT_EXCEPTIONS:
                raise
            
        #if not isinstance(res, dict):
        if not getClassName(res) in ['dict', 'OrderedDict']:
            res = {} if res is None else {self.GENERAL_RESDICTKEY : res}
            #res = {self.GENERAL_RESDICTKEY : res}

        ResultsMemoizer.flushStoredResults()
        return res, stat
    
    def getNumUserBins(self):
        if self._numUserBins is None:
            self._numUserBins = sum(1 for el in self._userBinSource)
        return self._numUserBins

    def _checkNumUserBinsIsValid(self):
        numUserBins = self.getNumUserBins()
        if numUserBins < 1:
            raise InvalidFormatError('Zero analysis bins specified.')
            #return False
        elif numUserBins > MAX_NUM_USER_BINS and not self._avoidUbStatMemoization():
            raise InvalidFormatError('Maximum number of user bins exceeded - Maximum: '+str(MAX_NUM_USER_BINS)+ ', Requested: '+str(numUserBins))
            #return False
        return True
    
    def _emptyResults(self):
        return Results(self._track.trackName, self._track2.trackName \
                        if self._track2 is not None else [], self._statClass.__name__)
        
    def _endProgress(self):
        self._progress.printMessage('\nFormatting results...')
        self._progress.printActiveTime()

    def _avoidUbStatMemoization(self):
        #fixme: temporary solution.. along with its use later on..:
        return 'DataComparison' in self._statClass.__name__

class AssemblyGapJob(StatJob):
    def __init__(self, userBinSource, genome, **kwArgs):
        track = PlainTrack(GenomeInfo.getPropertyTrackName(genome, 'gaps'))
        StatJob.__init__(self, userBinSource, track, None, AssemblyGapCoverageStat, **kwArgs)

    def run(self, printProgress=PRINT_PROGRESS):
        res = StatJob.run(self, printProgress=printProgress)
        ResultsMemoizer.flushStoredResults()
        return res
    
#class CountBothTracksJob(StatJob):
#    def __init__(self, userBinSource, trackName1, trackName2):
#        track1, track2 = Track(trackName1), Track(trackName2)
#        StatJob.__init__(self, userBinSource, track1, track2, CountPointBothTracksStat)


class AnalysisDefJob(StatJob):
    '''
    @takes(AnalysisDefJob, str, list, list, UserBinSource)
    @returns Results
    '''
    def __init__(self, analysisDef, trackName1, trackName2, userBinSource,
                 genome=None, galaxyFn=None, *args, **kwArgs):
        from gold.description.Analysis import Analysis

        #  to be removed later.. Just for convenience with development now..
        self._analysisDef = analysisDef
        #  self._trackName1 = trackName1
        #  self._trackName2 = trackName2
        
        if genome is None:
            genome = userBinSource.genome
            
        self._galaxyFn = galaxyFn
            
        self._analysis = Analysis(analysisDef, genome, trackName1, trackName2)
        self._setRandomSeedIfNeeded()
            
        track, track2 = self._analysis.getTracks()
        StatJob.__init__(self, userBinSource, track, track2,
                         self._analysis.getStat(), *args, **kwArgs)

    def _setRandomSeedIfNeeded(self):
        from gold.util.RandomUtil import getRandomSeed
        randSeedChoice = self._analysis.getChoice('randomSeed')
        if randSeedChoice == 'Random':
            self._analysis.changeChoices('randomSeed', [(str(getRandomSeed()),)*2])
    
    def run(self, printProgress=PRINT_PROGRESS):
        '''
        Runs the statistic specified in self._analysis (from analysisDef) and returns an object of class Result
        
        '''
        #Should be there for batch runs.. Should never happen from GUI..
        if self._statClass == None:
            self._handleMissingStat()
            return None

        if DebugConfig.USE_PROFILING:
            from gold.util.Profiler import Profiler
            profiler = Profiler()
            resDict = {}
            profiler.run('resDict[0] = StatJob.run(self, printProgress=printProgress)', globals(), locals())
            res = resDict[0]
        else:
            res = StatJob.run(self, printProgress=printProgress)
        
        res.setAnalysis(self._analysis)
        res.setAnalysisText(str(self._analysis))
        
        ResultsMemoizer.flushStoredResults()
        
        if DebugConfig.USE_PROFILING:
            profiler.printStats()
            if DebugConfig.USE_CALLGRAPH and self._galaxyFn:
                profiler.printLinkToCallGraph(['profile_AnalysisDefJob'], self._galaxyFn)
        
        return res

    def _handleMissingStat(self):
        from gold.application.LogSetup import logMessage, logging
        from gold.description.RunDescription import RunDescription
        import gold.description.Analysis as AnalysisModule
        #AnalysisModule.VERBOSE = True
        msg = 'Started run with invalid statistic... Def: ' + self._analysisDef
                    #+ ', Run description: ' + \
                    #RunDescription.getRevEngBatchLine( self._trackName1, self._trackName2, self._analysisDef, \
                                                      #'Not Available', 'Not Available', self._userBinSource.genome)
        logMessage(msg, level=logging.ERROR)
        raise Exception(msg)
        #res = Results(self._trackName1, self._trackName2, self._analysisDef.split('->')[1])
        #res.addAnalysisDef(self._analysisDef)
        #res.addError(Exception('Invalid statistics selected (Could be beause of an error in statistic. See log.)'))
        #self._analysis.resetValidStat()
        #return res
    
class Progress():
    def __init__(self, totalCount, printProgress=True, description=None, **ignoredKwArgs):
        self._totalCount = totalCount
        self._currCount = 0
        self._description = description
        self._startTime = time.time()
        self._printProgress = printProgress
        self._startGlobalTime = None
        
    def addCount(self, newCounts = 1):
        if not self._printProgress:
            return
        
        if self._description != None:
                print self._description
                self._description = None
        
        for percentage in range( 100*self._currCount/self._totalCount +1, 100*(self._currCount+newCounts)/self._totalCount +1):    
            print '.',
            if percentage % 10 == 0:
                print percentage,'%'
        
        self._currCount += newCounts

    def addFullLocalAnalysisIteration(self, numBinsNotDetermined):
        pass

    def addGlobalAnalysisIteration(self, mValue, mThreshold, pValue, pThreshold):
        pass

    def printActiveTime(self):
        if not self._printProgress:
            return
        print '\nRun took %.1f seconds.\n\n' % (time.time() - self._startTime)
        
    def printMessage(self, msg, withLineSep=True):
        if not self._printProgress:
            return
        if withLineSep:
            print msg
        else:
            print msg,

    def globalAnalysisStarted(self):
        self._startGlobalTime = time.time()
        
    def globalAnalysisEnded(self):
        if not self._printProgress:
            return
        if self._startGlobalTime is None:
            logMessage('Called globalAnalysisEnded without globalAnalysisStarted being called before.', level=logging.WARN)
        print "\nglobal analysis took %f seconds" % (time.time() - self._startGlobalTime)

class SilentProgress(Progress):
    def __init__(self, totalCount, printProgress, description, **ignoredKwArgs):
        Progress.__init__(self, totalCount, False, description)

class StandardProgress(Progress):
    #pass
    def __init__(self, totalCount, printProgress, description=None, numSamplesPerIteration=None, **ignoredKwArgs):
        Progress.__init__(self, totalCount, printProgress, description=description)
        self._description += '\n\nComputation is completed for one bin at a time. Each printed dot represents one percent of bins being completed.'
        
class SequentialMcProgress(Progress):
    SCHEME_NAME = 'Sequential MC'
    def __init__(self, totalCount, printProgress, description=None, numSamplesPerIteration=None, **ignoredKwArgs):
        Progress.__init__(self, totalCount, printProgress, description=description)
        self._numIterations = 0
        from gold.statistic.RandomizationManagerStat import RandomizationManagerStatUnsplittable
        self._numSamplesPerIteration = int(numSamplesPerIteration) if numSamplesPerIteration is not None else 100 #RandomizationManagerStatUnsplittable.NUM_SAMPLES_PER_CHUNK
        self._description += '\nComputing p-values by %s, printing one dot per %i samples across bins' % (self.SCHEME_NAME, self._numSamplesPerIteration)
        
    def addFullLocalAnalysisIteration(self, numBinsNotDetermined):        
        self._numIterations += 1
        self.printMessage('.', withLineSep=False)
        if self._numIterations % 10 == 0:
            self.printMessage('%.1f%% of bins determined (%i samples per bin)' \
                % (100.0*(self._totalCount-numBinsNotDetermined)/self._totalCount, self._numIterations*self._numSamplesPerIteration))

    def addGlobalAnalysisIteration(self, mValue, mThreshold, pValue, pThreshold):        
        self._numIterations += 1
        self.printMessage('.', withLineSep=False)
        if self._numIterations % 10 == 0:
            self.printMessage('Reached %i samples for global analysis (Extreme samples:%i towards %i, P-value:%s towards %s)' % (self._numIterations*self._numSamplesPerIteration, mValue, mThreshold, pValue, pThreshold) )
        
    def addCount(self, newCounts = 1):
        if self._description != None:
            self.printMessage(self._description)
            self._description = None
        
class McFdrProgress(SequentialMcProgress):
    SCHEME_NAME = 'MCFDR'
