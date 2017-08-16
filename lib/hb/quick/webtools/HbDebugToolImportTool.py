from config.Config import PROTO_HB_TOOL_DIR
from proto.tools.DebugToolImportTool import DebugToolImportTool as ProtoDebugToolImportTool
from quick.webtools.GeneralGuiTool import GeneralGuiToolMixin


class HbDebugToolImportTool(GeneralGuiToolMixin, ProtoDebugToolImportTool):
    TOOL_DIR = PROTO_HB_TOOL_DIR

    @classmethod
    def getToolName(cls):
        return "Debug import of HyperBrowser ProTo tools"
