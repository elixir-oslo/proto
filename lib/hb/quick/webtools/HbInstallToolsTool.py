from config.Config import PROTO_HB_TOOL_DIR
from proto.tools.InstallToolsTool import InstallToolsTool as ProtoInstallToolsTool
from quick.webtools.GeneralGuiTool import GeneralGuiToolMixin


class HbInstallToolsTool(GeneralGuiToolMixin, ProtoInstallToolsTool):
    TOOL_DIR = PROTO_HB_TOOL_DIR
    TOOL_ID_PREFIX = 'hb'
    XML_TOOL_DIR = 'proto/hyperbrowser'

    @staticmethod
    def getToolName():
        return "Install HyperBrowser ProTo tool"

    @classmethod
    def getOptionsBoxToolXMLPath(cls, prevChoices):
        return cls._getToolXmlPath(prevChoices), 1, True
