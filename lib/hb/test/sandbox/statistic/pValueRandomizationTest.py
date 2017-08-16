from gold.track.GenomeRegion import GenomeRegion
from gold.application.StatRunner import StatRunner
from gold.track.Track import Track
from gold.track.TrackView import TrackView
from gold.statistic.AllStatistics import *
from gold.origdata.GenomeElementSource import GenomeElementSource
from quick.postprocess.GlobalCollectorPP import GlobalCollectorPP
from stats import lmean
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

    geSource = GenomeElementSource('M:\\Hyperbrowser\\new_hb\\2sSegs.bed','hg18')
    

# Randomized p-value distribution
    data = StatRunner.run(geSource, track, track2, RandomizationManagerStat, MeanStat, 5)
    print data
    l = [index for index in range(len(data)) if data[index] < 1.0]
    d2 = [data[index] for index in range(len(data)) if data[index] < 1.0]
    hist(d2, 100)
    show()
    
    
if __name__ == "__main__":
    #cProfile.run( 'runIntegrationTest()' , 'myProf.txt' )
    #p = pstats.Stats('myProf.txt')
    #p.sort_stats('time').print_stats(10)
    runIntegrationTest()

#for i in xrange(1000):
#    c = CountStat(GenomeRegion('chr1',1000,10000))
#    c.compute()
