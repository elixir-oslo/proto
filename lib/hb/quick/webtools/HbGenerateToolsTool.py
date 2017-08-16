import re

from config.Config import PROTO_HB_TOOL_DIR
from proto.HtmlCore import HtmlCore
from quick.webtools.GeneralGuiTool import GeneralGuiToolMixin
from proto.tools.GenerateToolsTool import GenerateToolsTool as ProtoGenerateToolsTool


class HbGenerateToolsTool(GeneralGuiToolMixin, ProtoGenerateToolsTool):
    TOOL_DIR = PROTO_HB_TOOL_DIR
    WEB_CONTROLLER = 'hyper'
    EXPLORE_TOOL_ID = 'hb_proto_explore_tools_tool'

    @staticmethod
    def getToolName():
        return "Generate HyperBrowser ProTo tool"

    @classmethod
    def _getProtoToolSymlinkedPackageName(cls, prevChoices):
        return '.'.join(['quick', 'webtools'] + cls._getSelectedDirs(prevChoices))

    @classmethod
    def getOptionsBoxPackageNameInfo(cls, prevChoices):
        core = HtmlCore()
        core.divBegin(divClass='infomessagesmall')
        core.append('Package name selected: ')
        core.emphasize(cls._getProtoToolPackageName(prevChoices))
        core.line('')
        core.line('')
        core.append('To import tool, use equivalent package name: ')
        core.emphasize(cls._getProtoToolSymlinkedPackageName(prevChoices))
        core.divEnd()
        return '__rawstr__', str(core)

    @classmethod
    def validateAndReturnErrors(cls, choices):
        errorMsg = super(HbGenerateToolsTool, cls).validateAndReturnErrors(choices)
        if errorMsg:
            return errorMsg

        for dirName in cls._getSelectedDirs(choices):
            if dirName and not re.match(r'^[a-z]+$', dirName):
                return 'No special characters are allowed for directory names, ' \
                       'only lowercase letters [a-z]: ' + dirName

        if choices.moduleName and not re.match(r'^[A-Z][a-zA-Z0-9]+Tool$', choices.moduleName):
            return 'The module name must be in CamelCase and end with "Tool". ' \
                   'No underscores or other special characters are allowed. ' \
                   'Current module name : ' + choices.moduleName
