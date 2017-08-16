from config.Config import COMP_BIN_SIZE, IS_EXPERIMENTAL_INSTALLATION
from config.Config import ALLOW_COMP_BIN_SPLITTING as CFG_ALLOW_COMP_BIN_SPLITTING
from gold.track.GenomeRegion import GenomeRegion
from quick.util.GenomeInfo import GenomeInfo
from gold.util.CommonFunctions import isIter

class CompBinManager:
    #ALLOW_COMP_BIN_SPLITTING = True
    ALLOW_COMP_BIN_SPLITTING = CFG_ALLOW_COMP_BIN_SPLITTING
    
    
    @staticmethod
    def splitUserBin(region):
        'Splits a region into several compBins, based on borders as defined by getCompBinSize'
        #assert( len(region) > 0 )
        start = (int(region.start) / CompBinManager.getCompBinSize()) * CompBinManager.getCompBinSize() #round off to nearest whole compBin border        
        compBins = []
    
        while start < region.end:
            part = GenomeRegion(region.genome, region.chr)
            end = start + CompBinManager.getCompBinSize()
            part.start =  max(start, region.start)
            part.end = min(end, region.end)
            compBins.append( part )
            start += CompBinManager.getCompBinSize()   
    
        return compBins

    @staticmethod
    def getIndexBinSize():
        return COMP_BIN_SIZE
    
    @staticmethod
    def getCompBinSize():
        return COMP_BIN_SIZE    

    @staticmethod
    def getBinNumber(pos):
        return pos / CompBinManager.getCompBinSize()

    @staticmethod
    def getPosFromBinNumber(binNum):
        return binNum * CompBinManager.getCompBinSize()

    @staticmethod
    def getOffset(pos, bin):
        return pos - (bin * CompBinManager.getCompBinSize())

    @staticmethod
    def isMemoBin(region):
        if not IS_EXPERIMENTAL_INSTALLATION:
            return CompBinManager.isCompBin(region)
        
        if CompBinManager.ALLOW_COMP_BIN_SPLITTING:
            isCompBin = CompBinManager.isCompBin(region)
            return isCompBin
        else:
            isChr = not hasattr(region, '__iter__') and any([region.chr, region.start, region.end] == [r.chr, r.start, r.end] \
                                                            for r in GenomeInfo.getChrRegs(region.genome))
            isChrArm = not hasattr(region, '__iter__') and any([region.chr, region.start, region.end] == [r.chr, r.start, r.end] \
                                                            for r in GenomeInfo.getChrArmRegs(region.genome))
            
            return (isChr or isChrArm)
        
    @staticmethod
    def isCompBin(region):
        if isIter(region):
            return False
        
        offsetOK = (CompBinManager.getOffset( region.start, CompBinManager.getBinNumber(region.start) ) == 0)
        lengthOK = (len(region) == min(CompBinManager.getCompBinSize(), GenomeInfo.getChrLen(region.genome, region.chr) - region.start))
        return offsetOK and lengthOK
    
    @staticmethod
    def getNumOfBins(region):
        #assert( len(region) > 0 )
        start = CompBinManager.getBinNumber(region.start)
        end = CompBinManager.getBinNumber(region.end - 1)        
        return end - start + 1
    
    @staticmethod
    def canBeSplitted(region):
        return CompBinManager.ALLOW_COMP_BIN_SPLITTING and CompBinManager.getNumOfBins(region) > 1
