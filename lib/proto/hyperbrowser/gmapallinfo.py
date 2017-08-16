from gold.application.GalaxyInterface import GalaxyInterface
import quick.extra.GoogleMapsInterface as GMI

from proto.hyper_gui import *
from proto.BaseToolController import *
from proto.hyperbrowser.HyperBrowserControllerMixin import HyperBrowserControllerMixin


class GMapAllInfoController(BaseToolController, HyperBrowserControllerMixin):
    def __init__(self, trans, job):
        BaseToolController.__init__(self, trans, job)
    
    def action(self):
        map = GMI.Map(self.params['map'])
        self.cookies = map.getSavedCookies(self.params['load'])
        

    def getInfoText(self):
        info = self.cookies['idxclusters']
        return info

    
def getController(transaction = None, job = None):
    return GMapAllInfoController(transaction, job)
