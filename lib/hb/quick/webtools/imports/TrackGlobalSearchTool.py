from collections import OrderedDict, namedtuple
from unidecode import unidecode

import gold.gsuite.GSuiteComposer as GSuiteComposer
import quick.gsuite.GSuiteHbIntegration
import quick.gsuite.GSuiteUtils as GSuiteUtils
from gold.gsuite.GSuitePreprocessor import GSuitePreprocessor
from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.trackaccess.TrackGlobalSearchModule import TrackGlobalSearchModule
from quick.webtools.GeneralGuiTool import GeneralGuiTool

from quick.extra.ProgressViewer import ProgressViewer
from quick.trackaccess.TrackGlobalSearchModule import TrackGlobalSearchModule
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.gsuite.GSuiteHbIntegration import getGSuiteHistoryOutputName

VocabularyElement = namedtuple('VocabularyElement', ('category', 'subCategory','sourceTool','sourceTable','toolAttr','toolVal'))

class TrackGlobalSearchTool(GeneralGuiTool):
    RESULT_COLS = ['hb_datatype','hb_cell_tissue_type','hb_target','hb_genomebuild','hb_filesuffix']
    RESULT_COLS_HEADER = ['Type of data','Cell/Tissue type','Target','Genome build','File suffix']

    def __new__(cls, *args, **kwArgs):
        cls.exception = None
        cls.useSqlite = True
        #cls.remoteGSuite = None

        return GeneralGuiTool.__new__(cls, *args, **kwArgs)

    @staticmethod
    def getToolName():
        return 'Create a GSuite from an integrated catalog of genomic datasets (track selection by data-type)'        

    @staticmethod
    def getInputBoxNames():
        #return ['Search Type:','Search:','Sub-Category:','Select Source:','URL:', '']
        return [#('Search Type:','searchType'),\
                ('', 'basicQuestionId'),\
                ('Select track category','search'),\
                ('Select track sub-category','subCategory'),\
                ('Select database','source'),\
                ('<b>Transfer selection to advanced mode for further fine-tuning?</b>', 'transfer'),\
                ('Transfer URL','testURL'),\
                ('Select File Type:','filetype'),\
                ('<h3>Select type of data</h3>', 'dataType'),\
                ('','dataInfo'),\
                ('<b>Limit selection of tracks?</b>','outputType'),\
                ('Download and preprocess? (temporary)', 'downloadAndPreprocess'),\
                ('Select genome (temporary):', 'genome'),\
                #('<b>Redirect URL</b>', 'url'),\
                #('<h3>Manually Select Among Matching Tracks</h3>','showResults'),\
                ('<h3>Matching Tracks</h3>','results'),\
                ('<h3>Results</h3>','resultsTable'),\
                ('','historyElementsInfo')]

    #@classmethod
    #def getOptionsBoxSearchType(cls):
    #    #return OrderedDict([(str(t),False) for t in cls.VOCABULARY])
    #    return ['Categorized','Text']

    @classmethod
    def getOptionsBoxBasicQuestionId(cls):
        return '__hidden__', None

    @classmethod
    def getOptionsBoxSearch(cls, prevChoices):

        
        gsm = TrackGlobalSearchModule(cls.useSqlite)
        return ['--Select--'] + gsm.getCategories()

    #@classmethod
    #def getInfoForOptionsBoxSearch(cls, prevChoices):
    #    if prevChoices.searchType == 'Text':
    #        return 'Enter search keys and values separated by "&", e.g.\n'+\
    #    'Histone modifications=H2AK5ac & Open Chromatin=Dnase HSS'
    #    else:
    #        return

    @classmethod
    def getOptionsBoxSubCategory(cls, prevChoices):

        if prevChoices.search == '--Select--':
            return
        gsm = TrackGlobalSearchModule(cls.useSqlite)
        return ['--Select--'] + gsm.getSubCategories(prevChoices.search)

    @classmethod
    def getOptionsBoxSource(cls, prevChoices):

        if prevChoices.subCategory in [None,'--Select--']:
            return
        gsm = TrackGlobalSearchModule(cls.useSqlite)
        items = gsm.getItems(prevChoices.search,prevChoices.subCategory)
        ##return [str(item) for item in items]
        
        sourceTupleList = gsm.getDataSources(items)
        sourceList = []
        countAll = 0
        for src,count in sourceTupleList:
            sourceList.append(src+' ['+str(count)+' files found]')
            countAll += count
        
        if len(sourceList) > 1:
            sourceList.insert(0, 'All databases ['+str(countAll)+' files found]')
        
        ##Asked to be removed by Sveinung. Commenting it out (maybe it will be reused later)
        # HBGsuite = quick.gsuite.GSuiteHbIntegration.getSubtracksAsGSuite('hg19', ['Sample data', 'Chromatin catalog', prevChoices.search, prevChoices.subCategory])
        # if HBGsuite.numTracks() > 0:
        #     sourceList.append('HyperBrowser['+str(HBGsuite.numTracks())+']')
        
        return sourceList

    # @classmethod
    # def getInfoForOptionsBoxSource(cls, prevChoices):
    #     return "The provided file types are: 'tsv','broadPeak','narrowPeak', and 'bed'."\
    #         " So any difference in the number of tracks between this source list and"\
    #         " the 'what to do?' list below, is due to the fact that some track"\
    #         " file types are not currently supported"
        
    @classmethod
    def getOptionsBoxTransfer(cls, prevChoices):
        if not prevChoices.source or 'All' in prevChoices.source or 'HyperBrowser' in prevChoices.source:
            return
        return ['No','Yes']
    
    @classmethod
    def getOptionsBoxTestURL(cls, prevChoices):
        pass
        ##important for testing (DON'T REMOVE):
        # if prevChoices.transfer == 'Yes':
        #      gsm = TrackGlobalSearchModule(cls.useSqlite)
        #      sourceTool,attr_val_dict = gsm.getSourceToolURLParams(prevChoices.search,\
        #                                                  prevChoices.subCategory,\
        #                                                  prevChoices.source.split('[')[0].strip())
        #
        #      return '__rawstr__','Source tool: '+str(sourceTool)+'<br> Attribute-value Dict: '+str(attr_val_dict)+\
        #      '<br>URL: ' + str(cls.createGenericGuiToolURL('hb_track_source_test_tool', sourceTool,attr_val_dict))

    @classmethod
    def getOptionsBoxDataType(cls, prevChoices):
        
        if not prevChoices.source or prevChoices.source.find('HyperBrowser') > -1 or prevChoices.transfer == 'Yes':
            return
        gsm = TrackGlobalSearchModule(cls.useSqlite)
        items = gsm.getItems(prevChoices.search, prevChoices.subCategory)
        source = prevChoices.source.split('[')[0].strip()
        datatypes = gsm.getDataTypes(items,source)
        countAll = 0
        for dt,count in datatypes.iteritems():
            countAll += count
        ##Change requested by Sveinung for simplicity
        #return OrderedDict([(dataType + ' ['+str(count)+']',True) for dataType,count in datatypes.iteritems()])

        #return ['All data types ['+str(countAll)+' files found]'] + \
        return [dataType + ' ['+str(count)+' files found]' for dataType,count in datatypes.iteritems()]

    @classmethod
    def getOptionsBoxDataInfo(cls,prevChoices):
        if not prevChoices.dataType:
            return
        string = '<div style="border:1px dashed black; border-radius: 10px;'+\
        ' background-color: #E5E4E2; margin-left: 20px;'+\
        ' margin-right: 20px; padding-bottom: 8px; padding-left: 8px;'+\
        ' padding-right: 8px; padding-top: 8px;">'+\
        'To be edited by Sveinung'
        return '__rawstr__', string


    
    @classmethod
    def getOptionsBoxFiletype(cls, prevChoices):

        return
        # if not prevChoices.source or prevChoices.source.find('HyperBrowser') > -1 or prevChoices.transfer == 'Yes':
        #     return
        # gsm = TrackGlobalSearchModule(cls.useSqlite)
        # items = gsm.getItems(prevChoices.search, prevChoices.subCategory)
        # source = prevChoices.source.split('[')[0].strip()
        # result = gsm.getFileTypes(items,source)
        #
        # filteredResult = result
        # return OrderedDict([(el.split('[')[0],True) for el in filteredResult])
        
        #Hard-coded way for filtering with specific filetypes#
        # filteredResult = []
        # for el in result:
        #     if el.split('[')[0] in ['tsv','broadPeak','narrowPeak','bed']:
        #         filteredResult.append(el)


        #Skip showing the filetype count for now (problems, e.g. 'bam' and 'bai')
        #return OrderedDict([(el,True) for el in filteredResult])
        
        #return OrderedDict([(el,True) for el in result])

    @classmethod
    def getOptionsBoxOutputType(cls, prevChoices):
        #if prevChoices.source.find('HyperBrowser') > -1:
        #    return
        if not prevChoices.source or prevChoices.transfer == 'Yes' or prevChoices.source.find('HyperBrowser') == -1 \
        and not prevChoices.dataType:
        #and len([x for x,selected in prevChoices.dataType.iteritems() if selected]) == 0:
           return
        
        gsm = TrackGlobalSearchModule(cls.useSqlite)
        source = prevChoices.source.split('[')[0].strip()
        if prevChoices.source.find('HyperBrowser') > -1:
            #fileTypes = []
            dataTypes = []
        else:
            #fileTypes = [x.split('[')[0] for x,selected in prevChoices.filetype.iteritems() if selected]
            #dataTypes = [x.split('[')[0].strip() for x,selected in prevChoices.dataType.iteritems() if selected]
            dataTypes = [prevChoices.dataType.split('[')[0].strip()]

        count = gsm.getGSuite(prevChoices.search,prevChoices.subCategory,source,dataTypes,filterFileSuffix = True).numTracks()
                
        choicesList =  ['Keep all tracks as selected above ['+str(count)+']','Select tracks manually']
        ##if prevChoices.source.find('HyperBrowser') == -1:
        choicesList.extend(['Select 10 random tracks','Select 50 random tracks'])
        # # if gsm.dataSourceExists(source):
        # #     choicesList.append('Transfer selection to advanced mode for further fine-tuning')

        return choicesList

    @classmethod
    def getOptionsBoxDownloadAndPreprocess(cls, prevChoices):
        #if prevChoices.searchType != 'Categorized Search for Tracks':
        #    return
        return '__hidden__','Yes'
        # if not prevChoices.source or prevChoices.transfer == 'Yes':
        #     return
        # return ['Yes','No']

    @classmethod
    def getOptionsBoxGenome(cls, prevChoices):
        #if prevChoices.source.find('HyperBrowser') > -1:
        #    return
        #if prevChoices.downloadAndPreprocess == 'Yes':
        
        #return '__genome__'
        return '__hidden__','hg19'

    #@classmethod
    #def getOptionsBoxShowResults(cls, prevChoices):
    #    if prevChoices.source.find('HyperBrowser') > -1:
    #        return
    #    if len([x for x,selected in prevChoices.filetype.iteritems() if selected]) == 0:
    #       return
    #    else:
    #       return ['No','Yes']

    @classmethod
    def getOptionsBoxResults(cls, prevChoices):
        #if prevChoices.source.find('HyperBrowser') > -1:
        #    return
        #if prevChoices.showResults in [None,'No']:
        #   return
        if not prevChoices.source or prevChoices.transfer == 'Yes' or prevChoices.outputType != 'Select tracks manually':
            return
        gsm = TrackGlobalSearchModule(cls.useSqlite)
        if prevChoices.source.find('HyperBrowser') > -1:
            return gsm.getTrackFileList(prevChoices.search, prevChoices.subCategory, 'HyperBrowser')
        else:
            source = prevChoices.source.split('[')[0].strip()
            # # allFileTypes = [x.split('[')[0] for x,selected in prevChoices.filetype.iteritems()]
            # # fileTypes = [x.split('[')[0] for x,selected in prevChoices.filetype.iteritems() if selected]
            ##allDataTypes = [x.split('[')[0].strip() for x,selected in prevChoices.dataType.iteritems()]
            #dataTypes = [x.split('[')[0].strip() for x,selected in prevChoices.dataType.iteritems() if selected]
            dataTypes = [prevChoices.dataType.split('[')[0].strip()]
            
            ##Was made to speadup so that there will be no filetype comparisons,
            ##but deactivated for now since there is hardcoded filtering in
            ##prevChoices.fileType
            #if len(allFileTypes) == len(fileTypes):
            #    fileTypes = []
            
            #return '__rawStr__',gsm.getTrackFileList(prevChoices.search, prevChoices.subCategory,source,dataTypes)
            return gsm.getTrackFileList(prevChoices.search, prevChoices.subCategory,source,dataTypes)
            
        #items = gsm.getItems(prevChoices.search, prevChoices.subCategory)
    
    #@classmethod
    #def getOptionsBoxUrl(cls, prevChoices):
    #    gsm = TrackGlobalSearchModule(cls.useSqlite)
    #    sourceTool,attr_val_dict = gsm.getSourceToolURLParams(prevChoices.search,\
    #                                                    prevChoices.subCategory,\
    #                                                    prevChoices.source.split('[')[0].strip())
    #    #attr_val_dict = {}
    #    #i = 0
    #    #attr_val_dict['attributeList'+str(i)] = 'Table Name'
    #    #attr_val_dict['multiSelect'+str(i)] = 'Text Search'
    #    ##attr_val_dict['valueList'+str(i)] = hit.toolVal
    #    #attr_val_dict['multiValueReceiver'+str(i)] = 'wgEncodeBroadHistone.*H3k0?9ac.*'
    #    return cls.createGenericGuiToolURL('hb_track_source_test_tool',\
    #                                           sourceTool,attr_val_dict)

    @classmethod
    def getOptionsBoxResultsTable(cls, prevChoices):#To display results in HTML table

        if not prevChoices.source or prevChoices.transfer == 'Yes' or prevChoices.source.find('HyperBrowser') == -1 \
        and not prevChoices.dataType:
        #and len([x for x,selected in prevChoices.dataType.iteritems() if selected]) == 0:
           return

        gsm = TrackGlobalSearchModule(cls.useSqlite)
        source = prevChoices.source.split('[')[0].strip()
        #dataTypes = [x.split('[')[0].strip() for x,selected in prevChoices.dataType.iteritems() if selected]
        dataTypes = [prevChoices.dataType.split('[')[0].strip()]
        rowDicts = None
        if prevChoices.outputType in [None,'select 10 random tracks','select 50 random tracks']:
            return
        elif 'all tracks' in prevChoices.outputType:
                rowDicts = gsm.getRowsDicts(prevChoices.search,prevChoices.subCategory,source,dataTypes,\
                                            filterFileSuffix = True)
        elif prevChoices.outputType == 'Select tracks manually':
                rowDicts = gsm.getRowsDicts(prevChoices.search,prevChoices.subCategory,source,dataTypes,\
                                            selectedFileIDs = prevChoices.results, filterFileSuffix = True)

        htmlTableDict = {}
        if rowDicts:
            for row in rowDicts:
                if 'url' in row:
                    filename = row['url'].split('/')[-1]
                elif 'uri' in row:
                    filename = row['uri'].split('/')[-1]
                elif '_url' in row:
                    filename = row['_url'].split('/')[-1]
                else:
                    filename = '<No filename>'
                rowList = []
                for attr in cls.RESULT_COLS:
                    if attr in row:
                        rowList.append(unicode(row[attr]))

                htmlTableDict[filename] = rowList

        if len(htmlTableDict) == 0:
            return
        html = HtmlCore()
        html.tableFromDictionary(htmlTableDict, columnNames = ['File name'] + cls.RESULT_COLS_HEADER,\
                                 tableId='t1', expandable=True)

        return '__rawstr__', unicode(html)

    @classmethod
    def getOptionsBoxHistoryElementsInfo(cls,prevChoices):
        if not prevChoices.dataType:
            return

        desc = prevChoices.subCategory

        core = HtmlCore()
        core.styleInfoBegin(styleClass='infomessagesmall')
        core.paragraph('This tool will create seven history elements (one of which is hidden):')
        descriptionList = \
            [('%s' % getGSuiteHistoryOutputName('storage', desc),
              'hidden history element containing the actual downloaded track data. Should '
              'in most cases be ignored'),
             ('%s' % getGSuiteHistoryOutputName('preprocessed', desc),
              'use this in the analysis tool of choice'),
             ('%s' % getGSuiteHistoryOutputName('nopreprocessed', desc),
              'preprocessing fails due to some issues with the track data. Some '
              'manipulation is probably needed before one tries preprocessing again'),
             ('%s' % getGSuiteHistoryOutputName('primary', desc),
              'use this if you need to manipulate the raw track data using a manipulation '
              'tool. The GSuite resulting from manipulation needs to be preprocessed '
              'before analysis'),
             ('%s' % getGSuiteHistoryOutputName('nodownload', desc),
              'in some cases the downloading of tracks fails, but might work if one tries again'),
             ('%s' % getGSuiteHistoryOutputName('remote', desc),
              'this refers to the original files available at a remote server. Use this '
              'if one for some reason needs to re-download all the tracks'),
             ('%s' % getGSuiteHistoryOutputName('progress', desc),
              'click the eye icon of this element to show the progress of the import')]
        for label, description in descriptionList:
            core.descriptionLine(label, description)
        core.styleInfoEnd()

        return '__rawstr__', unicode(core)

    @classmethod
    def getExtraHistElements(cls, choices):
        from gold.gsuite.GSuiteConstants import GSUITE_SUFFIX, GSUITE_STORAGE_SUFFIX
        fileList = []

        if choices.outputType and choices.downloadAndPreprocess == 'Yes' and \
                choices.source.find('HyperBrowser') == -1 and \
                choices.transfer != 'Yes':
            from quick.webtools.GeneralGuiTool import HistElement
            desc = unidecode(choices.subCategory)

            fileList += \
                [HistElement(getGSuiteHistoryOutputName('remote', desc), GSUITE_SUFFIX),
                 HistElement(getGSuiteHistoryOutputName('nodownload', desc), GSUITE_SUFFIX),
                 HistElement(getGSuiteHistoryOutputName('primary', desc), GSUITE_SUFFIX),
                 HistElement(getGSuiteHistoryOutputName('nopreprocessed', desc), GSUITE_SUFFIX),
                 HistElement(getGSuiteHistoryOutputName('preprocessed', desc), GSUITE_SUFFIX),
                 HistElement(getGSuiteHistoryOutputName('storage', desc), GSUITE_STORAGE_SUFFIX,
                                                        hidden=True)]

        return fileList

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        if not choices.source:
            return
        source = choices.source.split('[')[0].strip()
        fileTypes = []
        gsm = TrackGlobalSearchModule(cls.useSqlite)
        desc = choices.subCategory
        
        if choices.source.find('HyperBrowser') == -1:
            #items = gsm.getItems(choices.search,choices.subCategory)
            # # allFileTypes = [x.split('[')[0] for x,selected in prevChoices.filetype.iteritems()]
            # # fileTypes = [x.split('[')[0] for x,selected in prevChoices.filetype.iteritems() if selected]
            ##allDataTypes = [x.split('[')[0].strip() for x,selected in choices.dataType.iteritems()]
            #dataTypes = [x.split('[')[0].strip() for x,selected in choices.dataType.iteritems() if selected]
            dataTypes = [choices.dataType.split('[')[0].strip()]

            ##Was made to speadup so that there will be no filetype comparisons,
            ##but deactivated for now since there is hardcoded filtering in
            ##prevChoices.fileType
            #if len(allFileTypes) == len(fileTypes):
            #    fileTypes = []

        if 'all tracks' in choices.outputType:
                remoteGSuite = gsm.getGSuite(choices.search,choices.subCategory,source,dataTypes,filterFileSuffix = True)
        elif choices.outputType == 'Select tracks manually':
                remoteGSuite = gsm.getGSuite(choices.search,choices.subCategory,source,dataTypes,\
                                             filterFileSuffix = True,selectedFileIDs = choices.results)
        elif choices.outputType == 'Select 10 random tracks':
                remoteGSuite = gsm.getRandomGSuite(choices.search,choices.subCategory,source,dataTypes,\
                                                   filterFileSuffix = True,count = 10)
        elif choices.outputType == 'Select 50 random tracks':
                remoteGSuite = gsm.getRandomGSuite(choices.search,choices.subCategory,source,dataTypes,\
                                                   filterFileSuffix = True,count = 50)

        if choices.downloadAndPreprocess == 'Yes' and choices.source.find('HyperBrowser') == -1:
            trackCount = remoteGSuite.numTracks()
            progressViewer = \
                ProgressViewer([('Download tracks', trackCount),
                                ('Preprocess tracks', trackCount)], galaxyFn)

            #from gold.gsuite.GSuiteDownloader import GSuiteMultipleGalaxyFnDownloader
            #gSuiteDownloader = GSuiteMultipleGalaxyFnDownloader()
            #localGSuite, errorLocalGSuite = \
            #    gSuiteDownloader.visitAllGSuiteTracksAndReturnOutputAndErrorGSuites\
            #        (remoteGSuite, progressViewer, cls.extraGalaxyFn)
            from gold.gsuite.GSuiteDownloader import GSuiteSingleGalaxyFnDownloader
            from quick.gsuite.GSuiteHbIntegration import \
                writeGSuiteHiddenTrackStorageHtml

            gSuiteDownloader = GSuiteSingleGalaxyFnDownloader()
            hiddenStorageFn = cls.extraGalaxyFn[getGSuiteHistoryOutputName('storage', desc)]
            localGSuite, errorLocalGSuite = \
                gSuiteDownloader.visitAllGSuiteTracksAndReturnOutputAndErrorGSuites \
                    (remoteGSuite, progressViewer, hiddenStorageFn, [])
            writeGSuiteHiddenTrackStorageHtml(hiddenStorageFn)

            progressViewer.updateProgressObjectElementCount('Preprocess tracks', localGSuite.numTracks())
            gSuitePreprocessor = GSuitePreprocessor()
            preProcessedGSuite, errorPreProcessGSuite = \
                gSuitePreprocessor.visitAllGSuiteTracksAndReturnOutputAndErrorGSuites\
                    (localGSuite, progressViewer)
            #preProcessedGSuite, errorPreProcessGSuite = localGSuite.preProcessAllLocalTracksAndReturnOutputAndErrorGSuites(progressViewer)
            GSuiteComposer.composeToFile(remoteGSuite,
                cls.extraGalaxyFn[getGSuiteHistoryOutputName('remote', desc)])
            GSuiteComposer.composeToFile(errorLocalGSuite,
                cls.extraGalaxyFn[getGSuiteHistoryOutputName('nodownload', desc)])
            GSuiteComposer.composeToFile(localGSuite,
                cls.extraGalaxyFn[getGSuiteHistoryOutputName('primary', desc)])
            GSuiteComposer.composeToFile(errorPreProcessGSuite,
                cls.extraGalaxyFn[getGSuiteHistoryOutputName('nopreprocessed', desc)])
            GSuiteComposer.composeToFile(preProcessedGSuite,
                cls.extraGalaxyFn[getGSuiteHistoryOutputName('preprocessed', desc)])

        else:
            GSuiteComposer.composeToFile(remoteGSuite, galaxyFn)


    @classmethod
    def validateAndReturnErrors(cls, choices):
        #if choices[0] == 'Text' and choices[1].strip() == '':
        #    return 'You have to enter a search text'
        if cls.exception:
            return cls.exception

        if choices.search in [None,'--Select--'] or choices.subCategory in [None,'--Select--']:
            return ''
        #if choices.outputType == 'Categorized Search for Tracks':
        if not choices.filetype in [None,'',[]] and len([x for x,selected in choices.filetype.iteritems() if selected]) == 0:
            return 'You have to select at least one file type'

            if choices.downloadAndPreprocess == 'Yes':
                errorStr = cls._checkGenome(choices.genome)
                if errorStr:
                    return errorStr

        return GeneralGuiTool._checkGenome(choices.genome)

    @classmethod
    def getOutputName(cls, choices):
        if choices.downloadAndPreprocess == 'Yes':  # and choices.source.find('HyperBrowser') == -1:
            return getGSuiteHistoryOutputName('progress', choices.subCategory)
        else:
            return getGSuiteHistoryOutputName('primary', choices.subCategory)

    @classmethod
    def isRedirectTool(cls,choices):
        if choices.transfer == 'Yes':
            return True
        return False

    @classmethod
    def getRedirectURL(cls, choices):
        gsm = TrackGlobalSearchModule(cls.useSqlite)
        sourceTool,attr_val_dict = gsm.getSourceToolURLParams(choices.search,\
                                                        choices.subCategory,\
                                                        choices.source.split('[')[0].strip())
        
        return cls.createGenericGuiToolURL('hb_track_source_test_tool', sourceTool,attr_val_dict)
        #return choices.url
    
    @staticmethod
    def isPublic():
        '''
        Specifies whether the tool is accessible to all users. If False, the
        tool is only accessible to a restricted set of users as defined in
        LocalOSConfig.py.
        '''
        return True

    @classmethod
    def getToolDescription(cls):
        '''
        Specifies a help text in HTML that is displayed below the tool.
        '''
        from proto.hyperbrowser.HtmlCore import HtmlCore

        core = HtmlCore()
        desc = """This tool is a simplified version of the <b>Create a remote GSuite from a public repository</b> tool.
        Several categories of genomic tracks that can be found in the supported databases have been preselected and
        categorized to ease the search. Additionally the
        selected genomic tracks will be downloaded and preprocessed, i.e. prepared for analysis. Each intermediate step
        will be reported for transparency. This tool offers easier
        use at the exchange of the fine tuned search available in the more advanced tool."""
        core.paragraph(desc)

        core. paragraph('To use the tool, please follow these steps:')
        core.orderedList(['Select one of the predefined categories.',
                         'Select the attribute of interest.',
                          'Select either all or a preferred database.',
                          'Select the preferred data type.',
                          'Execute the tool.'])

        return str(core)# + cls.getPlot()


    @staticmethod
    def getOutputFormat(choices):
        if choices.downloadAndPreprocess == 'Yes':  # and choices.source.find('HyperBrowser') == -1:
            return 'customhtml'
        else:
            return 'gsuite'

    @classmethod
    def getPlot(cls):
        import quick.webtools.restricted.visualization.visualizationPlots as vp
        plot = vp.addJSlibs()
        plot = plot + vp.useThemePlot()
        plot = plot + vp.addJSlibsExport()

        try:
            #Required
            #dataX =  [[10, 20, 30], [2, 10, 20], [2, 100, 20]]
            dataX =  [[20], [10]]
            '''More information about the template are in quick.webtools.restricted.visualization.visualizationPlots'''
            #Additional
            #categories = ['cat1', 'cat2', 'cat3']
            categories = ['Data Repositories']
            yAxisTitle = 'yAxisTitle'
            seriesName = []
            seriesType=[]
            for item in cls.Rpositories:
                seriesName.append(str(item))
                seriesType.append('column')
            #seriesName=[str(cls.Rpositories[0]), str(cls.Rpositories[1]), str(cls.Rpositories[2])]
            shared=False
            titleText = 'titleText'
            #legend =True
            legend =False
            xAxisRotation=-90

            stacked=True

            plot = plot + vp.drawChart(dataX, type='column', categories=categories, yAxisTitle =yAxisTitle,minWidth = 600, legend =legend, xAxisRotation=xAxisRotation, seriesType=seriesType, seriesName=seriesName, shared=shared, titleText=titleText, stacked = stacked)
            return plot
        except Exception as e:
            return str(e)+'\n'+str(cls.Rpositories)

    # @staticmethod
    # def getFullExampleURL():
    #     return 'https://hyperbrowser.uio.no/nar/u/hb-superuser/p/browse-catalog-of-chromatin-tracks'
