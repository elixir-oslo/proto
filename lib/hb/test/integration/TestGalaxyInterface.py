#!/usr/bin/env python
import ast
import unittest
from test.integration.GalaxyIntegrationTest import GalaxyIntegrationTest
from gold.application.GalaxyInterface import GalaxyInterface
import os, sys
import gold.description.Analysis
import gold.statistic.Statistic
from config.Config import DebugConfig

class TestGalaxyInterface(GalaxyIntegrationTest):
    def testRun(self):
        self._assertRunEqual([[('Both', 0L), ('Neither', 29920), ('Only1', 1L), ('Only2', 20079L)], [('Both', 2L), ('Neither', 0), ('Only1', 0L), ('Only2', 49998L)]],\
            ["segsLen1"],["segs"],'RawOverlapStat','chr21:10000001-10100000','50000')

    def testRunValid(self):
        self.assertEqual(True, GalaxyInterface.runValid(["segsLen1"],["segs"],'RawOverlapStat','chr21:1-4001','2000','TestGenome'))
        self.assertNotEqual(True, GalaxyInterface.runValid(["segsLen1"],["segs"],'','TestGenome:chr21:1-4001','2000','TestGenome'))
        self.assertNotEqual(True, GalaxyInterface.runValid(["segsLen1"],["segs"],'RawOverlapStat','1-4001','2000','TestGenome'))
        self.assertNotEqual(True, GalaxyInterface.runValid(["segsLen1"],["segs"],'RawOverlapStat','TestGenome:chr21:1-4001','default','TestGenome'))
        self.assertNotEqual(True, GalaxyInterface.runValid(["segs"],["segs"],'','TestGenome:chr21:1-4001','default','TestGenome'))
        self.assertNotEqual(True, GalaxyInterface.runValid(["segs"],["segs"],'','TestGenome:chr21:1-4001','default','hg18'))

    def testRunBatchLines(self):
        self._assertBatchEqual([[[('Both', 0L), ('Neither', 29920), ('Only1', 1L), ('Only2', 20079L)], [('Both', 2L), ('Neither', 0), ('Only1', 0L), ('Only2', 49998L)]]],\
            ['TestGenome|chr21:10000001-10100000|50000|segsLen1|segs|RawOverlapStat'])

    def testRunSuperBatchLines(self):
        self._assertBatchEqual([[[('Both', 0L), ('Neither', 29920), ('Only1', 1L), ('Only2', 20079L)], [('Both', 2L), ('Neither', 0), ('Only1', 0L), ('Only2', 49998L)]], \
                                [[('Both', 8372L), ('Neither', 15169), ('Only1', 14752L), ('Only2', 11707L)], [('Both', 24265L), ('Neither', 0), ('Only1', 0L), ('Only2', 25735L)]]],\
            ['TestGenome|chr21:10000001-10100000|50000|segsLen1/segsMany|segs|RawOverlapStat'])

    def testGetStatOptions(self):
        if self.VERBOSE:
            DebugConfig.VERBOSE = True
            DebugConfig.PASS_ON_COMPUTE_EXCEPTIONS = True


        prevVal = DebugConfig.PASS_ON_VALIDSTAT_EXCEPTIONS
        DebugConfig.PASS_ON_VALIDSTAT_EXCEPTIONS= False
        self.assertTrue(len( GalaxyInterface.getStatOptions('TestGenome',['segsMany'], ['segs'], 'Hypothesis testing') ) > 0)
        self.assertTrue(len( GalaxyInterface.getStatOptions('TestGenome',['segsMany'], ['nums'], 'Hypothesis testing') ) > 0)
        DebugConfig.PASS_ON_VALIDSTAT_EXCEPTIONS= prevVal


    def testGetRunDescription(self):
        prevVal = DebugConfig.PASS_ON_VALIDSTAT_EXCEPTIONS
        DebugConfig.PASS_ON_VALIDSTAT_EXCEPTIONS = False
        analysisDef = 'Different frequency inside segments?:Are track1-points occurring [tail:Alternative hypothesis=different:with different frequency/more:more frequently/less:less frequently] inside track2-segment than outside? [rawStatistic:=PointCountInsideSegsStat:] [assumptions:_Assumptions=poissonPoints:Poisson-distributed points/_PermutedSegsAndSampledIntersegsTrack:Permuted segments, sampled spaces (MC)/_PermutedSegsAndIntersegsTrack:Permuted segments, permuted spaces (MC)/_RandomGenomeLocationTrack:Segments fetched from random genome location (MC)] [numResamplings:_Resamplings=20/200/2000] -> PointCountInSegsPvalStat, RandomizationManagerStat'
        GalaxyInterface.getRunDescription(['segsMany'], ['segs'], analysisDef, 'chr21:2-4001','2000', 'TestGenome')
        DebugConfig.PASS_ON_VALIDSTAT_EXCEPTIONS = prevVal

    def _assertExpandBedSegments(self, inContents, outContents, upFlank, downFlank,
                                 treatTrackAs, removeChrBorderCrossing, suffix):

        from tempfile import NamedTemporaryFile

        with NamedTemporaryFile(suffix=suffix) as inFile:
            inFile.write(inContents)
            inFile.flush()

            with NamedTemporaryFile(suffix=suffix) as outFile:
                GalaxyInterface.expandBedSegments(inFile.name, outFile.name, 'TestGenome', upFlank, downFlank,
                                                  treatTrackAs, removeChrBorderCrossing, suffix)

                expandedContents = outFile.read()

                self.assertEquals(outContents, expandedContents)

    def testExpandBedSegments(self):
        self._assertExpandBedSegments(
            '\t'.join(['chr21', '10', '20']) + os.linesep +
                '\t'.join(['chr21', '30', '40']) + os.linesep,
            '\t'.join(['chr21', '6', '26']) + os.linesep +
                '\t'.join(['chr21', '26', '46']) + os.linesep,
            upFlank=4, downFlank=6, treatTrackAs='segments', removeChrBorderCrossing=False, suffix='bed')

        self._assertExpandBedSegments(
            '\t'.join(['chr21', '10', '20', '.', '0', '+']) + os.linesep +
                '\t'.join(['chr21', '30', '40', '.', '0', '-']) + os.linesep,
            '\t'.join(['chr21', '6', '26', '.', '0', '+']) + os.linesep +
                '\t'.join(['chr21', '24', '44', '.', '0', '-']) + os.linesep,
            upFlank=4, downFlank=6, treatTrackAs='segments', removeChrBorderCrossing=False, suffix='bed')

        self._assertExpandBedSegments(
            '\t'.join(['chr21', '10', '20', '.', '0', '+']) + os.linesep +
                '\t'.join(['chr21', '30', '40', '.', '0', '-']) + os.linesep,
            '\t'.join(['chr21', '11', '22', '.', '0', '+']) + os.linesep +
                '\t'.join(['chr21', '29', '40', '.', '0', '-']) + os.linesep,
            upFlank=4, downFlank=6, treatTrackAs='middle', removeChrBorderCrossing=False, suffix='bed')

        self._assertExpandBedSegments(
            '\t'.join(['chr21', '10', '20', '.', '0', '+']) + os.linesep +
                '\t'.join(['chr21', '30', '40', '.', '0', '-']) + os.linesep,
            '\t'.join(['chr21', '6', '17', '.', '0', '+']) + os.linesep +
                '\t'.join(['chr21', '33', '44', '.', '0', '-']) + os.linesep,
            upFlank=4, downFlank=6, treatTrackAs='upstream', removeChrBorderCrossing=False, suffix='bed')

        self._assertExpandBedSegments(
            '\t'.join(['chr21', '10', '20', '.', '0', '+']) + os.linesep +
                '\t'.join(['chr21', '30', '40', '.', '0', '-']) + os.linesep,
            '\t'.join(['chr21', '15', '26', '.', '0', '+']) + os.linesep +
                '\t'.join(['chr21', '24', '35', '.', '0', '-']) + os.linesep,
            upFlank=4, downFlank=6, treatTrackAs='downstream', removeChrBorderCrossing=False, suffix='bed')

        self._assertExpandBedSegments(
            '\t'.join(['chr21', '10', '11', '.', '0', '+']) + os.linesep +
                '\t'.join(['chr21', '30', '31', '.', '0', '-']) + os.linesep,
            '\t'.join(['chr21', '6', '17', '.', '0', '+']) + os.linesep +
                '\t'.join(['chr21', '24', '35', '.', '0', '-']) + os.linesep,
            upFlank=4, downFlank=6, treatTrackAs='points', removeChrBorderCrossing=False, suffix='point.bed')

        self._assertExpandBedSegments(
            'track type=bedGraph' + os.linesep +
                '\t'.join(['chr21', '10', '20', '0.5']) + os.linesep +
                '\t'.join(['chr21', '30', '40', '-0.5']) + os.linesep,
            'track type=bedGraph' + os.linesep +
                '\t'.join(['chr21', '6', '26', '0.5000']) + os.linesep +
                '\t'.join(['chr21', '26', '46', '-0.5000']) + os.linesep,
            upFlank=4, downFlank=6, treatTrackAs='segments', removeChrBorderCrossing=False, suffix='bedgraph')

        self._assertExpandBedSegments(
            '\t'.join(['chrM', '500', '1000', '.', '0', '+']) + os.linesep +
                '\t'.join(['chrM', '16000', '16500', '.', '0', '-']) + os.linesep,
            '\t'.join(['chrM', '0', '1000', '.', '0', '+']) + os.linesep +
                '\t'.join(['chrM', '16000', '16571', '.', '0', '-']) + os.linesep,
            upFlank=600, downFlank=0, treatTrackAs='segments', removeChrBorderCrossing=False, suffix='bed')

        self._assertExpandBedSegments(
            '\t'.join(['chrM', '800', '1000', '.', '0', '+']) + os.linesep +
                '\t'.join(['chrM', '16000', '16500', '.', '0', '-']) + os.linesep,
            '\t'.join(['chrM', '200', '1000', '.', '0', '+']) + os.linesep,
            upFlank=600, downFlank=0, treatTrackAs='segments', removeChrBorderCrossing=True, suffix='bed')

    def runTest(self):
        self.testRun()

if __name__ == "__main__":
    #TestGalaxyInterface().debug()
    if len(sys.argv) == 2:
        TestGalaxyInterface.VERBOSE = ast.literal_eval(sys.argv[1])
        sys.argv = sys.argv[:-1]
    unittest.main()
