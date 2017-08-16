import os
from gold.statistic.AllStatistics import STAT_CLASS_DICT
from gold.application.StatRunner import StatJob
from test.gold.track.common.SampleTrack import SampleTrack
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num
from gold.track.GenomeRegion import GenomeRegion
from gold.result.Results import Results
import traceback

RESULT_INFO_LIST_FN = os.sep.join(['gold', 'description', 'ResultInfoList.py'])

def _getSampleTrack(numbers = False):
    if numbers:
        return SampleTrack( SampleTV_Num(anchor=[0,50]), True )
    else:
        return SampleTrack( SampleTV(starts=True, ends=True, vals=True, numElements=50, anchor=[0,1000]), True )

resultInfoDict = {}
commentList = []
for line in open(RESULT_INFO_LIST_FN):
    if line.strip()=='' or line.startswith('#'):
        commentList.append(line)
    else:
        print line
        key, resultTuple = [x.strip() for x in line.split('=')]
        resultInfoDict[key] = resultTuple
    
track1 = _getSampleTrack(False)
track2 = _getSampleTrack(False)

track1_Num = _getSampleTrack(True)
track2_Num = _getSampleTrack(True)

def _getStatResDict(track1, track2):
    results = StatJob([GenomeRegion('hg18', 'chr1', 0, 1)], track1, track2, statClass, minimal=True).run()
    #results = StatRunner.run([GenomeRegion('hg18', 'chr1', 0, 1)], track1, track2, statClass, minimal=True, rawStatistic='TpRawOverlapStat', randTrackClass='PermutedSegsAndIntersegsTrack')
    for key in results.getResDictKeys():
        resultInfoKey = statClass.__name__ + '_' + key.replace('-','_').replace(' ','_')
        if not resultInfoKey in resultInfoDict:
            resultInfoDict[resultInfoKey] = str(('', ''))

#def _getStatResDict2(track1, track2,analysisDef):
#    from gold.description.Analysis import Analysis
#    defLine = analysisDef.getDefAfterChoices()
#    analysis = Analysis(defLine, 'hg18',track1, track2)
#    try:
#        statClass = analysis.getStat()
#    except Exception,e:
#        print e
#        import traceback
#        print traceback.format_exc()
#        
#        import sys
#        sys.exit()
#        
#    print statClass, defLine, track1
#    results = StatJob([GenomeRegion('hg18', 'chr1', 0, 1)], track1, track2, statClass, minimal=True).run()
#    #results = StatRunner.run([GenomeRegion('hg18', 'chr1', 0, 1)], track1, track2, statClass, minimal=True, rawStatistic='TpRawOverlapStat', randTrackClass='PermutedSegsAndIntersegsTrack')
#    for key in results.getResDictKeys():
#        resultInfoKey = statClass.__name__ + '_' + key.replace('-','_').replace(' ','_')
#        if not resultInfoKey in resultInfoDict:
#            resultInfoDict[resultInfoKey] = str(('', ''))

#aList = []
#from copy import deepcopy
#from gold.description.AnalysisManager import AnalysisManager
#analysisDict = AnalysisManager.getAnalysisDict()
#categories = analysisDict.keys()
#for cat in categories:
#    analyses = analysisDict[cat].values()
#    for a in analyses:
#        #if a.getChoice('assumptions')
#        opts = a.getOptionsAsKeys()
#        if 'assumptions' in opts:
#            for choice in (opts['assumptions']):
#                a.setChoice('assumptions',choice)
#                aList.append(a)
#                #stat = a.getStat()
#                #statClassList.append(stat)
#        else:
#            aList.append(a)
#            #stat = a.getStat()
#            #statClassList.append(stat)    
            



#for a in aList:
#    #print statClass
#    try:
#        _getStatResDict2(track1, track2,a)
#    except Exception,e:
#        try:
#            _getStatResDict2(track1_Num, track2_Num,a)
#        except Exception,e:
#            try:
#                _getStatResDict2(track1, track2_Num,a)
#            except Exception,e:
#                print e.__class__, e, traceback.format_exc()
#                pass    

#print [ k + ' = ' + resultInfoDict[k] + os.linesep \
#                                          for k in sorted(resultInfoDict)]
#import sys
#sys.exit()

statClassList = STAT_CLASS_DICT.values()

for statClass in statClassList:
    print statClass
    try:
        _getStatResDict(track1, track2)
    except Exception,e:
        try:
            _getStatResDict(track1_Num, track2_Num)
        except Exception,e:
            try:
                _getStatResDict(track1, track2_Num)
            except Exception,e:
                print statClass.__name__ + ': ',e.__class__, e
                pass
                    
resultInfoEntries = [ k + ' = ' + resultInfoDict[k] + os.linesep for k in sorted(resultInfoDict)]
open(RESULT_INFO_LIST_FN,'w').writelines(commentList + resultInfoEntries)
#for k in sorted(resultInfoDict):
    #print k, resultInfoDict[k]
