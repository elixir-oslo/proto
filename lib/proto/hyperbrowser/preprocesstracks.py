# instance is dynamically imported into namespace of <modulename>.mako template (see web/controllers/hyper.py)


import sys
from gold.application.GalaxyInterface import GalaxyInterface
from proto.hyperbrowser.hyper_gui import SelectElement, TrackWrapper
from proto.BaseToolController import *
from HyperBrowserControllerMixin import HyperBrowserControllerMixin


class ToolController(HyperBrowserControllerMixin, BaseToolController):
    def __init__(self, trans, job):
        BaseToolController.__init__(self, trans, job)
        self.genomes = GalaxyInterface.getAllGenomes(self.galaxy.getUserName() \
                                                     if hasattr(self, 'galaxy') else '')
        self.genome = self.params.get('dbkey', self.genomes[0][1])

    def action(self):
        self.genomeElement = SelectElement('dbkey', self.genomes, self.genome)
        self.track = TrackWrapper('track1', GalaxyInterface, [], self.galaxy, [], self.genome)
        self.track.extraTracks = []
        self.track.legend = 'Track'
        self.track.fetchTracks()

    def execute(self):
        self.stdoutToHistory()
        #print self.params
        #tracks = self.params['track1'].split(':')
        username = self.params['userEmail'] if self.params.has_key('userEmail') else ''
        track = self.params['track1'] if self.params.has_key('track1') else []
        print 'GalaxyInterface.startPreProcessing', (self.genome, track, username)
        GalaxyInterface.startPreProcessing(self.genome, track, username)


def getController(transaction = None, job = None):
    return ToolController(transaction, job)

