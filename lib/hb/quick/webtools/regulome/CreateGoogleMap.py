import os

from config.Config import MAPS_PATH
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.util.CommonFunctions import changedWorkingDir
from glob import glob
# This is a template prototyping GUI that comes together with a corresponding
# web page.

class CreateGoogleMap(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Create google map"

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
        return ['Select heatmap file', 'Select map id', 'Specify new mapId (no spaces)',  'Specify title', 'Specify google map folder name (no spaces)'] #Alternatively: [ ('box1','key1'), ('box2','key2') ]

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
        return '__history__', 'html'



    @staticmethod
    def getOptionsBox2(prevChoices):

        COMMON_MAPS_PATH = os.sep.join([MAPS_PATH, 'common'])
        resultList = ['-----  Select  -----', 'make new map id']

        with changedWorkingDir(COMMON_MAPS_PATH):
            resultList += sorted([v for v in glob('*') if v.find('.')<0])

        #return ['disease_tf_count', 'disease_tf_log', 'disease_tf_binary', 'disease_tf_count_noflanks', \
        #'tf_disease_count', 'tf_disease_log', 'tf_disease_binary', 'tf_disease_noflanks_count', \
        #'tf_barjoseph_disease_binary', 'tf_barjoseph_disease_1bpupstream_binary'] + ['tf_barjoseph_intogen_tissues_transcript_binary', 'tf_intogen_tissues_transcript_binary',
        #'tf_barjoseph_intogen_tumors_transcript_binary', 'tf_intogen_tumors_transcript_binary'] + ['tf_barjoseph_intogen_v1_tissues_transcript_binary', 'tf_intogen_v1_tissues_transcript_binary',
        #'tf_barjoseph_intogen_v1_tumors_transcript_binary', 'tf_intogen_v1_tumors_transcript_binary'] + ['tf_barjoseph_intogen_v2_tissues_transcript_binary', 'tf_intogen_v2_tissues_transcript_binary',
        #'tf_barjoseph_intogen_v2_tumors_transcript_binary', 'tf_intogen_v2_tumors_transcript_binary',
        #'tf_barjoseph_intogen_v2_tissues_copynumber_binary', 'tf_intogen_v2_tissues_copynumber_binary',
        #'tf_barjoseph_intogen_v2_tumors_copynumber_binary', 'tf_intogen_v2_tumors_copynumber_binary'] + ['tf_barjoseph_phenopedia_binary', 'tf_phenopedia_binary', 'tf_barjoseph_phenopedia_150_binary', 'tf_phenopedia_150_binary'] + ['disease_methylations_count', 'disease_mirna_count', 'disease_repeats_count', \
        #'histmod_disease_count', 'mirna_disease_count', 'repeats_disease_count'] + ['histone_tf_count', 'tf_histmod_count'] + ['go_tf_log', 'tf_geneontology_log', 'tf_geneontology_binary',
        #'tf_barjoseph_geneontology_1bpupstream_binary'] + ['tf_chrarms_count', 'histmod_chrarms_count', 'histmod_geneontology_count', 'gautvik', 'gautvik_least1000',
        #'gautvik_most1000', 'gautvik_mirna', '3d_lieberman', 'encode_gwas_vs_dhs', 'encode_tf_vs_tf', 'encode_gwas_vs_dhs', 'encode_tf_vs_tf']

        return resultList


    @staticmethod
    def getOptionsBox3(prevChoices):
        if prevChoices[-2] == 'make new map id':
            return ''

    @staticmethod
    def getOptionsBox4(prevChoices):
        return ''

    @staticmethod
    def getOptionsBox5(prevChoices):
        return ''

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

        from quick.application.GalaxyInterface import GalaxyInterface
        from proto.hyperbrowser.HtmlCore import HtmlCore

        print GalaxyInterface.getHtmlBeginForRuns(galaxyFn)
        print GalaxyInterface.getHtmlForToggles(withRunDescription=False)
        print str(HtmlCore().styleInfoBegin(styleClass='debug'))

        from quick.application.ExternalTrackManager import ExternalTrackManager
        datasetId = ExternalTrackManager.extractIdFromGalaxyFn(ExternalTrackManager.extractFnFromGalaxyTN(choices[0]))[1]
        #print datasetId
        #print choices

        ##batchid = index for kjoering i batch. Ikke-batch-kjoering: 0
        #batchid = 0

        ##mapId = Definer hva slags type innhold i Google map-bokser (naar du trykker). Innholdet er definert (hardkodet) i GoogleMapsInterface.py: getHtmlText() og getClusterHtmlText()
        ##Eks: encode_tf_vs_tf
        if choices[1] != 'make new map id':
            mapId = choices[1]
        else:
            mapId = choices[2]
            from quick.application.ExternalTrackManager import ExternalTrackManager
            histHtml = open(ExternalTrackManager.extractFnFromGalaxyTN(choices[0].split(':'))).read()

            #rowTrackName = histHtml.split('<h3>TRACK 1</h3>')[-1].split('</b>')[1].split('\n')[0].strip()#.split(':')
            #colTrackName = histHtml.split('<h3>TRACK 2</h3>')[-1].split('</b>')[1].split('\n')[0].strip()#.split(':')

            from quick.application.GalaxyInterface import GalaxyInterface

            batchLine = histHtml.split('<h3>CORRESPONDING BATCH COMMAND LINE</h3>')[-1].split('<p>')[1].split('/p')[0].strip()
            genome = histHtml.split('<h3>GENOME</h3>')[-1].split('name:</b>')[1].split('<')[0].strip()
            fullAccess = GalaxyInterface.userHasFullAccess(username)

            from quick.batch.BatchRunner import BatchRunner
            batchContents = BatchRunner.parseBatchLine(batchLine, genome, fullAccess)
            rowTrackName = ':'.join(batchContents.cleanedTrackName1)
            colTrackName = ':'.join(batchContents.cleanedTrackName2)

            from quick.extra.CreateGoogleMapType import createMapType
            createMapType(mapId, genome, rowTrackName, colTrackName, 'None', 'None', 'None')

            from config.Config import HB_SOURCE_CODE_BASE_DIR
            GMapInterfaceFn = HB_SOURCE_CODE_BASE_DIR+'/quick/extra/GoogleMapsInterface.py'
            GMapInterfaceContent = open(GMapInterfaceFn).read()
            replaceStr = "'%s', 'encode_gwas_vs_dhs'" % mapId
            GMapInterfaceContent = GMapInterfaceContent.replace("'encode_gwas_vs_dhs'", replaceStr)
            open(GMapInterfaceFn,'w').write(GMapInterfaceContent)

        #title = navn paa Regulomet slik brukeren ser det, Eks: "ENCODE test, TFs vs TFs"
        title = choices[3]

        ##name = navn paa katalog for google map: Eks: encode_test_tf_vs_tf
        name = choices[4]

        from quick.extra.CreateGoogleMap import GoogleMapCreator
        from quick.extra.GoogleMapsInterface import Map


        onMedSeqProd = False
        #batchid
        creator = GoogleMapCreator(name, datasetId, mapId, genome=genome)
        creator.tile(onMedSeqProd)
        creator.copyResultFiles()
        creator.createResultShelves()
        creator.createIndexFile(title, genome)
        creator.fixPermissions()

        print str(HtmlCore().styleInfoEnd())

        map = Map(name)

        row = []
        row.append( str(HtmlCore().link(map.getPrettyName(), map.getUrl())) )
        row.append( str(HtmlCore().link('Run description', map.getRunDescriptionUrl())) )
        row.append( str(HtmlCore().link('Counts', map.getCountUrl())) )
        row.append( str(HtmlCore().link('Effect size', map.getEffectSizeUrl())) )
        row.append( str(HtmlCore().link('P-values', map.getPvalUrl())) )

        core = HtmlCore()
        core.tableHeader(None)
        core.tableLine(row)
        core.tableFooter()

        print core
        print GalaxyInterface.getHtmlEndForRuns()

    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
       '''
        if choices[2] is not None and any(x in choices[2] for x in [' ', '\t']):
            return 'Whitespace is not allowed in mapId name.'

        if choices[4] is not None and any(x in choices[4] for x in [' ', '\t']):
            return 'Whitespace is not allowed in google map folder name.'

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
        return 'customhtml'
