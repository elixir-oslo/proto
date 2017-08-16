import os
from collections import namedtuple, OrderedDict
from threading import Thread, RLock, Condition, current_thread, Lock

from gold.gsuite.GSuite import GSuite
from gold.gsuite.GSuiteTrack import GalaxyGSuiteTrack
from gold.origdata.GESourceWrapper import GESourceWrapper
from gold.origdata.GenomeElementSource import GenomeElementSource


printLock = Lock()


ThreadInfo = namedtuple('ThreadInfo', ('thread', 'condition'))


def getRandomTracks(gSuite, number, seed=9001):
    from gold.util.RandomUtil import random
    randomTrackList = []
    trackList = [t for t in gSuite.allTracks()]
    trackIndexList = [i for i in range(len(trackList))]

    random.seed(seed)
    for i in range(number):
        if len(trackIndexList) == 0:
            break
        index = random.randint(0, len(trackIndexList)-1)
        randomTrackList.append(trackList[trackIndexList[index]])
        trackIndexList.pop(index)

    return randomTrackList


def getRandomGSuite(gSuite, number, seed=9001):
    rGSuite = GSuite()
    randomTrackList = getRandomTracks(gSuite, number, seed)
    for track in randomTrackList:
        rGSuite.addTrack(track)

    return rGSuite


def attributesType(gSuite):
    allAttributes = OrderedDict()

    for track in gSuite.allTracks():
        for attribute in track.attributes:
            allAttributes[attribute] = ''

    i = 0
    for x in gSuite.allTracks():
        if i == 0:
            for attribute in allAttributes.keys():
                t = x.getAttribute(attribute)
                if t == None:
                    allAttributes[attribute] = False
                else:
                    try:
                        t = float(t)
                        allAttributes[attribute] = True
                    except:
                        allAttributes[attribute] = False

        i += 1

    return allAttributes


def getAllTracksWithAttributes(gSuite):
    allAttributes = gSuite.attributes
    allTracksWithAttributes = []

    for x in gSuite.allTracks():
        part = []
        part.append(x.trackName)
        for attribute in allAttributes:
            t = x.getAttribute(attribute)
            part.append(t)
        allTracksWithAttributes.append(part)

    return allTracksWithAttributes


class ValueDependentThreadedGESource(GESourceWrapper, GenomeElementSource):
    """
    GenomeElementSource wrapper that handles multiple threads reading specific vals.

    ValueDependentThreadedGESource inherits from GESourceWrapper, which in practice
    works as if would have been the contained GenomeElementSource, except for overridden
    methods.

    __iter__ and next() methods are the main overridden methods. As one does not want
    each thread to restart the iterator, the __iter__() method does nothing, while
    the iter() method is the real iteration start. ValueDependentThreadedGESource
    makes sure that only one thread (based upon the value of the current GenomeElement
    object) is allowed to read from it at any time (using the next() method).
    Each time the current value changes (for the new GenomeElement), the correct
    waiting thread is notified (or a new thread is created if no other thread is
    waiting), nand the current thread waits.

    Init parameters:
    geSource -- The contained GenomeElementSource that is to be split up
    threadInfoDict -- Dict of value -> ThreadInfo tuple
    valAttr -- The attribute of GenomeElement used as the value to split by
    threadFactoryFunc -- Callback function to generate new threads
    """

    # To override the __new__ method of GenomeElementSource
    def __new__(cls, geSource, geSourceLock, threadInfoDict, valAttr, threadFactoryFunc):
        return object.__new__\
            (cls, geSource, geSourceLock, threadInfoDict, valAttr, threadFactoryFunc)
    
    def __init__(self, geSource, geSourceLock, threadInfoDict, valAttr, threadFactoryFunc):
        self._geSource = geSource
        self._lock = geSourceLock
        self._threadInfoDict = threadInfoDict
        self._valAttr = valAttr
        self._threadFactoryFunc = threadFactoryFunc
        self._geIter = None
        self._curGE = None
        self._curThreadVal = None
        self._firstThreadVal = None
        self._threadsToStopIteraton = set()
        self._prefixList = None

    def iter(self): # Real iterator start
        with self._lock:
            self._geIter = self._geSource.__iter__()

            try:
                self._curGE = self._geIter.next()
                self._curThreadVal = self.curVal()
                self._firstThreadVal = self._curThreadVal

            except StopIteration:
                self._curGE = None
                self._markIteratorAsFinished()

                lastWarningMsg = ' Last warning when parsing file: %s' % self._geIter.getLastWarning() \
                                 if self._geIter.anyWarnings() else ''
                raise Warning('File has no valid data lines.%s' % lastWarningMsg)

    def __iter__(self):
        with self._lock:
            # For allowing several consecutive iterations to be started
            ti = self._threadInfoDict[self._curThreadVal]
            if ti.thread.name in self._threadsToStopIteraton:
                if self._curGE is None and \
                        self._curThreadVal != self._firstThreadVal:
                    self._curThreadVal = self._firstThreadVal

                    firstThreadCond = self._threadInfoDict[self._firstThreadVal].condition
                    firstThreadCond.notify()

                    # Stops the current thread at this point. Waits until it is notified
                    # that curVal has changed back to the val of the thread
                    curThreadCond = ti.condition
                    curThreadCond.wait()

                if self._curGE is None:
                    self.iter()

                self._threadsToStopIteraton.remove(ti.thread.name)

            return self

    def next(self):
        with self._lock:
            self._checkFinished()
            curVal = self.curVal()

            if not curVal in self._threadInfoDict:
                newThread = self._threadFactoryFunc(self)
                self._threadInfoDict[curVal] = ThreadInfo(newThread, Condition(self._lock))
                newThread.start() # New thread will wait on lock

            curThreadCond = self._threadInfoDict[self._curThreadVal].condition
            if self._curThreadVal != curVal: # Thread should halt
                self._curThreadVal = curVal

                nextThreadCond = self._threadInfoDict[curVal].condition
                nextThreadCond.notify() # Notify the thread writing the curVal

                # Stops the current thread at this point. Waits until it is notified
                # that curVal has changes back to the val of the thread
                curThreadCond.wait()

            return self._fetchNextGeAndReturnCurGe()

    def _fetchNextGeAndReturnCurGe(self):
        self._checkFinished()
        
        curGE = self._curGE

        try:
            self._curGE = self._geIter.next()
        except StopIteration:
            self._curGE = None
            self._markIteratorAsFinished()

        return curGE

    def _markIteratorAsFinished(self):
        for ti in self._threadInfoDict.values():
            self._threadsToStopIteraton.add(ti.thread.name)
            
    def _checkFinished(self):
        if current_thread().name in self._threadsToStopIteraton:
            raise StopIteration()

    def getPrefixList(self):
        return GenomeElementSource.getPrefixList(self)

    def parseFirstDataLine(self): # As the super method calls __iter__
        with self._lock:
            if self._curGE is None:
                self.__iter__()
            return self._curGE

    def curVal(self):
        with self._lock:
            if self._curGE is None:
                self.parseFirstDataLine()
            return str(getattr(self._curGE, self._valAttr))


class ValSpecificFileComposerThread(Thread):
    """
    Thread that reads from a ValueDependentThreadedGESource for a single value
    and composes an output file based upon the read GenomeElements. The new file
    will be named VALUE.SUFFIX, where value is the current value as defined by
    the ValueDependentThreadedGESource, and SUFFIX is defined by the selected
    FileFormatComposer class.

    valDepThreadedGeSource -- Instance of ValueDependentThreadedGESource
    condition - Instance of threading.Condition
    composerCls -- FileFormatComposer class to use
    baseDir -- Base directory for the output
    """

    @staticmethod
    def getThreadFactoryFunc(composerCls, baseDir, finishedCond):
        def newThread(valDepThreadedGeSource, composerCls, baseDir, finishedCond):
            return ValSpecificFileComposerThread(valDepThreadedGeSource, \
                                                 composerCls, baseDir, finishedCond)

        from functools import partial
        return partial(newThread, composerCls=composerCls, \
                       baseDir=baseDir, finishedCond=finishedCond)

    def __init__(self, valDepThreadedGeSource, composerCls, baseDir, finishedCond):
        Thread.__init__(self)
        self._geSource = valDepThreadedGeSource
        self._composerCls = composerCls
        self._baseDir = baseDir
        self._finishedCond = finishedCond
        self.extraFileName = None

    def run(self):
        curVal = self._geSource.curVal()
        suffix = self._composerCls.getDefaultFileNameSuffix()
        self.extraFileName = curVal + '.' + suffix
        outputFn = os.path.join(self._baseDir, self.extraFileName)
        
        composer = self._composerCls(self._geSource)
        composer.composeToFile(outputFn)

        with self._finishedCond:
            self._finishedCond.notify()


def createGalaxyGSuiteBySplittingInputFileOnAttribute \
        (galaxyFn, inputGeSource, genome, composerCls, valAttr):
    from quick.application.ExternalTrackManager import ExternalTrackManager
    
    threadInfoDict = OrderedDict()
    baseDir = ExternalTrackManager.getGalaxyFilesDir(galaxyFn)
    finishedCond = Condition()
    threadFactoryFunc = ValSpecificFileComposerThread.\
        getThreadFactoryFunc(composerCls, baseDir, finishedCond)

    geSourceLock = RLock()
    valDepThreadedGeSource = \
        ValueDependentThreadedGESource(inputGeSource, geSourceLock, \
                                       threadInfoDict, valAttr, threadFactoryFunc)
    valDepThreadedGeSource.iter()

    firstThreadCond = Condition(geSourceLock)
    firstThread = threadFactoryFunc(valDepThreadedGeSource)
    firstVal = valDepThreadedGeSource.curVal()
    threadInfoDict[firstVal] = ThreadInfo(firstThread, firstThreadCond)

    with finishedCond:
        firstThread.start()
        finishedCond.wait()

    gsuite = GSuite()

    # At this point one of the threads is finished, but the other threads are still waiting.
    for val, ti in threadInfoDict.iteritems():
        with ti.condition:
            ti.condition.notify()

        ti.thread.join()
        
        uri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn,
                                            extraFileName=ti.thread.extraFileName)
        track = GalaxyGSuiteTrack(uri, title=val, genome=genome)
        gsuite.addTrack(track)

    return gsuite
