import os

from gold.result.HistoryPresenter import HistoryPresenter
from quick.util.CommonFunctions import ensurePathExists


class WigPresenter(HistoryPresenter):
    def _writeContent(self, resDictKey, fn):
        ensurePathExists(fn)
        outF = open( fn ,'w')
        outF.write('track type=wiggle_0 name=' + self._results.getStatClassName() + '_' + resDictKey + os.linesep)
        for bin in self._results.getAllRegionKeys():
            outF.write( '\t'.join([str(x) for x in \
                        [bin.chr, bin.start, bin.end, str(self._results[bin].get(resDictKey)).replace('None', 'nan')] ]) + os.linesep)
        outF.close()

    def _getSuffix(self):
        return 'wig'
