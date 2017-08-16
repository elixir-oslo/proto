from gold.track.GenomeRegion import GenomeRegion
from gold.application.StatRunner import StatRunner
from gold.track.Track import Track
from gold.origdata.GenomeElementSource import GenomeElementSource
from quick.postprocess.GlobalCollectorPP import GlobalCollectorPP
from quick.postprocess.XBinnerPP import XBinnerPP
from quick.application.AutoBinner import AutoBinner
from config.Config import DEFAULT_GENOME
from gold.statistic.AllStatistics import *
from quick.postprocess.LinePlotter import LinePlotter
from quick.postprocess.ScatterPlotter import ScatterPlotter
#from pylab import *
#import cProfile
#import pstats 

def runIntegrationTest():    
    track = Track(['melting']) #hpv_200kb
    track2 = Track(['melting'])
    geSource = GenomeElementSource('Z:\\new_hb\\2sSegs.bed','hg18')
    geSource = GenomeElementSource('/usit/titan/u1/bjarnej/new_hb','hg18')

    userBinSource = AutoBinner(parseRegSpec('chr20', DEFAULT_GENOME), 1e9) #fixme: do a conversion from  binSpecification to binSource..

#    print StatRunner.run(userBinSource, track, track2, RawOverlapStat)
#    print StatRunner.run(userBinSource, track, track2, GenomeWideRandStat)

#    lp = LinePlotter(geSource, track, track2, CountStat, MeanStat, "myNewFile.png", 5)
#    lp.createData()

#    sp = ScatterPlotter(geSource, track, track2, CountStat, MeanStat, "myNewFile2.png", 5)
#    sp.createData()


    #data = StatRunner.run(geSource, track, track2, ZipperStat, CountStat, MeanStat)

    
if __name__ == "__main__":
    runIntegrationTest()
 #   cProfile.run( 'runIntegrationTest()' , 'myProf.txt' )
  #  p = pstats.Stats('myProf.txt')
   # p.sort_stats('time').print_stats(10) 

#for i in xrange(1000):
#    c = CountStat(GenomeRegion('chr1',1000,10000))
#    c.compute()
