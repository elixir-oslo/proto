import os
from collections import OrderedDict

from proto.ProtoToolRegister import (getProtoToolList, getRelativeModulePath,
                                     retrieveHiddenModulesSet, storeHiddenModules,
                                     HIDDEN_MODULES_CONFIG_FN)
from proto.config.Config import PROTO_TOOL_DIR
from proto.tools.GeneralGuiTool import GeneralGuiTool


class HideInExplorerTool(GeneralGuiTool):
    TOOL_DIR = PROTO_TOOL_DIR

    @classmethod
    def getToolName(cls):
        return "Hide ProTo tool modules from 'Explore ProTo tools'"

    @classmethod
    def getInputBoxNames(cls):
        return [('Select tool modules (files) to show in the ProTo tool explorer', 'tools')]

    # @classmethod
    # def getInputBoxOrder(cls):
    #     return None
    #
    # @classmethod
    # def getInputBoxGroups(cls, choices=None):
    #     return None

    @classmethod
    def _getModuleToModulePathDict(cls):
        tool_info_dict = getProtoToolList(tool_dir=cls.TOOL_DIR)
        modules = sorted(tool_info.module_name for tool_info in tool_info_dict.values())
        return OrderedDict([(module_name, getRelativeModulePath(module_name))
                            for module_name in modules])

    @classmethod
    def getOptionsBoxTools(cls):
        module_to_module_path_dict = cls._getModuleToModulePathDict()
        hidden_tools_set = retrieveHiddenModulesSet(HIDDEN_MODULES_CONFIG_FN)
        return OrderedDict([(module_name, module_path not in hidden_tools_set)
                            for module_name, module_path in module_to_module_path_dict.iteritems()])
    #
    # @classmethod
    # def getOptionsBoxSecondKey(cls, prevChoices):
    #     return ''

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
        module_to_module_path_dict = cls._getModuleToModulePathDict()
        storeHiddenModules(HIDDEN_MODULES_CONFIG_FN,
                           [module_to_module_path_dict[module_name]
                            for module_name, selected in choices.tools.iteritems()
                            if not selected])

    @classmethod
    def validateAndReturnErrors(cls, choices):
        return None

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

    @classmethod
    def isHistoryTool(cls):
        return False

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
        core.paragraph("This tool is used to hide modules containing ProTo tools from "
                       'the "Explore ProTo tools" tool. This is both useful in order to '
                       "to reduce the list, and also to reduce the loading times of the "
                       "explore tool.")
        core.paragraph("Hidden tool modules are stored in the "
                       '"%s" ' % os.path.basename(HIDDEN_MODULES_CONFIG_FN) +
                       'file in the "config" folder. This file can be manually edited if needed.')
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
