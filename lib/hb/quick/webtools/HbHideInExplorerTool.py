from config.Config import PROTO_HB_TOOL_DIR
from proto.tools.HideInExplorerTool import HideInExplorerTool as ProtoHideInExplorerTool
from quick.webtools.GeneralGuiTool import GeneralGuiToolMixin


class HbHideInExplorerTool(GeneralGuiToolMixin, ProtoHideInExplorerTool):
    TOOL_DIR = PROTO_HB_TOOL_DIR

    @classmethod
    def getToolName(cls):
        return "Hide HB ProTo tool modules from 'Explore HB ProTo tools'"
