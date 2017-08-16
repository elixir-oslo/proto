from gold.track.GenomeRegion import GenomeRegion
from gold.application.StatRunner import StatRunner
from gold.track.Track import Track
from gold.track.TrackView import TrackView
from gold.origdata.GenomeElementSource import GenomeElementSource
from quick.postprocess.GlobalCollectorPP import GlobalCollectorPP
from quick.application.AutoBinner import AutoBinner
from quick.application.UserBinSource import UserBinSource
from quick.postprocess.XBinnerPP import XBinnerPP
from quick.postprocess.HistBinnerPP import HistBinnerPP
from quick.postprocess.YSummarizerPP import YSummarizerPP
from gold.statistic.AllStatistics import MeanInsideOutsideTwoTailRandStat
from config.Config import *
#from proto.RSetup import r
from numpy import *
import profile
import hotshot, hotshot.stats


#import cProfile
import pstats 


def _getRegion(chr, start, end):
    return GenomeRegion('hg18','chr'+str(chr), start, end)

class MyTrack:
    def __init__(self, trackView):
        self._trackView = trackView
        
    def getTrackView(self, region):
        return self._trackView[region.start:region.end]
    
    def addFormatReq(self, requestedTrackFormat):
        assert(requestedTrackFormat.isCompatibleWith(self._trackView.trackFormat))

def runIntegrationTest():    
#    myTrack = Track(['bs','wenjie1'])
#    myTrack2 = Track(['melting'])
#    myTrack = Track(['melting','2state'])
    myTrack = Track(['melting','2state'])
    myTrack2 = Track(['melting'])
#    userBinSource = AutoBinner(parseRegSpec('chr1:1-1000000', genome), 100000) #fixme: do a conversion from  binSpecification to binSource..
#    userBinSource = UserBinSource('chr1:1-10000','1000') #fixme: do a conversion from  binSpecification to binSource..
#    userBinSource = UserBinSource('chr1:184916000-184936000','10000') #fixme: do a conversion from  binSpecification to binSource..
#    userBinSource = UserBinSource('chr1:11913000-11916000','1000') #fixme: do a conversion from  binSpecification to binSource..
    userBinSource = UserBinSource('chrM','10000') #fixme: do a conversion from  binSpecification to binSource..

    #regionIter = GenomeElementSource('/Volumes/insilico.titan.uio.no/HyperBrowser/new_hb/data/2sSegs.bed','hg18')
    
    #genomeAnchor = GenomeRegion(genome='hg18', chr='chrM', start=0, end=14)
    #trackView = TrackView([2, 6, 12], [3, 9, 14], None, None, genomeAnchor)
    #trackView2 = TrackView(None, None, [79, 70, 76, 68, 69, 71, 79, 79, 80, 73, 68, 69, 78, 80], None, genomeAnchor)

    #myTrack = MyTrack(trackView)
    #myTrack2 = MyTrack(trackView2)

    print StatRunner.run(userBinSource, myTrack, myTrack2, MeanInsideOutsideTwoTailRandStat)



#    stat = MeanInsideOutsideTwoTailRandStat(userBinSource, myTrack, myTrack2, numResamplings=1000)
#    stat.createChildren()
#    stat.compute()
#    print stat.getResult()
    #data = StatRunner.run(regionIter, myTrack, myTrack2, MeanNumInSegStat)
    #print data

#    data = StatRunner.run(regionIter, track, track2, AvgInsideAvgOutsideStat, trackView, trackView2)
#    print data
    
    
if __name__ == "__main__":
#    profile.run( 'runIntegrationTest()' , 'myProf.txt' )
#    p = pstats.Stats('myProf.txt')
#    p.sort_stats('time').print_stats(50)

#    prof = hotshot.Profile("stones.prof")
#   benchtime, stones = prof.runcall(runIntegrationTest())
#   prof.close()
#   stats = hotshot.stats.load("stones.prof")
#    stats.strip_dirs()
#    stats.sort_stats('time', 'calls')
#    stats.print_stats(20)



    runIntegrationTest()

#for i in xrange(1000):
#    c = CountStat(GenomeRegion('chr1',1000,10000))
#    c.compute()
