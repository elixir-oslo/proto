from gold.track.GenomeRegion import GenomeRegion
from gold.application.StatRunner import StatRunner
from gold.track.Track import Track
from gold.track.TrackView import TrackView
from gold.statistic.AllStatistics import *
from gold.origdata.GenomeElementSource import GenomeElementSource
from quick.postprocess.SingleValExtractor import SingleValExtractor
from quick.postprocess.GlobalCollectorPP import GlobalCollectorPP
#from stats import lmean
from quick.postprocess.XBinnerPP import XBinnerPP
from quick.postprocess.HistBinnerPP import HistBinnerPP
from quick.postprocess.YSummarizerPP import YSummarizerPP
from pylab import *

#import cProfile
import pstats 


def _getRegion(chr, start, end):
    return GenomeRegion('hg18','chr'+str(chr), start, end)

def runIntegrationTest():    
    track = Track(['melting'])
    track2 = Track(['melting'])
    #regionIter = [_getRegion(c,s,e) for c,s,e in [('M',1000,2000),('M',2000,5000),('M',1000,15000)]]#('M',4000,4000)] ]
    regionIter = GenomeElementSource('Z:\\new_hb\\2sSegs.bed','hg18')

    # segments:
    genomeAnchor = GenomeRegion(genome='hg18', chr='chrM', start=0, end=50)
    trackView = TrackView(genomeAnchor, [2, 16, 23, 40], [9, 20, 26, 45], None, 4, None)
    trackView2 = TrackView(genomeAnchor, [4, 8, 22], [6, 16, 24], None, 3, None)

#    data = StatRunner.run(regionIter, track, track2, RawOverlapStat, trackView, trackView2)
#    data = StatRunner.run(regionIter, track, track2, DerivedOverlapStat, trackView, trackView2)
    data = StatRunner.run(regionIter, track, track2, AccuracyStat, trackView, trackView2)
    print data
    param = "cc"
    for el in data:
        s = SingleValExtractor(el, param)
        print s.getVal()
    

    
if __name__ == "__main__":
    #cProfile.run( 'runIntegrationTest()' , 'myProf.txt' )
    #p = pstats.Stats('myProf.txt')
    #p.sort_stats('time').print_stats(10)
    runIntegrationTest()

#for i in xrange(1000):
#    c = CountStat(GenomeRegion('chr1',1000,10000))
#    c.compute()
