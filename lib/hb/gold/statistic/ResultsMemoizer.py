from gold.statistic.MemoDataCollection import MemoDataCollection
from gold.util.CommonFunctions import createMemoPath, getClassName
from gold.util.CompBinManager import CompBinManager
from config.Config import LOAD_DISK_MEMOIZATION as CFG_LOAD_DISK_MEMOIZATION, \
    STORE_DISK_MEMOIZATION as CFG_STORE_DISK_MEMOIZATION
#from quick.util.CommonFunctions import ensurePathExists

#import third_party.safeshelve as safeshelve
#import quick.util.SafeCPickleBasedShelve as safeshelve
import os

class ResultsMemoizer(object):
    LOAD_DISK_MEMOIZATION = CFG_LOAD_DISK_MEMOIZATION
    STORE_DISK_MEMOIZATION = CFG_STORE_DISK_MEMOIZATION
#    TEMP_ONE_MEMODICT_PER_CHR_TR1 = True

    memoDataCollection = MemoDataCollection()
    #readShelves = {}
    #writeShelves = {}
    #writeShelves = {}
    #STATS_WITHOUT_MEMOIZATION = ['RawDataStatUnsplittable', 'CustomRStatUnsplittable', \
    #                             'BasicCustomRStatUnsplittable','ZipperStatUnsplittable', \
    #                             'XYPairStatUnsplittable', 'DataComparisonStatUnsplittable',\
    #                             'ListCollapserStatUnsplittable', 'SingleValExtractorStatUnsplittable']

    # #fixme: Only temporarily. One path with chromosome length and track1 hash
    # @classmethod
    # def _createShortMemoPath(cls, stat):
    #     return os.sep.join([MEMOIZED_DATA_PATH, str(len(stat._region)),  str(stat._track.getUniqueKey(stat._region.genome))])
    
    @classmethod
    def storeResult(cls, stat):
        if not cls.STORE_DISK_MEMOIZATION or stat.resultLoadedFromDisk or not ResultsMemoizer.isMemoizable(stat):
            return

        memoPath = cls._createMemoPath(stat)
        #memoFn = cls._createShelfFn(memoPath)

#        if cls.TEMP_ONE_MEMODICT_PER_CHR_TR1 and not len(stat._region) == COMP_BIN_SIZE: #fixme: Temporary fix. Stores one memodict per Chromosome/track1 pair
##            print 'storing', os.sep.join([MEMOIZED_DATA_PATH, str(len(stat._region))]), memoPath
#            cls.memoDataCollection[cls._createShortMemoPath(stat)][memoPath] = stat._result
#        else:
        posIndex = str(stat._region.start)

        #if not memoPath in cls.writeShelves:
            #ensurePathExists(memoFn)
            #cls.writeShelves[memoPath] = safeshelve.open(memoFn, 'c', block=False)
            #cls._openShelf(memoPath, memoFn)
        
        #cls.writeShelves[memoPath]
        cls.memoDataCollection[memoPath][posIndex] = stat._result

    @classmethod
    def loadResult(cls, stat):
        if not cls.LOAD_DISK_MEMOIZATION or not ResultsMemoizer.isMemoizable(stat):
            return
        
        memoPath = cls._createMemoPath(stat)
        #memoFn = cls._createShelfFn(memoPath)
        
        #if cls.TEMP_ONE_MEMODICT_PER_CHR_TR1 and not len(stat._region) == COMP_BIN_SIZE: #fixme: Temporary fix. Stores one memodict per Chromosome/track1 pair
#            print 'returning',os.sep.join([MEMOIZED_DATA_PATH, str(len(stat._region))]), memoPath
#            res = cls.memoDataCollection[cls._createShortMemoPath(stat)].get(memoPath)
#            print res
#        else:
        posIndex = str(stat._region.start)
        
        #if not os.path.exists(memoFn)\
        #  or memoPath in cls.writeShelves: #No use in trying to read, as we anyway already have a write-lock..
        #    return None
        #
        #if not os.path.exists(memoFn):
        #    return None
        #
        #if not memoPath in cls.readShelves:
        #    if not os.path.exists(memoFn):
        #        return
        #    cls.readShelves[memoPath] = safeshelve.open(memoFn, 'r', block=False)
        #    #cls._openShelf(memoPath, memoFn)
        #    
        res = cls.memoDataCollection[memoPath].get(posIndex)
        # if res is not None:
        #if posIndex in cls.readShelves[memoPath]:
            #print 'using res for posIndex: ', posIndex
        stat.setMemoizedResult( res )
        #else:
            #print 'did not find res for posIndex: ', posIndex
        
    #@classmethod
    #def _openShelf(cls, memoPath, memoFn):
    #    #os.umask(0002)
    #    cls.openShelves[memoPath] = safeshelve.open(memoFn, 'c')
        
    #@classmethod
    #def _createShelfFn(cls, memoPath):
        #return memoPath + os.sep + 'memo.shelf'

    @classmethod
    def _createMemoPath(cls, stat):
        genome = stat._region.genome
        #combTrackName = stat._track.trackName + (stat._track2.trackName if hasattr(stat,'_track2') else [])
        statId = getClassName(stat) + '_' + stat.VERSION
        configHash = stat.getConfigKey()
        track1Hash = stat._track.getUniqueKey(genome)
        track2Hash = (stat._track2.getUniqueKey(genome) if hasattr(stat,'_track2') else None)
        #basePath = os.sep.join([MEMOIZED_DATA_PATH, getClassName(stat)])
        return createMemoPath(stat._region, statId, configHash, track1Hash, track2Hash)
        #return createMemoPath(combTrackName, genome, chr, getClassName(stat))
    
    @classmethod
    def isMemoizable(cls, stat):
        allTracks = [stat._track] + ([stat._track2] if hasattr(stat,'_track2') else [])
        #notRandomized = all([ (re.match('^[0-9]+$',tr.trackName[-1]) is None) for tr in allTracks]) 
        #notRandomized = not any(isinstance(tr, RandomizedTrack) for tr in allTracks)
        
        #return getClassName(stat) not in cls.STATS_WITHOUT_MEMOIZATION \
        #        and notRandomized \
        #        and CompBinManager.isCompBin(stat._region)
        return stat.IS_MEMOIZABLE and all(track.IS_MEMOIZABLE for track in allTracks) and \
            CompBinManager.isMemoBin(stat._region) 
#        return stat.IS_MEMOIZABLE and all(track.IS_MEMOIZABLE for track in allTracks) and \
#            CompBinManager.isMemoBin(stat._region) 
                                                   

    @classmethod
    def flushStoredResults(cls):
        cls.memoDataCollection.close()
        
        #for path in cls.writeShelves.keys():
        #    cls.writeShelves[path].close()
        #cls.writeShelves = {}
        #cls.readShelves = cls.writeShelves
        #for path in cls.readShelves.keys():
        #    cls.readShelves[path].close()
        #cls.readShelves = {}
        
    
