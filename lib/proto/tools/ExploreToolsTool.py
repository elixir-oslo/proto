import os

from proto.ProtoToolRegister import getNonHiddenProtoToolList, HIDDEN_NONTOOL_MODULES_CONFIG_FN
from proto.config.Config import PROTO_TOOL_DIR
from proto.tools.GeneralGuiTool import MultiGeneralGuiTool


class ExploreToolsTool(MultiGeneralGuiTool):
    # For subclass override
    TOOL_DIR = PROTO_TOOL_DIR

    @staticmethod
    def getToolName():
        return "Explore ProTo tools"

    @staticmethod
    def getToolSelectionName():
        return "-----  Select tool -----"

    @staticmethod
    def useSubToolPrefix():
        return True

    @classmethod
    def getSubToolClasses(cls):
        tool_info_dict = getNonHiddenProtoToolList(tool_dir=cls.TOOL_DIR)
        tool_classes = [tool_info.prototype_cls for tool_info in tool_info_dict.values()]
        return sorted(tool_classes, key=lambda c: c.__module__)

    @staticmethod
    def getToolDescription():
        from proto.HtmlCore import HtmlCore
        core = HtmlCore()
        core.smallHeader("General description")
        core.paragraph("This tool is used to try out ProTo tools that have "
                       "not been installed as separate tools in the tool "
                       "menu. This is typically used for development "
                       "purposes, so that one can polish the tool until it "
                       "is finished for deployment in the tool menu. "
                       "When a tool is installed into the menu, the tool "
                       "disappears from the tool list in this tool."
                       "The logic for inclusion in the list is that there "
                       "exists a Python module with a class that inherits "
                       "from GeneralGuiTool, without there existing "
                       "a Galaxy xml file for the tool.")
        core.paragraph("Note: when the list of tools is generated, modules "
                       "under the tool directory that does not contain "
                       "ProTo tool classes are stored and excluded from "
                       "subsequent runs. This is done to improve loading "
                       "times. The hidden tool modules are stored in the "
                       '"%s" ' % os.path.basename(HIDDEN_NONTOOL_MODULES_CONFIG_FN) +
                       'file in the "config" folder. This file can be manually edited if needed.')
        return str(core)
