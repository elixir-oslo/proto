from galaxy.webapps.galaxy.controllers import proto
from galaxy.web.base.controller import web


class HyperController(proto.ProtoController):
    @staticmethod
    def _convert_mako_from_rel_to_abs(mako):
        return '/hyperbrowser/' + mako

    @staticmethod
    def _get_controller_module_name(rel_mako):
        return 'proto.hyperbrowser.' + rel_mako

    @staticmethod
    def _fill_mako_template(template_mako, tool_controller, trans):
        from gold.application.GalaxyInterface import GalaxyInterface
        return trans.fill_template(template_mako, trans=trans,
                                   hyper=GalaxyInterface, control=tool_controller)

    @web.expose
    def index(self, trans, mako='/hyperbrowser/analyze', **kwd):
        return self._index(trans, mako, **kwd)

