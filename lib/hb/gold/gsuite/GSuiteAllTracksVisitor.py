class GSuiteAllTracksVisitor(object):
    def __init__(self, gSuiteTrackVisitor):
        self._gSuiteTrackVisitor = gSuiteTrackVisitor

    def visitAllGSuiteTracksAndReturnOutputAndErrorGSuites(self, gSuite, progressViewer=None, *args, **kwArgs):
        from gold.gsuite.GSuite import GSuite

        outGSuite = GSuite()
        errorGSuite = GSuite()

        for track in gSuite.allTracks():
            try:
                outGSuite.addTrack( self._gSuiteTrackVisitor.visit(track, *args, **kwArgs) )
            except Exception as e:
                track.comment = 'An error occurred for the following track: ' + str(e)
                errorGSuite.addTrack(track)
                # raise #TODO: remove after debug
            if progressViewer:
                progressViewer.update()

        return outGSuite, errorGSuite
