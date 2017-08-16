#!/usr/bin/env python
import ast
import unittest
from test.integration.GalaxyIntegrationTest import GalaxyIntegrationTest
from gold.statistic.AllStatistics import DiffRelFreqPValStat
from quick.application.UserBinSource import UserBinSource
import tempfile
from numpy import nan, array, uint32, uint64
import sys


class TestStatistics(GalaxyIntegrationTest):
    def testCountStat(self):
        self._assertRunEqual([[('Result', 119121)], [('Result', 0)]],\
           ["segsMany"],[],'CountStat','TestGenome:chr21:10000001-11000000','500000')

    def testProportionCountStat(self):
        self._assertRunEqual([[('Result', 0.238242)], [('Result', 0)]],\
           ["segsMany"],[],'ProportionCountStat','TestGenome:chr21:10000001-11000000','500000')

    def testRawOverlapStat(self):
        self._assertRunEqual([[('Both', 45732), ('Neither', 335724), ('Only1', 73389), ('Only2', 45155)], [('Both', 0), ('Neither', 500000), ('Only1', 0), ('Only2', 0)]],\
            ["segsMany"],["segs"],'RawOverlapStat','TestGenome:chr21:10000001-11000000','500000')

    def testCountPointStat(self):
        self._assertRunEqual([[('Result', 447)], [('Result', 0)]],\
           ["segsMany"],[],'CountPointStat','TestGenome:chr21:10000001-11000000','500000')

    def testMeanOfMeanSdStat(self):
        self._assertRunEqual([[('meanOfMean', 1.0),('meanOfStdDev', 2.0)], []],\
           ["segsMeanSd"],[],'MeanOfMeanSdStat','TestGenome:chr21:1-10000','5000')

    def testCountPointAllowingOverlapStat(self):
        self._assertRunEqual([[('Result', 451)], [('Result', 0)]],\
           ["segsMany"],[],'CountPointAllowingOverlapStat','TestGenome:chr21:10000001-11000000','500000')

    def testDerivedOverlapStat(self):
        self._assertRunEqual([[('1in2', 3.3008780423396855), ('1inside2', 0.6), ('1outside2', 0.18176981769817699), ('2in1', 6.7520052372726571), ('2inside1', 3.300802094909063e-05), ('2outside1', 4.8886249031441187e-06), ('expOverlap', 0.90887), ('intersectionToUnionRatio', 3.3007294612109276e-05), ('overlapToExpOverlapRatio', 3.300802094909063)], []],\
           ["segs"],["segsLen1"],'DerivedOverlapStat','TestGenome:chr21:10000001-11000000','500000')

    def testAccuracyStat(self):
        self._assertRunEqual([[('cc', -0.025049347917182399), ('hammingDistance', 52194.0), ('precision', 0.46571726194723101), ('recall', 0.68870412965034078)], [('cc', -0.010647574707691357), ('hammingDistance', 58548.0), ('precision', 0.62932525951557095), ('recall', 0.2048334115438761)]],\
           ["segs"],["segsMany"],'AccuracyStat','TestGenome:chr21:10000001-10200000','100000')

    def testPointPositioningPValStat(self):
        self._assertRunEqual([[('Distribution', 'Normal approximation'), ('N', 43), ('P-value', 0.016785313177222032), ('Test statistic: W12', 297.0), ('altHyp', 'ha1')], [('Distribution', 'N/A'), ('N', 0), ('P-value', None), ('Test statistic: W12', 0), ('altHyp', 'ha1')]],\
           ["segsMany"],["segs"],'Dummy [assumptions:=independentPoints:] [tail:=ha1:] -> PointPositioningPValStat','TestGenome:chr21:10000001-12000000','1000000')

    #@unittest.SkipTest
    def testPointCountInSegsPvalStat(self):
        self._assertRunEqual([[('DiffFromExpected', 137.37351100000001), ('E(Test statistic): ExpPointsInside', 40.626488999999999), ('P-value', 0.0), ('PointsTotal', 447), ('SegCoverage', 0.090886999999999996), ('Test statistic: PointsInside', 178)], []], \
           ["segsMany"],["segs"],'Dummy [assumptions:=poissonPoints:] -> PointCountInSegsPvalStat','TestGenome:chr21:10000001-12000000','1000000')

    def testHigherFunctionInSegsPValStat(self):
        self._assertRunEqual([[('P-value', 0.0), ('Test statistic: T-score', -110.31444260717221), ('diffOfMeanInsideOutside', -2.0027601830846322), ('meanInside', 67.998406240717003), ('meanOutside', 70.001166423801635), ('varInside', 15.273266218843471), ('varOutside', 17.62805051010037)], [('P-value', nan), ('Test statistic: T-score', nan), ('diffOfMeanInsideOutside', nan), ('meanInside', nan), ('meanOutside', 73.330117985131494), ('varInside', nan), ('varOutside', 3.368940587350831)]],\
           ["segs"],["nums"],'HigherFunctionInSegsPValStat','TestGenome:chr21:10000001-10400000','200000')

    def testDiffRelFreqPValStat(self):
        #DiffRelFreqPValStat.cfgGlobalSource = UserBinSource('TestGenome:chr21:10000001-15000000','1000000')
        DiffRelFreqPValStat.MIN_POP_FOR_GAUSSIAN_APPROXIMATION = 2
        self._assertRunEqual([[('CountTrack1', 447), ('CountTrack2', 2), ('EstDiff', -0.10854430379746835), ('P-value', 0.81033860025943638), ('SEDiff', 0.12346579381820473), ('Test statistic: Z-score', -0.8791447447970302)], [('CountTrack1', 0), ('CountTrack2', 0), ('EstDiff', 0.0), ('P-value', None), ('SEDiff', None), ('Test statistic: Z-score', None)]],\
           ["segsMany"],["segs"],'Dummy [globalSource:=test:] -> DiffRelFreqPValStat','TestGenome:chr21:10000001-11000000','500000')

    def testDiffOfMeanInsideOutsideStat(self):
        self._assertRunEqual([[('Result', -1.02224308506662)], [('Result', -0.5900265413161776)]],\
           ["segs"],["nums"],'DiffOfMeanInsideOutsideStat','TestGenome:chr21:10000001-10200000','100000')

    def testNearestPointDistsStat(self):
        self._assertRunEqual([[('Result', [423, 995])], [('Result', [])]],\
           ["segs"],["segsMany"],'NearestPointDistsStat','TestGenome:chr21:10000001-12000000','1000000')

    def testCustomRStatBasic(self):
        f = tempfile.NamedTemporaryFile('w')
        f.write('return(sum(track2[3,]))')
        f.flush()
        fn = f.name.encode('hex_codec')

        self._assertRunEqual([[('Result', 331878.279)], [('Result', 341672.234)]],\
           ["segsMany"],["nums"],'[scriptFn:='+fn+':] -> CustomRStat','TestGenome:chr21:10000001-10010000','5000')

    def testDataComparisonStat(self):
        self._assertRunEqual([[('Result', [331878.279, 3490])], [('Result', [341672.234, 384])]],\
           ["nums"],["segsMany"],'[track1SummarizerName:=SumStat:] [track2SummarizerName:=CountStat:] -> DataComparisonStat','TestGenome:chr21:10000001-10010000','5000')

    def testROCScoreFuncValBasedStat(self):
        self._assertRunEqual([[('Result', 0.77777778)], [('Result', 0.5)]],\
           ["tcMarkedSegs"],["nums"],'ROCScoreFuncValBasedStat','TestGenome:chr21:26000001-27000000','500000')

    def testROCScoreOverlapBasedStat(self):
        self._assertRunEqual([[('Result', 0.5)], [('Result', 0.5)]],\
           ["tcMarkedSegs"],["segs"],'ROCScoreOverlapBasedStat','TestGenome:chr21:10000001-11000000','500000')

    def testNearestPointDistPValStat(self):
        self._assertRunEqual([[('P-value', 0.31603053435114503)], [('P-value', None)]],\
           ["segs"],["segsMany"],'NearestPointDistPValStat','TestGenome:chr21:10000001-12000000','1000000')

    def testCorrCoefStat(self):
        self._assertRunEqual([[('Result', -0.2184815145471653)], [('Result', -0.2299035655969795)]],\
           ["nums"],["nums2"],'CorrCoefStat','TestGenome:chr21:10000001-10200000','100000')

    def testSimpleFunctionCorrelationPvalStat(self):
        self._assertRunEqual([[('P-value', 0.0), ('Test statistic: pearson', -110.1530291776199)], [('P-value', 0.0), ('Test statistic: pearson', -360.783609248802)]],\
           ["nums"],["nums2"],'SimpleFunctionCorrelationPvalStat','TestGenome:chr21:10000001-10400000','200000')

    ##Without overlaps between categories:
    #
    #def testGeneralOneCatTrackStat(self):
    #    self._assertRunEqual([[('DNA', 16605), ('LINE', 211836), ('LTR', 122475), ('Low_complexity', 12594), ('Other', 2705), ('SINE', 82589), ('Satellite', 11197), ('Simple_repeat', 16282), ('Unknown', 73), ('rRNA', 1036), ('scRNA', 198), ('snRNA', 107), ('tRNA', 58)], [('DNA', 22968), ('LINE', 202898), ('LTR', 103598), ('Low_complexity', 15356), ('Other', 644), ('RNA', 99), ('SINE', 65097), ('Simple_repeat', 12151), ('snRNA', 106)]],\
    #        ["catSegs"],[],'[rawStatistic:=CountStat:] -> GeneralOneCatTrackStat','TestGenome:chr21:14000001-16000000','1000000', globalTarget=[('DNA', 39573), ('LINE', 414734), ('LTR', 226073), ('Low_complexity', 27950), ('Other', 3349), ('RNA', 99), ('SINE', 147686), ('Satellite', 11197), ('Simple_repeat', 28433), ('Unknown', 73), ('rRNA', 1036), ('scRNA', 198), ('snRNA', 213), ('tRNA', 58)])
    #
    #def testGeneralOneCatTrackStat2(self):
    #    self._assertRunEqual([[('DNA', 16605), ('LINE', 211836), ('LTR', 122475), ('Low_complexity', 12594), ('Other', 2705), ('SINE', 82589), ('Satellite', 11197), ('Simple_repeat', 16282), ('Unknown', 73), ('rRNA', 1036), ('scRNA', 198), ('snRNA', 107), ('tRNA', 58)], [('DNA', 22968), ('LINE', 202898), ('LTR', 103598), ('Low_complexity', 15356), ('Other', 644), ('RNA', 99), ('SINE', 65097), ('Simple_repeat', 12151), ('snRNA', 106)]],\
    #        ["catSegs"],[],'[rawStatistic:=CountStat:] -> GeneralOneCatTrackJoinWithDictSumStat','TestGenome:chr21:14000001-16000000','1000000', globalTarget=[('DNA', 39573), ('LINE', 414734), ('LTR', 226073), ('Low_complexity', 27950), ('Other', 3349), ('RNA', 99), ('SINE', 147686), ('Satellite', 11197), ('Simple_repeat', 28433), ('Unknown', 73), ('rRNA', 1036), ('scRNA', 198), ('snRNA', 213), ('tRNA', 58)])
    #
    #def testGeneralOneCatTrackStat(self):
    #    self._assertRunEqual([[('DNA', 17867), ('LINE', 208851), ('LTR', 130550), ('Low_complexity', 7079), ('Other', 2705), ('SINE', 87311), ('Satellite', 8466), ('Simple_repeat', 14838), ('Unknown', 73), ('rRNA', 736), ('scRNA', 198), ('snRNA', 150), ('tRNA', 97)], [('DNA', 27514), ('LINE', 198519), ('LTR', 104011), ('Low_complexity', 5789), ('Other', 644), ('RNA', 99), ('SINE', 79468), ('Simple_repeat', 7646), ('snRNA', 106)]],\
    #        ["catSegs"],[],'[rawStatistic:=CountStat:] -> GeneralOneCatTrackStat','TestGenome:chr21:14000001-16000000','1000000', \
    #                         globalTarget=[('DNA', 45381), ('LINE', 407370), ('LTR', 234561), ('Low_complexity', 12868), ('Other', 3349), ('RNA', 99.0), ('SINE', 166779), ('Satellite', 8466.0), ('Simple_repeat', 22484), ('Unknown', 73.0), ('rRNA', 736.0), ('scRNA', 198.0), ('snRNA', 256), ('tRNA', 97.0)])
    #
    #def testGeneralOneCatTrackStat2(self):
    #    self._assertRunEqual([[('DNA', 17867), ('LINE', 208851), ('LTR', 130550), ('Low_complexity', 7079), ('Other', 2705), ('SINE', 87311), ('Satellite', 8466), ('Simple_repeat', 14838), ('Unknown', 73), ('rRNA', 736), ('scRNA', 198), ('snRNA', 150), ('tRNA', 97)], [('DNA', 27514), ('LINE', 198519), ('LTR', 104011), ('Low_complexity', 5789), ('Other', 644), ('RNA', 99), ('SINE', 79468), ('Simple_repeat', 7646), ('snRNA', 106)]],\
    #        ["catSegs"],[],'[rawStatistic:=CountStat:] -> GeneralOneCatTrackJoinWithDictSumStat','TestGenome:chr21:14000001-16000000','1000000', \
    #                         globalTarget=[('DNA', 45381), ('LINE', 407370), ('LTR', 234561), ('Low_complexity', 12868), ('Other', 3349), ('RNA', 99.0), ('SINE', 166779), ('Satellite', 8466.0), ('Simple_repeat', 22484), ('Unknown', 73.0), ('rRNA', 736.0), ('scRNA', 198.0), ('snRNA', 256), ('tRNA', 97.0)])

    def testBpCoverageByCatStat(self):
        self._assertRunEqual([[('DNA', 17865), ('LINE', 208718), ('LTR', 130168), ('Low_complexity', 7079), ('Other', 2705), ('SINE', 87240), ('Satellite', 8466), ('Simple_repeat', 14479), ('Unknown', 73), ('rRNA', 733), ('scRNA', 198), ('snRNA', 150), ('tRNA', 97)], [('DNA', 27387), ('LINE', 198315), ('LTR', 103965), ('Low_complexity', 5789), ('Other', 644), ('RNA', 99), ('SINE', 79425), ('Simple_repeat', 7639), ('snRNA', 106)]],\
            ["catSegs"],[],'BpCoverageByCatStat','TestGenome:chr21:14000001-16000000','1000000')

#    def testGeneralTwoTracksOneCatTrackStat(self):
#        self._assertRunEqual([[('DNA', {'Both': 3107, 'Neither': 801705, 'Only2': 180432, 'Only1': 14756}), ('LINE', {'Both': 59949, 'Neither': 667799, 'Only2': 123511, 'Only1': 148636}), ('LTR', {'Both': 19020, 'Neither': 705326, 'Only2': 164877, 'Only1': 110766}), ('Low_complexity', {'Both': 1592, 'Neither': 810976, 'Only2': 181945, 'Only1': 5487}), ('Other', {'Both': 0, 'Neither': 813758, 'Only2': 183537, 'Only1': 2705}), ('SINE', {'Both': 13682, 'Neither': 742906, 'Only2': 169924, 'Only1': 73487}), ('Satellite', {'Both': 0, 'Neither': 807997, 'Only2': 183537, 'Only1': 8466}), ('Simple_repeat', {'Both': 1752, 'Neither': 803736, 'Only2': 182144, 'Only1': 12368}), ('Unknown', {'Both': 0, 'Neither': 816390, 'Only2': 183537, 'Only1': 73}), ('rRNA', {'Both': 0, 'Neither': 815730, 'Only2': 183540, 'Only1': 730}), ('scRNA', {'Both': 0, 'Neither': 816265, 'Only2': 183537, 'Only1': 198}), ('snRNA', {'Both': 0, 'Neither': 816313, 'Only2': 183537, 'Only1': 150}), ('tRNA', {'Both': 39, 'Neither': 816405, 'Only2': 183498, 'Only1': 58})], [('DNA', {'Both': 163, 'Neither': 965484, 'Only2': 7256, 'Only1': 27097}), ('LINE', {'Both': 0, 'Neither': 794393, 'Only2': 7496, 'Only1': 198111}), ('LTR', {'Both': 0, 'Neither': 888743, 'Only2': 7338, 'Only1': 103919}), ('Low_complexity', {'Both': 0, 'Neither': 986919, 'Only2': 7292, 'Only1': 5789}), ('Other', {'Both': 0, 'Neither': 992064, 'Only2': 7292, 'Only1': 644}), ('RNA', {'Both': 0, 'Neither': 992609, 'Only2': 7292, 'Only1': 99}), ('SINE', {'Both': 0, 'Neither': 913283, 'Only2': 7335, 'Only1': 79382}), ('Simple_repeat', {'Both': 58, 'Neither': 985127, 'Only2': 7241, 'Only1': 7574}), ('snRNA', {'Both': 0, 'Neither': 992602, 'Only2': 7292, 'Only1': 106})]],
#            ["catSegs"],["segs"],'[rawStatistic:=RawOverlapStat:] -> GeneralOneCatTrackStat','TestGenome:chr21:14000001-16000000','1000000', \
#                             globalTarget=[('DNA', {'Both': 3270, 'Neither': 1767189, 'Only2': 187688, 'Only1': 41853}), ('LINE', {'Both': 59949, 'Neither': 1462192, 'Only2': 131007, 'Only1': 346747}), ('LTR', {'Both': 19020, 'Neither': 1594069, 'Only2': 172215, 'Only1': 214685}), ('Low_complexity', {'Both': 1592, 'Neither': 1797895, 'Only2': 189237, 'Only1': 11276}), ('Other', {'Both': 0, 'Neither': 1805822, 'Only2': 190829, 'Only1': 3349}), ('RNA', {'Both': 0, 'Neither': 992609, 'Only2': 7292, 'Only1': 99}), ('SINE', {'Both': 13682, 'Neither': 1656189, 'Only2': 177259, 'Only1': 152869}), ('Satellite', {'Both': 0, 'Neither': 807997, 'Only2': 183537, 'Only1': 8466}), ('Simple_repeat', {'Both': 1810, 'Neither': 1788863, 'Only2': 189385, 'Only1': 19942}), ('Unknown', {'Both': 0, 'Neither': 816390, 'Only2': 183537, 'Only1': 73}), ('rRNA', {'Both': 0, 'Neither': 815730, 'Only2': 183540, 'Only1': 730}), ('scRNA', {'Both': 0, 'Neither': 816265, 'Only2': 183537, 'Only1': 198}), ('snRNA', {'Both': 0, 'Neither': 1808915, 'Only2': 190829, 'Only1': 256}), ('tRNA', {'Both': 39, 'Neither': 816405, 'Only2': 183498, 'Only1': 58})])

#    def testGeneralTwoTracksOneCatTrackStat2(self):
#        self._assertRunEqual([[('DNA', {'Both': 3107, 'Neither': 801705, 'Only2': 180432, 'Only1': 14756}), ('LINE', {'Both': 59949, 'Neither': 667799, 'Only2': 123511, 'Only1': 148636}), ('LTR', {'Both': 19020, 'Neither': 705326, 'Only2': 164877, 'Only1': 110766}), ('Low_complexity', {'Both': 1592, 'Neither': 810976, 'Only2': 181945, 'Only1': 5487}), ('Other', {'Both': 0, 'Neither': 813758, 'Only2': 183537, 'Only1': 2705}), ('SINE', {'Both': 13682, 'Neither': 742906, 'Only2': 169924, 'Only1': 73487}), ('Satellite', {'Both': 0, 'Neither': 807997, 'Only2': 183537, 'Only1': 8466}), ('Simple_repeat', {'Both': 1752, 'Neither': 803736, 'Only2': 182144, 'Only1': 12368}), ('Unknown', {'Both': 0, 'Neither': 816390, 'Only2': 183537, 'Only1': 73}), ('rRNA', {'Both': 0, 'Neither': 815730, 'Only2': 183540, 'Only1': 730}), ('scRNA', {'Both': 0, 'Neither': 816265, 'Only2': 183537, 'Only1': 198}), ('snRNA', {'Both': 0, 'Neither': 816313, 'Only2': 183537, 'Only1': 150}), ('tRNA', {'Both': 39, 'Neither': 816405, 'Only2': 183498, 'Only1': 58})], [('DNA', {'Both': 163, 'Neither': 965484, 'Only2': 7256, 'Only1': 27097}), ('LINE', {'Both': 0, 'Neither': 794393, 'Only2': 7496, 'Only1': 198111}), ('LTR', {'Both': 0, 'Neither': 888743, 'Only2': 7338, 'Only1': 103919}), ('Low_complexity', {'Both': 0, 'Neither': 986919, 'Only2': 7292, 'Only1': 5789}), ('Other', {'Both': 0, 'Neither': 992064, 'Only2': 7292, 'Only1': 644}), ('RNA', {'Both': 0, 'Neither': 992609, 'Only2': 7292, 'Only1': 99}), ('SINE', {'Both': 0, 'Neither': 913283, 'Only2': 7335, 'Only1': 79382}), ('Simple_repeat', {'Both': 58, 'Neither': 985127, 'Only2': 7241, 'Only1': 7574}), ('snRNA', {'Both': 0, 'Neither': 992602, 'Only2': 7292, 'Only1': 106})]],\
#            ["catSegs"],["segs"],'[rawStatistic:=RawOverlapStat:] -> GeneralOneCatTrackJoinWithDoubleDictSumStat','TestGenome:chr21:14000001-16000000','1000000',\
#                             globalTarget=[('DNA', {'Both': 3270, 'Neither': 1767189, 'Only2': 187688, 'Only1': 41853}), ('LINE', {'Both': 59949, 'Neither': 1462192, 'Only2': 131007, 'Only1': 346747}), ('LTR', {'Both': 19020, 'Neither': 1594069, 'Only2': 172215, 'Only1': 214685}), ('Low_complexity', {'Both': 1592, 'Neither': 1797895, 'Only2': 189237, 'Only1': 11276}), ('Other', {'Both': 0, 'Neither': 1805822, 'Only2': 190829, 'Only1': 3349}), ('RNA', {'Both': 0, 'Neither': 992609, 'Only2': 7292, 'Only1': 99}), ('SINE', {'Both': 13682, 'Neither': 1656189, 'Only2': 177259, 'Only1': 152869}), ('Satellite', {'Both': 0, 'Neither': 807997, 'Only2': 183537, 'Only1': 8466}), ('Simple_repeat', {'Both': 1810, 'Neither': 1788863, 'Only2': 189385, 'Only1': 19942}), ('Unknown', {'Both': 0, 'Neither': 816390, 'Only2': 183537, 'Only1': 73}), ('rRNA', {'Both': 0, 'Neither': 815730, 'Only2': 183540, 'Only1': 730}), ('scRNA', {'Both': 0, 'Neither': 816265, 'Only2': 183537, 'Only1': 198}), ('snRNA', {'Both': 0, 'Neither': 1808915, 'Only2': 190829, 'Only1': 256}), ('tRNA', {'Both': 39, 'Neither': 816405, 'Only2': 183498, 'Only1': 58})])

#    def testGeneralTwoCatTracksStat(self):
#        self._assertRunEqual([[('FV', {'LTR': 555, 'Satellite': 0, 'rRNA': 0, 'DNA': 0, 'Simple_repeat': 0, 'Unknown': 0, 'scRNA': 0, 'snRNA': 0, 'Other': 0, 'tRNA': 0, 'LINE': 397, 'SINE': 171, 'Low_complexity': 0}), ('HIV', {'LTR': 0, 'Satellite': 0, 'rRNA': 0, 'DNA': 0, 'Simple_repeat': 0, 'Unknown': 0, 'scRNA': 0, 'snRNA': 0, 'Other': 0, 'tRNA': 0, 'LINE': 311, 'SINE': 0, 'Low_complexity': 0}), ('HTLV1', {'LTR': 87, 'Satellite': 0, 'rRNA': 0, 'DNA': 0, 'Simple_repeat': 0, 'Unknown': 0, 'scRNA': 0, 'snRNA': 0, 'Other': 0, 'tRNA': 0, 'LINE': 0, 'SINE': 0, 'Low_complexity': 0}), ('MLV', {'LTR': 0, 'Satellite': 0, 'rRNA': 0, 'DNA': 0, 'Simple_repeat': 0, 'Unknown': 0, 'scRNA': 0, 'snRNA': 0, 'Other': 0, 'tRNA': 0, 'LINE': 0, 'SINE': 0, 'Low_complexity': 0}), ('SIV', {'LTR': 0, 'Satellite': 0, 'rRNA': 0, 'DNA': 0, 'Simple_repeat': 0, 'Unknown': 0, 'scRNA': 0, 'snRNA': 0, 'Other': 0, 'tRNA': 0, 'LINE': 0, 'SINE': 1, 'Low_complexity': 0})], [('FV', {'LTR': 655, 'snRNA': 0, 'Other': 0, 'DNA': 0, 'Simple_repeat': 46, 'LINE': 367, 'SINE': 39, 'RNA': 0, 'Low_complexity': 0}), ('HTLV1', {'LTR': 0, 'snRNA': 0, 'Other': 0, 'DNA': 0, 'Simple_repeat': 0, 'LINE': 177, 'SINE': 0, 'RNA': 0, 'Low_complexity': 0})]],
#                             ["catSegs2"],["catSegs"],'[rawStatistic:=TpRawOverlapStat:] -> GeneralTwoCatTracksJoinWithDoubleDictSumStat','TestGenome:chr21:14000001-16000000','1000000', \
#                             globalTarget=[('FV', {'LTR': 1210, 'Satellite': 0, 'rRNA': 0, 'DNA': 0, 'Simple_repeat': 46, 'Unknown': 0, 'scRNA': 0, 'Low_complexity': 0, 'Other': 0, 'tRNA': 0, 'LINE': 764, 'SINE': 210, 'RNA': 0, 'snRNA': 0}), ('HIV', {'LTR': 0, 'Satellite': 0, 'rRNA': 0, 'DNA': 0, 'Simple_repeat': 0, 'Unknown': 0, 'scRNA': 0, 'Low_complexity': 0, 'Other': 0, 'tRNA': 0, 'LINE': 311, 'SINE': 0, 'snRNA': 0}), ('HTLV1', {'LTR': 87, 'Satellite': 0, 'rRNA': 0, 'DNA': 0, 'Simple_repeat': 0, 'Unknown': 0, 'scRNA': 0, 'Low_complexity': 0, 'Other': 0, 'tRNA': 0, 'LINE': 177, 'SINE': 0, 'RNA': 0, 'snRNA': 0}), ('MLV', {'LTR': 0, 'Satellite': 0, 'rRNA': 0, 'DNA': 0, 'Simple_repeat': 0, 'Unknown': 0, 'scRNA': 0, 'Low_complexity': 0, 'Other': 0, 'tRNA': 0, 'LINE': 0, 'SINE': 0, 'snRNA': 0}), ('SIV', {'LTR': 0, 'Satellite': 0, 'rRNA': 0, 'DNA': 0, 'Simple_repeat': 0, 'Unknown': 0, 'scRNA': 0, 'Low_complexity': 0, 'Other': 0, 'tRNA': 0, 'LINE': 0, 'SINE': 1, 'snRNA': 0})])

#    def testGeneralTwoCatTracksStat2(self):
#        self._assertRunEqual([[('FV', {'LTR': 555, 'Satellite': 0, 'rRNA': 0, 'DNA': 0, 'Simple_repeat': 0, 'Unknown': 0, 'scRNA': 0, 'snRNA': 0, 'Other': 0, 'tRNA': 0, 'LINE': 397, 'SINE': 171, 'Low_complexity': 0}), ('HIV', {'LTR': 0, 'Satellite': 0, 'rRNA': 0, 'DNA': 0, 'Simple_repeat': 0, 'Unknown': 0, 'scRNA': 0, 'snRNA': 0, 'Other': 0, 'tRNA': 0, 'LINE': 311, 'SINE': 0, 'Low_complexity': 0}), ('HTLV1', {'LTR': 87, 'Satellite': 0, 'rRNA': 0, 'DNA': 0, 'Simple_repeat': 0, 'Unknown': 0, 'scRNA': 0, 'snRNA': 0, 'Other': 0, 'tRNA': 0, 'LINE': 0, 'SINE': 0, 'Low_complexity': 0}), ('MLV', {'LTR': 0, 'Satellite': 0, 'rRNA': 0, 'DNA': 0, 'Simple_repeat': 0, 'Unknown': 0, 'scRNA': 0, 'snRNA': 0, 'Other': 0, 'tRNA': 0, 'LINE': 0, 'SINE': 0, 'Low_complexity': 0}), ('SIV', {'LTR': 0, 'Satellite': 0, 'rRNA': 0, 'DNA': 0, 'Simple_repeat': 0, 'Unknown': 0, 'scRNA': 0, 'snRNA': 0, 'Other': 0, 'tRNA': 0, 'LINE': 0, 'SINE': 1, 'Low_complexity': 0})], [('FV', {'LTR': 655, 'snRNA': 0, 'Other': 0, 'DNA': 0, 'Simple_repeat': 46, 'LINE': 367, 'SINE': 39, 'RNA': 0, 'Low_complexity': 0}), ('HTLV1', {'LTR': 0, 'snRNA': 0, 'Other': 0, 'DNA': 0, 'Simple_repeat': 0, 'LINE': 177, 'SINE': 0, 'RNA': 0, 'Low_complexity': 0})]],
#                             ["catSegs2"],["catSegs"],'[rawStatistic:=TpRawOverlapStat:] -> GeneralTwoCatTracksStat','TestGenome:chr21:14000001-16000000','1000000', \
#                             globalTarget=[('FV', {'LTR': 1210, 'Satellite': 0, 'rRNA': 0, 'DNA': 0, 'Simple_repeat': 46, 'Unknown': 0, 'scRNA': 0, 'Low_complexity': 0, 'Other': 0, 'tRNA': 0, 'LINE': 764, 'SINE': 210, 'RNA': 0, 'snRNA': 0}), ('HIV', {'LTR': 0, 'Satellite': 0, 'rRNA': 0, 'DNA': 0, 'Simple_repeat': 0, 'Unknown': 0, 'scRNA': 0, 'Low_complexity': 0, 'Other': 0, 'tRNA': 0, 'LINE': 311, 'SINE': 0, 'snRNA': 0}), ('HTLV1', {'LTR': 87, 'Satellite': 0, 'rRNA': 0, 'DNA': 0, 'Simple_repeat': 0, 'Unknown': 0, 'scRNA': 0, 'Low_complexity': 0, 'Other': 0, 'tRNA': 0, 'LINE': 177, 'SINE': 0, 'RNA': 0, 'snRNA': 0}), ('MLV', {'LTR': 0, 'Satellite': 0, 'rRNA': 0, 'DNA': 0, 'Simple_repeat': 0, 'Unknown': 0, 'scRNA': 0, 'Low_complexity': 0, 'Other': 0, 'tRNA': 0, 'LINE': 0, 'SINE': 0, 'snRNA': 0}), ('SIV', {'LTR': 0, 'Satellite': 0, 'rRNA': 0, 'DNA': 0, 'Simple_repeat': 0, 'Unknown': 0, 'scRNA': 0, 'Low_complexity': 0, 'Other': 0, 'tRNA': 0, 'LINE': 0, 'SINE': 1, 'snRNA': 0})])

#    def testGeneralTwoCatTracksMatrixStat(self):
#        self._assertRunEqual([[('Cols', ['LTR', 'Satellite', 'rRNA', 'DNA', 'Simple_repeat', 'Unknown', 'scRNA', 'Low_complexity', 'Other', 'tRNA', 'LINE', 'SINE', 'snRNA']), ('Matrix', [[87, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 311, 0, 0], [555, 0, 0, 0, 0, 0, 0, 0, 0, 0, 397, 171, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0]]), ('Rows', ['HTLV1', 'MLV', 'HIV', 'FV', 'SIV'])], [('Cols', ['LTR', 'DNA', 'snRNA', 'RNA', 'Low_complexity', 'Other', 'LINE', 'SINE', 'Simple_repeat']), ('Matrix', [[0, 0, 0, 0, 0, 177, 0, 0, 0], [655, 0, 0, 0, 46, 367, 39, 0, 0]]), ('Rows', ['HTLV1', 'FV'])]], \
#                             ["catSegs2"],["catSegs"],'[rawStatistic:=TpRawOverlapStat:] -> GeneralTwoTracksIterateValsMatrixStat','TestGenome:chr21:14000001-16000000','1000000', \
#                             globalTarget=[('Cols', ['LTR', 'Satellite', 'rRNA', 'DNA', 'Simple_repeat', 'Unknown', 'scRNA', 'snRNA', 'Other', 'tRNA', 'LINE', 'SINE', 'RNA', 'Low_complexity']), ('Matrix', [[1210, 0, 0, 0, 46, 0, 0, 0, 0, 0, 764, 210, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 311, 0, 0], [87, 0, 0, 0, 0, 0, 0, 0, 0, 0, 177, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0]]), ('Rows', ['FV', 'MLV', 'HIV', 'HTLV1', 'SIV'])])

#    def testCategoryMatrixStat(self):
#        self._assertRunEqual([[('Cols', ['DNA', 'LINE', 'Low_complexity', 'LTR', 'Other', 'RNA', 'rRNA', 'Satellite', 'scRNA', 'Simple_repeat', 'SINE', 'snRNA', 'srpRNA', 'tRNA', 'Unknown']), ('Matrix', [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0], [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0]]), ('Rows', ['ASV', 'FV', 'HIV', 'HPV', 'HTLV1', 'MLV', 'SIV'])], [('Cols', ['DNA', 'LINE', 'Low_complexity', 'LTR', 'Other', 'RNA', 'rRNA', 'Satellite', 'scRNA', 'Simple_repeat', 'SINE', 'snRNA', 'srpRNA', 'tRNA', 'Unknown']), ('Matrix', [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]), ('Rows', ['ASV', 'FV', 'HIV', 'HPV', 'HTLV1', 'MLV', 'SIV'])]], \
#                             ["catSegs2"],["catSegs"],'[rawStatistic:=PointCountInsideSegsStat:] [tf1=SegmentToEndPointFormatConverter]-> CategoryMatrixStat','TestGenome:chr21:14000001-16000000','1000000', \
#                             globalTarget=[('Cols', ['DNA', 'LINE', 'Low_complexity', 'LTR', 'Other', 'RNA', 'rRNA', 'Satellite', 'scRNA', 'Simple_repeat', 'SINE', 'snRNA', 'srpRNA', 'tRNA', 'Unknown']), ('Matrix', [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 2, 0, 0, 0, 0], [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0]]), ('Rows', ['ASV', 'FV', 'HIV', 'HPV', 'HTLV1', 'MLV', 'SIV'])])

    def testCategoryMatrixStat(self):
        self._assertRunEqual([[('Result', {'Rows': ['ASV', 'FV', 'HIV', 'HPV', 'HTLV1', 'MLV', 'SIV'], 'Matrix': [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0], [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0]], 'Cols': ['DNA', 'LINE', 'Low_complexity', 'LTR', 'Other', 'RNA', 'rRNA', 'Satellite', 'scRNA', 'Simple_repeat', 'SINE', 'snRNA', 'srpRNA', 'tRNA', 'Unknown']})], [('Result', {'Rows': ['ASV', 'FV', 'HIV', 'HPV', 'HTLV1', 'MLV', 'SIV'], 'Matrix': [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], 'Cols': ['DNA', 'LINE', 'Low_complexity', 'LTR', 'Other', 'RNA', 'rRNA', 'Satellite', 'scRNA', 'Simple_repeat', 'SINE', 'snRNA', 'srpRNA', 'tRNA', 'Unknown']})]],
                             ["catSegs2"],["catSegs"],'[rawStatistic:=PointCountInsideSegsStat:] [tf1=SegmentToEndPointFormatConverter]-> CategoryMatrixStat','TestGenome:chr21:14000001-16000000','1000000', \
                             globalTarget=[('Result', {'Rows': ['ASV', 'FV', 'HIV', 'HPV', 'HTLV1', 'MLV', 'SIV'], 'Matrix': [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 2, 0, 0, 0, 0], [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0]], 'Cols': ['DNA', 'LINE', 'Low_complexity', 'LTR', 'Other', 'RNA', 'rRNA', 'Satellite', 'scRNA', 'Simple_repeat', 'SINE', 'snRNA', 'srpRNA', 'tRNA', 'Unknown']})])

#    def testCategoryPointCountInSegsMatrixStat(self):
#        self._assertRunEqual([[('Cols', ['DNA', 'LINE', 'LTR', 'Low_complexity', 'Other', 'SINE', 'Satellite', 'Simple_repeat', 'Unknown', 'rRNA', 'scRNA', 'snRNA', 'tRNA']), ('Matrix', [[0L, 0L, 1L, 0L, 0L, 1L, 0L, 0L, 0L, 0L, 0L, 0L, 0L], [0L, 1L, 0L, 0L, 0L, 0L, 0L, 0L, 0L, 0L, 0L, 0L, 0L], [0L, 0L, 0L, 0L, 0L, 1L, 0L, 0L, 0L, 0L, 0L, 0L, 0L], [0L, 0L, 0L, 0L, 0L, 0L, 0L, 0L, 0L, 0L, 0L, 0L, 0L], [0L, 0L, 0L, 0L, 0L, 1L, 0L, 0L, 0L, 0L, 0L, 0L, 0L]]), ('Rows', ['FV', 'HIV', 'HTLV1', 'MLV', 'SIV'])], [('Cols', ['DNA', 'LINE', 'LTR', 'Low_complexity', 'Other', 'RNA', 'SINE', 'Simple_repeat', 'snRNA']), ('Matrix', [[0L, 0L, 0L, 0L, 0L, 0L, 1L, 1L, 0L], [0L, 0L, 0L, 0L, 0L, 0L, 0L, 0L, 0L]]), ('Rows', ['FV', 'HTLV1'])]],
#                             ["catSegs2"],["catSegs"],'[tf1=SegmentToEndPointFormatConverter]-> CategoryPointCountInSegsMatrixStat','TestGenome:chr21:14000001-16000000','1000000', \
#                             globalTarget=[('Cols', ['DNA', 'LINE', 'Low_complexity', 'LTR', 'Other', 'RNA', 'rRNA', 'Satellite', 'scRNA', 'Simple_repeat', 'SINE', 'snRNA', 'srpRNA', 'tRNA', 'Unknown']), ('Matrix', [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 2, 0, 0, 0, 0], [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0]]), ('Rows', ['ASV', 'FV', 'HIV', 'HPV', 'HTLV1', 'MLV', 'SIV'])])

    def testCategoryPointCountInSegsMatrixStat(self):
        self._assertRunEqual([[('Result', {'Rows': array(['FV', 'HIV', 'HTLV1', 'MLV', 'SIV'], dtype='|S5'), 'Matrix': array([[0, 0, 1, 0, 1, 0, 0, 0, 0, 0], [0, 1, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 1, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 1, 0, 0, 0, 0, 0]], dtype=uint64), 'Cols': array(['DNA', 'LINE', 'LTR', 'Low_complexity', 'SINE', 'Satellite', 'Simple_repeat', 'rRNA', 'snRNA', 'tRNA'], dtype='|S14')})], [('Result', {'Rows': array(['FV'], dtype='|S5'), 'Matrix': array([[0, 0, 0, 0, 1, 1]], dtype=uint64), 'Cols': array(['DNA', 'LINE', 'LTR', 'Low_complexity', 'SINE', 'Simple_repeat'], dtype='|S14')})]], \
                             ["catSegs2"],["catSegs"],'[tf1=SegmentToEndPointFormatConverter]-> CategoryPointCountInSegsMatrixStat','TestGenome:chr21:14000001-16000000','1000000', \
                             globalTarget=[('Result', {'Rows': array(['FV', 'HIV', 'HTLV1', 'MLV', 'SIV'], dtype='|S5'), 'Matrix': array([[0, 0, 1, 0, 2, 0, 1, 0, 0, 0], [0, 1, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 1, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 1, 0, 0, 0, 0, 0]], dtype=uint64), 'Cols': array(['DNA', 'LINE', 'LTR', 'Low_complexity', 'SINE', 'Satellite', 'Simple_repeat', 'rRNA', 'snRNA', 'tRNA'], dtype='|S14')})])

    def testSameTrackRawOverlapStat(self):
        """Tests the analysis of a track as segments vs the same track as points"""
        self._assertRunEqual([[('Both', 447), ('Neither', 380879), ('Only1', 0), ('Only2', 118674)],
                              [('Both', 0), ('Neither', 500000), ('Only1', 0), ('Only2', 0)]],\
                             ["segsMany"], ["segsMany"], '[tf1=SegmentToStartPointFormatConverter] -> RawOverlapStat',
                             'TestGenome:chr21:10000001-11000000', '500000')

    def runTest(self):
        #self.testHigherFunctionInSegsPValStat()
        #self.testROCScoreFuncValBasedStat()
        #self.testNearestPointDistPValStat()
        #self.testNearestPointDistsStat()
        #self.testCountStat()
        #self.testNearestPointDistPValStat()
        #self.testDiffRelFreqPValStat()
        pass
    
if __name__ == "__main__":
    if len(sys.argv) == 2:
        TestStatistics.VERBOSE = ast.literal_eval(sys.argv[1])
        sys.argv = sys.argv[:-1]
    unittest.main()
    TestStatistics().run()
    TestStatistics().debug()
