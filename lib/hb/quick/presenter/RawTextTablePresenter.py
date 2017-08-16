import os

from config.Config import MAX_LOCAL_RESULTS_IN_TABLE
from gold.result.Presenter import Presenter
from gold.util.CommonFunctions import strWithStdFormatting
from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.util.CommonFunctions import ensurePathExists


class RawTextTablePresenter(Presenter):
    def __init__(self, results, baseDir, header):
        Presenter.__init__(self, results, baseDir)
        self._fn = os.sep.join([baseDir, 'table.txt'])
        self._writeContent(self._fn, header)

    def getDescription(self):
        return 'Raw text table (all)'
    
    def getReference(self, resDictKey):
        return HtmlCore().link('View', self._getRelativeURL(self._fn))

    def _writeContent(self, fn, header):
        #core = HtmlCore()
        
        #core.begin()
        #core.bigHeader(header)
        #core.header('Local result table')
        text = ''
        if len( self._results.getAllRegionKeys() ) > MAX_LOCAL_RESULTS_IN_TABLE:
            text += 'Local results were not printed because of the large number of bins: ' \
                  + str(numUserBins) + ' > ' + str(MAX_LOCAL_RESULTS_IN_TABLE)
        else:
            #core.tableHeader([ str( HtmlCore().textWithHelp(baseText, helpText) ) for baseText, helpText in 
            #                  ([('Region','')] + self._results.getLabelHelpPairs()) ])
            
            for regionKey in self._results.getAllRegionKeys():
                text += '\t'.join([str(regionKey)] +\
                    [ strWithStdFormatting( self._results[regionKey].get(resDictKey) ) \
                     for resDictKey in self._results.getResDictKeys() ]) + os.linesep
            #core.tableFooter()

        #core.end()
        
        ensurePathExists(fn)        
        open(fn,'w').write( text )
