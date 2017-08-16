from quick.webtools.GeneralGuiTool import GeneralGuiTool
from collections import OrderedDict


# This is a template prototyping GUI that comes together with a corresponding
# web page.

class GTSuiteFormatError(Exception):
      pass
class GTSuite(object):
      def __init__(self, gtsFile):
          self._file = gtsFile
          self._dataset = None
          self._attributes = None
          
      #-------------------------------------------------------------------------    
      def makeDataset(self):
          
          #try:
            self._dataset = []
            with open(self._file,'r') as f:
               lines = f.readlines()
            if not (lines[0].startswith('#') and lines[1].startswith('#')):
               raise GTSuiteFormatError('GTrack-Suite format miss-match')
            self._attributes =\
             lines[0].strip('#').strip('\n').strip().strip('\t').lower().split('\t|')
            if '' in self._attributes:
               self._attributes.remove('')
            for l in lines[2:]:
                row = l.split('\t')
                rowDict = {}
                i = 0
                for el in row:
                    rowDict.update({self._attributes[i]:el.strip('\n')})
                    i +=1
                #rowDict.update({'filename':row['url'].split('/')[-1]})
                self._dataset.append(rowDict)
          #except:
          #  raise GTSuiteFormatError('GTrack-Suite format miss-match')      
      #-------------------------------------------------------------------------    
      def getAttributes(self):
          return self._attributes
      #-------------------------------------------------------------------------        
      def getTrackFileNames(self):
          names = []
          for rowDict in self._dataset:
              names.append(rowDict['url'].split('/')[-1])
          return names
      #-------------------------------------------------------------------------    
      def getAttributesString(self,List):
          string = ''
          for a in List:
              string += str(a)+',' 
          return string    
      #-------------------------------------------------------------------------    
      def filterOutAttributes(self, filterOutList):
          for attr in filterOutList:
              if attr in self._attributes:
                 self._attributes.remove(attr)
      #-------------------------------------------------------------------------    
      def filterOutRows(self, filenameList):
          for filename in filenameList:
              for rowDict in self._dataset:
                  if rowDict['url'].find(filename) > -1:
                     self._dataset.remove(rowDict)
                     break
      #-------------------------------------------------------------------------    
      def getDatasetString(self):
          string = '#'
          for a in self._attributes:
              string += a.upper() + '\t|'
          string += '\n' +'#'+'-'*100+'\n'
          
          for rowDict in self._dataset:
              rowstr = ''
              for k in self._attributes:
                  rowstr += rowDict[k] + '\t'
              string += rowstr.strip('\t') + '\n'
                  
          return string
##############################################################################
class TrackDownload(GeneralGuiTool):
    #OUTPUT_FORMAT = 'gtsuite'
        
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "GSuite Manager"

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

        Note: the key has to be camelCase (e.g. "firstKey")
        '''
        return [('GTrackSuite File:', 'gts'),('Operation:', 'operation'),\
        ('Select Rows','selectRows'),('Select Attributes','selectAttributes')]#+\
        #[('Variable input box ' + str(i), 'variable' + str(i))\
        #         for i in xrange(TestTool1. MAX_INPUT_BOXES)]
        

    
    #@classmethod
    #def setupVariableBoxFunctions(cls):
    #    for i in xrange(cls.MAX_INPUT_BOXES):
    #        setattr(cls, 'getOptionsBoxVariable%s' % i,\
    #         partial(cls._getVariableBox, index=i))
    
    #@classmethod
    #def _getVariableBox(cls, prevChoices, index):
    #       if index > 12:
    #          return
    #       return ['Choice 1 for variable %s' %index,\
    #               'Choice 2 for variable %s' %index]         
    
    @staticmethod
    def getOptionsBoxGts(): # Must have this name ('getOptionsBoxFirst' +
    
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
        - The contents is the default value shown inside the text area
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
        return '__history__','gtsuite'

    @staticmethod
    def getOptionsBoxOperation(prevChoices):
        '''
        See getOptionsBoxFirstKey().

        prevChoices is a namedtuple of selections made by the user in the
        previous input boxes (that is, a namedtuple containing only one element
        in this case). The elements can accessed either by index, e.g.
        prevChoices[0] for the result of input box 1, or by key, e.g.
        prevChoices.key (case 2).
        '''
        if prevChoices.gts != None:
           return ['Download Files','Select Rows','Select Attributes']

    @staticmethod
    def getOptionsBoxSelectRows(prevChoices):
        if prevChoices.operation == 'Select Rows':
           gtsFile = prevChoices.gts.split(':')[2]
           gts = GTSuite(gtsFile)
           gts.makeDataset()
           return OrderedDict([(x,True) for x in gts.getTrackFileNames()])   
        
    @staticmethod
    def getOptionsBoxSelectAttributes(prevChoices):
        if prevChoices.operation == 'Select Attributes':
           gtsFile = prevChoices.gts.split(':')[2]
           gts = GTSuite(gtsFile)
           gts.makeDataset()
           return OrderedDict([(x,True) for x in gts.getAttributes()])
    
    @classmethod
    def execute(cls,choices, galaxyFn=None, username=''):
        '''
        Is called when execute-button is pushed by web-user. Should print
        output as HTML to standard out, which will be directed to a results page
        in Galaxy history. If getOutputFormat is anything else than HTML, the
        output should be written to the file with path galaxyFn. If needed,
        StaticFile can be used to get a path where additional files can be put
        (e.g. generated image files). choices is a list of selections made by
        web-user in each options box.
        '''
        
        gtsFile = choices.gts.split(':')[2]
        gts = GTSuite(gtsFile)
        gts.makeDataset()
        filterOutList = []
        with open(galaxyFn, 'w') as outFile:
          #outFile.write('START:\n')   
          if choices.operation == 'Select Attributes':
             filterOutList=[x for x,add in choices.selectAttributes.iteritems()\
              if not add]
             gts.filterOutAttributes(filterOutList)
             outFile.write(gts.getDatasetString())
          elif choices.operation == 'Select Rows':
             filterOutList=[x for x,add in choices.selectRows.iteritems() if not add]
             gts.filterOutRows(filterOutList)
             outFile.write(gts.getDatasetString())
          else:
             cls.OUTPUT_FORMAT = 'txt'
             import ftplib, os, tarfile
             for rowDict in gts._dataset:
                url = rowDict['url']    
                sitename = url.split(':')[1].strip('/').split('/')[0]
                filename = url.split('/')[-1]
                filepath = url.split(sitename)[1]
                fileExt = filename.strip(filename.split('.')[0])
                if url.find('Epigenome') > -1:
                  try:
                    conn = ftplib.FTP(sitename)
                    conn.login('anonymous')
                    
                    f =  open(cls.makeHistElement(galaxyExt=fileExt.split('gz'),\
                    title=str(filename)), 'w')
                    localFPath = os.path.abspath(f.name) 
                    conn.retrbinary('RETR ' + filepath, f.write, 1024)
                    conn.quit()
                    f.close()
                    outFile.write('Downloaded file <'+filename+'> to history\n')
                  except Exception as e:
                    outFile.write('Error downloading file <'+filename+'>:\n')
                    outFile.write(str(e)+'\n')
                else:
                  try:  
                    
                    rsyncURL = 'rsync://' + sitename + filepath
                    import subprocess
                    subprocess.call(['rsync', '-a', '-P', rsyncURL,os.path.abspath(cls.makeHistElement(galaxyExt=fileExt.split('gz'), title=str(filename)))])
                    outFile.write('Downloaded file <'+filename+'> to history\n')
                  except Exception as e:
                    outFile.write('Error downloading file <'+filename+'>:\n')
                    outFile.write(str(e)+'\n')
            #outFile.write(gts.getAttributesString(gts.getAttributes()))           
          
             
    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        
        '''
        if choices.gts == None:
           return 'You must select a GTrack Suite file'
        #try:
        #    int(choices.firstNumber)
        #    int(choices.secondNumber)
        #except:
        #    return 'The The two numbers must be integers'

        


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
    #    '''
    #    Specifies whether the tool is accessible to all users. If False, the
    #    tool is only accessible to a restricted set of users as defined in
    #    LocalOSConfig.py.
    #    '''
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
    @classmethod
    def getOutputFormat(cls,choices):
        if choices.operation == 'Download Files':
           return 'txt'
        else:
           return 'gtsuite'     
