from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
#from gold.statistic.RawDataStat import RawDataStat
#from gold.track.TrackFormat import TrackFormatReq
from quick.statistic.ThreeWayProportionalBpOverlapStat import ThreeWayProportionalBpOverlapStat
#from quick.statistic.ThreeWayBpOverlapProportionalToGlobalBpsStat import ThreeWayBpOverlapProportionalToGlobalBpsStat
from quick.util.CommonFunctions import numAsPaddedBinary

class ThreeWayExpectedBpOverlapStat(MagicStatFactory):
    pass

            
class ThreeWayExpectedBpOverlapStatUnsplittable(Statistic):
    def _compute(self):        
        propOverlap = self._children[0].getResult()
        numTracks = len(propOverlap.keys()[0]) #due to binary coding of track combinations
        res = {}
        for comb in range(0,2**numTracks): #enumerate with binary number corresponding to all subsets
            #print 'comb:',comb
            binary = numAsPaddedBinary(comb,numTracks)
            if comb==0:
                combinedOverlap = 1.0
            else:
                combinedOverlap = propOverlap[binary]
                #print 'using base for binary %s: %s' % (binary, propOverlap[binary])
            for index, wasPartOfCombined in enumerate(binary):
                #if not wasPartOfCombined:
                if wasPartOfCombined=='0':
                    combinedOverlap *= propOverlap[ numAsPaddedBinary(2**(numTracks-index-1),numTracks) ]
                    #print 'multiplying %s, i.e. %s' % (numAsPaddedBinary(2**(numTracks-index-1),numTracks), propOverlap[ numAsPaddedBinary(2**(numTracks-index-1),numTracks) ])
            res[binary.replace('0','*').replace('1','&')] = combinedOverlap
        
        return res
                        
    def _createChildren(self):
        self._addChild( ThreeWayProportionalBpOverlapStat(self._region, self._track, self._track2, **self._kwArgs) )
