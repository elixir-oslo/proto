from os import system
from os.path import dirname

from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.util.CommonFunctions import changedWorkingDir
from quick.webtools.GeneralGuiTool import GeneralGuiTool


#import scipy.misc.pilutil as smp
#from os import system
#This is a template prototyping GUI that comes together with a corresponding web page.
#

class GenerateCircosImage(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Generate Circos image"

    @staticmethod
    def getInputBoxNames():
        "Returns a list of names for input boxes, implicitly also the number of input boxes to display on page. Each such box will call function getOptionsBoxK, where K is in the range of 1 to the number of boxes"
        #can have two syntaxes: either a list of stings or a list of tuples where each tuple has two items(Name of box on webPage, name of getOptionsBox)
        return ['select history item','test']

    @staticmethod    
    def getOptionsBox1():
        '''Returns a list of options to be displayed in the first options box
        Alternatively, the following have special meaning:
        '__genome__'
        '__track__'
        ('__history__','bed','wig','...')
        '''
        return '__history__', 'bed','bedgraph','category.bed'
    
    
    @staticmethod    
    def getOptionsBox2(prevChoices):
        return prevChoices[0],1,True
    

    #@staticmethod    
    #def getOptionsBox4(prevChoices):
    #    return ['']

    #@staticmethod
    #def getDemoSelections():
    #    return ['testChoice1','..']
        
    @classmethod    
    def execute(cls, choices, galaxyFn=None, username=''):
        
        histItem = choices[0].split(':')
        filSuffix = ExternalTrackManager.extractFileSuffixFromGalaxyTN(histItem)
        histFile = ExternalTrackManager.extractFnFromGalaxyTN(histItem)
        galaxyOutputFile = GalaxyRunSpecificFile(['circos.png'], galaxyFn)
        
        outputFn = galaxyOutputFile.getDiskPath(True)
        type = 'line' if filSuffix == 'bedgraph' else 'highlight'
        paramDict = {histFile:{'type':type, 'r0':'0.90r','r1':'1.0r'}}
        if type == 'line':
            try:
                vals = [float(line.strip().split()[-1]) for line in open(histFile,'r') if line.strip()[0] == 'c']
            except Exception, e:
                print e
            paramDict[histFile]['max'] = max(vals)
            paramDict[histFile]['min'] = min(vals)
        
        with changedWorkingDir('/usit/invitro/site/circos/circos-0.56/bin/'):
            
            command_line = cls.MakeCircosConfFile(paramDict, galaxyFn, outputFn)
            print outputFn, command_line
            system(command_line)
            #import shlex, subprocess
            #args = shlex.split(command_line)
            #p = subprocess.call(args)
        
        
        '''Is called when execute-button is pushed by web-user.
        Should print output as HTML to standard out, which will be directed to a results page in Galaxy history.
        If getOutputFormat is anything else than HTML, the output should be written to the file with path galaxyFn.
        If needed, StaticFile can be used to get a path where additional files can be put (e.g. generated image files).
        choices is a list of selections made by web-user in each options box.
        '''
        print 'Executing...'

    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not valid,
        an error text explaining the problem should be returned. The GUI then shows this text
        to the user (if not empty) and greys out the execute button (even if the text is empty).
        If all parameters are valid, the method should return None, which enables the execute button.
        '''
        return None
    
    # @classmethod
    # def getTests(cls):
    #     choicesFormType = ['str', 'str']
    #     testRunList = ["$Tool[hb_generate_circos_image]('galaxy:bed:/usit/invitro/data/galaxy/galaxy-dist-hg-dev/database/files/026/dataset_26109.dat:9%20-%20Create%20combination%20track'|'galaxy:bed:/usit/invitro/data/galaxy/galaxy-dist-hg-dev/database/files/026/dataset_26109.dat:9%20-%20Create%20combination%20track')"]
    #     return cls.formatTests(choicesFormType, testRunList)

    #@staticmethod
    #def isPublic():
    #    return False
    #
    #@staticmethod
    #def isRedirectTool():
    #    return False
    #
    #@staticmethod
    #def isHistoryTool():
    #    return True
    #
    #@staticmethod
    #def isDynamic():
    #    return True
    #
    #@staticmethod
    #def getResetBoxes():
    #    return []
    #
    #@staticmethod
    #def getToolDescription():
    #    return ''
    #
    #@staticmethod
    #def getToolIllustration():
    #    return None
    #@staticmethod
    #def isBatchTool():
    #    return False
    #
    #@staticmethod
    #def isDebugMode():
    #    return True
    #
    #@staticmethod    
    #def getOutputFormat(choices):
    #    '''The format of the history element with the output of the tool.
    #    Note that html output shows print statements, but that text-based output
    #    (e.g. bed) only shows text written to the galaxyFn file.
    #    '''
    #    return 'html'
    #
    @staticmethod 
    def MakeCircosConfFile(dataset, galaxyFn, outputFn):
        circosMal = """<<include etc/colors_fonts_patterns.conf>>
        <ideogram>
        <spacing>
        default = 0.005r
        break   = 0.5r
        axis_break_at_edge = yes
        axis_break         = yes
        axis_break_style   = 2
        <break_style 1>
        stroke_color = black
        fill_color   = blue
        thickness    = 0.25r
        stroke_thickness = 2
        </break>
        <break_style 2>
        stroke_color     = black
        stroke_thickness = 2
        thickness        = 1.5r
        </break>
        </spacing>
        
        #<<include ideogram.position.conf>>
        radius           = 0.85r
        thickness        = 30p
        fill             = yes
        fill_color       = black
        stroke_thickness = 2
        stroke_color     = black
        
        #<<include ideogram.label.conf>>
        show_label       = yes
        label_font       = default
        label_radius     = dims(ideogram,radius) + 0.075r
        label_size       = 36
        label_parallel   = yes
        label_case       = upper
        
        #<<include bands.conf>>
        show_bands            = yes
        fill_bands            = yes
        band_stroke_thickness = 2
        band_stroke_color     = white
        band_transparency     = 3
        
        
        </ideogram>
        
        
        #<<include ticks.conf>>
        show_ticks          = yes
        show_tick_labels    = yes
        
        <ticks>
        tick_separation      = 3p
        label_separation     = 5p
        radius               = dims(ideogram,radius_outer)
        multiplier           = 1e-6
        color          = black
        size           = 20p
        thickness      = 4p
        label_offset   = 5p
        format         = %%d
        
        <tick>
        spacing        = 1u
        show_label     = yes
        label_size     = 16p
        </tick>
        
        <tick>
        spacing        = 5u
        show_label     = yes
        label_size     = 18p
        </tick>
        
        <tick>
        spacing        = 10u
        show_label     = yes
        label_size     = 20p
        </tick>
        
        <tick>
        spacing        = 20u
        show_label     = yes
        label_size     = 24p
        </tick>
        </ticks>
        
        karyotype   = %s
        #data/karyotype/karyotype.human.hg19_mod.txt
        
        <image>
        
        dir   = %s
        file  = circos.png
        png   = yes
        svg   = no
        # radius of inscribed circle in image
        radius         = 1500p
        # by default angle=0 is at 3 o'clock position
        angle_offset      = -90
        #angle_orientation = counterclockwise
        auto_alpha_colors = yes
        auto_alpha_steps  = 5
        background = white
        
        </image>
        
        chromosomes_units = 1000000
        chromosomes_display_default = yes
        
        #chromosomes = hs1;hs2;hs3;hs4;hs5;hs6
        %s
        <<include etc/housekeeping.conf>>
        """
        
        plotsMal = "<plots>\n%s\n</plots>\n"
        plotMal = "<plot>\nfile=%s\ntype=%s\nline\nr0=%s\nr1=%s\nmin=%s\nmax=%s\ncolor=black\nthickness=2\nextend_bin=no\naxis=yes\naxis_color=lgrey\naxis_thickness=2\naxis_spacing=0.1\n</plot>\n"
        #% (file, plotType, r0, r1, minVal, maxVal)
        highlightsMal = "<highlights>\n%s\n</highlights>\n"
        highlightMal = "<highlight>\nfile=%s\nr0=%s\nr1= %s\n</highlight>\n" #% (fn, r0, r1)
        
        
        circosConfFile = GalaxyRunSpecificFile(['circos.conf'], galaxyFn)
        dir = dirname(outputFn)
        
        #dataset = {'/usit/titan/u1/kaitre/circosData/100kb_extended_MS_regions.bed':{'type':'highlight', 'r0':'0.90r', 'r1':'0.95r'}}
        #{'/usit/titan/u1/kaitre/circosData/SE_bcell_Factor_of_observed_vs_expected_overlap_per_cytoband.bedgraph':{'type':'line','r0':'0.95r', 'r1':'1.0r','min':'0', 'max':'1500' }\
        #            , '/usit/titan/u1/kaitre/circosData/AP_bcell_Factor_of_observed_vs_expected_overlap_per_cytoband.bedgraph':{'type':'line', 'r0':'0.90r', 'r1':'0.95r', 'min':'0', 'max':'1500'}}
        plotStr = ''
        highlightStr = ''
        for data in dataset.keys():
            if dataset[data]['type'] in ['line','histogram']:
                plotStr += plotMal % (data, dataset[data]['type'], dataset[data]['r0'], dataset[data]['r1'], dataset[data]['min'], dataset[data]['max'])
            
            elif dataset[data]['type'] in ['highlight']:
                highlightStr += highlightMal % (data, dataset[data]['r0'], dataset[data]['r1'])
                
        if plotStr != '':
            plotStr = plotsMal % plotStr
        if highlightStr !='':
            highlightStr = highlightsMal % highlightStr
        #print circosMal % ('data/karyotype/karyotype.human.hg19_mod.txt',dir, plotStr+highlightStr)
        circosConfFile.writeTextToFile(circosMal % ('data/karyotype/karyotype.human.hg19_mod.txt',dir, plotStr+highlightStr))
        #open(circosConfFile.getDiskPath(True), 'w').write(circosMal % ('data/karyotype/karyotype.human.hg19_mod.txt',dir, plotStr+highlightStr))
        
        return 'circos -conf %s -noparanoid' % circosConfFile.getDiskPath()
        
        
            
