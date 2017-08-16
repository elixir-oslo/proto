from collections import OrderedDict
from collections import defaultdict
from time import time

from config.Config import DATA_FILES_PATH, HB_SOURCE_CODE_BASE_DIR
from gold.track.GenomeRegion import GenomeRegion
from gold.track.Track import PlainTrack
from proto.hyperbrowser.HtmlCore import HtmlCore
from proto.hyperbrowser.StaticFile import StaticFile, GalaxyRunSpecificFile
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.extra.MotifScanner import MotifScanner
from quick.webtools.GeneralGuiTool import GeneralGuiTool


class AnalyzeTfsVersusSnv(GeneralGuiTool):
    
    DATA_REPO = 'ENCODE-TRANSFAC-based'
    EXT_DATA_SRC = 'from history'
    
    @staticmethod
    def getToolName():
        return "TF-SNV"

    @staticmethod
    def getInputBoxNames():
        "Returns a list of names for input boxes, implicitly also the number of input boxes to display on page. Each such box will call function getOptionsBoxK, where K is in the range of 1 to the number of boxes"
        return [('Select genome','genome'), ('Select source for datasets', 'datasource'), ('Select GTrackSuite dataset from history', 'history'), ('Select Cell types','celltype'), ('Select variation track','track'),
            ('Select source for PWM', 'pwmsource'), ('Select PWM dataset from history', 'pwmhistory'),('Expand binding regions', 'expand')]#('Select cell type', 'celltype')
    
    @staticmethod    
    def getOptionsBoxGenome():
        return '__genome__'
    
    @classmethod    
    def getOptionsBoxDatasource(cls, prevChoices):
        return ['-----  Select  -----', cls.DATA_REPO, cls.EXT_DATA_SRC]
    
    @classmethod    
    def getOptionsBoxHistory(cls, prevChoices):
        if prevChoices.datasource == cls.EXT_DATA_SRC:
            return '__history__',
    
    @classmethod    
    def getOptionsBoxCelltype(cls, prevChoices):
        if prevChoices.history and prevChoices.history != '-----  Select  -----':
            resultSet = set([line.split('\t')[1] for line in open(ExternalTrackManager.extractFnFromGalaxyTN(prevChoices.history.split(':'))).readlines()[1:] if line.find('\t')>0])
            #return ['Hello World']
            return OrderedDict([(v, False) for v in resultSet])
    
    @classmethod    
    def getOptionsBoxPwmsource(cls, prevChoices):
        if prevChoices.datasource != '-----  Select  -----':
            return ['-----  Select  -----', cls.DATA_REPO, cls.EXT_DATA_SRC]
    
    @classmethod    
    def getOptionsBoxPwmhistory(cls, prevChoices):
        if prevChoices.pwmsource == cls.EXT_DATA_SRC:
            return '__history__',
    
#    @classmethod    
#    def getOptionsBoxCelltype(cls, prevChoices):
#        
#        #encodeFile = open('/usit/invitro/hyperbrowser/staticFiles/kaitre/files.txt')
#	encodeFile = open(StaticFile(['files','kaitre','files.txt']).getDiskPath())
#        encodeTab = [v for v in encodeFile.read().split('\n') if v.find('dataType=ChipSeq;')>0]
#        
#        terms = cls.putENCODEContolVocabulary('Cell Line')
#        
#
#        candidateCells = terms.keys() #[k for k, v in t if v.get('type') == 'Cell Line']
#        cellCounter = defaultdict(int)
#        for line in encodeTab:
#            cellCounter[line.split('cell=')[1].split(';')[0]] +=1
#        
#        countSorted = sorted([(v,k)for k, v in cellCounter.items() if v>10], reverse=True)
#        return ['%s(%i)' % (v,k) for k, v in countSorted]
           
        #return ['K562'] #will be read from disk, based on existing subtracks at some level..

    @staticmethod    
    def getOptionsBoxTrack(prevChoices):
        if prevChoices.datasource != '-----  Select  -----':
            return ('__history__', 'category.bed', 'gtrack') #check that correct format..

    #@staticmethod    
    #def getOptionsBoxData(prevChoices):
    #    return '__history__', 'bed'
    #    #return ['Use TF ChIP-seq and DNAse footprints', 'Use only TF ChIP-seq', 'Use only DNAse footprints']
    
    #@staticmethod    
    #def getOptionsBoxPwm(prevChoices):
    #    return ('__history__',)
    
    @staticmethod    
    def getOptionsBoxExpand(prevChoices):
        if prevChoices.track:
            return '0'
    
    
    @classmethod    
    def convertGTrackSuiteToDict(cls, fn):
        trackPrefixConverter = {'hb//':'', '':''}
        res = defaultdict(dict)
        with open(fn) as fil:
            head = fil.readline()
            for line in fil:
                row = line.strip().split('\t')
                track, cell, tf, pwm = row[:4]
                #track = trackPrefixConverter[track]
                if res[cell].has_key(tf):
                    res[cell][tf].append((track,pwm))
                else:
                    res[cell][tf] = [(track, pwm)]
        return res
    
    
    @classmethod    
    def execute(cls, choices, galaxyFn=None, username=''):
        from quick.application.ProcTrackOptions import ProcTrackOptions
        #from quick.application.ProcTrackOptions import ProcTrackOptions
        #SHELVE_FN = DATA_FILES_PATH + sep + 'TrackInfo.shelve'
        #trackInfoShelve = shelve.open(SHELVE_FN, 'c')
        #
        #cellType = choices.celltype.split('(')[0].strip()
        #hg19Keys = [k for k in trackInfoShelve.keys() if k.startswith('hg19:Gene regulation')]
        #print 'Size of trackInfo shelve(hg19):', len(hg19Keys)
        #
        ##code for finding candidate tracks for hg19 for selected celltype
        #trackCandidateDict = dict()
        #for tnStr in hg19Keys:
        #    value = trackInfoShelve.get(tnStr).description
        #    if re.search('cell='+cellType+'.*dataType=ChipSeq<.*view=Peaks<', value):
        #        tn = tnStr.split(':')
        #        if  ProcTrackOptions.isValidTrack(tn[0], tn[1:], True):
        #            trackCandidateDict[tnStr] = re.sub('[\-\_\s]','', value.split('antibody=')[1].split('<')[0].strip().upper())
        
        genome = choices.genome
        mutationTrack = choices.track.split(':')
        expand = choices.expand
        
        if choices.datasource == cls.DATA_REPO:
            dataFn = DATA_FILES_PATH + 'EncodeBasedTfMappings.txt'
        else:
            dataFn = ExternalTrackManager.extractFnFromGalaxyTN(choices.history.split(':'))
        gSuiteDict = cls.convertGTrackSuiteToDict(dataFn)
        
        cellTypeList = [k for k, v in choices.celltype.items() if v]
        motifFn = HB_SOURCE_CODE_BASE_DIR + '/data/all_PWMs.txt'
        motifFn2 = ExternalTrackManager.extractFnFromGalaxyTN(choices.pwmhistory.split(':')) if choices.pwmhistory else None
        
            
        motifScanObj = MotifScanner(motifFn, fn2=motifFn2)
        resultDict = dict()
        for cellType, tfDict in gSuiteDict.items():
            if not cellType in cellTypeList:
                continue
            
            multiTfDict = MultiExactlySpecifiedTF()
            for keyTf, trackPwmList in tfDict.items():
                for track, motifId in trackPwmList:
                    if not ProcTrackOptions.isValidTrack(genome, track.split(':'), True):
                        print 'missing or invalid track: ', track
                        continue
                    tfObj = ExactlySpecifiedTF(keyTf, track, motifId, [track.split(':'), mutationTrack], galaxyFn)
                    tfObj.getFastaFiles(genome)
                    tfObj.getPwmScores(motifId, motifScanObj)
                    multiTfDict[tfObj.tf+'_'+tfObj.chipSeqPeaks+'_'+motifId] = tfObj
            resultDict[cellType] = multiTfDict
        
        for cType, mDict in resultDict.items():
            print mDict.getHtmlResultsTable()    
            
        ##hardcoded tf til pwmId tfNames2pwmIdsFn 
        #DATA_PATH = DATA_FILES_PATH + '/tfbs'
        #tfNames2pwmIdsFn = DATA_PATH + '/tfNames2pwmIds.shelf'
        #tfToPwmIdsDict = shelve.open(tfNames2pwmIdsFn)
        #
        #multiTfDict = MultiExactlySpecifiedTF()
        #trackList = [v[0] for v in GalaxyInterface.getSubTrackNames(genome, ['Private','GWAS', cellType], deep=False)[0]]
        #count, tfNums = 0, len(tfToPwmIdsDict)
        #for keyTf, motifList in tfToPwmIdsDict.items(): 
        #    count+=1
        #    searchTF = re.sub('[\-\_\s]','', keyTf.upper())
        #    #print 'KEYTF!!!!!!,  ', keyTf, searchTF
        #    motifId = motifList[0]
        #    #finds the CHiPSeq tracks corresponding with celltype and  Tfs
        #    
        #    antibodyFor1TfList = [k for k ,v in cls.putENCODEContolVocabulary('Antibody').items() if v['targetId'] ==  'GeneCard:'+searchTF]    
        #    #they are used to find matches with trackCandidateDict
        #    tfTracks = [ key.split(':')[1:] for key, value in trackCandidateDict.items() if value in antibodyFor1TfList]
        #    
        #    if len(tfTracks)>0:
        #        print 'Found %i CHiPSeq track for TF = %s (Tf no. %i of %i)<br/>' % (len(tfTracks), keyTf, count, tfNums)
        #    for track in tfTracks:
        #        
        #        tfObj = ExactlySpecifiedTF(keyTf, ':'.join(track), motifId, [track, mutationTrack.split(':')], galaxyFn)
        #        tfObj.getFastaFiles(genome)
        #        tfObj.getPwmScores(motifId, moticScanObj)
        #        multiTfDict[tfObj.tf+'_'+tfObj.chipSeqPeaks] = tfObj
        #        
        #print multiTfDict.getHtmlResultsTable()
    
    @classmethod
    def putENCODEContolVocabulary(cls, termType):
        
        cvfile = open(StaticFile(['files','kaitre','cv.ra']).getDiskPath())
        thisinfo = {}
        terms = dict()
        for line in cvfile:
            line = line.strip()
            if line == '':
                if 'term' in thisinfo:
                    if thisinfo.has_key('type') and thisinfo['type'] == termType:
                        terms[thisinfo['term']] = thisinfo
                    
                thisinfo = {}
                continue
            if line[0]=='#':
                continue
	
            param, value = line.split(' ',1)
            thisinfo[param]=value
        return terms
    
    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not valid,
        an error text explaining the problem should be returned. The GUI then shows this text
        to the user (if not empty) and greys out the execute button (even if the text is empty).
        If all parameters are valid, the method should return None, which enables the execute button.
        '''
        return None
    
    @staticmethod
    def isPublic():
        return False
    
    
    #@classmethod
    #def ScanFastaforPwmMax(cls, motifFn, fastaFn):
    #    #motifFn = ExternalTrackManager.extractFnFromGalaxyTN(choices[0].split(':'))
    #    #fastaFn = ExternalTrackManager.extractFnFromGalaxyTN(choices[1].split(':'))
    #    
    #    from quick.webtools.tfbs.TestOverrepresentationOfPwmInDna import parseTransfacMatrixFile
    #    from third_party.MotifTools import Motif
    #    from third_party.Fasta import load
    #
    #    countMats = parseTransfacMatrixFile(motifFn)
    #    resultDict = dict()
    #    for motifId, countMat in countMats.items():
    #        motif = Motif(backgroundD={'A': 0.25, 'C': .25, 'G': .25, 'T': .25} )
    #        motif.compute_from_counts(countMat,0.1)
    #        motif.name = motifId
    #        
    #        
    #        seqs = load(fastaFn,lambda x:x)
    #        bestScores = [motif.bestscore(seq.upper()) for seq in seqs.values()]
    #        
    #        resultDict[motifId] =  dict([(str(key),score) for key,score in zip(seqs.keys(), bestScores)])
    #    return resultDict
    
    
    
    
   
        

    @staticmethod    
    def getOutputFormat(choices):
        return 'customhtml'    




class MultiExactlySpecifiedTF(dict):
    
    def __setitem__(self, key, item):
        assert isinstance(key, basestring)
        assert isinstance(item, ExactlySpecifiedTF)
        dict.__setitem__(self, key, item)
    
    
    def getHtmlResultsTable(self):
        
        headerTab = ['TF', 'Chip-seq peaks: ', 'PWM','Number of SNV-intersected binding regions',
                    'Highest binding difference','Avg binding difference', 'Number of regions with binding difference', 'Original Fasta', 'Mutated Fasta', 'PWM score for each region', 'Gtrack of PWM score for each region', 'BED of PWM score for each region']
        core = HtmlCore()
        core.begin()
        core.tableHeader(headerTab, sortable = True)
        for tfObj in self.values():
            if True:#hasattr(tfObj,'maxPwmDiff'):
                core.tableLine([tfObj.tf, tfObj.chipSeqPeaks, tfObj.pwm, tfObj.intersectingPoints, tfObj.maxPwmDiff, tfObj.avgPwmDiff, tfObj.numPwmDiff, tfObj.regularFasta.getLink('Original Fasta'), tfObj.mutatedFasta.getLink('Mutated Fasta'), tfObj.pwmDiffScore.getLink('PWM score for each region'), tfObj.gtrackDiffScore.getLink('Gtrack of PWM score for each region'), tfObj.bedPwmDiffScore.getLink('BED of PWM score for each region')])
        
        core.tableFooter()
        core.end()
        return str(core)


class ExactlySpecifiedTF(object):
    
    def __init__(self, tf, chipSeqPeaks, pwm, tracks, galaxyFn):
        self.tf = tf
        self.chipSeqPeaks = chipSeqPeaks
        self.pwm = pwm
        
        assert len(tracks) == 2
        self.track = tracks[0]
        self.mutationTrack = tracks[1]
        self.galaxyFn = galaxyFn
        
        self.bedPwmDiffScore = GalaxyRunSpecificFile(['pwmDiffScore', self.pwm+'_'.join(self.track),'pwmDiff.bed'], self.galaxyFn)
        self.pwmDiffScore = GalaxyRunSpecificFile(['pwmDiffScore', self.pwm+'_'.join(self.track),'pwmDiff.html'], self.galaxyFn)
        self.gtrackDiffScore = GalaxyRunSpecificFile(['pwmDiffScore', self.pwm+'_'.join(self.track),'pwmDiff.gtrack'], self.galaxyFn)
        self.mutatedFasta = GalaxyRunSpecificFile(['fastaFiles', '_'.join(self.track),'mutatedFastseq.fasta'], self.galaxyFn)
        self.regularFasta = GalaxyRunSpecificFile(['fastaFiles', '_'.join(self.track),'regularFastseq.fasta'], self.galaxyFn)
        
        self.maxPwmDiff = None
        self.avgPwmDiff = None
        self.numPwmDiff = 0
        
    def getFastaFiles(self, genome):
        assert self.track
        assert self.mutationTrack
        
        regionDict, pointDict = self.IntersectData(genome, [self.track, self.mutationTrack])
        self.intersectingPoints = str(sum([len(v) for v in regionDict.values()]))
        
        mutatedfastaDict = self.getMutatedSequence(genome, regionDict, pointDict)
        regularFastaDict = self.getMutatedSequence(genome, regionDict)
        
        
        self.mutatedFasta.writeTextToFile('\n'.join(['\n'.join(mutatedfastaDict[chrom]) for chrom in sorted(mutatedfastaDict.keys())]))
        self.regularFasta.writeTextToFile('\n'.join(['\n'.join(regularFastaDict[chrom]) for chrom in sorted(regularFastaDict.keys())]))
                
    @classmethod
    def getMutatedSequence(cls, genome, regionDict, pointDict=None):
        resultDict = defaultdict(list)
        regionList = []
        fastaTrack = PlainTrack( ['Sequence', 'DNA'] )
        for chrom in regionDict.keys():
            for start, end in regionDict[chrom]:
                
                
                seqTv = fastaTrack.getTrackView(GenomeRegion(genome, chrom, start, end))
                valList = list(seqTv.valsAsNumpyArray())
                if pointDict:
                    mutatedPoints = [v[1:] for v in pointDict[chrom] if v[0] == start]
                    for index, val in mutatedPoints:
                        val = val[-1] if val.find('>')>=0 else val
                        valList[index] = val
                resultDict[chrom].append('>%s %i-%i\n%s'%(chrom, start+1, end, ''.join(valList)))
        
        return resultDict
    
    
    @classmethod
    def IntersectData(cls, genome, tracks):
        from quick.util.CommonFunctions import getGeSource
        start = time()
        geSources = []
        for track in tracks:
            geSources.append(getGeSource(track, genome))
            #try:
            #    fileType = ExternalTrackManager.extractFileSuffixFromGalaxyTN(track)
            #    fn = ExternalTrackManager.extractFnFromGalaxyTN(track)
            #    if fileType == 'category.bed':
            #        geSources.append(BedCategoryGenomeElementSource(fn))
            #    elif fileType == 'gtrack':
            #        geSources.append(GtrackGenomeElementSource(fn))
            #    else:
            #        geSources.append(BedGenomeElementSource(fn))
            #    
            #except:
            #    geSources.append(FullTrackGenomeElementSource(genome, track, allowOverlaps=False))
                
        
        resultDict, pointDict = defaultdict(list), defaultdict(list)
        gs1, gs2 = geSources
        track1Dict, track2Dict = defaultdict(list), defaultdict(list)
        
        for ge in gs1:
            track1Dict[ge.chr].append((ge.start, ge.end))
        
        for ge in gs2:
            track2Dict[ge.chr].append((ge.start, ge.end, ge.val))
        
        
        for chrom in track1Dict.keys():
            counter = 0
            track2List = sorted(track2Dict[chrom])
            for start1, end1 in sorted(track1Dict[chrom]):
                while len(track2List)>counter:
                    start2, end2 , val= track2List[counter]
                    if start1<end2<=end1 or start1<=start2<end1:
                        resultDict[chrom].append([start1, end1])
                        pointDict[chrom].append([start1, start2-start1, str(val)])
                    elif start2<start1 and end2>end1:
                        resultDict[chrom].append([start1, end1])
                        pointDict[chrom].append([start1, start2-start1, str(val)])
                    elif start2>=end1:
                        break
                    counter+=1
        return resultDict, pointDict
    
    def getPwmScores(self, motifId, moticScanObj):
        pwmRegDict = moticScanObj.scanMotifInTwoSequences(motifId, self.regularFasta.getDiskPath(), self.mutatedFasta.getDiskPath())
        #pwmMutDict = moticScanObj.scanMotifInSequence(motifId, self.mutatedFasta.getDiskPath())
        #pwmRegDict = moticScanObj.scanMotifInSequence(motifId, self.regularFasta.getDiskPath())
        diffResDict = defaultdict(list)
        lineTab = []
        for region in sorted(pwmRegDict):
            chrom, start = region.split()
            end = region.replace('-',' ').split()[-1]
            start = int(start.split('-')[0])
            regular, mutated =  pwmRegDict[region]
            difference = abs(regular[0] - mutated[0])
            reg, regMut, mut, mutReg = regular[:2] + mutated[:2]
            regSeq, regMutSeq, regPos = regular[2:]
            mutSeq, mutRegSeq, mutPos = mutated[2:]
            #print 'regSeq, regMutSeq, regPos: ', regSeq, regMutSeq, regPos, type(regSeq), type(regMutSeq), type(regPos)
            string = '%s\t%f\t[%f -> %f]\t[%f -> %f]\t' % (region.replace('-',' ').replace(' ','\t'), difference, reg, regMut, mut, mutReg )
            string += '%s:%i-%i\t%s\t%s\t' % (chrom, start+regPos[0], start+regPos[1], regSeq, regMutSeq)
            string += '%s:%i-%i\t%s\t%s' % (chrom, start+mutPos[0], start+mutPos[1], mutSeq, mutRegSeq)
            diffResDict[difference].append(string)
            lineTab.append([chrom, str(start), str(end), str(difference), '[%f -> %f]'%(reg, regMut), '[%f -> %f]'%(mut, mutReg),
                            '%s:%i-%i' % (chrom, start+regPos[0], start+regPos[1]), regSeq, regMutSeq,
                            '%s:%i-%i' % (chrom, start+mutPos[0], start+mutPos[1]), mutSeq, mutRegSeq])
        #(scores[bestIndx], mScores[bestIndx], matches[bestIndx], mMatches[bestIndx], endpoints[bestIndx]), (mScores[mBestIndx], scores[mBestIndx], mMatches[mBestIndx], matches[mBestIndx], mEndpoints[mBestIndx])]
        
        diffList = diffResDict.keys()
        if len(diffList)>0:
            self.maxPwmDiff = str(max(diffList))
            self.avgPwmDiff = str(sum(diffList)/len(diffList))
            self.numPwmDiff = len(diffList)
            line = '# GTrack file\n#The columns in this dataset are:\n#\t(ChIP-seq_peak)chr\n#\tstart\n#\tend\n#\tmax(difference in column 5, difference in column 6)\n#\t[best_reference_sequence_PWM_hit_score -> corresponding_mutated_sequence_score]\n#\t[best_mutated_sequence_PWM_hit_score -> corresponding_reference_sequence_score]\n#\tchr:start-end(best_reference_sequence_PWM_hit_motif)\n#\tbest_reference_sequence_PWM_hit_motif\n#\tcorresponding_mutated_sequence_motif\n#\tchr:start-stop(best_mutated_sequence_PWM_hit_motif)\n#\tbest_mutated_sequence_PWM_hit_motif\n#\tcorresponding_reference_sequence_motif)\n##track type: valued segments\n##value column: val\n###seqid\tstart\tend\tval\treference_sequence_PWM\tmutated_sequence_PWM_hit_score\tbest_reference_sequence_PWM_hit_motif\tcorresponding_mutated_sequence_motif\tchr:start-stop(best_mutated_sequence_PWM_hit_motif)\tbest_mutated_sequence_PWM_hit_motif\tcorresponding_reference_sequence_motif\n'
            self.gtrackDiffScore.writeTextToFile(line)
            self.pwmDiffScore.writeTextToFile(self.getHtmlPwmTable(lineTab))
            self.bedPwmDiffScore.writeTextToFile('\n'.join(['\t'.join(v[:4])for v in lineTab]))
            for k in sorted(diffResDict.keys(), reverse=True):
                line = '\n'.join(diffResDict[k])
                #self.pwmDiffScore.writeTextToFile(line)
                self.gtrackDiffScore.writeTextToFile(line, mode='a')
    
    
    def getHtmlPwmTable(self, lineTab):
        headerTab = ['chrom', 'start', 'end', 'max PWM difference', 'best reference seq_PWM score -> corresponding mut seq score', 'best mut seq PWM score -> corresponding_ref seq score',
                     'ref region', 'ref seq', 'corresponding mut seq', 'mut region', 'mut seq', 'corresponding ref seq']
        core = HtmlCore()
        core.begin()
        core.tableHeader(headerTab, sortable = True)
        for row in lineTab:
            if True:#hasattr(tfObj,'maxPwmDiff'):
                core.tableLine(row)
        core.tableFooter()
        core.end()
        return str(core)
    
    def makeHtmlStr(self):
        htmlPage = GalaxyRunSpecificFile(['html', '_'.join(self.track),'page.html'], self.galaxyFn)
        htmlStr = 'TF: ' + self.tf +'<br/>\nChip-seq peaks: '+self.chipSeqPeaks+'<br/>\nPWM: '+self.pwm+'<br/>\nNumber of SNV-intersected binding regions: '+self.intersectingPoints+'<br/>\nHighest binding difference: '+self.maxPwmDiff+'<br/>\nAvg binding difference: '+self.avgPwmDiff+'<br/>\n'+self.regularFasta.getLink('Original Fasta')+'<br/>\n'+self.mutatedFasta.getLink('Mutated Fasta')+'<br/>\n'+ self.pwmDiffScore.getLink('PWM score for each region') +'<br/>\n'+ self.gtrackDiffScore.getLink('Gtrack of PWM score for each region') 
        htmlPage.writeTextToFile(htmlStr)
        return htmlPage.getLink(self.tf +':   '+self.track[-1])


#    from quick.webtools.GeneralGuiTool import GeneralGuiTool
#from gold.statistic.AllStatistics import STAT_CLASS_DICT
#from gold.statistic.MagicStatFactory import MagicStatFactory
#from quick.application.UserBinSource import UserBinSource
##from gold.application.StatRunner import StatJob        
#from os import sep
#from quick.util.GenomeInfo import GenomeInfo
#import time
#from config.Config import NONSTANDARD_DATA_PATH
#from quick.application.GalaxyInterface import GalaxyInterface
#from gold.application.StatRunner import *
##This is a template prototyping GUI that comes together with a corresponding web page.
##
#
#class Tool4(GeneralGuiTool):
#    @staticmethod
#    def getToolName():
#        return "Multiply number"
#
#    @staticmethod
#    def getInputBoxNames():
#        "Returns a list of names for input boxes, implicitly also the number of input boxes to display on page. Each such box will call function getOptionsBoxK, where K is in the range of 1 to the number of boxes"
#        return ['select genome', 'select track','select randomization class','select intensity track (if needed)']
#    
#    @staticmethod    
#    def getOptionsBox1():
#        return '__genome__'
#    
#    @staticmethod    
#    def getOptionsBox2(prevChoices):
#        return '__track__'
#
#    @staticmethod    
#    def getOptionsBox3(prevChoices):
#        return ['PermutedSegsAndIntersegsTrack','PermutedSegsAndSampledIntersegsTrack','ShuffledMarksTrack','SegsSampledByIntensityTrack','RandomGenomeLocationTrack']
#
#    @staticmethod    
#    def getOptionsBox4(prevChoices):
#        return '__track__'
#        
#    @classmethod    
#    def execute(cls, choices, galaxyFn=None, username=''):
#        start = time.time()
#        genome = choices[0]
#        trackName = choices[1].split(':')
#        #outFn = open(NONSTANDARD_DATA_PATH+'/hg19/Private/Sigven/resultat.bed','w')
#        randTrackClass = choices[2]
#        analysisDef = ' RandTrackClass [randTrackClass=%s] -> RandomizedRawDataStat' % randTrackClass
#        tnIntensity = choices[3].split(':') if choices[3] is not None else None
#        for regSpec in  GenomeInfo.getChrList(genome):
#            res = GalaxyInterface.runManual([trackName], analysisDef, regSpec, '*', genome, username=username, \
#                                            printResults=False, printHtmlWarningMsgs=False, trackNameIntensity=tnIntensity)
#
#            from gold.origdata.TrackGenomeElementSource import TrackViewGenomeElementSource, TrackViewListGenomeElementSource
#            from gold.origdata.BedComposer import BedComposer
#            
#            tvGeSource = TrackViewListGenomeElementSource(genome, [resDict['Result'] for resDict in res.values()], trackName)
#            BedComposer(tvGeSource).composeToFile(galaxyFn)
#                
#        #print 'run with Stat=%s, took(secs): ' % analysisDef, time.time()-start
#        
#    @staticmethod
#    def validateAndReturnErrors(choices):
#        '''
#        Should validate the selected input parameters. If the parameters are not valid,
#        an error text explaining the problem should be returned. The GUI then shows this text
#        to the user (if not empty) and greys out the execute button (even if the text is empty).
#        If all parameters are valid, the method should return None, which enables the execute button.
#        '''
#        return None
#    
#    #@staticmethod
#    #def isPublic():
#    #    return False
#    #
#    #@staticmethod
#    #def isRedirectTool():
#    #    return False
#    #
#    #@staticmethod
#    #def isHistoryTool():
#    #    return True
#    #
#    #@staticmethod
#    #def isDynamic():
#    #    return True
#    #
#    #@staticmethod
#    #def getResetBoxes():
#    #    return [1]
#    #
#    #@staticmethod
#    #def getToolDescription():
#    #    return ''
#    #
#    #@staticmethod
#    #def getToolIllustration():
#    #    return None
#    #
#    #@staticmethod
#    #def isDebugMode():
#    #    return True
#    #
#    @staticmethod    
#    def getOutputFormat(choices):
#        return 'bed'
#    
