from gold.application.GalaxyInterface import GalaxyInterface
from gold.application.StatRunner import AnalysisDefJob

trackName1 = ['Sequence','Repeating elements','LINE'] 
trackName2 = ['Sequence','Repeating elements','SINE']
#GalaxyInterface.getSubTrackNames(['Sequence','Repeating elements'],False)

analysisDef = 'bla bla -> PropFreqOfTr1VsTr2Stat' #or any other statistic from the HB collection
regSpec = 'chr1' #could also be e.g. 'chr1' for the whole chromosome or '*' for the whole genome
binSpec = '10m' #could also be e.g.'100', '1k' or '*' for whole regions/chromosomes as bins 
genome = 'hg18'

#GalaxyInterface.run(trackName1, trackName2, question, regSpec, binSpec, genome='hg18')
userBinSource = GalaxyInterface._getUserBinSource(regSpec,binSpec,genome)

result = AnalysisDefJob(analysisDef, trackName1, trackName2, userBinSource).run()
#result er av klassen Results..
#from gold.result.Results import Results

mainResultDict = result.getGlobalResult()
#from PropFreqOfTr1VsTr2Stat:...
#self._result = {'Track1Prop':ratio,'CountTrack1':c1, 'CountTrack2':c2,'Variance':variance}

mainValueOfInterest = mainResultDict['Variance']
print 'The ..variance..: ', mainValueOfInterest
