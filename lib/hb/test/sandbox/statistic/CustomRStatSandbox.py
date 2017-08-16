from gold.application.GalaxyInterface import GalaxyInterface
import os
import tempfile
import sys
from quick.result.ResultsCollection import ResultsCollection
from gold.statistic.CustomRStat import CustomRStat, CustomRStatUnsplittable
from gold.track.GenomeRegion import GenomeRegion
from gold.track.Track import Track
from quick.application.UserBinSource import UserBinSource
from gold.application.StatRunner import StatRunner
from quick.util.CommonFunctions import wrapClass
import urllib

#f = tempfile.NamedTemporaryFile()
#scriptLines = ['result <- sum(track1[,3])','2']

#scriptLines = ['return( sum(track1[3,]) )']
#scriptLines = ['return( sum(track1[3,]) )']
#scriptLines = ['return( sum(track1[3,]) + mean(track2[3,]) )']
scriptLines = ['a=track1[2,1]-track1[1,1]', 'b=track2[2,1]-track2[1,1]', 'return(a-b)']

fn = '/usit/titan/u1/geirksa/_data/rTempScript.txt'
open(fn,'w').writelines( [line+os.linesep for line in scriptLines] )
fn = fn.encode('hex_codec')

#
#for line in scriptLines:
#    f.write(line + os.linesep)
#f.flush()
#print f.name

def test1():
    #myTrack = Track(['melting'])
    #myTrack2 = Track(['curvature'])
    myTrack = Track(['genes','refseq'])
    myTrack2 = Track(['repeats'])
                     
    rStat = CustomRStatUnsplittable(GenomeRegion('hg18','chr1',0,100000000), myTrack, myTrack2, scriptFn = fn)
    #rStat._codeLines = scriptLines
    #rStat.compute()
    print rStat.getResult()

def test2():
    myTrack = Track(['melting'])
    myTrack2 = Track(['genes','refseq'])
    userBinSource = UserBinSource('chr1:0-10','10')
    
    res = StatRunner.run(userBinSource, myTrack, myTrack2, wrapClass(CustomRStat, {'scriptFn':fn}))
    resColl = ResultsCollection()
    resColl.addResults(None, res)
    print resColl.getHtmlString()

def test3():
    GalaxyInterface.run(['repeats','SINE'],['repeats'],\
                        '[scriptFn:='+fn+':] -> CustomRStat',\
                        'chr1:1-100000000','10m')
    
#test1()
#test2()
test3()
