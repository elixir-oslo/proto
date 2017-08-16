"""
Created on Nov 26, 2015

@author: boris
"""

import quick.gsuite.GSuiteHbIntegration


class BasicModeAnalysisInfoMixin(object):
    """
    classdocs
    
    """
    @staticmethod
    def getInputBoxNamesForAnalysisInfo():
        return [
                ('Basic mode question ID', 'bmQid'),
                ('Analysis info', 'analysisInfo')]

    @classmethod
    def getInputBoxGroups(cls, choices=None):
        if hasattr(super(BasicModeAnalysisInfoMixin, cls), 'getInputBoxGroups'):
            return super(BasicModeAnalysisInfoMixin, cls).getInputBoxGroups(choices)
        return None

    @staticmethod
    def getOptionsBoxBmQid():
        return '__hidden__', None
     
    @staticmethod
    def getOptionsBoxAnalysisInfo(prevChoices):
        if prevChoices.bmQid and prevChoices.bmQid not in ('None', '', None):
            htmlCore = quick.gsuite.GSuiteHbIntegration.getAnalysisQuestionInfoHtml(prevChoices.bmQid)
            return '__rawstr__', str(htmlCore)
