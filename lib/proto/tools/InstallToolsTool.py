import os
import re
import shutil
from cgi import escape

from proto.ProtoToolRegister import getProtoToolList
from proto.config.Config import (GALAXY_TOOL_CONFIG_FILE, PROTO_TOOL_DIR, SOURCE_CODE_BASE_DIR)
from proto.config.GalaxyConfigParser import GALAXY_BASE_DIR
from proto.tools.GeneralGuiTool import GeneralGuiTool


class InstallToolsTool(GeneralGuiTool):
    SELECT_TOOL_STR = '--- Select tool ---'

    # For subclass override
    TOOL_DIR = PROTO_TOOL_DIR
    XML_TOOL_DIR = 'proto'
    TOOL_ID_PREFIX = 'proto'

    @classmethod
    def _getToolInfoDict(cls):
        return getProtoToolList(tool_dir=cls.TOOL_DIR)

    @classmethod
    def _getPrototype(cls, tool):
        try:
            prototype = cls._getToolInfoDict()[tool].prototype_cls()
        except:
            prototype = None
        return prototype

    @staticmethod
    def getToolName():
        return "Install ProTo tool"

    @staticmethod
    def getInputBoxNames():
        return [('Select tool', 'tool'),
                ('Tool ID', 'toolID'),
                ('Tool name', 'name'),
                ('Tool description', 'description'),
                ('Tool XML file', 'toolXMLPath'),
                ('Select section', 'section')]

    @staticmethod
    def getResetBoxes():
        return [1, 2]

#    @staticmethod
#    def isHistoryTool():
#        return False

    @staticmethod
    def useSubToolPrefix():
        return True

    @classmethod
    def getOptionsBoxTool(cls):
        tool_info_dict = cls._getToolInfoDict()
        return [cls.SELECT_TOOL_STR] + sorted(tool_info_dict.keys())

    @classmethod
    def getOptionsBoxToolID(cls, prevChoices):
        import inflection
        if prevChoices.tool is None or prevChoices.tool == cls.SELECT_TOOL_STR:
            return ''
        tool_info_dict = cls._getToolInfoDict()
        module_name = tool_info_dict[prevChoices.tool].prototype_cls.__name__
        return cls.TOOL_ID_PREFIX + '_' + inflection.underscore(module_name)

    @classmethod
    def getOptionsBoxName(cls, prevChoices):
        prototype = cls._getPrototype(prevChoices.tool)
        if prototype is not None:
            return prototype.getToolName()

    @classmethod
    def getOptionsBoxDescription(cls, prevChoices):
        return ''

    @classmethod
    def _getProtoRelToolDirs(cls, fromBase=False):
        cmpDir = GALAXY_BASE_DIR if fromBase else SOURCE_CODE_BASE_DIR
        assert cls.TOOL_DIR.startswith(cmpDir)
        return cls.TOOL_DIR[len(cmpDir) + 1:].split(os.path.sep)

    @classmethod
    def _getToolXmlPath(cls, prevChoices):
        prototype = cls._getPrototype(prevChoices.tool)
        if prototype is not None:
            package = prototype.__module__.split('.')
            package_dir = os.path.sep.join(package[len(cls._getProtoRelToolDirs()):-1])
            return package_dir + os.path.sep + prototype.__class__.__name__ + '.xml' \
                if package_dir else prototype.__class__.__name__ + '.xml'

    @classmethod
    def getOptionsBoxToolXMLPath(cls, prevChoices):
        return cls._getToolXmlPath(prevChoices)

    @classmethod
    def getOptionsBoxSection(cls, prevChoices):
        toolConf = GalaxyToolConfig()
        return toolConf.getSections()

    #@classmethod
    #def getOptionsBoxInfo(cls, prevChoices):
    #    txt = ''
    #    if prevChoices.tool and prevChoices.section:
    #        txt = 'Install %s into %s' % (prevChoices.tool, prevChoices.section)
    #    tool_cls = prevChoices.tool
    #    prototype = cls.prototype
    #    tool_file = prevChoices.toolXMLPath
    #    xml = cls.toolConf.addTool(prevChoices.section, tool_file)
    #    tool_xml = cls.toolConf.createToolXml(tool_file, prevChoices.toolID, prevChoices.name, prototype.__module__, prototype.__class__.__name__, prevChoices.description)
    #    return 'rawstr', '<pre>' + escape(xml) + '</pre>' + '<pre>' + escape(tool_xml) + '</pre>'

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        # txt = ''
        # if choices.tool and choices.section:
        #     txt = 'Install %s into %s' % (choices.tool, choices.section)
        # tool_cls = choices.tool

        prototype = cls._getPrototype(choices.tool)
        tool_file = os.path.join(cls.XML_TOOL_DIR, choices.toolXMLPath)
        toolConf = GalaxyToolConfig()
        xml = toolConf.addTool(choices.section, tool_file)
        tool_xml = toolConf.createToolXml(choices.toolID,
                                          choices.name, cls.TOOL_ID_PREFIX,
                                          prototype.__module__,
                                          prototype.__class__.__name__,
                                          choices.description)

        abs_tool_xml_path = os.path.join(cls.TOOL_DIR, choices.toolXMLPath)

        try:
            os.makedirs(os.path.dirname(abs_tool_xml_path))
        except:
            pass

        with open(abs_tool_xml_path, 'w') as tf:
            tf.write(tool_xml)

        toolConf.write()

        from proto.HtmlCore import HtmlCore
        core = HtmlCore()

        extraJavaScriptCode = '''
<script type="text/javascript">
    $().ready(function() {
        $("#reload_toolbox").click(function(){
            $.ajax({
            url: "/api/configuration/toolbox",
            type: 'PUT'
            }).done(function() {
                    top.location.reload();
                }
            );
        });
    });
</script>
'''
        core.begin(extraJavaScriptCode=extraJavaScriptCode)
        core.link('Reload toolbox/menu', url='#', args='id="reload_toolbox"')
        core.preformatted(escape(xml))
        core.preformatted(escape(tool_xml))
        core.end()
        print>>open(galaxyFn, 'w'), core

    @classmethod
    def validateAndReturnErrors(cls, choices):
        if choices.tool == cls.SELECT_TOOL_STR:
            return 'Please select a ProTo tool to install in the menu'

        if not choices.toolID or len(choices.toolID) < 6 or \
                not re.match(r'^[a-z0-9_]+$', choices.toolID):
            return 'Tool ID must be at least 6 characters, ' \
                   'all lowercase characters or underscore, ' \
                   'and not contain special characters: ' + choices.toolID

        if not choices.toolID.startswith(cls.TOOL_ID_PREFIX + '_'):
            return 'Tool ID must start with "%s": %s' % \
                   (cls.TOOL_ID_PREFIX + '_', choices.toolID)

    @classmethod
    def getToolDescription(cls):
        from proto.HtmlCore import HtmlCore
        core = HtmlCore()
        core.smallHeader("General description")
        core.paragraph(
            "This tool is used to install ProTo tools into the tool menu. "
            "The installation process creates a Galaxy tool XML file and "
            "adds the tool to the tool menu (in the 'tool_conf.xml' file). "
            "After execution, the XML file has been generated and added "
            "to the tool configuration file, but Galaxy needs to reload "
            "the tool menu for it to become visible. This is done by a "
            "Galaxy administrator, either from the Admin menu, or from a "
            "link in the output history element from this tool.")
        core.paragraph("Note that the after this tool has been executed "
                       "but before a Galaxy administrator has reloaded the "
                       "tool menu, the tool is not available from neither "
                       "of the 'ProTo tool explorer' tool or from the "
                       "Galaxy menu.")
        core.divider()
        core.smallHeader("Parameters")

        core.descriptionLine("Select tool", "The tool to install.",
                             emphasize=True)
        core.descriptionLine("Tool ID",
                             "The Galaxy tool id for the new tool to be "
                             "created. This is the 'id' argument to the "
                             "<tool> tag in the tool XML file.",
                             emphasize=True)
        core.descriptionLine("Tool name",
                             "The name of the tool as it will appear in the "
                             "tool menu. The tool name will appear as a HTML "
                             "link.", emphasize=True)
        core.descriptionLine("Tool description",
                             "The description of the tool as it will appear "
                             "in the tool menu. The tool description will "
                             "appear directly after the tool name as "
                             "normal text.", emphasize=True)
        core.descriptionLine("Tool XML file",
                             "The path (relative to '%s') and name " %
                             os.path.sep.join([''] + cls._getProtoRelToolDirs(fromBase=True)) +
                             "of the Galaxy tool XML file to be created. "
                             "The tool file can be named anything and be "
                             "placed anywhere (as the 'tool_conf.xml' file "
                             "contains the path to the tool XML file). "
                             "However, we encourage the practice of placing "
                             "the Galaxy tool XML file together with the "
                             "Python module, in the same directory and "
                             "with the same name as tool module (with e.g. "
                             "'ABCTool.xml' instead of 'AbcTool.py').",
                             emphasize=True)
        core.descriptionLine("Select section in tool_conf.xml file",
                             "The section in the tool_conf.xml file where"
                             "the tool should be placed in the menu. "
                             "This corresponds to the first level in the"
                             "tool hierarchy.", emphasize=True)
        return str(core)

    @staticmethod
    def getOutputFormat(choices):
        return 'customhtml'


class GalaxyToolConfig(object):
    tool_xml_template = '''<tool id="%s" name="%s" version="1.0.0"
  tool_type="%s_generic" proto_tool_module="%s" proto_tool_class="%s">
  <description>%s</description>
</tool>\n'''

    def __init__(self, tool_conf_fn=GALAXY_TOOL_CONFIG_FILE):
        self.tool_conf_fn = tool_conf_fn
        with open(self.tool_conf_fn, 'r') as tcf:
            self.tool_conf_data = tcf.read()

    def getSections(self):
        self.sectionPos = {}
        section_names = []
        for m in re.finditer(r'\n[^!\n]+<section ([^>]+)>', self.tool_conf_data):
            attrib = {}
            for a in re.findall(r'([^ =]+)="([^"]+)"', m.group(1)):
                attrib[a[0]] = a[1]
            self.sectionPos[attrib['name']] = m.end(0)
            section_names.append(attrib['name'])
        return section_names

    def addTool(self, section_name, tool_file):
        self.getSections()
        tool_tag = '\n    <tool file="%s" />' % (tool_file,)
        pos = self.sectionPos[section_name]
        self.tool_conf_data = self.tool_conf_data[:pos] + tool_tag + self.tool_conf_data[pos:]
        return self.tool_conf_data

    def write(self):
        shutil.copy(self.tool_conf_fn, self.tool_conf_fn + '.bak')
        with open(self.tool_conf_fn, 'w') as f:
            f.write(self.tool_conf_data)

    def createToolXml(self, tool_id, tool_name, tool_id_prefix, tool_module, tool_cls, tool_descr):
        tool_xml = self.tool_xml_template % (tool_id, tool_name, tool_id_prefix,
                                             tool_module, tool_cls, tool_descr)
        return tool_xml
