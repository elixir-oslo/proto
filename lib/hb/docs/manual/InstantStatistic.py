from gold.application.GalaxyInterface import GalaxyInterface

#first you need to create a statistic class. For this you will use a StatisticTemplate, and just add a few custom lines of code..
#In our example we will make a simple statistic that computes the number of bps covered by all segments of a single track (in a bin).
#1: open the file StatisticTemplate.py
#2: save this file with your own name in the folder "quick/statistic". Lets call it "BpCoverageStat.py".  (By putting your new class here, it will automatically be loaded into the Hyperbrowser system.)
#3: rename the classes according to your name for the statistic - the same as used for the file. The file should then have a class "BpCoverageStat" and a class "BpCoverageStatUnsplittable". (The system will automatically use the unsplittable class, and would in certain cases also automatically have used a corresponding splittable class if it had been defined..)
#4: define what input your statistic will need. In our case we will simply need the raw track data. Add the following line in the method "_createChildren":
#self._addChild( RawDataStat(self._region, self._track, TrackFormatReq()) )
#5: define how to compute the result. Add the following line under "_compute":
#return sum( el.end() - el.start() for el in self._children[0].getResult())
#6: Now you can make a simple call that computes full genome-wide results based on your statistics code:
GalaxyInterface.run(['genes','refseq'], ['repeats','LINE'], 'My new statistic -> BpCoverageStat', '*', '*', genome='hg18')
#7: You can also very simply make your new statistic available on the web if you have a web system running against the Hyperbrowser. Simply add the following line somewhere inside the string variable "QUESTION_SPEC_STR" in the file "gold/description/AnalysisList.py":
#'My new statistic -> BpCoverageStat'
