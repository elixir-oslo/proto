from gold.result.Presenter import Presenter
from gold.util.CommonFunctions import strWithStdFormatting

class GlobalValuePresenter(Presenter):
    def __init__(self, results, baseDir=None):
        Presenter.__init__(self, results, baseDir)

    def getDescription(self):
        return 'Summary'
        
    def getReference(self, resDictKey):
        globalRes = self._results.getGlobalResult()
        return strWithStdFormatting( globalRes[resDictKey] ) if globalRes not in [None,{}] else 'None'

class ForgivingGlobalValuePresenter(GlobalValuePresenter):
    def getTrackName(self, trackIndex):
        return self._results.getTrackNames()[trackIndex]
    
    def getReference(self, resDictKey):
        globalRes = self._results.getGlobalResult()
        if globalRes is None:
            return 'N/A'
        elif resDictKey in globalRes:
            return GlobalValuePresenter.getReference(self, resDictKey)
        else:
            return ''


