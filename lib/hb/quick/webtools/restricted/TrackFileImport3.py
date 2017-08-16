import datetime
import os
from collections import OrderedDict
from functools import partial

from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.restricted.EncodeDatabase import EncodeDatabase


# This is a template prototyping GUI that comes together with a corresponding
# web page.

class TrackFileImport3(GeneralGuiTool):
    
    DB = EncodeDatabase("host='localhost' dbname='abdulara'"\
                            " user='abdulara' password='144144'")
    
    INDEX_TABLE = None
    ATTRIBUTES = []
    
    SELECTED_ATTRIBUTES = []
    RESULT_FILES_URLS = []
    SELECTED_FILES_INDEXES = []
    TIME_STAMP = None
    
    colList = DB.getTableCols('file_encode', ordered = True)
    for col in colList:
       searchable = DB.runQuery\
       ("select _searchable from field where term = '"+col+"';")
       #print searchable
       if searchable[0][0] == True and col.find('_') == -1:
          ATTRIBUTES.append(col)
    
              
    @staticmethod
    def getToolName():                                                      
        
        return "ENCOCE (UCSC and Ensembl)"

    @staticmethod
    def getInputBoxNames():
        
        attrBoxes = []
        for i in xrange(len(TrackFileImport3.ATTRIBUTES)):
            attrBoxes.append(('<b>Select Attribute:</b>',\
                 'attributeList%s' % i))
            attrBoxes.append((35*'&#160'+'Select Value: ',\
                 'valueList%s' % i))
            attrBoxes.append(('Range ' + TrackFileImport3.ATTRIBUTES[i],\
                 'variableRange%s' % i))
            
        
        
        return [#('Track source', 'source'), \
                #('Search method', 'search'), \
                ('HIDDEN_0','hidden'),\
                ('Session Id','sessionId'),
                #('Select an attribute:','attributes'),\
                #('Filter by dataType?', 'filterDataType'), \
                #('dataType', 'dataType'), \
                #('Filter by cell?', 'filterCell'), \
                #('cell', 'cell'), \
                #('Filter by antibody?', 'filterAntibody'), \
                #('antibody', 'antibody'), \
                #('Filter by type?', 'filterType'),\
                 ] +\
                 attrBoxes +\
                [#('HIDDEN_1','dbTemp'),\
                 ('<h3>Download Results?</h3>', 'download'),\
                 ('<h3>Results</h3>','results'),\
                 ('<h3>Output Format</h3>','outFormat')]

    #@staticmethod
    #def getInputBoxOrder():
    #    '''
    #    Specifies the order in which the input boxes should be displayed, as a
    #    list. The input boxes are specified by index (starting with 1) or by
    #    key. If None, the order of the input boxes is in the order specified by
    #    getInputBoxNames.
    #    '''
    #    return None

    #@staticmethod
    #def getOptionsBoxSource(): # Alternatively: getOptionsBoxKey1()
        
    #    return ['-- Select track source --', 'ENCODE','EpiGenome']

    #@staticmethod
    #def getOptionsBoxSearch(prevChoices): # Alternatively: getOptionsBoxKey2()
        
    #    if prevChoices.source != '-- Select track source --':
    #        return ['-- Select search method --', 'Structured search']

    
    @staticmethod
    def getOptionsBoxHidden():
        return
                 
    @classmethod
    def getOptionsBoxSessionId(cls,prevChoices): 
        if prevChoices.sessionId == None:
			     cls.TIME_STAMP = str(datetime.datetime.now())
           #TrackFileImport.DB.createTableFromList('temp',['session_id','attr'])
        else:
			     cls.TIME_STAMP = prevChoices.sessionId
        return '__hidden__',cls.TIME_STAMP
    
               
    #@staticmethod
    #def getOptionsBoxAttributes(prevChoices): 
        #if not prevChoices.search == 'Structured search':
        #    return 
        
    #    colsList = []
    #    for col in TrackFileImport3.ATTRIBUTES:
            #colsList.append((col,False))
    #        colsList.append(col)
        
        #return OrderedDict(colsList)
    #    colsList.insert(0,'--None--')
        #colsList.insert(1,'--All--')
    #    return colsList
        
    
    #@staticmethod
    #def getOptionsBoxDbTemp(prevChoices):
    #    
    #    selected_attr = prevChoices.attributes
    #    if selected_attr in [None,'--None--'] :
    #       TrackFileImport3.DB.runQuery\
    #       ("delete from temp where session_id like '"+prevChoices.sessionId+"';")
    #       return
    #    
    #    rows = TrackFileImport3.DB.runQuery\
    #    ("select attr from temp where session_id like '"+prevChoices.sessionId+"';")
    #    selected_attrs_db = [x[0] for x in rows]
    #    if selected_attr == '--All--':
    #       for x in TrackFileImport3.ATTRIBUTES:
    #          if not selected_attr in selected_attrs_db:
    #             TrackFileImport3.DB.insertRow\
    #             ('temp',{'session_id':prevChoices.sessionId,'attr':x}) 
    #    elif not selected_attr in selected_attrs_db:
    #       TrackFileImport3.DB.insertRow\
    #       ('temp',{'session_id':prevChoices.sessionId,'attr':selected_attr})
    #    
    #       
    #    return    
    
    @classmethod
    def setupVariableBoxFunctions(cls):
        for i in xrange(len(TrackFileImport3.ATTRIBUTES)):
            setattr(cls, 'getOptionsBoxValueList%s' % i,\
             partial(cls._getVariableBox, index=i))
            setattr(cls, 'getOptionsBoxAttributeList%s' % i,\
             partial(cls._getVariableListBox, index=i)) 
            setattr(cls, 'getOptionsBoxVariableRange%s' % i,\
             partial(cls._getVariableRangeBox, index=i))
    
    @classmethod
    def _getVariableRangeBox(cls, prevChoices, index):
        rows = TrackFileImport3.DB.runQuery\
        ("select attr from temp where session_id like '"+prevChoices.sessionId+"';")
        selected_attrs = [x[0] for x in rows]
        if not TrackFileImport3.ATTRIBUTES[index] in selected_attrs:
           return
        if getattr(prevChoices, 'valueList%s' % index) == '--Range--':
           return ''
        
    @classmethod
    def _getVariableListBox(cls, prevChoices, index):
        if index > 0 and getattr(prevChoices, 'valueList%s' % (index-1))\
         in [None,'--Everything--','']:
           return
        #if val == None:
        #   return
        colsList = TrackFileImport3.ATTRIBUTES[:]
        colsList.insert(0,'--None--')
        if index == 0:
           return colsList
        for i in xrange(len(TrackFileImport3.ATTRIBUTES)):
            if i >= index:
               break
            val = getattr(prevChoices, 'attributeList%s' % i)
            if val in [None,'--None--']:
               continue
            elif val in colsList:
               colsList.remove(val)  
                    
            #   colsList.append(TrackFileImport3.ATTRIBUTES[i])
            #elif getattr(prevChoices, 'valueList%s' % i) == None:
            #   colsList.append(TrackFileImport3.ATTRIBUTES[i])
        return colsList
        
    @classmethod
    def _getVariableBox(cls, prevChoices, index):
        
        #rows = TrackFileImport3.DB.runQuery\
        #("select attr from temp where session_id like '"+prevChoices.sessionId+"';")
        #selected_attrs = [x[0] for x in rows]
        value = getattr(prevChoices, 'attributeList%s' % index)
        if value in [None,'--None--']:
            return
        
        #appear = False
        
        #for i in xrange(len(TrackFileImport3.ATTRIBUTES)):
        #    if i > index:
        #       continue
        #    elif getattr(prevChoices, 'attributeList%s' % i) == value:
        #       appear = True
        
        #if not appear:
        #   return 
                
        #col = TrackFileImport3.ATTRIBUTES[index]
        
        WHERE = ''
        for i in xrange(len(TrackFileImport3.ATTRIBUTES)):
            #Otherwise, will generate an exception. Because 'prevChoices'
            #must be only the 'Previous' ones
            if i >= index: 
               break
            col = getattr(prevChoices, 'attributeList%s' % i)
            val = getattr(prevChoices, 'valueList%s' % i)
            if col in [None,'--None--'] or val in ['--Everything--','--Range--',None,'']:
               continue
            col = TrackFileImport3.DB.correctColumNames([col])[0]
            
            
            WHERE += col + " LIKE '" + val + "' AND "
            
        if WHERE.endswith('AND '):
           WHERE = WHERE.strip('AND ')
        
        rows = TrackFileImport3.DB.getColGroup('file_encode',\
                                               value,\
                                               where = WHERE, ordered = True)
        
        if len(rows) == 0:
           return ['--Everything--','--Range--']
        elif rows[0][0] != None and str(rows[0][0]).find('Error') != -1:
           return rows[0][0].split('\n')  
        items = [name for name,count in rows]
        if None in items:
           items.remove(None)
        items.insert(0,'--Everything--')
        ##items.insert(1,'--Range--')
        
        return items
        
           
    @classmethod
    def getOptionsBoxSessionId(cls, prevChoices):
        #return '1'
        if prevChoices.sessionId == None:
			     cls.TIME_STAMP = str(datetime.datetime.now())
        else:
			     cls.TIME_STAMP = prevChoices.sessionId
  		  
        return '__hidden__',cls.TIME_STAMP
    
    @staticmethod
    def getOptionsBoxDownload(prevChoices):
        selected_attrs = 0
        for i in xrange(len(TrackFileImport3.ATTRIBUTES)):
            if not getattr(prevChoices, 'valueList%s' % i) in [None,'','--Everything--']:
                  selected_attrs+=1
        
        if selected_attrs == 0:
           return
        else:   
           return ['--NO--',\
           'Download results to history']#,'Download and convert to GTrack'] 
    
    @staticmethod
    def getOptionsBoxOutFormat(prevChoices): 
        
        
        if prevChoices.download != None:
           return ['Text','Html']
        
    @staticmethod
    def getOptionsBoxResults(prevChoices): 
        if prevChoices.download in [None,'--NO--']:
           return
        cols,colListString = TrackFileImport3.getColListString()
        rows = TrackFileImport3.getRows(prevChoices,colListString)
        List = []
        for row in rows:
            if row == None or len(row)<len(cols):
               continue
            
            #line = ''
            #for i in xrange(len(row)):
            #    line+= str(row[i])+'\t|'
            #line = line.strip('|')
            TrackFileImport3.RESULT_FILES_URLS.append(row[0].replace('http://','ftp://'))
            filename = row[0].split('/')[-1]
            List.append((filename,False))
    
        return OrderedDict(List)
        
    
    #@staticmethod
    @classmethod
    def execute(cls,choices, galaxyFn=None, username=''):
        
        
               
        cols, colListString = TrackFileImport3.getColListString()
        
        rows = TrackFileImport3.getRows(choices,colListString)
        
        outFile = open(galaxyFn, 'w')
        
        
        if len(TrackFileImport3.RESULT_FILES_URLS) > 0:
         
          
          i = 0
          for x,selected in choices.results.iteritems():
             if selected:
                TrackFileImport3.SELECTED_FILES_INDEXES.append(i)  
             i +=1
          import ftplib
          for i in TrackFileImport3.SELECTED_FILES_INDEXES:
              
              url = TrackFileImport3.RESULT_FILES_URLS[i]
              sitename = url.split(':')[1].strip('/').split('/')[0]
              filename = url.split('/')[-1]
              filepath = url.split(sitename)[1]
              fileExt = filename.strip(filename.split('.')[0])
              try:  
                conn = ftplib.FTP(sitename)
                conn.login('anonymous')
                
                f =  open(cls.makeHistElement(galaxyExt=fileExt.split('gz'),\
                 title=str(filename)), 'w')
                locatFPath = os.path.abspath(f.name) 
                conn.retrbinary('RETR ' + filepath, f.write, 1024)
                conn.quit()
                f.close()
              except:
                outFile.write('Error downloading file: '+filename+'\n')     
              #if fileExt.endswith('gz'):
              #   tar = tarfile.open(locatFPath, "r:gz")
                 
                      
        if choices.outFormat == 'Html':
           TrackFileImport3.printHtml(cols,rows,colListString,outFile)
        else:
           TrackFileImport3.printText(cols,rows,colListString,outFile)
        
    @staticmethod
    def getColListString():
        cols = TrackFileImport3.DB.correctColumNames\
        (TrackFileImport3.DB.getTableCols('file_encode'))
        colListString = ''
        cols.insert(0, cols.pop(cols.index('_url')))
        cols.insert(1, cols.pop(cols.index('datatype')))
        cols.insert(2, cols.pop(cols.index('cell')))
        cols.insert(3, cols.pop(cols.index('antibody')))
        cols.insert(4, cols.pop(cols.index('_source')))
        for col in cols:
           colListString += col+','
        
        return cols,colListString.strip(',')    
    
    @staticmethod
    def getRows(choices,colListString):
        WHERE = ''
        
        for i in xrange(len(TrackFileImport3.ATTRIBUTES)):
                        
            col = getattr(choices, 'attributeList%s' % i)
            val = getattr(choices, 'valueList%s' % i)
            if col in [None,'--None--'] or val in ['--Everything--','--Range--',None,'']:
               continue
            col = TrackFileImport3.DB.correctColumNames([col])[0]            
            
            
            WHERE += col + " LIKE '" + val + "' AND "
            
        if WHERE.endswith('AND '):
           WHERE = WHERE.strip('AND ')
        
        query = "select "+colListString+" from file_encode "
        if WHERE != '':
           query += "where "+WHERE+";"
        else:
           query += ";"
        
        rows = TrackFileImport3.DB.runQuery(query)
        if len(rows) == 0 or rows == None:
           return
        return rows
        
    @staticmethod
    def printHtml(cols,rows,colListString,outFile):
        
        colListString = colListString.replace('_','').upper()
        colListString = colListString.replace('"','')
        
        
        from proto.hyperbrowser.HtmlCore import HtmlCore
        core = HtmlCore()
        core.begin()
        
        core.tableHeader(colListString.split(','),sortable = True)
        
        if len(TrackFileImport3.SELECTED_FILES_INDEXES)>0:
           arr = TrackFileImport3.SELECTED_FILES_INDEXES
        else:
           arr = range(len(rows))
        for i in arr:
            row = rows[i]
            if row == None or len(row)<len(cols):
               continue
            url = str(row[0])
            filename = url.split('/')[-1]
            link = HtmlCore().link(filename,url)
            row = list(row)
            row[0] = link
            core.tableLine([str(x) for x in row])
            
        core.tableFooter()
        core.end()
        outFile.write(str(core))
            
        outFile.close()
    
    @staticmethod
    def printText(cols,rows,colListString,outFile):
        
        colListString = colListString.replace(',','\t|')
        colListString = colListString.replace('_','').upper()
        colListString = colListString.replace('"','')
        colListString = colListString.strip('|')
        outFile.write('#'+colListString+'\n')
        outFile.write('#'+'-'*100+'\n')
        
        if len(TrackFileImport3.SELECTED_FILES_INDEXES)>0:
           arr = TrackFileImport3.SELECTED_FILES_INDEXES
        else:
           arr = range(len(rows))
        for i in arr:
            row = rows[i]
            if row == None or len(row)<len(cols):
               continue
            #filename = row[0].split('/')[-1]
            line = ''
            
            for i in xrange(len(row)):
                line+= str(row[i])+'\t'
            line = line.strip('\t')
            #outFile.write(row[1]+'\t|'+row[0]+newLine)
            outFile.write(line+'\n')
            #outFile.write('-'*100+'\n')
            
        outFile.close()
    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''

        try:# The list will be 'None' when the page is initially loaded
            selected_attrs = 0
            for i in xrange(len(TrackFileImport3.ATTRIBUTES)):
                if not getattr(choices, 'valueList%s' % i) in\
                 [None,'','--Everything--']:
                      selected_attrs+=1
            
            if selected_attrs == 0:
               return 'You need to select at least one attribute'            
        except Exception as e:
            return str(e) + '--You need to select at least one attribute'

    #@staticmethod
    #def getSubToolClasses():
    #    '''
    #    Specifies a list of classes for subtools of the main tool. These
    #    subtools will be selectable from a selection box at the top of the page.
    #    The input boxes will change according to which subtool is selected.
    #    '''
    #    return None

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
    #    return ['source','search','dataType','cell','antibody','type']
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
    #@staticmethod
    #def getFullExampleURL():
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
        
        if choices.outFormat == 'Html':
           return 'customhtml'
        else: 
           return 'gtsuite'

    
#TrackFileImport3.DB.createTableFromList('temp',['attr'])
TrackFileImport3.setupVariableBoxFunctions()
