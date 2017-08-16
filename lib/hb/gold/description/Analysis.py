import sys
import traceback
from gold.util.CommonFunctions import insertTrackNames, getClassName, prettyPrintTrackName
from gold.track.GenomeRegion import GenomeRegion
from gold.track.Track import Track
from config.Config import DebugConfig
from gold.util.CustomExceptions import IncompatibleTracksError, ShouldNotOccurError, \
                                       IncompatibleAssumptionsError, IdenticalTrackNamesError
from gold.util.RandomUtil import initSeed
from gold.application.StatRunner import StatJob
from gold.description.TrackInfo import TrackInfo
from quick.application.UserBinSource import MinimalBinSource
from quick.util.CommonFunctions import wrapClass, allElementsVersusRest
from gold.description.AnalysisDefHandler import AnalysisDefHandler
from gold.description.AnalysisOption import AnalysisOption
from gold.application.LogSetup import logging, HB_LOGGER, logException, logMessage
import gold.application.StatRunner as StatRunnerModule

def noProgress(func):
    def decoratedFunc(*args):
        prevCfgPrintProgress = StatRunnerModule.PRINT_PROGRESS
        StatRunnerModule.PRINT_PROGRESS = False
        res = func(*args)
        StatRunnerModule.PRINT_PROGRESS = prevCfgPrintProgress
        return res
    return decoratedFunc

class Analysis(AnalysisDefHandler):
    def __init__(self, analysisLine, genome, trackName1, trackName2, reversed=False):
        #print 'IN ANALYSIS: ',analysisLine
        AnalysisDefHandler.__init__(self, analysisLine, reversed)
        self._genome = genome
        self._setTracks(trackName1, trackName2)
        self._useConvertersFromId()
        self._validStatClass = None

    def getTracks(self):
        return self._track, self._track2
    
    def _setTracks(self, trackName1, trackName2):
        self._track = Track(trackName1)
        self._track2 = Track(trackName2)
        #self.resetValidStat()
        #print 'setTracks: ',self._track.trackName

    def _useConvertersFromId(self):
        formatConverter1 = self.getChoice(self.TF1_KEY)
        formatConverter2 = self.getChoice(self.TF2_KEY)
        #assert( not None in [formatConverter1, formatConverter2] )
        self.setConverters(formatConverter1, formatConverter2)

    def setConverters(self, formatConverter1, formatConverter2):
        self._setConverter(self._track, formatConverter1, self.TF1_KEY)
        self._setConverter(self._track2, formatConverter2, self.TF2_KEY)
        
    def _setConverter(self, track, formatConverter, labelKey):
        if track is not None:
            track.setFormatConverter(formatConverter)
            if formatConverter is not None:
                self._appendConverterOptions(track, labelKey)
    
    def resetTracks(self):
        for track in (self._track, self._track2):
            if track is not None:
                track.resetTrackSource()
        
    #def resetValidStat(self):
    #    if hasattr(self, '_validStatClass'):
    #        del self._validStatClass
    
    def getAllStats(self):
        return self._statClassList
    
    def isValid(self):
        return len(self._analysisParts) > 0 and self.getStat() is not None
    
    #def getStat(self):
    #    #assert( len(self._statClassList) >= 1 )
    #    #if not hasattr(self, '_validStatClass'):
    #    prevCfgPrintProgress = StatRunnerModule.PRINT_PROGRESS
    #    StatRunnerModule.PRINT_PROGRESS = False
    #    validStatClass = self._determineStatClass()
    #    StatRunnerModule.PRINT_PROGRESS = prevCfgPrintProgress
    #    return validStatClass
    
    def getGenome(self):
        return self._genome
               
    def getStat(self):
        if self._validStatClass is None:
            options = self.getAllOptionsAsKeys()
            if self.ASSUMP_LABEL_KEY in options:
                validAssumptions = []
                allAssumptions = options[self.ASSUMP_LABEL_KEY]
                for assumption in allAssumptions:
                    self.setChoice(self.ASSUMP_LABEL_KEY, assumption)
                    if self._determineStatClass() is not None:
                        validAssumptions.append(assumption)
                if len(validAssumptions) == 0:
                    return None
                
                if len(validAssumptions) not in [0, len(allAssumptions)]:
                    self._logAssumptionReduction( set(allAssumptions) - set(validAssumptions) )
                self.reduceChoices(self.ASSUMP_LABEL_KEY, validAssumptions)
                self.setDefaultChoice(self.ASSUMP_LABEL_KEY)
            
            self._validStatClass = self._determineStatClass()
            if self._validStatClass is not None:
                self._appendConverterOptions(self._track, self.TF1_KEY)
                self._appendConverterOptions(self._track2, self.TF2_KEY)
        return self._validStatClass
        
    def _logAssumptionReduction(self, removedAssumptions):
        #global VERBOSE
        #prev = VERBOSE
        #VERBOSE = True
    
        for assumption in removedAssumptions:
            logMessage('Assumption "' + str(assumption) + '" was removed from analysisDef: ' + self.getDef())
            self.setChoice(self.ASSUMP_LABEL_KEY, assumption)
            self._determineStatClass()    
            
        #VERBOSE = prev
        
    #@noProgress
    def _determineStatClass(self):
        assert( hasattr(self, '_track') )
        assert( hasattr(self, '_track2') )
        dummyGESource = MinimalBinSource(self._genome)

        if len(self._statClassList)==0:
            #logging.getLogger(HB_LOGGER).warning('Stat class list is empty, for analysisDef: ' + self._analysisLine)
            if self._reversed:
                logMessage('Stat class list is empty, for analysisDef: ' + self._analysisLine, level = logging.WARNING)
            if DebugConfig.PASS_ON_VALIDSTAT_EXCEPTIONS:
                raise ShouldNotOccurError('Stat class list is empty. Analysisdef: '+self._analysisLine)
        
        for statClass in self._statClassList:
            if DebugConfig.VERBOSE:
                logMessage(statClass.__name__ + ': Trying (' + self.getDefAfterChoices() + ')')
#                print statClass.__name__ + ': Trying (' + self.getDefAfterChoices() + ')'

            #for reversed, trackA, trackB in [(False, self._track, self._track2), (True, self._track2, self._track) ]:
            tracks = (self._track, self._track2)
            trackUniqueKeys = [tr.getUniqueKey(self._genome) for tr in tracks if tr is not None]

            trackA, trackB = tracks
            if trackA is None:
                continue

            try:
                StatJob(dummyGESource, trackA, trackB, statClass, minimal=True, **self.getChoices(filterByActivation=True)).run(False)
                #In order not to mess up integration tests
                initSeed()

                for trackIndex, restTrackIndexes in allElementsVersusRest(xrange(len(tracks))):
                    track = tracks[trackIndex]
                    if track is not None and track.formatConverters is None:
                        uniqueKeyForRestTracks = \
                            set(trackUniqueKeys[i] for i in restTrackIndexes)

                        # If several tracks are the same, memory memoization will only result
                        # in one RawDataStat being created, for one Track object. This is a
                        # wanted optimization. In other cases, something is probably wrong if
                        # a track has not been touched. However, this rule may be revisited
                        # when track structure functionality is implemented.
                        if trackUniqueKeys[trackIndex] not in uniqueKeyForRestTracks:
                            raise IncompatibleTracksError(
                                'Track ' + prettyPrintTrackName(track.trackName) +
                                ' was created, but not touched by statistic')

            except IncompatibleTracksError, e:
                if DebugConfig.VERBOSE:
                    logException(e, level=logging.DEBUG,
                                 message='(Warning: error in _determineStatClass for stat: %s)' % statClass.__name__)
                if DebugConfig.PASS_ON_VALIDSTAT_EXCEPTIONS:
                    raise
            except (AssertionError, IncompatibleAssumptionsError, IdenticalTrackNamesError), e:
                if DebugConfig.VERBOSE:
                    logException(e, level=logging.DEBUG,
                                 message='(Warning: error in _determineStatClass for stat: %s)' % statClass.__name__)
                if DebugConfig.PASS_ON_VALIDSTAT_EXCEPTIONS:
                    raise
            except OSError, e:
                if DebugConfig.VERBOSE:
                    logException(e, message='(Error in _determineStatClass, with statClass %s)' % statClass.__name__)
                if DebugConfig.PASS_ON_VALIDSTAT_EXCEPTIONS:
                    raise
                elif not 'withOverlaps' in str(e):
                    raise


            except Exception, e:
                if getClassName(e) == 'AttributeError' and \
                        any(x in str(e) for x in ["has no attribute '_track2'", "'NoneType' object has no attribute"]):
                    if DebugConfig.VERBOSE:
                        logException(e, level=logging.DEBUG, message='(Warning: error in _determineStatClass for stat: %s)' % statClass.__name__)
                else:
                    logException(e, message='(Error in _determineStatClass, with statClass %s)' % statClass.__name__)
                if DebugConfig.PASS_ON_VALIDSTAT_EXCEPTIONS:
                    raise

            else:
                #self._reversed = reversed
                #self._conversionsUsed = len(trackA.conversionsUsed) > 0 or \
                #    ((trackB is not None) and len(trackB.conversionsUsed) > 0)
                ##self._validStatClass = functools.partial(statClass, **self.getChoices())
                #functools.update_wrapper(self._validStatClass, statClass)
                validStatClass = wrapClass(statClass, keywords=self.getChoices(filterByActivation=True) ) #fixme: Perhaps return validStatClass, self.getChoices() instead?
                #self.setConverters( self._track.formatConverters, self._track2.formatConverters if self._track2 is not None else None)
                #self._updateOptions()
                if DebugConfig.VERBOSE:
                    logMessage(statClass.__name__ + ': OK')
#                        print statClass.__name__ + ': OK'
                return validStatClass
            finally:
                self.resetTracks()
        
        return None
    
    def _appendConverterOptions(self, track, labelKey):
        if track is None:
            return

        if track.formatConverters is None:
            # May happen in the second track object if one analyses a track versus itself
            return
        
        if self.getChoice(labelKey) is not None:
            assert(self.getChoice(labelKey) == getClassName(track.formatConverters[0]))
            return
        
        labelPair = (labelKey, '_Treat ' + prettyPrintTrackName(track.trackName) + ' as')
        choicePairs = [ ( getClassName(fc), fc.getOutputDescription(TrackInfo(self._genome, track.trackName).trackFormatName) ) \
                        for fc in track.formatConverters ]
        
        text = '[' + ':'.join(labelPair) + '=' + '/'.join( [':'.join(x) for x in choicePairs] ) + ']'
        self._analysisParts.append(AnalysisOption( text ))
        
    def __str__(self):
        rawText = ''.join( [str(x) for x in self._analysisParts if not (isinstance(x, AnalysisOption) and x.isHidden())] ) 
            #+ (' (converting segments to points)')
        if self._reversed:
        #    rawText = rawText.replace('track1','trackTemp').replace('track2','track1').replace('trackTemp','track2')\
        #        + ' (using reversed track order)'
            rawText += ' (using reversed track order)'
        #assert self._track is not None
        return insertTrackNames(rawText, self._track.trackName, self._track2.trackName if self._track2 is not None else None) 
        
    #def setChoice(self, optionLabelText, choiceText):
    #    raise ShouldNotOccurError
