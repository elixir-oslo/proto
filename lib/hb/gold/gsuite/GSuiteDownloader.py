import os

from gold.gsuite.GSuiteConstants import REMOTE, COMPRESSION_SUFFIXES, \
                                        OPTIONAL_STD_COL_NAMES, OPTIONAL_STD_COL_SPECS
from gold.gsuite.GSuiteRequirements import GSuiteRequirements
from gold.gsuite.GSuiteTrack import GSuiteTrack, GalaxyGSuiteTrack
from gold.gsuite.GSuiteAllTracksVisitor import GSuiteAllTracksVisitor
from gold.gsuite.GSuiteFunctions import getTitleAndSuffixWithCompressionSuffixesRemoved, \
                                    getTitleWithCompressionSuffixesRemoved, \
                                    getDuplicateIdx, renameBaseFileNameWithDuplicateIdx
from gold.util.CustomExceptions import ShouldNotOccurError, InvalidFormatError
from quick.util.CommonFunctions import ensurePathExists
from third_party.Visitor import Visitor

# Classes

class GSuiteMultipleGalaxyFnDownloader(GSuiteAllTracksVisitor):
    def __init__(self):
        GSuiteAllTracksVisitor.__init__(self, GSuiteTrackExclusiveGalaxyFnDownloader())

class GSuiteSingleGalaxyFnDownloader(GSuiteAllTracksVisitor):
    def __init__(self):
        GSuiteAllTracksVisitor.__init__(self, GSuiteTrackSharedGalaxyFnDownloader())

class GSuiteTrackDownloader(Visitor):
    def genericVisit(self, gSuiteTrack, *args, **kwArgs):
        gSuiteReq = GSuiteRequirements(allowedLocations=[REMOTE])
        gSuiteReq.check(gSuiteTrack)


class GSuiteTrackBasicDownloader(GSuiteTrackDownloader):
    def visitFtpGSuiteTrack(self, gSuiteTrack, outFileName):
        import ftplib

        try:
            conn = ftplib.FTP(gSuiteTrack.netloc)
            conn.login('anonymous')
            out = open(outFileName, 'w')
            conn.retrbinary('RETR ' + gSuiteTrack.path, out.write, 1024)
        except Exception, exc:
            print 'Exception: '
            print exc
        finally:
            conn.quit()
            out.flush()

    def visitHttpGSuiteTrack(self, gSuiteTrack, outFileName):
        import urllib2
        response = urllib2.urlopen(gSuiteTrack.uriWithoutSuffix)
        data = response.read()
        out = open(outFileName, 'w')
        out.write(data)
        out.close()

    def visitRsyncGSuiteTrack(self, gSuiteTrack, outFileName):
        import sys
        import subprocess
        subprocess.check_call(['rsync', '-a', '-P', \
                                gSuiteTrack.uriWithoutSuffix, outFileName], \
                                stderr=sys.stdout)

class GSuiteTrackUncompressorAndDownloader(GSuiteTrackDownloader):
    def visitFtpGSuiteTrack(self, gSuiteTrack, outFileName):
        self._downloadToFileAndUncompress(gSuiteTrack, outFileName)

    def visitHttpGSuiteTrack(self, gSuiteTrack, outFileName):
        self._downloadToFileAndUncompress(gSuiteTrack, outFileName)

    def visitRsyncGSuiteTrack(self, gSuiteTrack, outFileName):
        self._downloadToFileAndUncompress(gSuiteTrack, outFileName)

    def _downloadToFileAndUncompress(self, gSuiteTrack, outFileName):
        import tempfile
        tmpSuffix='.' + gSuiteTrack.suffix if gSuiteTrack.suffix else ''
        tmpFile = tempfile.NamedTemporaryFile(delete = False, suffix=tmpSuffix)

        gSuiteTrackDownloader = GSuiteTrackBasicDownloader()
        gSuiteTrackDownloader.visit(gSuiteTrack, tmpFile.name)

        self._uncompressTemporaryFile(gSuiteTrack, tmpFile.name, outFileName)

    def _uncompressTemporaryFile(self, gSuiteTrack, tmpFileName, outFileName):
        import subprocess
        import os, sys, shutil

        for compSuffix in COMPRESSION_SUFFIXES:
            reduceLen = len(compSuffix)+1

            suffix = gSuiteTrack.suffix
            if suffix and (suffix == compSuffix or
                           suffix.lower().endswith('.' + compSuffix)):
                if compSuffix == 'gz':
                    subprocess.check_call(['gunzip', tmpFileName], stderr=sys.stdout)

                    unzippedFileName = tmpFileName[:-reduceLen]

                    ensurePathExists(outFileName)
                    #os.rename(unzippedFileName, outFileName)
                    shutil.move(unzippedFileName, outFileName)
                else:
                    raise ShouldNotOccurError
                break
        else:
            #os.rename(tmpFileName, outFileName)
            shutil.move(tmpFileName, outFileName)

        currentUmask = os.umask(0)
        os.umask(currentUmask)
        os.chmod(outFileName, 0o666 - currentUmask)


class GSuiteCachedTrackDownloader(GSuiteTrackDownloader):
    def _getUriForDownloadedAndUncompressedTrackPossiblyCached(self, gSuiteTrack, galaxyFn, uncomprSuffix, extraFileName=None):
        from gold.gsuite.GSuiteTrackCache import GSUITE_TRACK_CACHE
        cache = GSUITE_TRACK_CACHE

        if cache.isCached(gSuiteTrack):
            cachedUri = cache.getCachedGalaxyUri(gSuiteTrack)
            if os.path.exists(GSuiteTrack(cachedUri).path):
                return cache.getCachedGalaxyUri(gSuiteTrack)

        if extraFileName:
            from quick.application.ExternalTrackManager import ExternalTrackManager
            outGalaxyFn = ExternalTrackManager.createGalaxyFilesFn(galaxyFn, extraFileName)
            ensurePathExists(outGalaxyFn)
            if extraFileName.endswith('.' + uncomprSuffix):
                uri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn, extraFileName=extraFileName)
            else:
                uri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn, extraFileName=extraFileName, suffix=uncomprSuffix)
        else:
            outGalaxyFn = galaxyFn
            uri = GalaxyGSuiteTrack.generateURI(galaxyFn=outGalaxyFn, suffix=uncomprSuffix)

        uncompressorAndDownloader = GSuiteTrackUncompressorAndDownloader()
        uncompressorAndDownloader.visit(gSuiteTrack, outGalaxyFn)

        if cache.shouldBeCached(gSuiteTrack):
            cache.cache(gSuiteTrack, uri)

        return uri


class GSuiteTrackExclusiveGalaxyFnDownloader(GSuiteCachedTrackDownloader):
    def visitRemoteGSuiteTrack(self, gSuiteTrack, uncomprTitleToGalaxyFnDict):
        self.genericVisit(gSuiteTrack, uncomprTitleToGalaxyFnDict)

        uncomprTitle, uncomprSuffix = getTitleAndSuffixWithCompressionSuffixesRemoved(gSuiteTrack)
        outGalaxyFn = uncomprTitleToGalaxyFnDict[uncomprTitle]

        uri = self._getUriForDownloadedAndUncompressedTrackPossiblyCached(gSuiteTrack, outGalaxyFn, uncomprSuffix)
        return GSuiteTrack(uri, title=uncomprTitle, fileFormat=gSuiteTrack.fileFormat,
                           trackType=gSuiteTrack.trackType, genome=gSuiteTrack.genome,
                           attributes=gSuiteTrack.attributes)


class GSuiteTrackSharedGalaxyFnDownloader(GSuiteCachedTrackDownloader):
    def genericVisit(self, gSuiteTrack, galaxyFn, colHierarchyList):
        gSuiteReq = GSuiteRequirements(allowedLocations=[REMOTE])
        gSuiteReq.check(gSuiteTrack)

        allowedCols = OPTIONAL_STD_COL_NAMES + gSuiteTrack.attributes.keys()
        for col in colHierarchyList:
            if col not in allowedCols:
                raise InvalidFormatError('Column "%s" not found: %s' % (col, allowedCols))

    def visitRemoteGSuiteTrack(self, gSuiteTrack, galaxyFn, colHierarchyList):
        import os
        self.genericVisit(gSuiteTrack, galaxyFn, colHierarchyList)

        uncomprTitle, uncomprSuffix = getTitleAndSuffixWithCompressionSuffixesRemoved(gSuiteTrack)
        rawFileName = getTitleWithCompressionSuffixesRemoved( GSuiteTrack(gSuiteTrack.uri) )

        duplicateIdx = getDuplicateIdx(uncomprTitle)
        rawFileName = renameBaseFileNameWithDuplicateIdx(rawFileName, duplicateIdx)

        memberHierarchyList = []
        for colName in colHierarchyList:
            memberName = colName

            for colSpec in OPTIONAL_STD_COL_SPECS:
                if not colSpec.deprecated:
                    if colName == colSpec.colName:
                        memberName = colSpec.memberName

            memberHierarchyList.append(memberName)

        extraFileName = os.path.sep.join([getattr(gSuiteTrack, memberName) for memberName in memberHierarchyList] +
                                         [rawFileName])

        uri = self._getUriForDownloadedAndUncompressedTrackPossiblyCached(gSuiteTrack, galaxyFn,
                                                                          uncomprSuffix, extraFileName)
        return GSuiteTrack(uri, title=uncomprTitle, fileFormat=gSuiteTrack.fileFormat,
                           trackType=gSuiteTrack.trackType, genome=gSuiteTrack.genome,
                           attributes=gSuiteTrack.attributes)
