from gold.util.CustomExceptions import AbstractClassError
'''
Presenter is the root class and absolute superclass for all presenter-classes
It has two instance variables:
    _results: a Results object containing all results data from an analysis run(subclass of dict)
    _baseDir: the filepath to the folder where the history-item is saved
'''
class Presenter(object):
    def __init__(self, results, baseDir=None):
        self._results = results
        self._baseDir = baseDir
    
    def getDescription(self):
        raise AbstractClassError
        
    def getReference(self, resDictKey):
        raise AbstractClassError

    #TODO: refactor all presenters to use StaticFile. Then remove the following convenience method:
    def _getRelativeURL(self, fullFn):
        import os.path
        
        baseDirForRelativeUrl = self._baseDir.rstrip(os.path.sep)
        if os.path.split(baseDirForRelativeUrl)[-1].isdigit(): #ResultsViewerCollection
            baseDirForRelativeUrl = os.path.dirname(baseDirForRelativeUrl)

        if fullFn.startswith(baseDirForRelativeUrl + os.path.sep):
            return fullFn[len(baseDirForRelativeUrl) + 1:]

#mal:
    #def __init__(self, results, baseDir=None):
    #    Presenter.__init__(results, baseDir)
    #
    #def getDescription(self):
    #    
    #def getReference(self, resDictKey):
