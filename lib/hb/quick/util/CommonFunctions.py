import os
import sys
import re
import urllib
import contextlib
import traceback

import itertools
import numpy
import functools
import operator
from collections import Iterable, OrderedDict

from config.Config import PROCESSED_DATA_PATH, DEFAULT_GENOME, \
    ORIG_DATA_PATH, MEMOIZED_DATA_PATH, NONSTANDARD_DATA_PATH, \
    PARSING_ERROR_DATA_PATH, IS_EXPERIMENTAL_INSTALLATION
from gold.util.CommonConstants import BINARY_MISSING_VAL
from quick.application.SignatureDevianceLogging import takes, returns
from third_party.decorator import decorator

from proto.CommonFunctions import *


def createDirPath(trackName, genome, chr=None, allowOverlaps=False, basePath=PROCESSED_DATA_PATH):
    """
    >>> createDirPath(['trackname'],'genome','chr1')
    '/100000/noOverlaps/genome/trackname/chr1'
    """
    from gold.util.CompBinManager import CompBinManager
    if len(trackName)>0 and trackName[0] == 'redirect':
        genome = trackName[1]
        chr = trackName[2]
        #trackName[3] is description
        trackName = trackName[4:]

    #print [basePath, str(CompBinManager.getIndexBinSize()), ('withOverlaps' if allowOverlaps else 'noOverlaps'), genome] +\
    #    list(trackName) + ([chr] if chr is not None else [])

    return os.sep.join( [basePath, str(CompBinManager.getIndexBinSize()), ('withOverlaps' if allowOverlaps else 'noOverlaps'), genome] +\
        list(trackName) + ([chr] if chr is not None else []) )


def createMemoPath(region, statId, configHash, track1Hash, track2Hash):
    chr = region.chr
    genome = region.genome
    return os.sep.join( [MEMOIZED_DATA_PATH, str(len(region)), statId, genome, str(track1Hash)] + \
                        ([str(track2Hash)] if track2Hash is not None else []) + \
                        [str(configHash), chr] ).replace('-','_') #replace('-','_') because hashes can be minus, and minus sign makes problems with file handling


@takes(str,(list,tuple),(str,type(None)))
def createOrigPath(genome, trackName, fn=None):
    #print 'genome:',genome
    #print 'trackName:',trackName
    return os.sep.join([ORIG_DATA_PATH, genome] + trackName + ([fn] if fn is not None else []))


@takes(str,(list,tuple),(str,type(None)))
def createCollectedPath(genome, trackName, fn=None):
    return os.sep.join([NONSTANDARD_DATA_PATH, genome] + trackName + ([fn] if fn is not None else []))


@takes(str,(list,tuple),(str,type(None)))
def createParsingErrorPath(genome, trackName, fn=None):
    return os.sep.join([PARSING_ERROR_DATA_PATH, genome] + trackName + ([fn] if fn is not None else []))


@takes(str)
def getFileSuffix(fn):
    from gold.application.DataTypes import getSupportedFileSuffixes
    for suffix in getSupportedFileSuffixes():
        if '.' in suffix and fn.endswith('.' + suffix):
            return suffix
    return os.path.splitext(fn)[1].replace('.','')


@takes(str)
def stripFileSuffix(fn):
    suffix = getFileSuffix(fn)
    return fn[:-len(suffix)-1]


def getOrigFns(genome, trackName, suffix, fileTree='standardized'):
    assert fileTree in ['standardized', 'collected', 'parsing error']
    from gold.application.LogSetup import logMessage, logging

    if fileTree == 'standardized':
        path = createOrigPath(genome, trackName)
    elif fileTree == 'collected':
        path = createCollectedPath(genome, trackName)
    else:
        path = createParsingErrorPath(genome, trackName)

    if not os.path.exists(path):
        if IS_EXPERIMENTAL_INSTALLATION:
            logMessage('getOrigFn - Path does not exist: ' + path, logging.WARNING)
        return []

    return [path + os.sep + x for x in os.listdir(path) if os.path.isfile(path + os.sep + x) \
            and x.endswith(suffix) and not x[0] in ['.','_','#'] and not x[-1] in ['~','#']]


def getOrigFn(genome, trackName, suffix, fileTree='standardized'):
    fns = getOrigFns(genome, trackName, suffix, fileTree=fileTree)
    if len(fns) != 1:
        if IS_EXPERIMENTAL_INSTALLATION:
            from gold.application.LogSetup import logMessage, logging
            logMessage('getOrigFn - Cannot decide among zero or several filenames: %s' % fns, logging.WARNING)
        return None

    return fns[0]


def parseDirPath(path):
    'Returns [genome, trackName, chr] from directory path'
    path = path[len(PROCESSED_DATA_PATH + os.sep):]# + str(CompBinManager.getIndexBinSize())):]
    while path[0] == os.sep:
        path = path[1:]
    path.replace(os.sep*2, os.sep)
    el = path.split(os.sep)
    return el[2], tuple(el[3:-1]), el[-1]


def extractTrackNameFromOrigPath(path):
    excludeEl = None if os.path.isdir(path) else -1
    path = path[len(ORIG_DATA_PATH):]
    path = path.replace('//','/')
    if path[0]=='/':
        path = path[1:]
    if path[-1]=='/':
        path = path[:-1]
    return path.split(os.sep)[1:excludeEl]


def getStringFromStrand(strand):
    if strand in (None, BINARY_MISSING_VAL):
        return '.'
    return '+' if strand else '-'


def parseTrackNameSpec(trackNameSpec):
    return trackNameSpec.split(':')


def prettyPrintTrackName(trackName, shortVersion=False):
    from urllib import unquote
    if len(trackName) == 0:
        return ''
    elif len(trackName) == 1:
        return trackName[0]
    elif trackName[0] in ['galaxy','redirect','virtual']:
        return "'" + re.sub('([0-9]+) - (.+)', '\g<2> (\g<1>)', unquote(trackName[3])) + "'"
    elif trackName[0] in ['external']:
        return "'" + re.sub('[0-9]+ - ', '', unquote(trackName[-1])) + "'"
    else:
        if trackName[-1]=='':
            return "'" + trackName[-2] + "'"
        return "'" + trackName[-1] + (' (' + trackName[-2] + ')' if not shortVersion else '') + "'"
        #return "'" + trackName[1] + (' (' + '-'.join(trackName[2:]) + ')' if len(trackName) > 2 else '') + "'"
        #return trackName[1] + (' (' + '-'.join(trackName[2:]) + ')' if len(trackName) > 2 else '')


def insertTrackNames(text, trackName1, trackName2 = None, shortVersion=False):
    PREFIX = '(the points of |points of |point of |the segments of |segments of |segment of |the function of |function of )?'
    POSTFIX = '([- ]?segments?|[- ]?points?|[- ]?function)?'
    newText = re.sub(PREFIX + '[tT](rack)? ?1' +  POSTFIX, prettyPrintTrackName(trackName1, shortVersion), text)
    if trackName2 != None:
        newText = re.sub(PREFIX + '[tT](rack)? ?2' + POSTFIX, prettyPrintTrackName(trackName2, shortVersion), newText)
    return newText


def resultsWithoutNone(li, ignoreNans=False):
    for el in li:
        if el is not None and not (ignoreNans and numpy.isnan(el)):
            yield el


def smartSum(li, ignoreNans=False):
    try:
        resultsWithoutNone(li, ignoreNans).next()
    except StopIteration:
        return None

    return sum(resultsWithoutNone(li, ignoreNans))


def smartMean(li, ignoreNans=False, excludeNonesFromMean=False, returnZeroForEmpty=False):

    smrtSum = smartSum(li, ignoreNans=ignoreNans)
    if smrtSum is not None:
        if excludeNonesFromMean:
            return float(smrtSum)/len(resultsWithoutNone(li, ignoreNans=ignoreNans))
        else:
            return float(smrtSum)/len(li)
    if returnZeroForEmpty:
        return 0.0


def smartMeanNoNones(li):
    return smartMean(li, excludeNonesFromMean=True)


def smartMeanWithNones(li):
    return smartMean(li)


def smartMin(li, ignoreNans=False):
    try:
        resultsWithoutNone(li, ignoreNans).next()
    except StopIteration:
        return None

    return min(resultsWithoutNone(li, ignoreNans))


def isIter(obj):
    from numpy import memmap
    if isinstance(obj, memmap):
        return False
    return hasattr(obj, '__iter__')


def isNumber(s):
    try:
        float(s)
        return True
    except:
        return False


def getClassName(obj):
    return obj.__class__.__name__


def smartStrLower(obj):
    return str.lower(str(obj))


def splitOnWhitespaceWhileKeepingQuotes(msg):
    return re.split('\s+(?=(?:[^"]*"[^"]*")*[^"]*$)', msg.strip())


def parseShortenedSizeSpec(spec):
    spec = spec.strip()
    if spec[-1].lower() == 'k':
        size = int(spec[0:-1]) * 1000
    elif spec[-1].lower() == 'm':
        size = int(spec[0:-1]) * 1000000
    else:
        size = int(spec)
    return size


def generateStandardizedBpSizeText(size):
    if size == 0:
        return '0 bp'
    elif size % 10**9 == 0:
        return str(size/10**9) + ' Gb'
    elif size % 10**6 == 0:
        return str(size/10**6) + ' Mb'
    elif size % 10**3 == 0:
        return str(size/10**3) + ' kb'
    else:
        return str(size) + ' bp'


def quenchException(fromException, replaceVal):
    "if a certain exception occurs within method, catch this exception and instead return a given value"
    def _quenchException(func, *args, **kwArgs):
        try:
            return func(*args, **kwArgs)
        except fromException,e:
            return replaceVal
    return decorator(_quenchException)


def reverseDict(mapping):
    vals = mapping.values()
    assert len(set(vals)) == len(vals) #Ensure all values are unique
    return dict((v,k) for k, v in mapping.iteritems())


def mean(l):
    return float(sum(l)) / len(l)


def product(l):
    """Product of a sequence."""
    return functools.reduce(operator.mul, l, 1)


def flatten(l):
    for el in l:
        if isinstance(el, Iterable) and not isinstance(el, basestring):
            for sub in flatten(el):
                yield sub
        else:
            yield el


def findKeysWithValDefinedByNumpyFunc(d, func=max):
    import numpy as np
    vals = np.array(d.values())
    keys = np.array(d.keys())
    return list(keys[vals == func(vals)])


def findKeysWithMaxVal(d):
    return findKeysWithValDefinedByNumpyFunc(d, lambda x: x.max())


def findKeysWithMinVal(d):
    return findKeysWithValDefinedByNumpyFunc(d, lambda x: x.min())


def pairwise(iterable):
    from itertools import tee, izip

    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)


def multiReplace(str, fromList, toList):
    assert len(fromList) == len(toList)
    for i, fromStr in enumerate(fromList):
        str = str.replace(fromStr, toList[i])
    return str


def replaceIllegalElementsInTrackNames(string):
    return multiReplace(string, [':','=','[',']','/','-->'],['.','-','(',')','_', '-'])


def arrayEquals(x, y):
    try:
        return x == y
    except:
        return (x == y).all()


def repackageException(fromException, toException):
    def _repackageException(func, *args, **kwArgs):
        try:
            return func(*args, **kwArgs)
        except fromException,e:
            raise toException('Repackaged exception.., original was: ' + getClassName(e) + ' - '+str(e) + ' - ' + traceback.format_exc())
    return decorator(_repackageException)

#Typical use, for instance
    #from gold.util.CommonFunctions import repackageException
    #from gold.util.CustomExceptions import ShouldNotOccurError
    #@repackageException(Exception, ShouldNotOccurError)

#Repackaging can also be done manually for chunks of code by:
    #import traceback
    #from gold.util.CustomExceptions import ShouldNotOccurError
    #from gold.util.CommonFunctions import getClassName
    #try:
    #    pass #code chunk here..
    #except Exception,e:
    #    raise ShouldNotOccurError('Repackaged exception.., original was: ' + getClassName(e) + ' - '+str(e) + ' - ' + traceback.format_exc())


def reloadModules():
    for module in [val for key, val in sys.modules.iteritems() \
                   if key.startswith('gold') or key.startswith('quick') or key.startswith('test')]:
        try:
            reload(module)
        except:
            print module


def wrapClass(origClass, keywords={}):
    # for key in keywords.keys():
    #    if re.match('^[0-9]+$',keywords[key]) is not None:
    #        keywords[key] = int(keywords[key])
    #    elif re.match('^[0-9]?[.][0-9]?$',keywords[key]) is not None and keywords[key] != '.':
    #        keywords[key] = float(keywords[key])

    args = []
    wrapped = functools.partial(origClass, *args, **keywords)
    functools.update_wrapper(wrapped, origClass)
    return wrapped


def isFlatList(list):
    for l in list:
        if type(l) == type([]):
            return False
    return True


def flattenList(list):
    '''
    recursively flattens a nested list (does not handle dicts and sets..) e.g.
    [1, 2, 3, 4, 5] == flattenList([[], [1,2],[3,4,5]])
    '''
    if isFlatList(list):
        return list
    else:
        return flattenList(reduce(lambda x, y: x + y, list))


def allElementsVersusRest(inList):
    """
    :return: list of tuples, where first element of each tuple is each element in inList in turn,
             while the second element of the tuple is a tuple of the rest of the elements of
             inList. Example: inList = [1,2,3] ->  returns [(1, (2, 3)), (2, (1, 3), (3, (1, 2))]
    """
    return zip([inList[x] for x in range(len(inList))],
               reversed(list(itertools.combinations(inList, len(inList)-1))))


def listStartsWith(a, b):
    return len(a) > len(b) and a[:len(b)] == b


def isListType(x):
    import numpy
    return type(x) == list or type(x) == tuple or isinstance(x, numpy.ndarray) or isinstance(x, dict)


def ifDictConvertToList(d):
    return [(x, d[x]) for x in sorted(d.keys())] if isinstance(d, dict) else d


def smartRecursiveAssertList(x, y, assertEqualFunc, assertAlmostEqualFunc):
    import numpy
    # print x,y

    if isListType(x):
        if isinstance(x, numpy.ndarray):
            try:
                assertEqualFunc(x.shape, y.shape)
            except Exception, e:
                raise AssertionError(str(e) + ' on shape of lists: ' + str(x) + ' and ' + str(y))

            try:
                assertEqualFunc(x.dtype, y.dtype)
            except Exception, e:
                raise AssertionError(str(e) + ' on datatypes of lists: ' + str(x) + ' and ' + str(y))
        else:
            try:
                assertEqualFunc(len(x), len(y))
            except Exception, e:
                raise AssertionError(str(e) + ' on length of lists: ' + str(x) + ' and ' + str(y))

        for el1, el2 in zip(*[ifDictConvertToList(_) for _ in [x, y]]):
            smartRecursiveAssertList(el1, el2, assertEqualFunc, assertAlmostEqualFunc)

    else:
        try:
            assertAlmostEqualFunc(x, y)
        except (TypeError, FloatingPointError):
            assertEqualFunc(x, y)


def bothIsNan(a, b):
    import numpy

    try:
        if not any(isListType(x) for x in [a, b]):
            return numpy.isnan(a) and numpy.isnan(b)
    except (TypeError, NotImplementedError):
        pass
    return False


def smartAssertEquals(a, b):
    if not bothIsNan(a, b):
        assert a == b


def smartRecursiveEquals(a, b):
    try:
        smartRecursiveAssertList(a, b, smartAssertEquals, smartAssertEquals)
        return True
    except AssertionError:
        return False


def reorderTrackNameListFromTopDownToBottomUp(trackNameSource):
    prevTns = []
    source = trackNameSource.__iter__()
    trackName = source.next()

    try:
        while True:
            if len(prevTns) == 0 or listStartsWith(trackName, prevTns[0]):
                prevTns.insert(0, trackName)
                trackName = source.next()
                continue
            yield prevTns.pop(0)

    except StopIteration:
        while len(prevTns) > 0:
            yield prevTns.pop(0)


R_ALREADY_SILENCED = False


def silenceRWarnings():
    global R_ALREADY_SILENCED
    if not R_ALREADY_SILENCED:
        from proto.RSetup import r
        r('sink(file("/dev/null", open="wt"), type="message")')
        R_ALREADY_SILENCED = True


R_ALREADY_SILENCED_OUTPUT = False


def silenceROutput():
    global R_ALREADY_SILENCED_OUTPUT
    if not R_ALREADY_SILENCED_OUTPUT:
        from proto.RSetup import r
        r('sink(file("/dev/null", open="wt"), type="output")')
        R_ALREADY_SILENCED_OUTPUT = True


NUMPY_ALREADY_SILENCED = False


def silenceNumpyWarnings():
    global NUMPY_ALREADY_SILENCED
    if not NUMPY_ALREADY_SILENCED:
        import warnings
        warnings.filterwarnings("ignore", message='Mean of empty slice.')
        warnings.filterwarnings("ignore",
                                message='Invalid value encountered in median')
        NUMPY_ALREADY_SILENCED = True


def createHyperBrowserURL(genome, trackName1, trackName2=None, track1file=None, track2file=None, \
                          demoID=None, analcat=None, analysis=None, \
                          configDict=None, trackIntensity=None, method=None, region=None, \
                          binsize=None, chrs=None, chrArms=None, chrBands=None, genes=None):
    urlParams = []
    urlParams.append(('dbkey', genome))
    urlParams.append(('track1', ':'.join(trackName1)))
    if trackName2:
        urlParams.append(('track2', ':'.join(trackName2)))
    if track1file:
        urlParams.append(('track1file', track1file))
    if track2file:
        urlParams.append(('track2file', track2file))
    if demoID:
        urlParams.append(('demoID', demoID))
    if analcat:
        urlParams.append(('analcat', analcat))
    if analysis:
        urlParams.append(('analysis', analysis))
    if configDict:
        for key, value in configDict.iteritems():
            urlParams.append(('config_%s' % key, value))
    if trackIntensity:
        urlParams.append(('trackIntensity', trackIntensity))
    if method:
        urlParams.append(('method', method))
    if region:
        urlParams.append(('region', region))
    if binsize:
        urlParams.append(('binsize', binsize))
    if chrs:
        urlParams.append(('__chrs__', chrs))
    if chrArms:
        urlParams.append(('__chrArms__', chrArms))
    if chrBands:
        urlParams.append(('__chrBands__', chrBands))
    if genes:
        urlParams.append(('genes', genes))
    # genes not __genes__?
    # encode?

    from config.Config import URL_PREFIX
    return URL_PREFIX + '/hyper?' + '&'.join([urllib.quote(key) + '=' + \
                                              urllib.quote(value) for key, value in urlParams])


def numAsPaddedBinary(comb, length):
    return '0' * (length - len(bin(comb)[2:])) + bin(comb)[2:]


@contextlib.contextmanager
def changedWorkingDir(new_dir):
    orig_dir = os.getcwd()
    os.chdir(new_dir)
    try:
        yield
    finally:
        os.chdir(orig_dir)


def convertTNstrToTNListFormat(tnStr, doUnquoting=False):
    tnList = re.split(':|\^|\|', tnStr)
    if doUnquoting:
        tnList = [urllib.unquote(x) for x in tnList]
    return tnList


# used by echo
def name(item):
    " Return an item's name. "
    return item.__name__


def format_arg_value(arg_val):
    """ Return a string representing a (name, value) pair.

    >>> format_arg_value(('x', (1, 2, 3)))
    'x=(1, 2, 3)'
    """
    arg, val = arg_val
    return "%s=%r" % (arg, val)


def echo(fn, write=sys.stdout.write):
    """ Echo calls to a function.

    Returns a decorated version of the input function which "echoes" calls
    made to it by writing out the function's name and the arguments it was
    called with.
    """
    # import functools
    # Unpack function's arg count, arg names, arg defaults
    code = fn.func_code
    argcount = code.co_argcount
    argnames = code.co_varnames[:argcount]
    fn_defaults = fn.func_defaults or list()
    argdefs = dict(zip(argnames[-len(fn_defaults):], fn_defaults))

    @functools.wraps(fn)
    def wrapped(*v, **k):
        # Collect function arguments by chaining together positional,
        # defaulted, extra positional and keyword arguments.
        positional = map(format_arg_value, zip(argnames, v))
        defaulted = [format_arg_value((a, argdefs[a]))
                     for a in argnames[len(v):] if a not in k]
        nameless = map(repr, v[argcount:])
        keyword = map(format_arg_value, k.items())
        args = positional + defaulted + nameless + keyword
        write("%s(%s)\n" % (name(fn), ", ".join(args)))
        return fn(*v, **k)

    return wrapped


def getGeSource(track, genome=None):
    from quick.application.ExternalTrackManager import ExternalTrackManager
    from gold.origdata.BedGenomeElementSource import BedGenomeElementSource, BedCategoryGenomeElementSource
    from gold.origdata.GtrackGenomeElementSource import GtrackGenomeElementSource
    from gold.origdata.TrackGenomeElementSource import FullTrackGenomeElementSource

    if isinstance(track, basestring):
        track = track.split(':')

    try:
        fileType = ExternalTrackManager.extractFileSuffixFromGalaxyTN(track)
        fn = ExternalTrackManager.extractFnFromGalaxyTN(track)
        if fileType == 'category.bed':
            return BedCategoryGenomeElementSource(fn)
        elif fileType == 'gtrack':
            return GtrackGenomeElementSource(fn)
        else:
            return BedGenomeElementSource(fn)
    except:
        return FullTrackGenomeElementSource(genome, track, allowOverlaps=False)


# generate powerset for set
# powerset([a,b,c]) = [(), (a), (b), (c), (a,b), (a,c), (a,b), (a,b,c))
def powerset(iterable):
    from itertools import chain, combinations
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


# Generate all supersets of a set represented by a binary string
# e.g. allSupersets('010') = ['110','011','111']
def allSupersets(binaryString):
    length = len(binaryString)
    binaryList = list(binaryString)
    zeroIndex = [i for i, val in enumerate(binaryList) if val == '0']
    for comb in powerset(zeroIndex):
        if comb:
            yield ''.join([binaryList[i] if i not in comb else '1' for i in range(length)])


def getUniqueFileName(origFn):
    import os

    i = 0
    newOrigFn = origFn

    while os.path.exists(newOrigFn):
        newOrigFn = origFn + '.%s' % i
        i += 1

    return newOrigFn


def cleanUpTrackType(trackTypeStr):
    REPLACE_DICT = {
        'unmarked': '',
        'Unmarked': '',
        'marked': 'valued',
        'Marked': 'Valued'
    }

    for old, new in REPLACE_DICT.iteritems():
        trackTypeStr = trackTypeStr.replace(old, new).strip()

    return trackTypeStr
