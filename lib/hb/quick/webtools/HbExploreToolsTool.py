from config.Config import PROTO_HB_TOOL_DIR
from proto.tools.ExploreToolsTool import ExploreToolsTool as ProtoExploreToolsTool
from quick.webtools.GeneralGuiTool import GeneralGuiToolMixin


class HbExploreToolsTool(GeneralGuiToolMixin, ProtoExploreToolsTool):
    TOOL_DIR = PROTO_HB_TOOL_DIR

    @classmethod
    def getToolName(cls):
        return "Explore HyperBrowser ProTo tools"
