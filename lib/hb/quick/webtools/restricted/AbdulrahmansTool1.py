#from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.GeneralGuiTool import MultiGeneralGuiTool

from quick.webtools.restricted.ChromCoord import ChromCoord

# This is a template prototyping GUI that comes together with a corresponding
# web page.
##########################################################################
class AbdulrahmansTool1(MultiGeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Test tools Developed by Abdulrahman Azab"
    @staticmethod
    def getSubToolClasses():
        return [ChromCoord]
#########################################################################
#
#


