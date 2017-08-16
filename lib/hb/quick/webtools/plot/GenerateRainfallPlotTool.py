from collections import OrderedDict

import math

from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.util.GenomeInfo import GenomeInfo
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.restricted.visualization.visualizationGraphs import visualizationGraphs
from quick.webtools.plot.RainfallPlot import RP

# author: DD
# date: 07.11.2016


class GenerateRainfallPlotTool(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Generate rainfall plot"

    @staticmethod
    def getInputBoxNames():
        return [
            ('Select GSuite', 'gsuite'),
            ('Select type of plotting', 'multiPlot'),
            # ('Select scale for bps value', 'scale'),
            ('Select bin size (default: 1000000)', 'bps'),
            # ('Point overlap points on black', 'overlap')
        ]

    @staticmethod
    def getOptionsBoxGsuite():
        return '__history__', 'gsuite'

    @staticmethod
    def getOptionsBoxMultiPlot(prevChoices):
        return ['Single', 'Multi']

    # @staticmethod
    # def getOptionsBoxScale(prevChoices):
    #     return ['Linear', 'Log']

    # @staticmethod
    # def getOptionsBoxOverlap(prevChoices):
    #     return ['no', 'yes']


    @staticmethod
    def getOptionsBoxBps(prevChoices):
        return '1000000'

    @staticmethod
    def getOutputFormat(choices):
        return 'customhtml'



    @staticmethod
    def validateAndReturnErrors(choices):

        if not choices.gsuite:
            return "Please select a GSuite from history"

        gsuite = getGSuiteFromGalaxyTN(choices.gsuite)
        if gsuite.genome == 'unknown':
            return "Please select a genome while creating GSuite"

        return None


    @staticmethod
    def getToolDescription():

        htmlCore = HtmlCore()

        htmlCore.paragraph('The tool is used to generate frequency of dataset and rainfall plots.')

        htmlCore.divider()

        htmlCore.paragraph('The input for tool is a GSuite file contains one or more datasets.')
        htmlCore.paragraph('The output for tool is a plot.')


        return str(htmlCore)

    @staticmethod
    def isPublic():
        return True


    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        #gsuite
        gsuite = getGSuiteFromGalaxyTN(choices.gsuite)

        #all boxes
        multiPlot = choices.multiPlot
        #scale = choices.scale
        #overlap = choices.overlap
        overlap = 'no'
        bps = int(choices.bps)

        rp = RP(gsuite)

        #get length of chromosomes and ordering
        chrItems = GenomeInfo.getStdChrLengthDict(gsuite.genome)
        chrOrder, chrLength = GenerateRainfallPlotTool.sortChrDict(chrItems)

        dataDict, dataDictLine, elementOrder, listResCopy, listDataCountPerBin, newResBinSizeListSum, chrList = GenerateRainfallPlotTool.countMutations(
            gsuite, chrLength, bps)

        seriesType, newSeriesNameRes, newSeriesNameResOE, yAxisMultiVal = rp.getOptionsForPlot(elementOrder, gsuite.allTrackTitles())
        newResList, newResBinSizeList, newResBinSizeListSortedList = rp.generateBinSizeList(elementOrder, listResCopy, listDataCountPerBin, newResBinSizeListSum)

        vg = visualizationGraphs()

        res = ''
        if multiPlot == 'Single':
            res += GenerateRainfallPlotTool.drawSinglePlot(vg, newResBinSizeListSortedList, chrLength, newResList, newSeriesNameRes, newResBinSizeList, overlap, seriesType, yAxisMultiVal)

        else:
            res += GenerateRainfallPlotTool.drawMultiPlot(newResList, newSeriesNameRes, newResBinSizeList, vg, seriesType, yAxisMultiVal)


        htmlCore = HtmlCore()
        htmlCore.begin()
        htmlCore.line('Bin size: ' + str(bps))
        htmlCore.line(res)
        htmlCore.end()
        htmlCore.hideToggle(styleClass='debug')
        print htmlCore




    @classmethod
    def prepareUpdateButton(cls, newResList):
        listElAll = []
        for l in newResList:
            listElAll += [[ll[0], round(ll[1], 1)] for ll in l]

        epsilonTF = True

        if epsilonTF == False:

            z = []
            y = []
            for i in listElAll:
                if i not in z:
                    z.append(i)
                else:
                    y.append(i)
        else:
            pass

        return "<button id='up'> update </button> <script> var listElAll =  " + str(listElAll) + "; </script>"

    @classmethod
    def prepareDataForRP(cls, newResList, newSeriesNameRes, newResBinSizeList):

        for nrNum in range(0, len(newResList)*2):
            if nrNum % 2 ==0:
                newSeriesNameRes[nrNum] = 'Frequency of ' + newSeriesNameRes[nrNum]
            else:
                newSeriesNameRes[nrNum] = 'Rainfall plot of ' + newSeriesNameRes[nrNum].replace('-- point', '')

        data = newResList + newResBinSizeList

        return data, newSeriesNameRes

    @classmethod
    def addJSForOverlap(cls):
        return """
                    <script>

                    function round(number, decimals)
                    {
                    return +(Math.round(number + "e+" + decimals) + "e-" + decimals);
                    }

                    function decNum(num)
                    {
                      return num.toString().length;
                    }


                    function arrayMinMax(arr) {
                      var len = arr.length,
                      maxX = -Infinity;
                      minX = Infinity;
                      maxY = -Infinity;
                      minY = Infinity;

                      maxArr = []

                      while (len--)
                      {
                        if (arr[len][0] < minX)
                        {
                          minX = arr[len][0];
                        }
                        if (arr[len][0] > maxX)
                        {
                          maxX = arr[len][0];
                        }

                        if (arr[len][1] < minY)
                        {
                          minY = arr[len][1];
                        }
                        if (arr[len][1] > maxY)
                        {
                          maxY = arr[len][1];
                        }



                      }

                      maxArr.push(minX);
                      maxArr.push(maxX);
                      maxArr.push(minY);
                      maxArr.push(maxY);

                      return maxArr;
                    }



                    $('#up').click(function () {

                        chart2  = $('#container2').highcharts();




                    var minX = 0;
                    var maxX = chart2.plotSizeX;
                    var minY = 0;
                    var maxY = chart2.plotSizeY * 0.7;



                    console.log(minX, minY, maxX, maxY);


                    decNumX = decNum(maxX);
                    decNumY = decNum(maxY);

                    minmaxArr = arrayMinMax(listElAll);

                    var minXval = minmaxArr[0];
                    var maxXval = minmaxArr[1];
                    var minYval = minmaxArr[2];
                    var maxYval = minmaxArr[3];

                    var xx=0;
                    var yy=0;
                    var listElAllNorm = [];

                    //to improve because 1 dot is 4 piksels - not 1, so it means that it will not find piksels which are partially
                    //covered, need to be fully covered

                    for (var elN =0; elN< listElAll.length; elN++)
                    {
                        //listElAllNorm.push([round((listElAll[elN][0] - minX) / (maxX - minX), decNumX-3), round((listElAll[elN][1] - minY) / (maxY - minY), decNumY-3)]);
                        xx = round((listElAll[elN][0] - minXval) / (maxXval - minXval), decNumX);
                        xx = xx * (maxX-minX) + minX;
                        yy = round((listElAll[elN][1] - minYval) / (maxYval - minYval), decNumY);
                        yy = yy * (maxY-minY) + minY;
                        listElAllNorm.push([xx, yy]);
                    }


                    //console.log(listElAllNorm);



                    var z = []
                    var yy = [] //unique elements
                    var index = 0
                    for (i in listElAllNorm)
                    {
                        //trick with changing list into string , because there is no simple method for array of arrays
                        //console.log(index, listElAllNorm[i], z, z.indexOf(listElAllNorm[i].toString()), yy);
                        if (z.indexOf(listElAllNorm[i].toString()) == -1)
                        {
                           z.push(listElAllNorm[i].toString());
                        }
                        else
                        {
                           yy.push(index);
                        }
                        index+=1;
                    }

                    //console.log(yy);


                    y = []
                    for (yEl in yy)
                    {
                        y.push(listElAll[yy[yEl]])
                    }



                    var seriesLength = chart2.series.length;
                    for(var i = seriesLength - 1; i > -1; i--)
                    {

                    if(chart2.series[i].name == 'overlap')
                       chart2.series[i].remove();
                    }

                    chart2.addSeries({
                        type: 'scatter',
                        name: 'overlap',
                        data: y.slice(0,y.length-1),
                        color: "#000000",
                        marker: { radius: 2, symbol: 'circle', },
                         yAxis: 0
                    });

                    //chart2.redraw();


                    //console.log(chart2);




                                })
                                </script>

                    """

    @classmethod
    def drawSinglePlot(cls, vg, newResBinSizeListSortedList, chrLength, newResList, newSeriesNameRes, newResBinSizeList,
                       overlap, seriesType, yAxisMultiVal):

        res = ''
        # line plot with sum of frequencies
        # res += vg.drawLineChart(
        #     [newResBinSizeListSortedList],
        #     seriesName=['sum per bin'],
        #     height=300,
        #     xAxisTitle='Genomic position',
        #     yAxisTitle='values',
        #     minY=0,
        #     plotLines=chrLength.values(),
        #     plotLinesName=chrLength.keys()
        # )
        #
        # res += '<div style="clear:both;"> </div>'

        data, newSeriesNameRes = GenerateRainfallPlotTool.prepareDataForRP(newResList, newSeriesNameRes,
                                                                           newResBinSizeList)

        if overlap == 'yes':
            res += GenerateRainfallPlotTool.prepareUpdateButton(newResList)

        # RP plot with frequency line
        res += vg.drawLineChartMultiYAxis(
            data,
            seriesName=newSeriesNameRes,
            seriesType=seriesType,
            height=400,  # newHeight + 0.3*newHeight,
            reversed=False,
            markerRadius=2,
            xAxisTitle='Genomic position',
            yAxisTitle=['Genomic distance', 'values'],
            yAxisMulti=yAxisMultiVal,
            minY=0,
            plotLines=chrLength.values(),
            plotLinesName=chrLength.keys()
        )

        if overlap == 'yes':
            res += GenerateRainfallPlotTool.addJSForOverlap()

        res += '<div style="clear:both;"> </div>'

        return res

    @classmethod
    def countForMultiPlot(cls, newResList, newSeriesNameRes, newResBinSizeList):

        for nrNum in range(0, len(newResList) * 2):
            if nrNum % 2 == 0:
                newSeriesNameRes[nrNum] = 'Frequency of ' + newSeriesNameRes[nrNum]
            else:
                newSeriesNameRes[nrNum] = 'Rainfall plot of ' + newSeriesNameRes[nrNum].replace('-- point', '')


        maxLength = -10000
        for nrNum in range(1, len(newResList)):
            if maxLength < newResList[nrNum][-1][0]:
                maxLength = newResList[nrNum][-1][0]

        #newSeriesNameRes[0] = newSeriesNameRes[0] + ' -- ' + str(len(newResList[0]))
        for nrNum in range(1, len(newResList)):
            for nrNum1 in range(0, len(newResList[nrNum])):
                newResList[nrNum][nrNum1][0] = newResList[nrNum][nrNum1][0] + maxLength * nrNum
            for nrNum1 in range(0, len(newResBinSizeList[nrNum])):
                newResBinSizeList[nrNum][nrNum1][0] = newResBinSizeList[nrNum][nrNum1][0] + maxLength * nrNum
            #newSeriesNameRes[nrNum] = newSeriesNameRes[nrNum] + ' -- ' + str(len(newResList[nrNum]))

        return newResList, newResBinSizeList, newSeriesNameRes

    @classmethod
    def drawMultiPlot(cls, newResList, newSeriesNameRes, newResBinSizeList, vg, seriesType, yAxisMultiVal):
        res = ''
        newResList, newResBinSizeList, newSeriesNameRes = GenerateRainfallPlotTool.countForMultiPlot(newResList,
                                                                                                     newSeriesNameRes,
                                                                                                     newResBinSizeList)
        res += vg.drawLineChartMultiYAxis(
            newResList + newResBinSizeList,
            seriesName=newSeriesNameRes,
            seriesType=seriesType,
            height=500,
            reversed=False,
            markerRadius=1,
            label='<b>{series.name}: </b>{point.x}, {point.y} <br \>',
            xAxisTitle='Genomic position',
            yAxisTitle=['Genomic distance', 'Values'],
            yAxisMulti=yAxisMultiVal,
            minY=0,
            # plotLines=chrLength.values(),
            # plotLinesName=chrLength.keys()
        )

        res += '<div style="clear:both;"> </div>'
        return res


    @classmethod
    def countMutations(cls, gsuite, chrLength, bps):

        dataDict = OrderedDict()
        dataDictLine = OrderedDict()

        chrList = []

        elementOrder = []

        # parse the tracks
        for track in gsuite.allTrackTitles():

            # count one track
            gSuiteTrack = gsuite.getTrackFromTitle(track)
            trackName = track

            dataDict[trackName] = OrderedDict()
            dataDictLine[trackName] = OrderedDict()

            # read from file
            newDict = OrderedDict()
            with open(gSuiteTrack.path, 'r') as f:
                i = 0
                for x in f.readlines():
                    el = x.strip('\n').split('\t')
                    if len(el) >= 2:
                        try:
                            st = int(el[1])
                            if not el[0] in newDict:
                                newDict[el[0]] = []
                            if not el[0] in chrList:
                                chrList.append(el[0])
                            newDict[el[0]].append([el[0], st, int(el[2])])
                        except:
                            pass
                i += 1

            # sort file according to start position
            newDict2 = OrderedDict()
            for key, it in chrLength.items():
                if key in newDict:
                    newDict2[key] = sorted(newDict[key], key=lambda x: x[1])

            j=0
            chr =''
            for key, it in newDict2.items():

                if j == 0:
                    chr = key
                    j+=1
                i = 0
                prevEnd = 0
                label = 0

                for el in it:
                    if len(el) >= 2:

                        if not int(el[1]) in dataDictLine[trackName]:
                            dataDictLine[trackName][int(el[1])] = 1
                        start = int(el[1])
                        if prevEnd != 0:


                            if chr == key: #this is a condition which allow us to do not count the distance for the last an start points on the next chromosomes
                                if not label in dataDict[trackName]:
                                    dataDict[trackName][label] = OrderedDict()
                                    dataDict[trackName][label]['val'] = 0
                                    dataDict[trackName][label]['tot'] = 0

                                if start - prevEnd > 0:
                                    dataDict[trackName][label]['val'] += math.log(start - prevEnd, 10)
                                elif start - prevEnd == 0:
                                    dataDict[trackName][label]['val'] += start - prevEnd

                                dataDict[trackName][label]['tot'] += 1
                            else:
                                chr = key

                        label = int(el[1]) + int(chrLength[el[0]])

                        prevEnd = int(el[1])  # not anymore prevEnd
                        i += 1

            elementOrder.append(i)


        listResCopy = []
        for key0, it0 in dataDict.iteritems():
            listResPart = []
            for key2 in sorted(it0):
                listResPart.append([key2, it0[key2]['val']])
            listResCopy.append(listResPart)

        # if there is no need to have ordering
        # elementOrder = sorted(range(len(elementOrder)), key=lambda k: elementOrder[k], reverse=True)
        # then
        elementOrder = [k for k in range(0, len(elementOrder))]

        lengthOfLastChromosome = GenomeInfo.getChrLen(gsuite.genome, chrLength.keys()[-1])

        howManyIntervalsPerBin = int((chrLength.values()[-1] + lengthOfLastChromosome) / bps) + 1

        listOfBinSumPerTrack = []
        for interval in range(0, howManyIntervalsPerBin):
            listOfBin = (interval * bps, (interval + 1) * bps)
            listOfBinSumPerTrack.append(listOfBin)

            newResBinSizeListSum = {}

        listDataCountPerBin = []
        for el in listResCopy:
            data = filter(None, [filter(lambda l: t[0] <= int(l[0]) < t[1], el) for t in listOfBinSumPerTrack])
            listData = []
            for d in data:

                countD = int(d[0][0] / bps) * bps + bps / 2
                lenD = len(d)

                w = 0
                listData.append([countD, lenD])

                if not countD in newResBinSizeListSum.keys():
                    newResBinSizeListSum[countD] = lenD
                else:
                    newResBinSizeListSum[countD] += lenD

            listDataCountPerBin.append(listData)

        return dataDict, dataDictLine, elementOrder, listResCopy, listDataCountPerBin, newResBinSizeListSum, chrList

    @classmethod
    def sortChrDict(cls, chr):

        remeberString = []
        keysList = []
        for el in chr.keys():
            try:
                elC = int(el.replace('chr', ''))
                keysList.append(elC)
            except:
                remeberString.append(el.replace('chr', ''))

        sChr = sorted(keysList) + sorted(remeberString)

        chrDict = OrderedDict()
        chrLength = OrderedDict()
        val = 0
        for elChr in sChr:
            el = 'chr' + str(elChr)
            chrDict[el] = chr[el]
            chrLength[el] = val
            val += chr[el]

        return chrDict, chrLength



    #@staticmethod
    #def getSubToolClasses():
    #    '''
    #    Specifies a list of classes for subtools of the main tool. These
    #    subtools will be selectable from a selection box at the top of the page.
    #    The input boxes will change according to which subtool is selected.
    #    '''
    #    return None
    #
    #@staticmethod
    #def isPublic():
    #    '''
    #    Specifies whether the tool is accessible to all users. If False, the
    #    tool is only accessible to a restricted set of users as defined in
    #    LocalOSConfig.py.
    #    '''
    #    return False
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
    #@staticmethod
    #def getOutputFormat(choices):
    #    '''
    #    The format of the history element with the output of the tool. Note
    #    that html output shows print statements, but that text-based output
    #    (e.g. bed) only shows text written to the galaxyFn file.In the latter
    #    case, all all print statements are redirected to the info field of the
    #    history item box.
    #    '''
    #    return 'html'
