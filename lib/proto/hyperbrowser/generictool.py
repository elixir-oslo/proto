from proto.generictool import GenericToolController
from HyperBrowserControllerMixin import HyperBrowserControllerMixin


class HBGenericToolController(HyperBrowserControllerMixin, GenericToolController):
    pass


def getController(transaction = None, job = None):
    return HBGenericToolController(transaction, job)
