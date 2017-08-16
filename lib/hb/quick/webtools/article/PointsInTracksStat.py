from gold.application.HBAPI import doAnalysis
from gold.description.AnalysisDefHandler import AnalysisDefHandler
from gold.description.AnalysisList import REPLACE_TEMPLATES
from gold.track.Track import Track
from quick.application.UserBinSource import GlobalBinSource
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN


class PointsInTracksStat:

    def __init__(self, choices, galaxyFn=None, username=''):
        '''
        Is called when execute-button is pushed by web-user. Should print
        output as HTML to standard out, which will be directed to a results page
        in Galaxy history. If getOutputFormat is anything else than HTML, the
        output should be written to the file with path galaxyFn. If needed,
        StaticFile can be used to get a path where additional files can be put
        (e.g. generated image files). choices is a list of selections made by
        web-user in each options box.
        '''
        analysisDefString = REPLACE_TEMPLATES['$MCFDRv3$'] + ' -> CollectionBinnedHypothesisWrapperStat'
        analysisSpec = AnalysisDefHandler(analysisDefString)
        analysisSpec.setChoice('MCFDR sampling depth', choices.mcfdrDepth)
        analysisSpec.addParameter('assumptions', 'PermutedSegsAndIntersegsTrack_')
        if choices.question == "question 8":
            analysisSpec.addParameter('rawStatistic', 'MultitrackRawBinnedOverlapV2Stat')
        else:
            analysisSpec.addParameter('rawStatistic', 'MultitrackRawSingleBinV2Stat')
#        analysisSpec.addParameter('pairwiseStatistic', choices.stat)
        analysisSpec.addParameter('summaryFunc', choices.summaryFunc)
        analysisSpec.addParameter('tail', 'right-tail')
        analysisSpec.addParameter('localBinSize', choices.binSize)
        analysisSpec.addParameter('question', choices.question)
        analysisBins = GlobalBinSource(choices.genome)
        gsuite = getGSuiteFromGalaxyTN(choices.tracks)
        tracks = [Track(x.trackName) for x in gsuite.allTracks()]
        tracks = tracks[0:2]
        results = doAnalysis(analysisSpec, analysisBins, tracks)
        print results

#
##        analysisDefString = REPLACE_TEMPLATES['$MCFDR$'] + ' -> MultitrackRawBinnedStat'
#        analysisDefString = REPLACE_TEMPLATES['$MCFDRv3$'] + ' -> MultitrackRawDBGStat'
##        analysisDefString = REPLACE_TEMPLATES['$MCFDR$'] + ' -> MultitrackRawOverlapStat'
#        analysisSpec = AnalysisDefHandler(analysisDefString)
#        print analysisDefString
#        analysisSpec.setChoice('MCFDR sampling depth', choices.mcfdrDepth)
#        analysisSpec.addParameter('assumptions', 'PermutedSegsAndIntersegsTrack_')
#        analysisSpec.addParameter('rawStatistic', 'SummarizedInteractionWithOtherTracksStat')
#        analysisSpec.addParameter('pairwiseStatistic', choices.stat)
#        analysisSpec.addParameter('summaryFunc', choices.summaryFunc)
#        analysisSpec.addParameter('tail', 'right-tail')
#        analysisBins = GlobalBinSource(choices.genome)
#        gsuite = getGSuiteFromGalaxyTN(choices.tracks)
#
#        print [x for x in gsuite.allTracks()]
#        print [x.trackName for x in gsuite.allTracks()]
#        tracks = [Track(t.trackName) for t in gsuite.allTracks()]
#        tracks = tracks[0:2]
##        for t in tracks:
##            t._trackFormatReq._allowOverlaps = False
#        results = doAnalysis(analysisSpec, analysisBins, tracks)
#        print results
