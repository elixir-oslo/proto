from collections import OrderedDict

from gold.gsuite.GSuiteConstants import TITLE_COL
from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.restricted.visualization.visualizationGraphs import visualizationGraphs
import math
from gold.gsuite import GSuiteConstants, GSuiteFunctions


# This is a template prototyping GUI that comes together with a corresponding
# web page.

class GenericPlotDataTool(GeneralGuiTool):


    ALLOW_UNKNOWN_GENOME = True
    
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Plot metadata values of a GSuite file"
        #Plot tabular values

    @staticmethod
    def getInputBoxNames():
        return [
                ('Select GSuite','gSuite'),
                ('Select way of showing series as', 'plotSeries'),
                ('Select type of chart', 'plotType'),
                ('Select value for x-Axis', 'columnX'),
                ('Select type of scale for x-Axis', 'axesScaleX'),
                ('Select value for y-Axis', 'columnY'),
                ('Select type of scale for y-Axis', 'axesScaleY'),
                #('Select results of plotting', 'plotRes'),
                ]

    @staticmethod
    def getOptionsBoxGSuite():
        #return GeneralGuiTool.getHistorySelectionElement('gsuite', 'txt', 'tabular')
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @classmethod
    def getOptionsBoxPlotSeries(cls, prevChoices): 
        return ['Single', 'Multi']
    
    @classmethod
    def getOptionsBoxPlotType(cls, prevChoices):
        if prevChoices.plotSeries == 'Single': 
            #return ['Column', 'Heatmap', 'Line', 'Pie', 'Scatter']
            return ['Column', 'Scatter']
        else:
            return ['Column', 'Scatter']
            #return ['Column', 'Line', 'Pie', 'Scatter']
    
    
    @classmethod
    def getOptionsBoxColumnX(cls, prevChoices): # Alternatively: getOptionsBox2()
        if not prevChoices.gSuite:
            return
        
        gSuite = getGSuiteFromGalaxyTN(prevChoices.gSuite)
        attributeList = gSuite.attributes
        
        return ['line number'] + [TITLE_COL] + attributeList
    
    
    @staticmethod
    def getOptionsBoxAxesScaleX(prevChoices):
        return ['linear', 'log10', 'no uniform scale (sorted values as labels)']

    
    @classmethod
    def getOptionsBoxColumnY(cls, prevChoices): # Alternatively: getOptionsBox2()
        if not prevChoices.gSuite:
            return
        
        gSuite = getGSuiteFromGalaxyTN(prevChoices.gSuite)

        from quick.gsuite.GSuiteUtils import attributesType
        attribute = attributesType(gSuite)
        
        att=OrderedDict()
        for key, it in attribute.iteritems():
            if it == True:
                att[key] = False
        
        if prevChoices.plotSeries == 'Single': 
            if prevChoices.plotType == 'Pie':
                return att.keys()
        
        return att
    
    @staticmethod
    def getOptionsBoxAxesScaleY(prevChoices):
        return ['linear', 'log10']
    
#     @staticmethod
#     def getOptionsBoxPlotRes(prevChoices):
#         
#         if not prevChoices.gSuite:
#             return
#         
#         columnX = prevChoices.columnX
#         columnY = prevChoices.columnY
#         
#         if prevChoices.plotType == 'Scatter' or prevChoices.plotType == 'Line':
#             if columnX in columnY.keys():
#                 return ['separate', 'combine']
#                 
                
  

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        
        #data from choices
        gSuite = choices.gSuite
        plotType = choices.plotType
        columnX = choices.columnX
        columnY = choices.columnY
        plotSeries = choices.plotSeries
        
        axesScaleX = choices.axesScaleX 
        axesScaleY = choices.axesScaleY
        
        #'linear', 'log10', 'no uniform scale (sorted values as labels)'
        if axesScaleX == 'linear':
        #plotRes = choices.plotRes
            plotRes = 'combine'
        elif  axesScaleX == 'log10':
            plotRes = 'separate'
        elif axesScaleX == 'no uniform scale (sorted values as labels)':
            plotRes = 'separate'
        
        
        
        #unpack gsuite
        gSuite = getGSuiteFromGalaxyTN(gSuite)
        
        #full list of attributes (meta-data)
        attributeList = gSuite.attributes
        
        #fill list of attributes plus title
        attributeList = [TITLE_COL] + attributeList
        
        #dictNum - include numerical values which can be presented in y-axes
        #need to do that because pie can have only one chocie and then it is not returing dict
        from quick.gsuite.GSuiteUtils import attributesType
        attribute = attributesType(gSuite)

        dictNum=OrderedDict()
        for key, it in attribute.iteritems():
            if it == True:
                dictNum[key] = False
        
        #check if it is dict or not
        if not isinstance(columnY, dict):
            tempDict={}
            tempDict[columnY] = 'True'
            columnY=tempDict
        
        
        seriesName=[]
        
        #check if user selected categoriesNumber and it is possible to use combinate 
        categoriesNumber = False
             
        sortedCat=None
        categories=None
        if columnX == TITLE_COL:
            categories = gSuite.allTrackTitles()
        elif columnX == 'line number':
            categories = None
        else:
            if columnX in dictNum.keys():
                categoriesBefore = [float(v) for v in gSuite.getAttributeValueList(columnX)]
                
                if axesScaleX == 'log10':
                    for cbN in range(0, len(categoriesBefore)):
                        if categoriesBefore[cbN]!=0:
                            categoriesBefore[cbN]=math.log(categoriesBefore[cbN], 10)
                
                sortedCat = sorted(range(len(categoriesBefore)), key=lambda k: categoriesBefore[k])
                categories=[]
                for n in sortedCat:
                    categories.append(categoriesBefore[n])
                
                categoriesNumber=True
                
            else:
                categories = gSuite.getAttributeValueList(columnX)
                
        
        #data are sorted according to numerical values
        data=[]
        for key, it in columnY.iteritems():
            if it == 'True':
                dataPart=[]
                seriesName.append(key)
                dataPart = []
                for x in gSuite.getAttributeValueList(key):
                    try:
                        if axesScaleY == 'log10':
                            if x!=0:
                                dataPart.append(math.log(float(x), 10))
                            else:
                                dataPart.append(0)
                        else:
                            dataPart.append(float(x))
                    except:
                        # need to support None in heatmap
                        if plotType == 'Heatmap':
                            dataPart.append(0)
                        else:
                            dataPart.append(x)
                if sortedCat!=None:
                    dataPartTemp=[]
                    for n in sortedCat:
                        dataPartTemp.append(dataPart[n])
                    dataPart = dataPartTemp
                data.append(dataPart)
                
        
        label=''
        if len(seriesName)!=0:
            label = '<b>{series.name}</b>: {point.x} {point.y}'
        else:
            label = '{point.x} {point.y}'
        
        vg = visualizationGraphs()
        
#         'Column', 'Scatter', 'Heatmap'
        
        if axesScaleX == 'log10':
            xAxisTitle = str(columnX) + ' (' + str(axesScaleX) + ')'
        else:
            xAxisTitle = str(columnX)
        
        if axesScaleY == 'log10':
            yAxisTitle = str('values') + ' (' + str(axesScaleY) + ')'
        else:
            yAxisTitle = str('values')    
        
        minFromList = min(min(d) for d in data)
        if minFromList > 0:
            minFromList = 0
        
        
        #combain series with data
        if plotRes == 'combine':
            if categoriesNumber == True:
                newData=[]
                for d in data:
                    newDataPart=[]
                    for cN in range(0, len(categories)):
                        newDataPart.append([categories[cN], d[cN]])
                    newData.append(newDataPart)
                data=newData
                categories=None
                        
                    
        
        
        res=''
        if plotSeries == 'Single':
            if plotType == 'Scatter':
                res += vg.drawScatterChart(
                     data,
                     categories = categories,
                     xAxisRotation = 90,
                     marginTop = 30,
                     xAxisTitle = xAxisTitle,
                     yAxisTitle = yAxisTitle,
                     height = 500,
                     seriesName = seriesName,
                     label = label,
                     minY=minFromList
#                      titleText = 'Plot',
                     )
            if plotType == 'Pie':
                res += vg.drawPieChart(
                    data[0],
                    seriesName = categories,
                    height = 400,
                    titleText = seriesName[0],
                    )
                
            if plotType == 'Column':
                res += vg.drawColumnChart(
                     data,
                     categories = categories,
                     xAxisRotation = 90,
                     marginTop = 30,
                     xAxisTitle = xAxisTitle,
                     yAxisTitle = yAxisTitle,
                     height = 500,
                     seriesName = seriesName,
                     label = label,
                     minY=minFromList
#                      titleText = 'Plot',
                     )
            if plotType == 'Line':
                res += vg.drawLineChart(
                     data,
                     categories = categories,
                     xAxisRotation = 90,
                     marginTop = 30,
                     xAxisTitle = xAxisTitle,
                     yAxisTitle = yAxisTitle,
                     height = 500,
                     seriesName = seriesName,
                     label = label,
                     minY=minFromList
#                      titleText = 'Plot',
                     )
            if plotType == 'Heatmap':
                res += vg.drawHeatmapSmallChart(
                     data,
                     categories = categories,
                     xAxisRotation = 90,
                     marginTop = 30,
                     xAxisTitle = xAxisTitle,
                     yAxisTitle = yAxisTitle,
                     height = 500,
                     seriesName = seriesName,
                     label = label,
#                      titleText = 'Plot',
                     )
        elif plotSeries == 'Multi':
            if plotType == 'Scatter':
                for nrD in range(0, len(data)):
                    if plotRes == 'combine':
                        data[nrD]=[data[nrD]]
                    res += vg.drawScatterChart(
                         data[nrD],
                         categories = categories,
                         xAxisRotation = 90,
                         marginTop = 30,
                         xAxisTitle = xAxisTitle,
                         yAxisTitle = yAxisTitle,
                         height = 500,
                         seriesName = [seriesName[nrD]],
                         label = label,
                         minY=minFromList
    #                      titleText = 'Plot',
                         )
            if plotType == 'Column':
                res += vg.drawColumnCharts(
                     data,
                     categories = [categories for x in range(0, len(data))],
                     xAxisRotation = 90,
                     marginTop = 30,
                     xAxisTitle = xAxisTitle,
                     yAxisTitle = yAxisTitle,
                     height = 500,
                     seriesName = [[seriesName[elD]] for elD in range(0, len(data))],
                     label = label,
                     minY=minFromList
#                      titleText = 'Plot',
                     ) 
            if plotType == 'Line':
                for nrD in range(0, len(data)):
                    if plotRes == 'combine':
                        data[nrD]=[data[nrD]]
                    res += vg.drawLineChart(
                         data[nrD],
                         categories = categories,
                         xAxisRotation = 90,
                         marginTop = 30,
                         xAxisTitle = xAxisTitle,
                         yAxisTitle = yAxisTitle,
                         height = 500,
                         seriesName = [seriesName[nrD]],
                         label = label,
                         minY=minFromList
    #                      titleText = 'Plot',
                         )                  
        
        htmlCore = HtmlCore()
        htmlCore.begin()
        htmlCore.divBegin(divId='results-page')
        htmlCore.divBegin(divClass='results-section')
        
        htmlCore.line(res)
        
        htmlCore.divEnd()
        htmlCore.divEnd()
        htmlCore.end()
        
        print htmlCore
        
    @classmethod
    def validateAndReturnErrors(cls, choices):

        errorString = GeneralGuiTool._checkGSuiteFile(choices.gSuite)
        if errorString:
            return errorString
        
        gSuite = getGSuiteFromGalaxyTN(choices.gSuite)
        errorString = GeneralGuiTool._checkGSuiteRequirements \
            (gSuite)
        
        if errorString:
            return errorString
        
        columnY = choices.columnY
        if isinstance(columnY, dict):
            if not True in columnY.values():
                errorString = 'Check at least one value for y-Axis'
                return errorString


    #@staticmethod
    #def getSubToolClasses():
    #    '''
    #    Specifies a list of classes for subtools of the main tool. These
    #    subtools will be selectable from a selection box at the top of the page.
    #    The input boxes will change according to which subtool is selected.
    #    '''
    #    return None
    #
    @staticmethod
    def isPublic():
        '''
        Specifies whether the tool is accessible to all users. If False, the
        tool is only accessible to a restricted set of users as defined in
        LocalOSConfig.py.
        '''
        return True
    #
    #@staticmethod
    #def isRedirectTool():
    #    '''
    #    Specifies whether the tool should redirect to an URL when the Execute
    #    button is clicked.
    #    '''
    #    return False
    #
    #@staticmethod
    #def getRedirectURL(choices):
    #    '''
    #    This method is called to return an URL if the isRedirectTool method
    #    returns True.
    #    '''
    #    return ''
    #
    #@staticmethod
    #def isHistoryTool():
    #    '''
    #    Specifies if a History item should be created when the Execute button is
    #    clicked.
    #    '''
    #    return True
    #
    #@classmethod
    #def isBatchTool(cls):
    #    '''
    #    Specifies if this tool could be run from batch using the batch. The
    #    batch run line can be fetched from the info box at the bottom of the
    #    tool.
    #    '''
    #    return cls.isHistoryTool()
    #
    #@staticmethod
    #def isDynamic():
    #    '''
    #    Specifies whether changing the content of texboxes causes the page to
    #    reload.
    #    '''
    #    return True
    #
    #@staticmethod
    #def getResetBoxes():
    #    '''
    #    Specifies a list of input boxes which resets the subsequent stored
    #    choices previously made. The input boxes are specified by index
    #    (starting with 1) or by key.
    #    '''
    #    return []
    #
    
    @staticmethod
    def createDescription(toolDescription=None, stepsToRunTool=None, toolResult=None, limitation=None):
        core = HtmlCore()
        
        if toolDescription!=None or stepsToRunTool!=None or toolResult!=None or limitation!=None:
            core.divBegin(divId='decription-page')
            core.divBegin(divClass='decription-section')
            core.header('Description')  
            
            #small description of tool (The resaon of creating the tool)
            if toolDescription!=None:
                core.divBegin(divClass='decription-section-main')
                core.paragraph(toolDescription)
                core.divEnd()
    
            #how to use tool
            if stepsToRunTool!=None:
                core.paragraph('To run the tool, follow these steps:')
                core.orderedList(stepsToRunTool)
    
            #what is the result of tool
            if toolDescription!=None:
                core.divBegin(divClass='decription-section-main')
                core.paragraph(toolResult)
                core.divEnd()
            
            #what are the limitation for tool
    #         if limitation:
    #             limits...
            
            
            core.divEnd()
            core.divEnd()
        
        return str(core)
    
    @staticmethod
    def getToolDescription():
        
        toolDescription = 'The tool allow to present metadata columns from gSuite or results from tabular file in the chart.'
        
        stepsToRunTool = ['Select GSuite or file with tabular from history',
                          'Select way of showing series as single or multi charts',
                          'Select type of chart',
                          'Select value for x-Axis',
                          'Select type of scale for x-Axis',
                          'Select value for y-Axis',
                          'Select type of scale for y-Axis',
                          'Select results of plotting (option available for selected type of charts)']
        
        toolResult = 'The results are presented in an interactive chart'
        
        return GenericPlotDataTool.createDescription(toolDescription=toolDescription, 
                                              stepsToRunTool=stepsToRunTool, 
                                              toolResult=toolResult)
    
    #@staticmethod
    #def getToolIllustration():
    #    '''
    #    Specifies an id used by StaticFile.py to reference an illustration file
    #    on disk. The id is a list of optional directory names followed by a file
    #    name. The base directory is STATIC_PATH as defined by Config.py. The
    #    full path is created from the base directory followed by the id.
    #    '''
    #    return None
    #
    #@staticmethod
    #def getFullExampleURL():
    #    return None
    #
    #@staticmethod
    #def isDebugMode():
    #    '''
    #    Specifies whether the debug mode is turned on.
    #    '''
    #    return False
    #
    @staticmethod
    def getOutputFormat(choices):
        return 'customhtml'
