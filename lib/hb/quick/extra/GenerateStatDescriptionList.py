from gold.description.AnalysisManager import AnalysisManager
import os

STAT_DESCRIPTION_LIST_FN = os.sep.join(['gold', 'description', 'StatDescriptionList.py'])

#analyses = AnalysisManager.getAllAnalyses()
#statClasses = []
#for a in analyses:
#    statClasses += [x.__name__ for x in a._statClassList]
#allStatClassesSet = set(statClasses)

coveredStats = set([line.split('=')[0].strip() for line in open(STAT_DESCRIPTION_LIST_FN) if line.count('=') == 1])

avoidStatSet = set(['RandomizationManagerStat'])

analysisDict = AnalysisManager.getAnalysisDict()

categories = analysisDict.keys()

for cat in categories:
    analyses = analysisDict[cat].values()
    statClasses = []
    for a in analyses:
        statClasses += [x.__name__ for x in a._statClassList]
    allStatClassesSet = set(statClasses)
    uncoveredStatClasses = allStatClassesSet - coveredStats
    missingStatClasses = uncoveredStatClasses - avoidStatSet
    print '#' + cat
    for stat in missingStatClasses:
        print stat + " = ''"
