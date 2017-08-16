import unittest
import quick.application.ExternalTrackManager

class GSuiteTestWithMockEncodingFuncs(unittest.TestCase):
    def setUp(self):
        @staticmethod
        def getEncodedDatasetIdFromGalaxyFn(galaxyFn):
            return str(hash(galaxyFn))

        @staticmethod
        def getGalaxyFnFromEncodedDatasetId(datasetId):
            return '/path/to/dataset_%s.dat' % datasetId

        @staticmethod
        def getGalaxyFilesFnFromEncodedDatasetId(datasetId):
            return '/path/to/dataset_%s_files' % datasetId

        self.oldGetEncodeDatasetIdFunc = \
            quick.application.ExternalTrackManager.ExternalTrackManager.getEncodedDatasetIdFromGalaxyFn
        quick.application.ExternalTrackManager.ExternalTrackManager.getEncodedDatasetIdFromGalaxyFn = \
            getEncodedDatasetIdFromGalaxyFn

        self.oldGetGalaxyFnFunc = \
            quick.application.ExternalTrackManager.ExternalTrackManager.getGalaxyFnFromEncodedDatasetId
        quick.application.ExternalTrackManager.ExternalTrackManager.getGalaxyFnFromEncodedDatasetId = \
            getGalaxyFnFromEncodedDatasetId

        self.oldGetGalaxyFilesFnFunc = \
            quick.application.ExternalTrackManager.ExternalTrackManager.getGalaxyFilesFnFromEncodedDatasetId
        quick.application.ExternalTrackManager.ExternalTrackManager.getGalaxyFilesFnFromEncodedDatasetId = \
            getGalaxyFilesFnFromEncodedDatasetId

    def tearDown(self):
        quick.application.ExternalTrackManager.ExternalTrackManager.getEncodedDatasetIdFromGalaxyFn = \
            self.oldGetEncodeDatasetIdFunc
        quick.application.ExternalTrackManager.ExternalTrackManager.getGalaxyFnFromEncodedDatasetId = \
            self.oldGetGalaxyFnFunc
        quick.application.ExternalTrackManager.ExternalTrackManager.getGalaxyFilesFnFromEncodedDatasetId = \
            self.oldGetGalaxyFilesFnFunc
