import traceback
from importlib import import_module

from proto.HtmlCore import HtmlCore
from proto.ProtoToolRegister import getProtoToolList
from proto.config.Config import PROTO_TOOL_DIR
from proto.tools.GeneralGuiTool import GeneralGuiTool


class DebugToolImportTool(GeneralGuiTool):
    TOOL_DIR = PROTO_TOOL_DIR
    SELECT_TEXT = '--- Select module ---'

    @classmethod
    def getToolName(cls):
        return "Debug import of ProTo tools"

    @classmethod
    def getInputBoxNames(cls):
        return [('Select tool module with import errors', 'tool'),
                ('Error message', 'error')]

    # @classmethod
    # def getInputBoxOrder(cls):
    #     return None
    #
    # @classmethod
    # def getInputBoxGroups(cls, choices=None):
    #     return None

    @classmethod
    def getOptionsBoxTool(cls):
        tool_info_dict = getProtoToolList(tool_dir=cls.TOOL_DIR, debug_imports=True)
        return [cls.SELECT_TEXT] + \
               [x for x in sorted(set(tool_info.module_name for
                                      tool_info in tool_info_dict.values()))]
    @classmethod
    def getOptionsBoxError(cls, prevChoices):
        if prevChoices.tool != cls.SELECT_TEXT:
            try:
                import_module(prevChoices.tool)
            except Exception:
                core = HtmlCore()
                core.divBegin(divClass='infomessagesmall')
                core.smallHeader('Exception traceback:')
                core.preformatted(traceback.format_exc())
                core.divEnd()
                return '__rawstr__', str(core)

    # @classmethod
    # def getInfoForOptionsBoxKey(cls, prevChoices):
    #     return None
    #
    # @classmethod
    # def getDemoSelections(cls):
    #     return ['testChoice1', '..']
    #
    # @classmethod
    # def getExtraHistElements(cls, choices):
    #     return None

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        import_module(choices.tool)

    @classmethod
    def validateAndReturnErrors(cls, choices):
        if choices.tool == cls.SELECT_TEXT:
            return 'Please select a tool module with import errors'

    # @classmethod
    # def getSubToolClasses(cls):
    #     return None
    #
    # @classmethod
    # def isPublic(cls):
    #     return False
    #
    # @classmethod
    # def isRedirectTool(cls):
    #     return False
    #
    # @classmethod
    # def getRedirectURL(cls, choices):
    #     return ''
    #
    # @classmethod
    # def isHistoryTool(cls):
    #     return True
    #
    # @classmethod
    # def isBatchTool(cls):
    #     return cls.isHistoryTool()
    #
    # @classmethod
    # def isDynamic(cls):
    #     return True
    #
    # @classmethod
    # def getResetBoxes(cls):
    #     return []

    @classmethod
    def getToolDescription(cls):
        from proto.HtmlCore import HtmlCore
        core = HtmlCore()
        core.smallHeader("General description")
        core.paragraph("This tool is used for debugging when an uninstalled tool does not appear "
                       'in the "Explore ProTo tools" tool. This is typically due to an Python '
                       "exception being raised at the import the tool module. This tool "
                       "lists all modules under the tool directory that cannot be imported "
                       "due to an exception. When selecting the tool, a traceback of the "
                       'exception is shown. One can also click "Execute" to store the exception '
                       "within a history element (which will then become red). This is "
                       "useful if one wants to send a bug report for the exception, or if one "
                       "wants to keep a backlog of the error messages.")
        return str(core)

    # @classmethod
    # def getToolIllustration(cls):
    #     return None
    #
    # @classmethod
    # def getFullExampleURL(cls):
    #     return None
    #
    # @classmethod
    # def isDebugMode(cls):
    #     return False
    #
    # @classmethod
    # def getOutputFormat(cls, choices):
    #     return 'html'
    #
    # @classmethod
    # def getOutputName(cls, choices=None):
    #     return cls.getToolSelectionName()
