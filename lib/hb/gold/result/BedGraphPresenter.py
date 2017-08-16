import os

from gold.result.HistoryPresenter import HistoryPresenter
from gold.util.CommonFunctions import isNumber
from quick.util.CommonFunctions import ensurePathExists


class BedGraphPresenter(HistoryPresenter):
    def _writeContent(self, resDictKey, fn):
        ensurePathExists(fn)
        outF = open( fn ,'w')
        outF.write('track type=bedGraph name=' + self._results.getStatClassName() + '_' + resDictKey + \
                   (' viewLimits=0:1 autoScale=off' if resDictKey.lower() in ['pval','p-value'] else '') + os.linesep)
        for bin in self._results.getAllRegionKeys():
            val = str(self._results[bin].get(resDictKey))
            if not isNumber(val) and val not in ['None','nan','.']:
                outF.close()
                os.unlink(fn)
                return
            outF.write( '\t'.join([str(x) for x in \
                        [bin.chr, bin.start, bin.end, str(self._results[bin].get(resDictKey)).replace('None', 'nan')] ]) + os.linesep)
        outF.close()

    def _getSuffix(self):
        return 'bedgraph'
