import os
import tempfile
from collections import OrderedDict

from config.Config import DATA_FILES_PATH
from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
from quick.webtools.GeneralGuiTool import GeneralGuiTool

os.environ['HOME'] = "/tmp"

from gold.application.MatPlotLibSetup import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
import matplotlib.font_manager
from numpy import arange


#    



class MicroArrayBrowserTool(GeneralGuiTool):
    SHELVE_FN = DATA_FILES_PATH + os.sep + 'WordTrackDict.shelve'
    ave_names = {} # Array for average sample names
    y_values = []
    exons = []
    probesets = []
    samples = []
    transcript_id = ""
    gene_id = ""
    exp_str = "" # String with sample expression ids
    gene_start = 0
    gene_end = 0
    strand = 0
    chromosome = 0
    associated_gene_name = ""
    conn = None
    
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Browse microarray datasets"

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
        return ['Write gene search string', 'Select Gene of interest', 'Select dataset', 'Select meadian', 'Select transcript', 'Set expression string'] #Alternatively: [ ('box1','key1'), ('box2','key2') ]

    #@staticmethod
    #def getInputBoxOrder():
    #    '''
    #    Specifies the order in which the input boxes should be displayed, as a
    #    list. The input boxes are specified by index (starting with 1) or by
    #    key. If None, the order of the input boxes is in the order specified by
    #    getInputBoxNames.
    #    '''
    #    return None
    
    @classmethod
    def mysqlConnect(cls):
        import MySQLdb.cursors
        if not cls.conn:
            cls.conn = MySQLdb.connect (host = "127.0.0.1",
                                user = "microarray",
                                passwd = "k9f50",
                                db = "microarray",
                                cursorclass=MySQLdb.cursors.DictCursor)
        return cls.conn

    
    @classmethod
    def geneSearch(cls, search_string):        
        
#        conn = MySQLdb.connect (host = '127.0.0.1', #"invitro.titan.uio.no"
#                            user = 'microarray',
#                            passwd = 'k9f50',
#                            db = 'microarray',
#                            cursorclass=MySQLdb.cursors.DictCursor)

        conn = cls.mysqlConnect()
        cursor = conn.cursor()

        cursor.execute("call searchGene(%s)", (search_string));
        rows = cursor.fetchall()
        cursor.close()
        
        genes = []

        for row in rows:
            gene_id = row['gene_id']
            associated_gene_name = row['associated_gene_name']
            genes.append(' '.join([gene_id, associated_gene_name]))

        return genes

    
    @classmethod
    def getDataSets(cls, priv='0'):

        conn = cls.mysqlConnect()

        cursor = conn.cursor()

        cursor.execute("call getDataSets(%s)", (priv));
        rows = cursor.fetchall();
        cursor.close()

        dataSets = [];

        for row in rows:
            normalization_id = row['normalization_id'];
            name = row['name'];
            dataSets.append(': '.join([str(normalization_id), name]));

        return dataSets;

    
    @classmethod
    def getTranscriptList(cls, gene_id):

        conn = cls.mysqlConnect()

        cursor = conn.cursor()

        cursor.execute("call getGeneTranscripts(%s)", (gene_id))
        rows = cursor.fetchall()
        cursor.close()

        transcriptList = []

        for row in rows:
            transcript_id = row['transcript_id']
            transcriptList.append(transcript_id)
        return transcriptList

    
    @classmethod
    def getMedians(cls, priv='0'):

        conn = cls.mysqlConnect()

        cursor = conn.cursor()

        cursor.execute("call getDataSets(%s)", (priv))
        rows = cursor.fetchall()
        cursor.close()

        dataSets = []

        for row in rows:
            normalization_id = row['normalization_id']
            name = row['name']
            dataSets.append(': '.join([str(normalization_id), name]))

        return dataSets;

    
    @classmethod    
    def getOptionsBox1(cls): # Alternatively: getOptionsBoxKey1()
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
        return ''
    
    @classmethod     
    def getOptionsBox2(cls, prevChoices): # Alternatively: getOptionsBoxKey2()
        '''
        See getOptionsBox1().
        
        prevChoices is a namedtuple of selections made by the user in the
        previous input boxes (that is, a namedtuple containing only one element
        in this case). The elements can accessed either by index, e.g.
        prevChoices[0] for the result of input box 1, or by key, e.g.
        prevChoices.key (case 2).
        '''
        if prevChoices[0] not in [None, '']:
            geneList = cls.geneSearch(prevChoices[0])
            return ['-----  select  -----'] + geneList
        #if prevChoices[0]!='':
        #    path = EXT_ORIG_DATA_PATH+'/hg18/'
        #    result = []
        #    for root, folder, files in os.walk(path):
        #        if folder==[]:
        #            if root.find(prevChoices[0])>=0:
        #                result.append(root)
        #    
        #    return ('\n'.join(result), 40, True)
                        
            
            #return ['-----  select  -----','Gen1', 'Gen2']
    
    @classmethod    
    def getOptionsBox3(cls, prevChoices): # Alternatively: getOptionsBoxKey2()
        '''
        See getOptionsBox1().
        
        prevChoices is a namedtuple of selections made by the user in the
        previous input boxes (that is, a namedtuple containing only one element
        in this case). The elements can accessed either by index, e.g.
        prevChoices[0] for the result of input box 1, or by key, e.g.
        prevChoices.key (case 2).
        '''
        if prevChoices[1] not in [None,'-----  select  -----']:
            dataSets = cls.getDataSets()
            return ['-----  select  -----'] + dataSets
            #return OrderedDict(zip(dataSets, [False]*len(dataSets) ) )
            #return ['-----  select  -----','Dataset1', 'Dataset2','Dataset3']
    
    @classmethod  
    def getOptionsBox4(cls, prevChoices): # Alternatively: getOptionsBoxKey2()
        '''
        See getOptionsBox1().
        
        prevChoices is a namedtuple of selections made by the user in the
        previous input boxes (that is, a namedtuple containing only one element
        in this case). The elements can accessed either by index, e.g.
        prevChoices[0] for the result of input box 1, or by key, e.g.
        prevChoices.key (case 2).
        '''
        if prevChoices[2] not in [None, '-----  select  -----']:
            return ['-----  select  -----'] + cls.getMedians()
            #return ('__multihistory__' ,'bed','wig')#
    
    @classmethod  
    def getOptionsBox5(cls, prevChoices): # Alternatively: getOptionsBoxKey2()
        '''
        See getOptionsBox1().
        
        prevChoices is a namedtuple of selections made by the user in the
        previous input boxes (that is, a namedtuple containing only one element
        in this case). The elements can accessed either by index, e.g.
        prevChoices[0] for the result of input box 1, or by key, e.g.
        prevChoices.key (case 2).
        '''
        if prevChoices[2] not in [None, '-----  select  -----']:
            return [prevChoices[1]] + cls.getTranscriptList(prevChoices[1].split()[0])
            #return ('__multihistory__' ,'bed','wig')#

    @classmethod  
    def getOptionsBox6(cls, prevChoices): # Alternatively: getOptionsBoxKey2()
        import MySQLdb.cursors

        vals = []

        if prevChoices[2] not in [None, '-----  select  -----']:

            dataset_id = prevChoices[2].split(':')[0]

            conn = MySQLdb.connect (host = '127.0.0.1', #"invitro.titan.uio.no"
                                user = 'microarray',
                                passwd = 'k9f50',
                                db = 'microarray',
                                cursorclass=MySQLdb.cursors.DictCursor)
        
            cursor = conn.cursor()
            
            cursor.execute("call getNormalizationSamples(%s)", (dataset_id));

            rows = cursor.fetchall()
            cursor.close()

            for row in rows:
                sample_id=row['preprocessing_id'];
                sample_name=row['SAMPLE'];
                vals.append('%s: %s' % (sample_id, sample_name))

            
            return OrderedDict(zip(vals, [False]*len(vals) ) )
        
        return None
    
    
        
    #@staticmethod    
    #def getOptionsBox3(prevChoices):
    #    return ['']

    #@staticmethod    
    #def getOptionsBox4(prevChoices):
    #    return ['']

    #@staticmethod
    #def getDemoSelections():
    #    return ['testChoice1','..']
        
    @classmethod     
    def execute(cls, choices, galaxyFn=None, username=''):
	
	
	
	htmlStr = '''
	<script type="text/javascript" src="https://www.google.com/jsapi"></script>
	<script type="text/javascript">
        google.load("visualization", "1.1", {packages:["corechart", "controls"]});
        
    function makeGooglePlot(){
	var data = %s;
        var dEntry = google.visualization.arrayToDataTable(data);
        
        var dashboard = new google.visualization.Dashboard(
             document.getElementById('dashboard'));
      
         var control = new google.visualization.ControlWrapper({
           'controlType': 'ChartRangeFilter',
           'containerId': 'control',
           'options': {
             // Filter by the date axis.
             'filterColumnIndex': 0,
             'ui': {
               'chartType': 'LineChart',
               'chartOptions': {
                 'chartArea': {'width': '80%%'},
                 
               },
               'chartView': {
                 'columns': %s
               }
             }
           }
         });
      
         var chart = new google.visualization.ChartWrapper({
           'chartType': 'LineChart',
           'containerId': 'chart',
           'options': {
             // Use the same chart area width as the control for axis alignment.
             'chartArea': {'height': '80%%', 'width': '80%%'},
             'legend': {'position': 'right'},
             'title': 'Gene: %s',
             'hAxis': {'title': 'Exon number'},
             'vAxis': {'title': 'Expression value(log2)'}
           }
         });
         
         dashboard.bind(control, chart);
         dashboard.draw(dEntry);
      }

      google.setOnLoadCallback(makeGooglePlot);
    </script>
	
	<div id="dashboard" style="width: 1000px; height: 700px;"><div id="chart" style="width: 100%%; height: 500px;"></div><div id="control" style="width: 100%%; height: 50px;"></div> </div>

	'''
	
        
        cls.gene_id = choices[1].split()[0]
        cls.transcript_id = choices[4] if choices[4].startswith('ENST') else '0'
        cls.median_id = choices[3].split(':')[0] if not choices[3].startswith('-----') else '0' # Used if median value is sent to the script.
        # The median of all samples in the selected data set will then be included in the plot.
        #print choices[-1]
        cls.exp_str = '-'.join([k.split(':')[0] for k, v in choices[-1].items() if v])
        #s = exp_str.split('-')
        #for item in s:
        #    if "(" in item and ")" in item:
        #        ms=item[item.find("(")+1:item.find(")")]
        #        ave_names[item[0:item.find("(")]] = ms
        #cls.exp_str = re.sub("\((.*?)\)", "", exp_str) # remove average-names.
        
        cls.getGeneInfo();
        cls.getArrayData();

        strList = ["x"]+[k.split(':')[1] for k, v in choices[-1].items() if v]

        if (cls.median_id != "0" and len(cls.y_values[0]) > 0):
            cls.getMedianData();	    
            strList += [choices[3].split(':')[1]]
            
	tab = [[i+1]+list(k) for i, k in enumerate(zip(*cls.y_values))]
	tab.insert(0,strList)
	
	print htmlStr % (repr(tab), repr(range(len(tab[1]))), choices[1])
	
	#cls.buildfigure(galaxyFn);

    
    
    @classmethod
    def getGeneInfo(cls):
    
        conn = cls.mysqlConnect()
    
        cursor = conn.cursor()
    
        cursor.execute("call getGeneInfo(%s)", (cls.gene_id));
    
        rows = cursor.fetchall()
    
        for row in rows:
            cls.associated_gene_name = row['associated_gene_name']
    
        cursor.close()
    
    @classmethod
    def getArrayData(cls):

        
        conn = cls.mysqlConnect()
        
        cursor = conn.cursor()
    
        cls.exp_str = cls.exp_str.replace('-', ';');
    
        if cls.transcript_id == "0":
	    #print 'hei, hei', cls.gene_id, cls.exp_str
            cursor.execute("call getGeneValues(%s, %s, %s)", (cls.gene_id, cls.exp_str, 2));
        else:
	    #print 'hei, heia', cls.transcript_id, cls.exp_str
            cursor.execute("call getTranscriptValues(%s, %s, %s)", (cls.transcript_id, cls.exp_str, 2));
    
    
        rows = cursor.fetchall()
    
        y_value = []
        cnter = 0;
        i = 0;
        for row in rows:
	    #print row
            cls.chromosome = row['chromosome']
            cls.strand = row['strand']
            val = row['val']
            if cls.strand == -1:
                ex_start = row['g_stop'] + row['g_start'] - row['ex_start'];
            else:
                ex_start = row['ex_start'];
            exon_id = row['exon_id']
            probeset_id = row['probeset_id']
            sample = row['samples']
            if (cnter != row['allcnter'] and i > 0): # New sample coming up, record what we got so far.
                cls.y_values.append(y_value)
                y_value = []
            if (cnter != row['allcnter']):
                if row['pre'] in cls.ave_names:
                    cls.samples.append(cls.ave_names[row['pre']][:10])
                else:
                    cls.samples.append(sample[:15])
                cls.gene_start = row['g_start'];
                cls.gene_end = row['g_stop'];
            cnter = row['allcnter']
            if (cnter == 1):
                cls.exons.append(exon_id)
                cls.probesets.append(probeset_id)
            y_value.append(val)
            i = i + 1;

        cls.y_values.append(y_value)
    
        cursor.close()
        #print cls.y_values
    
    
    @classmethod
    def getMedianData(cls):
        conn = cls.mysqlConnect()
    
        cursor = conn.cursor()
    
        if (cls.median_id == "61" or cls.median_id == "62"):
            orig_median = 6;
        else:
            orig_median = cls.median_id;
    
        if cls.transcript_id == "0":
            #print cls.gene_id, cls.median_id, orig_median
            cursor.execute("call getGeneMedian(%s, %s, %s, %s)", (cls.gene_id, cls.median_id, orig_median, 2));
        else:
            cursor.execute("call getTranscriptMedian(%s, %s, %s, %s)", (cls.transcript_id, cls.median_id, orig_median, 2));
    
        rows = cursor.fetchall()
    
        y_value = []
        cnter = 0;
        i = 0;
        for row in rows:
            #print row
            cls.strand = row['strand']
            val = row['val']
            if cls.strand == -1:
                ex_start = row['g_stop'] + row['g_start'] - row['ex_start'];
            else:
                ex_start = row['ex_start'];
            cls.gene_start = row['g_start'];
            cls.gene_end = row['g_stop'];
            y_value.append(val)
            i = i + 1;
    
        if len(y_value) > 0:
            cls.samples.append('Median')
            cls.y_values.append(y_value)
    
        cursor.close()


    
    
    @classmethod
    def buildfigure(cls):
        
        fig = Figure(figsize=(10, 6))
        
        uniform_x_values = arange(len(cls.y_values[0]));
        lines = 0;
    
        ax = fig.add_axes([0.028, 0.311, 0.75, 0.65]) # Create axes for plot
    
        if (len(uniform_x_values) > 0):
    
            colors = ["r-", "k-", "b-", "g-", "c-", "m-", "y-"];
    
            ax2 = ax.twinx() # To get vertical axes on both sides.
            # Needed for showing coverage and array units on different axes.
    
            ax2.yaxis.set_ticks_position("left")
    #        ax.yaxis.set_ticks_position("right")
    
            for t in ax2.get_yticklabels():
                t.set_fontsize(6)
    
            for item in cls.y_values:
                ind = lines%7;
                #print len(uniform_x_values), len(item)
                line = ax2.plot(uniform_x_values, item, '0.4', markersize=2, markerfacecolor='g',label=cls.samples[lines], linewidth=0.8, zorder=2)
                lines = lines + 1;
    
            prop = matplotlib.font_manager.FontProperties(size=6)
    
            if (cls.transcript_id == "0"):
                ax.set_title(cls.associated_gene_name + " / " + cls.gene_id, fontsize=8);
            else:
                ax.set_title(cls.transcript_id, fontsize=8);
    
            ax2.yaxis.grid(True);
    
            ax2.axis([uniform_x_values[0], uniform_x_values[len(uniform_x_values)-1], 0, 15])
            ax.set_yticklabels([])
    
            ax.xaxis.tick_bottom()
            ax.set_xticks( uniform_x_values ) #set these the same as x input into plot
    
            exons_no = range(1, len(cls.exons)+1)
    
            for i in range(0, len(cls.exons)):
                cls.probesets[i] = str(cls.probesets[i]) + " / " + cls.exons[i]
                labels = ax.set_xticklabels(cls.probesets)
                for label in labels:
                    label.set_rotation(90)
                    label.set_fontsize(6)
    
            for t in ax.get_yticklabels():
                t.set_fontsize(6)
            
        else: # Give explanation if no data is present in the database.
            ax.text(0.1, 0.8,'Currently no microarray data\navailable for ' + gene_id,
            size='9',
            horizontalalignment = 'left',
            verticalalignment   = 'top',
            multialignment      = 'center')
            ax.axis('off')
    
        canvas = FigureCanvasAgg(fig)
    
        tempfilenum,tempfilename=tempfile.mkstemp(suffix='.png') #function print_figure below requires a suffix
        canvas.print_figure(tempfilename, dpi=150)
        imageFile = GalaxyRunSpecificFile(['Image', 'resultImage.png'], galaxyFn)
        #magefile=file(tempfilename,'rb')
        #print "Content-type: image/png\n"
        #imagefile.seek(0)
        #print imagefile.read()
        fig.savefig(imageFile.getDiskPath(ensurePath=True))
        #fig.savefig(sys.stdout)
    
        #imageFile.close()
        print '<img src="%s">' % (imageFile.getURL())
    
    
    @classmethod 
    def validateAndReturnErrors(cls, choices):
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
