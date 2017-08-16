import math
import inspect

from gold.statistic.CoreStatistics import *
#from gold.track.GenomeRandomizedTrack import GenomeRandomizedTrack
#from gold.track.GaussianRandomizedTrack import GaussianRandomizedTrack
from gold.track.GenomeRegion import GenomeRegion
from gold.track.Track import Track
from gold.track.TrackFormat import TrackFormatReq
from quick.statistic.SingleValExtractorStat import SingleValExtractorStat
# from gold.statistic.DerivedOverlapStat import DerivedOverlapStat

class StatFacade(object):
    pass

class ROCScoreFuncValBasedStat(StatFacade):
    def __new__(cls, region, track1, track2, **kwArgs):
        return ComputeROCScoreFromRankedTargetControlMarksStat(region, track1, track2,'funcval')

class ROCScoreOverlapBasedStat(StatFacade):
    def __new__(cls, region, track1, track2, **kwArgs):
        return ComputeROCScoreFromRankedTargetControlMarksStat(region, track1, track2,'overlap')
    
#Broken! A better cfgHandling must be implemented..
# Works if avoiding points?!..

class LogSumSegSegDistReshuffledStat(StatFacade):
    def __new__(cls, region, track1, track2, **kwArgs):
        return RandomizationManagerStat(region, track1, track2, LogSumSegSegDistStat, PermutedSegsAndIntersegsTrack, **kwArgs)

class LogSumDistReshuffledStat(StatFacade):
    def __new__(cls, region, track1, track2, **kwArgs):
        return RandomizationManagerStat(region, track1, track2, LogSumDistStat, PermutedSegsAndIntersegsTrack, **kwArgs)

class LogSumSegSegDistStat(StatFacade):
    def __new__(cls, region, track1, track2, **kwArgs):
        return ListCollapserStat(region, track1, track2, NearestSegmentDistsStat, \
                                 lambda l:sum(math.log(el) if el is not None and el != 0 else 0 for el in l), **kwArgs)

class LogMeanSegSegDistStat(StatFacade):
    def __new__(cls, region, track1, track2, **kwArgs):
        return ListCollapserStat(region, track1, track2, NearestSegmentDistsStat, \
                                 lambda l:(1.0*sum(math.log(el) if el not in [None, 0] else 0 for el in l)/len(l) \
                                           if len(l) != 0 else None), **kwArgs)

class MeanSegSegDistStat(StatFacade):
    def __new__(cls, region, track1, track2, **kwArgs):
        return ListCollapserStat(region, track1, track2, NearestSegmentDistsStat, \
                                 lambda l:(1.0*sum(l)/len(l) \
                                           if len(l) != 0 else None), **kwArgs)

class LogSumSegDistStat(StatFacade):
    def __new__(cls, region, track1, track2, **kwArgs):
        return ListCollapserStat(region, track1, track2, NearestSegmentFromPointDistsStat, \
                                 lambda l:sum(math.log(el) if el is not None and el != 0 else 0 for el in l), **kwArgs)

class LogMeanSegDistStat(StatFacade):
    def __new__(cls, region, track1, track2, **kwArgs):
        return ListCollapserStat(region, track1, track2, NearestSegmentFromPointDistsStat, \
                                 lambda l:(1.0*sum(math.log(el) if el not in [None, 0] else 0 for el in l)/len(l) \
                                           if len(l) != 0 else None), **kwArgs)
class MeanSegDistStat(StatFacade):
    def __new__(cls, region, track1, track2, **kwArgs):
        return ListCollapserStat(region, track1, track2, NearestSegmentFromPointDistsStat, \
                                 lambda l:(1.0*sum(l)/len(l) \
                                           if len(l) != 0 else None), **kwArgs)
class LogSumDistStat(StatFacade):
    def __new__(cls, region, track1, track2, **kwArgs):
        return ListCollapserStat(region, track1, track2, NearestPointDistsStat, \
                                 lambda l:sum(math.log(el) if el is not None else 0 for el in l), **kwArgs)

class LogMeanDistStat(StatFacade):
    def __new__(cls, region, track1, track2, **kwArgs):
        return ListCollapserStat(region, track1, track2, NearestPointDistsStat, \
                                 lambda l:(1.0*sum(math.log(el) if el not in [None, 0] else 0 for el in l)/len(l) \
                                           if len(l) != 0 else None), **kwArgs)

class MeanDistStat(StatFacade):
    def __new__(cls, region, track1, track2, **kwArgs):
        return ListCollapserStat(region, track1, track2, NearestPointDistsStat, \
                                 lambda l:(1.0*sum(l)/len(l) \
                                           if len(l) != 0 else None), **kwArgs)

#class MeanInsideOutsideTwoTailRandStat(StatFacade):
#    def __new__(cls, region, track1, track2, **kwArgs):
#        return RandomizationManagerStat(region, track1, track2, DiffOfMeanInsideOutsideStat, GaussianRandomizedTrack, **kwArgs)

#class ReshuffledStat(StatFacade):
#    def __new__(cls, region, track1, track2, **kwArgs):
#        return RandomizationManagerStat(region, track1, track2, RawOverlapStat, ReshuffledRandomizedTrack, **kwArgs)

class TpReshuffledStat(StatFacade):
    def __new__(cls, region, track1, track2, **kwArgs):
        return RandomizationManagerStat(region, track1, track2, TpRawOverlapStat, PermutedSegsAndIntersegsTrack, **kwArgs)

class TpPointReshuffledStat(StatFacade):
    def __new__(cls, region, track1, track2, **kwArgs):
        return RandomizationManagerStat(region, track1, track2, TpPointInSegStat, PermutedSegsAndIntersegsTrack, **kwArgs)

class TpRawOverlapStat(StatFacade):
    def __new__(cls, region, track1, track2, **kwArgs):
        return SingleValExtractorStat(region, track1, track2, childClass=RawOverlapStat, resultKey='Both', **kwArgs)

class TpRawSegsOverlapStat(StatFacade):
    def __new__(cls, region, track1, track2, **kwArgs):
        return SingleValExtractorStat(region, track1, track2, childClass=RawSegsOverlapStat, resultKey='Both', **kwArgs)

class TpPointInSegStat(StatFacade):
    def __new__(cls, region, track1, track2, **kwArgs):
        return SingleValExtractorStat(region, track1, track2, childClass=PointCountsVsSegsStat, resultKey='Both', **kwArgs)

class MaxOfMarksStat(StatFacade):
    def __new__(cls, region, track1, track2=None, **kwArgs):
        return MarksAggregationStat(region, track1, None, 'max', **kwArgs)
    
class ThreeTrackBpsCoveredByAllTracksStat(StatFacade):
    def __new__(cls, region, track1, track2, **kwArgs):
        return SingleValExtractorStat(region, track1, track2, childClass=ThreeWayBpOverlapStat, resultKey='111', **kwArgs)

class SegmentOverviewWithoutOverlapStat(StatFacade):
    def __new__(cls, region, track1, track2, rawStatistics=None, **kwArgs):
        return GenericResultsCombinerStat(region, track1, track2, rawStatistics=(CountElementStat,ProportionCountStat,AvgSegLenStat),withOverlaps='no')
    
class DiffRelCoverageMainValueStat(StatFacade):
    def __new__(cls, region, track1, track2, **kwArgs):
        return SingleValExtractorStat(region, track1, track2, childClass=DiffRelCoverageStat, resultKey='Differential relative coverage', **kwArgs)

class SegmentRawDataStat(StatFacade):
    def __new__(cls, region, track1, track2, **kwArgs):
        return RawDataStat(region, track1, TrackFormatReq(dense=False, interval=True), **kwArgs)
    
class SegmentTrackOverviewStat(StatFacade):
    def __new__(cls, region, track1, track2, rawStatistics=None, **kwArgs):
        return GenericResultsCombinerStat(region, track1, track2, 
                                          rawStatistics=(CountStat, 
                                                         CountElementStat, 
                                                         AvgElementLengthStat, 
                                                         MinMaxMedianElementLengthsStat, 
                                                         AvgElementDistStat, 
                                                         MinMaxMedianElementDistancesStat,
                                                         ProportionElementCountStat),
                                          withOverlaps='no')
        
class ObservedVsExpectedStat(StatFacade):
    '''
    STAT T5
    (N bp(Ai intersection Aj)) / (bp(Ai) bp(Aj))
    '''
    def __new__(cls, region, track1, track2, **kwArgs):
        return SingleValExtractorStat(region, track1, track2, childClass=DerivedOverlapStat, resultKey='overlapToExpOverlapRatio', **kwArgs)

#class GenomeWideRandStat(StatFacade):
#    def __new__(cls, region, track1, track2, **kwArgs):
#        return RandomizationManagerStat(region, track1, track2, TpRawOverlapStat, GenomeRandomizedTrack, **kwArgs)

#def _getDummy(statClass):
#    dummy = statClass(GenomeRegion(genome='TestGenome', chr='chr21', start=0, end=0), Track(['dummy']), None)
#    assert(dummy.__class__ != statClass) #if not, resultLabel should be set
#    return dummy
        
#def _transferMemberMagic(statClass):
#    if not hasattr(statClass,'resultLabel'):                
#        statClass.resultLabel = _getDummy(statClass).resultLabel
#        
#    if not hasattr(statClass, 'minimize'):
#        statClass.minimize = _getDummy(statClass).minimize
    
STATFACADE_CLASS_DICT = dict([cls.__name__, cls] for cls in globals().values() \
                        if inspect.isclass(cls) and issubclass(cls, StatFacade) and cls!=StatFacade)
#
#for statClass in STATFACADE_CLASS_DICT.values():
#    _transferMemberMagic(statClass)
