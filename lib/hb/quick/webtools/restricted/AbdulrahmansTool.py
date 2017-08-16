#from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.GeneralGuiTool import MultiGeneralGuiTool

# from quick.webtools.restricted.TestTool import TestTool
from quick.webtools.restricted.TestTool1 import TestTool1
from collections import OrderedDict

# This is a template prototyping GUI that comes together with a corresponding
# web page.

class AbdulrahmansTool(MultiGeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Abdulrahman's tools"

    @staticmethod
    def getToolSelectionName():
        return "-----  Select test tool"

    @staticmethod
    def getSubToolSelectionTitle():
        return 'Select the test tool to run:'


    @staticmethod
    def getSubToolClasses():
        return [TestTool1]
        
    @staticmethod
    def isPublic():
        '''
        Specifies whether the tool is accessible to all users. If False, the
        tool is only accessible to a restricted set of users as defined in
        LocalOSConfig.py.
        '''
        return True
    @staticmethod
    def getToolDescription():
        '''
        Specifies a help text in HTML that is displayed below the tool.
        '''
        #string = 'This tool does two things:<br><ul>'
        #string += '<li>Thing 1</li>'
        #string += '<li>Thing 2</li></ul>'
        
        #return string
    
    @staticmethod
    def getFullExampleURL():
        return 'https://hyperbrowser.uio.no/dev2/u/azab/p/universal-import-tool-user-guide'   
