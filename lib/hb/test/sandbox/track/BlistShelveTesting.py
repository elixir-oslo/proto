import shelve
from blist import sorteddict
from collections import namedtuple, OrderedDict
from gold.util.CustomExceptions import InvalidFormatError
from gold.util.CompBinManager import CompBinManager
from quick.util.GenomeInfo import GenomeInfo

BoundingRegionInfo = namedtuple('BoundingRegionInfo', ['start', 'end', 'startIdx', 'endIdx', 'startBinIdx', 'endBinIdx'])

def storeShelve(genome, brTuples, sparse=True):
    boundingRegionShelve = shelve.open('/tmp/brshelve.shelve', 'c', writeback=True)
    
    lastRegion = None
    chrStartIdxs = OrderedDict()
    chrEndIdxs = OrderedDict()
    totElCount = 0
    totBinCount = 0
    
    for br in brTuples:
        if lastRegion is not None:
            if br.region < lastRegion:
                raise InvalidFormatError("Error: bounding regions are unsorted: %s > %s. The Genomic HyperBrowser preprocessor requires sorted bounding regions." % (lastRegion, br.region))
            if lastRegion.overlaps(br.region):
                raise InvalidFormatError("Error: bounding regions '%s' and '%s' overlap." % (lastRegion, br.region))
        
        if len(br.region) < 1:
            raise InvalidFormatError("Error: bounding region '%s' does not have positive length." % br.region)
        
        if lastRegion is None or br.region.chr != lastRegion.chr:
            boundingRegionShelve[br.region.chr] = sorteddict()
            if sparse:
                chrStartIdxs[br.region.chr] = totElCount
                #chrLen = GenomeInfo.getChrLen(br.region.genome, br.region.chr)
                #startIdx, endIdx, startBinIdx = totElCount, totElCount, totBinCount
                #endBinIdx = totBinCount + CompBinManager.getNumOfBins(GenomeRegion(start=0, end=chrLen))
                #chrInfo[br.region.chr] = BoundingRegionInfo(0, chrLen, startIdx, endIdx, startBinIdx, endBinIdx)
        
        startIdx, endIdx = (totElCount, totElCount + br.elCount) if not sparse else (None, None)
        totElCount += br.elCount
        chrEndIdxs[br.region.chr] = totElCount
        #print startIdx, endIdx, totElCount
        
        #if sparse:
        #    binCount = CompBinManager.getNumOfBins(br.region)
        #    startBinIdx, endBinIdx = totBinCount, totBinCount + binCount
        #    totBinCount += binCount
        #    print startBinIdx, endBinIdx, totBinCount
        #else:
        #    startBinIdx, endBinIdx = None, None
        
        boundingRegionShelve[br.region.chr][br.region.start] = BoundingRegionInfo(br.region.start, br.region.end, startIdx, endIdx, None, None)
        
        lastRegion = br.region
    
    if sparse:
        totBinCount = 0
        for chr in chrStartIdxs:
            #print chr
            chrLen = GenomeInfo.getChrLen(genome, chr)
            numBinsInChr = CompBinManager.getNumOfBins(GenomeRegion(start=0, end=chrLen))
            for key in boundingRegionShelve[chr].keys():
                startBinIdx = totBinCount
                endBinIdx = totBinCount + numBinsInChr
                brInfo = boundingRegionShelve[chr][key]
                boundingRegionShelve[chr][key] = BoundingRegionInfo(brInfo.start, brInfo.end, \
                                                                    chrStartIdxs[chr], chrEndIdxs[chr], \
                                                                    startBinIdx, endBinIdx)
            totBinCount += numBinsInChr
            #print boundingRegionShelve[chr]
        
    boundingRegionShelve.sync()
    
def getBoundingRegionInfo(region):
    boundingRegionShelve = shelve.open('/tmp/brshelve.shelve')
    #print region
    
    if region.chr in boundingRegionShelve:
        idx = boundingRegionShelve[region.chr].keys().bisect_right(region.start)
        #print boundingRegionShelve[region.chr]
        #print idx
        
        if idx > 0:
            key = boundingRegionShelve[region.chr].keys()[idx-1]
            brInfo = boundingRegionShelve[region.chr][key]
            if region.start < brInfo.end and region.end <= brInfo.end:
                return brInfo
    
    raise Exception("Bounding region encompassing region '%s' was not found." % region)

brTuples = [BoundingRegionTuple(GenomeRegion('TestGenome', 'chr21', 0, 1000000), 10),\
            BoundingRegionTuple(GenomeRegion('TestGenome', 'chr21', 2000000, 2500000), 20),\
            BoundingRegionTuple(GenomeRegion('TestGenome', 'chrM', 1000, 2000), 5)]

for sparse in [False, True]:
    storeShelve('TestGenome', brTuples, sparse=sparse)

    print getBoundingRegionInfo(GenomeRegion('TestGenome', 'chr21', 50000, 52000))
    print getBoundingRegionInfo(GenomeRegion('TestGenome', 'chr21', 2050000, 2052000))
    print getBoundingRegionInfo(GenomeRegion('TestGenome', 'chrM', 1000, 2000))
    
    try:
        getBoundingRegionInfo(GenomeRegion('TestGenome', 'chr21', 50000, 1052000))
    except Exception, e:
        print e
    
    try:
        getBoundingRegionInfo(GenomeRegion('TestGenome', 'chr21', 1000000, 1052000))
    except Exception, e:
        print e
    
    try:
        getBoundingRegionInfo(GenomeRegion('TestGenome', 'chrM', 1500, 3000))
    except Exception, e:
        print e
    
    try:
        getBoundingRegionInfo(GenomeRegion('TestGenome', 'chr2', 100000, 110000))
    except Exception, e:
        print e
        
    import os
    os.remove('/tmp/brshelve.shelve')

for sparse in [False, True]:
    storeShelve('TestGenome', [], sparse=sparse)
    
    try:
        getBoundingRegionInfo(GenomeRegion('TestGenome', 'chr21', 50000, 52000))
    except Exception, e:
        print e
        
    import os
    os.remove('/tmp/brshelve.shelve')
