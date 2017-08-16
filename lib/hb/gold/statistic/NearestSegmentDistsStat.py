import ast
from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic, StatisticConcatDictOfListResSplittable, OnlyGloballySplittable
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq
from gold.util.CustomExceptions import NotSupportedError
from gold.util.CommonConstants import BINARY_MISSING_VAL
from collections import OrderedDict

class NearestSegmentDistsStat(MagicStatFactory):
    pass

class NearestSegmentDistsStatSplittable(StatisticConcatDictOfListResSplittable, OnlyGloballySplittable):
    IS_MEMOIZABLE = False

class NearestSegmentDistsStatUnsplittable(Statistic):
    'For each segment in track1, finds the distance to the closest segment of track2, overlap counting as zero distance..'
    
    IS_MEMOIZABLE = False

    def _init(self, distDirection='both', withOverlaps='no', addSegmentLengths='True', **kwArgs):
        assert( withOverlaps in ['no','yes'] )
        self._withOverlaps = withOverlaps
        
        assert distDirection in ['upstream','downstream','both']
        self._distDirection = distDirection
        
        assert addSegmentLengths in ['True', 'False']
        self._addSegmentLengths = ast.literal_eval(addSegmentLengths)

    def _append(self, dists, dist, toNames, name):
        dists.append(dist)
        if name is not None:
            toNames.append(name)
        
    def _compute(self):
        if self._region.strand == False and self._distDirection != 'both':
            raise NotSupportedError() #support by switching between left/right-computation..

        tv1 = self._children[0].getResult()
        tv2 = self._children[1].getResult()
        tv1HasName = tv1.hasExtra('name')
        tv2HasName = tv2.hasExtra('name')
        tv1HasId = tv1.idsAsNumpyArray() is not None
        tv2HasId = tv2.idsAsNumpyArray() is not None
        
        dists = []
        segLengths = []
        fromNames = []
        toNames = []
        
        for p,ldist,rdist,lname,rname in self._yieldLeftAndRightDists(tv1, tv2, tv1HasName, tv2HasName, tv1HasId, tv2HasId): #p is here the track1-point that we have a left/right-distance for
            if tv1HasName:
                fromNames.append(p.name())
            elif tv1HasId:
                fromNames.append(p.id())
            
            segLengths.append(len(p))
            #p.strand
            #self._distDirection
            
            if rdist == 0:
                self._append(dists, 0, toNames, rname)
            elif ldist == 0:
                self._append(dists, 0, toNames, lname)
            elif self._distDirection == 'both':
                minDist, minName = min((x,name) for x,name in [[ldist,lname],[rdist,rname]] if x is not None)
                self._append(dists, minDist, toNames, minName)
            elif p.strand() in [True,None,BINARY_MISSING_VAL]:
                if self._distDirection in ['downstream']:
                    self._append(dists, rdist, toNames, rname)
                else:
                    self._append(dists, ldist, toNames, lname)
            else:
                if self._distDirection in ['downstream']:
                    self._append(dists, ldist, toNames, lname)
                else:
                    self._append(dists, rdist, toNames, rname)
                    
        return OrderedDict([('Result', dists)] + \
                           ([('SegLengths', segLengths)] if self._addSegmentLengths else []) + \
                           ([('FromNames', fromNames)] if tv1HasName else ([('FromIds', fromNames)] if tv1HasId else [])) + \
                           ([('ToNames', toNames)] if tv2HasName else ([('ToIds', fromNames)] if tv2HasId else [])))
    
    def _yieldLeftAndRightDists(self, tv1, tv2, tv1HasName, tv2HasName, tv1HasId, tv2HasId):
        tv2Iter = tv2.__iter__()

        try:
            p2 = tv2Iter.next()
            prevP2_end = None
            prevP2_name = None
        except:
            #no points in track2
            self._result = OrderedDict([('Result', [None for el in tv1])] + \
                           ([('SegLengths', [len(el) for el in tv1])] if self._addSegmentLengths else []) + \
                           ([('FromNames', [el.name for el in tv1])] if tv1HasName else ([('FromIds', [el.id for el in tv1])] if tv1HasId else [])) + \
                           ([('ToNames', [None for el in tv1])] if tv2HasName > 0 else ([('ToIds', [None for el in tv1])] if tv2HasId else [])))
            return
                
        for p1 in tv1:
            try:
                if p2==None:
                    p2 = tv2Iter.next()
                
                while p2.start() < p1.start():
                    prevP2_end = p2.end()
                    prevP2_name = p2.name() if tv2HasName else (p2.id() if tv2HasId else None)
                    p2 = None
                    p2 = tv2Iter.next()
                
                leftDist = max(0,p1.start()-(prevP2_end-1)) if prevP2_end!= None else None
                rightDist  = max(0,p2.start()-(p1.end()-1))

                yield p1, leftDist, rightDist, prevP2_name, p2.name() if tv2HasName else (p2.id() if tv2HasId else None)
                
            except StopIteration:
                if prevP2_end == None:
                    yield p1, None, None, None, None
                else:
                    yield p1, max(0,p1.start()-(prevP2_end-1)), None, prevP2_name, None
        

            
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(dense=False, interval=True, allowOverlaps = (self._withOverlaps == 'yes'))) )
        self._addChild( RawDataStat(self._region, self._track2, TrackFormatReq(dense=False, interval=True, allowOverlaps = False)) )
