from proto.CommonFunctions import extractFnFromDatasetInfo
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from gold.gsuite import GSuiteConstants
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.webtools.mixin.GenomeMixin import GenomeMixin


class MatchTfWithPWM(GeneralGuiTool, GenomeMixin):
    ALLOW_UNKNOWN_GENOME = False
    ALLOW_GENOME_OVERRIDE = False
    ALLOW_MULTIPLE_GENOMES = False
    WHAT_GENOME_IS_USED_FOR = 'the analysis'  # Other common possibility: 'the analysis'

    GSUITE_ALLOWED_LOCATIONS = [GSuiteConstants.LOCAL]
    GSUITE_ALLOWED_FILE_TYPES = [GSuiteConstants.PREPROCESSED]
    GSUITE_ALLOWED_TRACK_TYPES = [GSuiteConstants.SEGMENTS,
                                  GSuiteConstants.VALUED_SEGMENTS]

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Match a suite of TFs with PWMs"

    @classmethod
    def getInputBoxNames(cls):
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

        return [('', 'basicQuestionId'),
                ('Gsuite file containing transcription factors', 'gsuite')] +\
                cls.getInputBoxNamesForGenomeSelection()
                #UserBinSelector.getUserBinInputBoxNames()

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
    def getOptionsBoxBasicQuestionId():
        return '__hidden__', None

    @staticmethod
    def getOptionsBoxGsuite(prevChoices): # Alternatively: getOptionsBox2()
        '''
        See getOptionsBoxFirstKey().

        prevChoices is a namedtuple of selections made by the user in the
        previous input boxes (that is, a namedtuple containing only one element
        in this case). The elements can accessed either by index, e.g.
        prevChoices[0] for the result of input box 1, or by key, e.g.
        prevChoices.key (case 2).
        '''
        return ('__history__',)

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        '''
        Is called when execute-button is pushed by web-user. Should print
        output as HTML to standard out, which will be directed to a results page
        in Galaxy history. If getOutputFormat is anything else than HTML, the
        output should be written to the file with path galaxyFn. If needed,
        StaticFile can be used to get a path where additional files can be put
        (e.g. generated image files). choices is a list of selections made by
        web-user in each options box.
        '''

        import shelve
        mapper = shelve.open("/hyperbrowser/data/tfbs/tfNames2pwmIds.shelf")
        mapper["CTCF"] = ["REN_20"]
        print "Test"

        outfile = open(galaxyFn, "w")

        gsuite = getGSuiteFromGalaxyTN(choices.gsuite)

        fileName = extractFnFromDatasetInfo(choices.gsuite)
        attributes_ordered = []

        metaFields = []

        # First: Write old headers to output file
        f = open(fileName, "r")
        headerLines = []
        for line in f.readlines():
            if line[0:3] == "###": # This is the field header line
                #headerLines.append([line.rstrip() + "\tpwm\n"]) # Add a pwm id field
                #attributes_ordered = line.replace("###", "").split('\t') # Fetch order list of attributes
                metaFields = line.replace("###", "").split("\t")[2:] # uri and title always first two fields?
                break # Break since this is the last header line
            else:
                headerLines.append(line)



        # Iterate over all TFs in gsuite file. Match to PWMs and write to output gusite file
        tflines = []
        attributes = []
        for x in gsuite.allTracks():
            print x
            #print "Processing " + x.attributes["table name"]
            if not "antibody" in x.attributes:
                print "Warning: TF is missing antibody meta data"
            elif not "cell" in x.attributes:
                print "Warning: TF is missing cell type meta data"
            else:
                if x.attributes["antibody"] in mapper:
                    line = x.uri + "\t" + x.title
                    pwms = []
                    for field in metaFields:
                        line += "\t"
                        if field.lower() in x.attributes:
                            line += x.attributes[field.lower()]
                        else:
                            line += "None"


                    for pwm in mapper[x.attributes["antibody"]]:
                        pwms.append(pwm)
                        #tflines.append(x.uri + "\t" + x.title + "\t" + '\t'.join(x.attributes.values()) + "\t" + pwm + "\n")

                    pwms = list(set(pwms)) # Only keep unique PWMs

                    line += "\t" + ','.join(pwms) + "\n"
                    tflines.append(line)
                else:
                    print "Warning: Antibody is missing in mapper"
        print tflines


        # First write header lines
        outfile.writelines(headerLines)

        # Now get the correct meta data field names from attributes and write one line with those
        outfile.writelines(["###" + '\t'.join(["uri", "title"] + metaFields).rstrip() + "\tpwm" + "\n"])

        outfile.writelines(tflines)


    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return "gsuite"


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

    @classmethod
    def validateAndReturnErrors(cls, choices):
        '''
        Should validate the selected input parameters. If the parameters are
        not valid, an error text explaining the problem should be returned. The
        GUI then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are
        valid, the method should return None, which enables the execute button.
        '''

        errorString = cls._checkGSuiteFile(choices.gsuite)
        if errorString:
            return errorString

        gSuite = getGSuiteFromGalaxyTN(choices.gsuite)

        errorString = cls._checkGSuiteRequirements(
            gSuite,
            allowedLocations=cls.GSUITE_ALLOWED_LOCATIONS,
            allowedFileFormats=cls.GSUITE_ALLOWED_FILE_TYPES,
            allowedTrackTypes=cls.GSUITE_ALLOWED_TRACK_TYPES)
        if errorString:
            return errorString

        errorString = cls._validateGenome(choices.genome)
        if errorString:
            return errorString

    @staticmethod
    def isPublic():
        return True
