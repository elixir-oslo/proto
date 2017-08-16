from collections import OrderedDict
import math
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.util.GenomeInfo import GenomeInfo



class RP():
    def __init__(self, gsuite):
        self.gsuite = gsuite


    def sortChrDict(self):

        chr = GenomeInfo.getStdChrLengthDict(self.gsuite.genome)

        remeberString = []
        keysList = []
        for el in chr.keys():
            try:
                elC = int(el.replace('chr', ''))
                keysList.append(elC)
            except:
                remeberString.append(el.replace('chr', ''))

        sChr = sorted(keysList) + sorted(remeberString)

        chrDict = OrderedDict()
        chrLength = OrderedDict()
        val = 0
        for elChr in sChr:
            el = 'chr' + str(elChr)
            chrDict[el] = chr[el]
            chrLength[el] = val
            val += chr[el]

        return chrDict, chrLength


    def openBedFile(self, bedRegions):
        bedFile = ExternalTrackManager.extractFnFromGalaxyTN(bedRegions.split(':'))
        with open(bedFile, 'r') as f:
            lines = f.readlines()
        bedData = OrderedDict()
        for l in lines:
            l = l.strip('\n').split('\t')
            strL = l[0] + '-' + l[1] + '-' + l[2]
            if not strL in bedData.keys():
                bedData[strL] = []
        return bedData

    def countMutations(self, chrLength, bedData):
        dataDict = OrderedDict()
        dataDictLine = OrderedDict()

        elementOrder = []

        newDictRegions = OrderedDict()
        tracRegions = 0
        for trackN in self.gsuite.allTrackTitles():
            if not tracRegions in newDictRegions.keys():
                newDictRegions[tracRegions] = OrderedDict()
            for kit in bedData.keys():
                if not kit in newDictRegions[tracRegions].keys():
                    newDictRegions[tracRegions][kit] = []
            tracRegions += 1

        tracRegions = 0
        for track in self.gsuite.allTrackTitles():

            # count one track
            gSuiteTrack = self.gsuite.getTrackFromTitle(track)
            trackName = track

            dataDict[trackName] = OrderedDict()
            dataDictLine[trackName] = OrderedDict()

            # read from file
            newDict = {}
            with open(gSuiteTrack.path, 'r') as f:
                i = 0
                for x in f.readlines():
                    el = x.strip('\n').split('\t')
                    if len(el) >= 2:
                        try:
                            st = int(el[1])
                            if not el[0] in newDict:
                                newDict[el[0]] = []
                            newDict[el[0]].append([el[0], st, int(el[2])])
                        except:
                            pass
                i += 1

            # sort file according to start position
            newDict2 = OrderedDict()
            for key, it in chrLength.items():
                if key in newDict:
                    newDict2[key] = sorted(newDict[key], key=lambda x: x[1])

            for key, it in newDict2.items():
                if i == 0:
                    chr = key
                i = 0
                prevEnd = 0
                label = 0

                for el in it:

                    if len(el) >= 2:

                        if not int(el[1]) in dataDictLine[trackName]:
                            dataDictLine[trackName][int(el[1])] = 1
                        start = int(el[1])
                        if prevEnd != 0:
                            if not label in dataDict[trackName]:
                                dataDict[trackName][label] = OrderedDict()
                                dataDict[trackName][label]['val'] = 0
                                dataDict[trackName][label]['tot'] = 0

                            for elReg in newDictRegions[tracRegions].keys():

                                chrReg = elReg.split('-')[0]
                                startReg = elReg.split('-')[1]
                                endReg = elReg.split('-')[2]

                                if prevEnd > int(startReg) and start <= int(endReg) and chrReg == key:

                                    newDictRegions[tracRegions][elReg].append(start - prevEnd)
                                    break



                            if start - prevEnd != 0:
                                dataDict[trackName][label]['val'] += math.log(start - prevEnd, 10)
                            else:
                                dataDict[trackName][label]['val'] += start - prevEnd


                            dataDict[trackName][label]['tot'] += 1

                        label = int(el[1]) + int(chrLength[el[0]])

                        prevEnd = int(el[1])
                        i += 1

            elementOrder.append(i)

            tracRegions += 1

        listResCopy = []
        for key0, it0 in dataDict.iteritems():
            listResPart = []
            for key2 in sorted(it0):
                listResPart.append([key2, it0[key2]['val']])
            listResCopy.append(listResPart)

        elementOrder = sorted(range(len(elementOrder)), key=lambda k: elementOrder[k])

        return dataDict, dataDictLine, elementOrder, listResCopy, newDictRegions

    def getOptionsForPlot(self, elementOrder, tName):
        seriesType = []
        newSeriesNameRes = []
        newSeriesNameResOE = []
        yAxisMultiVal = []

        for el in elementOrder:
            newSeriesNameRes.append(tName[el])
            seriesType.append('scatter')
            yAxisMultiVal.append(0)
            newSeriesNameResOE.append(tName[el])

        for el in elementOrder:
            newSeriesNameRes.append(str(tName[el]) + '-- point')
            seriesType.append('line')
            yAxisMultiVal.append(1)
            newSeriesNameResOE.append(str(tName[el]) + '-- distribution')

        return seriesType, newSeriesNameRes, newSeriesNameResOE, yAxisMultiVal

    def countHist(self, newResList):

        poissonListMean = []
        if len(newResList) != 0:

            from proto.RSetup import r, robjects

            newResListLog = []
            for el in newResList:
                if el == 0:
                    newResListLog.append(0)
                else:
                    newResListLog.append(math.log(el, 10))

            # , breaks=ceiling(max(vec)) - floor((min(vec)))
            rCode = 'dataRPois <- function(vec) {' \
                    'hist(vec, prob=T)' \
                    '}'
            dd = robjects.FloatVector(newResListLog)
            dataFromRPois = r(rCode)(dd)

            breaks = list(dataFromRPois.rx2('breaks'))

            try:
                counts = list(dataFromRPois.rx2('density'))
            except:
                counts = [dataFromRPois.rx2('density')]

            for elN in range(0, len(counts)):
                br = (breaks[elN] + breaks[elN + 1]) / 2
                ct = counts[elN]

                poissonListMean.append([br, ct])

        return poissonListMean

    def countPoissonDistribution(self, numMut, intervalLen):

        poissonListMean = []

        if numMut != 0:

            from proto.RSetup import r, robjects
            # number of mutation/ length of interval
            rCode = 'dataRPois <- function(vec) {' \
                    'vecNew = log10(rexp(10000, vec[1]/vec[2])); ' \
                    'data=hist(vecNew, prob=T)' \
                    '}'
            dd = robjects.FloatVector(
                [numMut, intervalLen])
            dataFromRPois = r(rCode)(dd)

            breaks = list(dataFromRPois.rx2('breaks'))
            counts = list(dataFromRPois.rx2('density'))
            for elN in range(0, len(counts)):
                br = (breaks[elN] + breaks[elN + 1]) / 2
                ct = counts[elN]
                poissonListMean.append([br, ct])

        return poissonListMean

    def generateBinSizeList(self, elementOrder, listResCopy, listDataCountPerBin, newResBinSizeListSum):
        newResList = []
        newResBinSizeList = []
        for el in elementOrder:
            newResList.append(listResCopy[el])
            newResBinSizeList.append(listDataCountPerBin[el])

        newResBinSizeListSorted = OrderedDict(sorted(newResBinSizeListSum.items()))

        newResBinSizeListSortedList = []
        for key, value in newResBinSizeListSorted.iteritems():
            newResBinSizeListSortedList.append([key, value])

        return newResList, newResBinSizeList, newResBinSizeListSortedList
