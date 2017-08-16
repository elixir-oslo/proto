import gold.statistic
import quick.statistic
from gold.util.CompBinManager import CompBinManager
from weakref import WeakValueDictionary
from config.Config import DebugConfig, USE_MEMORY_MEMOIZATION,LOG_PATH
from gold.statistic.Statistic import OnlyGloballySplittable, Statistic
from gold.util.CommonFunctions import isIter
from gold.application.LogSetup import logging, logMessage, PARALLEL_LOGGER, logException
from gold.util.CustomExceptions import SplittableStatNotAvailableError
from quick.util.debug import DebugUtil


class MagicStatFactory(object):
    #resultLabel = 'Result'

    _memoDict = WeakValueDictionary()   
    
    @classmethod
    def resetMemoDict(cls):
        #cls._memoDict = WeakValueDictionary()
        for key in cls._memoDict.keys():
            del cls._memoDict[key]

    @classmethod
    def getMemoDictSize(cls):
        return len(cls._memoDict.keys())
    
    @staticmethod
    def _getClass(className, suffix):
        try:
            return globals()['gold'].__dict__['statistic'].__dict__[className].__dict__[className + suffix]
        except Exception, e:
            #if VERBOSE:
            #    print 'MGF:' ,e.__class__, e
            return globals()['quick'].__dict__['statistic'].__dict__[className].__dict__[className + suffix]

    @staticmethod
    def _transferMembers(origCls, subCls):
        #subCls.resultLabel = origCls.resultLabel
        #subCls.minimize = origCls.minimize
        return subCls

    @staticmethod
    def _getSubCls(origCls, region):
        #print "with class: ",origCls.__name__,'and region: ',region,"<br>"
        if isIter(region) or CompBinManager.canBeSplitted(region):
            try:                
                splittableClass = MagicStatFactory._getClass(origCls.__name__, 'Splittable')
                #print "FOUND SPLITTABLE: ", <splittableClass
                if isIter(region):
                    #Always use splittableClass if a global region
                    return splittableClass
                else:
                    #Use only if splittableClass also accepts splitting of userbins
                    if not issubclass(splittableClass, OnlyGloballySplittable):
                        return splittableClass                    
            #except (KeyError, SplittableStatNotAvailableError), e:
            except KeyError, e:
                if DebugConfig.VERBOSE:
                    logException(e, level=logging.DEBUG, message="In MagicStatFactory._getSubCls: ")
        #print "Going for: ", 'Unsplittable','<br>'
        return MagicStatFactory._getClass(origCls.__name__, 'Unsplittable')
        
    def __new__(origCls, region, *args, **keywords):

        subCls = MagicStatFactory._getSubCls(origCls, region)
#         uniqueKey = Statistic.constructUniqueKey(subCls, region, *args, **keywords)
        uniqueKey = subCls.constructUniqueKey(subCls, region, *args, **keywords)
        if MagicStatFactory._memoDict.has_key(uniqueKey) and USE_MEMORY_MEMOIZATION:
            #print '-',[[x.__class__, str(x._region), x._track.trackName, x._track2.trackName if hasattr(x,'_track2') else ''] for x in [protoStat, MagicStatFactory._memoDict[protoStat]]]
            return MagicStatFactory._memoDict[uniqueKey]
        else:
            #print "Not there: %s - %s (%s)" % (region, uniqueKey, ', '.join([str(x) for x in (subCls, region, args, keywords)]))
            newStat = MagicStatFactory._createNew(origCls, subCls, region, *args, **keywords)
            MagicStatFactory._memoDict[uniqueKey] = newStat
                
            return newStat

    @staticmethod
    def updateMemoDict(stat, statKwUpdateDict):
        oldUniqueKey = stat.getUniqueKey()
        stat._kwArgs.update(statKwUpdateDict)
        newUniqueKey = stat.getUniqueKey()

        del MagicStatFactory._memoDict[oldUniqueKey]
        MagicStatFactory._memoDict[newUniqueKey] = stat


    @staticmethod
    def _createNew(origCls, subCls, region, *args, **keywords):
        #return MagicStatFactory._transferMembers(origCls, subCls(region, *args, **keywords))
        return subCls(region, *args, **keywords)
        #return subCls.__new__(subCls, region, *args, **keywords) 
        
    @classmethod
    def minimize(cls, genome):
        pass
