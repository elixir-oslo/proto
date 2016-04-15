# Copyright (C) 2009, Geir Kjetil Sandve, Sveinung Gundersen and Morten Johansen
# This file is part of The Genomic HyperBrowser.
#
#    The Genomic HyperBrowser is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    The Genomic HyperBrowser is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with The Genomic HyperBrowser.  If not, see <http://www.gnu.org/licenses/>.

#from quick.application.ExternalTrackManager import ExternalTrackManager
#import os.path
import os
import re
from config.Config import DEFAULT_GENOME, URL_PREFIX
from gold.description.TrackInfo import TrackInfo
from gold.track.TrackFormat import TrackFormat
from gold.util.CommonFunctions import createDirPath, getClassName
from gold.util.CustomExceptions import ShouldNotOccurError, InvalidFormatError
from gold.application.DataTypes import getSupportedFileSuffixes
from quick.util.GenomeInfo import GenomeInfo
from quick.util.CommonFunctions import extractIdFromGalaxyFn as commonExtractIdFromGalaxyFn
from quick.application.SignatureDevianceLogging import takes,returns

class ExternalTrackManager:
    '''
    Handles external track names. These are of three types:

    ['external','...']: ExternalTN. Handled basically just as a standard
        trackname. Only particularity is that the top category 'external' is not
        shown explicitly to users for track selection in HyperBrowser (is
        hidden).. Is of structure ['external'] + [URL_PREFIX] + id + [name],
        where id can be a list of length>1 (typically 2, due to codings from
        galaxy id..)

    ['galaxy','...']: GalaxyTN. An especially coded TN, used mainly to process
        files from galaxy history, but can also be used otherwise. Structure is:
        ['galaxy', fileEnding, origformatTrackFn, name] First element used for
        assertion, second element to determine origformat (as galaxy force
        ending .dat) origformatTrackFn is the file name to the data source for
        track data to be preprocessed. Typically ends with
        'XXX/dataset_YYYY.dat'. XXX and YYYY are numbers which are extracted and
        used as id in the form [XXX, YYYY] The last element is the name of the
        track, only used for presentation purposes.

    ['virtual','...'] VirtualMinimalTN. An especially coded TN, used for
        minimal runs of all statistics in order to display the analyses fitting
        for the selection of tracks in the user interface. The virtual track
        reads one data line of the original track file, and creates a virtual
        trackview based on the contents (VirtualMinimalTrack). Has the same
        syntax as GalaxyTN, apart from the first element, which is 'virtual'
        instead of 'galaxy'.

    ['redirect','...'] RedirectTN. An especially coded TN, used for redirecting
        minimal runs toward one of the preprocessed tracks under the genome
        'ModelsForExternalTracks'. The structure is [ 'redirect', genome, chr,
        description ] + trackName of the track to redirect to. This is used
        instead of the external track, which then does not need to have an
        associated original data file. Is handled by the createDirPath function
        in CommonFunctions.
    '''

    @staticmethod
    def isHistoryTrack(tn):
        return ExternalTrackManager.isExternalTrack(tn) or ExternalTrackManager.isGalaxyTrack(tn) \
            or ExternalTrackManager.isVirtualTrack(tn) or ExternalTrackManager.isRedirectTrack(tn)

    @staticmethod
    def isExternalTrack(tn):
        return (tn is not None and len(tn)>0 and tn[0].lower() == 'external')

    @staticmethod
    #@takes(list)
    def isGalaxyTrack(tn):
        return (tn is not None and len(tn)>0 and tn[0].lower() == 'galaxy')

    @staticmethod
    def isVirtualTrack(tn):
        return (tn is not None and len(tn)>0 and tn[0].lower() == 'virtual')

    @staticmethod
    def isRedirectTrack(tn):
        return (tn is not None and len(tn)>0 and tn[0]=='redirect')

    @staticmethod
    def constructVirtualTrackNameFromGalaxyTN(galaxyTN):
        return ['virtual'] + galaxyTN[1:]

    @staticmethod
    def constructRedirectTrackName(trackName, genome, chr, description):
        return [ 'redirect', genome, chr, description ] + trackName

    @staticmethod
    def extractIdFromGalaxyFn(fn):
        return commonExtractIdFromGalaxyFn(fn)

    @classmethod
    def getEncodedDatasetIdFromGalaxyFn(cls, galaxyFn):
        plainId = ExternalTrackManager.extractIdFromGalaxyFn(galaxyFn)[1]
        return cls.getEncodedDatasetIdFromPlainGalaxyId(plainId)

    @staticmethod
    def getEncodedDatasetIdFromPlainGalaxyId(plainId):
        from quick.util.CommonFunctions import galaxySecureEncodeId
        return galaxySecureEncodeId(plainId)

    @staticmethod
    def getGalaxyFnFromEncodedDatasetId(encodedId):
        from quick.util.CommonFunctions import galaxySecureDecodeId, \
                                               getGalaxyFnFromDatasetId

        plainId = galaxySecureDecodeId(encodedId)
        return getGalaxyFnFromDatasetId(plainId)

    @staticmethod
    def getGalaxyFilesDir(galaxyFn):
        return galaxyFn[:-4] + '_files'

    '''
    id is the relative file hierarchy, encoded as a list of strings
    '''
    @classmethod
    def getGalaxyFilesFilename(cls, galaxyFn, id):
        return os.path.sep.join([cls.getGalaxyFilesDir(galaxyFn)] + id)

    @staticmethod
    def getGalaxyFilesFnFromEncodedDatasetId(encodedId):
        galaxyFn = ExternalTrackManager.getGalaxyFnFromEncodedDatasetId(encodedId)
        return ExternalTrackManager.getGalaxyFilesDir(galaxyFn)

    @staticmethod
    def createGalaxyFilesFn(galaxyFn, filename):
        return os.path.sep.join([ExternalTrackManager.getGalaxyFilesDir(galaxyFn), filename])

    @staticmethod
    def extractFnFromGalaxyTN(galaxyTN):
        return galaxyTN[2] if type(galaxyTN) == list else galaxyTN.split(':')[2]

    @staticmethod
    def extractNameFromHistoryTN(galaxyTN):
        if isinstance(galaxyTN, str):
            galaxyTN = galaxyTN.split(':')
        
        assert ExternalTrackManager.isHistoryTrack(galaxyTN)
        from urllib import unquote
        if ExternalTrackManager.isExternalTrack(galaxyTN):
            return unquote(galaxyTN[-1])
        else:
            return unquote(galaxyTN[3])

    @staticmethod
    def extractFileSuffixFromGalaxyTN(galaxyTN, allowUnsupportedSuffixes=False):
        if type(galaxyTN) == str:
            galaxyTN = galaxyTN.split(':')
        suffix = galaxyTN[1]
        if not allowUnsupportedSuffixes and not suffix.lower() in getSupportedFileSuffixes():
            raise ShouldNotOccurError('File type "' + suffix + '" is not supported.')
        return suffix

    @staticmethod
    def createSelectValueFromGalaxyTN(galaxyTN):
        assert(galaxyTN[0].lower() == 'galaxy')
        return ','.join(['galaxy',\
                        ExternalTrackManager.extractIdFromGalaxyFn\
                         (ExternalTrackManager.extractFnFromGalaxyTN(galaxyTN))[1],\
                        ExternalTrackManager.extractFileSuffixFromGalaxyTN(galaxyTN),\
                        ExternalTrackManager.extractNameFromHistoryTN(galaxyTN)])

    @classmethod
    def getStdTrackNameFromGalaxyTN(cls, galaxyTN, allowUnsupportedSuffixes=False):
        if type(galaxyTN) == str:
            galaxyTN = galaxyTN.split(':')

        assert galaxyTN[0].lower() == 'galaxy'
        if not allowUnsupportedSuffixes and not galaxyTN[1].lower() in getSupportedFileSuffixes():
            raise InvalidFormatError('File type "%s" is not supported.' % galaxyTN[1].lower())

        fn = cls.extractFnFromGalaxyTN(galaxyTN)
        id = cls.extractIdFromGalaxyFn(fn)
        name = galaxyTN[-1]
        return ExternalTrackManager.createStdTrackName(id, name)

    @classmethod
    def createStdTrackName(cls, id, name, subtype = ''):
        encodedId = cls.getEncodedDatasetIdFromPlainGalaxyId(id[1])
        urlPrefix = URL_PREFIX.replace(os.path.sep, '')
        #return ['external'] + ([urlPrefix] if urlPrefix != '' else []) + id + [name] + ([subtype] if subtype != '' else [])
        return ['external'] + ([urlPrefix] if urlPrefix != '' else []) + \
               [encodedId[:2], encodedId] + id[2:] + ([name] if name else []) + \
               ([subtype] if subtype != '' else [])

    @classmethod
    def renameExistingStdTrackIfNeeded(cls, genome, stdTrackName):
        oldTrackName = None
        for allowOverlaps in [False, True]:
            parentDir = createDirPath(stdTrackName[:-1], genome, allowOverlaps=allowOverlaps)
            if os.path.exists(parentDir):
                dirContents = os.listdir(parentDir)
                realDirs = [x for x in dirContents if os.path.isdir(os.path.join(parentDir, x))
                            and not os.path.islink(os.path.join(parentDir, x))]

                reqDirName = stdTrackName[-1]
                reqDirPath = os.path.join(parentDir, reqDirName)

                from gold.application.LogSetup import logMessage
                logMessage('Checking ' + reqDirPath)
                
                if os.path.islink(reqDirPath) and not os.path.isdir(os.readlink(reqDirPath)):
                    # This is to fix a bug that ended in the symlink pointing to a file
                    os.remove(reqDirPath)
                    logMessage('Removed ' + reqDirPath)

                if realDirs and reqDirName not in dirContents:
                    oldTrackName = stdTrackName[:-1] + [realDirs[0]]
                    os.symlink(realDirs[0], reqDirPath)

        if oldTrackName is not None:
            ti = TrackInfo(genome, oldTrackName)
            ti.trackName = stdTrackName
            ti.store()

    @staticmethod
    def getGESourceFromGalaxyOrVirtualTN(trackName, genome):
        fn = ExternalTrackManager.extractFnFromGalaxyTN(trackName)
        suffix = ExternalTrackManager.extractFileSuffixFromGalaxyTN(trackName)
        return ExternalTrackManager.getGESource(fn, suffix, genome=genome)

    @staticmethod
    def getGESource(fullFn, fileSuffix, extTrackName=None, genome=None, printWarnings=False):
        from gold.origdata.GenomeElementSource import GenomeElementSource
        return GenomeElementSource(fullFn, suffix=fileSuffix, forPreProcessor=True, genome=genome,
                                   trackName=extTrackName, external=True, printWarnings=printWarnings)

    @staticmethod
    def preProcess(fullFn, extTrackName, fileSuffix, genome, raiseIfAnyWarnings=False,
                   printProgress=True, mergeChrFolders=True):
        from gold.origdata.PreProcessTracksJob import PreProcessExternalTrackJob
        job = PreProcessExternalTrackJob(genome, fullFn, extTrackName, fileSuffix,
                                         printProgress=printProgress,
                                         raiseIfAnyWarnings=raiseIfAnyWarnings,
                                         mergeChrFolders=mergeChrFolders)
        return job.process()

    @classmethod
    def getPreProcessedTrackFromGalaxyTN(cls, genome, galaxyTN, printErrors=True, printProgress=True,
                                         raiseIfAnyWarnings=False, renameExistingTracksIfNeeded=True,
                                         mergeChrFolders=True):
        '''
        Takes a GalaxyTN as input, pre-processes the data that GalaxyTN refers to, and finally returns
        an ExternalTN that refers to the pre-processed data and can be used as a normal track name.
        '''
        from gold.util.CommonFunctions import replaceIllegalElementsInTrackNames
        stdTrackName = cls.getStdTrackNameFromGalaxyTN(galaxyTN, allowUnsupportedSuffixes=True)
        legalTrackName = [replaceIllegalElementsInTrackNames(part) for part in stdTrackName]

        if renameExistingTracksIfNeeded:
            cls.renameExistingStdTrackIfNeeded(genome, legalTrackName)
        fn = cls.extractFnFromGalaxyTN(galaxyTN)
        fileSuffix = cls.extractFileSuffixFromGalaxyTN(galaxyTN, allowUnsupportedSuffixes=True)

        if printProgress:
            print 'Preprocessing external track...<br><pre>'

        try:
            if cls.preProcess(fn, legalTrackName, fileSuffix, genome,
                              printProgress=printProgress,
                              raiseIfAnyWarnings=raiseIfAnyWarnings,
                              mergeChrFolders=mergeChrFolders):
                if printProgress:
                    print '</pre>Finished preprocessing.<br>'
            else:
                if printProgress:
                    print '</pre>Already preprocessed, continuing...<br>'
        #except IOError:
        #    print '</pre>Already preprocessed, continuing...<br>'
        except Exception as e:
            if printErrors:
                print '</pre>An error occured during preprocessing: ', getClassName(e) + ':', e, '<br>'
            raise
        #else:
        #    print '</pre>Finished preprocessing.<br>'
        return legalTrackName

    @classmethod
    def constructGalaxyTnFromSuitedFn(cls, fn, fileEnding=None,name=''):
        #to check that valid ID can later be constructed
        cls.extractIdFromGalaxyFn(fn)

        if fileEnding is None:
            fileEnding = fn.split('.')[-1]
        return ['galaxy', fileEnding, fn, name]
