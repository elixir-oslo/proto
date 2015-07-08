import os
from collections import namedtuple

#from config.Config import DATA_FILES_PATH
#from gold.application.LogSetup import logMessage
#from gold.util.CustomExceptions import Warning
#from quick.util.CommonFunctions import getUniqueWebPath, getRelativeUrlFromWebPath, extractIdFromGalaxyFn
#from quick.application.SignatureDevianceLogging import takes,returns

class GeneralGuiTool(object):
    def __init__(self, toolId=None):
        self.__class__.toolId = toolId

    # API methods
    @staticmethod
    def getInputBoxNames():
        return []

    @staticmethod
    def getSubToolClasses():
        return None

    @classmethod
    def getToolSelectionName(cls):
        return cls.getToolName()

    @staticmethod
    def isPublic():
        return False

    @staticmethod
    def isRedirectTool():
        return False

    @staticmethod
    def isHistoryTool():
        return True

    @classmethod
    def isBatchTool(cls):
        return False
#        return cls.isHistoryTool()

    @staticmethod
    def isDynamic():
        return True

    @staticmethod
    def getResetBoxes():
        return []

    @staticmethod
    def getInputBoxOrder():
        return None

    @staticmethod
    def getToolDescription():
        return ''

    @staticmethod
    def getToolIllustration():
        return None

    @staticmethod
    def getFullExampleURL():
        return None

    @classmethod
    def doTestsOnTool(cls, galaxyFn, title, label):
        from quick.application.GalaxyInterface import GalaxyInterface
        from collections import OrderedDict
        import sys

        if hasattr(cls, 'getTests'):
            galaxy_ext = None
            testRunList = cls.getTests()
            for indx, tRun in enumerate(testRunList):
                choices = tRun.split('(',1)[1].rsplit(')',1)[0].split('|')
                choices = [eval(v) for v in choices]
                if not galaxy_ext:
                    galaxy_ext = cls.getOutputFormat(choices)
                output_filename = cls.makeHistElement(galaxyExt=galaxy_ext, title=title+str(indx), label=label+str(indx))
                sys.stdout = open(output_filename, "w", 0)
                cls.execute(choices, output_filename)
            sys.stdout = open(galaxyFn, "a", 0)
        else:
            print open(galaxyFn, "a").write('No tests specified for %s' % cls.__name__)


    @classmethod
    def getTests(cls):
        import shelve
        SHELVE_FN = DATA_FILES_PATH + os.sep + 'tests' + os.sep + '%s.shelve'%cls.toolId
        if os.path.isfile(SHELVE_FN):

            testDict = shelve.open(SHELVE_FN)
            resDict = dict()
            for k, v in testDict.items():
                resDict[k] = cls.convertHttpParamsStr(v)
            return resDict
        return None

    @staticmethod
    def isDebugMode():
        return False

    @staticmethod
    def getOutputFormat(choices=None):
        return 'html'

    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not valid,
        an error text explaining the problem should be returned. The GUI then shows this text
        to the user (if not empty) and greys out the execute button (even if the text is empty).
        If all parameters are valid, the method should return None, which enables the execute button.
        '''
        return None

    # Convenience methods

    @classmethod
    def convertHttpParamsStr(cls, streng):
        strTab = []
        for v in streng.split('\n'):
            if v:
                strTab.append(v)

        return dict([tuple(v.split(':',1)) for v in strTab])

    @classmethod
    def getOptionBoxNames(cls):
        labels = cls.getInputBoxNames()
        #inputOrder = range(len(labels) if not cls.getInputBoxOrder() else cls.getInputBoxOrder()
        boxMal = 'box%i'
        if type(labels[0]).__name__ == 'str':
            return [boxMal%i for i in range(1, len(labels)+1)]
            #return [boxMal % i for i in inputOrder]
        else:
            return [i[0] for i in labels]
            #return [labels[i][0] for i in inputOrder]

    @classmethod
    def formatTests(cls, choicesFormType, testRunList):
        labels = cls.getOptionBoxNames()
        if len(labels) != len(choicesFormType):
            logMessage('labels and choicesFormType are different:(labels=%i, choicesFormType=%i)' % (len(labels), len(choicesFormType)))
        return (testRunList, zip(labels, choicesFormType))

    @classmethod
    def _getPathAndUrlForFile(cls, galaxyFn, relFn):
        '''
        Gets a disk path and a URL for storing a run-specific file.
        galaxyFn is connected to the resulting history item in Galaxy,
          and is used to determine a unique disk path for this specific run.
        relFn is a relative file name (i.e. only name, not full path) that one
          wants a full disk path for, as well as a URL referring to the file.
        '''
        fullFn = cls._getDiskPathForFiles(galaxyFn) + os.sep + relFn
        url = cls._getBaseUrlForFiles(fullFn)
        return fullFn, url

    @staticmethod
    def _getDiskPathForFiles(galaxyFn):
        galaxyId = extractIdFromGalaxyFn(galaxyFn)
        return getUniqueWebPath(galaxyId)

    @staticmethod
    def _getBaseUrlForFiles(diskPath):
        return getRelativeUrlFromWebPath(diskPath)

    @staticmethod
    def _getGenomeChoice(choices, genomeChoiceIndex):
        if genomeChoiceIndex is None:
            genome = None
        else:
            if type(genomeChoiceIndex) == int:
                genome = choices[genomeChoiceIndex]
            else:
                genome = getattr(choices, genomeChoiceIndex)

            if genome in [None, '']:
                return genome, 'Please select a genome build'

        return genome, None

    @staticmethod
    def _getTrackChoice(choices, trackChoiceIndex):
        if type(trackChoiceIndex) == int:
            trackChoice = choices[trackChoiceIndex]
        else:
            trackChoice = getattr(choices, trackChoiceIndex)

        if trackChoice is None:
            return trackChoice, 'Please select a track'

        trackName = trackChoice.split(':')
        return trackName, None

    @staticmethod
    def _checkTrack(choices, trackChoiceIndex=1, genomeChoiceIndex=0, filetype=None, validateFirstLine=True):
        genome, errorStr = GeneralGuiTool._getGenomeChoice(choices, genomeChoiceIndex)
        if errorStr:
            return errorStr

        trackName, errorStr = GeneralGuiTool._getTrackChoice(choices, trackChoiceIndex)
        if errorStr:
            return errorStr

        from quick.application.ExternalTrackManager import ExternalTrackManager
        if ExternalTrackManager.isGalaxyTrack(trackName):
            errorStr = GeneralGuiTool._checkHistoryTrack(choices, trackChoiceIndex, genome, filetype, validateFirstLine)
            if errorStr:
                return errorStr
        else:
            if not GeneralGuiTool._isValidTrack(choices, trackChoiceIndex, genomeChoiceIndex):
                return 'Please select a valid track'

    @staticmethod
    def _isValidTrack(choices, tnChoiceIndex=1, genomeChoiceIndex=0):
        from quick.application.GalaxyInterface import GalaxyInterface
        from quick.application.ProcTrackOptions import ProcTrackOptions

        genome, errorStr = GeneralGuiTool._getGenomeChoice(choices, genomeChoiceIndex)
        if errorStr or genome is None:
            return False

        trackName, errorStr = GeneralGuiTool._getTrackChoice(choices, tnChoiceIndex)
        if errorStr:
            return False

        return ProcTrackOptions.isValidTrack(genome, trackName, True) or \
            GalaxyInterface.isNmerTrackName(genome, trackName)

    @staticmethod
    def _checkHistoryTrack(choices, historyChoiceIndex, genome, filetype=None, validateFirstLine=True):
        fileStr = filetype + ' file' if filetype else 'file'

        trackName, errorStr = GeneralGuiTool._getTrackChoice(choices, historyChoiceIndex)
        if errorStr:
            return 'Please select a ' + fileStr + ' from history.'

        if validateFirstLine:
            return GeneralGuiTool._validateFirstLine(trackName, genome, fileStr)

    @staticmethod
    def _validateFirstLine(galaxyTN, genome=None, fileStr='file'):
        try:
            from quick.application.ExternalTrackManager import ExternalTrackManager
            from gold.origdata.GenomeElementSource import GenomeElementSource

            suffix = ExternalTrackManager.extractFileSuffixFromGalaxyTN(galaxyTN)
            fn = ExternalTrackManager.extractFnFromGalaxyTN(galaxyTN)

            GenomeElementSource(fn, genome, suffix=suffix).parseFirstDataLine()

        except Exception, e:
            return fileStr.capitalize() + ' invalid: ' + str(e)

    @staticmethod
    def _getBasicTrackFormat(choices, tnChoiceIndex=1, genomeChoiceIndex=0):
        genome = GeneralGuiTool._getGenomeChoice(choices, genomeChoiceIndex)[0]
        tn = GeneralGuiTool._getTrackChoice(choices, tnChoiceIndex)[0]

        from quick.application.GalaxyInterface import GalaxyInterface
        from gold.description.TrackInfo import TrackInfo
        from quick.application.ExternalTrackManager import ExternalTrackManager
        from gold.track.TrackFormat import TrackFormat

        if ExternalTrackManager.isGalaxyTrack(tn):
            geSource = ExternalTrackManager.getGESourceFromGalaxyOrVirtualTN(tn, genome)
            try:
                tf = GeneralGuiTool._convertToBasicTrackFormat(TrackFormat.createInstanceFromGeSource(geSource).getFormatName())
            except Warning:
                return genome, tn, ''
        else:
            if GalaxyInterface.isNmerTrackName(genome, tn):
                tfName = 'Points'
            else:
                tfName = TrackInfo(genome, tn).trackFormatName
            tf = GeneralGuiTool._convertToBasicTrackFormat(tfName)
        return genome, tn, tf

    @staticmethod
    def _getValueTypeName(choices, tnChoiceIndex=1, genomeChoiceIndex=0):
        genome = GeneralGuiTool._getGenomeChoice(choices, genomeChoiceIndex)[0]
        tn = GeneralGuiTool._getTrackChoice(choices, tnChoiceIndex)[0]

        from quick.application.GalaxyInterface import GalaxyInterface
        from gold.description.TrackInfo import TrackInfo
        from quick.application.ExternalTrackManager import ExternalTrackManager
        from gold.track.TrackFormat import TrackFormat

        if ExternalTrackManager.isGalaxyTrack(tn):
            geSource = ExternalTrackManager.getGESourceFromGalaxyOrVirtualTN(tn, genome)
            valTypeName = TrackFormat.createInstanceFromGeSource(geSource).getValTypeName()
        else:
            if GalaxyInterface.isNmerTrackName(genome, tn):
                valTypeName = ''
            else:
                valTypeName = TrackInfo(genome, tn).markType
        return valTypeName.lower()

    #@staticmethod
    #def _getBasicTrackFormatFromHistory(choices, tnChoiceIndex=1):
    #    from quick.application.ExternalTrackManager import ExternalTrackManager
    #    from gold.track.TrackFormat import TrackFormat
    #    genome = choices[0]
    #    tn = choices[tnChoiceIndex].split(':')
    #    geSource = ExternalTrackManager.getGESourceFromGalaxyOrVirtualTN(tn, genome)
    #    tf = GeneralGuiTool._convertToBasicTrackFormat(TrackFormat.createInstanceFromGeSource(geSource).getFormatName())
    #
    #
    #    return genome, tn, tf


    @staticmethod
    def _convertToBasicTrackFormat(tfName):
        tfName = tfName.lower()

        if tfName.startswith('linked '):
            tfName = tfName[7:]

        tfName = tfName.replace('unmarked ','')
        tfName = tfName.replace('marked','valued')

        return tfName

    @classmethod
    def getNamedTuple(cls):
        names = cls.getInputBoxNames()
        anyTuples = False
        vals = []
        for i in range(len(names)):
            name = names[i]
            if isinstance(name, tuple):
                anyTuples = True
                vals.append(name[1])
            else:
                vals.append('box' + str(1 + i))

        if anyTuples:
            return namedtuple('ChoiceTuple', vals)
        else:
            return None

    @staticmethod
    def _exampleText(text):
        from gold.result.HtmlCore import HtmlCore
        core = HtmlCore()
        core.styleInfoBegin(styleClass='debug', linesep=False)
        core.append(text.replace('\t','\\t'))
        core.styleInfoEnd()
        return str(core)

    @classmethod
    def makeHistElement(cls,  galaxyExt='html', title='new Dataset', label='Newly created dataset',):
        import simplejson, glob
        #print 'im in makeHistElement'
        json_params =  cls.runParams
        datasetId = json_params['output_data'][0]['dataset_id'] # dataset_id fra output_data
        hdaId = json_params['output_data'][0]['hda_id'] # # hda_id fra output_data
        metadata_parameter_file = open( json_params['job_config']['TOOL_PROVIDED_JOB_METADATA_FILE'], 'a' )
        newFilePath = json_params['param_dict']['__new_file_path__']
        numFiles = len(glob.glob(newFilePath+'/primary_%i_*'%hdaId))
        #title += str(numFiles+1)
        #print 'datasetId', datasetId
        #print 'newFilePath', newFilePath
        #print 'numFiles', numFiles
        outputFilename = os.path.join(newFilePath , 'primary_%i_%s_visible_%s' % ( hdaId, title, galaxyExt ) )
        #print 'outputFilename', outputFilename
        metadata_parameter_file.write( "%s\n" % simplejson.dumps( dict( type = 'dataset', #new_primary_
                                         dataset_id = datasetId,#base_
                                         ext = galaxyExt,
                                         #filename = outputFilename,
                                         #name = label,
                                         metadata = {'dbkey':['hg18']} )) )
        metadata_parameter_file.close()
        return outputFilename


#+        new_primary_datasets = {}
#+        try:
#+            json_file = open( os.path.join( job_working_directory, jobs.TOOL_PROVIDED_JOB_METADATA_FILE ), 'r' )
#+            for line in json_file:
#+                line = simplejson.loads( line )
#+                if line.get( 'type' ) == 'new_primary_dataset':
#+                    new_primary_datasets[ os.path.split( line.get( 'filename' ) )[-1] ] = line
#+        except Exception, e:
#+            log.debug( "Error opening galaxy.json file: %s" % e )
#         # Loop through output file names, looking for generated primary
#         # datasets in form of:
#         #     'primary_associatedWithDatasetID_designation_visibility_extension(_DBKEY)'
#+        primary_datasets = {}
#         for name, outdata in output.items():
#             filenames = []
#             if 'new_file_path' in self.app.config.collect_outputs_from:
#@@ -2664,8 +2673,6 @@
#                 primary_data.info = outdata.info
#                 primary_data.init_meta( copy_from=outdata )
#                 primary_data.dbkey = dbkey
#-                primary_data.set_meta()
#-                primary_data.set_peek()
#                 # Associate new dataset with job
#                 job = None
#                 for assoc in outdata.creating_job_associations:
#@@ -2677,6 +2684,15 @@
#                     self.sa_session.add( assoc )
#                     self.sa_session.flush()
#                 primary_data.state = outdata.state
#+                #add tool/metadata provided information
#+                new_primary_datasets_attributes = new_primary_datasets.get( os.path.split( filename )[-1] )
#+                if new_primary_datasets_attributes:
#+                    dataset_att_by_name = dict( ext='extension' )
#+                    for att_set in [ 'name', 'info', 'ext', 'dbkey' ]:
#+                        dataset_att_name = dataset_att_by_name.get( att_set, att_set )
#+                        setattr( primary_data, dataset_att_name, new_primary_datasets_attributes.get( att_set, getattr( primary_data, dataset_att_name ) ) )
#+                primary_data.set_meta()
#+                primary_data.set_peek()
#                 self.sa_session.add( primary_data )
#                 self.sa_session.flush()
#                 outdata.history.add_dataset( primary_data )
#
#Repository URL: https://bitbucket.org/galaxy/galaxy-central/
#
#--
#
#This is a commit notification from bitbucket.org. You are receiving
#this because you have the service enabled, addressing the recipient of
#this email.
#Previous message: [galaxy-commits] commit/galaxy-central: greg: Apply patch from Peter Cock which issues a warning if loading a loc file with inconsistent numbers of tabs.
#Next message: [galaxy-commits] commit/galaxy-central: 2 new changesets
#Messages sorted by: [ date ] [ thread ] [ subject ] [ author ]
#More information about the galaxy-commits mailing list

class MultiGeneralGuiTool(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "-----  Select tool -----"

    @staticmethod
    def getToolSelectionName():
        return "-----  Select tool -----"

    @staticmethod
    def validateAndReturnErrors(choices):
        return ''

    @staticmethod
    def getInputBoxNames():
        return []

    @staticmethod
    def useSubToolPrefix():
        return False


class HistElement(object):
    def __init__(self, name, format, label=None, hidden=False):
        self.name = name
        self.format = format
        self.label = label
        self.hidden = hidden
