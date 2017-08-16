from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.util.TrackReportCommon import STAT_OVERLAP_COUNT_BPS,\
    STAT_OVERLAP_RATIO, STAT_FACTOR_OBSERVED_VS_EXPECTED, processRawResults, processResult, \
    STAT_COVERAGE_RATIO_VS_REF_TRACK, STAT_COVERAGE_RATIO_VS_QUERY_TRACK, STAT_COVERAGE_REF_TRACK_BPS
from gold.gsuite.GSuiteConstants import TITLE_COL
from quick.webtools.mixin.UserBinMixin import UserBinMixin
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from collections import OrderedDict
from quick.application.GalaxyInterface import GalaxyInterface
from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.application.ExternalTrackManager import ExternalTrackManager
import operator
from quick.webtools.restricted.visualization.visualizationGraphs import visualizationGraphs

# This is a template prototyping GUI that comes together with a corresponding
# web page.

class PlotLevelGSuite(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Plot level GSuite"

    @staticmethod
    def getInputBoxNames():
        return [('Select tabular file','file'),
                ('Is the header in your file','fileHeader'),
                ('Select label for x-Axis','columnX'),
                ('Select value for y-Axis','columnY'),
                ('Select title for plots','title'),
                ('Sorted by (index from all label counted from 0)','columnSorted'),
                ('Filtered by (index from all label counted from 0)','columnFiltered'),
                ('Select way of showing plots as', 'plot'),
                ('Select way of showing series as', 'plotSeries'),
                ]

    @staticmethod
    def getOptionsBoxFile():
        return GeneralGuiTool.getHistorySelectionElement('txt', 'tabular')
    
    
    
    
    @staticmethod
    def getOptionsBoxFileHeader(prevChoices):
        return ['Yes', 'No']
    
    @staticmethod
    def getOptionsBoxColumnX(prevChoices):
        
        if not prevChoices.file:
            return
        
        i=0
        with open(ExternalTrackManager.extractFnFromGalaxyTN(prevChoices.file.split(':')), 'r') as f:
            columnXdict=OrderedDict()
            for x in f.readlines():
                if i ==0:
                    el = x.strip('\n').split('\t')
                    nr=0
                    for e in el:
                        if e!='':
                            columnXdict['column index('+str(nr) + ')-- ' + str(e)] = False
                            nr+=1
                i+=1
        f.closed
        
        
#         if prevChoices.title:
#             titledict = prevChoices.title
#             
#             for k, v in titledict.items():
#                 if v == True:
#                     del columnXdict[k]
#         
#         if prevChoices.columnY:
#             columnYdict = prevChoices.columnY
#             
#             for k, v in columnYdict.items():
#                 if v == True:
#                     del columnXdict[k]
        
        return columnXdict
    
    @staticmethod
    def getOptionsBoxColumnY(prevChoices):
        
        if not prevChoices.file:
            return
        
        i=0
        with open(ExternalTrackManager.extractFnFromGalaxyTN(prevChoices.file.split(':')), 'r') as f:
            columnYdict=OrderedDict()
            for x in f.readlines():
                if i ==0:
                    el = x.strip('\n').split('\t')
                    nr=0
                    for e in el:
                        if e!='':
                            columnYdict['column index('+str(nr) + ')-- ' + str(e)] = False
                            nr+=1
                i+=1
        f.closed
        
        if prevChoices.columnX:
            columnXdict = prevChoices.columnX
            
            for k, v in columnXdict.items():
                if v == True:
                    del columnYdict[k]
        
#         if prevChoices.title:
#             titledict = prevChoices.title
#             
#             for k, v in titledict.items():
#                 if v == True:
#                     del columnXdict[k]
            
        return columnYdict
    
    @staticmethod
    def getOptionsBoxTitle(prevChoices):
        
        if not prevChoices.file:
            return
        
        i=0
        with open(ExternalTrackManager.extractFnFromGalaxyTN(prevChoices.file.split(':')), 'r') as f:
            titledict=OrderedDict()
            for x in f.readlines():
                if i ==0:
                    el = x.strip('\n').split('\t')
                    nr=0
                    for e in el:
                        if e!='':
                            titledict['column index('+str(nr) + ')-- ' + str(e)] = False
                            nr+=1
                i+=1
        f.closed
        
        if prevChoices.columnX:
            columnXdict = prevChoices.columnX
            
            for k, v in columnXdict.items():
                if v == True:
                    del titledict[k]
        
        if prevChoices.columnY:
            columnYdict = prevChoices.columnY
            
            for k, v in columnYdict.items():
                if v == True:
                    del titledict[k]
            
            
        return titledict
    
    
    @staticmethod
    def getOptionsBoxColumnSorted(prevChoices):
        return ''
    
    @staticmethod
    def getOptionsBoxColumnFiltered(prevChoices):
        return ''

    @classmethod
    def getOptionsBoxPlot(cls, prevChoices):
        return ['Single', 'Multi']

    @classmethod
    def getOptionsBoxPlotSeries(cls, prevChoices):
        if prevChoices.plot == 'Multi':
            return ['Single', 'Multi']
    
    @staticmethod
    def returnList(columnX, key=False):
        columnXList=[] 
        i=0
        for k,v in columnX.iteritems():
            if key == True:
                if v == 'True':
                    columnXList.append(i)
            else:
                columnXList.append(k)
            i+=1
        return columnXList
    
    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        
        file = choices.file
        fileHeader = choices.fileHeader
        title = choices.title
        columnX = choices.columnX
        columnY = choices.columnY

        plot = choices.plot
        plotSeries = choices.plotSeries
        
        columnSorted = choices.columnSorted
        columnFiltered = choices.columnFiltered
        
        
        i=0
        with open(ExternalTrackManager.extractFnFromGalaxyTN(file.split(':')), 'r') as f:
            dataX=[]
            for x in f.readlines():
                if i==0 and fileHeader == 'Yes':
                    pass
                else:
                    el = x.strip('\n').split('\t')
                    nr=0
                    
                    l=[]
                    for e in el:
                        if e!='':
                            try:
                                l.append(float(e))
                            except:
                                l.append(e)
                            nr+=1
                    dataX.append(l)
                i+=1
        f.closed
        
        
        oryginalList = PlotLevelGSuite.returnList(columnX)
        
        
        columnX = PlotLevelGSuite.returnList(columnX, True)
        columnY = PlotLevelGSuite.returnList(columnY, True)
        
        
        title = PlotLevelGSuite.returnList(title, True)
        
        columnSortedList = columnSorted.strip(' ').split(',')
        columnFiltered = columnFiltered.strip(' ').split(',')
        
        for cNum in range(0, len(columnSortedList)):
            columnSortedList[cNum] = int(columnSortedList[cNum])
        
        dataX = sorted(dataX, key=operator.itemgetter(*columnSortedList), reverse=False)
        #dataX = sorted(dataX, key=operator.itemgetter(3,4,0,1,2), reverse=False)
        
        
        #prepare data for plotting
        
        final = OrderedDict()
        
        for dNum in range(0, len(dataX)):
            
            columnFilteredList=''
            for eNum in columnFiltered:
                columnFilteredList += str(dataX[dNum][int(eNum)])+ '-'
            
            
            if not columnFilteredList in final:
                
                final[columnFilteredList] = OrderedDict()
                final[columnFilteredList]['title']=''
                
                tit = ''
                j=0
                for eNum in title:
                    if j < len(title)-1:
                        tit += str(dataX[dNum][eNum]) + ' '
                    else:
                        tit += str(dataX[dNum][eNum])
                    j+=1
                    
                final[columnFilteredList]['title']=tit
                final[columnFilteredList]['categories']=[]
                final[columnFilteredList]['data']=OrderedDict()
                
            cat = ''
            j=0
            for eNum in columnX:
                if j < len(columnX)-1:
                    cat += str(dataX[dNum][eNum]) + ' '
                else:
                    cat += str(dataX[dNum][eNum])
                j+=1
            final[columnFilteredList]['categories'].append(cat)
            
            
            for eNum in columnY:
                if not eNum in final[columnFilteredList]['data']:
                    final[columnFilteredList]['data'][eNum]=[]
                final[columnFilteredList]['data'][eNum].append(dataX[dNum][eNum])
                
        seriesName=[]
        data=[]
        categories=[]
        d=[]
        cat=[]
        title=[]
        plotLinesName=[]
        plotLines=[]
        pl=[]
        i=0
        
        for k1, v1 in final.iteritems():
#             d=[]
            for k2, v2 in v1['data'].iteritems():
#                 d.append(v2)
                if plot == 'Single':
                    data += v2
                seriesName.append([oryginalList[k2].split("--")[0]])


            if plot == 'Single':
                categories += v1['categories']
                plotLinesName.append(k1)

                if i == 0:
                    #plotLines.append([0, len(v1['categories'])])
                    plotLines.append(0)
                else:
                    plotLines.append(plotLines[-1]+len(v1['categories']))
                    #plotLines.append([plotLines[-1][1], plotLines[-1][1]+len(v1['categories'])])
                
                
            title.append(v1['title'])
            
            if plot == 'Multi' and plotSeries =='Single':
                data.append([v2])
                categories.append(v1['categories'])

            if plot == 'Multi' and plotSeries =='Multi':

                if len(categories) > 0 and v1['categories'] != categories[len(cat)-1]:
                    data.append(d)
                    d=[v2]
                    plotLinesName.append(pl)
                    pl = [k1]
                    if not v1['categories'] in categories:
                        categories.append(v1['categories'])
                else:
                    if not v1['categories'] in categories:
                        categories.append(v1['categories'])
                    d.append(v2)
                    pl.append(k1)
            
            i+=1

        if plot == 'Multi' and plotSeries == 'Multi':
            data.append(d)
            plotLinesName.append(pl)
        
        vg = visualizationGraphs()
        res=''
        
        
        if plot == 'Single':
            res += vg.drawColumnChart(
                data,
                categories = categories,
                xAxisRotation = 90,
                marginTop = 30,
                height = 300,
                plotLines = plotLines,
                plotLinesName=plotLinesName,
                plotBandsColor=True,
                showInLegend=False
                )

             
        if plot == 'Multi':
            if plotSeries == 'Multi':

                res += vg.drawColumnCharts(
                    data,
                    categories=categories,
                    xAxisRotation=90,
                    marginTop=30,
                    height=300,
                    seriesName=plotLinesName,
                    minY=0
                )
            if plotSeries == 'Single':
                res += vg.drawColumnCharts(
                    data,
                    categories = categories,
                    xAxisRotation = 90,
                    marginTop = 30,
                    height = 300,
                    seriesName = seriesName,
                    minY=0,
                    titleText = title,
                     )
            
        print res
        

    @staticmethod
    def validateAndReturnErrors(choices):
        
        return None

   
    @staticmethod
    def isPublic():
        
        return True
    
    @staticmethod
    def getOutputFormat(choices):
        
        return 'customhtml'
