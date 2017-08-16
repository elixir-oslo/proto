import math
from collections import OrderedDict

from gold.util.CustomExceptions import AbstractClassError
from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.application.GalaxyInterface import GalaxyInterface
from quick.webtools.restricted.visualization.visualizationGraphs import visualizationGraphs, dataTransformer

'''
Created on Nov 21, 2014

@author: boris
'''

class MultiTrackAnalysis(object):
    
    def __init__(self, tracks, trackNames, 
                 regSpec, binSpec, 
                 genome, galaxyFn, 
                 randOption = None, 
                 numResamplingsOption = None,
                 analysisDef = None):
        self._tracks = tracks
        self._trackNames = trackNames
        self._regSpec = regSpec
        self._binSpec = binSpec
        self._genome = genome
        self._galaxyFn = galaxyFn
        self._randOption = randOption
        self._numResamplingsOption = numResamplingsOption
        self._analysisDef = analysisDef

    def execute(self, printHtmlBeginEnd=True, printTrackNamesTable=True):
        print GalaxyInterface.getHtmlBeginForRuns(self._galaxyFn)
        core = HtmlCore()
        if printTrackNamesTable:
            core.divBegin('trackNames')
            dataDict = OrderedDict([(x, []) for x in self._trackNames])
            tblExpandable = True
            if len(self._trackNames) < 11:
                tblExpandable = False
            core.tableFromDictionary(dataDict, ['Tracks under analysis'], tableId="resTable", expandable=tblExpandable)
#             core.tableHeader(['Tracks under analysis:'])
#             for trackName in self._trackNames:
#                 core.tableLine([trackName])
#             core.tableFooter()
            core.divEnd()
        print core
        try:
            results = GalaxyInterface.run(self._tracks[0], self._tracks[1], 
                            self.getAnalysisDefinitionString(), self._regSpec,
                            self._binSpec, self._genome, self._galaxyFn, 
                            printRunDescription=False,
                            printHtmlBeginEnd = printHtmlBeginEnd,
                            fromMainTool=False)
            
            if self.hasVisualization():
                print self.visualizeResults(results)
                
#        except:
#            pass
        finally:
            core2 = HtmlCore()
            core2.hideToggle(styleClass='infomessagesmall')
            print core2
            print GalaxyInterface.getHtmlEndForRuns()
    
    def getAnalysisDefinitionString(self):
        if self._analysisDef:
            return self._analysisDef
        else:
            raise AbstractClassError()
        
    #override method to return true to add visualization to subclass 
    def hasVisualization(self):
        return False
    
    def visualizeResults(self, results):
        raise AbstractClassError()
    
    
class MultiTrackBasePairCoverage(MultiTrackAnalysis):
    
    def getAnalysisDefinitionString(self):
        ##for 20 or less tracks use a faster algorithm. For more than 20 there can be memory issues, so use naive algorithm for now 
#         analysisDef = 'dummy -> ThreeWayBpOverlapStat' if len(self._tracks) > 20 else 'dummy -> ThreeWayBpOverlapVegardAndKaiVersionWrapperStat'
#         from gold.application.LogSetup import setupDebugModeAndLogging
#         setupDebugModeAndLogging()
        analysisDef = 'dummy -> MultitrackBpOverlapStat'
        analysisDef = 'dummy [extraTracks=%s] '\
         % '&'.join(['|'.join(tn) for tn in self._tracks[2:] ]) + analysisDef

        return analysisDef
    
    def hasVisualization(self):
        return True
    
    def visualizeResults(self, results):
        
        globalResult = results.getGlobalResult()
        res = OrderedDict([(x, globalResult[x]) for x in globalResult if x not in ['Assembly_gap_coverage']] )
        
        dT = dataTransformer(res)
        seriesName, categories, data = dT.changeDictIntoListsByLevel()
        
        vg = visualizationGraphs()
        res = vg.drawColumnCharts(data, categories=categories)
        
        return vg.visualizeResults(res)
        
    
    
class MultiTrackBasePairCoverageProportional(MultiTrackAnalysis):
    
    def getAnalysisDefinitionString(self):
        ##for 20 or less tracks use a faster algorithm. For more than 20 there can be memory issues, so use naive algorithm for now 
#         analysisDef = 'dummy -> ThreeWayProportionalBpOverlapStat' if len(self._tracks) > 20 else 'dummy -> ThreeWayProportionalBpOverlapKaiAndVegardStat'
        analysisDef = 'dummy -> ThreeWayProportionalBpOverlapStat'
        analysisDef = 'dummy [extraTracks=%s] '\
         % '&'.join(['|'.join(tn) for tn in self._tracks[2:] ]) + analysisDef
        return analysisDef
    
    def hasVisualization(self):
        return True
    
    def visualizeResults(self, results):
        
        globalResult = results.getGlobalResult()
        res = OrderedDict([(x, globalResult[x]) for x in globalResult if x not in ['Assembly_gap_coverage']] )
        
        dT = dataTransformer(res)
        seriesName, categories, data = dT.changeDictIntoListsByLevel()
        
        vg = visualizationGraphs()
        res = vg.drawColumnCharts(data, categories=categories)
        
        return vg.visualizeResults(res)

class MultiTrackFactorsOfObserevedVsExpectedOverlap(MultiTrackAnalysis):
    
    def getAnalysisDefinitionString(self):
        analysisDef = 'Dummy [rawStatistic=ThreeWayExpectedWithEachPreserveCombinationBpOverlapStat]  [referenceResDictKey=preserveNone] \
            -> GenericFactorsAgainstReferenceResDictKeyStat'
        analysisDef = 'dummy [extraTracks=%s] '\
         % '&'.join(['|'.join(tn) for tn in self._tracks[2:] ]) + analysisDef
        return analysisDef
    
    def hasVisualization(self):
        return True
    
    def visualizeResults(self, results):
        
        globalResult = results.getGlobalResult()
        res = OrderedDict([(x, globalResult[x]) for x in globalResult if x not in ['Assembly_gap_coverage']] )
        
        dT = dataTransformer(res)
        seriesName, categories, data = dT.changeDictIntoList()
        
        vg = visualizationGraphs()
        res = vg.drawColumnChart(data, seriesName = ['Results'], categories=categories, xAxisRotation=270, extraScriptButton=[OrderedDict({'Use linear scale':'linear','Use log10 scale':'logarithmic'}), 'yAxisType'])
        
        return vg.visualizeResults(res)
        

class MultiTrackExpectedOverlapGivenBinPresence(MultiTrackAnalysis):
    
    def getAnalysisDefinitionString(self):
#         analysisDef = 'dummy -> ThreeWayExpectedBpOverlapGivenBinPresenceStat'
        analysisDef = 'dummy -> ThreeWayExpectedBpOverlapGivenBinPresenceAsWholeBpsStat'
        analysisDef = 'dummy [extraTracks=%s] '\
         % '&'.join(['|'.join(tn) for tn in self._tracks[2:] ]) + analysisDef
        return analysisDef
    
    def hasVisualization(self):
        return True
     
    def visualizeResults(self, results):
         
        globalResult = results.getGlobalResult()
        res = OrderedDict([(x, globalResult[x]) for x in globalResult if x not in ['Assembly_gap_coverage']] )
        
        dT = dataTransformer(res)
        seriesName, categories, data = dT.changeDictIntoList()
         
        vg = visualizationGraphs()
        res = vg.drawColumnChart(data, categories=categories, extraScriptButton=[OrderedDict({'Use linear scale':'linear','Use log10 scale':'logarithmic'}), 'yAxisType'])
         
        return vg.visualizeResults(res)
         
    
class MultiTrackHypothesisTesting(MultiTrackAnalysis):
    
    def getAnalysisDefinitionString(self):
        #Old version
        analysisDef = 'dummy [tail=different] [rawStatistic=SingleValExtractorStat] \
            [childClass=ThreeWayBpOverlapStat] [resultKey=%s] %s %s -> RandomizationManagerStat' \
            % ('1'*(len(self._tracks)), self._randOption, self._numResamplingsOption)

        
        from gold.application.LogSetup import setupDebugModeAndLogging
        setupDebugModeAndLogging()

#         analysisDef = 'dummy [tail=different] [rawStatistic=SingleValExtractorStat] \
#             [childClass=MultitrackBpOverlapStat] [resultKey=%s] %s %s -> RandomizationManagerStat' \
#             % ('1'*(len(self._tracks)), self._randOption, self._numResamplingsOption)
        analysisDef = 'dummy [extraTracks=%s] '\
         % '&'.join(['|'.join(tn) for tn in self._tracks[2:] ]) + analysisDef
        return analysisDef
    
class MultiTrackCoverageDepthBps(MultiTrackAnalysis):
    
    def getAnalysisDefinitionString(self):
        
        analysisDef = 'dummy -> ThreeWayCoverageDepthStat'
        analysisDef = 'dummy [extraTracks=%s] '\
         % '&'.join(['|'.join(tn) for tn in self._tracks[2:] ]) + analysisDef
        return analysisDef
    
    def hasVisualization(self):
        return True
    
    def visualizeResults(self, results):
        
        globalResult = results.getGlobalResult()
        res = OrderedDict([(x, globalResult[x]) for x in globalResult if x not in ['Assembly_gap_coverage', 'BinSize', 'Depth 0']] )
        
        dT = dataTransformer(res)
        seriesName, categories, data = dT.changeDictIntoList()
        
        vg = visualizationGraphs()
        res = vg.drawColumnChart(data, categories=categories)
        
        return vg.visualizeResults(res)
        
    
class MultiTrackCoverageDepthProportional(MultiTrackAnalysis):
    
    def getAnalysisDefinitionString(self):
        analysisDef = 'dummy -> ThreeWayCoverageDepthProportionalStat'
        analysisDef = 'dummy [extraTracks=%s] '\
         % '&'.join(['|'.join(tn) for tn in self._tracks[2:] ]) + analysisDef
        return analysisDef
    
    def hasVisualization(self):
        return True
    
    def visualizeResults(self, results):
        
        globalResult = results.getGlobalResult()
        res = OrderedDict([(x, globalResult[x]) for x in globalResult if x not in ['Assembly_gap_coverage', 'BinSize', 'Depth 0']] )
        
        dT = dataTransformer(res)
        seriesName, categories, data = dT.changeDictIntoList()
        
        vg = visualizationGraphs()
        return  vg.drawPieChart(data, seriesName=categories)
        
class MultiTrackCoverageDepthProportionalToAny(MultiTrackAnalysis):
    
    def getAnalysisDefinitionString(self):
        analysisDef = 'dummy -> ThreeWayCoverageDepthProportionalToAnyDepthStat'
        analysisDef = 'dummy [extraTracks=%s] '\
         % '&'.join(['|'.join(tn) for tn in self._tracks[2:] ]) + analysisDef
        return analysisDef
    
    def hasVisualization(self):
        return True
    
    def visualizeResults(self, results):
        
        globalResult = results.getGlobalResult()
        res = OrderedDict([(x, globalResult[x]) for x in globalResult if x not in ['Assembly_gap_coverage']] )
        
        dT = dataTransformer(res)
        seriesName, categories, data = dT.changeDictIntoList()
        
        vg = visualizationGraphs()
        return  vg.drawPieChart(data, seriesName=categories)
    
 
class MultiTrackCoverageDepthExtra(MultiTrackAnalysis):
    
    def getAnalysisDefinitionString(self):
        analysisDef = 'dummy -> ThreeWayExtraCoverageGivenDepthStat'
        analysisDef = 'dummy [extraTracks=%s] '\
         % '&'.join(['|'.join(tn) for tn in self._tracks[2:] ]) + analysisDef
        return analysisDef
    
    def hasVisualization(self):
        return True
    
    def visualizeResults(self, results):
        
        globalResult = results.getGlobalResult()
        res = OrderedDict([(x, globalResult[x]) for x in globalResult if x not in ['Assembly_gap_coverage', 'BinSize']] )
      
        dT = dataTransformer(res)
        seriesName, categories, data = dT.changeDictIntoListByTrackString(numStart=0, numEnd=len(res))
        
        vg = visualizationGraphs()
        res = vg.drawColumnChart(data, categories=categories)
        
        return vg.visualizeResults(res)
        
    
class MultiTrackCoverageProportionToOthers(MultiTrackAnalysis):
    
    def getAnalysisDefinitionString(self):
# 
#         from gold.application.LogSetup import setupDebugModeAndLogging
#         setupDebugModeAndLogging()

        analysisDef = 'dummy -> ThreeWayPerTrackDepthProportionsStat'
        analysisDef = 'dummy [extraTracks=%s] '\
         % '&'.join(['|'.join(tn) for tn in self._tracks[2:] ]) + analysisDef
        return analysisDef
    
    def hasVisualization(self):
        return True
    
    def visualizeResults(self, results):
        
        globalResult = results.getGlobalResult()
        res = OrderedDict([(x, globalResult[x]) for x in globalResult if x not in ['Assembly_gap_coverage']] )
        
        dT = dataTransformer(res)
        seriesName, categories, data = dT.changeDictIntoListsByNumber(math.sqrt(len(res)))
    
        vg = visualizationGraphs()
        return  vg.drawPieCharts(data, seriesName=categories, addOptions='width: 50%; float:left; margin: 0 auto')
    
class MultiTrackInclusionStructure(MultiTrackAnalysis):
    
    def getAnalysisDefinitionString(self):
        analysisDef = 'dummy -> ThreeWayTrackInclusionBpOverlapStat'
        analysisDef = 'dummy [extraTracks=%s] '\
         % '&'.join(['|'.join(tn) for tn in self._tracks[2:] ]) + analysisDef
        return analysisDef
    
    def hasVisualization(self):
        return True
    
    def visualizeResults(self, results):
        
        globalResult = results.getGlobalResult()
        res = OrderedDict([(x, globalResult[x]) for x in globalResult if x not in ['Assembly_gap_coverage', 'Inclusions']] )
        
        dT = dataTransformer(res)
        seriesName, categories, data = dT.changeDictIntoListsByLevel()
        
        vg = visualizationGraphs()
        res = vg.drawColumnCharts(data, categories=categories)
        
        return vg.visualizeResults(res)
        
    
class MultiTrackFocusedTrackDepthCoverage(MultiTrackAnalysis):
    
    def getAnalysisDefinitionString(self):
        
        from gold.application.LogSetup import setupDebugModeAndLogging
        setupDebugModeAndLogging()        
        
        analysisDef = 'dummy -> ThreeWayFocusedTrackCoveragesAtDepthsStat'
        analysisDef = 'dummy [extraTracks=%s] '\
         % '&'.join(['|'.join(tn) for tn in self._tracks[2:] ]) + analysisDef
        return analysisDef
    
    def hasVisualization(self):
        return True
    
    def visualizeResults(self, results):
        
        globalResult = results.getGlobalResult()
        res = OrderedDict([(x, globalResult[x]) for x in globalResult if x not in ['Assembly_gap_coverage', 'BinSize']] )
        
        dT = dataTransformer(res)
        seriesName, categories, data = dT.changeDictIntoListsByTrackString(strNum="T", numStart=1, numEnd=int(math.sqrt(len(res)/2)))
        vg = visualizationGraphs()
        res = vg.drawColumnCharts(data, categories=categories, seriesName=seriesName, addOptions='width: 50%; float:left; margin: 0 auto')

        return res
        
class MultiTrackFocusedTrackDepthCoverageProportional(MultiTrackAnalysis):
    
    def getAnalysisDefinitionString(self):
        analysisDef = 'dummy -> ThreeWayFocusedTrackProportionCoveragesAtDepthsStat'
        analysisDef = 'dummy [extraTracks=%s] '\
         % '&'.join(['|'.join(tn) for tn in self._tracks[2:] ]) + analysisDef
        return analysisDef
    
    def hasVisualization(self):
        return True
    
    def visualizeResults(self, results):
        
        globalResult = results.getGlobalResult()
        res = OrderedDict([(x, globalResult[x]) for x in globalResult if x not in ['Assembly_gap_coverage', 'BinSize']] )
        
        print res
        
        dT = dataTransformer(res)
        seriesName, categories, data = dT.changeDictIntoListsByTrackString(strNum="T", numStart=1, numEnd=int(math.sqrt(len(res))))
        
        vg = visualizationGraphs()
        res = vg.drawPieCharts(data, seriesName=categories, addOptions='width: 50%; float:left; margin: 0 auto')
        
        return  res
