from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic, StatisticConcatResSplittable, OnlyGloballySplittable
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq
from gold.util.CustomExceptions import NotSupportedError
from gold.track.TrackView import AutonomousTrackElement

class NearestPointDistsStat(MagicStatFactory):
    pass

class NearestPointDistsStatSplittable(StatisticConcatResSplittable, OnlyGloballySplittable):
    pass

class NearestPointDistsStatUnsplittable(Statistic):
    'For each point in track1, finds the distance to the right/left/both to the next point of track2..'
    def __init__(self, region, track, track2, distDirection='both', **kwArgs):
        assert( distDirection in ['left','right','both'])
        
        self._distDirection = distDirection
        Statistic.__init__(self, region, track, track2, distDirection=distDirection, **kwArgs)

    def _compute(self):
        if self._region.strand == False and self._distDirection != 'both':
            raise NotSupportedError() #support by switching between left/right-computation..
        
        tv1 = self._children[0].getResult()
        tv2 = self._children[1].getResult()
        dists = []
        tv2Iter = tv2.__iter__()

        try:
            p2 = tv2Iter.next()
            p2Pos = p2.start()
            prevP2 = None
            
        except:
            #no points in track2            
            return [None for el in tv1]
        
        emptyP2 = False
        
        for p1 in tv1:
            #p1 = el1
            try:
                while p2Pos < p1.start():
                    if not emptyP2:
                        prevP2 = AutonomousTrackElement(trackEl=p2)
                    p2 = tv2Iter.next()
                    p2Pos = p2.start()
                self._appendToDists(dists, p1, p2, prevP2)
            except StopIteration:
                emptyP2 = True
                self._appendToDists(dists, p1, None, prevP2)
        return dists

    @staticmethod
    def _getObservator(p1, p2):
        return abs(p2.start() - p1.start()) if p2 != None else None
        
    def _appendToDists(self, dists, p1, rightP2, leftP2):        
        if self._distDirection == 'right':
            dists.append( self._getObservator(p1, rightP2) )
        elif self._distDirection == 'left':
            if rightP2!=None and rightP2.start()==p1.start():
                dists.append( self._getObservator(p1, rightP2) )
            else:
                dists.append( self._getObservator(p1, leftP2) )
        else:
            if leftP2==rightP2==None:
                dists.append(None)
            else:
                left = p1.start() - leftP2.start() if leftP2 != None else None
                right = rightP2.start() - p1.start() if rightP2 != None else None
                if left==None or (right!=None and left>right):
                    dists.append( self._getObservator(p1, rightP2) )
                else:
                    dists.append( self._getObservator(p1, leftP2) )
                #dists.append( min(x for x in [left,right] if x!=None) )
            
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(dense=False, interval=False)) )
        self._addChild( RawDataStat(self._region, self._track2, TrackFormatReq(dense=False, interval=False)) )
