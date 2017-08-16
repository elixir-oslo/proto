import cProfile
import pstats

from proto.hyperbrowser.HtmlCore import HtmlCore
from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
from quick.util.CommonFunctions import ensurePathExists
from quick.util.PstatsUtil import OverheadStats


class Profiler:
    PROFILE_HEADER = '--- Profile ---'
    PROFILE_FOOTER = '--- End Profile ---'

    def __init__(self):
        self._prof = cProfile.Profile()
        self._stats = None

    def run(self, runStr, globals, locals):
        self._prof = self._prof.runctx(runStr, globals, locals)
        self._stats = pstats.Stats(self._prof)

    def start(self):
        self._prof.enable()

    def stop(self):
        self._prof.disable()
        self._stats = pstats.Stats(self._prof)

    def printStats(self):
        if self._stats == None:
            return
        
        print Profiler.PROFILE_HEADER
        self._stats.sort_stats('cumulative')
        self._stats.print_stats()
        print Profiler.PROFILE_FOOTER
        
        print Profiler.PROFILE_HEADER
        self._stats.sort_stats('time')
        self._stats.print_stats()
        print Profiler.PROFILE_FOOTER

    def printLinkToCallGraph(self, id, galaxyFn, prune=True):
        statsFile = GalaxyRunSpecificFile(id + ['pstats.dump'], galaxyFn)
        dotFile = GalaxyRunSpecificFile(id + ['callGraph.dot'], galaxyFn)
        pngFile = GalaxyRunSpecificFile(id + ['callGraph.png'], galaxyFn)
        
        ensurePathExists(statsFile.getDiskPath())
        
        self._stats.dump_stats(statsFile.getDiskPath())
        stats = OverheadStats(statsFile.getDiskPath())
        stats.writeDotGraph(dotFile.getDiskPath(), prune=prune)
        stats.renderGraph(dotFile.getDiskPath(), pngFile.getDiskPath())
        
        print str(HtmlCore().link('Call graph based on profiling (id=%s)' % ':'.join(id), pngFile.getURL()))
