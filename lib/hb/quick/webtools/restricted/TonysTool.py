from collections import defaultdict

from PIL import Image

from gold.application.LogSetup import logMessage
from gold.origdata.BedGraphComposer import BedGraphComposer
from gold.origdata.TrackGenomeElementSource import TrackGenomeElementSource
from gold.track.GenomeRegion import GenomeRegion
from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.util.GenomeInfo import GenomeInfo
from quick.webtools.GeneralGuiTool import GeneralGuiTool


# This is a template prototyping GUI that comes together with a corresponding
# web page.

class TonysTool(GeneralGuiTool):
    
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
        print len(res[0]), res[-1][-1]
        #
        print len(res), ' x ', len(res[0])
        return res
    
    @classmethod
    def getValuesFromBedFile(cls, genome, fn, colorPattern=(1,0,0)):
        resDict = defaultdict(list)
        valDict = defaultdict(list)
        lineTab = []
        if type(fn) == type(None):
            return resDict
        elif isinstance(fn, basestring):
            lineTab = open(fn,'r').read().split('\n')
        else:
            lineTab = fn.returnComposed().split('\n')
        
        valueList = []
        for line in lineTab:
            lineTab = line.split('\t')
            try:
                chrom = lineTab[0]
                valDict[chrom]+=[float(lineTab[3])]
            except:
                logMessage(line)
        
        maxVal = max(max(valDict.values()))
        for chrom in GenomeInfo.getChrList(genome):
            if valDict.has_key(chrom):
                try:
                    resDict[chrom]+= [tuple([255 - (int(val*255/maxVal)*v) for v in colorPattern]) for val in valDict[chrom]]
                except:
                    logMessage ('Ny rundeeee:  '+ str([v for v in valDict[chrom][:10]])+ ':   '+str(maxVal))
                               
        print 'count', len(valDict.values())
        return resDict, maxVal
    
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
                color = tuple([min(v) for v in zip(*tempRes)])
                newResult[chrom]+=[color]
        return newResult
    
    @classmethod
    def MakeHeatmapFromTracks(cls, tr1, tr2=None, tr3=None):
        tableRowEntryTemplate = """<tr><td>%s</td><td><a href="%s"><img src="%s" /></a></td></tr>"""
        htmlPageTemplate = """<html><body><table border="1">%s</table></body></html>"""
        #fileDict = dict()
        
        tr1, tr2, tr3 = [ExternalTrackManager.extractFnFromGalaxyTN(x.split(':')) if x != '----- select -----' else None for x in choices[1:] ]
        ResultDicts = []
        maxVals = []
        for tr,color in [(tr1, (1,0,0)),(tr2, (0,1,0)),(tr3, (0,0,1))]:
            if tr:
                res, maxVal = getValuesFromBedFile(tr,color)
                ResultDicts += [res]
                maxVals.append(maxVal)
            else:
                maxVals.append(None)
        
        #ResultDicts += [getValuesFromBedFile(tr2,colorPattern=(0,1,0))] if tr2 else []
        
    
    
        htmlTableContent = []
        resultDict = syncResultDict(ResultDicts)
        
        for chrom, valList in resultDict.items():
            areaList = []
            #For doing recursive pattern picture
            posMatrix = cls.getResult(len(valList), 2,2)
            javaScriptList = [[0 for v in xrange(len(posMatrix[0])) ] for t in xrange(len(posMatrix))]
            rowLen = len(posMatrix[0])
            
            im = Image.new("RGB", (rowLen, len(posMatrix)), "white")
            for yIndex, row in enumerate(posMatrix):
                for xIndex, elem in enumerate(row):
                    im.putpixel((xIndex, yIndex), valList[elem])
                    region = yIndex*rowLen + xIndex
                    javaScriptList[yIndex][xIndex] = chrom+':'+str(elem*10)+'-'+str((elem+1)*10)+': '+repr([ round((255-v)/255.0 ,2 ) for v in valList[elem]])
                    #areaList.append(areaTemplate % (xIndex*10, yIndex*10, xIndex*11, yIndex*11, repr(valList[elem])))
            im2 = im.resize((len(posMatrix[0])*10, len(posMatrix)*10))
            
            fileElements = [GalaxyRunSpecificFile(['Recursive', chrom+'.png' ], galaxyFn), 
                            GalaxyRunSpecificFile(['Recursive', chrom+'Big.png' ], galaxyFn), 
                            GalaxyRunSpecificFile(['Recursive', chrom+'Zooming.html' ], galaxyFn)]
            #fileDict['Recursive/'+chrom] = fileElements
            im.save(fileElements[0].getDiskPath(ensurePath=True))
            im2.save(fileElements[1].getDiskPath(ensurePath=True))
            
            
            open(fileElements[2].getDiskPath(ensurePath=True),'w').write(htmlTemplate % (str(javaScriptList), fileElements[1].getURL(), fileElements[0].getURL()))
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
        
        
        ######open(galaxyFn,'w').write(htmlPageTemplate % ('\n'.join(htmlTableContent)))
    
    
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Tonys tool"

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
        return ['Select genome','Select source of track', 'Select Track', 'Select source of track', 'Select Track', 'Select source of track', 'Select Track' ] #Alternatively: [ ('box1','key1'), ('box2','key2') ]

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
        return ['no selection', 'from history', 'from tracks']
        
    @staticmethod    
    def getOptionsBox3(prevChoices):
        #return ''
        if prevChoices[-2] == 'from history':
            return ('__history__' ,'bed','bedgraph')#
        elif prevChoices[-2] == 'from tracks':
            return '__track__'
        else:
            return None
    
    @staticmethod    
    def getOptionsBox4(prevChoices):
        return ['no selection', 'from history', 'from tracks']
        
    @staticmethod    
    def getOptionsBox5(prevChoices):
        #return ''
        if prevChoices[-2] == 'from history':
            return ('__history__' ,'bed','bedgraph')#
        elif prevChoices[-2] == 'from tracks':
            return '__track__'
        else:
            return None
    
    @staticmethod    
    def getOptionsBox6(prevChoices):
        return ['no selection', 'from history', 'from tracks']
        
    @staticmethod    
    def getOptionsBox7(prevChoices):
        #return ''
        if prevChoices[-2] == 'from history':
            return ('__history__' ,'bed','bedgraph')#
        elif prevChoices[-2] == 'from tracks':
            return '__track__'
        else:
            return None
    
    
    
    #@staticmethod
    #def getDemoSelections():
    #    return ['testChoice1','..']
        
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
        
        
        #matchPos = strVal.search(':');\n   if (matchPos !=-1)\n    {\n   valList = eval(strVal.split(:)[1]);\n                formVal ="%s: " +valList[0]+"\n%s: " +valList[1]+"\n%s: " +valList[2];\n                document.myform.posAnchor.value = liste[pos_y][pos_x] + counter;\n            }\n        else\n            {\n                document.myform.posAnchor.value = "0";\n            }\n\n
        htmlTemplate = '''<html><head>\n\n<link href="http://ajax.googleapis.com/ajax/libs/jqueryui/1.8/themes/base/jquery-ui.css" rel="stylesheet" type="text/css"/>\n  <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.5/jquery.min.js"></script>\n  <script src="http://ajax.googleapis.com/ajax/libs/jqueryui/1.8/jquery-ui.min.js"></script>\n    <style type="text/css">\n    #slider { margin: 10px; }\n  </style>\n  <script type="text/javascript">\n  jQuery(document).ready(function() {\n    jQuery("#slider").slider({min: 0, value: 370, max: %i });\n  });\n  </script>\n\n\n  <link rel="stylesheet" type="text/css" href="http://hyperbrowser.uio.no/dev2/static/hyperbrowser/files/kaitre//image_zoom/styles/stylesheet.css" />
                    \n<script language="javascript" type="text/javascript" src="http://hyperbrowser.uio.no/dev2/static/hyperbrowser/files/kaitre//image_zoom/scripts/mootools-1.2.1-core.js">\n</script><script language="javascript" type="text/javascript" src="http://hyperbrowser.uio.no/dev2/static/hyperbrowser/files/kaitre//image_zoom/scripts/mootools-1.2-more.js">\n</script><script language="javascript" type="text/javascript" src="http://hyperbrowser.uio.no/dev2/static/hyperbrowser/files/kaitre//image_zoom/scripts/ImageZoom.js"></script>\n
        \n\n\n\n<script type="text/javascript" >\nliste =%s;\ncounter = 0;\n\n\nfunction point_it2(event){\n	pos_x = event.offsetX?(event.offsetX):event.pageX-document.getElementById("zoomer_image").offsetLeft;\n	pos_y = event.offsetY?(event.offsetY):event.pageY-document.getElementById("zoomer_image").offsetTop;\n        pos_x = Math.floor(pos_x/10);\n	pos_y = Math.floor(pos_y/10);\n	counter++;\n	strVal = liste[pos_y][pos_x];\n   	document.myform.posAnchor.value = liste[pos_y][pos_x] + counter;\n         val = strVal.split(':')[1].split('-')[0];\n	jQuery( "#slider" ).slider( "option", "value", val );\n        }\n</script>\n\n\n\n\n</head>
        <body><div id="container"><!-- Image zoom start --><div id="zoomer_big_container"></div><div id="zoomer_thumb">\n<a href="%s" target="_blank" >\n<img src="%s" /></a></div><!-- Image zoom end --></div>\n\n\n<form name="myform" action="http://www.mydomain.com/myformhandler.cgi" method="POST">\n<div align="center">\n\n<input type="text" name="posAnchor" size="50" value=".">\n<br>\n</div>\n</form>\n\n<div id="slider" onchange="jQuery('zoomer_region').css({ 'left': '31px', 'top': '15px'});"></div>\n%s</body></html>'''
        
        tableRowEntryTemplate = """<tr><td>%s</td><td><a href="%s"><img src="%s" /></a></td></tr>"""
        htmlPageTemplate = """<html><body><table border="1">%s</table></body></html>"""
        #fileDict = dict()
        tnList = []
        trackNameList = []
        genome = choices[0]
        for index in [1,3,5]:
            if choices[index] == 'no selection':
                tnList.append(None)
                trackNameList.append('.')
            elif choices[index] == 'from history':
                tnList.append(ExternalTrackManager.extractFnFromGalaxyTN(choices[index+1].split(':')))
                trackNameList.append(ExternalTrackManager.extractNameFromHistoryTN(choices[index+1].split(':')))
            else:
                regionList = []
                for chrom in GenomeInfo.getChrList(genome):
                    start = 0
                    binsize = 10000
                    chromSize = GenomeInfo.getChrLen(genome, chrom)
                    while start<=chromSize-binsize:
                        regionList.append(GenomeRegion(genome, chrom, start, start+binsize))
                        start+=binsize
                    if start<chromSize:
                        regionList.append(GenomeRegion(genome, chrom, start, chromSize))
                trackNameList.append(choices[index+1].split(':')[-1])        
                trackGESource = TrackGenomeElementSource(genome, choices[index+1].split(':'), regionList)
                bedgraphComp = BedGraphComposer(trackGESource)
                tnList.append(bedgraphComp)
                
        
        tr1, tr2, tr3 = tnList
        tName1, tName2, tName3 = trackNameList
        ResultDicts = []
        maxVals = []
        for tr,color in [(tr1, (1,0,0)),(tr2, (0,1,0)),(tr3, (0,0,1))]:
            logMessage(repr(tr))
            if tr:
                res, maxVal = cls.getValuesFromBedFile(genome, tr,color)
                logMessage('maxval:  '+str(maxVal))
                ResultDicts += [res]
                maxVals.append(maxVal)
            else:
                maxVals.append(None)
        htmlTnRangeVals = '\n'.join(['<br/>value range for track %i(%s): 0 - %i' % (index, v[0], v[1]) for index, v in  enumerate(zip(trackNameList, maxVals)) if v[0]!='.'])
        
        #ResultDicts = [cls.getValuesFromBedFile(genome, tr1,colorPattern=(1,0,0))]
        #ResultDicts += [cls.getValuesFromBedFile(genome, tr2,colorPattern=(0,1,0))] if tr2 else []
        #ResultDicts += [cls.getValuesFromBedFile(genome, tr3,colorPattern=(0,0,1))] if tr3 else []
    
    
        htmlTableContent = []
        resultDict = cls.syncResultDict(ResultDicts)
        
        for chrom, valList in resultDict.items():
            areaList = []
            #For doing recursive pattern picture
            posMatrix = cls.getResult(len(valList), 2,2)
            javaScriptList = [[0 for v in xrange(len(posMatrix[0])) ] for t in xrange(len(posMatrix))]
            rowLen = len(posMatrix[0])
            
            im = Image.new("RGB", (rowLen, len(posMatrix)), "white")
            for yIndex, row in enumerate(posMatrix):
                for xIndex, elem in enumerate(row):
                    im.putpixel((xIndex, yIndex), valList[elem])
                    region = yIndex*rowLen + xIndex
                    javaScriptList[yIndex][xIndex] = chrom+':'+str(elem*10)+'-'+str((elem+1)*10)+': '+repr([ round((255-v)/255.0 ,2 ) for v in valList[elem]])
                    #areaList.append(areaTemplate % (xIndex*10, yIndex*10, xIndex*11, yIndex*11, repr(valList[elem])))
            imSmall = im.resize((len(posMatrix[0])*3, len(posMatrix)*3))
            im2 = im.resize((len(posMatrix[0])*10, len(posMatrix)*10))
            
            fileElements = [GalaxyRunSpecificFile(['Recursive', chrom+'.png' ], galaxyFn),
                            GalaxyRunSpecificFile(['Recursive', chrom+'Big.png' ], galaxyFn),
                            GalaxyRunSpecificFile(['Recursive', chrom+'Zooming.html' ], galaxyFn)]
            #fileDict['Recursive/'+chrom] = fileElements
            imSmall.save(fileElements[0].getDiskPath(ensurePath=True))
            im2.save(fileElements[1].getDiskPath(ensurePath=True))
            
            #
            open(fileElements[2].getDiskPath(ensurePath=True),'w').write(htmlTemplate % (int(GenomeInfo.getChrLen(genome, chrom)/1000.0)+1, str(javaScriptList), fileElements[1].getURL(), fileElements[0].getURL(), htmlTnRangeVals) )#tName1, tName2, tName3, 
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
        
        
        open(galaxyFn,'w').write(htmlPageTemplate % ('\n'.join(htmlTableContent)))
        
        
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
    #    name. The base directory is STATIC_PATH as defined by Config.py. The
    #    full path is created from the base directory followed by the id.
    #    '''
    #    return None
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
