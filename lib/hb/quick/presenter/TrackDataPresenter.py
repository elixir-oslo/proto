from quick.util.CommonFunctions import ensurePathExists
from gold.result.HistoryPresenter import HistoryPresenter
from gold.origdata.TrackGenomeElementSource import TrackViewListGenomeElementSource
from gold.origdata.BedComposer import BedComposer
from gold.origdata.GtrackComposer import StdGtrackComposer
from gold.track.TrackView import TrackView

class TrackDataPresenter(HistoryPresenter):
    #def __init__(self, results, baseDir):
    #    Presenter.__init__(self, results, baseDir)

    def getDescription(self):
        return 'Raw track data'
            
    def _writeContent(self, resDictKey, fn):
        ensurePathExists(fn)
        arbitraryTV = self._results.getArbitraryLocalResult()['Result']
        
        assert isinstance(arbitraryTV, TrackView)
        #assert arbitraryTV.trackFormat.getFormatName() in [ 'Valued segments', 'Segments'], arbitraryTV.trackFormat.getFormatName()
        genome = arbitraryTV.genomeAnchor.genome
        #print 'GENOME: ',genome
        from gold.util.CommonFunctions import getClassName
        print type([self._results[key]['Result'] for key in sorted(self._results.keys())][0]), getClassName([self._results[key]['Result'] for key in sorted(self._results.keys())][0])
        tvGeSource = TrackViewListGenomeElementSource(genome, [self._results[key]['Result'] for key in sorted(self._results.keys())], 'Private:GK:test1:wgEncodeUchicagoTfbsK562EfosControlPk'.split(':') ) 
        if arbitraryTV.trackFormat.getFormatName() in ['Segments']:
            BedComposer(tvGeSource).composeToFile(fn)
        else:
            StdGtrackComposer(tvGeSource).composeToFile(fn)
                
        #trackView = self._results
        #outF = open( fn ,'w')
        #outF.write('track type=bedGraph name=' + self._results.getStatClassName() + '_' + resDictKey + \
        #           (' viewLimits=0:1 autoScale=off' if resDictKey.lower() in ['pval','p-value'] else '') + os.linesep)
        #for bin in self._results.getAllRegionKeys():
        #    val = str(self._results[bin].get(resDictKey))
        #    if not isNumber(val) and val not in ['None','nan','.']:
        #        outF.close()
        #        os.unlink(fn)
        #        return
        #    outF.write( '\t'.join([str(x) for x in \
        #                [bin.chr, bin.start, bin.end, str(self._results[bin].get(resDictKey)).replace('None', 'nan')] ]) + os.linesep)
        #outF.close()

    def _getSuffix(self):
        return 'bed'        
    #
    #def _getFn(self, resDictKey):
    #    return os.sep.join([self._baseDir, self._results.getStatClassName() + \
    #                        '_' + resDictKey + '.' + self._getSuffix()])
    #
    #def _getSuffix(self):
    #    raise AbstractClassError
