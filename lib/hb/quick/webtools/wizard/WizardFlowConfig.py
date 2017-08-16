class WizardFlowConfig(object):
    def nextStep(self, toolId):
        pass


#FLOW_STEP_DICT = dict([('fetchGsuite1', 'fetch_gsuite_tool'),
#                       ('fetchGsuite2', 'fetch_gsuite_tool'),
#                       ('analyze', 'coll_vs_coll_analysis_tool'),
#                       ('whereToFindGsuite', 'where_to_find'),
#                       ('compileFromHb', '...'),
#                       ('compileFromDatabase', '...')])

class MyFlow(WizardFlowConfig):
    #FLOW_ID = 'coll_vs_coll'

    #def getFirstStep():
    #    return 'fetchGsuite1'
    #
    #def nextStepFromFetchGsuite1(state):
    #    return 'fetchGsuite2'
    #
    #def nextStepFromFetchGsuite2(state):
    #    return 'analyze'
    #
    #def nextStepFromAnalyze(state):
    #    return None

    def nextStep(state):
        return

class Step(object):
    def nextStep(state):
        pass

class FetchGsuiteCommon(Step):
    TOOL_ID = 'fetch_gsuite_tool'

    def nextStep(state):
        whereToFetch = self.getToolClsForStep().whereToFetchGsuite()

        if whereToFetch == 'hb':
            return CompileFromHb(self.getNextMainStep())
        elif whereToFetch == 'already_have_gsuite':
            return self.getNextMainStep()
        else:
            return CompileFromDatabase(self.getNextMainStep())


class CollectionVsCollection(Step):
    def nextStep(state):
        return FetchGsuite1()

    class FetchGsuite1(FetchGsuiteCommon):
        def getNextMainStep():
            return FetchGsuite2()

    class FetchGsuite2(FetchGsuiteCommon):
        def getNextMainStep():
            return Analyze()

    class Analyze(Step):
        def getNextStep():
            return None


class CompileFromHb(Step):
    TOOL_ID = 'compile_from_hb_tool'

    def __init__(self, nextMainStep):
        self._nextMainStep = nextMainStep

    def nextStep(state):
        return self._nextMainStep

#class FetchGsuite(WizardFlowConfig):
#    def getFirstStep():
#        return 'whereToFindGsuite'
#
#    def nextStepFromWhereToFindGsuite(state):
#        if state['where_to_find'] == 'hb':
#            return 'compileFromHb'
#        else:
#            return 'compileFromDatabase'
#
#    def nextStepFromCompileFromHb(state):
#        return 'Back to superclass...'


#Which analysis? (Single collection, track vs collection, collection vs collection)
#Where to get first GSuite? ()

#Compile
#Edit
#Analyze

#flow
#step

def execute(cls):
    if choice.analysis == 'Collection vs collection':
        flow = CollectionVsCollection()
    cls._createNextHistoryElementFromFlow(flow, cls.toolId, choices)

def userHasSelectedC(cls, choices):
    return choices.state == 'C'
