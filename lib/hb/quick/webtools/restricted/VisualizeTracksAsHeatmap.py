import time
from collections import defaultdict

from PIL import Image

from gold.track.GenomeRegion import GenomeRegion
from gold.track.Track import PlainTrack
from gold.util.CommonFunctions import parseShortenedSizeSpec, prettyPrintTrackName
from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.util.GenomeInfo import GenomeInfo
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from third_party.alphanum import alphanum


# This is a template prototyping GUI that comes together with a corresponding
# web page.

#def chrNameCompare(x, y):
#    if all([True if len(v)>3 else False for v in [x,y]]):
#        if x[3:].isdigit() and y[3:].isdigit():
#            return int(x[3:]) - int(y[3:])
#        elif x[3:].isalpha():
#            return 1
#        else:
#            return -1
        

class VisualizeTracksAsHeatmap(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Create high-resolution map of multiple track distributions along genome"

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
        return ['Genome build: ', \
                'Fetch track from: ', \
                'Select track to visualize: ', \
                'Select track to visualize: ', \
                'Fetch track from: ', \
                'Select track to visualize: ', \
                'Select track to visualize: ', \
                'Fetch track from: ', \
                'Select track to visualize: ', \
                'Select track to visualize: ', \
                'Specify resolution (number of base pairs represented by a single pixel): '] #Alternatively: [ ('box1','key1'), ('box2','key2') ]

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
        
        History selection box:  ('__history__',) | ('__history__', 'bed', 'bedgraph')
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
    def getOptionsBox2(prevChoices):
        return ['history', 'HyperBrowser repository']
        
    @staticmethod    
    def getOptionsBox3(prevChoices):
        #return ''
        if prevChoices[1] == 'history':
            return '__history__','bed','point.bed','category.bed','valued.bed','bedgraph'
            
    @staticmethod    
    def getOptionsBox4(prevChoices):
        if prevChoices[1] == 'HyperBrowser repository':
            return '__track__'
    
    @staticmethod    
    def getOptionsBox5(prevChoices):
        return ['-- No track --', 'history', 'HyperBrowser repository']
        
    @staticmethod    
    def getOptionsBox6(prevChoices):
        #return ''
        if prevChoices[4] == 'history':
            return '__history__','bed','point.bed','category.bed','valued.bed','bedgraph'
            
    @staticmethod    
    def getOptionsBox7(prevChoices):
        if prevChoices[4] == 'HyperBrowser repository':
            return '__track__'
    
    @staticmethod    
    def getOptionsBox8(prevChoices):
        return ['-- No track --', 'history', 'HyperBrowser repository']
        
    @staticmethod    
    def getOptionsBox9(prevChoices):
        #return ''
        if prevChoices[7] == 'history':
            return '__history__','bed','point.bed','category.bed','valued.bed','bedgraph'
            
    @staticmethod    
    def getOptionsBox10(prevChoices):
        if prevChoices[7] == 'HyperBrowser repository':
            return '__track__'
    
    @staticmethod    
    def getOptionsBox11(prevChoices):
        #Binsize
        return '10000'
        
    @staticmethod    
    def getOptionsBox12(prevChoices):
        #Binsize
        return repr(prevChoices), 1, True
    
    @staticmethod
    def getDemoSelections():
        return ['hg19', 'HyperBrowser repository', 'None', 'Genes and gene subsets:Exons:Ensembl exons', 'HyperBrowser repository', 'None', 'Genes and gene subsets:Introns:Ensembl introns', 'HyperBrowser repository', 'None', 'Sequence:Repeating elements', '10000', 'None']
    
    @classmethod
    def getSubResult(cls, start, end, realNum, rows, cols):
        #print start, end
        if end-start == rows*cols:
            tempRes = [range(start+cols*i,min(realNum, start+cols*(i+1))) if start+cols*i < realNum else [] for i in range(rows)]
            return tempRes
            
            
        elif end-start > rows*cols:
            addition = int((end-start)/4)
            
            res1 = cls.getSubResult(start, start+addition, realNum, rows, cols)
            res2 = cls.getSubResult(start+addition, start+addition*2, realNum, rows, cols)
            res3 = cls.getSubResult(start+addition*2, start+addition*3, realNum, rows, cols)
            res4 = cls.getSubResult(start+addition*3, start+addition*4, realNum, rows, cols)
            
            entries = len(res1)
            result = [[] for v in range(entries*2)]
            counter=0
            for resTuple in [(res1,res2),(res3,res4)]:
                for index in range(entries):
                    result[counter] += resTuple[0][index]+resTuple[1][index]
                    counter+=1
            return result
    
    @classmethod
    def getResult(cls, numEntries, rows, cols):
        expandedEntries = rows*cols
        while expandedEntries< numEntries:
            expandedEntries*=4
            
        res = [row for row in cls.getSubResult(0, expandedEntries, numEntries, rows, cols) if row !=[]]
        return res
    
    @classmethod
    def putBpsInMicroDict(cls, microDict, chrom, bigBin, start, end, sEntry, eEntry, microBin ):
        
        if not microDict[chrom].has_key(bigBin):
            
            microDict[chrom][bigBin] = [0]*100
        
        if sEntry == eEntry:
            microDict[chrom][bigBin][sEntry] += end-start
            
        else:
            microDict[chrom][bigBin][sEntry] += microBin - (start%microBin)
            for i in range(sEntry+1, eEntry):
                microDict[chrom][bigBin][i] = microBin
                     
            rest = end%microBin
            if rest>0:
                microDict[chrom][bigBin][eEntry]+= rest
    
    @classmethod
    def putBpsInResultDict(cls, resDict, chrom, start, end, binSize, microDict, microBin, fullMicroBin):
        
        sEntry = start/binSize
        eEntry = end/binSize
        microStart, microEnd = start%binSize, end%binSize
        msEntry, meEntry = microStart/microBin, microEnd/microBin
        if sEntry == eEntry:
            resDict[chrom][sEntry] += end-start
            cls.putBpsInMicroDict(microDict, chrom, sEntry, microStart, microEnd, msEntry, meEntry, microBin)
        else:
            resDict[chrom][sEntry] += binSize - (start%binSize)
            cls.putBpsInMicroDict(microDict, chrom, sEntry, microStart, binSize-1, msEntry, 99, microBin)
            for i in range(sEntry+1, eEntry):
                resDict[chrom][i] = binSize
                microDict[chrom][i] = fullMicroBin
                
            rest = end%binSize
            if rest>0:
                resDict[chrom][eEntry]+= rest
                cls.putBpsInMicroDict(microDict, chrom, eEntry, 0, rest, 0, meEntry, microBin)
                
    @classmethod
    def formatBedLines(cls, genome, lineDict, binSize):
        chrLength = GenomeInfo.getStdChrLengthDict(genome)
        numElems = dict([(k, v/binSize+(1 if v%binSize>0 else 0))for k, v in chrLength.items()])
        resDict = dict([(k, [0.0]*v) for k, v in numElems.items()])
        microDict = defaultdict(dict)
        microBin = binSize/100
        fullMicroBin = [microBin]*100
        
        for chrom, vals in lineDict.items():
            try:
                prevStart, prevEnd = vals[0]
                for start,end in vals[1:]:
                    if prevEnd>=start:
                        if end>prevEnd:
                            prevEnd = end
                        continue
                    cls.putBpsInResultDict(resDict, chrom, prevStart, prevEnd, binSize, microDict, microBin, fullMicroBin)
                    prevStart, prevEnd = start, end
                cls.putBpsInResultDict(resDict, chrom, prevStart, prevEnd, binSize, microDict, microBin, fullMicroBin)
            except:
                pass
        #logMessage('resDict[chr1][26]:   '+repr(resDict['chr1'][26]))
        #logMessage("microDict['chr1'][26]:   "+str(sum([v if v<10001 else v-10000 for v in microDict['chr1'][26]]))+':   '+repr(microDict['chr1'][26]))
        maxVal = max( [max(v) for v in resDict.values()] )
        return resDict, microDict, maxVal
    
    
    @classmethod
    def getValuesFromBedFile(cls, genome, fn, colorPattern=(1,1,1), binSize=1000000):
        resDict = defaultdict(list)
        valDict = defaultdict(list)
        lineDict = defaultdict(list)
        colPatStr = repr(colorPattern)
        startTime = time.time()
        if type(fn) == type(None):
            return resDict
        elif isinstance(fn, basestring):
            for line in open(fn,'r'):
                row = line.split('\t')
                try:
                    lineDict[row[0]].append((int(row[1]), int(row[2])))
                    
                except:
                    pass
            for chrom in lineDict.keys():
                lineDict[chrom].sort()
        else:
            track, genomeRegList = fn
            for region in genomeRegList:
                tv = track.getTrackView(region)
                start = list(tv.startsAsNumpyArray())
                end = list(tv.endsAsNumpyArray())
                lineDict[region.chr] = [(int(k), int(v)) for k, v in zip(start, end)]
                
        #logMessage('Time after reading in files(%s): '%colPatStr + str(time.time()-startTime)) 
        valDict, microDict, maxVal = cls.formatBedLines(genome, lineDict, binSize)
        chrsWithData = set([k for k, v in valDict.items() if sum(v)>0])# set of chromosomes with actual values
        #logMessage('Time after processing files(%s): '%colPatStr + str(time.time()-startTime)) 
        for chrom in GenomeInfo.getChrList(genome):
            if valDict.has_key(chrom):
                try:
                    #resDict[chrom]+= [tuple([255 - (int(val*255/maxVal)*v) for v in colorPattern]) for val in valDict[chrom]]
                    resDict[chrom]+= [tuple([int(val*255/maxVal)*v for v in colorPattern]) for val in valDict[chrom]]
                except:
                    pass
                    #logMessage ('Ny rundeeee:  '+ str([v for v in valDict[chrom][:10]])+ ':   '+str(maxVal))
                               
        return resDict, microDict, maxVal, chrsWithData
    
    @classmethod
    def syncResultDict(cls, resultDicts):
        newResult = defaultdict(list)
        for chrom in resultDicts[0].keys():
            valLists = [v[chrom] for v in resultDicts]
            
            for elemIndex in range(len(valLists[0])):
                color = None
                tempRes = []
                for valListIndx in range(len(valLists)):
                    tempRes.append(valLists[valListIndx][elemIndex])
                #print tempRes
                color = tuple([max(v) for v in zip(*tempRes)])
                newResult[chrom]+=[color]
        return newResult
    
    @classmethod   
    def execute(cls, choices, galaxyFn=None, username=''):
        #val = strVal.split(':')[1].split('k')[0];
        htmlTemplate = '''<html><head>\n\n<link href="http://ajax.googleapis.com/ajax/libs/jqueryui/1.8/themes/base/jquery-ui.css" rel="stylesheet" type="text/css"/>\n  <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.5/jquery.min.js"></script>\n  <script src="http://ajax.googleapis.com/ajax/libs/jqueryui/1.8/jquery-ui.min.js"></script>\n
        <script type='text/javascript' src='https://www.google.com/jsapi'></script>
        <script type='text/javascript'> 
          google.load("visualization", "1", {packages:["corechart"]});\n google.setOnLoadCallback(drawLine);
          function drawLine(divId) {\n}
      </script>
        <style type="text/css">\n    #slider { margin: 10px; }\n  </style>\n  <script type="text/javascript">\n  jQuery(document).ready(function() {\n    jQuery("#slider").slider({min: 0, value: 370, max: %i });\n  });\n  </script>\n\n\n  <link rel="stylesheet" type="text/css" href="http://hyperbrowser.uio.no/gsuite/static/hyperbrowser/files/kaitre//image_zoom/styles/stylesheet.css" />
                    \n<script language="javascript" type="text/javascript" src="http://hyperbrowser.uio.no/gsuite/static/hyperbrowser/files/kaitre//image_zoom/scripts/mootools-1.2.1-core.js">\n</script><script language="javascript" type="text/javascript" src="http://hyperbrowser.uio.no/gsuite/static/hyperbrowser/files/kaitre//image_zoom/scripts/mootools-1.2-more.js">\n</script><script language="javascript" type="text/javascript" src="http://hyperbrowser.uio.no/gsuite/static/hyperbrowser/files/kaitre//image_zoom/scripts/ImageZoom.js"></script>\n
        \n\n\n\n<script type="text/javascript" >\nliste =%s;\ncounter = 0;\n\n\nfunction point_it2(event){\n
        document.myform.posAnchor.value = "";
        chrom = %s;\n
        trackNames = %s;
        pos_x = event.offsetX?(event.offsetX):event.pageX-document.getElementById("zoomer_image").offsetLeft;\n	pos_y = event.offsetY?(event.offsetY):event.pageY-document.getElementById("zoomer_image").offsetTop;\n        factor = %i;\n        pos_x = Math.floor(pos_x/factor);\n	pos_y = Math.floor(pos_y/factor);\n	counter++;\n
        var strVal = liste[pos_y][pos_x];
        var strTab = strVal.split(",");
        
        
        val = strTab[0];
        streng = chrom+":"+strTab[0]+"k | ";
        for(i=0; i<trackNames.length; i++) { 
            streng = streng + trackNames[i]+': '+strTab[i+1]+'%% | ';
           }
            
        document.myform.posAnchor.value = streng;\n
        jQuery( "#slider" ).slider( "option", "value", val );\n
        
                }\n</script>\n\n\n\n\n</head>
        <body>
        <h2 align="center" style="color:#FF7400;">Heatmap for chromosome %s</h2> 
        <div id="slider" ></div><br>
        \n<form name="myform" action="http://www.mydomain.com/myformhandler.cgi" method="POST">\n<div align="center">\n\n<input type="text" name="posAnchor" size="250" value=".">\n<br>\n</div>\n</form>\n<br>
        <div id="container"><!-- Image zoom start --><div id="zoomer_big_container"></div><div id="zoomer_thumb">\n<a href="%s" target="_blank" >\n<img src="%s" /></a></div><!-- Image zoom end --></div>\n\n\n%s
         
         <br/>%s</body></html>''' # onchange="jQuery('zoomer_region').css({ 'left': '31px', 'top': '15px'});"
        
        tableRowEntryTemplate = """<div class="tabbertab"><h2>%s</h2><a href="%s"><img src="%s" /></a></div>"""
        htmlPageTemplate = """<html><head>\n<script type="text/javascript" src="/gsuite/static/scripts/tabber.js"></script>\n<link href="/gsuite/static/style/tabber.css" rel="stylesheet" type="text/css" />\n
                    </head><body>%s</body></html>"""
        
        #fileDict = dict()
        binsize = parseShortenedSizeSpec(choices[10])
            
        tnList = []
        trackNameList = []
        genome = choices[0]
        chrLength = GenomeInfo.getStdChrLengthDict(genome)
        
        for index in [1,4,7]:
            startTime = time.time()
            if choices[index] in ['-- No track --','',None]:
                tnList.append(None)
                trackNameList.append('.')
                continue
            elif choices[index] == 'history':
                #trackName = ExternalTrackManager.getPreProcessedTrackFromGalaxyTN(choices[0], choices[index+1].split(':'))
                trackName = choices[index+1].split(':')
                tnList.append(ExternalTrackManager.extractFnFromGalaxyTN(trackName))
                trackNameList.append(prettyPrintTrackName(trackName))
            else:
                trackName = choices[index+2].split(':')
                track = PlainTrack(trackName)
                regionList = [GenomeRegion(genome, chrom, 0, chrLength[chrom]) for chrom in GenomeInfo.getChrList(genome)]
                tnList.append((track, regionList))    
                trackNameList.append(prettyPrintTrackName(trackName))
                
                
        trackNames = repr([v for v in trackNameList if v!='.'])
        tr1, tr2, tr3 = tnList
        ResultDicts = []
        maxVals = []#list of the maximum coverage in a bin for each track Used for normalization purposes
        chrsWithData = set()# set of chromosomes with any data. No point in generating images with no data...
        microDictList = []
        counter = 0
        for tr,color in [(tr1, (1,0,0)),(tr2, (0,1,0)),(tr3, (0,0,1))]:
            
            maxVal = None
            if tr:
                if len([1 for v in tnList if v]) == 1:
                    color = (1,1,1)
                
                res, microDict, maxVal, trackChrs = cls.getValuesFromBedFile(genome, tr,color, binsize)
                microDictList.append((trackNames[counter],microDict))
                counter+=1
                chrsWithData = chrsWithData|trackChrs
                ResultDicts += [res]   
            maxVals.append(maxVal)
            
        
        htmlTableContent = []
        resultDict = cls.syncResultDict(ResultDicts)
        binfactor = binsize/1000
        for chrom in sorted(list(chrsWithData), cmp=alphanum):
            valList = resultDict[chrom]
            areaList = []
            #For doing recursive pattern picture
            bigFactor = int(10*(binsize/10000.0)**(0.5))
            smallFactor = bigFactor/3
            posMatrix = cls.getResult(len(valList), 2,2)
            javaScriptList = [[0 for v in xrange(len(posMatrix[0])*bigFactor) ] for t in xrange(len(posMatrix)*bigFactor)]
            rowLen = len(posMatrix[0])
            
            im = Image.new("RGB", (rowLen, len(posMatrix)), "white")
            for yIndex, row in enumerate(posMatrix):
                for xIndex, elem in enumerate(row):
                    im.putpixel((xIndex, yIndex), valList[elem])
                    region = yIndex*rowLen + xIndex
                    #for yVals in range(yIndex*bigFactor, (yIndex+1)*bigFactor):
                    #    for xVals in range(yIndex*bigFactor, (yIndex+1)*bigFactor):
                    #        javaScriptList[yVals][xVals] = chrom+':'+str(elem)+'-'+str(elem+1)+': '+repr([ v/255.0 for v in valList[elem]])
                    
                    #javaScriptList[yIndex][xIndex] = chrom+':'+str(elem*binfactor)+'k - '+str((elem+1)*binfactor)+'k : '+repr([ trackNameList[indx]+'='+str(round(v*100/255.0, 2))+'%' for indx, v in enumerate(valList[elem])])
                    javaScriptList[yIndex][xIndex] = ','.join([str(elem*binfactor)]+[ str(round(v*100/255.0, 2)) for indx, v in enumerate(valList[elem]) if trackNameList[indx] !='.'] )
            for i in range(len(javaScriptList)):
                javaScriptList[i] = [v for v in javaScriptList[i] if v !=0]
                
        
            imSmall = im.resize((len(posMatrix[0])*smallFactor, len(posMatrix)*smallFactor))
            im2 = im.resize((len(posMatrix[0])*bigFactor, len(posMatrix)*bigFactor))
            
            fileElements = [GalaxyRunSpecificFile(['Recursive', chrom+'.png' ], galaxyFn ), GalaxyRunSpecificFile(['Recursive', chrom+'Big.png' ], galaxyFn), GalaxyRunSpecificFile(['Recursive', chrom+'Zooming.html' ], galaxyFn)]
            #fileDict['Recursive/'+chrom] = fileElements
            imSmall.save(fileElements[0].getDiskPath(ensurePath=True))
            im2.save(fileElements[1].getDiskPath(ensurePath=True))
            
            trackAndValRangeTab = zip(trackNameList, maxVals)
            colorTab = []
            onlyOneTrack = True if len([v for v in maxVals if v]) ==1 else False
            for color, vals in [('Red_combination',[1,0,0]), ('Green_combination',[0,1,0]), ('Blue_combination',[0,0,1]),('Red-Green_combination',[1,1,0]), ('Red-Blue_combination',[1,0,1]), ('Green-Blue_combination',[0,1,1]), ('Red-Green-Blue_combination',[1,1,1])]:    
                
                if not None in [maxVals[i] for i in range(len(vals)) if vals[i]>0]:
                    im = Image.new("RGB", (256 , 1), "white")
                    tracksInvolved = ' & '.join([str(index+1) for index, v in enumerate(vals) if v>0])
                    if onlyOneTrack:
                        vals = [1,1,1]
                    for val in range(256):
                        colVal = [val*v for v in vals]
                        
                        im.putpixel((val,0), tuple(colVal))
                    imColFile = GalaxyRunSpecificFile(['Recursive', color+'.png' ], galaxyFn)
                    imCol = im.resize((256, 10))
                    imCol.save(imColFile.getDiskPath(ensurePath=True))
                    colorTab.append('<tr><td>Track %s</td><td>  <img src="%s" /></td></tr>'% (tracksInvolved, imColFile.getURL()))
                    
            
            htmlTnRangeVals= '<br/><br/><table align="center"  cellspacing="10"><tr><th>Track number</th><th>Track name</th><th>Value range</th></tr>\n'
            htmlTnRangeVals += '\n'.join(['<tr/><td>Track %i </td><td>%s</td><td> 0 - %i</td></tr>' % (index+1, v[0], v[1]) for index, v in  enumerate(trackAndValRangeTab) if v[1]] )
            htmlTnRangeVals+='</table> <br/><table align="center"  cellspacing="10"><tr><th>Track combination</th><th>Colour range</th></tr>' + '\n'.join(colorTab) + '</table>\n'
            lineTabStr= ''
            #if chrom == 'chr1':
            #    tempList = [range(100)]+[v[1]['chr1'][26] for v in microDictList]
            #    chartTemplate =  "['%i',  %i, %i, %i]"
            #    lineTab = [ chartTemplate % v for v in zip(*tempList)]    
            #    lineTemplate = """<div id="%s" onclick="{\nvar data = google.visualization.arrayToDataTable([\n    %s\n  ]);\nvar options = {  title: 'Detailed Graph'    };var chart = new google.visualization.LineChart(document.getElementById('%s'));chart.draw(data, options);}" style="width: 1000px; height: 700px;"></div>"""
            #    lineTabStr = lineTemplate % ('line_div', ', '.join(lineTab),'line_div')    
            open(fileElements[2].getDiskPath(ensurePath=True),'w').write(htmlTemplate % (int(GenomeInfo.getChrLen(genome, chrom)/1000.0)+1, repr(javaScriptList), repr(chrom), trackNames,bigFactor, chrom, fileElements[1].getURL(), fileElements[0].getURL(), htmlTnRangeVals, lineTabStr) )# 
            htmlTableContent.append(tableRowEntryTemplate % (chrom, fileElements[2].getURL(), fileElements[0].getURL()))
            
            # FOr doing normal picture
            #columns = int(round((len(valList)/1000)+0.5))
            #im = Image.new("RGB", (1000, columns), "white")        
            #y=-1    
            #for index, valuTuple in enumerate(valList):
            #    x = index%1000
            #
            #    if x == 0:
            #        y+=1
            #    try:
            #        im.putpixel((x, y), valuTuple)
            #    except:
            #        pass
            #im.save(chrom+'.png')
            #htmlTableContent.append(tableRowEntryTemplate % (chrom, chrom+'.png'))
        
        tabberMal = '<div class="tabber">%s</div>'
        #tempRes, res = [],[]
        res = [tabberMal % v for v in htmlTableContent]
        #for i in htmlTableContent:
        #    if len(tempRes) == 10:
        #        res.append(tabberMal % '\n'.join(tempRes))
        #        tempRes = []
        #    tempRes.append(i)
        #if len(tempRes)>0:
        #    res.append(tabberMal % '\n'.join(tempRes))
        open(galaxyFn,'w').write(htmlPageTemplate % ('<br/>'.join(res)))
        
        
        #print '<img src="http://hyperbrowser.uio.no/dev2/static/hyperbrowser/files/kaitre/chrYBig.png"/>'

    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''
        
        for choiceIndex in [1,4,7]:
            if choices[choiceIndex] not in [None, '-- No track --']:
                trackChoiceIndex = choiceIndex+1 if choices[choiceIndex] == 'history' else choiceIndex+2
                errorStr = VisualizeTracksAsHeatmap._checkTrack(choices, trackChoiceIndex=trackChoiceIndex)
                if errorStr:
                    return errorStr
                    
                trackType = VisualizeTracksAsHeatmap._getBasicTrackFormat(choices, trackChoiceIndex)[-1]
            
                if trackType not in ['segments', 'points', 'valued segments', 'valued points']:
                    return 'Please select a track of segments or points. You selected a track with basic type: %s' % trackType
        
        try:
            resolution = parseShortenedSizeSpec(choices[10])
        except:
            return 'The resolution is incorrectly specified: "%s". Please integer numbers, ' % choices[10] + \
                   'or the shortened format, e.g. "20k" or "1m".'
            
        if resolution < 1000:
            return 'The smallest accepted resolution is 1000.'
        
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
    
    @classmethod
    def _additionalToolDescription(cls, core):
        core.paragraph('''
This tool uses up to three separate color
channels (red,green,blue) to visualize the presence of up to three different
tracks in corresponding parts of the genome by combining their color channel
values at individual pixels.''')
    
    @classmethod
    def getToolDescription(cls):
        '''
        Specifies a help text in HTML that is displayed below the tool.
        '''
        from proto.hyperbrowser.HtmlCore import HtmlCore
        core = HtmlCore()
        core.paragraph('''
Visualizing track elements along a line, such as in the UCSC Genome Browser or
the tool "Visualize track elements relative to anchor region", can necessarily only offer a global
overview at a very limited resolution. This tool instead uses a fractal layout
of the genome line (similar to a Hilbert curve) to map genome locations to
individual pixels in a matrix instead of along a line, effectively increasing
the resolution quadratically. Although the interpretation requires a certain
effort, this form of visualization can potentially be very informative.''')
        cls._additionalToolDescription(core)
        return str(core)
    #
    #@staticmethod
    #def getToolIllustration():
    #    '''
    #    Specifies an id used by StaticFile.py to reference an illustration file
    #    on disk. The id is a list of optional directory names followed by a file
    #    name. The base directory is STATIC_PATH as defined by Config.py. The
    #    full path is created from the base directory followed by the id.
    #    '''
    #    return None
        
    @staticmethod
    def getFullExampleURL():
        return 'u/hb-superuser/p/high-resolution-visualization-of-tracks'

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
    #def isDebugMode():
    #    '''
    #    Specifies whether debug messages are printed.
    #    '''
    #    return False
    #
    
    # @classmethod
    # def getTests(cls):
    #     return ["$Tool[hb_visualize_tracks_as_heatmap]('hg18'|'HyperBrowser repository'|None|'Sample data:Track types:Segments'|'HyperBrowser repository'|None|'Sample data:Track types:Valued segments (category)'|'HyperBrowser repository'|None|'Sample data:Track types:Valued segments (number)'|'10000')"]
    
    @staticmethod    
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        #
        return 'customhtml'
