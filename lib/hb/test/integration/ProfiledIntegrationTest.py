import sys
import StringIO

from gold.util.Profiler import Profiler
from test.integration.ProfilingStorage import ProfilingStorage
from test.util.Asserts import TestCaseWithImprovedAsserts
from third_party.asteval_raise_errors import Interpreter

class ProfiledIntegrationTest(TestCaseWithImprovedAsserts):
    VERBOSE = False
    def setUp(self):
        if not self.VERBOSE:
            sys.stdout = StringIO.StringIO()
        if not hasattr(ProfiledIntegrationTest, '_svnRevision'):
            ProfiledIntegrationTest._svnRevision = ProfilingStorage.getSvnRevision()
            
        #print ProfiledIntegrationTest._svnRevision, self._getId(), ProfilingStorage.isStored(self._getId(), ProfiledIntegrationTest._svnRevision)
        
        if ProfiledIntegrationTest._svnRevision != None and \
            not ProfilingStorage.isStored(self._getId(), ProfiledIntegrationTest._svnRevision):
            self._profiler = Profiler()
        else:
            self._profiler = None
        
    def _getId(self):
        return self.id().split('.')[-1]
    
    def _usesProfiling(self):
        return self._profiler is not None
    
    def _runWithProfiling(self, runStr, symbolDict={}):
        aeval = Interpreter()
        if symbolDict:
            aeval.symtable.update(symbolDict)

        if not self._usesProfiling():
            return aeval(runStr)
        else:
            print 'Running with profiling..'
            res = self._profiler.run('aeval(%s)' % runStr, globals, locals)
            self._profiler.printStats()
            return res
        
    def _storeProfile(self, diskMemo=False):
        if self.VERBOSE or not self._usesProfiling():
            return 
        
        ProfilingStorage.parseAndStoreProfile(sys.stdout.getvalue(), self._getId(),\
                                              ProfiledIntegrationTest._svnRevision, diskMemo)
