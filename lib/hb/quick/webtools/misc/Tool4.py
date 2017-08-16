# from quick.webtools.GeneralGuiTool import GeneralGuiTool
# from gold.statistic.AllStatistics import STAT_CLASS_DICT
# from gold.statistic.MagicStatFactory import MagicStatFactory
# from quick.application.UserBinSource import UserBinSource
# #from gold.application.StatRunner import StatJob        
# from os import sep
# from quick.util.GenomeInfo import GenomeInfo
# from config.Config import NONSTANDARD_DATA_PATH
# from quick.application.GalaxyInterface import GalaxyInterface
# from gold.application.StatRunner import *
# import re
# from gold.track.Track import PlainTrack
# from collections import defaultdict, Counter
# from quick.application.ExternalTrackManager import ExternalTrackManager
# from gold.origdata.BedGenomeElementSource import BedGenomeElementSource, BedCategoryGenomeElementSource
# from gold.origdata.GtrackGenomeElementSource import GtrackGenomeElementSource
# from gold.origdata.TrackGenomeElementSource import FullTrackGenomeElementSource
# from gold.track.GenomeRegion import GenomeRegion
# from gold.track.Track import PlainTrack
# from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
# from quick.extra.MotifScanner import MotifScanner
# from quick.application.GalaxyInterface import GalaxyInterface
# from proto.hyperbrowser.HtmlCore import HtmlCore
# from collections import OrderedDict
# #This is a template prototyping GUI that comes together with a corresponding web page.
# #
# from third_party.safeshelve import shelve
# from config.Config import DATA_FILES_PATH
# from time import time
# 
# class Tool4(GeneralGuiTool):
#     @staticmethod
#     def getToolName():
#         return "TF-SNV"
# 
#     @staticmethod
#     def getInputBoxNames():
#         "Returns a list of names for input boxes, implicitly also the number of input boxes to display on page. Each such box will call function getOptionsBoxK, where K is in the range of 1 to the number of boxes"
#         return [('Select genome','genome'), ('Select TF', 'tf'), ('select tracks associated with TF','track')]
#     
#     @staticmethod    
#     def getOptionsBoxGenome():
#         return '__genome__'
#     
#     @classmethod    
#     def getOptionsBoxCelltype(cls, prevChoices):
#         
#         encodeFile = open('/usit/invitro/hyperbrowser/staticFiles/kaitre/files.txt')
#         encodeTab = [v for v in encodeFile.read().split('\n') if v.find('dataType=ChipSeq;')>0]
#         
#         terms = cls.putENCODEContolVocabulary('Cell Line')
#         
# 
#         candidateCells = terms.keys() #[k for k, v in t if v.get('type') == 'Cell Line']
#         cellCounter = defaultdict(int)
#         for line in encodeTab:
#             cellCounter[line.split('cell=')[1].split(';')[0]] +=1
#         
#         countSorted = sorted([(v,k)for k, v in cellCounter.items() if v>10], reverse=True)
#         return ['%s(%i)' % (v,k) for k, v in countSorted]
#            
#         #return ['K562'] #will be read from disk, based on existing subtracks at some level..
#     
#     @classmethod
#     def getTfTracks(cls, tf):
#         
#         nSHELVE_FN = DATA_FILES_PATH + sep + 'tfTracksDict.shelve'
#         #SHELVE_FN = DATA_FILES_PATH + sep + 'TrackInfo.shelve'
#         #trackInfoShelve = shelve.open(SHELVE_FN, 'c')
#         #hg19Keys = [k for k in trackInfoShelve.keys() if k.startswith('hg19:Gene regulation')]# and trackInfoShelve[k]['timeOfPreProcessing'] != None]
#         tfTracksShelve = shelve.open(nSHELVE_FN)
#         #tfNames2pwmIdsFn = DATA_FILES_PATH + '/tfbs/tfNames2pwmIds.shelf'
#         #tfs =  sorted(shelve.open(tfNames2pwmIdsFn).keys())
#         #count=0
#         #for t in tfs:
#             #count+=1
#             #tmp = [v for v in hg19Keys if v.find(':'+t)>0]
#             #if len(tmp)>0:
#             #    tfTracksShelve[t] = tmp
#             #if count>=1000:
#             #    tfTracksShelve.sync()
#             #    count=0
#         if tf in tfTracksShelve:
#             res = OrderedDict([(v, False) for v in tfTracksShelve[tf]] )
#         else:
#             res = None
#         tfTracksShelve.close()
#         return res          
#     
#     @classmethod    
#     def getOptionsBoxTrack(cls, prevChoices):
#         if prevChoices.tf:
#             return cls.getTfTracks(prevChoices.tf)
#         
#     @staticmethod    
#     def getOptionsBoxTf(prevChoices):
#         tfNames2pwmIdsFn = DATA_FILES_PATH + '/tfbs/tfNames2pwmIds.shelf'
#         return  sorted(shelve.open(tfNames2pwmIdsFn).keys())
#     
#     #@staticmethod    
#     #def getOptionsBoxPwm(prevChoices):
#     #    return ('__history__',)
#     
#     #@staticmethod    
#     #def getOptionsBoxExpand(prevChoices):
#     #    return '0'
#     #
#     @classmethod
#     def getSequence(cls, genome, chrom, regStr):
#         return 'aCgTnN'
# 
#     @classmethod
#     def getSequence(cls, sequence, regList):
#         mutD = {'n':['a','c','g','t'],'a':['c','g','t'], 'c':['a','g','t'], 'g':['c','g','t'], 't':['c','g','t']}
#         for start, end in regList:
#             for indx, val in enumerate(sequence[start:end]):
#                 pos = start + indx
#                 for m in mutD[val]:
#                     yield pos, m
#                     
#     @classmethod    
#     def execute(cls, choices, galaxyFn=None, username=''):
#         from quick.application.ProcTrackOptions import ProcTrackOptions
#         chrLength = GenomeInfo.getStdChrLengthDict(genome)
#         sequence = fastaTrack.getTrackView(GenomeRegion(genome, chrom, 0, chrLength[chrom])).valsAsNumpyArray()
#         plainTrackList = [PlainTrack([k.split(':')]) for k, v in choices.track if v]
#         for chrom in chrLength:
#             sequence = ''.join(list(fastaTrack.getTrackView(GenomeRegion(genome, chrom, 0, chrLength[chrom])).valsAsNumpyArray())).lower()
#             for pTrack in plainTrackList:
#                 tv = pTrack.getTrackView(GenomeRegion(genome, chrom, 0, chrLength[chrom]))
#                 regs = zip( list(tv.startsAsNumpyArray()), list(tv.endsAsNumpyArray()) )
#                 for pos, mut in cls.getSequence():
#                     pass
#                     #do som pwm shit for the mutation at this position
# 
#         print 'Hello world'
#         SHELVE_FN = DATA_FILES_PATH + sep + 'TrackInfo.shelve'
#         trackInfoShelve = shelve.open(SHELVE_FN, 'c')
#         
#         #cellType = choices.celltype.split('(')[0].strip()
#         hg19Keys = [k for k in trackInfoShelve.keys() if k.startswith('hg19:Gene regulation')]
#         #print 'Size of trackInfo shelve(hg19):', len(hg19Keys)
#         
#         #code for finding candidate tracks for hg19 for selected celltype
#         #trackCandidateDict = dict()
#         for tnStr in hg19Keys:
#             value = trackInfoShelve.get(tnStr).description
#             if re.search('cell='+cellType+'.*dataType=ChipSeq<.*view=Peaks<', value):
#                 tn = tnStr.split(':')
#                 if  ProcTrackOptions.isValidTrack(tn[0], tn[1:], True):
#                     trackCandidateDict[tnStr] = re.sub('[\-\_\s]','', value.split('antibody=')[1].split('<')[0].strip().upper())
#         
#         
#           
#         
#         print 'able to loop through all hg19 values time to run was: '  
#         #for val in trackInfoShelve.values():
#         #    print val
#         #    break
#         genome = choices.genome
#         
#         #mutationTrack = choices.track
#         bpValues = ['a','c','g','t','n']
#         chrRegions = [v.split(':') for v in choices.track.split(',')]
#         regionDict = dict([(v[0], [int(t) for t in v[-1].split('-')]) for v in chrRegions])
#         bedLineTemplate = '%s\t%i\t%i\t%s>%s'
#         svnFileObj = GalaxyRunSpecificFile(['svn_file'], galaxyFn)
#         with open(svnFileObj.getDiskPath(ensurePath=True), 'w') as bedObj:
#             
#             for chrom, regStr in chrRegions:
#                 start, end = [int(v) for v in regStr.split('-')]
#                 sequence = cls.getMutatedSequence(genome)#cls.getSequence(genome, chrom, regStr)
#                 for indx, bp in enumerate(sequence):
#                     position = start+indx
#                     bp = bp.lower()
#                     mutations = [v for v in bpValues if v!=bp]
#                     mutationStrList = [bedLineTemplate % (chrom, position, position+1, bp, mut) for mut in mutations]
#                     print>>bedObj, '\n'.join(mutationStrList)
#         
#         print svnFileObj.getLink('mutationFile')
#         return True
#         sequence = getSequence(genome)
#         expand = choices.expand
#         #hard coded motifFn all_PWMs.txt
#         motifFn = '/usit/invitro/data/hyperbrowser/hb_core_developer/trunk/data/all_PWMs.txt'#ExternalTrackManager.extractFnFromGalaxyTN(choices.pwm.split(':'))
#         moticScanObj = MotifScanner(motifFn)
#         
#         print genome, cellType, expand, mutationTrack
#         tfToChipSeqDict = {'c-Myc':'c-Myc', 'E2':'E2F6', 'STAT1':'STAT1'}
#         DATA_PATH = DATA_FILES_PATH + '/tfbs'
#         tfNames2pwmIdsFn = DATA_PATH + '/tfNames2pwmIds.shelf'
#         
#         
#         tfToPwmIdsDict = shelve.open(tfNames2pwmIdsFn)
#         multiTfDict = MultiExactlySpecifiedTF()
#         trackList = [v[0] for v in GalaxyInterface.getSubTrackNames(genome, ['Private','GWAS', cellType], deep=False)[0]]
#         count, tfNums = 0, len(tfToPwmIdsDict)
#         for keyTf, motifList in tfToPwmIdsDict.items(): #tfToChipSeqDict.items():
#             count+=1
#             searchTF = re.sub('[\-\_\s]','', keyTf.upper())
#             #print 'KEYTF!!!!!!,  ', keyTf, searchTF
#             start = time()
#             
#             
#             
#             #motifList = tfToPwmIdsDict[keyTf]
#             motifId = motifList[0]
#             #finds the CHiPSeq tracks corresponding with celltype and  Tfs
#             antibodyFor1TfList = [k for k ,v in cls.putENCODEContolVocabulary('Antibody').items() if v['targetId'] ==  'GeneCard:'+searchTF]    
#             
#             tfTracks = [ key.split(':')[1:] for key, value in trackCandidateDict.items() if value in antibodyFor1TfList]
#             #tfTracks = [['Private','GWAS', cellType]+[v] for v in trackList if re.match(valTf+'_', v)]
#             if len(tfTracks)>0:
#                 print 'Found %i CHiPSeq track for TF = %s (Tf no. %i of %i)<br/>' % (len(tfTracks), keyTf, count, tfNums)
#             for track in tfTracks:
#                 
#                 tfObj = ExactlySpecifiedTF(keyTf, ':'.join(track), motifId, [track, mutationTrack.split(':')], galaxyFn)
#                 tfObj.getFastaFiles(genome)
#                 tfObj.getPwmScores(motifId, moticScanObj)
#                 multiTfDict[tfObj.tf+'_'+tfObj.chipSeqPeaks] = tfObj
#                 
#         print multiTfDict.getHtmlResultsTable()
#     
#     @classmethod
#     def putENCODEContolVocabulary(cls, termType):
#         cvfile = open('/usit/invitro/hyperbrowser/staticFiles/kaitre/cv.ra')
#         
#         thisinfo = {}
#         terms = dict()
#         for line in cvfile:
#             line = line.strip()
#             if line == '':
#                 if 'term' in thisinfo:
#                     if thisinfo.has_key('type') and thisinfo['type'] == termType:
#                         terms[thisinfo['term']] = thisinfo
#                     
#                 thisinfo = {}
#                 continue
#             if line[0]=='#':
#                 continue
# 	
#             param, value = line.split(' ',1)
#             thisinfo[param]=value
#         return terms
#     
#     @staticmethod
#     def validateAndReturnErrors(choices):
#         '''
#         Should validate the selected input parameters. If the parameters are not valid,
#         an error text explaining the problem should be returned. The GUI then shows this text
#         to the user (if not empty) and greys out the execute button (even if the text is empty).
#         If all parameters are valid, the method should return None, which enables the execute button.
#         '''
#         return None
#     
#     @staticmethod
#     def isPublic():
#         return False
#     
#     
#     @classmethod
#     def ScanFastaforPwmMax(cls, motifFn, fastaFn):
#         #motifFn = ExternalTrackManager.extractFnFromGalaxyTN(choices[0].split(':'))
#         #fastaFn = ExternalTrackManager.extractFnFromGalaxyTN(choices[1].split(':'))
#         
#         from quick.webtools.tfbs.TestOverrepresentationOfPwmInDna import parseTransfacMatrixFile
#         from third_party.MotifTools import Motif
#         from third_party.Fasta import load
# 
#         countMats = parseTransfacMatrixFile(motifFn)
#         resultDict = dict()
#         for motifId, countMat in countMats.items():
#             motif = Motif(backgroundD={'A': 0.25, 'C': .25, 'G': .25, 'T': .25} )
#             motif.compute_from_counts(countMat,0.1)
#             motif.name = motifId
#             
#             
#             seqs = load(fastaFn,lambda x:x)
#             bestScores = [motif.bestscore(seq.upper()) for seq in seqs.values()]
#             
#             resultDict[motifId] =  dict([(str(key),score) for key,score in zip(seqs.keys(), bestScores)])
#         return resultDict
#     
#     
#     @classmethod
#     def IntersectData(cls, genome, tracks):
#         start = time()
#         
#         
#        
#         geSources = []
#         for track in tracks:
#             try:
#                 fileType = ExternalTrackManager.extractFileSuffixFromGalaxyTN(track)
#                 fn = ExternalTrackManager.extractFnFromGalaxyTN(track)
#                 if fileType == 'category.bed':
#                     geSources.append(BedCategoryGenomeElementSource(fn))
#                 elif fileType == 'gtrack':
#                     geSources.append(GtrackGenomeElementSource(fn))
#                 else:
#                     geSources.append(BedGenomeElementSource(fn))
#                 
#             except:
#                 geSources.append(FullTrackGenomeElementSource(genome, track, allowOverlaps=False))
#                 
#         
#         resultDict, pointDict = defaultdict(list), defaultdict(list)
#         gs1, gs2 = geSources
#         track1Dict, track2Dict = defaultdict(list), defaultdict(list)
#         
#         for ge in gs1:
#             track1Dict[ge.chr].append((ge.start, ge.end))
#         
#         for ge in gs2:
#             track2Dict[ge.chr].append((ge.start, ge.end, ge.val))
#         
#         
#         for chrom in track1Dict.keys():
#             counter = 0
#             track2List = sorted(track2Dict[chrom])
#             for start1, end1 in sorted(track1Dict[chrom]):
#                 while len(track2List)>counter:
#                     start2, end2 , val= track2List[counter]
#                     if start1<end2<=end1 or start1<=start2<end1:
#                         resultDict[chrom].append([start1, end1])
#                         pointDict[chrom].append([start1, start2-start1, str(val)])
#                     elif start2<start1 and end2>end1:
#                         resultDict[chrom].append([start1, end1])
#                         pointDict[chrom].append([start1, start2-start1, str(val)])
#                     elif start2>=end1:
#                         break
#                     counter+=1
#         return resultDict, pointDict
#     
#     @classmethod
#     def getMutatedSequence(cls, genome, regionDict, pointDict=None):
#         resultDict = defaultdict(list)
#         regionList = []
#         fastaTrack = PlainTrack( ['Sequence', 'DNA'] )
#         for chrom in regionDict.keys():
#             for start, end in regionDict[chrom]:
#                 
#                 
#                 seqTv = fastaTrack.getTrackView(GenomeRegion(genome, chrom, start, end))
#                 valList = list(seqTv.valsAsNumpyArray())
#                 if pointDict:
#                     mutatedPoints = [v[1:] for v in pointDict[chrom] if v[0] == start]
#                     for index, val in mutatedPoints:
#                         val = val[-1] if val.find('>')>=0 else val
#                         valList[index] = val
#                 resultDict[chrom].append('>%s %i-%i\n%s'%(chrom, start+1, end, ''.join(valList)))
#         
#         return resultDict
#         
# 
#     @staticmethod    
#     def getOutputFormat(choices):
#         return 'customhtml'    
# 
# 
# 
# 
# class MultiExactlySpecifiedTF(dict):
#     
#     def __setitem__(self, key, item):
#         assert isinstance(key, basestring)
#         assert isinstance(item, ExactlySpecifiedTF)
#         dict.__setitem__(self, key, item)
#     
#     
#     def getHtmlResultsTable(self):
#         
#         headerTab = ['TF', 'Chip-seq peaks: ', 'PWM','Number of SNV-intersected binding regions',
#                     'Highest binding difference','Avg binding difference', 'Original Fasta', 'Mutated Fasta', 'PWM score for each region']
#         core = HtmlCore()
#         core.begin()
#         core.tableHeader(headerTab, sortable = True)
#         for tfObj in self.values():
#             if hasattr(tfObj,'maxPwmDiff'):
#                 core.tableLine([tfObj.tf, tfObj.chipSeqPeaks, tfObj.pwm, tfObj.intersectingPoints, tfObj.maxPwmDiff, tfObj.avgPwmDiff, tfObj.regularFasta.getLink('Original Fasta'), tfObj.mutatedFasta.getLink('Mutated Fasta'), tfObj.pwmDiffScore.getLink('PWM score for each region')])
#         
#         core.tableFooter()
#         core.end()
#         return str(core)
# 
# 
# class ExactlySpecifiedTF(object):
#     
#     def __init__(self, tf, chipSeqPeaks, pwm, tracks, galaxyFn):
#         self.tf = tf
#         self.chipSeqPeaks = chipSeqPeaks
#         self.pwm = pwm
#         
#         assert len(tracks) == 2
#         self.track = tracks[0]
#         self.mutationTrack = tracks[1]
#         self.galaxyFn = galaxyFn
#     
#     def getFastaFiles(self, genome):
#         assert self.track
#         assert self.mutationTrack
#         
#         regionDict, pointDict = Tool4.IntersectData(genome, [self.track, self.mutationTrack])
#         self.intersectingPoints = str(sum([len(v) for v in regionDict.values()]))
#         
#         mutatedfastaDict = Tool4.getMutatedSequence(genome, regionDict, pointDict)
#         regularFastaDict = Tool4.getMutatedSequence(genome, regionDict)
#         
#         self.mutatedFasta = GalaxyRunSpecificFile(['fastaFiles', '_'.join(self.track),'mutatedFastseq.fasta'], self.galaxyFn)
#         self.mutatedFasta.writeTextToFile('\n'.join(['\n'.join(mutatedfastaDict[chrom]) for chrom in sorted(mutatedfastaDict.keys())]))
# 
#         self.regularFasta = GalaxyRunSpecificFile(['fastaFiles', '_'.join(self.track),'regularFastseq.fasta'], self.galaxyFn)
#         self.regularFasta.writeTextToFile('\n'.join(['\n'.join(regularFastaDict[chrom]) for chrom in sorted(regularFastaDict.keys())]))
#                 
#     
#     def getPwmScores(self, motifId, moticScanObj):
#         pwmMutDict = moticScanObj.scanMotifInSequence(motifId, self.mutatedFasta.getDiskPath())
#         pwmRegDict = moticScanObj.scanMotifInSequence(motifId, self.regularFasta.getDiskPath())
#         diffResDict = defaultdict(list)
#         
#         for region in sorted(pwmMutDict.keys()):
#             difference = abs(pwmMutDict[region] - pwmRegDict[region])
#             diffResDict[difference].append('%s\t%f\t%f\t%f'%(region, pwmMutDict[region],  pwmRegDict[region], difference))
#         
#         diffList = diffResDict.keys()
#         if len(diffList)>0:
#             self.maxPwmDiff = str(max(diffList))
#             self.avgPwmDiff = str(sum(diffList)/len(diffList))
#             
#             self.pwmDiffScore = GalaxyRunSpecificFile(['pwmDiffScore', motifId+'_'.join(self.track),'pwmDiff.bed'], self.galaxyFn)
#             self.pwmDiffScore.writeTextToFile( '\n'.join(['\n'.join(diffResDict[k]) for k in sorted(diffResDict.keys(), reverse=True)]) )
#     
#     def makeHtmlStr(self):
#         htmlPage = GalaxyRunSpecificFile(['html', '_'.join(self.track),'page.html'], self.galaxyFn)
#         htmlStr = 'TF: ' + self.tf +'<br/>\nChip-seq peaks: '+self.chipSeqPeaks+'<br/>\nPWM: '+self.pwm+'<br/>\nNumber of SNV-intersected binding regions: '+self.intersectingPoints+'<br/>\nHighest binding difference: '+self.maxPwmDiff+'<br/>\nAvg binding difference: '+self.avgPwmDiff+'<br/>\n'+self.regularFasta.getLink('Original Fasta')+'<br/>\n'+self.mutatedFasta.getLink('Mutated Fasta')+'<br/>\n'+ self.pwmDiffScore.getLink('PWM score for each region')
#         htmlPage.writeTextToFile(htmlStr)
#         return htmlPage.getLink(self.tf +':   '+self.track[-1])
# 
# 
# #    from quick.webtools.GeneralGuiTool import GeneralGuiTool
# #from gold.statistic.AllStatistics import STAT_CLASS_DICT
# #from gold.statistic.MagicStatFactory import MagicStatFactory
# #from quick.application.UserBinSource import UserBinSource
# ##from gold.application.StatRunner import StatJob        
# #from os import sep
# #from quick.util.GenomeInfo import GenomeInfo
# #import time
# #from config.Config import NONSTANDARD_DATA_PATH
# #from quick.application.GalaxyInterface import GalaxyInterface
# #from gold.application.StatRunner import *
# ##This is a template prototyping GUI that comes together with a corresponding web page.
# ##
# #
# #class Tool4(GeneralGuiTool):
# #    @staticmethod
# #    def getToolName():
# #        return "Multiply number"
# #
# #    @staticmethod
# #    def getInputBoxNames():
# #        "Returns a list of names for input boxes, implicitly also the number of input boxes to display on page. Each such box will call function getOptionsBoxK, where K is in the range of 1 to the number of boxes"
# #        return ['select genome', 'select track','select randomization class','select intensity track (if needed)']
# #    
# #    @staticmethod    
# #    def getOptionsBox1():
# #        return '__genome__'
# #    
# #    @staticmethod    
# #    def getOptionsBox2(prevChoices):
# #        return '__track__'
# #
# #    @staticmethod    
# #    def getOptionsBox3(prevChoices):
# #        return ['PermutedSegsAndIntersegsTrack','PermutedSegsAndSampledIntersegsTrack','ShuffledMarksTrack','SegsSampledByIntensityTrack','RandomGenomeLocationTrack']
# #
# #    @staticmethod    
# #    def getOptionsBox4(prevChoices):
# #        return '__track__'
# #        
# #    @classmethod    
# #    def execute(cls, choices, galaxyFn=None, username=''):
# #        start = time.time()
# #        genome = choices[0]
# #        trackName = choices[1].split(':')
# #        #outFn = open(NONSTANDARD_DATA_PATH+'/hg19/Private/Sigven/resultat.bed','w')
# #        randTrackClass = choices[2]
# #        analysisDef = ' RandTrackClass [randTrackClass=%s] -> RandomizedRawDataStat' % randTrackClass
# #        tnIntensity = choices[3].split(':') if choices[3] is not None else None
# #        for regSpec in  GenomeInfo.getChrList(genome):
# #            res = GalaxyInterface.runManual([trackName], analysisDef, regSpec, '*', genome, username=username, \
# #                                            printResults=False, printHtmlWarningMsgs=False, trackNameIntensity=tnIntensity)
# #
# #            from gold.origdata.TrackGenomeElementSource import TrackViewGenomeElementSource, TrackViewListGenomeElementSource
# #            from gold.origdata.BedComposer import BedComposer
# #            
# #            tvGeSource = TrackViewListGenomeElementSource(genome, [resDict['Result'] for resDict in res.values()], trackName)
# #            BedComposer(tvGeSource).composeToFile(galaxyFn)
# #                
# #        #print 'run with Stat=%s, took(secs): ' % analysisDef, time.time()-start
# #        
# #    @staticmethod
# #    def validateAndReturnErrors(choices):
# #        '''
# #        Should validate the selected input parameters. If the parameters are not valid,
# #        an error text explaining the problem should be returned. The GUI then shows this text
# #        to the user (if not empty) and greys out the execute button (even if the text is empty).
# #        If all parameters are valid, the method should return None, which enables the execute button.
# #        '''
# #        return None
# #    
# #    #@staticmethod
# #    #def isPublic():
# #    #    return False
# #    #
# #    #@staticmethod
# #    #def isRedirectTool():
# #    #    return False
# #    #
# #    #@staticmethod
# #    #def isHistoryTool():
# #    #    return True
# #    #
# #    #@staticmethod
# #    #def isDynamic():
# #    #    return True
# #    #
# #    #@staticmethod
# #    #def getResetBoxes():
# #    #    return [1]
# #    #
# #    #@staticmethod
# #    #def getToolDescription():
# #    #    return ''
# #    #
# #    #@staticmethod
# #    #def getToolIllustration():
# #    #    return None
# #    #
# #    #@staticmethod
# #    #def isDebugMode():
# #    #    return True
# #    #
# #    @staticmethod    
# #    def getOutputFormat(choices):
# #        return 'bed'
# #    


##################################################

from collections import OrderedDict

from gold.gsuite import GSuiteConstants
from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.application.GalaxyInterface import GalaxyInterface
from quick.multitrack.MultiTrackCommon import getGSuiteDataFromGalaxyTN
from quick.util.TrackReportCommon import STAT_OVERLAP_COUNT_BPS,\
    STAT_OVERLAP_RATIO, STAT_FACTOR_OBSERVED_VS_EXPECTED, processRawResults,\
    STAT_COVERAGE_RATIO_VS_REF_TRACK, STAT_COVERAGE_RATIO_VS_QUERY_TRACK,\
    STAT_LIST_INDEX, addColumnPlotToHtmlCore
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.mixin.UserBinMixin import UserBinMixin


# This is a template prototyping GUI that comes together with a corresponding
# web page.

class Tool4(GeneralGuiTool, UserBinMixin):
    GSUITE_FILE_OPTIONS_BOX_KEYS = ['gSuiteFirst', 'gSuiteSecond']

    GSUITE_ALLOWED_FILE_FORMATS = [GSuiteConstants.PREPROCESSED]
    GSUITE_ALLOWED_LOCATIONS = [GSuiteConstants.LOCAL]
    GSUITE_ALLOWED_TRACK_TYPES = [GSuiteConstants.SEGMENTS, GSuiteConstants.POINTS]
    
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Track collection vs track collection analysis"

    @classmethod
    def getInputBoxNames(cls):
        '''
        Specifies a list of headers for the input boxes, and implicitly also the
        number of input boxes to display on the page. The returned list can have
        two syntaxes:

            1) A list of strings denoting the headers for the input boxes in
               numerical order.
            2) A list of tuples of strings, where each tuple has
               two items: a header and a key.

        The contents of each input box must be defined by the function
        getOptionsBoxK, where K is either a number in the range of 1 to the
        number of boxes (case 1), or the specified key (case 2).

        Note: the key has to be camelCase (e.g. "firstKey")
        '''
        return [('Select first GSuite','gSuiteFirst'),
                ('Select second GSuite', 'gSuiteSecond'),
                ('Select statistic', 'statistic')
                ] + cls.getInputBoxNamesForUserBinSelection()

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
    def getOptionsBoxGSuiteFirst(): # Alternatively: getOptionsBox1()
        '''
        Defines the type and contents of the input box. User selections are
        returned to the tools in the prevChoices and choices attributes to other
        methods. These are lists of results, one for each input box (in the
        order specified by getInputBoxOrder()).

        The input box is defined according to the following syntax:

        Selection box:          ['choice1','choice2']
        - Returns: string

        Text area:              'textbox' | ('textbox',1) | ('textbox',1,False)
        - Tuple syntax: (contents, height (#lines) = 1, read only flag = False)
        - The contents is the default value shown inside the text area
        - Returns: string

        Password field:         '__password__'
        - Returns: string

        Genome selection box:   '__genome__'
        - Returns: string

        Track selection box:    '__track__'
        - Requires genome selection box.
        - Returns: colon-separated string denoting track name

        History selection box:  ('__history__',) | ('__history__', 'bed', 'wig')
        - Only history items of specified types are shown.
        - Returns: colon-separated string denoting galaxy track name, as
                   specified in ExternalTrackManager.py.

        History check box list: ('__multihistory__', ) | ('__multihistory__', 'bed', 'wig')
        - Only history items of specified types are shown.
        - Returns: OrderedDict with galaxy id as key and galaxy track name
                   as value if checked, else None.

        Hidden field:           ('__hidden__', 'Hidden value')
        - Returns: string

        Table:                  [['header1','header2'], ['cell1_1','cell1_2'], ['cell2_1','cell2_2']]
        - Returns: None

        Check box list:         OrderedDict([('key1', True), ('key2', False), ('key3', False)])
        - Returns: OrderedDict from key to selection status (bool).
        '''
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @staticmethod
    def getOptionsBoxGSuiteSecond(prevChoices): # Alternatively: getOptionsBox2()
        '''
        See getOptionsBoxFirstKey().

        prevChoices is a namedtuple of selections made by the user in the
        previous input boxes (that is, a namedtuple containing only one element
        in this case). The elements can accessed either by index, e.g.
        prevChoices[0] for the result of input box 1, or by key, e.g.
        prevChoices.key (case 2).
        '''
        return GeneralGuiTool.getHistorySelectionElement('gsuite')
    
    @staticmethod
    def getOptionsBoxStatistic(prevChoices):
        return [STAT_OVERLAP_COUNT_BPS, 
                STAT_OVERLAP_RATIO, 
                STAT_FACTOR_OBSERVED_VS_EXPECTED,
                STAT_COVERAGE_RATIO_VS_QUERY_TRACK,
                STAT_COVERAGE_RATIO_VS_REF_TRACK
                ]
    #@staticmethod
    #def getOptionsBox3(prevChoices):
    #    return ['']

    #@staticmethod
    #def getOptionsBox4(prevChoices):
    #    return ['']

    #@staticmethod
    #def getInfoForOptionsBoxKey(prevChoices):
    #    '''
    #    If not None, defines the string content of an clickable info box beside
    #    the corresponding input box. HTML is allowed.
    #    '''
    #    return None

    #@staticmethod
    #def getDemoSelections():
    #    return ['testChoice1','..']

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        '''
        Is called when execute-button is pushed by web-user. Should print
        output as HTML to standard out, which will be directed to a results page
        in Galaxy history. If getOutputFormat is anything else than HTML, the
        output should be written to the file with path galaxyFn. If needed,
        StaticFile can be used to get a path where additional files can be put
        (e.g. generated image files). choices is a list of selections made by
        web-user in each options box.
        '''
        from gold.application.LogSetup import setupDebugModeAndLogging
        setupDebugModeAndLogging()
        
        targetTrackNames, targetTrackCollection, targetTrackGenome = getGSuiteDataFromGalaxyTN(choices.gSuiteFirst)
        targetTracksDict = OrderedDict(zip(targetTrackNames, targetTrackCollection))
        refTrackNames, refTrackCollection, refTrackCollectionGenome = getGSuiteDataFromGalaxyTN(choices.gSuiteSecond)
        assert targetTrackGenome == refTrackCollectionGenome, 'Reference genome must be the same one in both GSuite files.'
        refTracksDict = OrderedDict(zip(refTrackNames, refTrackCollection))
        
        regSpec, binSpec = UserBinMixin.getRegsAndBinsSpec(choices)
        
        
        analysisDef = 'dummy -> RawOverlapStat'
        results = OrderedDict()
        for targetTrackName, targetTrack in targetTracksDict.iteritems():
            for refTrackName, refTrack in refTracksDict.iteritems():
                result = GalaxyInterface.runManual([targetTrack, refTrack], 
                                                   analysisDef, regSpec, binSpec, 
                                                   targetTrackGenome, galaxyFn, 
                                                   printRunDescription=False, 
                                                   printResults=False)
                if targetTrackName not in results :
                    results[targetTrackName] = OrderedDict()
                results[targetTrackName][refTrackName] = result.getGlobalResult()
                
        targetTrackTitles = results.keys()
            
        stat = choices.statistic
        statIndex = STAT_LIST_INDEX[stat]
        title = stat + ' analysis of track collections'    
        
        processedResults = []
        headerColumn = []
        for targetTrackName in targetTrackTitles:
            resultRowDict = processRawResults(results[targetTrackName])
            resultColumn = []
            headerColumn = []
            for refTrackName, statList in resultRowDict.iteritems():
                resultColumn.append(statList[statIndex])
                headerColumn.append(refTrackName)
            processedResults.append(resultColumn)

        transposedProcessedResults = [list(x) for x in zip(*processedResults)]
        
        tableHeader = ['Track names'] + targetTrackTitles
        htmlCore = HtmlCore()
        htmlCore.begin()
        htmlCore.header(title)
        htmlCore.divBegin('resultsDiv')
        htmlCore.tableHeader(tableHeader, sortable=True, tableId='resultsTable')
        for i, row in enumerate(transposedProcessedResults):
            line = [headerColumn[i]] + row
            htmlCore.tableLine(line)
        htmlCore.tableFooter()
        htmlCore.divEnd()
        
        addColumnPlotToHtmlCore(htmlCore, targetTrackNames, refTrackNames, stat, title + ' plot', processedResults, xAxisRotation = 315)
        
        htmlCore.hideToggle(styleClass='debug')
        htmlCore.end()
        
        print htmlCore
        
    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''
        return None

    #@staticmethod
    #def getSubToolClasses():
    #    '''
    #    Specifies a list of classes for subtools of the main tool. These
    #    subtools will be selectable from a selection box at the top of the page.
    #    The input boxes will change according to which subtool is selected.
    #    '''
    #    return None
    #
    #@staticmethod
    #def isPublic():
    #    '''
    #    Specifies whether the tool is accessible to all users. If False, the
    #    tool is only accessible to a restricted set of users as defined in
    #    LocalOSConfig.py.
    #    '''
    #    return False
    #
    #@staticmethod
    #def isRedirectTool():
    #    '''
    #    Specifies whether the tool should redirect to an URL when the Execute
    #    button is clicked.
    #    '''
    #    return False
    #
    #@staticmethod
    #def getRedirectURL(choices):
    #    '''
    #    This method is called to return an URL if the isRedirectTool method
    #    returns True.
    #    '''
    #    return ''
    #
    #@staticmethod
    #def isHistoryTool():
    #    '''
    #    Specifies if a History item should be created when the Execute button is
    #    clicked.
    #    '''
    #    return True
    #
    #@staticmethod
    #def isDynamic():
    #    '''
    #    Specifies whether changing the content of texboxes causes the page to
    #    reload.
    #    '''
    #    return True
    #
    #@staticmethod
    #def getResetBoxes():
    #    '''
    #    Specifies a list of input boxes which resets the subsequent stored
    #    choices previously made. The input boxes are specified by index
    #    (starting with 1) or by key.
    #    '''
    #    return []
    #
    #@staticmethod
    #def getToolDescription():
    #    '''
    #    Specifies a help text in HTML that is displayed below the tool.
    #    '''
    #    return ''
    #
    #@staticmethod
    #def getToolIllustration():
    #    '''
    #    Specifies an id used by StaticFile.py to reference an illustration file
    #    on disk. The id is a list of optional directory names followed by a file
    #    name. The base directory is STATIC_PATH as defined by Config.py. The
    #    full path is created from the base directory followed by the id.
    #    '''
    #    return None
    #
    #@staticmethod
    #def getFullExampleURL():
    #    return None
    #
    #@classmethod
    #def isBatchTool(cls):
    #    '''
    #    Specifies if this tool could be run from batch using the batch. The
    #    batch run line can be fetched from the info box at the bottom of the
    #    tool.
    #    '''
    #    return cls.isHistoryTool()
    #
    #@staticmethod
    #def isDebugMode():
    #    '''
    #    Specifies whether debug messages are printed.
    #    '''
    #    return False
    #
    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'customhtml'
