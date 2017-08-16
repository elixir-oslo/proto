import os
import functools
#from proto.RSetup import r

from config.Config import HB_SOURCE_CODE_BASE_DIR
import config.Config

LOG_PATH = HB_SOURCE_CODE_BASE_DIR + os.sep + '.testlogs'

import gold.statistic.Statistic
import gold.application.StatRunner
from gold.statistic.ResultsMemoizer import ResultsMemoizer
from gold.application.GalaxyInterface import GalaxyInterface

import gold.description.Analysis
from test.util.Asserts import smartRecursiveAssertList
from test.integration.ProfiledIntegrationTest import ProfiledIntegrationTest

gold.application.StatRunner.PRINT_PROGRESS = False
#gold.description.Analysis.PASS_ON_VALIDSTAT_EXCEPTIONS = True
from config.Config import DebugConfig
DebugConfig.PASS_ON_VALIDSTAT_EXCEPTIONS = True

GalaxyInterface.APPEND_ASSEMBLY_GAPS = False
GalaxyInterface.APPEND_COUNTS = False
#quick.application.GalaxyInterface.DEFAULT_GENOME ='TestGenome'

class GalaxyIntegrationTest(ProfiledIntegrationTest):
    
    def _assertEqualResults(self, target, res):
        resList = [sorted(res[region].items()) for region in res.getAllRegionKeys()]
        if len(res.getAllErrors()) != 0:
            raise res.getAllErrors()[0]
        if self.VERBOSE:
            print 'Target: ', target
            print 'Result: ', resList

        self.assertListsOrDicts(target, resList)
    
    def _assertEqualGlobalResults(self, target, res):
        resList = sorted(res.getGlobalResult().items())
        if len(res.getAllErrors()) != 0:
            raise res.getAllErrors()[0]
        if self.VERBOSE:
            print 'Target: ', target
            print 'Result: ', resList

        self.assertListsOrDicts(target, resList)

    @staticmethod
    def _runTypeGenerator():
        for runType in ['full', 'compBin', 'loadMemo']:
            # Needs to set in config.Config due to GalaxyInterface._tempAnalysisDefHacks()
            config.Config.ALLOW_COMP_BIN_SPLITTING = False if runType == 'full' else True

            ResultsMemoizer.STORE_DISK_MEMOIZATION = True if runType == 'compBin' else False
            ResultsMemoizer.LOAD_DISK_MEMOIZATION = True if runType == 'loadMemo' else False

            print
            print "---------------------"
            print "Run type: " + runType
            print "---------------------"
            print

            yield runType

    def _assertRunEqual(self, target, *args, **kwArgs):
        if self.VERBOSE:
            DebugConfig.PASS_ON_COMPUTE_EXCEPTIONS = True
            print '\n***\n' + str(self.id()) + '\n***'
        
        args = list(args)
        analysisDef = [x.strip() for x in args[2].split('->')]
        if len(analysisDef) == 1:
            analysisDef.append(analysisDef[0])
        analysisDef[0] += ' [randomSeed:=0:]'
        
        args[2] = analysisDef[0] + " -> " + analysisDef[1]
        
        for runType in self._runTypeGenerator():
            if self._usesProfiling():
                DebugConfig.USE_PROFILING = True
                
            res = GalaxyInterface.run(*args, **{'genome':'TestGenome'})

            self._assertEqualResults(target, res)
            if kwArgs.get('globalTarget') != None:
                self._assertEqualGlobalResults(kwArgs['globalTarget'], res)
                
            # if self._usesProfiling():
            #     self._storeProfile(diskMemo)
    
    def _assertBatchEqual(self, target, *args):
        for runType in self._runTypeGenerator():
            batchRes = GalaxyInterface.runBatchLines(*args)
            for i in range(len(batchRes)):
                self._assertEqualResults(target[i], batchRes[i])
