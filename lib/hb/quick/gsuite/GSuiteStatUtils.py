from collections import OrderedDict

from gold.application.HBAPI import doAnalysis
from gold.description.AnalysisDefHandler import AnalysisSpec
from gold.gsuite import GSuiteComposer
from gold.gsuite.GSuite import GSuite
from gold.track.Track import Track
from gold.util import CommonConstants

T1_RATIO_OF_SECOND_INSIDE_FIRST = 'Proportion of the query track base-pairs coinciding with base-pairs from the reference track'
T2_RATIO_OF_SECOND_INSIDE_UNION = 'Proportion of the union of base-pairs of the two tracks that are covered by the reference track'
T3_RATIO_OF_INTERSECTION_TO_UNION = 'Jaccard index: ratio of overlapping base-pairs relative to the union base-pairs'
T4_RATIO_OF_INTERSECTION_TO_GEOMETRIC_MEAN = 'Ratio of probability in being inside the intersection and the geometric mean of being inside each track'
T5_RATIO_OF_OBSERVED_TO_EXPECTED_OVERLAP = 'Forbes coefficient: ratio of observed to expected overlap'
T6_STANDARD_DEVIATIONS_OF_OBSERVED_MINUS_EXPECTED_OVERLAP = 'Ratio of observed to expected overlap difference relative to the variance'
T7_RATIO_OF_OBSERVED_TO_EXPECTED_OVERLAP = 'Normalized Forbes coefficient: ratio of observed to expected overlap normalized in relation to the reference GSuite'
T8_CORRELATED_BIN_COVERAGE = 'Correlated bin coverage'
T9_TETRA_CORRELATION = 'Tetrachoric correlation of query track base-pairs and base-pairs from the reference track'

PAIRWISE_STAT_LABEL_TO_CLASS_MAPPING = OrderedDict([
    (T5_RATIO_OF_OBSERVED_TO_EXPECTED_OVERLAP, 'ObservedVsExpectedStat'),
    (T7_RATIO_OF_OBSERVED_TO_EXPECTED_OVERLAP, 'NormalizedObservedVsExpectedStat'),
    (T3_RATIO_OF_INTERSECTION_TO_UNION, 'RatioOfOverlapToUnionStat'),
    (T1_RATIO_OF_SECOND_INSIDE_FIRST, 'PropOfReferenceTrackInsideTargetTrackStat'),
    (T2_RATIO_OF_SECOND_INSIDE_UNION, 'PropOfReferenceTrackInsideUnionStat'),
    (T4_RATIO_OF_INTERSECTION_TO_GEOMETRIC_MEAN, 'RatioOfIntersectionToGeometricMeanStat'),
    # (T6_STANDARD_DEVIATIONS_OF_OBSERVED_MINUS_EXPECTED_OVERLAP, None),
    (T8_CORRELATED_BIN_COVERAGE, 'T1T2BinValuesCorrelationWithKendallCountStat'),
    (T9_TETRA_CORRELATION, 'TetrachoricCorrelationStat')
])

PAIRWISE_STAT_LABELS = PAIRWISE_STAT_LABEL_TO_CLASS_MAPPING.keys()

SUMMARY_FUNCTIONS_MAPPER = OrderedDict([('average', 'avg'), ('maximum', 'max'), ('minimum', 'min')])
SUMMARY_FUNCTIONS_LABELS = SUMMARY_FUNCTIONS_MAPPER.keys()


def runMultipleSingleValStatsOnTracks(gsuite, stats, analysisBins, queryTrack=None):
    '''
    gsuite: The gsuite of tracks
    stats: List of statistics
    analysisBins: BinSource object
    queryTrack: should be defined if there are stats that need to run on two tracks (e.g. overlap)

    Returns an OrderedDict:
                    Track title -> OrderedDict:
                                    Stat name -> single value'''

    assert stats is not None, 'stats argument not defined'
    assert type(stats) in [str, list], '''stats argument must be a list of statistics
                                         or ^-separated string of statistic names'''

    resultsDict = OrderedDict()

    from quick.statistic.GenericResultsCombinerStat import GenericResultsCombinerStat
    additionalAnalysisSpec = AnalysisSpec(GenericResultsCombinerStat)

    statsParam = stats if isinstance(stats, basestring) else "^".join([x.__name__ for x in stats])

    additionalAnalysisSpec.addParameter('rawStatistics', statsParam)  #use ^ separator to add additional stat classes.
    for refTrack in gsuite.allTracks():
        if refTrack.title not in resultsDict:
            resultsDict[refTrack.title] = OrderedDict()
        tracks = [Track(refTrack.trackName), queryTrack] if queryTrack else [Track(refTrack.trackName)]
        additionalResult = doAnalysis(additionalAnalysisSpec,
                                      analysisBins, tracks).getGlobalResult()
        for statClassName, res in additionalResult.iteritems():
            statPrettyName = CommonConstants.STATISTIC_CLASS_NAME_TO_NATURAL_NAME_DICT[
                statClassName] if statClassName in CommonConstants.STATISTIC_CLASS_NAME_TO_NATURAL_NAME_DICT else statClassName
            resultsDict[refTrack.title][statPrettyName] = res

    return resultsDict


def addResultsToInputGSuite(gsuite, results, attrNames, outputGSuiteFN):
    '''
    Add the values from the analysis results as metadata columns and create a new GSuite.
    If the new attribute names in attrNames already exist as metadata columns in the GSuite,
    attributes with added an appropriate _[index] will be added.
    '''
    assert isinstance(attrNames, (list, tuple)), 'attrNames must be of type list or tuple: %s' % str(attrNames)
    newAttrNames = []
    for attrName in attrNames:
        newAttrNames.append(_updateAttrNameWithIndexIfDuplicate(gsuite, attrName))
    outGSuite = GSuite()
    for gsTrack in gsuite.allTracks():
        currentTrackRes = results[gsTrack.title]
        if len(newAttrNames) == 1:
            if isinstance(currentTrackRes, (list, tuple)):
                if currentTrackRes[0]:
                    gsTrack.setAttribute(newAttrNames[0], str(currentTrackRes[0]))
            else:
                if currentTrackRes:
                    gsTrack.setAttribute(newAttrNames[0], str(currentTrackRes))
        else:
            assert isinstance(currentTrackRes,
                              (list, tuple)), 'Expected multiple results per track. Attribute names %s' % str(attrNames)
            for i, resultVal in enumerate(currentTrackRes):
                if resultVal:
                    gsTrack.setAttribute(newAttrNames[i], str(resultVal))
        outGSuite.addTrack(gsTrack)
    GSuiteComposer.composeToFile(outGSuite, outputGSuiteFN)


def _getIndexOfAttributeName(attrName):
    lastIndex = 0
    try:
        lastIndex = int(attrName.split("_")[-1])
    except:
        pass
    return lastIndex


def _updateAttrNameWithIndexIfDuplicate(gsuite, attrName):
    newAttrName = attrName.lower()
    if attrName in gsuite.attributes or attrName.lower() in gsuite.attributes: #check both for older examples
        while newAttrName in [x.lower() for x in gsuite.attributes]:
            lastIndex = _getIndexOfAttributeName(newAttrName) #0 if not there
            newAttrName = attrName.lower() + "_" + str(lastIndex + 1)
    return newAttrName
