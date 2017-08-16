#from quick.origdata.PreProcGenerator import PreProcGenerator
from gold.statistic.AllStatistics import RawOverlapStat
from quick.application.AutoBinner import AutoBinner
from gold.track.Track import Track
from gold.track.GenomeRegion import GenomeRegion
from config.Config import DEFAULT_GENOME
from gold.application.StatRunner import StatRunner
from gold.application.GalaxyInterface import GalaxyInterface
from quick.application.UserBinSource import parseRegSpec
import profile
import pstats

#PreProcGenerator.generateTrack(['genes'])
from gold.application.GalaxyInterface import GalaxyInterface

#GalaxyInterface.run(['hpv_200kb'], ['allTss'], RawOverlapStat)
def oldTest():
    results = []
    for chr in ['chr'+str(i) for i in range(1,21)]:
        userBinSource = AutoBinner(parseRegSpec(chr, DEFAULT_GENOME), 1e9) #fixme: do a conversion from  binSpecification to binSource..
        trackName1 = ['hpv_200kb']
        trackName2 = ['allTss']
        #trackName2 = ['melting','zvals','11mers']
        #trackName2 = ['melting']
        #trackName1 = ['melting']
        res = StatRunner.run(userBinSource , Track(trackName1), Track(trackName2), RawOverlapStat)
        results.append( res[0] )
        print res
        
    globResults = {}
    for key in results[0]:
        globResults[key] = sum(res[key] for res in results)
    print globResults
    tp,fp,tn,fn = [globResults[key] for key in 'TP,FP,TN,FN'.split(',')]
    print 'freq near HPV: ', 1.0* tp / (tp+fp)
    print 'freq far from HPV: ', 1.0* fn / (tn+fn)
    
def newTest():
    #GalaxyInterface.run(['genes','TSS'],['hpv_200kb'],'TpReshuffledStat','chr20:10000000-15000000,5000000')
    profile.run(  "GalaxyInterface.run(['genes','TSS'],['hpv_200kb'],'TpReshuffledStat','chr20:10000000-15000000,5000000')",'myProf.txt')
    p = pstats.Stats('myProf.txt')
    p.sort_stats('time').print_stats(50)
    
newTest()   
