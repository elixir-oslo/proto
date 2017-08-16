import os
from urllib import quote

from proto.HtmlCore import HtmlCore
from proto.config.Config import URL_PREFIX, PROTO_TOOL_DIR, SOURCE_CODE_BASE_DIR
from proto.tools.GeneralGuiTool import GeneralGuiTool


class GenerateToolsTool(GeneralGuiTool):
    MAX_DIR_LEVELS = 6
    NO_SELECTION = '--- Select a tool directory ---'
    NEW_DIR = 'Create a new directory...'

    # For subclass override
    TOOL_DIR = PROTO_TOOL_DIR
    WEB_CONTROLLER = 'proto'
    EXPLORE_TOOL_ID = 'proto_explore_tools_tool'

    def __new__(cls, *args, **kwargs):
        cls._setupExtraBoxMethods()
        return GeneralGuiTool.__new__(cls, *args, **kwargs)

    @staticmethod
    def getToolName():
        return "Generate ProTo tool"

    @classmethod
    def _getDirSelectionInputBoxNames(cls):
        inputBoxNames = []
        for i in range(cls.MAX_DIR_LEVELS):
            dirSelText = '&nbsp;&nbsp;' * i
            if i > 0:
                dirSelText += '-> '
            dirSelText += 'Choose directory for new tool (level %s)' % (i + 1)
            inputBoxNames += [(dirSelText, 'dirLevel%s' % i)]

            newDirText = '&nbsp;&nbsp;' * i + 'Name of new directory'
            inputBoxNames += [(newDirText, 'newDir%s' % i)]
        return inputBoxNames

    @classmethod
    def getInputBoxNames(cls):
        return [('', 'hidden')] + \
                cls._getDirSelectionInputBoxNames() +\
               [('Package name', 'packageNameInfo'),
                ('Module/class name', 'moduleName'),
                ('Tool name', 'toolName'),
                ('Use template with inline documentation', 'template')]

    #@staticmethod
    #def getResetBoxes():
    #    return ['moduleName']

    @staticmethod
    def getOptionsBoxHidden():
        # Just to make sure that the variable input boxes always take prevChoices
        return '__hidden__', ''

    @classmethod
    def _getSelectedDirs(cls, prevChoices, index=MAX_DIR_LEVELS):
        dirs = []
        for i in range(index):
            dirSelection = getattr(prevChoices, 'dirLevel%s' % i)

            if dirSelection == cls.NEW_DIR:
                dirSelection = getattr(prevChoices, 'newDir%s' % i).strip()

            if dirSelection is not None and dirSelection != cls.NO_SELECTION:
                dirs.append(dirSelection)
            else:
                break

        return dirs

    @classmethod
    def _getOptionsBoxDirLevel(cls, prevChoices, index):
        prevDirLevelKey = 'dirLevel%s' % (index - 1)
        prevDirLevel = getattr(prevChoices, prevDirLevelKey) if \
            hasattr(prevChoices, prevDirLevelKey) else ''
        if index == 0 or \
                (prevDirLevel and prevDirLevel != cls.NO_SELECTION and
                    not (prevDirLevel == cls.NEW_DIR and
                         not getattr(prevChoices, 'newDir%s' % (index - 1)))):

            selectedDir = os.path.sep.join([cls.TOOL_DIR] +
                                           cls._getSelectedDirs(prevChoices, index))
            try:
                subDirs = sorted([x for x in os.listdir(selectedDir) if
                           os.path.isdir(os.sep.join([selectedDir, x]))])
            except:
                subDirs = []
            return [cls.NO_SELECTION] + subDirs + [cls.NEW_DIR]

    @classmethod
    def _getOptionsBoxNewDir(cls, prevChoices, index):
        curDirChoice = getattr(prevChoices, 'dirLevel%s' % index)
        if curDirChoice == cls.NEW_DIR:
            return '', 1

    @classmethod
    def _setupExtraBoxMethods(cls):
        from functools import partial
        for i in xrange(cls.MAX_DIR_LEVELS):
            setattr(cls, 'getOptionsBoxDirLevel%s' % i,
                    partial(cls._getOptionsBoxDirLevel, index=i))
            setattr(cls, 'getOptionsBoxNewDir%s' % i,
                    partial(cls._getOptionsBoxNewDir, index=i))

        from gold.application.LogSetup import logMessage

    @classmethod
    def _getProtoRelToolDirs(cls):
        assert cls.TOOL_DIR.startswith(SOURCE_CODE_BASE_DIR)
        return cls.TOOL_DIR[len(SOURCE_CODE_BASE_DIR) + 1:].split(os.path.sep)

    @classmethod
    def _getProtoToolPackageName(cls, prevChoices):
        return '.'.join(cls._getProtoRelToolDirs() + cls._getSelectedDirs(prevChoices))

    @classmethod
    def getOptionsBoxPackageNameInfo(cls, prevChoices):
        core = HtmlCore()
        core.divBegin(divClass='infomessagesmall')
        core.append('Package name selected: ')
        core.emphasize(cls._getProtoToolPackageName(prevChoices))
        core.divEnd()
        return '__rawstr__', str(core)

    @staticmethod
    def getOptionsBoxModuleName(prevChoices):
        return 'ChangeMeTool'

    @staticmethod
    def getOptionsBoxToolName(prevChoices):
        return 'Title of tool'

    @staticmethod
    def getOptionsBoxTemplate(prevChoices):
        return ['Yes', 'No']

    @classmethod
    def _getPackageDir(cls, selectedDirs):
        return os.path.sep.join([cls.TOOL_DIR] + selectedDirs)

    @classmethod
    def _getPyName(cls, choices):
        packageDir = cls._getPackageDir(cls._getSelectedDirs(choices))
        return packageDir + '/' + choices.moduleName + '.py'

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        selectedDirs = cls._getSelectedDirs(choices)
        packageDir = cls._getPackageDir(selectedDirs)
        if not os.path.exists(packageDir):
            os.makedirs(packageDir)

        for i in range(len(selectedDirs)):
            init_py = os.path.sep.join([cls.TOOL_DIR] + selectedDirs[0:i+1]) + '/__init__.py'
            if not os.path.exists(init_py):
                print 'creating ', init_py
                open(init_py, 'a').close()

        if choices.template == 'Yes':
            templatefn = os.path.join(cls.TOOL_DIR, 'ToolTemplate.py')
        else:
            templatefn = os.path.join(cls.TOOL_DIR, 'ToolTemplateMinimal.py')

        with open(templatefn) as t:
            template = t.read()

        #template = re.sub(r'ToolTemplate', choices.moduleName, template)
        template = template.replace('ToolTemplate', choices.moduleName)
        template = template.replace('Tool not yet in use', choices.toolName)

        pyName = cls._getPyName(choices)
        with open(pyName, 'w') as p:
            p.write(template)

        numExcludedDirs = len(cls.TOOL_DIR.split(os.path.sep)) - \
            len(SOURCE_CODE_BASE_DIR.split(os.path.sep))
        exploreSubClassId = '.'.join(cls._getProtoRelToolDirs()[numExcludedDirs:] +
                                     selectedDirs + [choices.moduleName])
        explore_id = quote(exploreSubClassId + ': ' + choices.toolName)
        print 'Tool generated: <a href="%s/%s/?tool_id=%s&sub_class_id=%s">%s: %s</a>' % \
              (URL_PREFIX, cls.WEB_CONTROLLER, cls.EXPLORE_TOOL_ID,
               explore_id, choices.moduleName, choices.toolName)
        print 'Tool source path:', pyName

    @classmethod
    def validateAndReturnErrors(cls, choices):
        for dirName in cls._getSelectedDirs(choices):
            if not dirName:
                return 'Please enter a directory name'

            if dirName and dirName != dirName.lower():
                return 'Please use all lowercase letters for the directory name: ' + dirName

            if '.' in dirName:
                return 'Period characters, i.e. ".", are not allowed in a directory name: ' \
                       + dirName

        pyName = cls._getPyName(choices)
        if os.path.exists(pyName):
            return 'Python module "%s" already exists. Please rename the module or ' % pyName + \
                   'select another package/directory.'

    @staticmethod
    def getToolDescription():
        core = HtmlCore()
        core.smallHeader("General description")
        core.paragraph("This tool is used to dynamically generate a Python "
                       "module defining a new ProTo tool. After tool "
                       "execution, The tool will be available from the "
                       "'ProTo tool explorer' tool for development purposes.")
        core.divider()
        core.smallHeader("Parameters")
        core.descriptionLine("Choose directory for new tool",
                             "Hierarchical selection of directory in which to "
                             "place the new tool. The directory structure defines "
                             "the Python package which is used if one needs to import "
                             "the tool. The package name is automatically shown in an info "
                             "box according to the selections. It is also possible "
                             "to create new directories. Note that the creation of "
                             "new directories happens at execution of this tool. ",
                             emphasize=True)
        core.descriptionLine("Module/class name",
                             "The name of the Python module (filename) and "
                             "class for the new tool. For historical reasons, "
                             "ProTo uses 'MixedCase' naming for both the "
                             "module and the class. By convention, it is "
                             "advised (but not required) to end the name "
                             "with 'Tool', e.g. 'MyNewTool'. This will create "
                             "a Python module 'MyNewTool.py' with the class "
                             "'MyNewTool', inheriting from "
                             "'proto.GeneralGuiTool'.", emphasize=True)
        core.descriptionLine("Tool name",
                             "A string with the name or title of the tool. "
                             "This will appear on the top of the tool GUI "
                             "as well as being the default value for the "
                             "tool name in the menu (which can be changed "
                             "when installing).", emphasize=True)
        core.descriptionLine("Use template with inline documentation",
                             "The new Python module is based upon a template"
                             "file containing a simple example tool with "
                             "two option boxes (one selection box and one "
                             "text box). There are two such template files, "
                             "one that contains inline documentation of the "
                             "methods and possible choices, and one without "
                             "the documentation. Advanced users could select "
                             "the latter to make the tool code itself shorter "
                             "and more readable.", emphasize=True)
        return str(core)
