from _collections import defaultdict
from collections import OrderedDict

from numpy import mean, float64

from gold.application.HBAPI import doAnalysis
from gold.description.AnalysisDefHandler import AnalysisSpec
from gold.statistic.DerivedOverlapStat import DerivedOverlapStat
from gold.statistic.MultitrackCoverageDepthStat import MultitrackCoverageDepthStat
from gold.statistic.RawOverlapStat import RawOverlapStat
from gold.track.Track import Track
from gold.util.CommonFunctions import strWithNatLangFormatting
from proto.hyperbrowser.HtmlCore import HtmlCore
from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
from quick.application.GalaxyInterface import GalaxyInterface
from quick.multitrack.GSuiteOverview import GSuiteOverview
from quick.statistic.MultiTrackBpsCoveragePerDepthLevelStat import MultiTrackBpsCoveragePerDepthLevelStat
from quick.statistic.MultitrackSummarizedInteractionStat import MultitrackSummarizedInteractionStat
from quick.statistic.ThreeWayFocusedTrackProportionCoveragesAtDepthsRawStat import \
    ThreeWayFocusedTrackProportionCoveragesAtDepthsRawStat
from quick.visualization.VisualizationUtil import normalizeMatrixData

'''
Created on Dec 11, 2014

@author: boris
'''

REFERENCE_TRACK = 'Reference track'
STAT_OVERLAP_COUNT_BPS = 'Overlap count (bps)'
STAT_COVERAGE_QUERY_TRACK_BPS = 'Coverage query track (bps)'
STAT_COVERAGE_REF_TRACK_BPS = 'Coverage ref track (bps)'
STAT_OVERLAP_RATIO = 'Overlap ratio (overall)'
STAT_FACTOR_OBSERVED_VS_EXPECTED = 'Ratio of observed versus expected overlap'
STAT_COVERAGE_RATIO_VS_QUERY_TRACK = 'Overlap ratio to query track'
STAT_COVERAGE_RATIO_VS_REF_TRACK = 'Overlap ratio to reference track'

HEADER_ROW = [REFERENCE_TRACK,
              STAT_FACTOR_OBSERVED_VS_EXPECTED,
              STAT_OVERLAP_COUNT_BPS,
              STAT_COVERAGE_REF_TRACK_BPS,
              STAT_OVERLAP_RATIO,
              STAT_COVERAGE_RATIO_VS_QUERY_TRACK,
              STAT_COVERAGE_RATIO_VS_REF_TRACK]
STAT_LIST_INDEX = {STAT_OVERLAP_COUNT_BPS: 1,
                   STAT_COVERAGE_REF_TRACK_BPS: 2,
                   STAT_OVERLAP_RATIO: 3,
                   STAT_FACTOR_OBSERVED_VS_EXPECTED: 0,
                   STAT_COVERAGE_RATIO_VS_QUERY_TRACK: 4,
                   STAT_COVERAGE_RATIO_VS_REF_TRACK: 5}


def processRawResults(results):
    '''Results is a dict of trackName -> object returned by the RawOverlapStat statistic.
    The processed results is a dictionary where the key is the name of the reference track
    and therefore name of the raw in the results table.
    The value contains the list of statistics for that reference track
    and is later displayed as a row in the results table.
    '''
    resultsList = results.values()
    assert(len(resultsList) > 0)
    singleResult = resultsList[0]
    regionLength = singleResult['Neither'] + singleResult['Only1'] + singleResult['Only2'] + singleResult['Both']
    processedResults = OrderedDict()
    for refTrackName, refTrackResults in results.iteritems():
        processedResults[refTrackName] = []
        both = int(refTrackResults['Both'])
        query = int(refTrackResults['Only1']) + both
        reference = int(refTrackResults['Only2']) + both
        overlapRatio = both * 1.0 / regionLength
        expectedOverlapRatio = query * 1.0 / regionLength * reference / regionLength

        # processedResults[refTrackName].append(query) #1
        processedResults[refTrackName].append('N/A' if expectedOverlapRatio == 0.0
                                              else overlapRatio / expectedOverlapRatio) #0
        processedResults[refTrackName].append(both) #1

        processedResults[refTrackName].append(reference) #2

        processedResults[refTrackName].append(overlapRatio) #3


        processedResults[refTrackName].append('N/A' if query == 0.0
                                              else both * 1.0 / query) #4

        processedResults[refTrackName].append('N/A' if reference == 0.0
                                              else both * 1.0 / reference) #5
    return processedResults


#Diana
def processResult(singleResult):
    '''Results is an object returned by the RawOverlapStat statistic.
    The processed results is a dictionary where the key is the name of the refe_rence track
    and therefore name of the raw in the results table.
    The value contains the list of statistics for that reference track
    and is later displayed as a row in the results table.
    '''

    regionLength = singleResult['Neither'] + singleResult['Only1'] + singleResult['Only2'] + singleResult['Both']
    processedResults = [] #0
    both = int(singleResult['Both'])
    processedResults.append(both) #0
    query = int(singleResult['Only1']) + both
    #processedResults.append(query) #1
    reference = int(singleResult['Only2']) + both
    processedResults.append(reference) #2
    overlapRatio = both * 1.0 / regionLength
    processedResults.append(overlapRatio) #3
    expectedOverlapRatio = query * 1.0 / regionLength * reference / regionLength
    processedResults.append('N/A' if expectedOverlapRatio == 0.0
                            else overlapRatio / expectedOverlapRatio)  #4
    processedResults.append('N/A' if query == 0.0
                            else both * 1.0 / query)  #5
    processedResults.append('N/A' if reference == 0.0
                            else both * 1.0 / reference)  #6
    return processedResults


def addColumnPlotToHtmlCore(htmlCore, seriesName, categories,
                            yAxisTitle, titleText, dataX, shared=False, legend=False,
                            xAxisRotation=90, height=400):
    # hicharts doesn't handle None values
    # Not sure 0 is the best solution

    #     for i in range(len(dataX)):
    #         for j in range(len(dataX[i])):
    #             if dataX[i][j] == None:
    #                 dataX[i][j] = 0
    #
    #     htmlCore.divBegin('plotDiv')
    #     import quick.webtools.restricted.visualization.visualizationPlots as vp
    #     htmlCore.line(vp.addJSlibs())
    #     htmlCore.line(vp.useThemePlot())
    #     htmlCore.line(vp.addJSlibsExport())
    #     vp.addGuideline(htmlCore)
    #     seriesType = ['column'] * len(dataX)
    #     htmlCore.line(vp.drawChart(dataX, type='column', yAxisTitle=yAxisTitle,
    #                                categories=categories, legend=legend,
    #                                xAxisRotation=xAxisRotation,
    #                                seriesType=seriesType, seriesName=seriesName,
    #                                shared=shared, titleText=titleText, height=height,
    #                                overMouseAxisX=True,
    #                                overMouseLabelX = ' + this.value.substring(0, 20) +'
    #                                )
    #                   )
    #     htmlCore.divEnd()
    from quick.webtools.restricted.visualization.visualizationGraphs import visualizationGraphs
    htmlCore.divBegin('plotDiv')
    vg = visualizationGraphs()

    vg.countFromStart()

    htmlCore.line(vg.drawColumnChart(
        dataX,
        height=height,
        yAxisTitle=yAxisTitle,
        seriesName=seriesName,
        categories=categories,
        titleText=titleText,
        xAxisRotation=xAxisRotation
        ))
    htmlCore.divEnd()

# def addPlotToHtmlCore(htmlCore, seriesName, categories,
#                             yAxisTitle, titleText, dataX, shared = False, legend=False,
#                             xAxisRotation = 0, height=500):
#
#     from quick.webtools.restricted.visualization.visualizationGraphs import visualizationGraphs
#     htmlCore.divBegin('plotDiv')
#     vg = visualizationGraphs()
#
#     htmlCore.line(vg.drawColumnChart(dataX,
#                       height=height,
#                       yAxisTitle=yAxisTitle,
#                       categories=categories,
#                       xAxisRotation=xAxisRotation,
#                       seriesName=seriesName,
#                       shared=shared, titleText=titleText,
#                       overMouseAxisX=True,
#                       overMouseLabelX = ' + this.value.substring(0, 20) +'))
#     htmlCore.divEnd()

def addPlotToHtmlCore(htmlCore, seriesName, categories,
                            yAxisTitle, titleText, dataX, shared = False, legend=False,
                            xAxisRotation = 0, height=600):

    from quick.webtools.restricted.visualization.visualizationGraphs import visualizationGraphs
    htmlCore.divBegin('plotDiv')
    vg = visualizationGraphs()

    '''
    print dataX
    print height
    print yAxisTitle
    print categories
    print xAxisRotation
    print seriesName
    print shared
    print titleText
    '''

    htmlCore.line(vg.drawColumnChart(
        dataX,
        height=height,
        yAxisTitle=yAxisTitle,
        categories=categories,
        xAxisRotation=xAxisRotation,
        seriesName=seriesName,
        shared=shared,
        titleText=titleText,
        overMouseAxisX=True,
        overMouseLabelX=' + this.value.substring(0, 10) +'))
    htmlCore.divEnd()


def getOverlapResultsForTrackVsCollection(targetTrackGenome, targetTrack, referenceTracksGSuite, analysisBins=None):
    analysisSpec = AnalysisSpec(RawOverlapStat)
    if not analysisBins:
        analysisBins = GalaxyInterface._getUserBinSource('*', '*', genome=targetTrackGenome)

    results = OrderedDict()
    for refTrack in referenceTracksGSuite.allTracks():
        tracks = [targetTrack if isinstance(targetTrack, Track) else Track(targetTrack), Track(refTrack.trackName)]
        result = doAnalysis(analysisSpec, analysisBins, tracks)
        results[refTrack.title] = result.getGlobalResult()

    return results


def getRawAndDerivedOverlapResultsForTrackVsCollection(
        targetTrackGenome, targetTrack, referenceTracksGSuite, analysisBins=None):
    analysisSpec = AnalysisSpec(RawOverlapStat)
    analysisSpecDerived = AnalysisSpec(DerivedOverlapStat)

    #userBin = UserBinSource(regSpec, binSpec, genome=targetTrackGenome)
    if not analysisBins:
        analysisBins = GalaxyInterface._getUserBinSource('*', '*', genome=targetTrackGenome)
    results = OrderedDict()
    refTrackNames = list(referenceTracksGSuite.allTrackTitles())
    refTrackCollection = [track.trackName for track in referenceTracksGSuite.allTracks()]
    refTracksDict = OrderedDict(zip(refTrackNames, refTrackCollection))
    for refTrackName, refTrack in refTracksDict.iteritems():
        tracks = [Track(targetTrack), Track(refTrack)]
        rawResults = doAnalysis(analysisSpec, analysisBins, tracks)
        results[refTrackName] = dict()
        results[refTrackName]['raw'] = rawResults
        derivedResults = doAnalysis(analysisSpecDerived, analysisBins, tracks)
        results[refTrackName]['derived'] = derivedResults
    return results

def toPercentageValue(val, maxVal=1):
    '''
    Get the percentage value of val from maxVal
    '''
    if maxVal > 0:
        if val is not None:
            return 100.0 * float(val) / maxVal


def getOverlapAndEnrichmentValuesFromResultsDict(
        rawAndDerivedOverlapResultsData, overlapTableTitle, enrichmentTableTitle, galaxyFn):
    overlapCoverageList = [
        (x['raw'].getGlobalResult()['Both'],
         x['raw'].getGlobalResult()['Both'] + x['raw'].getGlobalResult()['Only2'])
        for x in rawAndDerivedOverlapResultsData.values()]
    exonOverlapTableData = OrderedDict([(key, toPercentageValue(
        val['raw'].getGlobalResult()['Both'],
        val['raw'].getGlobalResult()['Both'] +
            val['raw'].getGlobalResult()['Only2']))
        for (key, val) in rawAndDerivedOverlapResultsData.iteritems()])
    exonOverlapTableLink = generateTableURLFromDataDict(
        galaxyFn, overlapTableTitle.replace(' ', '_'),
        ['Track', 'Overlap proportion with exons (Ensembl) in %'],
        exonOverlapTableData, plotType='columnChart')
    avgExonsOverlap = mean([float(x[0]) / x[1] for x in overlapCoverageList if (x[1] and x[1] > 0)], dtype=float64)
    minExonsOverlap = min([float(x[0]) / x[1] for x in overlapCoverageList if (x[1] and x[1] > 0)])
    maxExonsOverlap = max([float(x[0]) / x[1] for x in overlapCoverageList if (x[1] and x[1] > 0)])
    exonEnrichmentList = [x['derived'].getGlobalResult()['2in1'] for x in rawAndDerivedOverlapResultsData.values()]
    exonEnrichmentTableData = OrderedDict(
        [(key, val['derived'].getGlobalResult()['2in1']) for (key, val) in rawAndDerivedOverlapResultsData.iteritems()])
    exonEnrichmentTableLink = generateTableURLFromDataDict(
        galaxyFn, enrichmentTableTitle.replace(' ', '_'),
        ['Track', 'Enrichment in exons (Ensembl)'],
        exonEnrichmentTableData, plotType='columnChart')
    exonEnrichmentListWithoutNone = [x if x else 0 for x in exonEnrichmentList]
    avgExonsEnrichment = mean(exonEnrichmentListWithoutNone, dtype=float64) if exonEnrichmentListWithoutNone else 0.0
    minExonsEnrihment = min(exonEnrichmentList) if None not in exonEnrichmentList else 0
    maxExonsEnrichment = max(exonEnrichmentList)
    return avgExonsOverlap, exonOverlapTableLink, minExonsOverlap, maxExonsOverlap, avgExonsEnrichment, exonEnrichmentTableLink, \
        minExonsEnrihment, maxExonsEnrichment

def genereteParagraphTitle(title):
    return '<div style="color:#545454;font-weight:bold;margin:0 0 10px 0; text-transform:uppercase; font-size:1.2em; width:100%; border-bottom:1px dashed #545454" >' + str(title) + '</div>'

def generateImgLink(el, title):
    return '<a href="' + str(el) +'">' + str(title) + '</a>';

def generateTable(vals, par):
    # print vals
    # print '<br \>'

    if par == 1:
        header = ['Overview', 'Average', 'Median', 'Minimum', 'Maximum', 'Histogram', 'Details']
    elif par == 2:
        header = ['Overview', 'Average %', 'Average bps']

    htmlCore = HtmlCore()
    # htmlCore.begin()
    if par == 1:
        htmlCore.tableHeader(header, sortable=False, tableId=1, addInstruction=True)
        htmlCore.tableLine(['Unique base-pair coverage (elements)', vals[0], vals[1], vals[3], vals[4],
                            generateImgLink(vals[20], 'Show histogram'),
                            generateImgLink(vals[2], 'Show detailed plot')])
        htmlCore.tableLine(['Genome fraction coverage (bps)', vals[5], vals[6], vals[8], vals[9],
                            generateImgLink(vals[21], 'Show histogram'),
                            generateImgLink(vals[7], 'Show detailed plot')])
        htmlCore.tableLine(['Genome fraction coverage (%)', vals[10], '', vals[12], vals[13],
                            generateImgLink(vals[22], 'Show histogram'),
                            generateImgLink(vals[11], 'Show detailed plot')])
    # htmlCore.tableLine(['Average contig coverage (%)', '', '', vals[14]+'-'+vals[15], vals[16]+'-'+vals[17], '-', '-'])
    elif par == 2:
        htmlCore.tableHeader(header, sortable=True, tableId=2, addInstruction=True)
        htmlCore.tableLine(
            ['Unique to that track (not present in any of the other ' + vals[2] + ' tracks)',
             vals[0] + '%', '~' + vals[1]])
        htmlCore.tableLine(['Shared with at least half (' + vals[5] + ')', vals[3] + '%', vals[4]])
        htmlCore.tableLine(['Shared with all the other', vals[6] + '%', vals[7]])
    htmlCore.tableFooter()
    # htmlCore.end()

    return str(htmlCore)


def addHistogramVisualization(tableData, tableHeader, plotType):

    #columnCharts - column chart with multi series
    #columnChart - single column chart
    #pieChart - single pie chart
    from quick.webtools.restricted.visualization.visualizationGraphs import visualizationGraphs, dataTransformer

    vg = visualizationGraphs(height=300)
    #just for separate pages
    vg.countFromStart()

    res = ''
    # DebugUtil.insertBreakPoint()
    if plotType != None:
        dT = dataTransformer(tableData)
        if plotType == 'columnCharts':
            tableHeader = [str(x) for x in tableHeader if x not in ['Track']]
            seriesName, categories, data = dT.changeDictIntoListsByNumber(len(tableData))
            res = vg.drawColumnCharts(data, categories=[tableHeader], seriesName=categories)
        elif plotType == 'columnChart':
            seriesName, categories, data = dT.changeDictIntoList()

            from proto.RSetup import r, robjects
            # count histogram
            rCode = 'ourHist <- function(vec) {hist(vec, plot=FALSE)}'
            dd=robjects.FloatVector(data)
            simpleHist = r(rCode)(dd)
            # simpleHistDict = asDict(simpleHist)

            #labels, values = zip(*Counter(data).items())

            try:
                counts = list(simpleHist.rx2('counts'))
            except:
                counts = [simpleHist.rx2('counts')]

            res = vg.drawColumnChart(counts, categories=list(simpleHist.rx2('breaks')), titleText=tableHeader[1], showInLegend=False, histogram=True, xAxisRotation=90)
        elif plotType =='pieChart':
            seriesName, categories, data = dT.changeDictIntoList()
            res = vg.drawPieChart(data, seriesName=categories, titleText=tableHeader[1],
                                  addOptions='width: 50%; margin: 0 auto')

    return res


# def asDict(vector):
#     """Convert an RPy2 ListVector to a Python dict"""
#     from rpy2 import robjects
#     import types
#     result = {}
#     for i, name in enumerate(vector.names):
#         if isinstance(vector[i], robjects.ListVector):
#             result[name] = as_dict(vector[i])
#         elif type(vector[i]) != types.BooleanType and len(vector[i]) == 1:
#             result[name] = vector[i][0]
#         else:
#             result[name] = vector[i]
#     return result


def generateHistogram(tableUniqueName, tableHeader, tableData, plotType=None):
    return str(addHistogramVisualization(tableData, tableHeader, plotType=plotType))


def generateHistogramURLFromDataDict(galaxyFn, tableUniqueName, tableHeader, tableData, plotType=None, fileExt='html'):
    helpHtmlCore = HtmlCore()
    helpHtmlCore.begin()
    helpHtmlCore.line(addHistogramVisualization(tableData, tableHeader, plotType=plotType))
    helpHtmlCore.end()

    tableFile = GalaxyRunSpecificFile(['Table', tableUniqueName + '.' + fileExt] , galaxyFn)
    with tableFile.getFile() as f:
        f.write(str(helpHtmlCore))
    return tableFile.getURL()


    #helpHtmlCore.tableFromDictionary(tableDataFormatted, tableHeader, tableId=tableUniqueName, sortable=True)


def generatePilotPageOneParagraphs(gSuite, galaxyFn, regSpec='*', binSpec='*', username=''):
#     userBin = GalaxyInterface._getUserBinSource("chr1:1-30m", "1m", genome=gSuite.genome)
    userBin = GalaxyInterface._getUserBinSource(regSpec, binSpec, genome=gSuite.genome)
    gSuiteOverview = GSuiteOverview(gSuite)
    gSOData = gSuiteOverview.getGSuiteOverviewData(analysisBins=userBin)
    paragraphs = []
#     genomeLen = GenomeInfo.getGenomeLen(gSuite.genome)


    tableData1 = gSOData.getElementCountDataDict()
    tableData2 = gSOData.getCoverageDataDict()
    tableData3 = gSOData.getPropCoverageDataDict()
#     table1 = generateHistogram('elementCount', ['Track', 'Histogram for unique base-pair coverage (elements)'], tableData1, plotType='columnChart')
#     table2 = generateHistogram('coverage', ['Track', 'Histogram for genome fraction coverage (bps)'], tableData2, plotType='columnChart')
#     table3 = generateHistogram('propCoverage', ['Track', 'Histogram for genome fraction coverage (%)'], tableData3, plotType='columnChart')

    table1LinkHist = generateHistogramURLFromDataDict(
        galaxyFn, 'histElementCount',
        ['Track', 'Histogram for unique base-pair coverage (elements)'],
        tableData1, plotType='columnChart')
    table2LinkHist = generateHistogramURLFromDataDict(
        galaxyFn, 'histCoverage',
        ['Track', 'Histogram for genome fraction coverage (bps)'],
        tableData2, plotType='columnChart')
    table3LinkHist = generateHistogramURLFromDataDict(
        galaxyFn, 'histPropCoverage',
        ['Track', 'Histogram for genome fraction coverage (%)'],
        tableData3, plotType='columnChart')



    table1Link = generateTableURLFromDataDict(
        galaxyFn, 'elementCount', ['Track', 'Element count'],
        tableData1, plotType='columnChart')
    table2Link = generateTableURLFromDataDict(
        galaxyFn, 'coverage', ['Track', 'Coverage in bps'],
        tableData2, plotType='columnChart')
    table3Link = generateTableURLFromDataDict(
        galaxyFn, 'propCoverage', ['Track', 'Proportional coverage'],
        tableData3, plotType='columnChart')


    tableData, regionNames = gSOData.getPropCoveragePerRegionDataDict()
    table4Link = generateTableURLFromDataDict(
        galaxyFn, 'propCoveragePerChr', ['Track'] + regionNames,
        tableData, plotType='columnCharts')
#     table4 = generateHistogram('propCoveragePerChr', ['Track', 'Histogram'], tableData, plotType='columnChart')

    tableData, regionNames = gSOData.getElementCountPerRegionDataDict()
    table5Link = generateTableURLFromDataDict(
        galaxyFn, 'elementCountPerChr', ['Track'] + regionNames,
        tableData, plotType='columnCharts')
#     table5 = generateHistogram('elementCountPerChr', ['Track', 'Histogram'], tableData, plotType='columnChart')

    vals = (gSOData.avgElementCount,
            gSOData.medianElementCount,
            table1Link,
            gSOData.minElementCount,
            gSOData.maxElementCount,
            gSOData.avgCoverage,
            gSOData.medianCoverage,
            table2Link,
            gSOData.minBpsCoverage,
            gSOData.maxBpsCoverage,
            toPercentageValue(gSOData.avgPropCoverage, 1),
            table3Link,
            toPercentageValue(gSOData.minPropCoverage, 1),
            toPercentageValue(gSOData.maxPropCoverage, 1),
            gSOData.minAvgPropCoveragePerRegion()[0],
            toPercentageValue(gSOData.minAvgPropCoveragePerRegion()[1], 1),
            gSOData.maxAvgPropCoveragePerRegion()[0],
            toPercentageValue(gSOData.maxAvgPropCoveragePerRegion()[1], 1),
            table4Link,
            table5Link,
            table1LinkHist,
            table2LinkHist,
            table3LinkHist
            )
    vals = tuple([strWithNatLangFormatting(x) for x in vals])

#     paragraphOne = '''
#         The tracks in the collection contain on average %s elements (median: %s elements),
#         <a href="%s">
#         ranging from %s to %s between the tracks.
#         </a>
#         The tracks cover on average %s bps (median: %s bps),
#         <a href="%s">
#         ranging from %s to %s bps between datasets.
#         </a>
#         This amounts to on average covering %s%% of the genome,
#         <a href="%s">
#         ranging from %s%% to %s%% between tracks.
#         </a>
#         The average coverage (across tracks) is lowest in %s (%s%%) and highest in %s (%s%%).
#         Detailed numbers per track can be inspected in a
#         <a href="%s">
#         table of coverage proportion per track per chromosome
#         </a>,
#         and in a
#         <a href="%s">
#         table of element count per track per chromosome
#         </a>.
#     ''' % vals
#     paragraphs.append(paragraphOne)


    paragraphs.append(generateTable(vals, 1))

#     paragraphs.append(genereteParagraphTitle('Unique base-pair coverage'))
#     par='''
#         The tracks in the collection contain on
#         average %s
#         elements (median: %s elements),
#         <a href="%s">
#         ranging from %s to %s between the tracks.
#         </a>
#         ''' % vals[0:5]
#     paragraphs.append(par)
#     paragraphs.append(table1)

#     paragraphs.append(genereteParagraphTitle('Genome fraction coverage'))
#     par='''
#         The tracks cover on average %s bps (median: %s bps),
#         <a href="%s">
#         ranging from %s to %s bps between datasets.
#         </a>
#         ''' % vals[5:10]
#     paragraphs.append(par)
#     paragraphs.append(table2)

#     paragraphs.append(genereteParagraphTitle(''))
#     par='''
#         This amounts to on average covering %s%% of the genome,
#         <a href="%s">
#         ranging from %s%% to %s%% between tracks.
#         </a>
#         ''' % vals[10:14]
#     paragraphs.append(par)
#     paragraphs.append(table3)

    paragraphs.append(genereteParagraphTitle('Average contig coverage'))
    par='''
        The average coverage (across tracks) is lowest in %s (%s%%) and highest in %s (%s%%).
        ''' % vals[14:18]
    paragraphs.append(par)

    par='''
        Detailed numbers per track can be inspected in a
        <a href="%s">
        table of coverage proportion per track per chromosome
        </a>,
        and in a
        <a href="%s">
        table of element count per track per chromosome
        </a>.
        ''' % vals[18:20]
    paragraphs.append(par)

    #####################################

    #paragraph 2

    multitrackCoverageDepthAnalysis = AnalysisSpec(MultitrackCoverageDepthStat)
    trackNameList = [Track(track.trackName) for track in gSuite.allTracks()]
    covDepthRes = doAnalysis(multitrackCoverageDepthAnalysis, userBin, trackNameList)
    globalResult = covDepthRes.getGlobalResult()
    if globalResult and 'Result' in globalResult:
        bpsPerDepthLevel = globalResult['Result']
        unionBps = sum(bpsPerDepthLevel[1:])
        sumBps = sum([x*i for i,x in enumerate(bpsPerDepthLevel)])

        vals = (
                gSuite.numTracks(),
                sumBps,
                unionBps
                )
        vals = tuple([strWithNatLangFormatting(x) for x in vals])
        paragraphs.append('''In total, the regions of the %s tracks encompass %s bps (plain sum of covered bps per track),
            representing %s unique bps of the genome (coverage of the union of all tracks).''' % vals)

    #########################################

    #paragraph 3

    tableData = gSOData.getAvgSegmentLengthDataDict()
    table6Link = generateTableURLFromDataDict(
        galaxyFn, 'avgSegLen', ['Track', 'Average segment length'],
        tableData, plotType='columnChart')

    vals = (gSOData.avgAvgSegmentLen,
            gSOData.medianAvgSegmentLen,
            table6Link,
            gSOData.minAvgSegmentLen,
            gSOData.maxAvgSegmentLen
            )
    vals = tuple([strWithNatLangFormatting(x) for x in vals])
    paragraphs.append('''
        The average segment length of the tracks is on average %s bps (median: %s bps),
        ranging from
        <a href="%s">
        average length of %s bps to %s bps between tracks
        </a>.
    ''' % vals)

    ###############################

    # Exons, introns overlap

    if gSuite.genome == 'hg19':
        exonsRawAndDerivedOverlap, intronsRawAndDerivedOverlap = \
            getExonIntronRawAndDerivedOvelapData(gSuite, analysisBins=userBin)
        #not very readable, but hey...
        avgExonsOverlap, exonOverlapTableLink, minExonsOverlap, maxExonsOverlap, \
        avgExonsEnrichment, exonEnrichmentTableLink, minExonsEnrihment, maxExonsEnrichment \
            = getOverlapAndEnrichmentValuesFromResultsDict(
                  exonsRawAndDerivedOverlap, 'Overlap with exons (Ensembl)',
                  'Enrichment in exons (Ensembl)', galaxyFn)

        overlapTableData = OrderedDict()
        for trackName in exonsRawAndDerivedOverlap:
            exonsOverlap = exonsRawAndDerivedOverlap[trackName]['raw'].getGlobalResult()['Both']
            intronsOverlap = intronsRawAndDerivedOverlap[trackName]['raw'].getGlobalResult()['Both']
            #intergenic = coverage - (exonsOverlap + intronOverlap) = Only2(from exon overlap) - intronOverlap
            intergenicOverlap = exonsRawAndDerivedOverlap[trackName]['raw'].getGlobalResult()['Only2'] - intronsOverlap
            overlapTableData[trackName] = [exonsOverlap, intronsOverlap, intergenicOverlap]
        overlapTableLink = generateTableURLFromDataDict(
            galaxyFn, 'Overlap',
            ['Track',
             'Overlap with exons (Ensembl)',
             'Overlap with introns (Ensembl)',
             'Overlap with intergenic regions (Ensembl)'
             ],
            overlapTableData,
            plotType='columnCharts')

        vals = (toPercentageValue(avgExonsOverlap),
                exonOverlapTableLink,
                toPercentageValue(minExonsOverlap),
                toPercentageValue(maxExonsOverlap),
                avgExonsEnrichment,
                exonEnrichmentTableLink,
                minExonsEnrihment,
                maxExonsEnrichment,
                overlapTableLink
                )
        vals = tuple([strWithNatLangFormatting(x) for x in vals])

        paragraphs.append('''
            On average, %s%% of the tracks fall within exonic regions, ranging from
            <a href="%s">
            %s%% to %s%% between tracks
            </a>.
            This corresponds to an enrichment factor of %s, ranging from
            <a href="%s">
            %s to %s between tracks
            </a>.
            Further details can be inspected in a
            <a href="%s">
            table showing distribution of each track between exons, introns and intergenic regions
            </a>.
        ''' % vals)

    if gSuite.genome == 'hg19':
        paragraph1Text = '''On average, %s%% of the tracks fall within repeat regions,
        ranging from
        <a href="%s">
        %s%% to %s%% between tracks
        </a>.
        This corresponds to an enrichment factor of %s,
        ranging from
        <a href="%s">
        %s to %s between tracks
        </a>.
        Further details can be inspected in
            <a href="%s">
            a table
            showing the proportion of each track covered by different classes of repeating elements
            </a>
            .

        '''

        commonRepeatsOverlapResults = \
            getCommonRepeatsRawAndDerivedOverlapData(gSuite, analysisBins=userBin)
        avgRepeatsOverlap, repeatOverlapTableLink, minRepeatsOverlap, maxRepeatsOverlap, \
        avgRepeatsEnrichment, repeatEnrichmentTableLink, minRepeatsEnrihment, maxRepeatsEnrichment\
        = getOverlapAndEnrichmentValuesFromResultsDict(
            commonRepeatsOverlapResults, 'Overlap with repeats', 'Enrichment in repeats', galaxyFn)

        allRepeatsOverlapResultsDict = getAllRepeatsProportionOverlapData(
            gSuite, analysisBins=userBin, username=username)

        allRepeatsOverlapTableLink = generateTableURLFromDataDict(
            galaxyFn, 'repeatsOverlapProportion', ['Repeats track'] + gSuite.allTrackTitles(),
            allRepeatsOverlapResultsDict, plotType='columnCharts')

        vals = (
                toPercentageValue(avgRepeatsOverlap),
                repeatOverlapTableLink,
                toPercentageValue(minRepeatsOverlap),
                toPercentageValue(maxRepeatsOverlap),
                avgRepeatsEnrichment,
                repeatEnrichmentTableLink,
                minRepeatsEnrihment,
                maxRepeatsEnrichment,
                allRepeatsOverlapTableLink
                )

        vals = tuple([strWithNatLangFormatting(x) for x in vals])


        repeatsParagraph = paragraph1Text % vals
        paragraphs.append(repeatsParagraph)

    paragraphs.append(str(getGSuiteOverviewHtmlCore(gSOData, expandable=True)))
    return paragraphs


def addVisualization(tableData, tableHeader, plotType, tableName):

    #columnCharts - column chart with multi series
    #columnChart - single column chart
    #pieChart - single pie chart

    from quick.webtools.restricted.visualization.visualizationGraphs import visualizationGraphs, dataTransformer

    vg = visualizationGraphs()
    vg.countFromStart()

    res=''

    if plotType!=None:
        dT = dataTransformer(tableData)
        if plotType == 'columnCharts':
            tableHeader = [str(x) for x in tableHeader if x not in ['Track']]
            seriesName, categories, data = dT.changeDictIntoListsByNumber(len(tableData))
            res = vg.drawColumnCharts(data,
                                      categories=[tableHeader],
                                      seriesName=categories,
                                      xAxisRotation=90,
                                      height=400)
        elif plotType == 'columnChart':
            seriesName, categories, data = dT.changeDictIntoList()


            res = vg.drawColumnChart(data,
                                     categories=categories,
                                     titleText=tableHeader[1],
                                     xAxisRotation=90,
                                     height=500,
                                     showInLegend=False,
                                     addTable=True,
                                     sortableAccordingToTable=True,
                                     tableName=tableName)
        elif plotType =='pieChart':
            seriesName, categories, data = dT.changeDictIntoList()
            res = vg.drawPieChart(data,
                                  seriesName=categories,
                                  titleText=tableHeader[1],
                                  addOptions='width: 50%; margin: 0 auto',
                                  height=400
                                  )

    return res


def generateTableURLFromDataDict(galaxyFn, tableUniqueName, tableHeader, tableData, plotType=None, fileExt='html'):
    '''
    Table data is a dict with row name as key. The value is either a list of values corresponding
    to the table header or a single value.
    '''
    #prettify data
    tableDataFormatted = OrderedDict()
    for key, val in tableData.iteritems():
        if isinstance(val, list):
            tableDataFormatted[key] = [strWithNatLangFormatting(x) for x in val]
        else:
            tableDataFormatted[key] = strWithNatLangFormatting(val)

    helpHtmlCore = HtmlCore()
    helpHtmlCore.begin()
    helpHtmlCore.tableFromDictionary(tableDataFormatted, tableHeader, tableId=tableUniqueName, sortable=True)

    helpHtmlCore.line(addVisualization(tableData, tableHeader, plotType=plotType, tableName=tableUniqueName))
    helpHtmlCore.end()
    tableFile = GalaxyRunSpecificFile(['Table', tableUniqueName + '.' + fileExt], galaxyFn)
    with tableFile.getFile() as f:
        f.write(str(helpHtmlCore))
    return tableFile.getURL()


def generateTableURL(galaxyFn, tableUniqueName, tableData, fileExt='html'):
    helpHtmlCore = HtmlCore()
    helpHtmlCore.begin()
    helpHtmlCore.line(tableData)
    helpHtmlCore.end()
    tableFile = GalaxyRunSpecificFile(['Table', tableUniqueName + '.' + fileExt], galaxyFn)
    with tableFile.getFile() as f:
        f.write(str(helpHtmlCore))
    return tableFile.getURL()


def generatePlotURLFromData(galaxyFn, rowNames, colNames, data, yAxisTitle, title, plotUniqueName, fileExt='html'):
    htmlCore = HtmlCore()
    htmlCore.begin()

    addColumnPlotToHtmlCore(htmlCore,
                            rowNames,
                            colNames,
                            yAxisTitle,
                            title,
                            data,
                            xAxisRotation = 90,
                            height = 500)
    htmlCore.end()
    plotFile = GalaxyRunSpecificFile(['Plot', plotUniqueName + "." + fileExt], galaxyFn)
    with plotFile.getFile() as f:
        f.write(str(htmlCore))
    return plotFile.getURL()


def getGSuiteOverviewHtmlCore(overviewData, expandable=False, visibleRows=6):
    htmlCore = HtmlCore()

    htmlCore.divBegin(divId='tracks')

    htmlCore.header('Track overview table')

    headerRowStats = ['Track', 'Base-pair coverage', 'Segment count', 'Segment length average',
                      'Segment length min', 'Segment length max', 'Segment length median', 'Segment distance average',
                      'Segment distance min', 'Segment distance max', 'Segment distance median']

#     htmlCore.tableHeader(headerRowStats, sortable=True)
    plotData = []
    tableData = OrderedDict()
    for trackOverviewData in overviewData.trackOverviewList:
        row = _buildTableRow(trackOverviewData)
        tableData[row[0]] = [strWithNatLangFormatting(x) for x in row[1:]]
#         htmlCore.tableLine([strWithNatLangFormatting(x) for x in row])
        plotData.append(row[1:])
#     htmlCore.tableFooter()
    if expandable and len(tableData) > visibleRows:
        htmlCore.tableFromDictionary(tableData, headerRowStats, tableId='gsOverviewTable',
                                     expandable=expandable, visibleRows=visibleRows)
    else:
        htmlCore.tableFromDictionary(tableData, headerRowStats, tableId='gsOverviewTable',
                                     expandable=False)

    htmlCore.divEnd()
    htmlCore.line("")
    htmlCore.line("")
    htmlCore.divBegin(divId='gsuite')
    htmlCore.header('GSuite overview table')
    headerRow = ['Base-pair coverage average', 'Segment count average',
                 'Base-pair coverage min', 'Base-pair coverage max']
    htmlCore.tableHeader(headerRow)
    htmlCore.tableLine([overviewData.avgCoverage, overviewData.avgElementCount,
                        overviewData.minBpsCoverage, overviewData.maxBpsCoverage])
    htmlCore.tableFooter()
    htmlCore.divEnd()

    trackNames = [x.trackName.replace('\'', '').replace('"','') for x in overviewData.trackOverviewList]

    plotData = normalizeMatrixData(plotData)
    addColumnPlotToHtmlCore(htmlCore,
                            trackNames,
                            headerRowStats[1:],
                            'Track stat',
                            'GSuite tracks overview plot',
                            plotData,
                            xAxisRotation = 90,
                            height = 400
                    )
    return htmlCore


def getExonIntronRawAndDerivedOvelapData(gSuite, analysisBins=None):
    '''
    Get raw and derived overlap data for tracks in gSuite against the exons and introns tracks from hg19 genome
    '''
    assert gSuite.genome == 'hg19', 'Only hg19 is currently supported'

    if not analysisBins:
        analysisBins = GalaxyInterface._getUserBinSource('*', '*', genome=gSuite.genome)

    exonsEnsemblTrack = ['Genes and gene subsets', 'Exons', 'Ensembl exons']
    exonsOverlap = getRawAndDerivedOverlapResultsForTrackVsCollection(
        'hg19', exonsEnsemblTrack, gSuite, analysisBins=analysisBins)

    intronsEnsemblTrack = ['Genes and gene subsets', 'Introns', 'Ensembl introns']
    intronsOverlap = getRawAndDerivedOverlapResultsForTrackVsCollection(
        'hg19', intronsEnsemblTrack, gSuite, analysisBins=analysisBins)

    return exonsOverlap, intronsOverlap


def getCommonRepeatsRawAndDerivedOverlapData(gSuite, analysisBins=None):
    '''
        Get raw and derived overlap results with the common Repeats track for hg19.
    '''
    assert gSuite.genome == 'hg19', 'Only hg19 is currently supported'

    if not analysisBins:
        analysisBins = GalaxyInterface._getUserBinSource('*', '*', genome=gSuite.genome)

    repeatsCommonTrack = ['Sequence', 'Repeating elements']
    repeatsCommonOverlap = getRawAndDerivedOverlapResultsForTrackVsCollection(
        'hg19', repeatsCommonTrack, gSuite, analysisBins)

    return repeatsCommonOverlap


def getAllRepeatsProportionOverlapData(gSuite, analysisBins=None, username=''):
    '''
        Get propotional overlap data against a precompiled Repeats track collection for hg19.
    '''
    assert gSuite.genome == 'hg19', 'Only hg19 is currently supported'
    if not analysisBins:
        analysisBins = GalaxyInterface._getUserBinSource('*', '*', genome=gSuite.genome)

    subtracks = GalaxyInterface.getSubTrackNames(
        gSuite.genome, ['Sequence', 'Repeating elements'],
        deep=False, username=username)[0]
    subtrackList = []

    for subtrack in subtracks:
        if subtrack and subtrack[1] != '-- All subtypes --':
            subtrackList.append(['Sequence', 'Repeating elements'] + [subtrack[1]])

    analysisSpec = AnalysisSpec(DerivedOverlapStat)
    resultsDict = defaultdict(list)
    for subtrack in subtrackList:
        for track in gSuite.allTracks():
            singleResult = doAnalysis(analysisSpec, analysisBins, [Track(subtrack), Track(track.trackName)])
            resultsDict[subtrack[-1]].append(singleResult.getGlobalResult()['1inside2'])

    return resultsDict


def _buildTableRow(trackOverviewData):
    row = []
    row.append(trackOverviewData.trackName)
    row.append(trackOverviewData.bpsCoverage)
    row.append(trackOverviewData.elementCount)
    row.append(trackOverviewData.avgSegmentLen)
    row.append(trackOverviewData.minSegmentLen)
    row.append(trackOverviewData.maxSegmentLen)
    row.append(trackOverviewData.medianSegmentLen)
    row.append(trackOverviewData.avgDistLen)
    row.append(trackOverviewData.minDistLen)
    row.append(trackOverviewData.maxDistLen)
    row.append(trackOverviewData.medianDistLen)
    return row


def toBpsPrefixedValue(rawVal):
    suffix = 'bps'
    if rawVal > 1000:
        rawVal = float(rawVal) / 1000
        suffix = 'Kbps'
    if rawVal > 1000:
        rawVal = rawVal / 1000
        suffix = 'Mbps'
    if rawVal > 1000:
        rawVal = rawVal / 1000
        suffix = 'Gbps'
    return strWithNatLangFormatting(rawVal) + ' ' + suffix


def generatePilotPageTwoParagraphs(gSuite, galaxyFn, regSpec='*', binSpec='*'):

#     from datetime import datetime

#     bpsDepthAnalysis = AnalysisSpec(ThreeWayFocusedTrackCoveragesAtDepthsRawStat)

    bpsPerDepthLevelAnalysis = AnalysisSpec(MultiTrackBpsCoveragePerDepthLevelStat)

#     bpsDepthAnalysis = AnalysisSpec(MultitrackFocusedCoverageDepthStat)
#
    paragraphs = []

    trackTitles = gSuite.allTrackTitles()

    userBin = GalaxyInterface._getUserBinSource(regSpec, binSpec, genome=gSuite.genome)

    bpsPerDepthLevel = doAnalysis(bpsPerDepthLevelAnalysis, userBin,
                                  [Track(track.trackName) for track in gSuite.allTracks()]).getGlobalResult()
    bpsSum = sum(bpsPerDepthLevel.values())

#     startTime = datetime.now()
#     bpsResultDict = doAnalysis(bpsDepthAnalysis, userBin, [Track(track.trackName) for track in gSuite.allTracks()]).getGlobalResult()
#     endTime = datetime.now()
#     print 'Raw depth results time: ', (endTime - startTime)
#     print 'RawResult: ', bpsResultDict


#     bpsResultDictFiltered = OrderedDict()
#
#     for key, val in bpsResultDict.iteritems():
#         if key != 'BinSize' and key[0] == True:
#             trackTitle = trackTitles[key[1]]
#             if trackTitle not in bpsResultDictFiltered:
#                 bpsResultDictFiltered[trackTitle] = OrderedDict()
#             bpsResultDictFiltered[trackTitle][key[2]] = val
#

    from math import ceil

#     avgUniqueBpsProp = mean([propResultDictFiltered[key][0] for key in propResultDictFiltered])
    avgUniqueBpsProp = 0.0 if bpsSum == 0 else float(bpsPerDepthLevel[0])/bpsSum
#     avgUniqueBps = mean([bpsResultDictFiltered[key][0] for key in bpsResultDictFiltered])
    avgUniqueBps = bpsPerDepthLevel[0]/gSuite.numTracks()
#     avgSharedWithHalfProp = mean([propResultDictFiltered[key][gSuite.numTracks()/2] for key in propResultDictFiltered])
    halfIndex = int(ceil(gSuite.numTracks() / 2.0 + 0.5)-1)
    atLeastHalfSum = sum([bpsPerDepthLevel[x] for x in bpsPerDepthLevel if x >= halfIndex])
    atLeastHalfSumBps = sum([bpsPerDepthLevel[x]/gSuite.numTracks() for x in bpsPerDepthLevel if x >= halfIndex])
    avgSharedWithHalfProp = 0.0 if bpsSum == 0 else float(atLeastHalfSum)/bpsSum
#     avgSharedWithHalfBps = mean([bpsResultDictFiltered[key][gSuite.numTracks()/2] for key in bpsResultDictFiltered])
    avgSharedWithHalfBps = atLeastHalfSumBps
#     avgSharedWithAllProp = mean([propResultDictFiltered[key][gSuite.numTracks()-1] for key in propResultDictFiltered])
    avgSharedWithAllProp = 0.0 if bpsSum == 0 else float(bpsPerDepthLevel[gSuite.numTracks()-1])/bpsSum
#     avgSharedWithAllBps = mean([bpsResultDictFiltered[key][gSuite.numTracks()-1] for key in bpsResultDictFiltered])
    avgSharedWithAllBps = bpsPerDepthLevel[gSuite.numTracks()-1]/gSuite.numTracks()

#     tableData = OrderedDict()
#     for key, val in propResultDictFiltered.iteritems():
#         tableData[key] = [strWithNatLangFormatting(toPercentageValue(val[i])) for i in range(gSuite.numTracks())]
#     table1Link = generateTableURLFromDataDict(galaxyFn, 'avgTrackVsOtherTable', ['Track'] + colNames, tableData)

    table1Data = OrderedDict()
    for depthLevel, bpsCount in bpsPerDepthLevel.iteritems():
        table1Data['Depth %i' % (depthLevel+1)] = strWithNatLangFormatting((float(bpsCount)/bpsSum * 100.0)) + ' %'

    table1Link = generateTableURLFromDataDict(
        galaxyFn, 'avgCoverageDepth', ['Coverage depth', 'Average proportion of bps(%)'],
        table1Data, plotType='pieChart')

    plot1Link = ''
    if gSuite.numTracks() < 31:
        colNames = ['Depth ' + str(x) for x in range(gSuite.numTracks())]
        propDepthAnalysis = AnalysisSpec(ThreeWayFocusedTrackProportionCoveragesAtDepthsRawStat)
    #     startTime = datetime.now()
        propResultDict = doAnalysis(
            propDepthAnalysis, userBin,
            [Track(track.trackName) for track in gSuite.allTracks()]).getGlobalResult()
    #     endTime = datetime.now()
    #     print 'Prop depth results time: ', (endTime - startTime)
    #     print 'PropResult: ', propResultDict
        propResultDictFiltered = OrderedDict()

        for key, val in propResultDict.iteritems():
            if key != 'BinSize' and key[0] == True:
                trackTitle = trackTitles[key[1]]
                if trackTitle not in propResultDictFiltered:
                    propResultDictFiltered[trackTitle] = OrderedDict()
                propResultDictFiltered[trackTitle][key[2]] = val
        plot1Data = []
        for i in range(len(trackTitles)):
            plot1Data.append([])
            for depth in range(gSuite.numTracks()):
                plot1Data[i].append(toPercentageValue(propResultDictFiltered[trackTitles[i]][depth]))

        plot1Link = generatePlotURLFromData(galaxyFn,
                                            trackTitles,
                                            colNames,
                                            plot1Data,
                                            'Tracks',
                                            'Individual track coverage shared with a varying number of other tracks (%)',
                                            'avgTrackVsOtherPlot')

    tableData = OrderedDict()

    for i, bpsDepth in bpsPerDepthLevel.iteritems():
        tableData[i+1] = toBpsPrefixedValue(bpsDepth/gSuite.numTracks())

    table2Link = generateTableURLFromDataDict(
        galaxyFn, 'avgBpsPerDepth',
        ['Coverage depth', 'Average coverage for depth for a track (bps)'],
        tableData, plotType='columnChart')

    vals = (
            toPercentageValue(avgUniqueBpsProp),
            toBpsPrefixedValue(avgUniqueBps),
            gSuite.numTracks() - 1,
            toPercentageValue(avgSharedWithHalfProp),
            toBpsPrefixedValue(avgSharedWithHalfBps),
            gSuite.numTracks()/2,
            toPercentageValue(avgSharedWithAllProp),
            toBpsPrefixedValue(avgSharedWithAllBps),
            table1Link)

    if gSuite.numTracks() < 31:
        vals += tuple([plot1Link])

    vals += tuple([table2Link])

    if gSuite.numTracks() > 3:
        vals += tuple([gSuite.numTracks()])

    vals = tuple([strWithNatLangFormatting(x) for x in vals])

    paragraphContent = '''
        On average, around %s%%  (~%s) of the base pairs of a single track are unique to that track
        (not present in any of the other %s tracks). Around %s%% (%s) are shared with at least half (%s)
        of the other tracks, while around %s%% (%s) is shared with all the other tracks.
        Details are available in the form of
        <a href="%s">
        a table showing the percentage of an average track shared
        with a varying depths (numbers of other tracks)
        </a>
        '''
    if gSuite.numTracks() < 31:
        paragraphContent += '''
        , as well as
        <a href="%s">
        plots showing the same for an individual track
        </a>'''
    paragraphContent +='''.
        There is also available
        <a href="%s">a table showing how many base pairs are covered by 1, 2, 3'''

    if gSuite.numTracks() > 3:
        paragraphContent += ''' and up to %s'''

    paragraphContent += ''' of
        the tracks
        </a>.
        '''
    paragraph = paragraphContent % vals
    paragraphs.append(generateTable(vals, 2))
    paragraphs.append(paragraph)

    return paragraphs


def generatePilotPageThreeParagraphs(gSuite, galaxyFn, regSpec='*', binSpec='*'):
    numTracks = gSuite.numTracks()
    userBin = GalaxyInterface._getUserBinSource(regSpec, binSpec, genome=gSuite.genome)
    #Q1,3
    analysisSpecQ13 = AnalysisSpec(MultitrackSummarizedInteractionStat)
    analysisSpecQ13.addParameter('pairwiseStatistic', 'PropOfReferenceTrackInsideTargetTrackStat')
    analysisSpecQ13.addParameter('summaryFunc', 'avg')
    analysisSpecQ13.addParameter('multitrackSummaryFunc', 'raw')
    analysisSpecQ13.addParameter('reverse', 'No')

    resultsQ13 = doAnalysis(
        analysisSpecQ13, userBin,
        [Track(x.trackName) for x in gSuite.allTracks() ]).getGlobalResult()['Result']
    resultsQ13 = [x for x in resultsQ13 if x]
    if resultsQ13:
        maxCoverageDegreeIndex = resultsQ13.index(max(resultsQ13))
        maxCoverageDegreeTrackTitle = gSuite.allTrackTitles()[maxCoverageDegreeIndex]
    else:
        maxCoverageDegreeTrackTitle = 'N/A'

    tableData = OrderedDict([(gSuite.allTrackTitles()[i], strWithNatLangFormatting(val))
                             for i, val in enumerate(resultsQ13)])
    table1Link = generateTableURLFromDataDict(
        galaxyFn, 'avgCoverageDegree',
        ['Track', 'Average coverage degree of other tracks'],
        tableData, plotType='columnChart')

    #Q2,3
    analysisSpecQ23 = AnalysisSpec(MultitrackSummarizedInteractionStat)
    analysisSpecQ23.addParameter('pairwiseStatistic', 'PropOfReferenceTrackInsideUnionStat')
    analysisSpecQ23.addParameter('summaryFunc', 'avg')
    analysisSpecQ23.addParameter('multitrackSummaryFunc', 'raw')
    analysisSpecQ23.addParameter('reverse', 'No')

    resultsQ23 = doAnalysis(
        analysisSpecQ23, userBin,
        [Track(x.trackName) for x in gSuite.allTracks() ]).getGlobalResult()['Result']
    resultsQ23 = [x for x in resultsQ23 if x]

    if resultsQ23:
        minUniqueCoverageIndex = resultsQ23.index(min(resultsQ23))
        minUniqueCoverageTrackTitle = gSuite.allTrackTitles()[minUniqueCoverageIndex]
    else:
        minUniqueCoverageTrackTitle = 'N/A'

    tableData = OrderedDict([(gSuite.allTrackTitles()[i], strWithNatLangFormatting(val))
                             for i, val in enumerate(resultsQ23)])
    table2Link =   generateTableURLFromDataDict(
        galaxyFn, 'avgUniqueCoverage',
        ['Track', 'Average unique coverage of track'],
        tableData, plotType='columnChart')

    #Q4,3
    analysisSpecQ43 = AnalysisSpec(MultitrackSummarizedInteractionStat)
    analysisSpecQ43.addParameter('pairwiseStatistic', 'RatioOfIntersectionToGeometricMeanStat')
    analysisSpecQ43.addParameter('summaryFunc', 'avg')
    analysisSpecQ43.addParameter('multitrackSummaryFunc', 'raw')
    analysisSpecQ43.addParameter('reverse', 'No')

    resultsQ43 = doAnalysis(
        analysisSpecQ43, userBin,
        [Track(x.trackName) for x in gSuite.allTracks() ]).getGlobalResult()['Result']
    resultsQ43 = [x for x in resultsQ43 if x]

    if resultsQ43:
        maxPreferenceIndex = resultsQ43.index(max(resultsQ43))
        maxPreferenceTrackTitle = gSuite.allTrackTitles()[maxPreferenceIndex]
    else:
        maxPreferenceTrackTitle = 'N/A'

    tableData = OrderedDict([(gSuite.allTrackTitles()[i], strWithNatLangFormatting(val))
                             for i, val in enumerate(resultsQ43)])
    table3Link =   generateTableURLFromDataDict(
        galaxyFn, 'mostTypical',
        ['Track', 'Average preference for locations shared with other tracks'],
        tableData, plotType='columnChart')

    vals = (
            numTracks,
            maxCoverageDegreeTrackTitle,
            table1Link,
            minUniqueCoverageTrackTitle,
            table2Link,
            maxPreferenceTrackTitle,
            table3Link
            )

    paragraph = '''
        Out of the %s tracks, the track %s is the one that shows the
        <a href="%s">
        highest degree of covering locations covered by the remaining tracks
        </a>
        (being most like a superset of all other experiments).
        The track %s is the one covering the
        <a href="%s">
        least locations unique to this dataset collection
        </a>
        (not covered by other tracks). The track %s is the most typical track,
        i.e. the one showing the
        <a href="%s">
        strongest preference for locating to positions covered by other tracks
         </a>
        in the collection.
    ''' % vals
    return [paragraph]


def generatePilotPageFiveParagraphs(gSuite, galaxyFn, regSpec='*', binSpec='*'):
    #Ripley K
    #One should always use bins equal or smaller than 10M fpr the ripleyK statistic
    gSuiteOverview = GSuiteOverview(gSuite)
    ripleysKAnalysisBin = GalaxyInterface._getUserBinSource(regSpec, "1m", genome=gSuite.genome)
    rkResults1Kpbs = gSuiteOverview.getGSuiteRipleysKData(bpWindow=1000, analysisBins=ripleysKAnalysisBin)
    ripleysKAnalysisBin = GalaxyInterface._getUserBinSource(regSpec, "10m", genome=gSuite.genome)
    rkResults1Mpbs = gSuiteOverview.getGSuiteRipleysKData(bpWindow=1000000, analysisBins=ripleysKAnalysisBin)
    avgRK1Kpbs, minRK1Kpbs, maxRK1Kpbs, weakStrong1Kpbs = \
        gSuiteOverview.getGSuiteRipleysKSummaryStatistics(rkResults1Kpbs)
    avgRK1Mpbs, minRK1Mpbs, maxRK1Mpbs, weakStrong1Mpbs = \
        gSuiteOverview.getGSuiteRipleysKSummaryStatistics(rkResults1Mpbs)
    weakStrong1Mpbs = '' if weakStrong1Mpbs == weakStrong1Kpbs else weakStrong1Mpbs
    table7Link = generateTableURLFromDataDict(
        galaxyFn, 'ripley1kbp', ['Track', 'Ripleys K (1kbp)'],
        rkResults1Kpbs, plotType='columnChart')
    table8Link = generateTableURLFromDataDict(
        galaxyFn, 'ripley1mbp', ['Track', 'Ripleys K (1mbp)'],
        rkResults1Mpbs, plotType='columnChart')

    vals = (weakStrong1Kpbs,
            avgRK1Kpbs,
            weakStrong1Mpbs,
            avgRK1Mpbs,
            table7Link,
            minRK1Kpbs,
            maxRK1Kpbs,
            table8Link,
            minRK1Mpbs,
            maxRK1Mpbs
            )
    vals = tuple([strWithNatLangFormatting(x) for x in vals])
    paragraph = '''
     On average, the tracks show a %s as measured by a Ripleys K
     of %s at scale 1Kbp and %s measured by %s at scale 1Mbp (on average across tracks).
     Between tracks, these numbers range from
     <a href="%s">
     %s to %s at scale 1Kbp
     </a>
      and from
      <a href="%s">
      %s to %s at scale 1Mbp
      </a>.
    ''' % vals
    return [paragraph]




def getQueryTrackCoverageFromRawOverlapResults(results):
    resultsList = results.values()
    assert(len(resultsList) > 0)
    singleResult = resultsList[0]
    return singleResult['Only1'] + singleResult['Both']


