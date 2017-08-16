import os

from gold.gsuite.GSuiteAllTracksVisitor import GSuiteAllTracksVisitor
from gold.gsuite.GSuiteConstants import LOCAL, PRIMARY, UNKNOWN
from gold.gsuite.GSuiteRequirements import GSuiteRequirements
from gold.gsuite.GSuiteTrack import GSuiteTrack, HbGSuiteTrack
from third_party.Visitor import Visitor


class GSuitePreprocessor(GSuiteAllTracksVisitor):
    def __init__(self):
        GSuiteAllTracksVisitor.__init__(self, GSuiteTrackPreprocessor())


class GSuiteTrackPreprocessor(Visitor):
    def genericVisit(self, gSuiteTrack):
        gSuiteReq = GSuiteRequirements(allowedLocations=[LOCAL], allowedFileFormats=[PRIMARY, UNKNOWN])
        gSuiteReq.check(gSuiteTrack)
        assert gSuiteTrack.genome != UNKNOWN, 'A genome build must be selected for the track: ' + gSuiteTrack.title

    def visitGalaxyGSuiteTrack(self, gSuiteTrack):
        self.genericVisit(gSuiteTrack)

        from quick.application.ExternalTrackManager import ExternalTrackManager
        from gold.description.TrackInfo import TrackInfo

        if gSuiteTrack.hasExtraFileName():
            baseFileName = os.path.basename(gSuiteTrack.uriWithoutSuffix)
        else:
            baseFileName = gSuiteTrack.title
        
        galaxyTN = ExternalTrackManager.constructGalaxyTnFromSuitedFn(
            gSuiteTrack.path, fileEnding=gSuiteTrack.suffix, name=baseFileName)
        trackName = ExternalTrackManager.getPreProcessedTrackFromGalaxyTN(
            gSuiteTrack.genome, galaxyTN, printErrors=False, printProgress=False,
            renameExistingTracksIfNeeded=False)

        trackType = TrackInfo(gSuiteTrack.genome, trackName).trackFormatName.lower()
        hbUri = HbGSuiteTrack.generateURI(trackName=trackName)

        return GSuiteTrack(hbUri, title=gSuiteTrack.title, trackType=trackType,
                           genome=gSuiteTrack.genome, attributes=gSuiteTrack.attributes,
                           comment=gSuiteTrack.comment)
