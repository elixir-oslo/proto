from quick.webtools.GeneralGuiTool import MultiGeneralGuiTool

# This is a template prototyping GUI that comes together with a corresponding
# web page.

class NullModelArticleTool(MultiGeneralGuiTool):
    @staticmethod
    def getSubToolClasses():
        return [PlotFigure1Tool, PlotFigure2Tool]

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Tools used in article: Monte Carlo null models for genomic data"

    @staticmethod
    def isPublic():
        return True


class PlotFigure1Tool(NullModelArticleTool):
    rCode =\
'''plotFig1 = function(fn) {
  r=read.csv(fn, sep='\t')
  plot(r[,2], r[,4], xlim=c(0,0.2), ylim=c(0,0.2),
       xlab='Preserving only the number of TFBS',
       ylab='Preserving empiric inter-TFBS distances',
       main='Do TFBS fall more than expected inside genes?')
  lines(0:1, 0:1, lty='dashed')
}
'''

    @staticmethod
    def getToolSelectionName():
        return "Plot figure 1 of manuscript"

    @staticmethod
    def getInputBoxNames():
        return ['Select 4-column tabular data for plot (where column 2 and 4 will be used)'] #Alternatively: [ ('box1','key1'), ('box2','key2') ]


    @staticmethod
    def getOptionsBox1(): # Alternatively: getOptionsBoxKey1()
        return ('__history__','tabular')

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
        from proto.RSetup import r
        from quick.application.ExternalTrackManager import ExternalTrackManager
        from proto.hyperbrowser.HtmlCore import HtmlCore
        dataFn = ExternalTrackManager.extractFnFromGalaxyTN(choices[0])
        sf = GalaxyRunSpecificFile(['fig1.png'], galaxyFn)
        sf.openRFigure()
        r(PlotFigure1Tool.rCode)(dataFn)
        sf.closeRFigure()
        core = HtmlCore()
        core.begin()
        core.image(sf.getURL() )
        core.end()
        print str(core)

    @staticmethod
    def getOutputFormat(choices):
        return 'customhtml'

    @staticmethod
    def validateAndReturnErrors(choices):
        from quick.application.ExternalTrackManager import ExternalTrackManager

        if not choices[0]:
            return 'No tabular history elements selected. Please select a history element with 4-column tabular data.'

        dataFn = ExternalTrackManager.extractFnFromGalaxyTN(choices[0])

        if len( open(dataFn).readline().split('\t') ) != 4:
            return 'Selected history element does not contain 4-column tabular data.'

    @classmethod
    def getToolDescription(cls):
        '''
        Specifies a help text in HTML that is displayed below the tool.
        '''
        from proto.hyperbrowser.HtmlCore import HtmlCore
        core = HtmlCore()
        core.descriptionLine('R-code', cls._exampleText(cls.rCode))
        return str(core)

    @staticmethod
    def isPublic():
        return True


class PlotFigure2Tool(NullModelArticleTool):
    rCode = \
'''plotFig1 = function(fn) {
  r=read.csv(fn, sep='\t')
  up = r[,1]
  ip = r[,2]
  is = r[,3]
  us = r[,4]
  plot(sort(up), type='l',
       xlab='Tests (bins corresponding to the 50 lowest p-values for each assumption)',
       ylab='P-value', ylim=c(0,0.35))
  lines(sort(ip), col='blue', lty='dashed')
  lines(sort(us), col='darkgreen', lty='dotted')
  lines(sort(is), col='red', lty='dotdash')
  legend('bottomright',
         legend=list('Uniform point location',
                     'Preserving inter-point distances',
                     'Uniform segment location',
                     'Preserving inter-segment location'),
         col=c('black','blue','darkgreen','red'), lty=c(1,2,3,4))
}
'''

    @staticmethod
    def getToolSelectionName():
        return "Plot figure 2 of manuscript"

    @staticmethod
    def getInputBoxNames():
        return ['Select 4-column tabular data for plot'] #Alternatively: [ ('box1','key1'), ('box2','key2') ]


    @staticmethod
    def getOptionsBox1(): # Alternatively: getOptionsBoxKey1()
        return ('__history__','tabular')

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
        from proto.RSetup import r
        from quick.application.ExternalTrackManager import ExternalTrackManager
        from proto.hyperbrowser.HtmlCore import HtmlCore
        dataFn = ExternalTrackManager.extractFnFromGalaxyTN(choices[0])
        sf = GalaxyRunSpecificFile(['fig2.png'], galaxyFn)
        sf.openRFigure()
        r(PlotFigure2Tool.rCode)(dataFn)
        sf.closeRFigure()
        core = HtmlCore()
        core.begin()
        core.image(sf.getURL() )
        core.end()
        print str(core)

    @staticmethod
    def getOutputFormat(choices):
        return 'customhtml'

    @staticmethod
    def validateAndReturnErrors(choices):
        from quick.application.ExternalTrackManager import ExternalTrackManager

        if not choices[0]:
            return 'No tabular history elements selected. Please select a history element with 4-column tabular data.'

        dataFn = ExternalTrackManager.extractFnFromGalaxyTN(choices[0])

        if len( open(dataFn).readline().split('\t') ) != 4:
            return 'Selected history element does not contain 4-column tabular data.'

    @classmethod
    def getToolDescription(cls):
        '''
        Specifies a help text in HTML that is displayed below the tool.
        '''
        from proto.hyperbrowser.HtmlCore import HtmlCore
        core = HtmlCore()
        core.descriptionLine('R-code', cls._exampleText(cls.rCode))
        return str(core)

    @staticmethod
    def isPublic():
        return True
