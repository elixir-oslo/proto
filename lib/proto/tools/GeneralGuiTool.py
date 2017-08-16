import os
from collections import namedtuple
from urllib import quote


class HistElement(object):
    def __init__(self, name, format, label=None, hidden=False):
        self.name = name
        self.format = format
        self.label = label
        self.hidden = hidden


BoxGroup = namedtuple('BoxGroup', ['label', 'first', 'last'])


class GeneralGuiTool(object):
    def __init__(self, toolId=None):
        self.__class__.toolId = toolId

    # API methods
    @staticmethod
    def getInputBoxNames():
        return []

    @staticmethod
    def getSubToolClasses():
        return None

    @classmethod
    def getToolSelectionName(cls):
        return cls.getToolName()

    @staticmethod
    def isPublic():
        return False

    @staticmethod
    def isRedirectTool(choices=None):
        return False

    @staticmethod
    def isHistoryTool():
        return True

    @staticmethod
    def isDynamic():
        return True

    @staticmethod
    def getResetBoxes():
        return []

    @staticmethod
    def getInputBoxOrder():
        return None

    @classmethod
    def getInputBoxGroups(cls, choices=None):
        if hasattr(super(GeneralGuiTool, cls), 'getInputBoxGroups'):
            return super(GeneralGuiTool, cls).getInputBoxGroups(choices)
        return None

    @staticmethod
    def getToolDescription():
        return ''

    @staticmethod
    def getToolIllustration():
        return None

    @staticmethod
    def getFullExampleURL():
        return None

    @staticmethod
    def isDebugMode():
        return False

    @staticmethod
    def getOutputFormat(choices=None):
        return 'html'

    @classmethod
    def getOutputName(cls, choices=None):
        return cls.getToolSelectionName()

    @staticmethod
    def validateAndReturnErrors(choices):
        return None

    # Convenience methods

    @classmethod
    def convertHttpParamsStr(cls, streng):
        strTab = []
        for v in streng.split('\n'):
            if v:
                strTab.append(v)

        return dict([tuple(v.split(':',1)) for v in strTab])

    @classmethod
    def getOptionBoxNames(cls):
        labels = cls.getInputBoxNames()
        #inputOrder = range(len(labels) if not cls.getInputBoxOrder() else cls.getInputBoxOrder()
        boxMal = 'box%i'
        if type(labels[0]).__name__ == 'str':
            return [boxMal%i for i in range(1, len(labels)+1)]
            #return [boxMal % i for i in inputOrder]
        else:
            return [i[0] for i in labels]
            #return [labels[i][0] for i in inputOrder]

    @classmethod
    def getNamedTuple(cls):
        names = cls.getInputBoxNames()
        anyTuples = False
        vals = []
        for i in range(len(names)):
            name = names[i]
            if isinstance(name, tuple):
                anyTuples = True
                vals.append(name[1])
            else:
                vals.append('box' + str(1 + i))

        if anyTuples:
            return namedtuple('ChoiceTuple', vals)
        else:
            return None

    @staticmethod
    def _exampleText(text):
        from proto.HtmlCore import HtmlCore
        core = HtmlCore()
        core.styleInfoBegin(styleClass='debug', linesep=False)
        core.append(text.replace('\t','\\t'))
        core.styleInfoEnd()
        return str(core)

    @classmethod
    def makeHistElement(cls,  galaxyExt='html', title='new Dataset', label='Newly created dataset',):
        import json, glob
        #print 'im in makeHistElement'
        json_params =  cls.runParams
        datasetId = json_params['output_data'][0]['dataset_id'] # dataset_id fra output_data
        hdaId = json_params['output_data'][0]['hda_id'] # # hda_id fra output_data
        metadata_parameter_file = open( json_params['job_config']['TOOL_PROVIDED_JOB_METADATA_FILE'], 'a' )
        newFilePath = json_params['param_dict']['__new_file_path__']
        numFiles = len(glob.glob(newFilePath+'/primary_%i_*'%hdaId))
        #title += str(numFiles+1)
        #print 'datasetId', datasetId
        #print 'newFilePath', newFilePath
        #print 'numFiles', numFiles
        outputFilename = os.path.join(newFilePath , 'primary_%i_%s_visible_%s' % ( hdaId, title, galaxyExt ) )
        #print 'outputFilename', outputFilename
        metadata_parameter_file.write( "%s\n" % json.dumps( dict( type = 'dataset', #new_primary_
                                         dataset_id = datasetId,#base_
                                         ext = galaxyExt,
                                         #filename = outputFilename,
                                         #name = label,
                                         metadata = {'dbkey':['hg18']} )) )
        metadata_parameter_file.close()
        return outputFilename

    @classmethod
    def createGenericGuiToolURL(cls, tool_id, sub_class_name=None, tool_choices=None):
        from proto.ProtoToolRegister import getToolPrototype
        tool = getToolPrototype(tool_id)
        base_url = '?mako=generictool&tool_id=' + tool_id + '&'
        if sub_class_name and isinstance(tool, MultiGeneralGuiTool):
            for subClass in tool.getSubToolClasses():
                if sub_class_name == subClass.__name__:
                    tool = subClass()
                    base_url += 'sub_class_id=' + quote(tool.getToolSelectionName()) + '&'

        #keys = tool.getNamedTuple()._fields
        if not tool_choices:
            args = []
        elif isinstance(tool_choices, dict):
            args = [ '%s=%s' % (k,quote(v)) for k,v in tool_choices.items()]
        elif isinstance(tool_choices, list):
            args = [ '%s=%s' % ('box%d'%(i+1,), quote(tool_choices[i])) for i in range(0, len(tool_choices)) ]

        return base_url + '&'.join(args)


class MultiGeneralGuiTool(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "-----  Select tool -----"

    @staticmethod
    def getToolSelectionName():
        return "-----  Select tool -----"

    @staticmethod
    def getSubToolSelectionTitle():
        return 'Select subtool:'

    @staticmethod
    def validateAndReturnErrors(choices):
        return ''

    @staticmethod
    def getInputBoxNames():
        return []

    @staticmethod
    def useSubToolPrefix():
        return False
