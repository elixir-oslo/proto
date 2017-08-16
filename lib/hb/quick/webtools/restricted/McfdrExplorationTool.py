from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
from quick.webtools.GeneralGuiTool import GeneralGuiTool


#This is a template prototyping GUI that comes together with a corresponding web page.
#

class McfdrExplorationTool(GeneralGuiTool):

    @staticmethod
    def getSubToolClasses():
        return [SubTool3, SubTool4]

    @staticmethod
    def getToolName():
        return "Specific MCFDR simulation"

    @staticmethod
    def getInputBoxNames():
        "Returns a list of names for input boxes, implicitly also the number of input boxes to display on page. Each such box will call function getOptionsBoxK, where K is in the range of 1 to the number of boxes"
        return ['underlying pVal','minNumSamples','maxNumSamples','chunkSize','numTests','pValEstimation']

    @staticmethod    
    def getOptionsBox1():
        "Returns a list of options to be displayed in the first options box"
        return '0.1'
    
    @staticmethod    
    def getOptionsBox2(prevChoices): 
        '''Returns a list of options to be displayed in the second options box, which will be displayed after a selection is made in the first box.
        prevChoices is a list of selections made by the web-user in the previous input boxes (that is, list containing only one element for this case)        
        '''
        return '100'
    
    @staticmethod    
    def getOptionsBox3(prevChoices):
        return '10000'

    @staticmethod    
    def getOptionsBox4(prevChoices):
        return '100'

    @staticmethod    
    def getOptionsBox5(prevChoices):
        return '1'

    @staticmethod    
    def getOptionsBox6(prevChoices):
        return ['Davison','ML']

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
        
        print 'temporarily overriding tool, running McFdr2 simulation..'
        from test.sandbox.extra.McFdr2 import analyzeSampleNumAccuracy
        for numSamples in [100,1000,10000]:
            print ''
            print 'numSamples %s: ' % numSamples,
            for i in range(3):
                print analyzeSampleNumAccuracy(numSamples),
        return
    
    
        from proto.RSetup import r
        from numpy import array,minimum
        pVal,minNumSamples,maxNumSamples,chunkSize,numTests = [float(x) for x in choices[:-1]]
        print 'pVal:%.2f, minNumSamples:%i, maxNumSamples:%i, chunkSize:%i, numTests:%i' % (pVal,minNumSamples,maxNumSamples,chunkSize,numTests)
        
        assert (maxNumSamples-minNumSamples)%chunkSize == 0
        assert numTests == 1 #More not yet supported. Should in McFdr be something like the min-max, i.e. the minimum across iterations of the maximum p-value across tests..
        
        pValEstimation = choices[-1]
        assert pValEstimation in ['Davison','ML']
        if pValEstimation=='Davison':
            pFunc = lambda k,n:1.0*(k+1)/(n+1)
        else:
            pFunc = lambda k,n:1.0*(k)/n
            
        numRepl = 10**4
        stdAtMin = [pFunc(k,minNumSamples) for k in r.rbinom(numRepl,minNumSamples,pVal)]
        stdAtMax = [pFunc(k,maxNumSamples) for k in r.rbinom(numRepl,maxNumSamples,pVal)]
        
        mcFdrBestPVals = array([1.0]*numRepl)
        mcFdrSamples = minNumSamples #array([minNumSamples]*numRepl)
        mcFdrExtremes = array(r.rbinom(numRepl,minNumSamples,pVal))
        while mcFdrSamples<maxNumSamples:
            tempMcFdrPVals = pFunc(mcFdrExtremes,mcFdrSamples)
            mcFdrBestPVals = minimum(mcFdrBestPVals,tempMcFdrPVals)
            
            mcFdrSamples += chunkSize
            mcFdrExtremes += array(r.rbinom(numRepl,chunkSize,pVal))
        tempMcFdrPVals = pFunc(mcFdrExtremes,mcFdrSamples)
        mcFdrBestPVals = minimum(mcFdrBestPVals,tempMcFdrPVals)
        assert mcFdrSamples == maxNumSamples
        
        print 'Mean values<br>'
        print 'AtMin:%.7f, AtMax:%.7f, McFdr:%.7f' % tuple([array(x).mean() for x in [stdAtMin, stdAtMax, mcFdrBestPVals]])
        
        breaks = [pVal*2*x/100.0 for x in range(0,101)] +[1.0]
        
        histRes = r.hist(stdAtMin,breaks=breaks,plot=False)
        xVals = histRes['mids']
        yValsStdAtMin = histRes['density']

        histRes = r.hist(stdAtMax,breaks=breaks,plot=False)
        assert xVals == histRes['mids']
        yValsStdAtMax = histRes['density']

        histRes = r.hist(mcFdrBestPVals,breaks=breaks,plot=False)
        assert xVals == histRes['mids']
        yValsMcFdr = histRes['density']
        
        staticFile = GalaxyRunSpecificFile(['pDistr.png'],galaxyFn)
        staticFile.openRFigure()
        staticFile.plotRLines(xVals, [yValsStdAtMin, yValsStdAtMax, yValsMcFdr],alsoOpenAndClose=False,xlab='p-value',ylab='density',xlim=[0,2*pVal])
        r.abline(v=pVal,lty='dotted',col='yellow')
        staticFile.closeRFigure()
        print staticFile.getLink('View estimated pval distribution')
        

    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not valid,
        an error text explaining the problem should be returned. The GUI then shows this text
        to the user (if not empty) and greys out the execute button (even if the text is empty).
        If all parameters are valid, the method should return None, which enables the execute button.
        '''
        return None
    
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
    #
    #@staticmethod
    #def isDebugMode():
    #    return True
    #
    #@staticmethod    
    #def getOutputFormat():
    #    return 'html'
    #


class SubTool3(McfdrExplorationTool):
    @staticmethod
    def getToolName():
        return "Another McFdr simulation"

    @staticmethod
    def getInputBoxNames():
        "Returns a list of names for input boxes, implicitly also the number of input boxes to display on page. Each such box will call function getOptionsBoxK, where K is in the range of 1 to the number of boxes"
        return ['underlying pVal','minNumSamples']

    @staticmethod    
    def getOptionsBox1():
        "Returns a list of options to be displayed in the first options box"
        return '0.1'
    
    @staticmethod    
    def getOptionsBox2(prevChoices): 
        '''Returns a list of options to be displayed in the second options box, which will be displayed after a selection is made in the first box.
        prevChoices is a list of selections made by the web-user in the previous input boxes (that is, list containing only one element for this case)        
        '''
        return '100'

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        print 'This is subclass'


class SubTool4(McfdrExplorationTool):
    @staticmethod
    def getToolName():
        return "Yet Another McFdr simulation"

    @staticmethod
    def getInputBoxNames():
        "Returns a list of names for input boxes, implicitly also the number of input boxes to display on page. Each such box will call function getOptionsBoxK, where K is in the range of 1 to the number of boxes"
        return ['Underlying pVal','MinNumSamples']

    @staticmethod    
    def getOptionsBox1():
        "Returns a list of options to be displayed in the first options box"
        return '0.2'
    
    @staticmethod    
    def getOptionsBox2(prevChoices): 
        '''Returns a list of options to be displayed in the second options box, which will be displayed after a selection is made in the first box.
        prevChoices is a list of selections made by the web-user in the previous input boxes (that is, list containing only one element for this case)        
        '''
        return '10'

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        print 'This is subclass'
