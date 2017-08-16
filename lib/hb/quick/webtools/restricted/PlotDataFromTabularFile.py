from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.application.ExternalTrackManager import ExternalTrackManager
from collections import OrderedDict
from quick.webtools.restricted.visualization.visualizationGraphs import visualizationGraphs
from proto.hyperbrowser.HtmlCore import HtmlCore
import math

# This is a template prototyping GUI that comes together with a corresponding
# web page.

class PlotDataFromTabularFile(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Plot data from tabular file"

    @staticmethod
    def getInputBoxNames():
        return [('Select tabular file','file'),
                ('Select way of showing series as', 'plotSeries'),
                ('Select type of chart', 'plotType'),
                ('Select value for x-Axis', 'columnX'),
                ('Select type of scale for x-Axis', 'axesScaleX'),
                ('Select value for y-Axis', 'columnY'),
                ('Select type of scale for y-Axis', 'axesScaleY'),
                ]

    @staticmethod
    def getOptionsBoxFile():
        return GeneralGuiTool.getHistorySelectionElement('txt', 'tabular')
    
    @classmethod
    def getOptionsBoxPlotSeries(cls, prevChoices): 
        return ['Single', 'Multi']
    
    @classmethod
    def getOptionsBoxPlotType(cls, prevChoices):
        return ['Column', 'Scatter']

    @staticmethod
    def getOptionsBoxColumnX(prevChoices):
        if not prevChoices.file:
            return
        
        file = prevChoices.file
        column = PlotDataFromTabularFile.returnColumnList(file)
            
        return ['line number'] + column
    
    @staticmethod
    def getOptionsBoxAxesScaleX(prevChoices):
        return ['linear', 'log10', 'no uniform scale (sorted values as labels)']

    
    @staticmethod
    def getOptionsBoxColumnY(prevChoices):
        if not prevChoices.file:
            return
        
        file = prevChoices.file
        column = PlotDataFromTabularFile.returnColumnDict(file, type = 'Number')
            
        return column
    
    @staticmethod
    def getOptionsBoxAxesScaleY(prevChoices):
        return ['linear', 'log10']
    
    
    
    @staticmethod
    def returnColumnList(file, type=None):
        inputFile = open(ExternalTrackManager.extractFnFromGalaxyTN(file.split(':')), 'r')  
        
        column=[]
        i=0
        with inputFile as f:
            for x in f.readlines():
                if i==0:
                    for el in list(x.strip('\n').split('\t')):
                        column.append(el)
                if type == 'Number':
                    if i==1:
                        keys = column.keys()
                        j=0
                        for el in list(x.strip('\n').split('\t')):
                            try:
                                el = float(el)
                            except:
                                inx = column.keys[j]
                                del column[inx]
                            j+=1
                i+=1
        inputFile.close()
        
        return column
    
    @staticmethod
    def returnColumnDict(file, type=None):
        inputFile = open(ExternalTrackManager.extractFnFromGalaxyTN(file.split(':')), 'r')  
        
        column=OrderedDict()
        i=0
        with inputFile as f:
            for x in f.readlines():
                if i==0:
                    for el in list(x.strip('\n').split('\t')):
                        column[el] = False
                if type == 'Number':
                    if i==1:
                        keys = column.keys()
                        j=0
                        for el in list(x.strip('\n').split('\t')):
                            try:
                                el = float(el)
                            except:
                                del column[keys[j]]
                            j+=1
                i+=1
        inputFile.close()
        
        return column
    
    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        
        file = choices.file
        columnX = choices.columnX
        columnY = choices.columnY
        plotType = choices.plotType
        axesScaleX = choices.axesScaleX
        axesScaleY = choices.axesScaleY
        plotSeries = choices.plotSeries
        
        if axesScaleX == 'linear':
            plotRes = 'combine'
        elif axesScaleX == 'log10':
            plotRes = 'separate'
        elif axesScaleX == 'no uniform scale (sorted values as labels)':
            plotRes = 'separate'
        
        
        inputFile = open(ExternalTrackManager.extractFnFromGalaxyTN(file.split(':')), 'r')  
        
        dataS=OrderedDict()
        dataS['xAxis'] = OrderedDict()
        dataS['yAxis'] = OrderedDict()
        i=0
        
        with inputFile as f:
            for x in f.readlines():
                if i==0:
                    rowColumn = list(x.strip('\n').split('\t'))
                else:
                    j=0
                    for el in list(x.strip('\n').split('\t')):
#                         if columnX[rowColumn[j]] == 'True':
#                             if not rowColumn[j] in dataS['xAxis']:
#                                 dataS['xAxis'][rowColumn[j]] = []
#                             dataS['xAxis'][rowColumn[j]].append(el)
                        if rowColumn[j] in columnX:
                            if not rowColumn[j] in dataS['xAxis']:
                                dataS['xAxis'][rowColumn[j]] = []
                            dataS['xAxis'][rowColumn[j]].append(el)
                        if rowColumn[j] in columnY and columnY[rowColumn[j]] == 'True':
                            if not rowColumn[j] in dataS['yAxis']:
                                dataS['yAxis'][rowColumn[j]] = []
                                
                            dataS['yAxis'][rowColumn[j]].append(float(el))
                            
                        j+=1
                i+=1
        inputFile.close()
        
        
#        this will be used just for x - values
#         keysX = dataS['xAxis'].keys()
#         if keysX == 1:
#             plotSeries = 'Single'
#         else:
#             plotSeries = 'Multi'

            
        #sorting categories values
        categoriesNumber = False
             
        sortedCat=None
        categories=None
        
        if columnX == 'line number':
            categories = None
        else:
            #if columnX['xAxis'] in columnY.keys():
            if columnX in columnY.keys():
                categoriesBefore = [float(v) for v in dataS['xAxis'][columnX]] 
               
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
                categories = dataS['xAxis'][columnX]
        
        
        
        #dataS are sorted according to numerical values
        seriesName=[]
        data=[]
        for key, it in columnY.iteritems():
            if it == 'True':
                dataPart=[]
                seriesName.append(key)
                dataPart = []
            
                for x in dataS['yAxis'][key]:
                    try:
                        if axesScaleY == 'log10':
                            if x!=0:
                                dataPart.append(math.log(float(x), 10))
                            else:
                                dataPart.append(0)
                        else:
                            dataPart.append(float(x))
                    except:
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
                   
                        
        vg = visualizationGraphs()
        
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
        
        htmlCore = HtmlCore()
        htmlCore.begin()
        htmlCore.divBegin(divId='results-page')
        htmlCore.divBegin(divClass='results-section')
        
        htmlCore.line(res)
        
        htmlCore.divEnd()
        htmlCore.divEnd()
        htmlCore.end()
        
        print htmlCore
        

    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''
        return None

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
    #@staticmethod
    #def getToolDescription():
    #    '''
    #    Specifies a help text in HTML that is displayed below the tool.
    #    '''
    #    return ''
    #
    #@staticmethod
    #def getToolIllustration():
    #    '''
    #    Specifies an id used by StaticFile.py to reference an illustration file
    #    on disk. The id is a list of optional directory names followed by a file
    #    name. The base directory is STATIC_PATH as defined by AutoConfig.py. The
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
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'customhtml'
