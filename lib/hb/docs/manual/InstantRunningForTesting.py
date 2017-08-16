#WORKING AS OF April 5, 2015

from gold.application.HBAPI import doAnalysis, GlobalBinSource, AnalysisSpec
#from gold.application.HBAPI import RegionIter, AnalysisDefHandler, GenomeRegion
from gold.track.Track import Track
from quick.statistic.SummarizedInteractionWithOtherTracksStat import SummarizedInteractionWithOtherTracksStat
from collections import OrderedDict
from quick.statistic.CollectionVsCollectionStat import CollectionVsCollectionStat
from quick.statistic.StatFacades import TpRawOverlapStat
from quick.statistic.QueryToReferenceCollectionWrapperStat import QueryToReferenceCollectionWrapperStat

analysisSpec = AnalysisSpec(SummarizedInteractionWithOtherTracksStat)
analysisSpec.addParameter("withOverlaps","yes")

analysisBins = GlobalBinSource('hg18')
tracks = [ 
          Track(['Genes and gene subsets','Genes','Refseq']),
          Track(['Genes and gene subsets','Genes','CCDS']),
          Track(['Genes and gene subsets','Genes','Ensembl']),
          Track(['Genes and gene subsets','Genes','GeneID'])
          
           ]
trackTitles = ['refseq', 'CCDS', 'Ensembl', 'GeneID']
# results = OrderedDict()
# analysisSpec = AnalysisSpec(SummarizedInteractionWithOtherTracksStat)
# analysisSpec = AnalysisSpec(CollectionVsCollectionStat)
analysisSpec = AnalysisSpec(QueryToReferenceCollectionWrapperStat)
# analysisSpec.addParameter('rawStatistic', 'RatioOfOverlapToUnionStat')
# analysisSpec.addParameter('rawStatistic', 'TpRawOverlapStat')
analysisSpec.addParameter('pairwiseStat', 'RatioOfOverlapToUnionStat')
# analysisSpec.addParameter('summaryFunc', 'avg')
# analysisSpec.addParameter('reverse', 'No')
# analysisSpec.addParameter('firstCollectionTrackNr', '2')
results = doAnalysis(analysisSpec, analysisBins, tracks)
# print results
# for t1Title, t1 in zip(trackTitles, tracks):
#     for t2Title, t2 in zip(trackTitles, tracks):
#         if t1Title != t2Title:
#             result = doAnalysis(analysisSpec, analysisBins, [t1, t2])
#             resultDict = result.getGlobalResult()
# #                     if 'Result' in resultDict:
#             results[(t1Title, t2Title)] = resultDict['Result']
# for key,val in results.iteritems():
#     print key
#     print val
#     print '____________________'
