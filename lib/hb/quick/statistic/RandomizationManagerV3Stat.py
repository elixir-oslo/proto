'''
Created on Nov 3, 2015

@author: boris
'''

from gold.statistic.MagicStatFactory import MagicStatFactory
from quick.statistic.McFdrSamplingV2Stat import *
from quick.statistic.StatisticV2 import StatisticV2
from quick.util.McEvaluators import *
from quick.statistic.NaiveMCSamplingV2Stat import NaiveMCSamplingV2Stat

class RandomizationManagerV3Stat(MagicStatFactory):
    '''
    classdocs
    '''
    pass

#class RandomizationManagerV3StatSplittable(StatisticSumResSplittable):
#    pass
            
class RandomizationManagerV3StatUnsplittable(StatisticV2):    
    IS_MEMOIZABLE = False

    def _init(self, evaluatorFunc, mcSamplerClass, tail, rawStatistic, **kwArgs):
        if type(evaluatorFunc) is str:
            evaluatorFunc = globals()[evaluatorFunc]
        self._evaluatorFunc = evaluatorFunc

        if type(mcSamplerClass) is str:
            mcSamplerClass = globals()[mcSamplerClass]
        self._mcSamplerClass = mcSamplerClass
        
        self._tail = tail
        self._rawStatistic = self.getRawStatisticClass(rawStatistic) #just to extract name

    def _compute(self):
        return self._evaluatorFunc( self._children[0].getResult(), self._tail, self.getRawStatisticMainClassName() )
    
    def _createChildren(self):
        self._addChild(self._mcSamplerClass(self._region, self._trackStructure, **self._kwArgs) )

    def getRawStatisticMainClassName(self):
        return self._rawStatistic.__name__.replace('Splittable', '').replace('Unsplittable', '')
        
    @classmethod
    def validateAndPossiblyResetLocalResults(cls, localManagerObjects):
        localSamplingObjects = [x._children[0] for x in localManagerObjects]
        numNonDetermined = localManagerObjects[0]._children[0].validateAndPossiblyResetLocalResults(localSamplingObjects)
        for i in range(len(localSamplingObjects)):
            if not localSamplingObjects[i].hasResult():
                del localManagerObjects[i]._result
        return numNonDetermined

    def validateAndPossiblyResetGlobalResult(self, dummy):
        res = self._children[0].validateAndPossiblyResetGlobalResult(dummy)
        if res[0]==1:
            #print 'TEMP3'
            del self._result
        return res
