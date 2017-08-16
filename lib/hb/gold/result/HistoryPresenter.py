import os

from gold.result.Presenter import Presenter
from gold.util.CustomExceptions import AbstractClassError
from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.util.CommonFunctions import getLoadToGalaxyHistoryURL


class HistoryPresenter(Presenter):
    def __init__(self, results, baseDir):
        Presenter.__init__(self, results, baseDir)

    def getDescription(self):
        return 'As track in history'

    def getReference(self, resDictKey):
        fn = self._getFn(resDictKey)
        self._writeContent(resDictKey, fn)
        if not os.path.exists(fn):
            return HtmlCore().textWithHelp('N/A', 'A %s file is not available for this type of data.' % self._getSuffix())
        
        genome = self._results.getGenome() #getAnalysis().getGenome() if self._results.getAnalysis() is not None else 'hg18'
        galaxyDataType = self._getSuffix()
        return HtmlCore().link('Load', getLoadToGalaxyHistoryURL(fn, genome, galaxyDataType)) 
            
    def _writeContent(self, resDictKey, fn):
        raise AbstractClassError

    def _getFn(self, resDictKey):
        return os.sep.join([self._baseDir, self._results.getStatClassName() + \
                            '_' + resDictKey + '.' + self._getSuffix()])
    
    def _getSuffix(self):
        raise AbstractClassError
