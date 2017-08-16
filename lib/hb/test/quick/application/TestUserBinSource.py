import unittest
from quick.application.UserBinSource import UserBinSource, AllCombinationsUserBinSource, PairedGenomeRegion

class TestUserBinSource(unittest.TestCase):
    def setUp(self):
        pass

    def testUserBinSource(self):
        bins = [bin for bin in UserBinSource('*','*', genome='hg18')]
        if len(bins) != 0:
            self.assertEqual(24, len(bins))
            self.assertEqual('chr22:1-49691432 (intersects centromere)', bins[21].strWithCentromerInfo())
        else:
            bins = [bin for bin in UserBinSource('*','*', genome='TestGenome')]
            self.assertEqual(2, len(bins))
            self.assertEqual('chr21:1-46944323 (intersects centromere)', bins[0].strWithCentromerInfo())

    def testAllCombinationsUserBinSource(self):
        binSource = UserBinSource('chr21:1-3m','1m', genome='TestGenome')
        pairedBins = AllCombinationsUserBinSource(binSource)

        self.assertEqual(6, sum(1 for bin in pairedBins))

        bins = list(binSource)
        PGR = PairedGenomeRegion
        self.assertEqual([PGR(bins[0], bins[0]),
                          PGR(bins[0], bins[1]),
                          PGR(bins[0], bins[2]),
                          PGR(bins[1], bins[1]),
                          PGR(bins[1], bins[2]),
                          PGR(bins[2], bins[2])],
                          [binPair for binPair in pairedBins])

        binPair = next(iter(pairedBins))

        self.assertEqual('(chr21:1-1000000, chr21:1-1000000)', str(binPair))
        self.assertEqual('(chr21:1-1000000, chr21:1-1000000)', binPair.strWithCentromerInfo())
        self.assertEqual('(chr21:0m-1m, chr21:0m-1m)', binPair.strShort())
        self.assertEqual(-8725196983528202459, hash(binPair))

    def runTest(self):
        self.testUserBinSource()

if __name__ == "__main__":
    #TestUserBinSource().debug()
    unittest.main()
