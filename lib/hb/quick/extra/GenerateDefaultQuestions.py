#import os
#from gold.statistic.AllStatistics import STAT_CLASS_DICT
#from gold.application.StatRunner import StatRunner
#from test.gold.track.common.SampleTrack import SampleTrack
#from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num
#from gold.track.GenomeRegion import GenomeRegion
from gold.description.AnalysisManager import AnalysisManager
from gold.statistic.AllStatistics import STAT_CLASS_DICT
#class GenerateDefaultAnalysiss:

#def _getSampleTrack(numbers = False):
#    if numbers:
#        return SampleTrack( SampleTV_Num(numElements=50), True )
#    else:
#        return SampleTrack( SampleTV(starts=True, ends=True, vals=True, numElements=50), True )

#stats = StatOptions().getStats(_getSampleTrack(), _getSampleTrack() )
stats = STAT_CLASS_DICT.values()
uncoveredStats = [stat.__name__ for stat in stats if not (True in [ (stat in a.getAllStats()) for a in AnalysisManager.getAllAnalyses() ]) ]
for stat in uncoveredStats:
    print 'Data inspection: ' + stat + ' -> ' + stat

#for statClass in STAT_CLASS_DICT.values():
#    try:
#        StatRunner.run([GenomeRegion('hg18', 'chr1', 0, 1)], track1, track2, statClass)
#    except:
#        pass
