import os
import urlparse

from collections import OrderedDict
from urllib import quote, quote_plus, unquote, unquote_plus 
from config.Config import ALLOW_GSUITE_FILE_PROTOCOL
from gold.gsuite.GSuiteConstants import HEADER_VAR_DICT, LOCATION_HEADER, FILE_FORMAT_HEADER, \
                                        TRACK_TYPE_HEADER, GENOME_HEADER, LOCAL, REMOTE, TEXT, BINARY, \
                                        MULTIPLE, UNKNOWN, PREPROCESSED, PRIMARY, BTRACK_SUFFIX
from gold.util.CustomExceptions import InvalidFormatError, AbstractClassError, \
                                       NotSupportedError
from gold.util.CommonFunctions import getFileSuffix
from quick.application.SignatureDevianceLogging import takes, returns


_GSUITE_TRACK_REGISTRY = {}

def quoteParseResults(parseResults):
    scheme = parseResults.scheme
    netloc = quote(parseResults.netloc, safe='')
    path = quote(parseResults.path, safe='/')
    params = quote(parseResults.params, safe='')
    query = quote_plus(parseResults.query, safe='=&')
    fragment = quote(parseResults.fragment, safe='')

    return urlparse.ParseResult(scheme, netloc, path, params, query, fragment)


def unquoteParseResults(parseResults):
    scheme = parseResults.scheme
    netloc = unquote(parseResults.netloc)
    path = unquote(parseResults.path)
    params = unquote(parseResults.params)
    query = unquote_plus(parseResults.query)
    fragment = unquote(parseResults.fragment)

    return urlparse.ParseResult(scheme, netloc, path, params, query, fragment)


def unquoteQueryDict(queryDict):
    resQueryDict = {}

    for key,val in queryDict.iteritems():
        resQueryDict[unquote_plus(key)] = [unquote_plus(_) for _ in val]

    return resQueryDict


class GSuiteTrackFactory(type):
    def __call__(cls, uri, **kwArgs):

        if cls is GSuiteTrack:
            # This is probably not needed, as the scheme should not be quoted
            #if doUnquote:
                #uri = unquote(uri)
            scheme = urlparse.urlparse(uri).scheme

            if scheme == '':
                raise InvalidFormatError('GSuite track URI does not have a specified ' \
                                         'protocol. URI: ' + uri)

            if scheme not in _GSUITE_TRACK_REGISTRY:
                raise InvalidFormatError('Track protocol "%s" is not supported in ' % scheme +\
                                         'this version of the GSuite format')
            return _GSUITE_TRACK_REGISTRY[scheme](uri, **kwArgs)
        return type.__call__(cls, uri, **kwArgs)


class GSuiteTrack(object):
    '''
    Abstract superclass for all protocol-specific subclasses of GSuite tracks
    '''
    __metaclass__ = GSuiteTrackFactory

    SCHEME = None

    def __init__(self, uri, title=None, fileFormat=None, trackType=None, genome=None,
                 attributes=OrderedDict(), comment=None, doUnquote=True):
        self._doUnquote = doUnquote

        self._parsedUri = urlparse.urlparse(uri)
        if self._parsedUri.query:
            self._queryDict = urlparse.parse_qs(self._parsedUri.query, keep_blank_values=False, strict_parsing=True)

        if doUnquote:
            self._parsedUri = unquoteParseResults(self._parsedUri)
            if self._parsedUri.query:
                self._queryDict = unquoteQueryDict(self._queryDict)

        assert self._parsedUri.scheme == self.SCHEME, [self._parsedUri.scheme, self.SCHEME]
        if self._parsedUri.fragment != '':
            raise InvalidFormatError('Fragment part of URI is not allowed: "#%s"' % self._parsedUri.fragment)

        self.title = title
        self.fileFormat = fileFormat if fileFormat is not None else HEADER_VAR_DICT[FILE_FORMAT_HEADER].default
        self.trackType = trackType if trackType is not None else HEADER_VAR_DICT[TRACK_TYPE_HEADER].default
        self.genome = genome if genome is not None else HEADER_VAR_DICT[GENOME_HEADER].default
        self.attributes = attributes
        self.comment = comment

        self._init(uri=uri, title=title, fileFormat=fileFormat, trackType=trackType, genome=genome,
                   attributes=attributes, comment=comment, doUnquote=doUnquote)

    def _init(self, **kwArgs):
        if hasattr(super(GSuiteTrack, self), '_init'):
            super(GSuiteTrack, self)._init(**kwArgs)

    @property
    def uri(self):
        parsedUri = quoteParseResults(self._parsedUri) if self._doUnquote else self._parsedUri
        return parsedUri.geturl()

    @property
    def uriWithoutSuffix(self):
        from urlparse import ParseResult
        uriCopy = ParseResult(scheme=self._parsedUri.scheme,
                              netloc=self._parsedUri.netloc,
                              path=self._parsedUri.path,
                              params='',
                              query=self._parsedUri.query,
                              fragment='')
        uriCopy = quoteParseResults(uriCopy) if self._doUnquote else uriCopy
        return uriCopy.geturl()

    @property
    def scheme(self):
        return self.SCHEME

    @property
    def netloc(self):
        netloc = self._parsedUri.netloc
        if netloc:
            return netloc

    @property
    def path(self):
        path = self._parsedUri.path
        if path:
            return path

    @property
    def query(self):
        query = self._parsedUri.query
        if query:
            return query

    @property
    def trackName(self):
        if self._parsedUri.query:
            if 'track' in self._queryDict:
                if len(self._queryDict['track']) > 1:
                    raise InvalidFormatError('More than one "track=" clause is not allowed '
                                             'in the query of the URI: ' + self.uri)
                return self._queryDict['track'][0].split(':')

    @property
    def suffix(self):
        if self._parsedUri.params != '':
            return self._parsedUri.params
        else:
            if self.path is None:
                return None

            suffix = getFileSuffix(self.path)
            if suffix == '':
                return None
            return suffix

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title):
        self._title = title if title is not None else self._generateTitle()

    def _generateTitle(self):
        if self.trackName:
            return self.trackName[-1]
        else:
            return os.path.basename(self._parsedUri.path)

    @property
    def fileFormat(self):
        return self._fileFormat

    @fileFormat.setter
    def fileFormat(self, fileFormat):
        try:
            self._checkHeaderValAllowed(fileFormat, FILE_FORMAT_HEADER)
        except:
            if fileFormat == TEXT:
                fileFormat = PRIMARY
            elif fileFormat == BINARY:
                fileFormat = PREPROCESSED
            else:
                raise
        
        self._fileFormat = fileFormat

    @property
    def trackType(self):
        return self._trackType

    @trackType.setter
    def trackType(self, trackType):
        self._checkHeaderValAllowed(trackType, TRACK_TYPE_HEADER)
        self._trackType = trackType

    @property
    def genome(self):
        return self._genome

    @genome.setter
    def genome(self, genome):
        self._checkHeaderValAllowed(genome, GENOME_HEADER)
        self._genome = genome

    @property
    def location(self):
        return HEADER_VAR_DICT[LOCATION_HEADER].default

    @property
    def attributes(self):
        return self._attributes

    @attributes.setter
    def attributes(self, attributes):
        self._attributes = OrderedDict()
        
        for key,val in attributes.iteritems():
            if val is not None:
                if val == '':
                    raise InvalidFormatError('Empty attribute contents not allowed. '
                                             'Please use ".", the period character, to '
                                             'indicate missing values')

                if self._doUnquote:
                    val = unquote(val)
                self._attributes[key] = val

    @takes(str, str)
    def setAttribute(self, attrName, attrVal):
        self._attributes[attrName] = attrVal

    @takes(str)
    @returns(str)
    def getAttribute(self, attrName):
        if attrName in self._attributes:
            return self._attributes[attrName]

    def _checkHeaderValAllowed(self, param, header):
        if param is not None and param not in HEADER_VAR_DICT[header].allowed:
            raise InvalidFormatError('Header "%s" value is not allowed: "%s". ' % (header, param) +\
                                     'Allowed values: ' + ', '.join(HEADER_VAR_DICT[header].allowed))

    def __getattr__(self, item):
        try:
            return self.__dict__['_attributes'][item]
        except KeyError:
            raise AttributeError("Member '%s' not found in class '%s'" %
                                 (item, self.__class__.__name__))

    @classmethod
    def generateURI(cls):
        raise AbstractClassError


class RemoteGSuiteTrack(GSuiteTrack):
    def _init(self, **kwArgs):
        if self.netloc is None:
            raise InvalidFormatError('Track protocol "%s" requires the specification ' % self.SCHEME +\
                                     'of a host server, e.g. "%s://server.org/path/to/file".' % self.SCHEME)

        super(RemoteGSuiteTrack, self)._init(**kwArgs)

    @property
    def location(self):
        return REMOTE

    @classmethod
    def generateURI(cls, netloc='', path='', suffix='', query='', trackName=[], doQuote=False):
        if not query:
            if trackName:
                query = 'track=' + ':'.join(trackName)

        parseResult = urlparse.ParseResult(cls.SCHEME, netloc, path, suffix, query, '')

        if doQuote:
            parseResult = quoteParseResults(parseResult)

        return urlparse.urlunparse(parseResult)


class LocalGSuiteTrack(GSuiteTrack):
    # In order to set doUnquote to False for all local tracks
    #def __init__(self, uri, title=None, fileFormat=None, trackType=None, genome=None,
    #             attributes=OrderedDict(), comment=None, doUnquote=True):
    #    GSuiteTrack.__init__(self, uri, title=title, fileFormat=fileFormat, trackType=trackType,
    #                         genome=genome, attributes=attributes, comment=comment, doUnquote=False)

    def _init(self, **kwArgs):
        if not self._parsedUri.path.startswith('/'):
            raise InvalidFormatError('Track protocol "%s" requires the ' % self.SCHEME +\
                                     'path to start with the "/" character. Path: "%s"' % self._parsedUri.path)

        super(LocalGSuiteTrack, self)._init(**kwArgs)

    @property
    def location(self):
        return LOCAL


class SuffixDependentGSuiteTrack(GSuiteTrack):
    def _init(self, **kwArgs):
        oldFileFormat = self.fileFormat

        if self.suffix is None:
            self.fileFormat = UNKNOWN
        else:
            from gold.origdata.GenomeElementSource import getGenomeElementSourceClass
            try:
                getGenomeElementSourceClass(None, suffix=self.suffix)
                self.fileFormat = PRIMARY

            except NotSupportedError:
                try:
                    from gold.gsuite.GSuiteFunctions import \
                        getTitleAndSuffixWithCompressionSuffixesRemoved
                    uncomprSuffix = getTitleAndSuffixWithCompressionSuffixesRemoved(self)[1]
                    getGenomeElementSourceClass(None, suffix=uncomprSuffix)
                    self.fileFormat = PRIMARY
                except NotSupportedError:
                    if self.suffix == BTRACK_SUFFIX:
                        self.fileFormat = PREPROCESSED
                    else:
                        self.fileFormat = UNKNOWN

        if oldFileFormat != UNKNOWN and oldFileFormat != self.fileFormat:
            raise InvalidFormatError('File format specified as parameter ("%s") does not ' % oldFileFormat +\
                                     'fit with track type as specified by the suffix '
                                     '"%s": "%s"' % (self.suffix, self.fileFormat))

        super(SuffixDependentGSuiteTrack, self)._init(**kwArgs)

    def getGenomeElementSource(self, printWarnings=True):
        from gold.origdata.GenomeElementSource import GenomeElementSource
        return GenomeElementSource(self.path, genome=self.genome, trackName=self.trackName, suffix=self.suffix,
                                   external=True, printWarnings=printWarnings)

class NoQueryForTextGSuiteTrack(GSuiteTrack):
    def _init(self, **kwArgs):
        if self.fileFormat in (PRIMARY, UNKNOWN) and self._parsedUri.query != '':
            raise InvalidFormatError('Queries in URI ("?%s") ' % self._parsedUri.query +\
                                     'is not allowed for non-binary tracks with "%s" as protocol.' % self.SCHEME)

        super(NoQueryForTextGSuiteTrack, self)._init(**kwArgs)


class SearchQueryForSuffixGSuiteTrack(GSuiteTrack):
    def _init(self, **kwArgs):
        super(SearchQueryForSuffixGSuiteTrack, self)._init(**kwArgs)

    def _getFileNameFromQuery(self):
        import re
        query = self._parsedUri.query
        for part in re.split('&|;', query):
            subparts = part.split('=')
            if len(subparts) == 2:
                key, val = subparts
                partSuffix = getFileSuffix(val)
                if partSuffix != '': # Looks like a file name with suffix
                    fileName = val
                    return fileName

    @property
    def suffix(self):
        suffix = super(SearchQueryForSuffixGSuiteTrack, self).suffix

        if suffix is None:
            fileName = self._getFileNameFromQuery()
            if fileName:
                suffix = getFileSuffix(fileName)

        return suffix

    def _generateTitle(self):
        fileName = self._getFileNameFromQuery()
        if fileName:
            return fileName
        else:
            return super(SearchQueryForSuffixGSuiteTrack, self)._generateTitle()


class PreprocessedGSuiteTrack(GSuiteTrack):
    def _init(self, fileFormat=None, **kwArgs):
        self.fileFormat = fileFormat #To handle deprecated 'binary' value

        if self.fileFormat is not None and self.fileFormat != PREPROCESSED:
            raise InvalidFormatError('Track protocol "%s" requires the file format ' % self.SCHEME +\
                                     'to be "%s", not "%s".' % (PREPROCESSED, fileFormat))

        self.fileFormat = PREPROCESSED

        kwArgs['fileFormat'] = fileFormat
        super(PreprocessedGSuiteTrack, self)._init(**kwArgs)


class FtpGSuiteTrack(RemoteGSuiteTrack, SuffixDependentGSuiteTrack):
    SCHEME = 'ftp'


class HttpGSuiteTrack(RemoteGSuiteTrack, SuffixDependentGSuiteTrack, SearchQueryForSuffixGSuiteTrack):
    SCHEME = 'http'


class HttpsGSuiteTrack(HttpGSuiteTrack, SearchQueryForSuffixGSuiteTrack):
    SCHEME = 'https'


class RsyncGSuiteTrack(RemoteGSuiteTrack, SuffixDependentGSuiteTrack):
    SCHEME = 'rsync'


class HbGSuiteTrack(LocalGSuiteTrack, PreprocessedGSuiteTrack, NoQueryForTextGSuiteTrack):
    SCHEME = 'hb'

    def _init(self, **kwArgs):
        if self._parsedUri.params != '':
            raise InvalidFormatError('File suffix parameter is not supported by the '
                                     '"%s" protocol: %s' % (self.SCHEME, self._parsedUri.params))

        if self._parsedUri.query != '':
            raise InvalidFormatError('Queries in URI ("?%s") ' % self._parsedUri.query +\
                                     'is not supported by the "%s" protocol.' % self.SCHEME)

        super(HbGSuiteTrack, self)._init(**kwArgs)

    @property
    def path(self):
        return None

    @property
    def trackName(self):
        path = self._parsedUri.path
        return path[1:].split('/')

    @classmethod
    def generateURI(cls, trackName=[], doQuote=True):
        path = '/' + '/'.join(trackName)
        parseResult = urlparse.ParseResult(cls.SCHEME, '', path, '', '', '')

        if doQuote:
            parseResult = quoteParseResults(parseResult)

        return urlparse.urlunparse(parseResult)


class GalaxyGSuiteTrack(LocalGSuiteTrack, SuffixDependentGSuiteTrack, NoQueryForTextGSuiteTrack):
    SCHEME = 'galaxy'

    def _init(self, **kwArgs):
        self.path #To make sure path is checked
        super(GalaxyGSuiteTrack, self)._init(**kwArgs)

    def hasExtraFileName(self):
        return len( self._parsedUri.path.split('/') ) > 2

    @property
    def path(self):
        from quick.application.ExternalTrackManager import ExternalTrackManager
        pathParts = self._parsedUri.path.split('/')

        if len(pathParts) == 2:
            return ExternalTrackManager.getGalaxyFnFromEncodedDatasetId(pathParts[1])
        elif len(pathParts) > 2:
            dir_ = ExternalTrackManager.getGalaxyFilesFnFromEncodedDatasetId(pathParts[1])
            return os.path.sep.join([dir_] + pathParts[2:])

        return None

    @classmethod
    def generateURI(cls, galaxyFn='', extraFileName='', suffix='', trackName=[], doQuote=True):
        from quick.application.ExternalTrackManager import ExternalTrackManager
        
        databaseId = ExternalTrackManager.getEncodedDatasetIdFromGalaxyFn(galaxyFn)
        path = '/' + databaseId + ('/' + extraFileName if extraFileName != '' else '')

        query = 'track=' + ':'.join(trackName) if trackName else ''
        parseResult = urlparse.ParseResult(cls.SCHEME, '', path, suffix, query, '')

        if doQuote:
            parseResult = quoteParseResults(parseResult)

        return urlparse.urlunparse(parseResult)


class FileGSuiteTrack(LocalGSuiteTrack, SuffixDependentGSuiteTrack, NoQueryForTextGSuiteTrack):
    SCHEME = 'file'
    #DO_UNQUOTE_DEFAULT = False

    @classmethod
    def generateURI(cls, path='', suffix='', trackName=[], doQuote=True):
        query = 'track=' + ':'.join(trackName) if trackName else ''
        parseResult = urlparse.ParseResult(cls.SCHEME, '', path, suffix, query, '')

        if doQuote:
            parseResult = quoteParseResults(parseResult)

        return urlparse.urlunparse(parseResult)


def registerGSuiteTrackClass(cls):
    if cls.SCHEME not in urlparse.uses_query:
        urlparse.uses_query.append(cls.SCHEME)

    if cls.SCHEME not in urlparse.uses_params:
        urlparse.uses_params.append(cls.SCHEME)

    _GSUITE_TRACK_REGISTRY[cls.SCHEME] = cls

def fixNetlocParsingForFile():
    urlparse.uses_netloc.remove(FileGSuiteTrack.SCHEME)

for cls in [FtpGSuiteTrack,
            HttpGSuiteTrack,
            HttpsGSuiteTrack,
            RsyncGSuiteTrack,
            HbGSuiteTrack,
            GalaxyGSuiteTrack]:
    registerGSuiteTrackClass(cls)

if ALLOW_GSUITE_FILE_PROTOCOL:
    registerGSuiteTrackClass(FileGSuiteTrack)
fixNetlocParsingForFile()
