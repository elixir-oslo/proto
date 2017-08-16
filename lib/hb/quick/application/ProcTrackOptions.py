import os
from gold.util.CommonFunctions import createDirPath
from gold.description.TrackInfo import TrackInfo
from gold.track.BoundingRegionShelve import isBoundingRegionFileName
from quick.util.CommonFunctions import smartStrLower
from quick.util.GenomeInfo import GenomeInfo

class ProcTrackOptions:
    @staticmethod
    def _getDirContents(genome, trackName):
        dirPath = createDirPath(trackName, genome)
#        print '<br>',"PATH: ", dirPath,'<br>'
        return os.listdir(dirPath) if os.path.exists(dirPath) else []

    @staticmethod
    def getSubtypes(genome, trackName, fullAccess=False):
        dirPath = createDirPath(trackName, genome)
        subtypes = [fn for fn in ProcTrackOptions._getDirContents(genome, trackName) \
                    if not (fn[0] in ['.','_'] or os.path.isfile(dirPath + os.sep + fn) \
                    or GenomeInfo.isValidChr(genome, fn))]

        #fixme, just temporarily:, these dirs should start with _
        subtypes= [x for x in subtypes if not x in ['external','ucsc'] ]

        if not fullAccess and not ProcTrackOptions._isLiteratureTrack(genome, trackName):
            subtypes = [x for x in subtypes if not TrackInfo(genome, trackName+[x]).private]

        return sorted(subtypes, key=smartStrLower)

    @staticmethod
    def _isLiteratureTrack(genome, trackName):
        return ':'.join(trackName).startswith( ':'.join(GenomeInfo.getPropertyTrackName(genome, 'literature')) )

    @staticmethod
    def _hasPreprocessedFiles(genome, trackName):
        for fn in ProcTrackOptions._getDirContents(genome, trackName):
            if GenomeInfo.isValidChr(genome, fn) or isBoundingRegionFileName(fn):
                return True

    @staticmethod
    def isValidTrack(genome, trackName, fullAccess=False):
        if not TrackInfo(genome, trackName).isValid(fullAccess):
            return False

        if ProcTrackOptions._hasPreprocessedFiles(genome, trackName):
            return True
        
        return  False
        #       len([fn for fn in ProcTrackOptions._getDirContents(genome, trackName) \
        #            if GenomeInfo.isValidChr(genome, fn) ]) > 0
