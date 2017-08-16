from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic, StatisticSumResSplittable

class GenericGenomeElementWriterStat(MagicStatFactory):
    '''
    Writes the GenomeElements received from its child class to a textual track.
    Takes a child class name as parameter generatorStatistic, takes a file name to write to,
    and passes all further parameters on.
    The result returned from this statistic is the number of elements written to the track.
    For now, only outputs standard bed files, but could be extended to work with GTrack of any type.
    '''
    pass

class GenericGenomeElementWriterStatSplittable(StatisticSumResSplittable):
    pass


class GenericGenomeElementWriterStatUnsplittable(Statistic):
    def _init(self, generatorStatistic=None, quotedOutTrackFn=None, **kwArgs):
        self._generatorStatisticClass = self.getRawStatisticClass(generatorStatistic)
        from urllib import unquote
        self._outTrackFn = unquote(quotedOutTrackFn)
        
    def _compute(self):
        if self._kwArgs.get('minimal'):
            return 0
        
        genomeElements = self._children[0].getResult()
        from gold.util.CommonFunctions import isIter
        from gold.origdata.GenomeElement import GenomeElement
        assert isIter(genomeElements)

        if len(genomeElements)==0:
            return
        
        assert type(genomeElements[0]) == GenomeElement
        #support relative coordinates, which should then be made absolute here..
        if genomeElements[0].genome==None: #then assume all are relative
            for ge in genomeElements:
                assert ge.genome==None
                assert ge.chr==None
                ge.genome = self._region.genome
                ge.chr = self._region.chr
                ge.start += self._region.start #since region was relative, add the start coordinate of the bin one is within
                ge.end += self._region.start #add same offset as for start..
        
        f = open(self._outTrackFn, 'a')
        
        for ge in genomeElements:
            f.write('\t'.join([ge.chr, str(ge.start), str(ge.end)]) + '\n')
        f.close()
        return len(genomeElements)
        
    def _createChildren(self):
        self._addChild( self._generatorStatisticClass(self._region, self._track, self._track2 if hasattr(self,'_track2') else None, **self._kwArgs) )
