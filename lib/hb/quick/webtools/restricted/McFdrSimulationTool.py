from quick.webtools.GeneralGuiTool import GeneralGuiTool
#This is a template prototyping GUI that comes together with a corresponding web page.
#

class McFdrSimulationTool(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Simulate p-values using the MCFDR scheme"

    @staticmethod
    def getInputBoxNames(prevChoices=None):
        "Returns a list of names for input boxes, implicitly also the number of input boxes to display on page. Each such box will call function getOptionsBoxK, where K is in the range of 1 to the number of boxes"
        return ['Number of tests (in the simulated multiple testing experiment):','Step size for increasing #true H1s:',\
                'Number of replications per value of #true H1s:', 'shape1 (a) param of beta-distr:','shape2 (b) param of beta-distr:',\
                'Cutoff h for sequential MC:', 'Max number of samples for sequential MC:','FDR-threshold:','Estimate Pi0 (alternatively pi0=1)',\
                'FDR stopping criterion:', 'Num samples per chunk:', 'Num samples initially (min samples):']
#maxNumSamples, h, fdrThreshold, totalNumTests, stepSize, numReplications,a,b
#totalNumTests, stepSize, numReplications,a,b, h, maxNumSamples, fdrThreshold

    @staticmethod    
    def getOptionsBox1():
        "Returns a list of options to be displayed in the first options box"
        return '60',1
    
    @staticmethod    
    def getOptionsBox2(prevChoices): 
        return '15',2

    @staticmethod    
    def getOptionsBox3(prevChoices): 
        return '1',3

    @staticmethod    
    def getOptionsBox4(prevChoices): 
        return '0.5',0

    @staticmethod    
    def getOptionsBox5(prevChoices): 
        return '25'

    @staticmethod    
    def getOptionsBox6(prevChoices): 
        return '20'

    @staticmethod    
    def getOptionsBox7(prevChoices): 
        return '1000'

    @staticmethod    
    def getOptionsBox8(prevChoices): 
        return '0.1'

    @staticmethod    
    def getOptionsBox9(prevChoices): 
        return ['By Pounds&Cheng','By Convest','By Histf1','No (1.0)']

    @staticmethod    
    def getOptionsBox10(prevChoices):
        return ['Simultaneous','Individual']

    @staticmethod    
    def getOptionsBox11(prevChoices):
        return '10'

    @staticmethod    
    def getOptionsBox12(prevChoices):
        return '100'
    
    @staticmethod
    def getDemoSelections():
        #totalNumTests, stepSize, numReplications,a,b, h, maxNumSamples, fdrThreshold 
        #return ['100', '10']
        return ['100', '10', '1', '0.5', '25', '20', '1000', '0.1','Yes','Simultaneous','50','100']

    @classmethod    
    def execute(cls, choices, galaxyFn=None, username=''):
        '''Is called when execute-button is pushed by web-user.
        Should print output as HTML to standard out, which will be directed to a results page in Galaxy history.
        If needed, StaticFile can be used to get a path where additional files can be put (e.g. generated image files).
        choices is a list of selections made by web-user in each options box.
        '''
        import datetime
        print 'Analysis initiated at time: ',datetime.datetime.now()
        print 'Corresponding batch command line:<br>', '$Tool[mc_fdr_simulation_tool](%s)' % '|'.join(choices)
        
        #maxNumSamples, h, fdrThreshold, totalNumTests, stepSize, numReplications,a,b
        totalNumTests, stepSize, numReplications,a,b, h, maxNumSamples, fdrThreshold,estimatePi0, fdrStoppingCriterion, samplesPerChunk, samplesInitially = choices
        assert not any([x in ['',None] for x in choices]), 'choices: ' + str(choices)
        from test.sandbox.extra.McFdr import Experiment, MultipleTestCollection, Simulator
        if estimatePi0.lower().startswith('no'):
            MultipleTestCollection.ESTIMATE_PI0 = False
        else:
            MultipleTestCollection.ESTIMATE_PI0 = estimatePi0[3:]
        
        assert fdrStoppingCriterion in ['Simultaneous','Individual']
        MultipleTestCollection.SIMULTANOUS_FDR_STOPPING_CRITERION = (fdrStoppingCriterion == 'Simultaneous')
            
        Simulator.NUM_SAMPLES_PER_CHUNK = int(samplesPerChunk)
        Simulator.NUM_SAMPLES_INITIALLY = int(samplesInitially)
        
        print 'Estimate Pi0: ',estimatePi0
        print 'FDR Stopping Criterion: ', fdrStoppingCriterion 
        print 'NumSamplesPerChunk: ',samplesPerChunk
        print 'NumSamplesInitially: ',samplesInitially
        
        from proto.RSetup import r
        if estimatePi0 == 'By Convest':
            r.source("http://www.nr.no/~egil/convest.R")
        #elif estimatePi0 == 'By Histf1':
        r('library(pi0)')
        if ',' in stepSize:
            stepSize = [int(x) for x in stepSize.split(',')]
        else:
            stepSize = int(stepSize)
        Experiment.compareCutoffSchemes(int(maxNumSamples), int(h), float(fdrThreshold),\
                                        int(totalNumTests), stepSize, int(numReplications)\
                                        ,float(a),float(b), galaxyFn)
        
    @staticmethod
    def isPublic():
        return True

    @staticmethod
    def getToolDescription():
        return 'samplesPerChunk: how many samples in a chunk before checking stopping criterion'
    #    
    #@staticmethod
    #def getToolIllustration():
    #    return None
    #
    #@staticmethod
    #def isDebugMode():
    #    return True
