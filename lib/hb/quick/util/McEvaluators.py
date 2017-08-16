from gold.util.CustomExceptions import ArgumentValueError
from collections import OrderedDict
PVAL_KEY = 'P-value'
M_KEY = 'NumMoreExtremeThanObs'
NUM_SAMPLES_KEY = 'NumResamplings'

from numpy import isnan,array, median

def evaluatePvalueAndNullDistribution(observedAndMcSamplesTuple, tail, rawStatisticMainClassName):
    observation = observedAndMcSamplesTuple[0]
    mcSamples = observedAndMcSamplesTuple[1]
    numResamplings = len(mcSamples)
    
    numpyRandResults = array(mcSamples)        
    
    nonNanNumpyRandResults = numpyRandResults[~isnan(numpyRandResults)]
    numberOfNonNanRandResults = len(nonNanNumpyRandResults)
    
    meanOfNullDistr = nonNanNumpyRandResults.mean(dtype='float64')
    medianOfNullDistr = median(nonNanNumpyRandResults)
    sdOfNullDistr = nonNanNumpyRandResults.std(dtype='float64')
    #sdCountFromNullOfObs = (observation - meanOfNullDistr) / sdOfNullDistr
    diffObsMean = (observation - meanOfNullDistr)
    
    # For more info on the formula for calculating p-values:
    # "Permutation P-values should never be zero: calculating exact P-values
    #  when permutations are randomly drawn" (http://www.ncbi.nlm.nih.gov/pubmed/21044043)
    numMoreExtreme = computeNumMoreExtreme(observation, mcSamples, tail)
    pval = computePurePseudoPvalue(observation, mcSamples, tail)
    return OrderedDict([(PVAL_KEY, pval), ('TSMC_'+rawStatisticMainClassName, observation), ('MeanOfNullDistr', meanOfNullDistr), \
                          ('MedianOfNullDistr', medianOfNullDistr), ('SdNullDistr', sdOfNullDistr), ('DiffFromMean', diffObsMean), (NUM_SAMPLES_KEY, numResamplings), \
                            ('NumSamplesNotNan', numberOfNonNanRandResults), (M_KEY,numMoreExtreme) ])

def evaluatePurePseudoPvalue(observedAndMcSamplesTuple, tail, rawStatisticMainClassName):
    observation = observedAndMcSamplesTuple[0]
    mcSamples = observedAndMcSamplesTuple[1]
    pval = computePurePseudoPvalue(observation, mcSamples, tail)
    return {PVAL_KEY:pval}

def computePurePseudoPvalue(observation, mcSamples, tail):
    numResamplings = len(mcSamples)
    if tail in ['right-tail', 'left-tail']:
        tailFactor = 1.0
    elif tail == 'two-tail':
        tailFactor = 2.0
    else:
        raise ArgumentValueError('Invalid value for tails argument:', tail)
    numMoreExtreme = computeNumMoreExtreme(observation, mcSamples, tail)
    pval = tailFactor * (numMoreExtreme+1) / (numResamplings+1)
    pval = min(1.0, pval)
    return pval

    
def computeNumMoreExtreme(observation, mcSamples, tail):
    numMoreExtremeRight = sum(1 for res in mcSamples \
                     if res >= observation ) 
    numMoreExtremeLeft = sum(1 for res in mcSamples \
                     if res <= observation ) 
    if tail == 'right-tail':
        return numMoreExtremeRight
    elif tail == 'left-tail':
        return numMoreExtremeLeft
    elif tail == 'two-tail':
        return min(numMoreExtremeLeft, numMoreExtremeRight)
    
    raise ArgumentValueError('Invalid value for tails argument:', tail)

    
    