from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic, StatisticDictSumResSplittable
from gold.statistic.RawSegsOverlapStat import RawSegsOverlapStat

class TwoLevelOverlapPreferenceStat(MagicStatFactory):
    pass

class TwoLevelOverlapPreferenceStatSplittable(StatisticDictSumResSplittable):
    def _combineResults(self):
        StatisticDictSumResSplittable._combineResults(self)
        self._result['t1prop'] = float(self._result['t1coverage']) / self._result['NumBps']
        self._result['t2prop'] = float(self._result['t2coverage']) / self._result['NumBps']
        self._result['ExpBothBpProportionGivenIndividualBinCoverage'] = self._result['ExpBothBpCoverageGivenIndividualBinCoverage'] / self._result['NumBps']
        self._result['ExpBothBpProportionFromGlobalIndividualCoverage'] = self._result['t1prop'] * self._result['t2prop']

        from proto.RSetup import robjects, r
        t1Props = [x['t1prop'] for x in self._childResults]
        t2Props = [x['t2prop'] for x in self._childResults]

        if len(t1Props)>1:
            correlation = float(r.cor(robjects.FloatVector(t1Props), robjects.FloatVector(t2Props)))
            import numpy
            if numpy.isnan(correlation):
                correlation = None
                correlationPval  = None
            else:
                correlationPval = r('function(x,y){res=cor.test(x,y); return(res$p.value)}')(robjects.FloatVector(t1Props), robjects.FloatVector(t2Props))
                
            #print 'CORR: ',type(correlation), correlation            
        else:
            correlationPval = correlation = None
            
        self._result['IndividualCoveragePerBinCorrelation'] = correlation
        self._result['IndividualCoveragePerBinCorrelationPvalue'] = correlationPval
        
        self._result['ObsBpProportionOverlap'] = (float(self._result['ObsBpOverlap'])/ self._result['NumBps']) if self._result['NumBps']>0 else None
        self._result['RatioOfObsToExpGivenGlobalCoverages'] = (self._result['ObsBpProportionOverlap'] / self._result['ExpBothBpProportionFromGlobalIndividualCoverage']) if self._result['ExpBothBpProportionFromGlobalIndividualCoverage'] >0 else None
        self._result['RatioOfObsToExpGivenIndividualBinCoverages'] = (self._result['ObsBpProportionOverlap'] / self._result['ExpBothBpProportionGivenIndividualBinCoverage']) if self._result['ExpBothBpProportionGivenIndividualBinCoverage']>0 else None
        
class TwoLevelOverlapPreferenceStatUnsplittable(Statistic):    
    def _compute(self):     
        neither,only1,only2,both = [ self._children[0].getResult()[key] for key in ['Neither','Only1','Only2','Both'] ]

        numBps = neither+only1+only2+both
        
        res = {}
        t1Coverage = only1+both
        t2Coverage = only2+both
        res['t1coverage'] = t1Coverage
        res['t2coverage'] = t2Coverage 
        res['t1prop'] = float(t1Coverage)/(numBps)
        res['t2prop'] = float(t2Coverage )/(numBps)
        res['ExpBothBpCoverageGivenIndividualBinCoverage'] = t1Coverage * res['t2prop']
        res['NumBps'] = numBps
        res['ExpBothBpProportionGivenIndividualBinCoverage'] = res['ExpBothBpCoverageGivenIndividualBinCoverage'] / numBps
        res['ObsBpOverlap'] = both
        res['ObsBpProportionOverlap'] = float(both )/ numBps

        #To be computed at global level by splittable version:
        res['ExpBothBpProportionFromGlobalIndividualCoverage'] = None
        res['IndividualCoveragePerBinCorrelation'] = None
        res['RatioOfObsToExpGivenGlobalCoverages'] = None
        res['RatioOfObsToExpGivenIndividualBinCoverages'] = None
        
        return res
        
    
    def _createChildren(self):
        self._addChild( RawSegsOverlapStat(self._region, self._track, self._track2) )
