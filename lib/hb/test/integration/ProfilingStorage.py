#!/usr/bin/env python
import ast
import os
import sys
import re
from copy import copy

#import shelve as safeshelve
import third_party.safeshelve as safeshelve

from gold.util.Profiler import Profiler
from gold.util.CustomExceptions import ShouldNotOccurError
from config.Config import DATA_FILES_PATH

class ProfilingStorage(object):
    STORAGE_FN = DATA_FILES_PATH + os.sep + 'profiles.shelf'

    @staticmethod
    def _getStorage(mode='r'):
        fn = ProfilingStorage.STORAGE_FN
        #if not os.path.exists(os.path.dirname(fn)):
        #    fn = os.path.basename(fn)
        if mode=='c':
            return safeshelve.open(fn, 'c', writeback=True)
        else:
            return safeshelve.open(fn, 'r')
    
    @staticmethod
    def isStored(testName, revision):
        if not os.path.exists(ProfilingStorage.STORAGE_FN):
            return False
        
        storage = ProfilingStorage._getStorage('r')
    
        isStored = False
        if storage.has_key(testName):
            if storage[testName].has_key(str(revision)):
                if any(diskMemo in storage[testName][str(revision)].keys() \
                       for diskMemo in ['False', 'True']):
                    isStored = True
        
        storage.close()
        return isStored
    
    @staticmethod
    def parseAndStoreProfile(stdout, testName, revision, diskMemo):
        offset = 0
        if diskMemo:
            offset = 2
        
        splittedStdout = stdout.split(Profiler.PROFILE_HEADER + os.linesep)
        
        totStats = re.findall('([0-9\.]+)', splittedStdout[offset+1].splitlines()[0])
        funcCalls = totStats[0]
        
        if len(totStats) == 2:
            primCalls = funcCalls
            cpuTime = totStats[1]
        elif len(totStats) == 3:
            primCalls = totStats[1]
            cpuTime = totStats[2]            
        else:
            raise ShouldNotOccurError()
        
        cumProfile = splittedStdout[offset+1].split(Profiler.PROFILE_FOOTER)[0]
        intProfile = splittedStdout[offset+2].split(Profiler.PROFILE_FOOTER)[0]
    
        storage = ProfilingStorage._getStorage('c')

        if not storage.has_key(testName):
            storage[testName] = {}
            
        if not storage[testName].has_key(str(revision)):
            storage[testName][str(revision)] = {}
            
        storage[testName][str(revision)][str(diskMemo)] = {'funcCalls': funcCalls, \
                                                           'primCalls': primCalls, \
                                                           'cpuTime': cpuTime, \
                                                           'cumProfile': cumProfile, \
                                                           'intProfile': intProfile}
        
        storage.close()
    
    @staticmethod
    def printSummary(numRecords):
        storage = ProfilingStorage._getStorage('r')

        print '--- Profile summary ---' + os.linesep
        for test in sorted(storage.keys()):
            print test + ':' + os.linesep
            print '\t\t\tNot memoized on disk\t\t\t\t\t\t\tMemoized on disk'
            print '\t\t'.join(['SVN Revision'] + ['Function calls','Primitive calls','CPU Time']*2)
            revisions = sorted([int(x) for x in storage[test].keys()])
            if numRecords is not None:
                revisions = revisions[-numRecords:]
            for rev in revisions:
                rev = str(rev)
                cols = [''] * 7
                cols[0] = rev
                field = copy(storage[test][rev])
                for diskMemo in field:
                    offset = 1
                    if diskMemo == 'True':
                        offset = 4
                    cols[offset] = field[diskMemo]['funcCalls']
                    cols[offset+1] = field[diskMemo]['primCalls']
                    cols[offset+2] = field[diskMemo]['cpuTime']
                print '\t\t\t'.join(cols)
                    
            print os.linesep, '-'*153, os.linesep
        storage.close()
    
    @staticmethod
    def printProfiling(testName, revision, diskMemo):
        storage = ProfilingStorage._getStorage('r')

        if storage.has_key(testName):
            if storage[testName].has_key(str(revision)):
                if storage[testName][str(revision)].has_key(str(diskMemo)):            
                    print os.linesep + testName + ':' + os.linesep

                    print Profiler.PROFILE_HEADER
                    print storage[testName][str(revision)][str(diskMemo)]['cumProfile']
                    print Profiler.PROFILE_FOOTER
                    print
                    print Profiler.PROFILE_HEADER
                    print storage[testName][str(revision)][str(diskMemo)]['intProfile']
                    print Profiler.PROFILE_FOOTER
                    
                    storage.close()    
                    return
        
        storage.close()
        print 'Error: Profile not available: ', testName, revision, diskMemo

    @staticmethod
    def getSvnRevision():
        for line in os.popen('svn status -u'):
            if not line.startswith('Status'):
                rev = re.findall('([0-9]+)', ' '.join(line.strip().split()[:-1]))
                #print line, rev
                if rev != []:
                    return None
            else:
                return int(line.split(':')[-1].strip())

if __name__ == "__main__":
    if len(sys.argv) in [2,3] and sys.argv[1].lower() == 'summary':
        ProfilingStorage.printSummary(int(sys.argv[2]) if len(sys.argv) >= 3 else None)
    elif len(sys.argv) == 4:
        ProfilingStorage.printProfiling(sys.argv[1], int(sys.argv[2]),
                                        ast.literal_eval(sys.argv[3]))
    else:
        print 'Syntax: python ProfilingStorage.py summary [numRecords]'
        print '        python ProfilingStorage.py testMethodName revision memoized'
        print '  (e.g) python ProfilingStorage.py TestStatistics.testCountStat 640 False'
