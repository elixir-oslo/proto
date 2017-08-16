import os
import ast
import quick.application.SignatureDevianceLogging as sdl

from gold.result.Results import Results

# Note: do not import functions here, as they will be callable from the
#       command line, via CustomFuncCatalog

@sdl.takes(str,str,str)
@sdl.returns(type(None))
def integrateTrackFromFile(inFn, genome, newTrackName, username='', privateAccess='True'):
    """inFn genome newTrackName  username='' privateAccess='True'"""
    from quick.util.CommonFunctions import convertTNstrToTNListFormat
    newTrackName = convertTNstrToTNListFormat(newTrackName, doUnquoting=True)

    if isinstance(privateAccess, basestring):
        privateAccess = ast.literal_eval(privateAccess)
    assert privateAccess in [False, True]

    from gold.util.CommonFunctions import createOrigPath
    path = createOrigPath(genome, newTrackName)
    assert not os.path.exists(path), 'Path already exists in standardized tracks: ' + path

    origFn = path + os.sep + os.path.basename(inFn)

    from quick.application.GalaxyInterface import GalaxyInterface
    GalaxyInterface._integrateTrack(genome, inFn, origFn, newTrackName, privateAccess, username)


@sdl.takes(str,str,str)
@sdl.returns(str)
def createHashBasedTrackNameFromFile(inFn, printTrackName='False'):
    """inFn printTrackName=False"""
    if isinstance(printTrackName, basestring):
        printTrackName = ast.literal_eval(printTrackName)
    assert printTrackName in [False, True]

    from hashlib import sha224
    trackName = ':'.join(['Private', 'Hashbased', sha224(inFn).hexdigest()])

    if printTrackName:
        print trackName

    return trackName


@sdl.takes(str,str,str)
@sdl.returns(type(None))
def integrateHashBasedTrackFromFile(inFn, genome, username=''):
    """inFn genome username=''"""
    newTrackName = createHashBasedTrackNameFromFile(inFn)
    integrateTrackFromFile(inFn, genome, newTrackName, privateAccess='True', username=username)

@sdl.takes(str,list,bool,str)
@sdl.returns(list)
def getSubTrackLeafTerms(genome, parentTrack, excludeSelfIfValid=True, username=''):
    from quick.application.GalaxyInterface import GalaxyInterface
    subTrackTriples = GalaxyInterface.getSubTrackNames(genome, parentTrack, deep=False, username=username)[0]
    filteredSubTrackLeaves = [x[0] for x in subTrackTriples if x not in [[],None] and not (excludeSelfIfValid and x[0]=='-- All subtypes --')]
    return filteredSubTrackLeaves


@sdl.takes(str,str,str,str)
@sdl.returns(Results)
def plainRun(analysisDef, genome, track1Fn, track2Fn):
    '''
    Currently under development, not yet functioning.
    Note that file names (track1Fn, track2Fn) must either be a valid .dat-file from a Galaxy system,
      or be located in a path where the two deepest levels are numerical values above 1000, and unique between different runs by this tool'''
    #GalaxyInterface.runManual(trackNames, analysisDef, regSpec, binSpec, genome, galaxyFn=None, trackNameIntensity=None, username='', \
              #printResults=True, printProgress=True, printHtmlWarningMsgs=True, applyBoundaryFilter=False, printRunDescription=True, **kwArgs):

    from quick.application.ExternalTrackManager import ExternalTrackManager

    #fixme: is this correct?
    assert all(idPart >1000 for idPart in ExternalTrackManager.extractIdFromGalaxyFn(track1Fn))
    tn1 = ExternalTrackManager.constructGalaxyTnFromSuitedFn(track1Fn)
    assert all(idPart >1000 for idPart in ExternalTrackManager.extractIdFromGalaxyFn(track2Fn))
    tn2 = ExternalTrackManager.constructGalaxyTnFromSuitedFn(track2Fn)

    from quick.application.GalaxyInterface import GalaxyInterface
    userBinSource = GalaxyInterface._getUserBinSource('chrs', '*', genome, tn1, tn2)

    from gold.application.StatRunner import AnalysisDefJob
    job = AnalysisDefJob(analysisDef, tn1, tn2, userBinSource)
    result = job.run(printProgress=False)
    return result
