#WORKING AS OF April 5, 2015

from gold.application.HBAPI import doAnalysis, GlobalBinSource, AnalysisSpec, PlainTrack
#from gold.application.HBAPI import RegionIter, AnalysisDefHandler, GenomeRegion
from quick.statistic.AvgSegLenStat import AvgSegLenStat

analysisSpec = AnalysisSpec(AvgSegLenStat)
analysisSpec.addParameter("withOverlaps","yes")
analysisBins = GlobalBinSource('hg18')
tracks = [ PlainTrack(['Genes and gene subsets','Genes','Refseq']) ]
result = doAnalysis(analysisSpec, analysisBins, tracks)
resultDict = result.getGlobalResult()
print "Avg gene length: ", resultDict['Result']
