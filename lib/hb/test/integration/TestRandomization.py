#!/usr/bin/env python
import ast
import unittest
import os
import tempfile
from test.integration.GalaxyIntegrationTest import GalaxyIntegrationTest
import sys
import numpy

class TestRandomization(GalaxyIntegrationTest):
    def testTpReshuffledStat(self):
        self._assertRunEqual([[('DiffFromMean', 0.0), ('MeanOfNullDistr', 4.0), ('MedianOfNullDistr', 4.0), ('NumMoreExtremeThanObs', 13), ('NumPointsTr1', 2), ('NumPointsTr2', 6), ('NumResamplings', 20), ('NumSamplesNotNan', 20), ('P-value', 0.6666666666666666), ('SdNullDistr', 1.3416407864998738), ('TSMC_TpRawOverlapStat', 4L)]],\
            ["segs"],["segsLen1"],'[tails:=right-tail:][numResamplings:=20:] [maxSamples:=20:] -> TpReshuffledStat','TestGenome:chr21:16000001-17000000','1000000')
    
    def testTpPointReshuffledStat(self):
        self._assertRunEqual([ [('DiffFromMean', 0.4), ('MeanOfNullDistr', 0.6), ('MedianOfNullDistr', 1.0), ('NumMoreExtremeThanObs', 11), ('NumPointsTr1', 2), ('NumPointsTr2', 447), ('NumResamplings', 20), ('NumSamplesNotNan', 20), ('P-value', 0.5714285714285714), ('SdNullDistr', 0.58309518948453021), ('TSMC_TpPointInSegStat', 1)],  [('DiffFromMean', 0.0), ('MeanOfNullDistr', 0.0), ('MedianOfNullDistr', 0.0), ('NumMoreExtremeThanObs', 20), ('NumPointsTr1', 0), ('NumPointsTr2', 0), ('NumResamplings', 20), ('NumSamplesNotNan', 20), ('P-value', None), ('SdNullDistr', 0.0), ('TSMC_TpPointInSegStat', 0)]],\
            ["segs"],["segsMany"],'[tails:=right-tail:][numResamplings:=20:] [maxSamples:=20:] -> TpPointReshuffledStat','TestGenome:chr21:10000001-11000000','500000')
    
    def testLogSumDistReshuffledStat(self): 
        self._assertRunEqual([[('DiffFromMean', -1371.3171584747324), ('MeanOfNullDistr', 4025.7179688777478), ('MedianOfNullDistr', 3980.4040522828809), ('NumMoreExtremeThanObs', 20), ('NumPointsTr1', 447), ('NumPointsTr2', 2), ('NumResamplings', 20), ('NumSamplesNotNan', 20), ('P-value', 1.0), ('SdNullDistr', 1249.2871300268578), ('TSMC_LogSumSegSegDistStat', 2654.4008104030154)], [('DiffFromMean', 0.0), ('MeanOfNullDistr', 0.0), ('MedianOfNullDistr', 0.0), ('NumMoreExtremeThanObs', 20), ('NumPointsTr1', 0), ('NumPointsTr2', 0), ('NumResamplings', 20), ('NumSamplesNotNan', 20), ('P-value', None), ('SdNullDistr', 0.0), ('TSMC_LogSumSegSegDistStat', 0)]],\
           ["segsMany"],["segs"],'[tails:=right-tail:][numResamplings:=20:] [maxSamples:=20:] -> LogSumSegSegDistReshuffledStat','TestGenome:chr21:10000001-11000000','500000')
    
    def testSimilarSegmentsReshuffledStat(self):
        self._assertRunEqual([ [('DiffFromMean', 0.0), ('MeanOfNullDistr', 0.0), ('MedianOfNullDistr', 0.0), ('NumMoreExtremeThanObs', 20), ('NumPointsTr1', 2), ('NumPointsTr2', 447), ('NumResamplings', 20), ('NumSamplesNotNan', 20), ('P-value', 1.0), ('SdNullDistr', 0.0), ('TSMC_SimilarSegmentStat', 0)], [('DiffFromMean', 0.0), ('MeanOfNullDistr', 0.0), ('MedianOfNullDistr', 0.0), ('NumMoreExtremeThanObs', 20), ('NumPointsTr1', 0), ('NumPointsTr2', 0), ('NumResamplings', 20), ('NumSamplesNotNan', 20), ('P-value', None), ('SdNullDistr', 0.0), ('TSMC_SimilarSegmentStat', 0)]],\
           ["segs"],["segsMany"],'[tails:=two-tail:] [rawStatistic:=SimilarSegmentStat] [randTrackClass:=PermutedSegsAndIntersegsTrack] [numResamplings:_Resamplings=20] [maxSamples:=20:] -> RandomizationManagerStat','TestGenome:chr21:10000001-12000000','1000000')
    
    def testSegmentOverlapsHighPresReshuffledStat(self):
        self._assertRunEqual([ [('DiffFromMean', 10101.099999999999), ('MeanOfNullDistr', 35630.900000000001), ('MedianOfNullDistr', 42016.0), ('NumMoreExtremeThanObs', 8), ('NumPointsTr1', 2), ('NumPointsTr2', 447), ('NumResamplings', 20), ('NumSamplesNotNan', 20), ('P-value', 0.8571428571428571), ('SdNullDistr', 15607.104529348166), ('TSMC_TpRawOverlapStat', 45732)], [('DiffFromMean', 0.0), ('MeanOfNullDistr', 0.0), ('MedianOfNullDistr', 0.0), ('NumMoreExtremeThanObs', 20), ('NumPointsTr1', 0), ('NumPointsTr2', 0), ('NumResamplings', 20), ('NumSamplesNotNan', 20), ('P-value', None), ('SdNullDistr', 0.0), ('TSMC_TpRawOverlapStat', 0L)]],\
           ["segs"],["segsMany"],'[tails:=two-tail:] [rawStatistic:=TpRawOverlapStat] [assumptions:=_PermutedSegsAndIntersegsTrack] [numResamplings:_Resamplings=20] [maxSamples:=20:] -> RandomizationManagerStat','TestGenome:chr21:10000001-12000000','1000000')
    
    def testSegmentOverlapsSegsByIntensityStat(self):
        self._assertRunEqual([[('DiffFromMean', 2.75), ('MeanOfNullDistr', 0.25), ('MedianOfNullDistr', 0.0), ('NumMoreExtremeThanObs', 0), ('NumPointsTr1', 2), ('NumPointsTr2', 5), ('NumResamplings', 20), ('NumSamplesNotNan', 20), ('P-value', 0.09523809523809523), ('SdNullDistr', 0.4330127018922193), ('TSMC_TpRawOverlapStat', 3L)], [('DiffFromMean', 0.0), ('MeanOfNullDistr', 0.0), ('MedianOfNullDistr', 0.0), ('NumMoreExtremeThanObs', 20), ('NumPointsTr1', 0), ('NumPointsTr2', 0), ('NumResamplings', 20), ('NumSamplesNotNan', 20), ('P-value', None), ('SdNullDistr', 0.0), ('TSMC_TpRawOverlapStat', 0L)]], \
           ["segs"],["segsLen1"],'[tails:=two-tail:] [trackNameIntensity:=nums] [rawStatistic:=TpRawOverlapStat] [assumptions:=_SegsSampledByIntensityTrack] [numResamplings:_Resamplings=20] [maxSamples:=20:] -> RandomizationManagerStat','TestGenome:chr21:10000001-12000000','1000000')

#def testMeanInsideOutsideTwoTailRandStat(self):
    #    self._assertRunEqual([[('Result', 0.3)], [('Result', 0.0)]],\
    #       ["segsMany"],["nums"],'[tails:=two-tail:][numResamplings:=10:] -> MeanInsideOutsideTwoTailRandStat','TestGenome:chr21:10000001-10010000','5000')
    
    def testCustomRStatMC(self):
        f = tempfile.NamedTemporaryFile('w')
        f.write('#Use in Monte Carlo'+os.linesep)
        f.write('return (sum(track1[3,]) + rnorm(1) )')
        f.flush()
        fn = f.name.encode('hex_codec')
        self._assertRunEqual([ [('DiffFromMean', 1.339094067690894), ('MeanOfNullDistr', 331878.20286021708), ('MedianOfNullDistr', 331877.98690898973), ('NumMoreExtremeThanObs', 3), ('NumPointsTr1', 5000), ('NumPointsTr2', 8), ('NumResamplings', 20), ('NumSamplesNotNan', 20), ('P-value', 0.19047619047619047), ('SdNullDistr', 0.95301654224649146), ('TSMC_BasicCustomRStat', 331879.5419542849)], [('DiffFromMean', 0.15747017646208405), ('MeanOfNullDistr', 341672.45392546954), ('MedianOfNullDistr', 341672.3240312665), ('NumMoreExtremeThanObs', 9), ('NumPointsTr1', 5000), ('NumPointsTr2', 4), ('NumResamplings', 20), ('NumSamplesNotNan', 20), ('P-value', 0.47619047619047616), ('SdNullDistr', 0.78302639824736542), ('TSMC_BasicCustomRStat', 341672.611395646)]],\
           ["nums"],["segsMany"],'[scriptFn:='+fn+':][tails:=right-tail:] -> CustomRStat','TestGenome:chr21:10000001-10010000','5000')
           
#    def testGenomeWideRandmizedRegionRun(self):
#        self._assertRunEqual([[('Result', 0.2)], [('Result', 0.0)], [('Result', 0.0)], [('Result', 1.0)]],\
#            ["segs"],["segsMany"],'[tails:=two-tail:][numResamplings:=5:] -> GenomeWideRandStat','TestGenome:chr21:10000000-10200000','50000')

    def runTest(self):
        #self.testSegmentOverlapsHighPresReshuffledStat()
        #self.testSimilarSegmentsReshuffledStat()
        self.testSegmentOverlapsSegsByIntensityStat()
        pass
    
if __name__ == "__main__":
    if len(sys.argv) == 2:
        TestRandomization.VERBOSE = ast.literal_eval(sys.argv[1])
        sys.argv = sys.argv[:-1]
    #TestRandomization().debug()
    #TestRandomization().run()
    unittest.main()
