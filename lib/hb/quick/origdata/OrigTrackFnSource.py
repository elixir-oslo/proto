import os
from config.Config import ORIG_DATA_PATH
from gold.util.CommonFunctions import extractTrackNameFromOrigPath
from gold.util.CommonFunctions import createOrigPath
from quick.util.GenomeInfo import GenomeInfo

#class OrigTrackFnSource(object):
#    def __init__(self, genome):
#        self._genome = genome
#
#    def __iter__(self):
#        return self.yielder()
#
#    def yielder(self):
#        for root, dirs, files in os.walk(ORIG_DATA_PATH + os.sep + self._genome):
#            for file in files:
#                yield root[len(ORIG_DATA_PATH):] + os.sep + file

#class OrigTrackDirSource(object):
#    def __init__(self, genome):
#        self._genome = genome
#
#    def __iter__(self):
#        return self.yielder()
#
#    def yielder(self):
#        for root, dirs, files in os.walk(ORIG_DATA_PATH + os.sep + self._genome):
#            for dir in dirs:
#                yield root[len(ORIG_DATA_PATH):] + os.sep + dir

class OrigTrackNameSource(object):
    def __init__(self, genome, trackNameFilter, avoidLiterature=True):
        self._genome = genome
        self._trackNameFilter = trackNameFilter
        self._avoidLiterature = avoidLiterature

    def __iter__(self):
        return self.yielder()

    def yielder(self):
        literatureTN = GenomeInfo.getPropertyTrackName(self._genome, 'literature')
        literatureTNBase = literatureTN[:-1]

        basePath = createOrigPath(self._genome, self._trackNameFilter)
        for root, dirs, files in os.walk(basePath,topdown=True):
            dirsToRemove = []
            if root==basePath:
                dirsToRemove.append('Trash')
                dirsToRemove.append('Trashcan')

            trackName = extractTrackNameFromOrigPath(root)
            if self._avoidLiterature and trackName == literatureTNBase:
                    dirsToRemove.append(literatureTN[-1])

            for oneDir in dirs:
                if oneDir[0] in ['.','_','#']:
                    dirsToRemove.append(oneDir)

            for rmDir in dirsToRemove:
                if rmDir in dirs:
                    dirs.remove(rmDir)

            #if sum(1 for f in files if f[0] not in ['.','_','#']) == 0:
            #    continue

            #print trackName
            #if any([part[0]=='.' for part in trackName]):
            #    continue

            filterLen = len(self._trackNameFilter)
            #print 'trackName ', trackName, ' and ',self._trackNameFilter

            if (self._trackNameFilter != trackName[:filterLen]):
                continue

#            print trackName
            yield trackName
