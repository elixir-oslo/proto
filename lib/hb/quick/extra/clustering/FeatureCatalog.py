from gold.description.AnalysisManager import AnalysisManager
#from quick.util.Decorators import obsoleteHbFunction
from gold.application.GalaxyInterface import GalaxyInterface
class FeatureCatalog(object):
    #@obsoleteHbFunction
    @staticmethod
    def getFeaturesFromTrackFormatCombination(tfName1, tfName2):
        if tfName1.lower() == tfName2.lower() == 'segments':
            return {'#Bp overlap': ['-> RawOverlapStat', 'Both'],
                    '#Bp overlap, diff from expected': ['[tail=more] [assumptions=bothIndependentBps]-> BpOverlapPValStat', 'DiffFromMean']}

    #@obsoleteHbFunction
    @staticmethod
    def getFeaturesFromTracks(genome, trackName1, trackName2): #change to one out of three specific catalogs..
        return ReferenceAnalsesAsFeaturesCatalog.getValidAnalyses(genome, trackName1, trackName2)

    @classmethod
    def getValidAnalyses(cls, genome, trackName1, trackName2):
        allFeatures = cls.getAllFeatures()
        validFeatures = {}
        trackName1, trackName2 = GalaxyInterface._cleanUpTracks([trackName1, trackName2], genome, realPreProc=False)
        #trackName1 = trackName1[1:] #FixMe, temp, Boris..
        #genome='hg19'
        #print 'TEMP3: ', (genome, trackName1, trackName2)
        if not GalaxyInterface.areTrackNamesValid(genome, trackName1, trackName2):
            return {}

        #print 'TEMP2: ', allFeatures
        for key in allFeatures:
            analysisDef = allFeatures[key][0]
            #print AnalysisManager._tryAnalysisDefForValidity(analysisDef, genome, trackName1, trackName2, tryReversed=False)
            if AnalysisManager._tryAnalysisDefForValidity(analysisDef, genome, trackName1, trackName2, tryReversed=False)[0] is not None: #maybe also try reversed..
                validFeatures[key] = allFeatures[key]

        #print "Valid: %s (for trackNames: %s and %s)" % (validFeatures, trackName1, trackName2)
        return validFeatures

class DirectDistanceCatalog(FeatureCatalog):
    @staticmethod
    def getAllFeatures():
        allFeatures = {}
        #US-US
        allFeatures['Ratio of intersection vs union of segments'] = ['dummy -> DerivedOverlapStat', 'intersectionToUnionRatio']
        #allFeatures['Pairwise overlap enrichment between tracks'] = ['dummy -> DerivedOverlapStat', '1in2']
        allFeatures['Pairwise overlap enrichment between tracks (v2)'] = ['dummy -> OverlapEnrichmentBasedDistanceStat', 'Result']
        return allFeatures

class LocalResultsAsFeaturesCatalog(FeatureCatalog):
    @staticmethod
    def getAllFeatures():
        allFeatures = {}
        #US-US
        allFeatures['Prop. Bp coverage per bin'] = ['dummy -> ProportionCountStat', 'Result']
        allFeatures['Prop. Bp coverage by points per bin'] = ['dummy -> PointFreqStat', 'Result']
        #allFeatures['Relative coverage per bin'] = ['dummy -> PropOfSegmentsInsideEachBinStat', 'Result']
        allFeatures['Relative coverage per bin'] = ['dummy [rawStatistic=CountSegmentStat] [globalSource=chrs] -> GenericRelativeToGlobalStat', 'Result']
        #allFeatures['Relative frequency per bin'] = ['dummy -> PropOfPointsInsideEachBinStat', 'Result']
        allFeatures['Relative coverage per bin'] = ['dummy [rawStatistic=CountPointStat] [globalSource=chrs] -> GenericRelativeToGlobalStat', 'Result']
        allFeatures['Mean bp-weighted mark value per bin'] = ['dummy -> MeanOverCoveredBpsStat', 'Result']
        allFeatures['Mean mark value per bin'] = ['dummy -> MeanMarkStat', 'Result']
        allFeatures['Microbin-based point count per bin'] = ['dummy [tf1=SegmentToMidPointFormatConverter] -> PointCountPerMicroBinV2Stat', 'Microbins']
        return allFeatures

class ReferenceAnalsesAsFeaturesCatalog(FeatureCatalog):
    @staticmethod
    def getAllFeatures():
        #NB! Must be a word/option before '->' in order for analysisDef to be valid
        #Allowed track conversions can be restricted by setting option for tf1 or tf2 in analysisDef
        allFeatures = {}
        #US-US
        allFeatures['#Bp overlap'] = ['dummy -> RawOverlapStat', 'Both']
        allFeatures['Prop. of tr2 covered by tr1'] = ['dummy -> DerivedOverlapStat', '1inside2']
        allFeatures['#Bp overlap, diff from expected'] = ['[tail=more] [assumptions=bothIndependentBps]-> BpOverlapPValStat', 'DiffFromMean']
        #US-F
        allFeatures['Mean inside'] = ['dummy -> MeanInsideStat','Result']
        #UP-US
        allFeatures['#Points inside'] = ['dummy [tf1=TrivialFormatConverter] ->PointCountInsideSegsStat','Result']
        allFeatures['Prop. of tr1-points falling inside segments of tr2'] = ['dummy -> DerivedPointCountsVsSegsStat', '2inside1']
        return allFeatures

class SplittedRegionsAsFeaturesCatalog(FeatureCatalog):
    @staticmethod
    def getAllFeatures():
        allFeatures = {}
        allFeatures['BinnedSegCoverage'] = ['dummy [tf1=TrivialFormatConverter] [numSubBins=20] -> BinScaledSegCoverageStat','Result']
        return allFeatures

if __name__ == '__main__':
    featureDict = ReferenceAnalsesAsFeaturesCatalog.getValidAnalyses('hg18','Phenotype and disease associations:Assorted experiments:Virus integration, Derse et al. (2007):ASV'.split(':')\
                                                       ,'DNA structure:Fragile sites'.split(':'))
    print 'vs ref: ', featureDict.keys()

    featureDict = DirectDistanceCatalog.getValidAnalyses('hg18','Phenotype and disease associations:Assorted experiments:Virus integration, Derse et al. (2007):ASV'.split(':')\
                                                       ,'DNA structure:Fragile sites'.split(':'))
    print 'direct dist: ', featureDict.keys()

    featureDict = LocalResultsAsFeaturesCatalog.getValidAnalyses('hg18','Phenotype and disease associations:Assorted experiments:Virus integration, Derse et al. (2007):ASV'.split(':')\
                                                       ,[])
    print 'local res: ', featureDict.keys()

#featureDict = FeatureCatalog.getFeaturesFromTracks('hg18','Phenotype and disease associations:Assorted experiments:Virus integration, Derse et al. (2007):ASV'.split(':')\
#                                                   ,'DNA structure:Fragile sites'.split(':'))
#print featureDict.keys()

#featureDict = FeatureCatalog.getFeaturesFromTrackFormatCombination(tfName1, tfName2)
#print 'Choose between: ', featureDict.keys()
#
#choice = '#Bp overlap'
#analysisDef, resDictKey = featureDict[choice]
#
#result = AnalysisDefJob(analysisDef).run()
#value = result[resDictKey]
