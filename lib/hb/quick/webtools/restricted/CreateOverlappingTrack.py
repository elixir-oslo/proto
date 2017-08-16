from quick.webtools.GeneralGuiTool import GeneralGuiTool

# This is a template prototyping GUI that comes together with a corresponding
# web page.

class CreateOverlappingTrack(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Create overlapping track"

    @staticmethod
    def getInputBoxNames():
        
        return ['select genome', 'Select track source','select track', 'Select track source', 'select track', 'Select track source', 'select track', 'Select track source', 'select track', 'Select track source', 'select track'] #Alternatively: [ ('box1','1'), ('box2','2') ]

    #@staticmethod
    #def getInputBoxOrder():
    #    '''
    #    Specifies the order in which the input boxes should be displayed, as a
    #    list. The input boxes are specified by index (starting with 1) or by
    #    key. If None, the order of the input boxes is in the order specified by
    #    getInputBoxNames.
    #    '''
    #    return None
    
    @staticmethod    
    def getOptionsBox1(): # Alternatively: getOptionsBoxKey()
        
        return '__genome__'
    
    @staticmethod    
    def getOptionsBox2(prevChoices):
        
        return '__multihistory__','bed','category.bed','valued.bed','bedgraph', 'gtrack'
    
    @staticmethod    
    def getOptionsBox3(prevChoices): # Alternatively: getOptionsBoxKey()
        return ('__hidden__','1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1')
    
    @staticmethod    
    def getOptionsBox4(prevChoices): # Alternatively: getOptionsBoxKey()
        return ['no','yes']
    
    @staticmethod    
    def getOptionsBox5(prevChoices):
        if prevChoices[-2] == 'yes':
            return '__track__'
    
    
    @staticmethod    
    def getOptionsBox6(prevChoices): # Alternatively: getOptionsBoxKey()
        if prevChoices[-2] and prevChoices[-2] != '-----  Select  -----':
            return '__track__'
    
    @staticmethod    
    def getOptionsBox7(prevChoices):
        
        if prevChoices[-2] and prevChoices[-2] != '-----  Select  -----':
            return '__track__'
    
    @staticmethod    
    def getOptionsBox8(prevChoices): # Alternatively: getOptionsBoxKey()
        
        if prevChoices[-2] and prevChoices[-2] != '-----  Select  -----':
            return '__track__'
    
    @staticmethod    
    def getOptionsBox9(prevChoices):
        
        if prevChoices[-2] and prevChoices[-2] != '-----  Select  -----':
            return '__track__'
    
    @staticmethod    
    def getOptionsBox10(prevChoices): # Alternatively: getOptionsBoxKey()
        if prevChoices[-2] and prevChoices[-2] != '-----  Select  -----':
            return '__track__'
    
    @staticmethod    
    def getOptionsBox11(prevChoices): # Alternatively: getOptionsBoxKey()
        
        if prevChoices[-2] and prevChoices[-2] != '-----  Select  -----':
            return '__track__'
    
  
        
    
    @classmethod    
    def execute(cls, choices, galaxyFn=None, username=''):
        
        from quick.application.ExternalTrackManager import ExternalTrackManager
        from collections import defaultdict
        from gold.origdata.BedGenomeElementSource import BedGenomeElementSource, BedCategoryGenomeElementSource
        from gold.origdata.GtrackGenomeElementSource import GtrackGenomeElementSource
        from gold.origdata.TrackGenomeElementSource import FullTrackGenomeElementSource
        from urllib import unquote
        print choices
        
        genome = choices[0]
        geSourceList, labelNames = [], []
        selectedHists = [unquote(val).split(':') for id,val in choices[1].iteritems() if val]
        inorout = [int(x) for x in  choices[2].split(',')]
        selectedHists += [v.split(':')for v in choices[3:]if v not in ['-----  Select  -----', 'no', 'yes', None,'']]
        for track in selectedHists: 
            try:
                fileType = ExternalTrackManager.extractFileSuffixFromGalaxyTN(track)
                fn = ExternalTrackManager.extractFnFromGalaxyTN(track)
                if fileType == 'category.bed':
                    geSourceList.append(BedCategoryGenomeElementSource(fn))
                elif fileType == 'gtrack':
                    geSourceList.append(GtrackGenomeElementSource(fn))
                else:
                    geSourceList.append(BedGenomeElementSource(fn))
                    
                labelNames.append(ExternalTrackManager.extractNameFromHistoryTN(track))
            except:
                geSourceList.append(FullTrackGenomeElementSource(genome, track, allowOverlaps=False))
                #labelNames.append(track[-1])
                labelNames.append(':'.join(track))
        
        primeList = [2,3,5,7,11, 13,17,19,23,29,31,37,41,43,47,53,59]
        resultCounter = defaultdict(int)
        posDict    = defaultdict(list)
        catDict  = defaultdict(list)
        
        debugstring = 'debug out:'
        
        for index, geSource in enumerate(geSourceList):
            primeNum = primeList[index]
            prevEnd = -1
            prevChr = ''
            for ge in geSource:
                
                posDict[ge.chr] += [ge.start, ge.end]
                catDict[ge.chr] += [primeNum, -primeNum]
                prevEnd = ge.end
                prevChr = ge.chr
        
        
        debugstring += 'posDict elements/2: ' + str(sum(len(v) for v in posDict.itervalues())/2)+'\n'
        debugstring += 'catDict elements/2: ' + str(sum(len(v) for v in catDict.itervalues())/2)+'\n'
        
        #maxState = reduce( lambda x, y: x*y, primeList[:len(geSourceList)] ) #assuming all tracks are in.
        selectedState = 1
        for n in range(len(geSourceList)):
            if inorout[n]:
                selectedState = selectedState * primeList[n]
        
        utfil = open(galaxyFn, 'w')
        for chrom in posDict.keys():
            indxSortedList = sorted(range(len(posDict[chrom])), key=posDict[chrom].__getitem__)
            
            posList = posDict[chrom]
            catList = catDict[chrom]
            catCoverageDepth = defaultdict(int)

            currentState = 1
            currentPos = 0
            
            for indx in indxSortedList:
                pos = posList[indx]
                primeVal = catList[indx]
                #print 'pos, primeVal: ', pos, primeVal
                #print 'resultCounter: ', resultCounter 
                if currentPos != pos:
                    if abs(currentState) == selectedState:
                        print>>utfil, '%s\t%i\t%i' % (chrom, currentPos, pos)
                    resultCounter[abs(currentState)] += pos-currentPos
                    #debugstring +='resultCounter='+str(resultCounter)+ ' currentPos='+ str(currentPos) + '    pos='+str(pos)+ '   chrom='+str(chrom)+  '   primeVal='+str(primeVal)+ '    catCoverageDepth='+str(catCoverageDepth) +'<br/>'
                    #print 'resultCounter,currentState,  pos and currentPos',abs(currentState),':',  pos, currentPos
                    currentPos=pos
                
                if primeVal<0:
                    catCoverageDepth[abs(primeVal)] -= 1
                    if catCoverageDepth[abs(primeVal)] == 0:
                        currentState/=primeVal
                else:
                    catCoverageDepth[primeVal] += 1
                    if catCoverageDepth[primeVal] == 1:
                        currentState*=primeVal
                    
        
        utfil.close()
        
                
    @staticmethod    
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'bed'    
 
