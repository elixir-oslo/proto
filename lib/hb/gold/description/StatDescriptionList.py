# Questions

BpOverlapPValOneTrackFixedStat = 'See <note>US_US_Overlap.pdf</note> for a more complete description of the test.'
BpOverlapPValStat = 'See <note>US_US_Overlap.pdf</note> for a more complete description of the test.'
RandomizationManagerStat_TpRawSegsOverlapStat = 'See <note>US_US_Overlap.pdf</note> for a more complete description of the test.'
PointFreqInSegsVsSegMarksStat = 'See <note>UP_MS_Located_in_highly_marked.pdf</note> for a more complete description of the test. ' +\
                                'N.B. Assumes segments of equal length or segment length considered unimportant. '+\
                                'Currently also assumes that no segments crosses bin borders. '
PointPositioningPValStat = 'See <note>UP_US_Uniform_positioning.pdf</note> for a more complete description of the test.'
PointCountInSegsPvalStat = 'See <note>UP_US_Located_inside.pdf</note> for a more complete description of the test.'
DiffRelFreqPValStat = 'See <note>UP_UP_Frequencies.pdf</note> for a more complete description of the test.'
FunctionCorrelationPvalStat = 'See <note>F_F_Similarity.pdf</note> for a more complete description of the test.'
SimpleFunctionCorrelationPvalStat = 'See <note>F_F_Similarity.pdf</note> for a more complete description of the test.'
RandomizationManagerStat_LogMeanDistStat = 'See <note>UP_UP_Distance.pdf</note> for a more complete description of the test.'
RandomizationManagerStat_LogMeanSegDistStat = 'See <note>UP_US_Distance.pdf</note> for a more complete description of the test.'
RandomizationManagerStat_SimpleSimilarSegmentStat = 'See <note>US_US_Similar_segments.pdf</note> for a more complete description of the test.'
RandomizationManagerStat_PointCountInsideSegsStat = 'See <note>UP_US_Located_inside.pdf</note> for a more complete description of the test.'
RandomizationManagerStat_DiffOfMeansAtPointsVsRemainingStat = 'See <note>UP_F_Value_in_points.pdf</note> for a more complete description of the test. ' +\
                                'N.B. A Monte Carlo solution is implemented instead of the analytic solution described in the note.'
RandomizationManagerStat_DiffOfMeanInsideOutsideStat = 'See <note>US_F_Value_in_segments.pdf</note> for a more complete description of the test. ' +\
                                'N.B. The test statistic used for the Monte Carlo solution differs from the one descirbed in the note.'
HigherFunctionInSegsPValStat = 'See <note>US_F_Value_in_segments.pdf</note> for a more complete description of the test. ' +\
                               'N.B. The analytic solution implemented (randomizing function values) is not described in the note.'
RandomizationManagerStat_NearestPointMarkDiffStat = 'See <note>MP_MP_Similar_marks.pdf</note> for a more complete description of the test.'
RandomizationManagerStat_CaseVsControlOverlapDifferenceStat = 'See <note>MS_US_Preferential_overlap.pdf</note> for a more complete description of the test.'
BinPreferencePValStat = 'See <note>UP_uniform_between_bins.pdf</note> for a more complete description of the test.'
#Data inspection
CorrCoefStat = ''
MarksSortedBySegmentOverlapStat = ''
CorrespondingPointMarkCCStat = ''
RawDataStat = ''
TpPointReshuffledStat = ''
MeanStat = ''
ProportionCountStat = ''
ListCollapserStat = ''
ROCScoreFuncValBasedStat = ''
MarksSortedByFunctionValueStat = ''
AccuracyStat = ''
SingleValExtractorStat = ''
SumInsideStat = ''
LogSumSegDistStat = ''
TpRawOverlapStat = ''
FreqChangeRatioStat = ''
SumOfSquaresStat = ''
ZipperStat = ''
MinAndMaxStat = ''
CountPointAllowingOverlapStat = ''
CustomRStat = ''
MeanValAtPointsStat = ''
BasicCustomRStat = ''
ROCScoreOverlapBasedStat = ''
SumStat = ''
TpPointInSegStat = ''
RawOverlapStat = ''
ComputeROCScoreFromRankedTargetControlMarksStat = ''
PointCountsVsSegsStat = ''
VarianceStat = ''
CountPointStat = ''
DiffOfMeanInsideOutsideStat = ''
StdDevStat = ''
DerivedOverlapStat = ''
PointPositionsInSegsStat = ''
TpReshuffledStat = ''
CountStat = ''

#Data Comparison
BinScaledSegCoverageStat = ''
DataComparisonStat = ''
BinScaledFunctionAvgStat = ''
BinScaledPointCoverageStat = ''

#Detailed inspection
FreqPerCatDistributionStat = ''
NearestSegmentDistsStat = ''
SmoothedPointMarksStat = ''
NearestPointDistsStat = ''
SegmentLengthsStat = ''
MarksListStat = ''

#def getDescription(statClassName):    
#    if not statClassName in globals():
#        return 'No description available'
#    assert type(globals()[statClassName]) is str
#    return globals()[statClassName]

