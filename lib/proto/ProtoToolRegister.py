import os
import re
import shelve
import sys
import traceback
from collections import namedtuple, OrderedDict
from importlib import import_module

from proto.config.Config import SOURCE_CODE_BASE_DIR, PROTO_TOOL_DIR, PROTO_TOOL_SHELVE_FN, \
    CONFIG_DIR
from proto.tools.GeneralGuiTool import GeneralGuiTool, MultiGeneralGuiTool

MULTI_GENERAL_GUI_TOOL = 'MultiGeneralGuiTool'

EXPLORE_TOOLS_TOOL_CLS_NAME = 'ExploreToolsTool'

DEFAULT_INSTALLED_CLASS_INFO = [('proto.tools.ToolTemplate', 'ToolTemplate'),
                                ('proto.tools.ToolTemplateMinimal', 'ToolTemplate'),
                                ('quick.webtools.ToolTemplate', 'ToolTemplate'),
                                ('quick.webtools.ToolTemplateMinimal', 'ToolTemplate')]

HIDDEN_MODULES_CONFIG_FN = \
    os.path.join(CONFIG_DIR, 'proto_tool_explorer_hidden_modules.txt')

HIDDEN_NONTOOL_MODULES_CONFIG_FN = \
    os.path.join(CONFIG_DIR, 'proto_tool_explorer_hidden_nontool_modules.txt')


ProtoToolInfo = namedtuple('ProtoToolInfo', ['prototype_cls', 'module_name'])
ProtoClassInfo = namedtuple('ProtoClassInfo', ['class_name', 'super_class_list'])


# Public functions

def getInstalledProtoTools():
    tool_shelve = shelve.open(PROTO_TOOL_SHELVE_FN, 'r')
    installed_class_info = [tool_shelve.get(t) for t in tool_shelve.keys() if os.path.exists(
        os.path.join(SOURCE_CODE_BASE_DIR, tool_shelve.get(t)[0].replace('.', os.path.sep)) +
        '.py')]
    tool_shelve.close()
    return installed_class_info


def getUniqueKeyForClass(module_name, class_name):
    module_fn = getRelativeModulePath(module_name)
    return os.path.join(module_fn, class_name)


def getRelativeModulePath(module_name):
    module_fn = os.path.join(SOURCE_CODE_BASE_DIR, module_name.replace('.', os.path.sep))
    return os.path.realpath(module_fn)[len(os.path.realpath(SOURCE_CODE_BASE_DIR)):]


def getProtoToolList(tool_dir=PROTO_TOOL_DIR, debug_imports=False):
    return _commonGetProtoToolList(tool_dir, debug_imports=debug_imports)


def getNonHiddenProtoToolList(tool_dir=PROTO_TOOL_DIR):
    except_modules_set = retrieveHiddenModulesSet(HIDDEN_MODULES_CONFIG_FN)
    except_modules_set.update(retrieveHiddenModulesSet(HIDDEN_NONTOOL_MODULES_CONFIG_FN))
    return _commonGetProtoToolList(tool_dir, except_modules_set=except_modules_set)


def retrieveHiddenModulesSet(hidden_modules_fn):
    if os.path.exists(hidden_modules_fn):
        return set([line.strip() for line in open(hidden_modules_fn)])
    else:
        return set()


def storeHiddenModules(hidden_modules_fn, hidden_module_paths, append=False):
    with open(hidden_modules_fn, 'a' if append else 'w') as config_file:
        for hidden_module_path in hidden_module_paths:
            config_file.write(hidden_module_path + os.linesep)


def getToolPrototype(toolId):
    tool_shelve = None
    try:
        tool_shelve = shelve.open(PROTO_TOOL_SHELVE_FN, 'r')
        module_name, class_name = tool_shelve[str(toolId)]
        module = __import__(module_name, fromlist=[class_name])
        prototype = getattr(module, class_name)(toolId)
    #except KeyError:
    #    prototype = None
    finally:
        if tool_shelve:
            tool_shelve.close()
    return prototype


# Private functions

def _commonGetProtoToolList(tool_dir=PROTO_TOOL_DIR, except_modules_set=set(), debug_imports=False):
    tmpSysPath = _fixSameNameImportIssues()

    pys = _findAllPythonFiles(tool_dir)
    installed_classes_set = _findInstalledClassesSet()

    tool_info_dict = \
        _findAllUninstalledTools(pys, tool_dir, except_modules_set,
                                 installed_classes_set, debug_imports=debug_imports)

    sys.path = tmpSysPath

    return tool_info_dict


def _findInstalledClassesSet():
    installed_class_info = DEFAULT_INSTALLED_CLASS_INFO + getInstalledProtoTools()
    installed_classes_set = set([getUniqueKeyForClass(module, class_name) for
                                 module, class_name in installed_class_info])
    return installed_classes_set


def _fixSameNameImportIssues():
    # To fix import issue if there are modules in /lib and /lib/proto with the
    # same name (e.g. 'config').
    tmpSysPath = sys.path
    if sys.path[0].endswith('/proto'):
        sys.path = tmpSysPath[1:]
    return tmpSysPath


def _filterInstalledSubClassTools(tmp_tool_info_dict, all_installed_sub_classes):
    tool_info_dict = OrderedDict()
    for tool_selection_name, tool_info in tmp_tool_info_dict.iteritems():
        prototype_cls = tool_info.prototype_cls
        if prototype_cls not in all_installed_sub_classes:
            tool_info_dict[tool_selection_name] = tool_info
    return tool_info_dict


def _findAllUninstalledTools(pys, tool_dir, except_modules_set,
                             installed_classes_set, debug_imports=False):
    all_modules = _findAllModulesWithClasses(except_modules_set, pys)

    installed_classes_set.update(_findInstalledSubClasses(all_modules, installed_classes_set))
    tool_info_dict = _getInfoForAllUninstalledTools(
        all_modules, tool_dir, installed_classes_set, debug_imports=debug_imports)

    return tool_info_dict


def _findAllModulesWithClasses(except_modules_set, pys):
    all_modules = []

    for fn in pys:
        module_name = _getModuleNameFromPath(fn)
        if except_modules_set and getRelativeModulePath(module_name) in except_modules_set:
            continue

        class_info_list = _findInfoForAllClasses(fn)
        all_modules.append((module_name, class_info_list))

    return all_modules


def _findInstalledSubClasses(all_modules, except_classes_set):
    all_installed_sub_classes_set = set()

    for module_name, class_info_list in all_modules:
        for class_name, super_classes in class_info_list:
            uniqueKey = getUniqueKeyForClass(module_name, class_name)
            try:
                if uniqueKey in except_classes_set and \
                        MULTI_GENERAL_GUI_TOOL in super_classes and \
                        class_name != EXPLORE_TOOLS_TOOL_CLS_NAME:
                    installed_sub_classes = _getSubClasses(class_name, module_name)
                    all_installed_sub_classes_set.update(installed_sub_classes)
            except Exception as e:
                pass

    return all_installed_sub_classes_set


def _getInfoForAllUninstalledTools(all_modules, tool_dir,
                                   installed_classes_set, debug_imports=False):
    tool_info_dict = OrderedDict()

    for module_name, class_info_list in all_modules:
        module_has_nontool_cls = False
        module_has_tool_cls = False

        for class_name, super_classes in class_info_list:
            uniqueKey = getUniqueKeyForClass(module_name, class_name)
            try:
                if uniqueKey not in installed_classes_set:
                    tool_selection_name, tool_info = \
                        _extractToolInfo(class_name, module_name, tool_dir)
                    if tool_selection_name:
                        module_has_tool_cls = True
                        if not debug_imports:
                            tool_info_dict[tool_selection_name] = tool_info
                    else:
                        module_has_nontool_cls = True
                else:
                    module_has_tool_cls = True
            except Exception as e:
                if debug_imports:
                    tool_selection_name = \
                        _createToolSelectionName(class_name, module_name, tool_dir)
                    tool_info_dict[tool_selection_name] = ProtoToolInfo(class_name, module_name)

        if module_has_nontool_cls and not module_has_tool_cls \
                and not MULTI_GENERAL_GUI_TOOL in super_classes:
            _storeAsNonToolHiddenModule(module_name)

    return tool_info_dict


def _storeAsNonToolHiddenModule(module_name):
    rel_module_name = getRelativeModulePath(module_name)
    if rel_module_name not in \
            retrieveHiddenModulesSet(HIDDEN_NONTOOL_MODULES_CONFIG_FN):
        storeHiddenModules(HIDDEN_NONTOOL_MODULES_CONFIG_FN,
                           [rel_module_name],
                           append=True)


def _getModuleNameFromPath(fn):
    return os.path.splitext(os.path.relpath(
        os.path.abspath(fn), SOURCE_CODE_BASE_DIR))[0].replace(os.path.sep, '.')


def _findInfoForAllClasses(fn):
    with open(fn) as f:
        class_info_list = []
        for line in f:
            match = re.match(r'class +(\w+) *\(([\w ,]+)\)', line)
            if match:
                class_name = match.group(1)
                super_class_list = [super_cls.strip() for super_cls in match.group(2).split(',')]
                class_info_list.append(ProtoClassInfo(class_name, super_class_list))
    return class_info_list


def _getSubClasses(class_name, module_name):
    sub_classes = set()

    module = import_module(module_name)
    prototype_cls = getattr(module, class_name)

    if prototype_cls.getSubToolClasses():
        for sub_cls in prototype_cls.getSubToolClasses():
            sub_classes.add(getUniqueKeyForClass(sub_cls.__module__, sub_cls.__name__))

    return sub_classes


def _extractToolInfo(class_name, module_name, tool_dir):
    module = import_module(module_name)
    prototype_cls = getattr(module, class_name)

    if issubclass(prototype_cls, GeneralGuiTool) \
            and not issubclass(prototype_cls, MultiGeneralGuiTool) \
            and hasattr(prototype_cls, 'getToolName'):
        tool_selection_name = \
            _createToolSelectionName(class_name, module_name, tool_dir)
        tool_info = ProtoToolInfo(prototype_cls, module_name)
        return tool_selection_name, tool_info

    return None, None


def _findAllPythonFiles(tool_dir):
    pys = []
    for d in os.walk(tool_dir, followlinks=True):
        if d[0].find('.svn') == -1:
            pys += [os.path.join(d[0], f) for f in d[2] if f.endswith('.py') and
                    not any(f.startswith(x) for x in ['.', '#', '_'])]
    return pys


def _createToolSelectionName(class_name, module_name, tool_dir):
    tool_dirLen = len(tool_dir.split(os.path.sep)) - \
                 len(SOURCE_CODE_BASE_DIR.split(os.path.sep))
    tool_module = module_name.split('.')[tool_dirLen:]
    if class_name != tool_module[-1]:
        tool_selection_name = '.'.join(tool_module) + \
                              ' [' + class_name + ']'
    else:
        tool_selection_name = '.'.join(tool_module)

    return tool_selection_name
