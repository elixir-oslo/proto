#from quick.webtools.GeneralGuiTool import GeneralGuiTool
import gold.gsuite.GSuiteConstants as GSuiteConstants
from quick.webtools.GeneralGuiTool import MultiGeneralGuiTool
from proto.tools.hyperbrowser.imports.CGAtlasTrackSearchTool import CGAtlasTrackSearchTool
from proto.tools.hyperbrowser.imports.EBIHubTrackSearchTool import EBIHubTrackSearchTool
from proto.tools.hyperbrowser.imports.EncodeTrackSearchTool import EncodeTrackSearchTool
from proto.tools.hyperbrowser.imports.Epigenome2ImputedTrackSearchTool import Epigenome2ImputedTrackSearchTool
from proto.tools.hyperbrowser.imports.Epigenome2TrackSearchTool import Epigenome2TrackSearchTool
from proto.tools.hyperbrowser.imports.FANTOM5TrackSearchTool import FANTOM5TrackSearchTool
from proto.tools.hyperbrowser.imports.GWASTrackSearchTool import GWASTrackSearchTool
from proto.tools.hyperbrowser.imports.ICGCTrackSearchTool import ICGCTrackSearchTool

# This is a template prototyping GUI that comes together with a corresponding
# web page.

class TrackSourceTestTool(MultiGeneralGuiTool):
    GSUITE_OUTPUT_LOCATION = GSuiteConstants.REMOTE
    GSUITE_OUTPUT_FILE_FORMAT = ', '.join([GSuiteConstants.UNKNOWN, GSuiteConstants.TEXT])
    GSUITE_OUTPUT_TRACK_TYPE = GSuiteConstants.UNKNOWN

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''

        return "Create a remote GSuite from a public repository (track selection by data-source)"


    #@classmethod
    #def getInputBoxNames(cls):
    #    return [('Test:','test')]
    #@classmethod
    #def getOptionsBoxTest(cls):
    #    return ' '

    @staticmethod
    def getSubToolClasses():
        return [EncodeTrackSearchTool,
                #EpigenomeTrackSearchTool,
                Epigenome2TrackSearchTool,
                #Epigenome2ImputedTrackSearchTool,
                CGAtlasTrackSearchTool,
                # FANTOM5TrackSearchTool,
                ICGCTrackSearchTool,
                #EBIHubTrackSearchTool,
                GWASTrackSearchTool
                ]

    @staticmethod
    def getSubToolSelectionTitle():
        return 'Select repository:'
    
    #@staticmethod
    #def getInfoForSubToolClasses():
    #    return 'xx'
    
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

        core.paragraph('The tool provides a structured search for genomic tracks stored in '
                       'the following repositories:')
        core.unorderedList(['ENCODE tracks which are located in both UCSC and Ensembl databases.',
#                            'Roadmap Epigenomics',
                            'Roadmap Epigenomics',
                            'Cancer Genome Atlas (TCGA)',
                            'FANTOM 5',
                            'International Cancer Genome Consortium (ICGC)',
                            'Ensembl BLUEPRINT epigenome project',
                            'NHGRI-EBI GWAS Catalog'])

        core.paragraph('The tool generates a metadata file in the GSuite format which contains '
                       'the URL and other metadata associated with each of the track files that '
                       'match the search criteria. To use the tool, please follow these steps:')
        core.orderedList(['Select an attribute from the attribute list to search with',
                          'Select the value associated with this attribute from the associated attribute list',
                          'Repeat steps 1 and 2 to filter using more attributes',
                          'Select whether to compile a GSuite using:' +
                          str(HtmlCore().unorderedList(['All rearch results',
                                                        'Present results as a file list and have '
                                                        'the option of selecting a subset of those '
                                                        'result to compile the GSuite'])),
                          'Specify  the format of the output (' + str(HtmlCore().highlight('gsuite')) +
                              ' for GSuite or ' + str(HtmlCore().highlight('HTML')) +
                              ' for a more human readable format)'])

        core.divider()
        core.smallHeader('Note')
        core.paragraph('Even though this tool can be used to build GSuite compilations of any files, '
                       'the resulting GSuite file will be more usable if the files are somewhat homogeneous '
                       'in file format and/or track type.')

        cls._addGSuiteFileDescription(core,
                                      outputLocation=cls.GSUITE_OUTPUT_LOCATION,
                                      outputFileFormat=cls.GSUITE_OUTPUT_FILE_FORMAT,
                                      outputTrackType=cls.GSUITE_OUTPUT_TRACK_TYPE)

        return str(core)

        #string += 'Another supported functionality is to manage the resulted metadata (GSuite) file, by the GSuite manager tool. The functionality is supported by three subtools:'
        #string += '<ol><li>Download the listed files in a GSuite as history elements</li>'
        #string += '<li>Select a subset of rows from a GSuite file</li>'
        #string += '<li>Select a subset of columns from a GSuite file</li></ol>'
        #string += '<i>Version 1.0.2 has an additional functionality that attribute lists appear accumulatively in the same order of the selection</i>'

    # @staticmethod
    # def getFullExampleURL():
    #     return 'https://hyperbrowser.uio.no/nar/u/hb-superuser/p/compile-gsuite-from-external-database---user-guide'
