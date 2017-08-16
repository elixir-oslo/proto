import unittest
from quick.result.Results import Results
from gold.application.GalaxyInterface import GalaxyInterface
from quick.result.Results import Results


class GalaxyInterfaceSandBox(unittest.TestCase):
    def _assertRunEqual(self, target, res):
        localResDict = res._resultComponents[Results.LOCAL_KEY][1]._results
        finalRes = [sorted(localResDict[key].items()) for key in sorted(localResDict.keys())]
        self.assertEqual(target, finalRes)

    #def testSomeStat(self):
    #    self._assertRunEqual([[('Result', 2)], [('Result', 8)]],\
    #       GalaxyInterface.run(["segsMany"],["segsMany"],'RawOverlapStat','TestGenome:chr21:10000000-20000000','*'))

    #def testCreateCustomTrack(self):
    #    funcStr = "lambda bpList: 1.0 * (bpList.count('a')-bpList.count('t')) / (bpList.count('a')+bpList.count('t')+ 0.00001) "
    #    GalaxyInterface.createCustomTrackChr('TestGenome', ['custom'], 101, funcStr, 'chrM')
    #    GalaxyInterface.run(["custom"],["custom"],'SumStat','TestGenome:chrM,8000')

    def testCountStat(self):
        #self._assertRunEqual([[('Result', 119121)], [('Result', 0)]],\
        GalaxyInterface.run(["segsMany"],["segs"],'CountStat','TestGenome:chr21:10000000-10004000','2000')

    def _assertRunEqual(self, target, res):
        localResDict = res._resultComponents[Results.LOCAL_KEY][1]._results
        finalRes = [sorted(localResDict[key].items()) for key in sorted(localResDict.keys())]
        self.assertEqual(target, finalRes)
    
    def _assertBatchEqual(self, target, batchRes):
        self._assertRunEqual(target, sorted(batchRes._resList.items())[0][1])
    
    #def testRun(self):
    #    self._assertRunEqual([[('FN', 0), ('FP', 0), ('TN', 5044739), ('TP', 4955261)], [('FN', 0), ('FP', 0), ('TN', 4900607), ('TP', 5099393)]],\
    #                         GalaxyInterface.run(["segs"],["segs"],'RawOverlapStat','TestGenome:chr1:1-20000000','10000000'))
    
    def runTest(self):
        #from numpy import memmap
        #import gc
        #gc.set_debug(gc.DEBUG_LEAK)
        #a = memmap('testfile', dtype='int32', mode='w+', shape=100)
        #b = a[0:10]
        #del b
        #print '*',gc.collect()
        self.testCountStat()
    
if __name__ == "__main__":
    #GalaxyInterfaceSandBox().run()
    GalaxyInterfaceSandBox().debug()
    #unittest.main()
