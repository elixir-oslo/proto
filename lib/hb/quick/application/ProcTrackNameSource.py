import os
from gold.util.CommonFunctions import parseDirPath
from gold.util.CommonFunctions import createDirPath
from quick.application.ProcTrackOptions import ProcTrackOptions
from quick.util.GenomeInfo import GenomeInfo

class ProcTrackNameSource(object):
    def __init__(self, genome, fullAccess=False, avoidLiterature=True, includeParentTrack=True):
        self._genome = genome
        self._fullAccess = fullAccess
        self._avoidLiterature = avoidLiterature
        self._includeParentTrack = includeParentTrack
    
    def __iter__(self):
        return self.yielder([])
    
    def yielder(self, curTn, level=0):
        if self._avoidLiterature and curTn == GenomeInfo.getPropertyTrackName(self._genome, 'literature'):
            return
        
        for subtype in ProcTrackOptions.getSubtypes(self._genome, curTn, self._fullAccess):
            #if self._avoidLiterature and subtype == 'Literature':
            
            if subtype[0] in ['.','_']:
                continue

            newTn = curTn + [subtype]

            doBreak = False
            for subTn in self.yielder(newTn, level=level+1):
                yield subTn

        if self._includeParentTrack or level > 0:
            if ProcTrackOptions.isValidTrack(self._genome, curTn, self._fullAccess):
                yield curTn
