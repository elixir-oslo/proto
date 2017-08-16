from proto.galaxy_tool_classes import ProtoTool, ProtoGenericTool


class ProtoHBTool(ProtoTool):
    tool_type = 'hyperbrowser'


class ProtoHBGenericTool(ProtoGenericTool):
    tool_type = 'hb_generic'
    # mako = '/proto/generictool'
    proto_action = '/hyper'
    proto_command = '$GALAXY_ROOT_DIR/lib/proto/hyperbrowser/HBToolExecute.py $output'

    # def parse(self, tool_source, guid=None):
    #    super(HyperBrowserGenericTool, self).parse(tool_source, guid)


hb_tool_types = {'hyperbrowser': ProtoHBTool,
                 'hb_generic': ProtoHBGenericTool}

