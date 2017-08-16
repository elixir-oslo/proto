import ast
import copy
import datetime
import os
import os.path
from collections import namedtuple

import third_party.safeshelve as safeshelve
from config.Config import DATA_FILES_PATH
from gold.track.TrackFormat import TrackFormatReq
from gold.util.CommonFunctions import strWithStdFormatting
from gold.util.CustomExceptions import ShouldNotOccurError
from proto.hyperbrowser.HtmlCore import HtmlCore
from proto.hyperbrowser.StaticFile import StaticImage

FieldInfo = namedtuple('FieldInfo', ['fullName', 'guiElementType'])

def constructKey(genome, trackName):
    key = ':'.join([genome] + trackName)
    if isinstance(key, unicode):
        key = str(key)
    assert type(key) == str, 'Non-str key: ' + key + ' of type: ' + str(type(key)) + '. Specific types: ' + str([type(x) for x in [genome] + trackName])
    return key

class TrackInfo(object):
    SHELVE_FN = DATA_FILES_PATH + os.sep + 'TrackInfo.shelve'

    PROTOCOL = 0

    FIELD_INFO_DICT = { \
        'description': FieldInfo('Description', 'textbox'), \
        'displayConvConf': FieldInfo('Display conventions and configuration', 'textbox'), \
        'methods': FieldInfo('Methods', 'textbox'), \
        'credits': FieldInfo('Credits', 'textbox'), \
        'reference': FieldInfo('References', 'textbox'), \
        'restrictions': FieldInfo('Data release policy', 'textbox'), \
        'version': FieldInfo('Version', 'textbox'), \
        'quality': FieldInfo('Quality', 'textbox'), \
        'hbContact': FieldInfo('HyperBrowser contact', 'textbox'), \
        'cellTypeSpecific': FieldInfo('Cell type specific', 'checkbox'), \
        'cellType': FieldInfo('Cell type', 'textbox'), \
        'private': FieldInfo('Private (our group only)', 'checkbox'), \
        'fileType': FieldInfo('File type', 'text'), \
        'trackFormatName': FieldInfo('Original track type', 'text'), \
        'markType': FieldInfo('Value type', 'text'), \
        'weightType': FieldInfo('Edge weight type', 'text'), \
        'undirectedEdges': FieldInfo('Undirected edges', 'text'), \
        'origElCount': FieldInfo('Original element count', 'text'), \
        'clusteredElCount': FieldInfo('Element count after merging', 'text'), \
        'numValCategories': FieldInfo('Original number of value categories', 'text'), \
        'numClusteredValCategories': FieldInfo('Number of value categories after clustering', 'text'), \
        'numEdgeWeightCategories': FieldInfo('Number of edge categories', 'text'), \
        'subTrackCount': FieldInfo('Total number of tracks (with subtracks)', 'text'), \
        'timeOfPreProcessing': FieldInfo('Time of preprocessing', 'text'), \
        'timeOfLastUpdate': FieldInfo('Time of last update', 'text'), \
        'lastUpdatedBy': FieldInfo('Last update by', 'text')}

    def __new__(cls, genome, trackName):
        trackInfoShelve = safeshelve.open(cls.SHELVE_FN, 'c', protocol=cls.PROTOCOL)
        stored = trackInfoShelve.get( constructKey(genome, trackName) )
        trackInfoShelve.close()
        if stored is not None:
            return stored
        else:
            return object.__new__(cls)

    def __init__(self, genome, trackName):
        existingAttrs = copy.copy(self.__dict__)
        assert existingAttrs.get('trackName') in [None, trackName], '%s not in [None, %s]' % (existingAttrs.get('trackName'), trackName) #An exception could here occur if there is a preprocessed directory that contains colon in its name, as this may lead to splitting some place and not splitting other places..
        assert existingAttrs.get('genome') in [None, genome], '%s not in [None, %s]' % (existingAttrs.get('genome'), genome)
        self.trackName = trackName
        self.genome = genome

        self.id = None

        self.description = ''
        self.displayConvConf = ''
        self.methods = ''
        self.credits = ''
        self.reference = ''
        self.restrictions = ''
        self.version = ''
        self.quality = ''
        self.hbContact = ''
        self.cellTypeSpecific = False
        self.cellType = ''

        self.private = False

        self.lastUpdatedBy = ''
        self.timeOfLastUpdate = None

        #self.header = ''
        self.fileType = ''
        self.trackFormatName = ''
        self.markType = ''
        self.weightType = ''
        self.undirectedEdges = None
        self.subTrackCount = None
        self.origElCount = None
        self.clusteredElCount = None
        self.numValCategories = None
        self.numClusteredValCategories = None
        self.numEdgeWeightCategories = None
        self.timeOfPreProcessing = None
        self.preProcVersion = ''

        self.__dict__.update(existingAttrs)

    @staticmethod
    def createInstanceFromKey(key):
        key = key.split(':')
        return TrackInfo(key[0], key[1:])

    @staticmethod
    def createInstanceAsCopyOfOther(genome, trackName, otherTrackName):
        ti = TrackInfo(genome, otherTrackName)
        ti.trackName = trackName
        return ti

    @staticmethod
    def createInstanceFromAttrsFromStrRepr(genome, strReprOfAttrDict):
        attrDict = ast.literal_eval(strReprOfAttrDict)
        trackName = attrDict['trackName']
        ti = TrackInfo(genome, trackName)
        ti.__dict__.update(attrDict)
        return ti

    def isValid(self, fullAccess=True):
        return (fullAccess or not self.private) and \
                self.timeOfPreProcessing is not None

    def resetTimeOfPreProcessing(self):
        self.timeOfPreProcessing = None
        self.store()

    def store(self):
        trackInfoShelve = safeshelve.open(self.SHELVE_FN, protocol=self.PROTOCOL)
        trackInfoShelve[ constructKey(self.genome, self.trackName) ] = self
        trackInfoShelve.close()

    def removeEntryFromShelve(self):
        trackInfoShelve = safeshelve.open(self.SHELVE_FN, protocol=self.PROTOCOL)
        key = constructKey(self.genome, self.trackName)
        if key in trackInfoShelve:
            del trackInfoShelve[key]
        trackInfoShelve.close()

    def __str__(self):
        return self.allInfo(printEmpty=True)

    def _isDenseTrack(self):
        try:
            return TrackFormatReq(name=self.trackFormatName).isDense()
        except:
            return False

    def _getFieldInfoDict(self, field, isDense):
        if field == 'clusteredElCount' and isDense:
            return self.FIELD_INFO_DICT['origElCount']

        if field == 'numClusteredValCategories' and isDense:
            return self.FIELD_INFO_DICT['numValCategories']

        return self.FIELD_INFO_DICT[field]

    def _addDescriptionLineIfTrue(self, core, isDense, printEmpty, field, expression, formatFunc=lambda x: str(x)):
        if printEmpty or expression:
            core.descriptionLine(self._getFieldInfoDict(field, isDense).fullName, formatFunc(getattr(self, field)))

    def _addTrackTypeIllustration(self, core, trackFormatName):
        tfAbbrev = ''.join([x[0] for x in trackFormatName.split()]).upper()
        core.image(StaticImage(['illustrations','%s.png' % tfAbbrev]).getURL(), \
                   style='width: 300px')

    def allInfo(self, printEmpty=False):
        core = HtmlCore()
        isDense = self._isDenseTrack()

        self._addDescriptionLineIfTrue(core, isDense, printEmpty, 'subTrackCount', \
            self.subTrackCount and (self.subTrackCount > 1 or not self.isValid()))
        self._addDescriptionLineIfTrue(core, isDense, printEmpty, 'origElCount', self.origElCount, \
            lambda x: strWithStdFormatting(x))
        self._addDescriptionLineIfTrue(core, isDense, printEmpty, 'clusteredElCount', self.clusteredElCount, \
            lambda x: strWithStdFormatting(x))
        self._addDescriptionLineIfTrue(core, isDense, printEmpty, 'numValCategories', self.numValCategories, \
            lambda x: strWithStdFormatting(x))
        self._addDescriptionLineIfTrue(core, isDense, printEmpty, 'numClusteredValCategories', self.numClusteredValCategories, \
            lambda x: strWithStdFormatting(x))
        self._addDescriptionLineIfTrue(core, isDense, printEmpty, 'numEdgeWeightCategories', self.numEdgeWeightCategories, \
            lambda x: strWithStdFormatting(x))

        self._addTrackTypeIllustration(core, self.trackFormatName)

        return self.mainInfo(printEmpty) + unicode(core)

    def mainInfo(self, printEmpty=False):
        core = HtmlCore()
        isDense = self._isDenseTrack()

        self._addDescriptionLineIfTrue(core, isDense, printEmpty, 'description', self.description)
        self._addDescriptionLineIfTrue(core, isDense, printEmpty, 'displayConvConf', self.displayConvConf)
        self._addDescriptionLineIfTrue(core, isDense, printEmpty, 'methods', self.methods)
        self._addDescriptionLineIfTrue(core, isDense, printEmpty, 'credits', self.credits)
        self._addDescriptionLineIfTrue(core, isDense, printEmpty, 'reference', self.reference, \
            lambda x: str( HtmlCore().link(x, x, True) ) if x.startswith('http://') else x)
        self._addDescriptionLineIfTrue(core, isDense, printEmpty, 'restrictions', self.restrictions)
        self._addDescriptionLineIfTrue(core, isDense, printEmpty, 'version', self.version)
        self._addDescriptionLineIfTrue(core, isDense, printEmpty, 'quality', self.quality)
        self._addDescriptionLineIfTrue(core, isDense, printEmpty, 'cellType', \
            self.cellTypeSpecific and self.cellType)
        self._addDescriptionLineIfTrue(core, isDense, printEmpty, 'hbContact', self.hbContact)
        self._addDescriptionLineIfTrue(core, isDense, printEmpty, 'trackFormatName', True)
        self._addDescriptionLineIfTrue(core, isDense, printEmpty, 'markType', self.markType)
        self._addDescriptionLineIfTrue(core, isDense, printEmpty, 'weightType', self.weightType)
        self._addDescriptionLineIfTrue(core, isDense, printEmpty, 'undirectedEdges', \
            self.undirectedEdges is not None and 'linked' in self.trackFormatName.lower())

        return unicode(core)

    def getUIRepr(self):
        uiRepr = []
        isDense = self._isDenseTrack()
        for field in ['description', 'displayConvConf', 'methods', 'credits', 'reference', 'restrictions', \
                      'version', 'quality', 'hbContact', 'cellTypeSpecific', 'cellType', \
                      'private', 'fileType', 'trackFormatName', 'markType', 'weightType', 'undirectedEdges', \
                      'origElCount', 'clusteredElCount', 'numValCategories', 'numClusteredValCategories', \
                      'numEdgeWeightCategories', 'subTrackCount', 'timeOfPreProcessing', 'timeOfLastUpdate', \
                      'lastUpdatedBy']:
            fieldInfo = self._getFieldInfoDict(field, isDense)
            uiRepr.append((fieldInfo.fullName, field, getattr(self, field), fieldInfo.guiElementType))
        return tuple(uiRepr)

    def getStrReprOfAttrDict(self):
        attrs =  [attr for attr in dir(self) \
                  if not callable(getattr(self, attr)) and not attr.startswith("__")]
        return repr( dict([(attr, getattr(self, attr)) for attr in attrs]) )


    def setAttrs(self, attrDict, username):
        self.__dict__.update(attrDict)
        self.lastUpdatedBy = username
        self.timeOfLastUpdate = datetime.datetime.now()

    @staticmethod
    def constructIdFromPath(genome, origPath, geSourceVersion, preProcVersion):
        if os.path.isdir(origPath):
            fileList = sorted([fn for fn in os.listdir(origPath) if os.path.isfile(origPath+os.sep+fn) and fn[0]!='.'])
        elif os.path.isfile(origPath):
            fileList = [os.path.basename(origPath)]
            origPath = os.path.dirname(origPath)
        else:
            raise ShouldNotOccurError

        fileInfo = tuple([ (fn, os.stat(os.sep.join([origPath, fn])).st_mtime ) for fn in fileList ])
        return hash( (hash(fileInfo), geSourceVersion, preProcVersion) )

    @staticmethod
    def constructIdByTimeStamp():
        return hash(datetime.datetime.now())

    @classmethod
    def getFilteredEntriesFromShelve(cls, genome, trackNameFilter):
        filterKey = constructKey(genome, trackNameFilter)
        trackInfoShelve = safeshelve.open(cls.SHELVE_FN, 'r', protocol=cls.PROTOCOL)
        filteredKeys = [x for x in trackInfoShelve.keys() if x.startswith(filterKey)]
        trackInfoShelve.close()
        return filteredKeys

    @classmethod
    def removeFilteredEntriesFromShelve(cls, genome, trackNameFilter):
        filteredKeys = TrackInfo.getFilteredEntriesFromShelve(genome, trackNameFilter)
        trackInfoShelve = safeshelve.open(cls.SHELVE_FN, 'w', protocol=cls.PROTOCOL)
        for key in filteredKeys:
            del trackInfoShelve[key]
        trackInfoShelve.close()

    @classmethod
    def updateShelveItemsAndCopyToNewFile(cls, updateHg18=False, removeDanglingItems=False):
        from quick.util.CommonFunctions import getUniqueFileName
        from config.Config import LOG_PATH
        from quick.application.ProcTrackOptions import ProcTrackOptions

        SHELVE_COPY_FN = DATA_FILES_PATH + os.sep + 'TrackInfo.shelve.copy'
        SHELVE_NEW_FN = DATA_FILES_PATH + os.sep + 'TrackInfo.shelve.new'
        SHELVE_ERRORS_FN = DATA_FILES_PATH + os.sep + 'TrackInfo.shelve.errors'
        SHELVE_KEYS_FN = DATA_FILES_PATH + os.sep + 'TrackInfo.shelve.new.keys'

        shelveNewFn = getUniqueFileName(SHELVE_NEW_FN)
        shelveErrorsFn = getUniqueFileName(SHELVE_ERRORS_FN)

        shelveCopyFn = SHELVE_COPY_FN
        shelveKeysFn = SHELVE_KEYS_FN

        logFn = os.path.join(LOG_PATH, 'TrackInfoCleanup.log')
        with open(logFn, 'w+') as logFile:
            import shutil

            trackInfoShelveNew = safeshelve.open(shelveNewFn, 'c', protocol=cls.PROTOCOL)
            trackInfoShelveErrors = safeshelve.open(shelveErrorsFn, 'c', protocol=cls.PROTOCOL)

            if not os.path.exists(shelveKeysFn):
                with open(shelveKeysFn, 'w') as keysFile:
                    assert not os.path.exists(shelveCopyFn)

                    shutil.copyfile(cls.SHELVE_FN, shelveCopyFn)
                    trackInfoShelve = safeshelve.open(shelveCopyFn, 'r', protocol=cls.PROTOCOL)

                    for key in trackInfoShelve.keys():
                        keysFile.write(key + os.linesep)

                    trackInfoShelve.close()

            with open(shelveKeysFn) as keysFile:
                keys = [line[:-1] for line in keysFile]

            for i,key in enumerate(keys):
                trackInfoShelve = safeshelve.open(shelveCopyFn, 'r', protocol=cls.PROTOCOL)

                try:
                    ti = trackInfoShelve[key]

                    if removeDanglingItems:
                        if not ti.isValid():
                            raise Exception('Track not valid')

                        #if not any( os.path.exists(createDirPath(ti.trackName, ti.genome, allowOverlaps=allowOverlaps))
                                    #for allowOverlaps in [False, True] ):
                        if not ti.genome in ['ModelsForExternalTracks']:
                            if not ProcTrackOptions._hasPreprocessedFiles(ti.genome, ti.trackName):
                                raise Exception('Preprocessed data does not exist')

                    if updateHg18 and (ti.genome == 'NCBI36' or 'NCBI36' in key):
                        ti.genome = 'hg18'
                        key = key.replace('NCBI36', 'hg18')

                    trackInfoShelveNew[key] = ti

                except Exception, e:
                    logFile.write('%s: %s' % (e, key) + os.linesep)
                    trackInfoShelveErrors[key] = ti

                if i%10000 == 0:
                    print '.',

            trackInfoShelve.close()
            trackInfoShelveNew.close()
            trackInfoShelveErrors.close()
