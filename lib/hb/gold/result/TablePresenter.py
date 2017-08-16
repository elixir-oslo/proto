import os

from config.Config import MAX_LOCAL_RESULTS_IN_TABLE
from gold.result.Presenter import Presenter
from gold.track.GenomeRegion import GenomeRegion
from proto.hyperbrowser.HtmlCore import HtmlCore
from proto.hyperbrowser.TextCore import TextCore
from quick.util.CommonFunctions import ensurePathExists


class TablePresenter(Presenter):
    FILE_NAME_PREFIX = 'table'
    
    def __init__(self, results, baseDir, header):
        Presenter.__init__(self, results, baseDir)
        #HTML
        self._htmlFn = os.sep.join([baseDir, self.FILE_NAME_PREFIX + '.html'])
        self._writeContent(self._htmlFn, header, HtmlCore)
        #Raw text
        self._rawFn = os.sep.join([baseDir, self.FILE_NAME_PREFIX + '.txt'])
        self._writeContent(self._rawFn, header, TextCore)
        
    def getDescription(self):
        return 'Table: values per bin'
    
    def getSingleReference(self):
        return str(HtmlCore().link('HTML', self._getRelativeURL(self._htmlFn))) + \
                '&nbsp;/&nbsp;' + \
                str(HtmlCore().link('Raw&nbsp;text', self._getRelativeURL(self._rawFn)))

    def _commonWriteContent(self, fn, header, coreCls, headerPrefix, numElements):
        core = coreCls()
        
        core.begin()
        core.styleInfoBegin(styleClass="infomessagesmall",
                            style='padding: 5px; margin-bottom: 10px; ' +\
                                  'background-image: none; background-color: #FFFC8C; ')
        core.header(headerPrefix)
        core.smallHeader(header)
        core.styleInfoEnd()

        #core.bigHeader(header)
        #core.header('Local result table')
        
        if isinstance(core, HtmlCore) and numElements > MAX_LOCAL_RESULTS_IN_TABLE:
            core.line('Local results were not printed because of the large number of bins: ' \
                  + str(numElements) + ' > ' + str(MAX_LOCAL_RESULTS_IN_TABLE))
        else:
            self._writeTable(core, coreCls)

        core.end()
        
        ensurePathExists(fn)        
        open(fn,'w').write( str(core) )

    def _writeContent(self, fn, header, coreCls):
        numRows = len(self._results.getAllRegionKeys())
        core = self._commonWriteContent(fn, header, coreCls, 'Local results table for:', numRows)
        
    def _writeTable(self, core, coreCls):
        core.tableHeader([ str( coreCls().textWithHelp(baseText, helpText) ) for baseText, helpText in 
                          ([('Region','')] + self._results.getLabelHelpPairs()) ], sortable=True)
            
        allRegions = [(GenomeRegion.strWithCentromerInfo(regionKey), regionKey) \
                      for regionKey in self._results.getAllRegionKeys()]
        
        from third_party.alphanum import alphanum
        from operator import itemgetter
        allRegions = sorted(allRegions, cmp=alphanum, key=itemgetter(0))
            
        for regionStr, regionKey in allRegions:
            core.tableLine([regionStr] +\
                [ str(coreCls().format( self._results[regionKey].get(resDictKey) )) \
                 for resDictKey in self._results.getResDictKeys() ])
        
        core.tableFooter()
        

class DistributionTablePresenter(TablePresenter):
    FILE_NAME_PREFIX = 'dist_table'
    
    def getDescription(self):
        return 'Table: distribution'
    
    def _writeContent(self, fn, header, coreCls):
        #print self._results.getGlobalResult()
        numRows = len(self._results.getGlobalResult().values()[0])
        core = self._commonWriteContent(fn, header, coreCls, 'Global distribution table for: ', numRows)
        
    def _writeTable(self, core, coreCls):
        core.tableHeader([ str( coreCls().textWithHelp(baseText, helpText) ) for baseText, helpText in 
                           self._results.getLabelHelpPairs() ], sortable=True)
            
        resDictKeys = self._results.getResDictKeys()
        for i,el in enumerate(self._results.getGlobalResult()[resDictKeys[0]]):
            core.tableLine(
                [ str(coreCls().format( self._results.getGlobalResult().get(resDictKey)[i] )) \
                  for resDictKey in resDictKeys ])
        core.tableFooter()
    
