from collections import defaultdict

from gold.description.TrackInfo import TrackInfo
from proto.hyperbrowser.HtmlCore import HtmlCore
from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
from quick.application.GalaxyInterface import GalaxyInterface
from quick.util.CommonFunctions import ensurePathExists
from quick.util.GenomeInfo import GenomeInfo
from quick.webtools.GeneralGuiTool import GeneralGuiTool


class ReportTrackProperties(GeneralGuiTool):
    
    pieList = []
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Generate track summary"

    @staticmethod
    def getInputBoxNames():
        '''
        Specifies a list of headers for the input boxes, and implicitly also the
        number of input boxes to display on the page. The returned list can have
        two syntaxes:
        
            1) A list of strings denoting the headers for the input boxes in
               numerical order.
            2) A list of tuples of strings, where each tuple has
               two items: a header and a key.
        
        The contents of each input box must be defined by the function
        getOptionsBoxK, where K is either a number in the range of 1 to the
        number of boxes (case 1), or the specified key (case 2).
        '''
        return ['Select Genome','Select Track'] #Alternatively: [ ('box1','key1'), ('box2','key2') ]

    #@staticmethod
    #def getInputBoxOrder():
    #    '''
    #    Specifies the order in which the input boxes should be displayed, as a
    #    list. The input boxes are specified by index (starting with 1) or by
    #    key. If None, the order of the input boxes is in the order specified by
    #    getInputBoxNames.
    #    '''
    #    return None
    
    @staticmethod    
    def getOptionsBox1(): # Alternatively: getOptionsBoxKey1()
        '''
        Defines the type and contents of the input box. User selections are
        returned to the tools in the prevChoices and choices attributes to other
        methods. These are lists of results, one for each input box (in the
        order specified by getInputBoxOrder()).
        
        The input box is defined according to the following syntax:
        
        Selection box:          ['choice1','choice2']
        - Returns: string
        
        Text area:              'textbox' | ('textbox',1) | ('textbox',1,False)
        - Tuple syntax: (contents, height (#lines) = 1, read only flag = False)
        - Returns: string
        
        Password field:         '__password__'
        - Returns: string
        
        Genome selection box:   '__genome__'
        - Returns: string
        
        Track selection box:    '__track__'
        - Requires genome selection box.
        - Returns: colon-separated string denoting track name
        
        History selection box:  ('__history__',) | ('__history__', 'bed', 'wig')
        - Only history items of specified types are shown.
        - Returns: colon-separated string denoting galaxy track name, as
                   specified in ExternalTrackManager.py.
        
        History check box list: ('__multihistory__', ) | ('__multihistory__', 'bed', 'wig')
        - Only history items of specified types are shown.
        - Returns: OrderedDict with galaxy id as key and galaxy track name
                   as value if checked, else None.
        
        Hidden field:           ('__hidden__', 'Hidden value')
        - Returns: string
        
        Table:                  [['header1','header2'], ['cell1_1','cell1_2'], ['cell2_1','cell2_2']]
        - Returns: None
        
        Check box list:         OrderedDict([('key1', True), ('key2', False), ('key3', False)])
        - Returns: OrderedDict from key to selection status (bool).
        '''
        return '__genome__'
    
    @staticmethod    
    def getOptionsBox2(prevChoices): # Alternatively: getOptionsBoxKey2()
        '''
        See getOptionsBox1().
        
        prevChoices is a namedtuple of selections made by the user in the
        previous input boxes (that is, a namedtuple containing only one element
        in this case). The elements can accessed either by index, e.g.
        prevChoices[0] for the result of input box 1, or by key, e.g.
        prevChoices.key (case 2).
        '''
        return '__track__'
        
    #@staticmethod    
    #def getOptionsBox3(prevChoices):
    #    return ['']

    #@staticmethod    
    #def getOptionsBox4(prevChoices):
    #    return ['']

    @staticmethod
    def getDemoSelections():
        return ['hg18','Phenotype and disease associations:Assorted experiments:Virus integration, HPV specific, Kraus and Schmitz']
        
    @classmethod    
    def execute(cls, choices, galaxyFn=None, username=''):
        '''
        Is called when execute-button is pushed by web-user. Should print
        output as HTML to standard out, which will be directed to a results page
        in Galaxy history. If getOutputFormat is anything else than HTML, the
        output should be written to the file with path galaxyFn. If needed,
        StaticFile can be used to get a path where additional files can be put
        (e.g. generated image files). choices is a list of selections made by
        web-user in each options box.
        '''
        regSpec = '*'
        binSpec = '*'
        analysisDef = 'dummy -> PropPointCountsAllowOverlapsVsSegsStat'
        genome = choices[0]
        tn1 = choices[1].split(':')
        trInfo1 = TrackInfo(genome, tn1)
        trackType = trInfo1.trackFormatName
        resultDict = defaultdict(dict)
        singleTrackDict = defaultdict(list)
        geneSourceList = []
        singleRuns = 0
        trackType, trackCatObj = cls.getTrackTypeAnalysis(genome, trackType)
        trackCatObj.runAllAnalysises(genome, tn1, regSpec, binSpec)
        
        #for index, values  in  enumerate(analysisList):
        #    geneSource, AnalysisElements = values
        #    
        #    if geneSource:
        #        geneSourceList +=[geneSource]
        #    else:
        #        singleRuns +=1
        #    if not geneSource and singleRuns>1:
        #        continue
        #    
        #    for analysisKey, analysisVals in AnalysisElements.items():
        #        trackName, analysisDef, resKey = analysisVals
        #        trackNames = [tn1] if trackName is None else [tn1, trackName]
        #        if trackName == None:
        #            if index>0:
        #                
        #                gen, an = singleTrackDict[analysisKey]
        #                resultDict[geneSource][analysisKey] = resultDict[gen][an]
        #                
        #            else: 
        #                singleTrackDict[analysisKey]+=[geneSource, analysisKey]
        #                resultDict[geneSource][analysisKey] = (resKey, GalaxyInterface.runManual(trackNames, analysisDef, regSpec, binSpec, genome, galaxyFn, printResults=False, printProgress=False))
        #                
        #        else:    
        #            resultDict[geneSource][analysisKey] = (resKey, GalaxyInterface.runManual(trackNames, analysisDef, regSpec, binSpec, genome, galaxyFn, printResults=False, printProgress=False))
        #            
                    
        
        core = HtmlCore()
        core.begin(extraJavaScriptFns=['tabber.js','https://www.google.com/jsapi'],\
                   extraCssFns=['tabber.css'])
        stack = []
        
        SummaryTextTemplate = '''<div style="background-color:#FFE899;"><h3>Track report:</h3><br/><b>The track consists of %i elements along the genome (%i after merging overlapping elements), and covers %i base pairs (%s percent ) of the genome.
        The distribution of track elements along the genome is *visualized below*. It overlaps %s percent with exons,
        %s percent with introns, and %s percent with remaining inter-genic regions (according to the Ensembl gene definition, version <E>).
        Corresponding numbers for other gene definitions, as well as local results per chromosome, are given in the *tables below*. </b><br></div>'''# %(resultDict[geneSourceList[0]]['CountPointStat'].getGlobalResult()['Result'])
        
        
        #if singleTrackDict.has_key('CountPointStat'):
        if trackCatObj.resultDict.has_key('CountPointStat'):
        
            
            #globalResDict, localResDict = cls.makeGlobalAndLocalResDicts(resultDict)
            globalResDict, localResDict = trackCatObj.makeGlobalAndLocalResDicts()
            geneSourceList = globalResDict.keys()
            print 'globalResDict', globalResDict
            print 'localResDict', localResDict
            if len(geneSourceList)==0:
                exonPercent, intronsPercent, interGeneticPercent = '0','0','0'
                geneSourceList += [None]
            else:
                sectionsEnsmblRes = globalResDict[geneSourceList[0]]
                totalEnsmbl = float(sum(sectionsEnsmblRes))
                exonPercent = str(round(sectionsEnsmblRes[0]*100/totalEnsmbl, 2)) if sectionsEnsmblRes>0 else '0'
                intronsPercent = str(round(sectionsEnsmblRes[1]*100/totalEnsmbl, 2)) if totalEnsmbl>0 else '0'
                interGeneticPercent = str(round(sectionsEnsmblRes[2]*100/totalEnsmbl, 2) ) if totalEnsmbl>0 else '0'
            
            
            resKey, result = trackCatObj.resultDict.get('CountPointStat')
            bpCoverage = numElems = int(result.getGlobalResult()[resKey])
            
            resKey, result = trackCatObj.resultDict.get('numElAllowOverlap')
            numUniqueElems = int(result.getGlobalResult()[resKey])
            
            if trackType.lower().find('segment')>=0:
                resKey, result = trackCatObj.resultDict.get('bpCoverage')
                bpCoverage = int(result.getGlobalResult()[resKey])
            
            genomeBps = sum( GenomeInfo.getStdChrLengthDict(genome).values())
            core.paragraph(SummaryTextTemplate % (numUniqueElems, numElems, bpCoverage, str(round(float(bpCoverage)/genomeBps, 2)) , exonPercent, intronsPercent, interGeneticPercent))
            core._str += '<div class="tabber">\n'
            stack.append('</div>\n')
            
            analysisDef = ' [centerRows=True] [normalizeRows=True] -> RawVisualizationDataStat'
            res = GalaxyInterface.runManual([tn1], analysisDef, regSpec, binSpec, genome, username=username, printResults=False, printHtmlWarningMsgs=False)
           
            cls.MakeGlobalResultsDiv(globalResDict, res, core, galaxyFn)
            cls.MakeLocalResultsDiv(localResDict, core)
            
            core._str += stack.pop()
            if len(cls.pieList)>0:
                core.line(cls.makeAllGooglePieChart(cls.pieList))
            
            print core
            
        #open(galaxyFn, 'w').write()
        
        
# This is a template prototyping GUI that comes together with a corresponding
# web page.
    
    
    @classmethod
    def makeTrackImage(cls, res, fn, main):
        from proto.RSetup import r
        resDictKey = 'Result'
        POINT_SIZE = 12
        LINE_HEIGHT = POINT_SIZE * 1.38
        
        ensurePathExists(fn)
        bmpFn = fn 

        width = 1000
        height = 30 *min(100, len(res))
        picType = 'png256'
        r.png(filename=bmpFn, height=max([200, height]), width=width, units='px', pointsize=POINT_SIZE, res=72)
        if resDictKey is not None:
            xlab = res.getLabelHelpPair(resDictKey)[0]
        else:
            xlab = None
        
        
        rCode = ''' par(mar=c(4.2, 0.2, 0.2, 14.2))\n
        plot.new()\n
            plot.window(xlim=c(0,%i),ylim=c(0,%i))\n
            axis(1)\n
            axis(4, at=((1:%i)*30)-21, lab=c(%s), las=1)\n
            %s
        '''
        
        yFloor = 1
        rectTemplate = 'rect(%f,%i,%f,%i, col="%s", border="%s")\n'
        rectVals = []
        globRes = res.getGlobalResult()
        visRes = globRes.values()[0]
        rawData = visRes.getAllTrackViews()
        
        yLabels = []
        maxVal = max([tv._bpSize() for tv in rawData])
        halfMax = maxVal/2
        for tv in rawData:
            yLabels.append('"'+tv.genomeAnchor.chr+': %s"'% ':'.join(str(tv.genomeAnchor).split()[0].split(':')[1:]))
            startArr, endArr = tv.startsAsNumpyArray(),tv.endsAsNumpyArray()
            if tv.normalizeRows:
                normalizer = 1000.0/tv._bpSize() if len(endArr)>0 else 0
                maxVal = 1000
                rectVals.append(rectTemplate % (0, yFloor+8, 1000, yFloor+8, 'lightgray', 'lightgray') )
                
                rectVals += [rectTemplate % (start*normalizer, yFloor, end*normalizer, yFloor+15, 'red', 'red') for start, end in zip(startArr, endArr)]
                
            else:
                extra1=extra2 = 0
                if tv.centerRows:
                    halfBin = tv._bpSize()/2
                    extra1 = halfMax-halfBin
                    extra2 = halfMax+halfBin
                    
                rectVals.append(rectTemplate % (0+extra1, yFloor+8, extra2 if tv.centerRows else tv._bpSize()  , yFloor+5, 'lightgray', 'lightgray') )
                rectVals += [rectTemplate % (start+extra1, yFloor, end+extra1, yFloor+15, 'red', 'red') for start, end in zip(startArr, endArr)]
            yFloor+=30
        
        if len(rectTemplate)>0:
            
            rScript = rCode % (maxVal, height, len(yLabels), ','.join(yLabels), '\n'.join(rectVals))
            r(rScript)
    
    @classmethod
    def makeAllGooglePieChart(cls, pieChartsList):
        
        googleTemplate = '''<script type="text/javascript">
      google.load("visualization", "1", {packages:["corechart"]});
      google.setOnLoadCallback(drawChart);
      function drawChart() {\n%s\n}\n</script>'''
        return googleTemplate % '\n\n'.join(pieChartsList)
    
    @classmethod
    def makeSinglePieChartSubstance(cls,divId, table, title):
        anchorStr = '<div id="%s" style="width: 500px; height: 300px;"></div>' % divId
        pieStr = '''var chart = new google.visualization.PieChart(document.getElementById('%s'));\n\t
        chart.draw(google.visualization.arrayToDataTable(%s), {title: '%s'});\n\t'''% (divId, repr(table) if not isinstance(table, basestring) else table, title)
        
        return anchorStr, pieStr 
    
    @classmethod
    def putPieChartsOnPage(cls,divId, core, xLabels, yLabels, dataList):
        anchorList = []
        for indx, geneSource in enumerate(yLabels):
            datarow = ['["%s", %f]' % (xLabels[i+1], float(v)) for i, v in enumerate(dataList[indx])]
            anchorStr, pieStr = cls.makeSinglePieChartSubstance(divId+'_'+geneSource, '[["label1", "label2"], '+','.join(datarow)+']', geneSource)
            
            anchorList.append(anchorStr)
            #core.line(anchorStr)
            cls.pieList.append(pieStr)
        core._str+='<table>\n'
        for i in range(0,len(anchorList),2):
            t1  = anchorList[i]
            t2 = anchorList[i+1]if i+1<len(anchorList) else ''
            
            core._str+='<tr><td>%s</td><td>%s</td></tr>\n' % (t1,t2)
        core._str+='</table>\n'
        
        
    @classmethod
    def MakeGlobalResultsDiv(cls, totResDict, visResults, core, galaxyFn):
        #core.divBegin(divId='globalResDiv', style='display:none')
        
        core._str+='<div class="tabbertab">\n     <h2>Global Result</h2>\n<div class="tabber" id="GlobalRes">\n'
        
        # tab for table
        
        yLabels = sorted([v for v in totResDict.keys() if v])
        dataList = [totResDict[v] for v in yLabels]
        xLabels = ['Gene source', 'Exon area', 'Intron area', 'Inter-gene area', 'Total']
        if len(yLabels)>0:
            core._str += '<div class="tabbertab">\n     <h2>Table</h2>\n'
            cls.makeHtmlTable(dataList, xLabels, yLabels, 'Global', core, 'Normal')
            core._str+='</div>\n'
        
        
        core._str += '<div class="tabbertab">\n     <h2>Visualization</h2>'
        figImage = GalaxyRunSpecificFile(['VizTrackOnGenome.png'], galaxyFn)
        cls.makeTrackImage(visResults, figImage.getDiskPath(ensurePath=True), '')
        figUrl = figImage.getURL()
        core.line('<img src="%s" alt="Figure" height="%i" width="800"/>' % (figUrl, max([200,30*min(100, len(visResults))]) ))
        if len(yLabels)>0:
            cls.putPieChartsOnPage('', core, xLabels, yLabels, dataList)
        
        core._str+='</div>\n</div>\n</div>\n'
    
    @classmethod
    def makeGlobalAndLocalResDicts(cls, trackTypeObj):
        localResDict = defaultdict(dict)
        globalResDict = dict()
        for exonKey, geneKey in trackTypeObj.getGeneAndExonKeyPairs():
            numGeneTracks = 0
            geneSource = geneKey.split('_')[-1]
            for run in [exonKey, geneKey,'CountPointStat']:
                numGeneTracks+=1
                resKey, runResult = trackTypeObj.resultDict[run]
                for ge in runResult.keys():
                    val = runResult[ge][resKey]
                    if localResDict[geneSource].has_key(ge):
                        templist = localResDict[geneSource][ge]
                        templist.append(val-templist[-1])
                    else:
                        templist = [val]
                    localResDict[geneSource][ge] = templist
            totalSum = [] #['Total for the genome']
            for i in range(numGeneTracks):
                totalSum.append(sum([v[i] for v in localResDict[geneSource].values()]))
            globalResDict[geneSource] = totalSum
        
        return globalResDict, localResDict
    
    
    @classmethod
    def MakeLocalResultsDiv(cls, localResDict, core):
        core._str+='<div class="tabbertab">\n     <h2>Local Result</h2>\n<div class="tabber" id="LocalRes">\n'
        
        
        for geneSource, formattedResult in localResDict.items():
            if geneSource == None:
                continue
            core._str += '<div class="tabbertab">\n     <h2>%s</h2>\n<div class="tabber" id="%s">\n' % (geneSource, geneSource)
            
            if len(formattedResult)>0:
                
                yLabels = sorted(formattedResult.keys())
                dataList = [formattedResult[v] for v in yLabels]
                yLabels = [str(v) for v in yLabels]
                xLabels = ['Region', 'Exon area', 'Intron area', 'Inter-gene area', 'Total']
                for label in ['Normal', 'Percent (Vertical)', 'Percent (Horizontal)']:
                    core._str += '<div class="tabbertab">\n     <h3>%s</h3>\n' % label
                    #core._str += '<table class="colored bordered" width="100%" style="table-layout:auto; word-wrap:break-word;">\
                    #             <tr><th class="header">Region</th><th class="header">Exon area</th><th class="header">Intron area</th><th class="header">Inter-gene area</th><th class="header">Total</th></tr>\
                    #             <tr><td>chr21:1-20000000</td><td>0</td><td>0</td><td>1</td><td>1</td></tr></table>\n'
                    cls.makeHtmlTable(dataList, xLabels, yLabels, geneSource, core, label)
                    if label == 'Normal':
                        cls.putPieChartsOnPage(geneSource, core, xLabels, yLabels, dataList)
                    core.divEnd()
            core.divEnd()
            core.divEnd()    
                
        #localFilePath = localResFile.getDiskPath(ensurePath=True)
        
        core.divEnd()
        core.divEnd()
         
    @classmethod
    def makeRadioButtons(cls, geneSource, core):
        #assume x and y labels are in accordance with the data
        
        core.line('<form>')
        core._str+='<input type="radio" value="%s_percent" onclick="showhide(\'table_%s_percentV\', \'\');">Percent (Vertical)' % (geneSource, geneSource)
        core._str+='<input type="radio" value="%s_percent_horiz" onclick="showhide(\'table_%s_percentH\', \'\');">Percent (Horisontal)' % (geneSource, geneSource)
        core.line('<input type="radio" value="%s" onclick="showhide(\'table_%s\', \'\');">Normal' % (geneSource, geneSource))
        core.line('</form>')
        core.paragraph('Results for %s.' % geneSource)   
        
    @classmethod
    def makeHtmlTable(cls,dataList, xLabels, yLabels, geneSource, core, percentage):
        #assume x and y labels are in accordance with the data
        
        geneId = geneSource+'_'+percentage
        verticalSum = [sum(v) for v in zip(*dataList)]
        hSum = [sum(v) for v in dataList]
        nCols = len(dataList[0])
        core.tableHeader(xLabels,firstRow=True)
        if percentage == 'Percent (Vertical)':
            for rIndex in range(len(yLabels)): 
                core.tableLine([yLabels[rIndex]]+[str((float(v)/float(verticalSum[i]))*100) if int(verticalSum[i])>0 else '0' for i, v in enumerate(dataList[rIndex])]+['-'])
                        
        elif percentage == 'Percent (Horizontal)':
            for rIndex in range(len(yLabels)):
                core.tableLine([yLabels[rIndex]]+[str((float(v)/hSum[rIndex])*100) if hSum[rIndex]>0 else '0' for i, v in enumerate(dataList[rIndex])]+['100'])
                    
        else:
            for rIndex in range(len(yLabels)):
                core.tableLine([yLabels[rIndex]]+dataList[rIndex] + [str(hSum[rIndex])] )
                
        core.tableLine(['Total']+(verticalSum+[str(sum(hSum))] if percentage=='Normal' else (['100']*nCols +['-'] if percentage=='Percent (Vertical)' else ['-']*nCols+['-']) ))
        core.tableFooter()
        
    
    @classmethod
    def makeJsSyntax(cls):
        
	return """function showhide(activeId, elemType){
            ids = null;
            divs = ["globalResDiv", "localResDiv", "localRes_Ensembl","localRes_Refseq","localRes_UCSC Known Genes"];
            tables = ["table_Global", "table_Global_percentV", "table_Global_percentH", "table_Ensembl","table_Refseq","table_UCSC Known Genes", "table_Ensembl_percentV","table_Refseq_percentV","table_UCSC Known Genes_percentV", "table_Ensembl_percentH","table_Refseq_percentH","table_UCSC Known Genes_percentH"]
            if (elemType === 'div'){
                ids = divs;
                
            }
            else {
                ids = tables;
            }
            for (i=0;i<ids.length;i++)
            {
                id = ids[i];
		if (document.getElementById){
			obj = document.getElementById(id);
                        
                        if (id === activeId){ 
				obj.style.display = "";
			}
                        else if (id.match("globalResDiv|localResDiv")){
                            if (activeId.match("globalResDiv|localResDiv")){
                                obj.style.display = "none";
                            }
                        }
                        else { 
				obj.style.display = "none"; 
			} 
		}
            }
        setDefault(activeId, elemType);
	}
        
        function setDefault(activeId, elemType){
            if (elemType === 'div'){
                obj = document.getElementById("table_Global");
                obj.style.display = "";
                obj = document.getElementById("table_Global_percentV");
                obj.style.display = "none";
                obj = document.getElementById("table_Global_percentH");
                obj.style.display = "none";
                
                obj = document.getElementById("table_Ensembl");
                obj.style.display = "";
                obj = document.getElementById("table_Refseq");
                obj.style.display = "";
                obj = document.getElementById("table_UCSC Known Genes");
                obj.style.display = "";
                obj = document.getElementById("table_Ensembl_percentV");
                obj.style.display = "none";
                obj = document.getElementById("table_Refseq_percentV");
                obj.style.display = "none";
                obj = document.getElementById("table_UCSC Known Genes_percentV");
                obj.style.display = "none";
                 obj = document.getElementById("table_Ensembl_percentH");
                obj.style.display = "none";
                obj = document.getElementById("table_Refseq_percentH");
                obj.style.display = "none";
                obj = document.getElementById("table_UCSC Known Genes_percentH");
                obj.style.display = "none";
                }
                if (activeId === "localResDiv"){
                obj = document.getElementById("localRes_UCSC Known Genes");
                obj.style.display = "";
            }
	}"""
    
    @classmethod
    def getTrackTypeAnalysis(cls, genome, trackFormatName):
        
        #trackTypeDict = {'points':'points' ,'valued points':'valuedPoints' ,'segments':'segments' ,\'valued segments':'valuedSegments' ,'genome partition':'genomePartition' ,        'step function':'stepFunction' ,'function':'function' ,'linked points':'linkedPoints' ,'linked valued points':'linkedValuedPoints' ,'linked segments':'linkedSegments' ,'linked valued segments':'linkedValuedSegments' ,'linked genome partition':'linkedGenomePartition' ,'linked step function':'linkedStepFunction' ,'linked function':'linkedFunction' ,'linked base pairs':'linkedBasePairs'}
        
        trackTypeDict = {'points':Points ,
        'valued points':ValuedPoints ,
        'segments':Segments ,
        'valued segments':ValuedSegments ,
        'step function':StepFunction ,
        'function':Function ,
        'linked points':LinkedPoints ,
        'linked valued points':LinkedValuedPoints ,
        'linked segments':LinkedSegments ,
        'linked valued segments':LinkedValuedSegments }
        resultList = []
        trackFormatName = trackFormatName.replace('Unmarked','').replace('Marked', 'Valued').strip().lower()
        
        return trackFormatName, trackTypeDict[trackFormatName](genome)
        
        
        #tnExon = 'Genes and gene subsets:Exons:Ensembl'.split(':')
        #tnGenes = 'Genes and gene subsets:Genes:Ensembl'.split(':')
        #countDef = 'dummy -> CountPointStat'
        #bpDef = 'dummy -> CountSegmentStat'
        #elemsAllowOverlap = 'dummy -> CountPointAllowingOverlapStat'
        #multiCountDef = 'dummy -> PointCountInsideSegsStat'
        #countConvertDef = 'dummy [tf1=SegmentToMidPointFormatConverter] -> PropPointCountsAllowOverlapsVsSegsStat'
        #SingleCountConvertDef  = 'dummy [tf1=SegmentToMidPointFormatConverter] -> CountPointStat'
        #
        #
        #for geneSource in ['Ensembl', 'Refseq', 'UCSC Known Genes']:
        #    tnExon = ('Genes and gene subsets:Exons:'+geneSource).split(':')
        #    tnGenes =('Genes and gene subsets:Genes:'+geneSource).split(':')
        #    ExonsCountPointStat = [tnExon, multiCountDef, 'Result']
        #    GenesCountPointStat = [tnGenes, multiCountDef, 'Result']
        #
        #    points = { 'numElAllowOverlap':[None, elemsAllowOverlap, 'Result'], 'CountPointStat':[None, countDef, 'Result']}
        #    
        #    valuedPoints = {'numElAllowOverlap':[None, elemsAllowOverlap, 'Result'], 'CountPointStat':[None, countDef, 'Result']}
        #    
        #    segments = {'numElAllowOverlap':[None, elemsAllowOverlap, 'Result'], 'bpCoverage':[None, bpDef, 'Result'], 'CountPointStat':[None, SingleCountConvertDef, 'Result']}#, 
        #    
        #    valuedSegments = {'numElAllowOverlap':[None, elemsAllowOverlap, 'Result'], 'bpCoverage':[None, bpDef, 'Result'], 'CountPointStat':[None, SingleCountConvertDef, 'Result']}
        #    
        #    genomePartition = {}
        #    
        #    stepFunction = {}
        #    
        #    function = {}
        #    
        #    linkedPoints = {'numElAllowOverlap':[None, elemsAllowOverlap, 'Result'], 'CountPointStat':[None, countDef, 'Result']}
        #    
        #    linkedValuedPoints = {'numElAllowOverlap':[None, elemsAllowOverlap, 'Result'], 'CountPointStat':[None, countDef, 'Result']}
        #    
        #    linkedSegments = {'numElAllowOverlap':[None, elemsAllowOverlap, 'Result'], 'bpCoverage':[None, bpDef, 'Result'], 'CountPointStat':[None, SingleCountConvertDef, 'Result']}
        #    
        #    linkedValuedSegments = {'numElAllowOverlap':[None, elemsAllowOverlap, 'Result'], 'bpCoverage':[None, bpDef, 'Result'], 'CountPointStat':[None, SingleCountConvertDef, 'Result']}
        #    
        #    linkedGenomePartition = {}
        #    
        #    linkedStepFunction = {}
        #    
        #    linkedFunction = {}
        #    
        #    linkedBasePairs = {}
        #    analysisDict = eval(trackTypeDict[trackFormatName])
        #    if GalaxyInterface.isTrackNameValid(genome, tnExon):
        #        analysisDict['Exons_CountPointStat'] = ExonsCountPointStat
        #
        #    if GalaxyInterface.isTrackNameValid(genome, tnGenes):
        #        analysisDict['Genes_CountPointStat'] = GenesCountPointStat
        #    
        #    if not set(['Exons_CountPointStat','Genes_CountPointStat']).intersection(set(analysisDict.keys())):
        #        geneSource = None
        #    resultList.append((geneSource, analysisDict))
        #    
        #
        #
        return trackFormatName, resultList#trackTypeDict[trackFormatName]
    
    @staticmethod
    def validateAndReturnErrors(choices):
        return None
        

class AnalysisTrack(object):
    
    def __init__(self, genome, statsToRun):
        self.resultDict = dict()
        self.analysisDict = statsToRun
        self.getGenesForGenome(genome)
    
    def getGenesForGenome(self, genome):
        tnExon = ['Genes and gene subsets','Exons']
        tnGenes =['Genes and gene subsets','Genes']
        multiCountDef = 'dummy -> PointCountInsideSegsStat'
        try:
            genesList = [ v[0] for v in GalaxyInterface.getSubTrackNames(genome, tnGenes, deep=False)[0]]
            exonList =  [ v[0] for v in GalaxyInterface.getSubTrackNames(genome, tnExon, deep=False)[0]]
            
            for tn in genesList:
                self.analysisDict['Genes_CountPointStat_'+tn] = [tnGenes+[tn], multiCountDef, 'Result']
            for tn in exonList:
                self.analysisDict['Exons_CountPointStat_'+tn] = [tnExon+[tn], multiCountDef, 'Result']
                
        except:
            pass
    
    def runAllAnalysises(self, genome, tn, regSpec, binSpec):
        for analysisKey, analysisVals in self.analysisDict.items():
                trackName, analysisDef, resKey = analysisVals
                trackNames = [tn] if trackName is None else [tn, trackName]
                try:
                    self.resultDict[analysisKey] = (resKey, GalaxyInterface.runManual(trackNames, analysisDef, regSpec, binSpec, genome, galaxyFn=None, printResults=False, printProgress=False))
                except:
                    pass
                
    def getGeneAndExonKeyPairs(self):
        resultList = []
        geneSourceSet = set([v.split('_')[-1] for v in self.analysisDict.keys() if v.find('_CountPointStat_')>=0])
        for gSource in geneSourceSet:
            resultList.append(('Exons_CountPointStat_'+gSource, 'Genes_CountPointStat_'+gSource))
        return resultList
    
    
    def makeGlobalAndLocalResDicts(self):
        localResDict = defaultdict(dict)
        globalResDict = dict()
        missingDict = defaultdict(list)
        for exonKey, geneKey in self.getGeneAndExonKeyPairs():
            numGeneTracks = 0
            geneSource = geneKey.split('_')[-1]
            for run in [exonKey, geneKey,'CountPointStat']:
                
                if self.resultDict.has_key(run):
                    resKey, runResult = self.resultDict[run]
                    for ge in runResult.keys():
                        val = runResult[ge][resKey]
                        if localResDict[geneSource].has_key(ge):
                            templist = localResDict[geneSource][ge]
                            templist.append(val-templist[-1])
                        else:
                            templist = [val]
                        localResDict[geneSource][ge] = templist
                else:
                    missingDict[geneSource].append(numGeneTracks)
                numGeneTracks+=1
            if missingDict.has_key(geneSource):
                for key, val in localResDict[geneSource].items():
                    for index in missingDict[geneSource]:
                        val.insert(index, 0)
                    localResDict[geneSource][key] = val
                
            totalSum = [] #['Total for the genome']
            for i in range(numGeneTracks):
                totalSum.append(sum([v[i] for v in localResDict[geneSource].values()]))
            globalResDict[geneSource] = totalSum
        
        return globalResDict, localResDict
        
class Points(AnalysisTrack):
    
    def __init__(self, genome, statsToRun=None):
        
        countDef = 'dummy -> CountPointStat'
        elemsAllowOverlap = 'dummy -> CountPointAllowingOverlapStat'
        
        points = { 'numElAllowOverlap':[None, elemsAllowOverlap, 'Result'], 'CountPointStat':[None, countDef, 'Result']}
        if type(statsToRun) == dict:
            points.update(statsToRun)
        super(Points, self).__init__(genome, points)


class ValuedPoints(Points):
    
    def __init__(self, genome, statsToRun=None):
        valuedPoints = {}
        if type(statsToRun) == dict:
            valuedPoints.update(statsToRun)
            
        super(ValuedPoints, self).__init__(genome, valuedPoints)

class LinkedPoints(Points):
    
    def __init__(self, genome, statsToRun=None):
        linkedPoints = {}
        if type(statsToRun) == dict:
            linkedPoints.update(statsToRun)
        super(LinkedPoints, self).__init__(genome, linkedPoints)

class LinkedValuedPoints(LinkedPoints):
    
    def __init__(self, genome, statsToRun=None):
        linkedValuedPoints = {}
        if type(statsToRun) == dict:
            linkedValuedPoints.update(statsToRun)
        super(LinkedValuedPoints, self).__init__(genome, linkedValuedPoints)

class Segments(AnalysisTrack):
    
    def __init__(self, genome, statsToRun=None):
        elemsAllowOverlap = 'dummy -> CountPointAllowingOverlapStat'
        SingleCountConvertDef  = 'dummy [tf1=SegmentToMidPointFormatConverter] -> CountPointStat'
        bpDef = 'dummy -> CountSegmentStat'
        
        segments = {'numElAllowOverlap':[None, elemsAllowOverlap, 'Result'], 'bpCoverage':[None, bpDef, 'Result'], 'CountPointStat':[None, SingleCountConvertDef, 'Result']}#, 
        if type(statsToRun) == dict:
            segments.update(statsToRun)    
        super(Segments, self).__init__(genome, segments)

class ValuedSegments(Segments):
    
    def __init__(self, genome, statsToRun=None):
        valuedSegments = {}
        if type(statsToRun) == dict:
            valuedSegments.update(statsToRun)
        super(ValuedSegments ,self).__init__(genome, valuedSegments)

class LinkedSegments(Segments):
    
    def __init__(self, genome, statsToRun=None):
        linkedSegments = {}
        if type(statsToRun) == dict:
            linkedSegments.update(statsToRun)
        super(LinkedSegments,self).__init__(genome, linkedSegments)

class LinkedValuedSegments(LinkedSegments):
    
    def __init__(self, genome, statsToRun=None):
        linkedValuedSegments = {}
        if type(statsToRun) == dict:
            linkedValuedSegments.update(statsToRun)
        super(LinkedValuedSegments, self).__init__(genome, linkedValuedSegments)

class Function(AnalysisTrack):
    
    def __init__(self, genome, statsToRun=None):
        function = {}
        if type(statsToRun) == dict:
            function.update(statsToRun)
        super(Function, self).__init__(genome, function)

class StepFunction(AnalysisTrack):
    
    def __init__(self, genome, statsToRun=None):
        stepFunction = {}
        if type(statsToRun) == dict:
            stepFunction.update(statsToRun)
        super(StepFunction, self).__init__(genome, stepFunction)
        
