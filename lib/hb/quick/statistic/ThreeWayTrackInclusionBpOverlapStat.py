from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from quick.util.CommonFunctions import numAsPaddedBinary
from quick.statistic.MultitrackBpOverlapStat import MultitrackBpOverlapStat


class ThreeWayTrackInclusionBpOverlapStat(MagicStatFactory):
    pass

#class ThreeWayProportionalBpOverlapStatSplittable(StatisticSumResSplittable):
#    pass
            
class ThreeWayTrackInclusionBpOverlapStatUnsplittable(Statistic):
    def _init(self, fuzzyThreshold=None, **kwArgs):
        if fuzzyThreshold in [None,'','None']:
            self._fuzzyThreshold = None
        else:
            self._fuzzyThreshold = float(fuzzyThreshold)
        
    
    
    def _compute(self):
        t = self._children[0].getResult()
        #print t.keys()
        numTracks = len(t.keys()[0])

        trackInclusions = []
        trackInclusionsV2 = []
        unfilteredTrackInclusions = []
        
        for combA in range(1,2**numTracks): #enumerate with binary number corresponding to all subsets
            for combB in range(1,2**numTracks):
                binaryA = numAsPaddedBinary(combA,numTracks)
                binaryB = numAsPaddedBinary(combB,numTracks)

                tracksInA = set([i for i,x in enumerate(binaryA) if x=='1'])
                tracksInB = set([i for i,x in enumerate(binaryB) if x=='1'])
                
                #B is subset of A, with exactly one less track included, and also has same coverage        
                #if (tracksInB < tracksInA) and (len(tracksInA-tracksInB) == 1) and t[binaryA] == t[binaryB]:

                #(non-empty) B is subset of A, and also has same coverage        
                if (tracksInB < tracksInA) and (len(tracksInB) > 0):
                    #print binaryA,binaryB,t[binaryA], t[binaryB], min(t[binaryA], t[binaryB])*self._fuzzyThreshold, max(t[binaryA], t[binaryB])
                    if (t[binaryA] == t[binaryB] or (self._fuzzyThreshold != None and min(t[binaryA], t[binaryB])*self._fuzzyThreshold >= max(t[binaryA], t[binaryB]))):
                        if t[binaryB]==0: #an empty track (typically an empty intersection between two tracks) is trivially covered by all other tracks - therefore uninformative and not added
                            continue
                        #print 'yes'
                        trackInclusions.append([binaryB,binaryA])
                        
            #for inclusion in trackInclusions:
                        includedTracks = (tracksInA-tracksInB)
                        #assert len(includedTrack)==1, includedTrack
                        #includedTrackStr = 'T'+str( list(includedTrack)[0]+1) #count from T1..
                        includedTrackStr = '&'.join(['T%i'%(i+1) for i in includedTracks]) #count from T1..
                        assert tracksInB == tracksInB.intersection(tracksInA)
                        bgTracks = tracksInB
                        bgTracksStr = '&'.join(['T%i'%(i+1) for i in bgTracks]) #count from T1..
                        trackInclusionsV2.append([bgTracksStr, includedTrackStr])
                        
                        unfilteredTrackInclusions.append([bgTracks,includedTracks])

        uti = unfilteredTrackInclusions
        #print 'uti: ', len(uti), uti
        filteredTrackInclusions = [[bg,incl] for bg,incl in uti if not (any((bg>ob and incl==oi) or (ob==bg and incl<oi) for ob,oi in uti))]
        #print 'filteredTrackInclusions: ', len(filteredTrackInclusions ), filteredTrackInclusions 
        filteredTrackInclusionsStr = ', '.join(sorted([\
            ' is covered by '.join([
            '&'.join(['T%i'%(i+1) for i in part])            
            for part in incl])
            for incl in filteredTrackInclusions]))
        filteredTrackInclusionsStrLetters = filteredTrackInclusionsStr.replace('T1','A').replace('T2','B').replace('T3','C').replace('T4','D').replace('T5','E').replace('T6','F')
        #print filteredTrackInclusionsStrLetters
        res = {}
        res.update(t)

#         res['Inclusions'] = '_'.join(['in'.join(incl) for incl in trackInclusions])
#         res['InclusionsV2'] = ', '.join([' in '.join(incl) for incl in trackInclusionsV2])
#         res['InclusionsV3'] = res['InclusionsV2'].replace('T1','A').replace('T2','B').replace('T3','C').replace('T4','D').replace('T5','E').replace('T6','F')
# 
        res['Inclusions'] = filteredTrackInclusionsStrLetters

        return res
                    
                        
        
        
    
    def _createChildren(self):
#         self._addChild( ThreeWayBpOverlapStat(self._region, self._track, self._track2, **self._kwArgs) )
        self._addChild( MultitrackBpOverlapStat(self._region, self._track, self._track2, **self._kwArgs) )
        
