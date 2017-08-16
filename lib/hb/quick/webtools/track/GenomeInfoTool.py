from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.util.GenomeInfo import GenomeInfo
from quick.webtools.util.CommonFunctionsForTools import validateURLs, validateURL, validateUcscValues
import os
import urllib
#This is a template prototyping GUI that comes together with a corresponding web page.
#

class GenomeInfoTool(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Edit genome info"

    @staticmethod
    def getInputBoxNames(prevChoices=None):
        "Returns a list of names for input boxes, implicitly also the number of input boxes to display on page. Each such box will call function getOptionsBoxK, where K is in the range of 1 to the number of boxes"
        return ['Genome build',\
                "Genome name <i>(human readable name to appear in selection boxes, e.g. 'Human Mar. 2006 (hg18/NCBI36)')</i>",\
                'Genome sequence URL(s) <i>(URL(s) for FASTA files of the genome assembly, optionally compressed)</i>',\
                'Genome build source <i>(e.g. NCBI)</i>',\
                'Genome build name <i>(e.g. hg18)</i>',\
                'Species <i>(e.g. Homo sapiens)</i>',\
                'Species taxonomy URL <i>(e.g. http://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?mode=Info&id=9606)</i>',\
                'Assembly details <i>(description of the assembly, HTML code accepted)</i>',\
                'Owners <i>(list of e-mail addresses)</i>',\
                'Access level for genome',\
                'Availability <i>(the type of installations where the genome is available)</i>',\
                'Mapping to UCSC table browser: Clade <i>(e.g. mammal)</i>',\
                'Mapping to UCSC table browser: Genome <i>(e.g. Human)</i>',\
                'Mapping to UCSC table browser: Assembly <i>(e.g. hg18)</i>',\
                'Installed by <i>(uneditable)</i>',\
                'Time of installation <i>(uneditable)</i>',\
                'Marked as correctly installed <i>(uneditable)</i>']
    
    @staticmethod    
    def getOptionsBox1(): 
        '''Returns a list of options to be displayed in the second options box, which will be displayed after a selection is made in the first box.
        prevChoices is a list of selections made by the web-user in the previous input boxes (that is, list containing only one element for this case)        
        '''
        return '__genome__'
    
    @staticmethod    
    def getOptionsBox2(prevChoices):
        #return str(prevChoices[0])
        return GenomeInfo(prevChoices[0]).fullName
        #return os.linesep.join([x + ": " + str(type(getattr(gi, x))) for x in dir(gi)]), 20, False
    
    @staticmethod    
    def getOptionsBox3(prevChoices):
        return os.linesep.join(GenomeInfo(prevChoices[0]).sourceUrls) , 3
    
    @staticmethod    
    def getOptionsBox4(prevChoices):
        return GenomeInfo(prevChoices[0]).genomeBuildSource
    
    @staticmethod    
    def getOptionsBox5(prevChoices):
        return GenomeInfo(prevChoices[0]).genomeBuildName
    
    @staticmethod
    def getOptionsBox6(prevChoices):
        return GenomeInfo(prevChoices[0]).species
    
    @staticmethod    
    def getOptionsBox7(prevChoices):
        return GenomeInfo(prevChoices[0]).speciesTaxonomyUrl
    
    @staticmethod    
    def getOptionsBox8(prevChoices):
        return GenomeInfo(prevChoices[0]).assemblyDetails, 7
    
    @staticmethod    
    def getOptionsBox9(prevChoices):
        return os.linesep.join(GenomeInfo(prevChoices[0]).privateAccessList), 5
    
    @staticmethod    
    def getOptionsBox10(prevChoices):
        return ['All', 'Owners only'] if not    GenomeInfo(prevChoices[0]).isPrivate else ['Owners only', 'All']

    @staticmethod    
    def getOptionsBox11(prevChoices):
        return ['Experimental only', 'All'] if GenomeInfo(prevChoices[0]).isExperimental else ['All', 'Experimental only']
    
    @staticmethod    
    def getOptionsBox12(prevChoices):
        return GenomeInfo(prevChoices[0]).ucscClade
    
    @staticmethod
    def getOptionsBox13(prevChoices):
        return GenomeInfo(prevChoices[0]).ucscGenome
    
    @staticmethod    
    def getOptionsBox14(prevChoices):
        return GenomeInfo(prevChoices[0]).ucscAssembly
        
    @staticmethod
    def getOptionsBox15(prevChoices):
        user = GenomeInfo(prevChoices[0]).installedBy
        return str(user if user else ''), 1, True
    
    @staticmethod
    def getOptionsBox16(prevChoices):
        time = GenomeInfo(prevChoices[0]).timeOfInstallation
        return str(time if time else ''), 1, True

    @staticmethod
    def getOptionsBox17(prevChoices):
        installed = GenomeInfo(prevChoices[0]).installed
        return str(installed), 1, True
    
    @staticmethod
    def getResetBoxes():
        return [1]

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
        '''Is called when execute-button is pushed by web-user.
        Should print output as HTML to standard out, which will be directed to a results page in Galaxy history. If getOutputFormat is anything else than HTML, the output should be written to the file with path galaxyFn.gtr
        If needed, StaticFile can be used to get a path where additional files can be put (e.g. generated image files).
        choices is a list of selections made by web-user in each options box.
        '''
        
        gi=GenomeInfo(choices[0])
        gi.fullName = choices[1]
        urls = choices[2].split()
        gi.sourceUrls = urls
    
        gi.genomeBuildSource = choices[3]
        gi.genomeBuildName = choices[4]
        gi.species = choices[5]
        gi.speciesTaxonomyUrl = choices[6]
        gi.assemblyDetails = choices[7]
        gi.privateAccessList = [v.strip()  for v in choices[8].replace(os.linesep, ' ').replace(',', ' ').split(' ') if v.find('@')>0]
        gi.isPrivate = (choices[9] == 'Owners only')
        gi.isExperimental = (choices[10] == 'Experimental only')
        gi.ucscClade = choices[11]
        gi.ucscGenome = choices[12]
        gi.ucscAssembly = choices[13]
        gi.store()
        
        return "Updated genome %s." % gi.fullName

    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not valid,
        an error text explaining the problem should be returned. The GUI then shows this text
        to the user (if not empty) and greys out the execute button (even if the text is empty).
        If all parameters are valid, the method should return None, which enables the execute button.
        '''
        
        if choices[1].strip() == '':
            return "Genome name box must be filled."
        
        # test if the URLs are alive
        urls = choices[2].strip().split()
        urlError = validateURLs(urls)
        if urlError:
            return urlError
            
        taxonomyUrl = choices[6].strip()
        if taxonomyUrl != '':
            urlError = validateURL(taxonomyUrl)
            if urlError:
                return urlError
        
        if len([v.strip()  for v in choices[8].replace(os.linesep, ' ').replace(',', ' ').split(' ') if not v =='' and v.find('@')<0])>0:
            return 'There is an invalid format inside the E-mail address field'

        ucscError = validateUcscValues([choices[x] for x in [11,12,13]])
        if ucscError:
            return ucscError
        
    @staticmethod
    def isHistoryTool():
        return False
        
    #@staticmethod
    #def isPublic():
    #    return True
    #
    #@staticmethod
    #def isRedirectTool():
    #    return False
    #
    #@staticmethod
    #def getToolDescription():
    #    return ''
    #
    #@staticmethod
    #def getToolIllustration():
    #    return None
    #
    #@staticmethod
    #def isDebugMode():
    #    return True
    #
    #@staticmethod
    #def isRedirectTool():
    #    return False
    #
    #@staticmethod    
    #def getOutputFormat():
    #    return 'html'
    #
    #@staticmethod
    #def validateAndReturnErrors(choices):
    #    '''
    #    Should validate the selected input parameters. If the parameters are not valid,
    #    an error text explaining the problem should be returned. The GUI then shows this
    #    to the user and greys out the execute button. If all parameters are valid, the method
    #    whould return None, which enables the execute button.
    #    '''
    #    return None
