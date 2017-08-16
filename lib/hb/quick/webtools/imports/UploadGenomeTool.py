from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.extra.GenomeImporter import GenomeImporter
import os
import sys
from quick.util.GenomeInfo import GenomeInfo
from gold.util.CustomExceptions import InvalidFormatError
from quick.webtools.util.CommonFunctionsForTools import validateURLs, validateURL, validateUcscValues
from shutil import copyfile
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.util.CommonFunctions import ensurePathExists

class UploadGenomeTool(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Upload genome sequence from URL"

    @staticmethod
    def getInputBoxNames(prevChoices=None):
        "Returns a list of names for input boxes, implicitly also the number of input boxes to display on page. Each such box will call function getOptionsBoxK, where K is in the range of 1 to the number of boxes"
        return ['Genome abbreviation <i>(internal short name of genome, e.g. hg18)</i>',\
                "Genome name <i>(human readable name to appear in selection boxes, e.g. 'Human Mar. 2006 (hg18/NCBI36)')</i>",\
                'Upload sequence from',\
                'Genome sequence URL(s) <i>(URL(s) for FASTA files of the genome assembly, optionally compressed)</i>',\
                'Genome sequence from history',\
                'Genome build source <i>(e.g. NCBI)</i>',\
                'Genome build name <i>(e.g. hg18)</i>',\
                'Species <i>(e.g. Homo Sapiens)</i>',\
                'Species taxonomy URL <i>(e.g. http://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?mode=Info&id=9606)</i>',\
                'Assembly details <i>(description of the assembly, HTML code accepted)</i>',\
                'Owners <i>(list of e-mail addresses)</i>',\
                'Access level for genome',\
                'Availability <i>(the type of installations where the genome is available)</i>',\
                'Mapping to UCSC table browser: Clade <i>(e.g. mammal)</i>',\
                'Mapping to UCSC table browser: Genome <i>(e.g. Human)</i>',\
                'Mapping to UCSC table browser: Assembly <i>(e.g. hg18)</i>',\
                'Upload genome annotations file (GFF)',\
                'Genome annotations URL(s) <i>(URL(s) for GFF files of the genome annotations, optionally compressed)</i>',\
                'Genome annotations file (GFF) from history']

    @staticmethod
    def getOptionsBox1():
        "Returns a list of options to be displayed in the first options box"
        return ''

    @staticmethod
    def getOptionsBox2(prevChoices):
        '''Returns a list of options to be displayed in the second options box, which will be displayed after a selection is made in the first box.
        prevChoices is a list of selections made by the web-user in the previous input boxes (that is, list containing only one element for this case)
        '''
        return ''

    @staticmethod
    def getOptionsBox3(prevChoices):
        return ['history','URL']

    @staticmethod
    def getOptionsBox4(prevChoices):
        if prevChoices[2] == 'URL':
            return '', 3

    @staticmethod
    def getOptionsBox5(prevChoices):
        if prevChoices[2] == 'history':
            return '__history__', 'fa', 'fasta'

    @staticmethod
    def getOptionsBox6(prevChoices):
        return ''

    @staticmethod
    def getOptionsBox7(prevChoices):
        return ''

    @staticmethod
    def getOptionsBox8(prevChoices):
        return ''

    @staticmethod
    def getOptionsBox9(prevChoices):
        return ''

    @staticmethod
    def getOptionsBox10(prevChoices):
        return '', 7

    @staticmethod
    def getOptionsBox11(prevChoices):
        return '', 5

    @staticmethod
    def getOptionsBox12(prevChoices):
        return ['Owners only', 'All']

    @staticmethod
    def getOptionsBox13(prevChoices):
        return ['Experimental only', 'All']

    @staticmethod
    def getOptionsBox14(prevChoices):
        return ''

    @staticmethod
    def getOptionsBox15(prevChoices):
        return ''

    @staticmethod
    def getOptionsBox16(prevChoices):
        return ''

    @staticmethod
    def getOptionsBox17(prevChoices):
        return ['Do not upload', 'from history', 'from URL']

    @staticmethod
    def getOptionsBox18(prevChoices):
        if prevChoices[16] == 'from URL':
            return '', 3

    @staticmethod
    def getOptionsBox19(prevChoices):
        if prevChoices[16] == 'from history':
            return '__history__', 'gff', 'gtf', 'gff3'


    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not valid,
        an error text explaining the problem should be returned. The GUI then shows this text
        to the user (if not empty) and greys out the execute button (even if the text is empty).
        If all parameters are valid, the method should return None, which enables the execute button.
        '''
        if ' ' in choices[0]:
            return 'Genome short name should not contain spaces.'

        basePath = GenomeImporter.getBasePathSequence(choices[0])
        if os.path.exists(basePath):
            return "Genome sequence path already exists: %s. Rename genome or delete directory to proceed." \
                % basePath

        if any(c.strip() == '' for c in choices[0:2]):
                return "Genome abbreviation and name boxes must be filled."

        if choices[2] == 'URL':
            if choices[3].strip() == '':
                return "Sequence URL box must be filled."
        else:
            error = GeneralGuiTool._checkTrack(choices, trackChoiceIndex=4, genomeChoiceIndex=None, \
                                               filetype='FASTA', validateFirstLine=True)
            if error:
                return error

        # test if the URLs are alive
        if choices[2] == 'URL':
            urls = choices[3].strip().split()
            urlError = validateURLs(urls)
            if urlError:
                return urlError

        taxonomyUrl = choices[8].strip()
        if taxonomyUrl != '':
            urlError = validateURL(taxonomyUrl)
            if urlError:
                return urlError
        import re
        emails = [v for v in re.split('[ ,\n\t\r]+',choices[10])]
        for email in emails:
            if not ('@' in email and '.' in email):
            #pass
        #if len([v for v in choices[8].replace(os.linesep, ' ').replace(',', ' ').split(' ') if not v =='' and v.find('@')<0])>0:
                return 'There is an invalid format (%s) inside the E-mail address field' % email

        ucscError = validateUcscValues([choices[x] for x in [13,14,15]])
        if ucscError:
            return ucscError

        if choices[16] == 'from URL':
            if choices[17].strip() == '':
                return "Genome annotation URL box must be filled."
        elif choices[16] == 'from history':
            error = GeneralGuiTool._checkTrack(choices, trackChoiceIndex=18, genomeChoiceIndex=None, \
                                               filetype='FASTA', validateFirstLine=True)
            if error:
                return error

        # test if the URLs are alive
        if choices[16] == 'from URL':
            urls = choices[17].strip().split()
            urlError = validateURLs(urls)
            if urlError:
                return urlError

    @classmethod
    def execute(cls, choices, galaxyFn=None , username=''):
        '''Is called when execute-button is pushed by web-user.
        Should print output as HTML to standard out, which will be directed to a results page in Galaxy history.
        If needed, StaticFile can be used to get a path where additional files can be put (e.g. generated image files).
        choices is a list of selections made by web-user in each options box.
        '''

        #print 'Executing... with choices %s'%str(choices)
        abbrv = choices[0]
        name = choices[1]

        #Should test that the genome is not in hyperbrowser.
        gi = GenomeInfo(abbrv)

        if gi.hasOrigFiles():
            sys.stderr.write( "Genome "+abbrv+ " is already in the Genomic HyperBrowser. Remove the old first.")
        else:
            gi.fullName = name
            if choices[2] == 'URL':
                urls = choices[3].split()
                gi.sourceUrls = urls
                for url in urls:
                    try:
                        GenomeImporter.downloadGenomeSequence(abbrv, url)
                    except InvalidFormatError:
                        return
            else:
                basePath =  GenomeImporter.getBasePathSequence(abbrv)
                fnSource = ExternalTrackManager.extractFnFromGalaxyTN(choices[4].split(':'))
                fnDest = basePath + os.path.sep + abbrv + '.fa'
                ensurePathExists(fnDest)
                copyfile(fnSource, fnDest)

            if choices[16] == 'from URL':
                urls = choices[3].split()
                gi.sourceUrls = urls
                for url in urls:
                    try:
                        GenomeImporter.downloadGffFile(abbrv, url)
                    except InvalidFormatError:
                        return
            elif choices[16] == 'from history':
                fnSource = ExternalTrackManager.extractFnFromGalaxyTN(choices[18].split(':'))
                fnDest =  GenomeImporter.getCollectedPathGFF(abbrv)
                ensurePathExists(fnDest)
                copyfile(fnSource, fnDest)

            chrs=GenomeImporter.extractChromosomesFromGenome(abbrv)
            #gi.sourceChrNames = chrs
            gi.installedBy = username
            gi.genomeBuildSource = choices[5]
            gi.genomeBuildName = choices[6]
            gi.species = choices[7]
            gi.speciesTaxonomyUrl = choices[8]
            gi.assemblyDetails = choices[9]
            gi.privateAccessList = [v.strip() for v in choices[10].replace(os.linesep, ' ').replace(',', ' ').split(' ') if v.find('@')>0]
            gi.isPrivate = (choices[11] != 'All')
            gi.isExperimental = (choices[12] != 'All')
            gi.ucscClade = choices[13]
            gi.ucscGenome = choices[14]
            gi.ucscAssembly = choices[15]

            galaxyFile=open(galaxyFn, "w")
            galaxyFile.write( 'Genome abbreviation: ' + abbrv + os.linesep)
            galaxyFile.write( 'Genome full name: ' + name + os.linesep)
            galaxyFile.write( 'Track name: ' + ':'.join(GenomeInfo.getSequenceTrackName(abbrv)) + os.linesep)
            galaxyFile.write( 'Temp chromosome names: ' + ' || '.join(chrs) + os.linesep)
            #GenomeImporter.saveTempInfo(abbrv, name, chrs)
            #print 'Chromosomes: '+chrs
            gi.store()


    @staticmethod
    def printTrackNameHistoryElement(genomeAbbrv, genomeFullName, trackName):
        print 'Genome abbreviation: ' + genomeAbbrv
        print 'Genome full name: ' + genomeFullName
        print 'Track name: ' + ':'.join(trackName)

    @staticmethod
    def isPublic():
        return False

    #@staticmethod
    #def getToolDescription():
    #    return 'Genome sequence should be given as one or more FASTA files, optionally compressed'
    #
    @staticmethod
    def getOutputFormat(choices=None):
        return 'hbgenome'

    #
    #@staticmethod
    #def getToolIllustration():
    #    return None
    #
    #@staticmethod
    #def isDebugMode():
    #    return True
