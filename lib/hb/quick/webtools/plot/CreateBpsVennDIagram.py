import itertools
import json
from collections import OrderedDict
from collections import defaultdict
from string import ascii_uppercase
from urllib import unquote

from gold.application.LogSetup import logMessage
from gold.gsuite import GSuiteConstants
from quick.application.ProcTrackOptions import ProcTrackOptions
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.plot.VennHTML import htmlMal

'''
This tool takes individual tracks (also called categories) or a category track and calculates all the possible combinations of coverage (implicit across the genome).
The output is a html/javascript report where the usere can select the combination of categories and get the Venn-diagram (for 5 or less categories) or the coverage count.
From the report the usere can start another job (tool) and get the selected category-combination as regions in a file in history. Then the full algorithm are run again, but this could have been cashed from the first run ( not implemented).
Works now for up to 18 categories.
Speed is about 3 million regions per minute, (all categories combined).
Memory use was about 2GB for 9 million regions from 9 input files.
There is big room for cpu/memory improvements if needed.

'''

class CreateBpsVennDIagram(GeneralGuiTool):

    GSUITE_ALLOWED_FILE_FORMATS = [GSuiteConstants.PREPROCESSED]
    GSUITE_ALLOWED_LOCATIONS = [GSuiteConstants.LOCAL]
    GSUITE_ALLOWED_TRACK_TYPES = [GSuiteConstants.POINTS,
                                  GSuiteConstants.VALUED_POINTS,
                                  GSuiteConstants.SEGMENTS,
                                  GSuiteConstants.VALUED_SEGMENTS]
    GSUITE_DISALLOWED_GENOMES = [GSuiteConstants.UNKNOWN,
                                 GSuiteConstants.MULTIPLE]
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Generate a Venn diagram of overlap between tracks in a GSuite"

    @staticmethod
    def getInputBoxNames():
        return ['Select input source',
                'Select GSuite',
                'select genome',
                'Several bed files or ONE category.bed file',
                'Select track from history (optional)',
                'Select track source (optional)',
                'Select track source (optional)',
                'Select track source (optional)',
                'Select track source (optional)',
                'Select track source (optional)',
                'Select track source (optional)',
                'Select track source (optional)',
                'Select track source (optional)',
                'Select track source (optional)',
                'Select track source (optional)',
                'Select track source (optional)',
                'Select track source (optional)',
                'Select track source (optional)',
                'Select track source (optional)',
                'Select track source (optional)',
                'Select track source (optional)',
                'Select track source (optional)',
                'Select track source (optional)']
        # Alternatively: [ ('box1','1'), ('box2','2') ]
        # return ['select genome', 'Select track source (optional)','Select track', 'Select track source (optional)', 'Select track source (optional)', 'Select track source (optional)', 'Select track source (optional)', 'Select track source (optional)', 'Select track source (optional)', 'Select track source (optional)', 'Select track source (optional)', 'Select track source (optional)', 'Select track source (optional)', 'Select track source (optional)', 'Select track source (optional)'] #Alternatively: [ ('box1','1'), ('box2','2') ]

    # @staticmethod
    # def getInputBoxOrder():
    #    '''
    #    Specifies the order in which the input boxes should be displayed, as a
    #    list. The input boxes are specified by index (starting with 1) or by
    #    key. If None, the order of the input boxes is in the order specified by
    #    getInputBoxNames.
    #    '''
    #    return None

    @staticmethod
    def getOptionsBox1():  # Alternatively: getOptionsBoxKey()
        return ['From GSuite']

    @staticmethod
    def getOptionsBox2(prevChoices):  # Alternatively: getOptionsBoxKey()
        if prevChoices[0] == 'From GSuite':
            return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @staticmethod
    def getOptionsBox3(prevChoices):  # Alternatively: getOptionsBoxKey()
        if prevChoices[0] == 'From repository':
            return '__genome__'

    @staticmethod
    def getOptionsBox4(prevChoices):  # Alternatively: getOptionsBoxKey()
        if prevChoices[0] == 'From repository':
            return ['Several bed files', 'One category.bed file']

    @staticmethod
    def getOptionsBox5(prevChoices):
        if prevChoices[0] == 'From repository':
            if prevChoices[1] == 'Several bed files':
                return '__multihistory__', 'bed', 'category.bed', 'valued.bed', 'bedgraph', 'gtrack'
            else:
                return '__multihistory__', 'category.bed'

    @staticmethod
    def getOptionsBox6(prevChoices):
        if prevChoices[0] == 'From repository':
            return '__track__'

    @staticmethod
    def getOptionsBox7(prevChoices):  # Alternatively: getOptionsBoxKey()
        if prevChoices[0] == 'From repository':
            if prevChoices[-2] and ProcTrackOptions.isValidTrack(prevChoices[2],
            prevChoices[-2].split(':'), True) and prevChoices[3] == 'Several bed files':
                return '__track__'

    @staticmethod
    def getOptionsBox8(prevChoices):  # Alternatively: getOptionsBoxKey()
        if prevChoices[0] == 'From repository':
            if prevChoices[-2] and ProcTrackOptions.isValidTrack(prevChoices[2], prevChoices[-2].split(':'), True):
                return '__track__'

    @staticmethod
    def getOptionsBox9(prevChoices):  # Alternatively: getOptionsBoxKey()
        if prevChoices[0] == 'From repository':
            if prevChoices[-2] and ProcTrackOptions.isValidTrack(prevChoices[2], prevChoices[-2].split(':'), True):
                return '__track__'

    @staticmethod
    def getOptionsBox10(prevChoices):  # Alternatively: getOptionsBoxKey()
        if prevChoices[0] == 'From repository':
            if prevChoices[-2] and ProcTrackOptions.isValidTrack(prevChoices[2], prevChoices[-2].split(':'), True):
                return '__track__'

    @staticmethod
    def getOptionsBox11(prevChoices):  # Alternatively: getOptionsBoxKey()
        if prevChoices[0] == 'From repository':
            if prevChoices[-2] and ProcTrackOptions.isValidTrack(prevChoices[2], prevChoices[-2].split(':'), True):
                return '__track__'

    @staticmethod
    def getOptionsBox12(prevChoices):  # Alternatively: getOptionsBoxKey()
        if prevChoices[-2] and ProcTrackOptions.isValidTrack(prevChoices[2], prevChoices[-2].split(':'), True):
            return '__track__'

    @staticmethod
    def getOptionsBox13(prevChoices):  # Alternatively: getOptionsBoxKey()
        if prevChoices[0] == 'From repository':
            if prevChoices[-2] and ProcTrackOptions.isValidTrack(prevChoices[2], prevChoices[-2].split(':'), True):
                return '__track__'

    @staticmethod
    def getOptionsBox14(prevChoices):  # Alternatively: getOptionsBoxKey()
        if prevChoices[0] == 'From repository':
            if prevChoices[-2] and ProcTrackOptions.isValidTrack(prevChoices[2], prevChoices[-2].split(':'), True):
                return '__track__'

    @staticmethod
    def getOptionsBox15(prevChoices):  # Alternatively: getOptionsBoxKey()
        if prevChoices[0] == 'From repository':
            if prevChoices[-2] and ProcTrackOptions.isValidTrack(prevChoices[2], prevChoices[-2].split(':'), True):
                return '__track__'

    @staticmethod
    def getOptionsBox16(prevChoices):  # Alternatively: getOptionsBoxKey()
        if prevChoices[0] == 'From repository':
            if prevChoices[-2] and ProcTrackOptions.isValidTrack(prevChoices[2], prevChoices[-2].split(':'), True):
                return '__track__'

    @staticmethod
    def getOptionsBox17(prevChoices):  # Alternatively: getOptionsBoxKey()
        if prevChoices[-2] and ProcTrackOptions.isValidTrack(prevChoices[2], prevChoices[-2].split(':'), True):
            return '__track__'

    @staticmethod
    def getOptionsBox18(prevChoices):  # Alternatively: getOptionsBoxKey()
        if prevChoices[0] == 'From repository':
            if prevChoices[-2] and ProcTrackOptions.isValidTrack(prevChoices[2], prevChoices[-2].split(':'), True):
                return '__track__'

    @staticmethod
    def getOptionsBox19(prevChoices):  # Alternatively: getOptionsBoxKey()
        if prevChoices[-2] and ProcTrackOptions.isValidTrack(prevChoices[2], prevChoices[-2].split(':'), True):
            return '__track__'

    @staticmethod
    def getOptionsBox20(prevChoices):  # Alternatively: getOptionsBoxKey()
        if prevChoices[0] == 'From repository':
            if prevChoices[-2] and ProcTrackOptions.isValidTrack(prevChoices[2], prevChoices[-2].split(':'), True):
                return '__track__'

    @staticmethod
    def getOptionsBox21(prevChoices):  # Alternatively: getOptionsBoxKey()
        if prevChoices[0] == 'From repository':
            if prevChoices[-2] and ProcTrackOptions.isValidTrack(prevChoices[2], prevChoices[-2].split(':'), True):
                return '__track__'

    @staticmethod
    def getOptionsBox22(prevChoices):  # Alternatively: getOptionsBoxKey()
        if prevChoices[-2] and ProcTrackOptions.isValidTrack(prevChoices[2], prevChoices[-2].split(':'), True):
            return '__track__'

    @staticmethod
    def getOptionsBox23(prevChoices):  # Alternatively: getOptionsBoxKey()
        if prevChoices[0] == 'From repository':
            if prevChoices[-2] and ProcTrackOptions.isValidTrack(prevChoices[2], prevChoices[-2].split(':'), True):
                return '__track__'

    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''

        if choices[0] == 'From GSuite':
            if not choices[1]:
                return 'Please select a GSuite from history'

        if choices[0] == 'From GSuite':
            errorString = GeneralGuiTool._checkGSuiteFile(choices[1])
            if errorString:
                return errorString
            gSuite = getGSuiteFromGalaxyTN(choices[1])
            errorString = GeneralGuiTool._checkGSuiteTrackListSize(gSuite, minSize=2)
            if errorString:
                return errorString
            errorString = GeneralGuiTool._checkGSuiteRequirements \
                (gSuite,
                 CreateBpsVennDIagram.GSUITE_ALLOWED_FILE_FORMATS,
                 CreateBpsVennDIagram.GSUITE_ALLOWED_LOCATIONS,
                 CreateBpsVennDIagram.GSUITE_ALLOWED_TRACK_TYPES,
                 CreateBpsVennDIagram.GSUITE_DISALLOWED_GENOMES)
            if errorString:
                return errorString


        genome, trackNames = CreateBpsVennDIagram.getTrackNamesFromFormParameters(choices)
        ret = ''
        # ret += 'coiches='+str(choices) + '<br/>'
        # ret += 'genome='+genome+'<br/>'
        # ret += 'trackNames='+str(trackNames)+'<br/><br/>'

        if choices[3] != 'Several bed files' and choices[0] == 'From repository':
            if len(list(trackNames)) == 0:
                return ret + 'Need one category.bed file as input'
            if len(list(trackNames)) > 1:
                return ret + 'Need just one category.bed file as input'
            if len(list(trackNames)) > len(CreateBpsVennDIagram.getPrimeList()):
                return ret + 'To many files for tool, max number of files is ' + len(CreateBpsVennDIagram.getPrimeList())
        else:
            if len(list(trackNames)) < 2:
                return ret + 'Need at least two tracks (or bed files) as input'

#         if ret:
#             return ret
        return None


    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        print choices
        logMessage('CreateBpsVennDIagram choices input: ' + repr(choices))
        debugstring = 'i execute\n'

        genome, trackNames = CreateBpsVennDIagram.getTrackNamesFromFormParameters(choices)
        trackNameStrings = [ ':'.join(tn) for tn in trackNames]
        print trackNameStrings

        geSourceList, trackNamesWithoutPath = CreateBpsVennDIagram.getGeSourceList(genome, trackNames)

        # Make input similar, if it is many files or one category.bed file.
        # turn into a categoryBedLIst
        if len(trackNames) == 1:  # assume input is one category.bed file
            categoryBedList, categoryNames = CreateBpsVennDIagram.getCategoryBedList(geSourceList[0])
        else:
            categoryBedList = CreateBpsVennDIagram.collapseToCategoryBedList(geSourceList, trackNamesWithoutPath)
            categoryNames = trackNamesWithoutPath

        # print categoryBedList
        # return
        # make cat selection list, all are considerd in the from this tool. To be used in subsequent methoods that also can be called from other tools where this come into play.
        labelToPrime = CreateBpsVennDIagram.getPrimeList()
        counter = 0
        catInfo = OrderedDict()
        for c in categoryNames:
            thisTrackName = trackNameStrings[0]
            if len(trackNames) > 1:
                thisTrackName = trackNameStrings[counter]
            debugstring += str(thisTrackName) + '\n'
            catInfo[c] = {'label':labelToPrime.keys()[counter], 'prime':labelToPrime.values()[counter], 'selection':'in', 'fullTrackName':thisTrackName}
            # catInfo[c] = {'label':labelToPrime.keys()[counter], 'prime':labelToPrime.values()[counter], 'selection':'in', 'fullTrackName':thisTrackName}
            counter = counter + 1

        # collapse to startorstop and state lists
        posDict, catDict = CreateBpsVennDIagram.getPosCatDictsFromCategoryBedList(categoryBedList, catInfo)

        # iterate list and get stateBPCounter and stateRegions
        stateBPCounter, stateRegions, thisdebugstring = CreateBpsVennDIagram.getStateCount(posDict, catDict)

        debugstring += 'stateBPCounter: ' + str(stateBPCounter) + '\n'

        utfil = open(galaxyFn, 'w')
        utfil.write(CreateBpsVennDIagram.getHtmlString(catInfo, stateBPCounter, genome))
        utfil.close()
        # Turn the stateBPCounter into the object used by javascript

        '''
        setResult = []
        #numBedfiles = len(labelNames)
        labels = [ci['label'] for ci in catInfo.values()]
        #labels = labels[:len(labelNames)]
        htmlLabels = ["%s:'%s'" % (value['label'], key) for key, value in catInfo.items()]
        #htmllabelFullTrackName = ["%s:'%s'" % (v, labelFullTrackName[i]) for i, v in enumerate(labels)]
        #htmllabelFullTrackName = ["%s:'%s'" % (k, v) for k, v in zip(labels, labelFullTrackName)] # will be one entry if labelFullTrackName has just one element i.e category file.
        #htmllabelFullTrackName = OrderedDict([(k,v) for k,v in zip(labels, labelFullTrackName)])
        combList = []
        for v in range(1,len(catInfo)+1):
            combList += list(itertools.combinations(labels, v))
        labelToPrime={value['label']:value['prime'] for key, value in catInfo.items()}
        convertDict = dict([(v,reduce(lambda x, y: x*y,[labelToPrime[t] for t in v])) for v in combList])
        for item in combList:
            if all([v in labels for v in item]):
                primeVal = convertDict[item]
                strName = ''.join(list(item))
                setResult.append('%s: %i' % (strName, stateBPCounter[primeVal] if stateBPCounter.has_key(primeVal) else 0))

        utfil = open(galaxyFn, 'w')
        #print>>utfil, htmlMal % (', '.join(htmlLabels), ', '.join(setResult), ', '.join(htmllabelFullTrackName), ', '.join(htmllabelIsHistoryElement), debugstring) # siste kan vere debugstring
        genomeparameter = genome
        if genomeparameter == '':
            genomeparameter= 'NOT_SET'
        print>>utfil, htmlMal % (', '.join(htmlLabels), ', '.join(setResult), json.dumps(catInfo), genomeparameter, '') # siste kan vere debugstring
        utfil.close()
        '''

    @classmethod
    def getHtmlString(cls, catInfo, stateBPCounter, genome):
        setResult = []
        labels = [ci['label'] for ci in catInfo.values()]
        # labels = labels[:len(labelNames)]
        htmlLabels = ["%s:'%s'" % (value['label'], key) for key, value in catInfo.items()]
        # htmllabelFullTrackName = ["%s:'%s'" % (v, labelFullTrackName[i]) for i, v in enumerate(labels)]
        # htmllabelFullTrackName = ["%s:'%s'" % (k, v) for k, v in zip(labels, labelFullTrackName)] # will be one entry if labelFullTrackName has just one element i.e category file.
        # htmllabelFullTrackName = OrderedDict([(k,v) for k,v in zip(labels, labelFullTrackName)])
        combList = []
        for v in range(1, len(catInfo) + 1):
            combList += list(itertools.combinations(labels, v))
        labelToPrime = {value['label']:value['prime'] for key, value in catInfo.items()}
        convertDict = dict([(v, reduce(lambda x, y: x * y, [labelToPrime[t] for t in v])) for v in combList])
        for item in combList:
            if all([v in labels for v in item]):
                primeVal = convertDict[item]
                strName = ''.join(list(item))
                setResult.append('%s: %i' % (strName, stateBPCounter[primeVal] if stateBPCounter.has_key(primeVal) else 0))

        genomeparameter = genome
        if genomeparameter == '':
            genomeparameter = 'NOT_SET'
        return htmlMal % (', '.join(htmlLabels), ', '.join(setResult), json.dumps(catInfo), genomeparameter, '')  # siste kan vere debugstring



    # returna a ordereddict with the 20 first primenumbers with 20 first letters as keys; 'A':2, 'B':3 .....
    @classmethod
    def getPrimeList(cls):
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71]  # supports 20 categories
        return OrderedDict([(k, v) for k, v in zip(ascii_uppercase, primes)])
    # extracts the genomename and tracknames (in list format) from the parameters
    @classmethod
    def getTrackNamesFromFormParameters(cls, choices):
        if choices[0] == 'From repository':
            genome = choices[2]
            trackNames = [unquote(val).split(':') for val in choices[4].values() if val]
            trackNames += [v.split(':')for v in choices[5:] if v and
                           ProcTrackOptions.isValidTrack(genome, v.split(':'), True)  ]
            return genome, trackNames
        else: #if 'From GSuite'
            gSuite = getGSuiteFromGalaxyTN(choices[1])
            tracks = [gSuiteTrack.trackName for gSuiteTrack in gSuite.allTracks()]
            genome = gSuite.genome
            return genome, tracks


    # The main algorithm for the tool.
    # posDict a dict wtih chr as keys and a list ov breakpoints (start and stop og regions) as value.
    # catDict similar to posDict but has a list of primevalues that act as unique keys for each category. Positive value means startpoint, a minus value means endpoint.
    # The lists get sorted first and then traversed, while keeping count of the state, i.e which categories that are currently 'in'
    # stateBPCounter, a dict where key is the state (categories included as a product of primes) and value is the base pair coverage count for that particular state.
    # stateRegions, a dict where chr is the key and state is the value.
    @classmethod
    def getStateCount(cls, posDict, catDict):
        stateBPCounter = defaultdict(int)
        stateRegions = defaultdict(list)
        debugstring = 'i getStateCount'
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
                # trackFile.write('pos, primeVal: ' + str(pos)+' '+str( primeVal)+ '\n')
                # trackFile.write('resultCounter: ' + str( resultCounter )+ '\n')
                if currentPos != pos:
                    stateRegions[chrom].append((currentPos, pos, abs(currentState)))
                    stateBPCounter[abs(currentState)] += pos - currentPos
                    # debugstring +='resultCounter='+str(resultCounter)+ ' currentPos='+ str(currentPos) + '    pos='+str(pos)+ '   chrom='+str(chrom)+  '   primeVal='+str(primeVal)+ '    catCoverageDepth='+str(catCoverageDepth) +'<br/>'
                    # print 'resultCounter,currentState,  pos and currentPos',abs(currentState),':',  pos, currentPos
                    currentPos = pos

                if primeVal < 0:
                    catCoverageDepth[abs(primeVal)] -= 1
                    if catCoverageDepth[abs(primeVal)] == 0:
                        currentState /= primeVal
                else:
                    catCoverageDepth[primeVal] += 1
                    if catCoverageDepth[primeVal] == 1:
                        currentState *= primeVal
        return stateBPCounter, stateRegions, debugstring

    # categoryBedList a dict where chr is key and value is a list of regions (start, end, category). i.e similar to a category.bed file.
    # catInfo, a dict where categoory is key and value is another dict of selections for that category. In this function regions from categories with 'selection' set to 'ignore' are not included. The prime to be used for each category is also given here.
    # posDict a dict wtih chr as keys and a list ov breakpoints (start and stop og regions) as value.
    # catDict similar to posDict but has a list of primevalues that act as unique keys for each category. Positive value means startpoint, a minus value means endpoint.
    @classmethod
    def getPosCatDictsFromCategoryBedList(cls, categoryBedList, catInfo):
        posDict = defaultdict(list)
        catDict = defaultdict(list)
        for key, val in categoryBedList.items():
            for line in val:
                thisCatInfo = catInfo[line[2]]
                if thisCatInfo['selection'] != 'ignore':
                    primeNum = thisCatInfo['prime']
                    posDict[key] += [ line[0], line[1] ]
                    catDict[key] += [primeNum, -primeNum]
        return posDict, catDict

    # Small helper method that makes a category.bed-like object from many bed-files so it can later be handled as it was a category.bed file.
    # geSourceList several bed files or similar.
    # trackNames, names to be used as categories. must be the same length as geSourceList
    @classmethod
    def collapseToCategoryBedList(cls, geSourceList, trackNames):
        ret = defaultdict(list)
        for geSource, trackName in zip(geSourceList, trackNames):
            for ge in geSource:
                ret[ge.chr].append((ge.start, ge.end, trackName))
        return ret

    # Small helper method to make a category.bed file into a fairly similar object in memory, so it later can be handled in the same manner as a similar object made from multiple bed files (in collapseToCategoryBedList).
    @classmethod
    def getCategoryBedList(cls, geSource):
        ret = defaultdict(list)
        catNames = set()
        for ge in geSource:
            catNames.add(ge.val)
            ret[ge.chr].append((ge.start, ge.end, ge.val))
        return ret, catNames

    # geSourceList several bed files or similar (or just one if input is a category.bed).
    # trackNamesWithoutPath, list of tracknames smilar to tracks except for history tracks that only uses the last (and informative) part.
    @classmethod
    def getGeSourceList(cls, genome, tracks):
        from quick.application.ExternalTrackManager import ExternalTrackManager
        from gold.origdata.BedGenomeElementSource import BedGenomeElementSource, BedCategoryGenomeElementSource
        from gold.origdata.GtrackGenomeElementSource import GtrackGenomeElementSource
        from gold.origdata.TrackGenomeElementSource import FullTrackGenomeElementSource
        geSourceList = []
        trackNamesWithoutPath = []
        for track in tracks:
            try:
                fileType = ExternalTrackManager.extractFileSuffixFromGalaxyTN(track)
                fn = ExternalTrackManager.extractFnFromGalaxyTN(track)
                if fileType == 'category.bed':
                    geSourceList.append(BedCategoryGenomeElementSource(fn))
                elif fileType == 'gtrack':
                    geSourceList.append(GtrackGenomeElementSource(fn))
                else:
                    geSourceList.append(BedGenomeElementSource(fn))
                trackNamesWithoutPath.append(ExternalTrackManager.extractNameFromHistoryTN(track))
            except:  # it is not a history, must be in HB track repository
                geSourceList.append(FullTrackGenomeElementSource(genome, track, allowOverlaps=True))
                trackNamesWithoutPath.append(':'.join(track))
        return geSourceList, trackNamesWithoutPath


    # @classmethod
    # def getTests(cls):
    #    choicesFormType = ['genome', 'str', 'dict'] + ['track']*18
    #    testRunList = ["$Tool[hb_create_bps_venn_d_iagram]('hg18'|'Severalbedfiles'|OrderedDict()|'Sample data:Track types:Segments'|'Sample data:Track types:Valued segments (category)'|'Sample data:Track types:Valued segments (number)'|''|None|None|None|None|None|None|None|None|None|None|None|None|None|None)"]
    #    return cls.formatTests(choicesFormType, testRunList)
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

    @staticmethod
    def isPublic():
        return True

    @classmethod
    def getToolDescription(cls):
        '''
        Specifies a help text in HTML that is displayed below the tool.
        '''
        from proto.hyperbrowser.HtmlCore import HtmlCore
        core = HtmlCore()
        core.paragraph('Calculates the base pair overlaps between all combinations of tracks specified '
                       'in the input GSuite file. In the resulting output page, up to 5 '
                       'tracks can be selected for inclusiion in a Venn diagram of base pair overlaps.')

        cls._addGSuiteFileDescription(core,
                                      allowedLocations=cls.GSUITE_ALLOWED_LOCATIONS,
                                      allowedFileFormats=cls.GSUITE_ALLOWED_FILE_FORMATS,
                                      allowedTrackTypes=cls.GSUITE_ALLOWED_TRACK_TYPES,
                                      disallowedGenomes=cls.GSUITE_DISALLOWED_GENOMES)

        return str(core)

    # @staticmethod
    # def getFullExampleURL():
    #     return 'u/hb-superuser/p/use-case---overlap-of-snp-platforms'
