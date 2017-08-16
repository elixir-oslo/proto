from gold.application.HBAPI import doAnalysis, AnalysisSpec, PlainTrack
from gold.description.AnalysisDefHandler import AnalysisDefHandler
from gold.description.AnalysisManager import AnalysisManager
from gold.gsuite.GSuite import GSuite
from quick.application.UserBinSource import UserBinSource
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.statistic.HotSpotRegionsStat import HotSpotRegionsStat
from quick.webtools.GeneralGuiTool import GeneralGuiTool


# This is a template prototyping GUI that comes together with a corresponding
# web page.

class GenerateGsuiteFileWithHotSpotRegions(GeneralGuiTool):
    
    
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Generate gSuite file with HotSpot regions"

    @staticmethod
    def getInputBoxNames():
        return [('Select track collection GSuite','gSuite'),
                ('Number of top hotspots', 'param'),
                ('User bin source', 'binSourceParam')
                ]

    @staticmethod
    def getOptionsBoxGSuite():
        return GeneralGuiTool.getHistorySelectionElement('gsuite')
    
    @staticmethod
    def getOptionsBoxParam(prevChoices):
        
        if prevChoices.gSuite:     
            from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
            gSuite = getGSuiteFromGalaxyTN(prevChoices.gSuite)
            tracks = list(gSuite.allTracks())
            fullCategory = AnalysisManager.combineMainAndSubCategories('Descriptive statistics', 'Distributions')
            if len(tracks) >0:
                analysis = GenerateGsuiteFileWithHotSpotRegions.resolveAnalysisFromName(gSuite.genome, fullCategory, \
                                                                tracks[0].trackName, 'Hot spot regions')
                
                if analysis and analysis.getOptionsAsKeys():
                    return analysis.getOptionsAsKeys().values()[1]

    @staticmethod
    def resolveAnalysisFromName(genome, fullCategory, trackName, analysisName):
        selectedAnalysis = None
        for analysis in AnalysisManager.getValidAnalysesInCategory(fullCategory, genome, trackName, None):
            if analysisName == AnalysisDefHandler.splitAnalysisText(str(analysis))[0]:
                selectedAnalysis = analysis
        
        return selectedAnalysis
    
    @staticmethod
    def getOptionsBoxBinSourceParam(prevChoices):
        if prevChoices.param:     
            return ''
    
    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        analysisSpec = AnalysisSpec(HotSpotRegionsStat)
        analysisSpec.addParameter("numberOfTopHotSpots", choices.param)
          
        #use gSuite from option
        gSuite = getGSuiteFromGalaxyTN(choices.gSuite)
        tracks = list(gSuite.allTracks())
        
        #create new gSuite object
        suite = GSuite()
        
        if choices.binSourceParam:
            binSourceParam = choices.binSourceParam
        else:
            binSourceParam = '10m'
        
        from proto.hyperbrowser.HtmlCore import HtmlCore
        
        htmlCore = HtmlCore()
        htmlCore.begin()
        
        for track in tracks:
            
            
            #analysis
            #analysisBins = GlobalBinSource(gSuite.genome)
            analysisBins = UserBinSource('*', binSourceParam, genome=gSuite.genome)
            result = doAnalysis(analysisSpec, analysisBins, [PlainTrack(track.trackName)])
            
            
            resultDict = result.getGlobalResult()
            
            
            trackName = track.trackName
            trackName[len(track.trackName)-1] = trackName[len(trackName)-1]+str(choices.param)
            
            #get results
#             if resultDict['Result']:
#                 res = '\n'.join(str(x) for x in resultDict['Result'])  
#                 trackRes = res.replace(':', '\t').replace('-', '\t')
#                 #build path to file
#                 
#                 outStaticFile = GalaxyRunSpecificFile([md5(str(track.trackName)).hexdigest() + '.bed'], galaxyFn)
#                 
#                 #full file            
#                 #f = open(galaxyTrackName.getDiskPath(), 'w')
#                 f = outStaticFile.getFile('w')
# #                 
# #                 print trackRes
# #                 print '---'
#                 
#                 f.write(trackRes)
#                 f.close()
#                 
#                 #add track to gSuite
#                 #suite.addTrack(HttpGSuiteTrack(outStaticFile.getURL(False), gSuite.genome))
#                 
#                 uri = HbGSuiteTrack.generateURI(trackName=track.trackName)
#                 
#                 suite.addTrack(GSuiteTrack(uri, trackType=track.trackType, genome=gSuite.genome))
                
            
            
            
            if resultDict['Result']:
                
                import operator
                resList = resultDict['Result']
                resList.sort(key=operator.itemgetter(1), reverse=True)
                
                param=int(choices.param)
                elNum = resList[int(choices.param)-1][1]
                for elN in range(int(choices.param), len(resList)):
                    if resList[elN][1] == elNum:
                        param+=1
                    else:
                        break
                
                trackName=track.trackName
                newlC=str(trackName[len(trackName)-1]) + '-' + str(int(choices.param))
                
                outputFile =  open(cls.makeHistElement(galaxyExt='bed',title=str(newlC)), 'w')
                
                elNX=0
                for x in resList[0:param]:
                    #outputFile.write(x[0].replace(':', '\t').replace('-', '\t') + '\t' + str(elNX) + '\t' + str(x[1]) + '\n')
                    outputFile.write(x[0].replace(':', '\t').replace('-', '\t') + '\n')
                    elNX+=1
                outputFile.close()
                
                htmlCore.line('File ' + str(newlC) + ' is in the history.')
                #build path to file
                
                #outStaticFile = GalaxyRunSpecificFile([md5(str(trackName)).hexdigest() + '.bed'], galaxyFn)
                
                #full file            
                #f = open(galaxyTrackName.getDiskPath(), 'w')
                #f = outStaticFile.getFile('w')
#                 
#                 print trackRes
#                 print '---'
                
                #f.write(trackRes)
                #f.close()
                
                #add track to gSuite
                #suite.addTrack(HttpGSuiteTrack(outStaticFile.getURL(False), gSuite.genome))
                
                #uri = HbGSuiteTrack.generateURI(trackName=trackName)
                
                #suite.addTrack(GSuiteTrack(uri, trackType=track.trackType, genome=gSuite.genome))
            
            
        #build gSuite
        #suite.downloadAllRemoteTracksAsSingleDatasetAndReturnOutputAndErrorGSuites(galaxyFn)
        
        #GSuiteComposer.composeToFile(suite, galaxyFn)
        
            
    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''
        
        from gold.gsuite.GSuiteConstants import UNKNOWN, MULTIPLE

        errorStr = GeneralGuiTool._checkGSuiteFile(choices.gSuite)
        if errorStr:
            return errorStr

        from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
        gSuite = getGSuiteFromGalaxyTN(choices.gSuite)
        if gSuite.numTracks() == 0:
            return 'Please select a GSuite file with at least one track'

        if not gSuite.isPreprocessed():
            return 'Selected GSuite file is not preprocess. Please preprocess ' \
                   'the GSuite file before continuing the analysis.'

        if gSuite.trackType in [UNKNOWN]:
            return 'The track type of the GSuite file is not known. The track type ' \
                   'is needed for doing analysis.'

        if gSuite.trackType in [MULTIPLE]:
            return 'All tracks in the GSuite file needs to be of the same track ' \
                   'type. Multiple track types are not supported.'
        
        
        return None

    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'html'
    
   
