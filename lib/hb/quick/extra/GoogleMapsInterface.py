import ast
import os
from string import capwords
from urllib import quote

import third_party.safeshelve as safeshelve
from config.Config import STATIC_PATH, STATIC_REL_PATH, URL_PREFIX
from quick.application.GalaxyInterface import GalaxyInterface

BASE_DIR = STATIC_PATH + '/maps'
BASE_URL = STATIC_REL_PATH + '/maps'

class Map:
    def __init__(self, name):
        self._name = name

    def __cmp__(self, other):
        return cmp(self.getPrettyName(), other.getPrettyName())

    def getName(self):
        return self._name

    def getPrettyName(self):
        titleFn = '/'.join([BASE_DIR, self._name, 'data', 'Title.txt'])
        if os.path.exists(titleFn):
            return open(titleFn).read().strip()
#        return capwords(self._name.replace('_', ' '))
        return capwords(self._name)

    def getUrl(self):
        return BASE_URL + '/' + self._name

    def getRunDescriptionUrl(self):
        return os.sep.join([BASE_URL, self._name, 'data', 'Run_description.html'])

    def getCountUrl(self):
        return os.sep.join([BASE_URL, self._name, 'data', 'Result_counts_table.html'])

    def getEffectSizeUrl(self):
        return os.sep.join([BASE_URL, self._name, 'data', 'Result_table.html'])

    def getPvalUrl(self):
        return os.sep.join([BASE_URL, self._name, 'data', 'Result_pval_table.html'])

    def getSavedCookies(self, fname = 'common'):
        name = self._name
        if name.isdigit():
            from quick.util.CommonFunctions import getGalaxyFnFromDatasetId
            from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
            galaxyFn = getGalaxyFnFromDatasetId( int(name) )
            outDir = GalaxyRunSpecificFile([], galaxyFn).getDiskPath()
        else:
            outDir = '/'.join([BASE_DIR, name])
        r = {}
        sname = outDir + '/cookies/' + fname + '.shelve'
        if os.path.exists(sname):
            s = safeshelve.open(sname, 'r')
            for x in s.keys():
                r[x] = s[x]
            s.close()
        return r

    @staticmethod
    def getMaps():
        maps = []
        for dir in os.listdir(BASE_DIR):
            if os.path.isdir(BASE_DIR + '/' + dir) and dir not in ['common', 'old']:
                maps.append(Map(dir))
        maps.sort()
        return maps


class MarkInfo:
    def __init__(self, name, colIdx, rowIdx, mapId):
        self._colIdx = colIdx
        self._rowIdx = rowIdx
        self._mapId = mapId
        self._mapName = name
        self._genome = self._findGenome(name)

        self._commonDir = '/'.join([BASE_DIR, 'common', mapId])
        self._resultDir = '/'.join([BASE_DIR, name, 'data'])

        self._openShelves = {}

    def _findGenome(self, name):
        genomeFn = os.sep.join([BASE_DIR, name, 'data', 'Genome.txt'])
        if os.path.exists(genomeFn):
            return open(genomeFn).read().strip()

        return 'hg18'

    def _openShelf(self, shelfFn, mode):
        if shelfFn not in self._openShelves:
            if not os.path.exists(shelfFn):
                raise OSError('Shelf file not found: %s' % shelfFn)
            self._openShelves[shelfFn] = safeshelve.open(shelfFn, mode)
        return self._openShelves[shelfFn]

#        if os.path.exists('/'.join([self._resultDir, 'Result_table.shelve'])):
#            self._valueDict = safeshelve.open('/'.join([self._resultDir, 'Result_table.shelve']), 'r')
#        else:
#            self._valueDict = safeshelve.open('/'.join([self._resultDir, 'Result_table.shelve']), 'c')
#            self._loadResultFileToShelve('/'.join([self._resultDir, 'Result_table.txt']))
#            self._valueDict.sync()

#    def setMark(self, colIdx, rowIdx):
#        self.colIdx = colIdx
#        self.rowIdx = rowIdx
    #
    #def _loadResultFileToShelve(self, filename):
    #    table = self._valueDict
    #    f = open(filename)
    #    idx = 0
    #    for line in f:
    #        if line.find('\t') >= 0:
    #            cols = line.strip().split('\t')
    #            self._valueDict[str(idx)] = cols
    #            idx += 1
    #    return table
    #
    def close(self):
        for shelf in self._openShelves.values():
            shelf.close()
        self._openShelves = {}
#        self.dict.close()
#        self.mesh.close()

    def _toStr(self, val):
        if val is None:
            return ''
        if type(val) in [list, tuple]:
            if (len(val) > 0) and (type(val[0]) in [list, tuple]):
                return '<br>'.join(['\t'.join(x) for x in val])
            else:
                return ', '.join(val)
        return str(val)

    def _singular(self, s):
        if s.endswith('s'):
            return s[:-1]
        elif s.endswith('loci'):
            return s[:-4] + 'locus'
        return s

    def _getValFromShelf(self, shelfFn, floatVal=False, toStr=False):
        if not os.path.exists(shelfFn):
            return ''

        resultsShelf = self._openShelf(shelfFn, 'r')
        ret = resultsShelf.get(repr((self._rowIdx, self._colIdx)))
        if toStr:
            if ret is None:
                return ''
            if floatVal:
                ret = '%.3g' % ret
            return str(ret)
        return ret

    def validMapId(self):
        return os.path.exists(self._commonDir)

    def getValue(self, toStr=False):
#        return self._valueDict[str(self._rowIdx)][self._colIdx]
        return self._getValFromShelf('/'.join([self._resultDir, 'Result_table.shelf']), floatVal=True, toStr=toStr)

    def getCount(self, toStr=False):
        return self._getValFromShelf('/'.join([self._resultDir, 'Result_counts_table.shelf']), toStr=toStr)

    def getPval(self, toStr=False):
        return self._getValFromShelf('/'.join([self._resultDir, 'Result_pval_table.shelf']), floatVal=True, toStr=toStr)

    def getSignificance(self, toStr=False):
        ret = self._getValFromShelf('/'.join([self._resultDir, 'Result_significance_table.shelf']), toStr=toStr)
        return 'Significant' if ret == 'True' else 'Not significant'

    def _convertNameToCorrectCase(self, name, lowerCaseName2NameShelf):
        if name in lowerCaseName2NameShelf:
            return self._toStr( lowerCaseName2NameShelf[name] )
        return name

    def _cleanUpName(self, name, lowerCase, removeParenthesis):
        if removeParenthesis:
            parStart = name.find('(')
            parEnd = name.find(')')
            if parStart != -1 and parEnd != -1 and parStart < parEnd:
                name = name[:parStart] + name[parEnd+1:]
        if len(name)>0 and name[1] == '$' and not lowerCase:
            name = name.upper().replace(' ','_') # Temporary hack for TFs
        return name

    def _getNameFromPos(self, pos2NameShelfFn, pos, lowerCaseName2NameShelfFn=None, removeParenthesis=False):
        pos2NameShelf = self._openShelf('/'.join([self._resultDir, pos2NameShelfFn]), 'r')
        name = self._toStr( pos2NameShelf.get(repr(pos)) )
        lowerCase = (lowerCaseName2NameShelfFn is None)
        if not lowerCase:
            lowerCaseName2NameShelf = self._openShelf('/'.join([self._commonDir, lowerCaseName2NameShelfFn]), 'r')
            name = self._convertNameToCorrectCase(name, lowerCaseName2NameShelf)
        return self._cleanUpName(name, lowerCase, removeParenthesis)

    def getRowName(self, lowerCase=True, removeParenthesis=False):
#        return self._valueDict[str(self._rowIdx)][0]
        return self._getNameFromPos('rowPos2Name.shelf', self._rowIdx, \
                                    ('rowLowerCaseName2Name.shelf' if not lowerCase else None), removeParenthesis)

    def getColName(self, lowerCase=True, removeParenthesis=False):
#        return self._valueDict['0'][self._colIdx - 1]
        return self._getNameFromPos('colPos2Name.shelf', self._colIdx, \
                                    ('colLowerCaseName2Name.shelf' if not lowerCase else None), removeParenthesis)

    def getRowElCount(self):
        pos2ElCount = self._openShelf('/'.join([self._resultDir, 'rowPos2ElCount.shelf']), 'r')
        return self._toStr( pos2ElCount.get(repr(self._rowIdx)) )

    def getColElCount(self):
        pos2ElCount = self._openShelf('/'.join([self._resultDir, 'colPos2ElCount.shelf']), 'r')
        return self._toStr( pos2ElCount.get(repr(self._colIdx)) )

    def _getIndexesFromName(self, query, name2PosShelfFn, pos2NameShelfFn, lowerCaseName2NameShelfFn, extraLowerCaseName2NameShelfFn):
        name2PosShelf = self._openShelf('/'.join([self._resultDir, name2PosShelfFn]), 'r')
        pos2NameShelf = self._openShelf('/'.join([self._resultDir, pos2NameShelfFn]), 'r')

        lowerCaseName2NameShelf = self._openShelf('/'.join([self._commonDir, lowerCaseName2NameShelfFn]), 'r')
        extraLowerCaseName2NameShelfFn = '/'.join([self._commonDir, extraLowerCaseName2NameShelfFn])
        if os.path.exists(extraLowerCaseName2NameShelfFn):
            extraLowerCaseName2NameShelf = self._openShelf(extraLowerCaseName2NameShelfFn, 'r')
        else:
            extraLowerCaseName2NameShelf = None

        names = name2PosShelf.keys()
        nameHits = [name for name in names if query.lower() in name]
        hits = []

        for name in nameHits:
            for pos in name2PosShelf[name]:
                hits.append([name, pos])

        for i, hit in enumerate(hits):
            if extraLowerCaseName2NameShelf is not None and hit[0] in extraLowerCaseName2NameShelf:
                hits[i][0] = extraLowerCaseName2NameShelf[hit[0]] + ' (' + \
                    self._convertNameToCorrectCase(pos2NameShelf[hit[1]], lowerCaseName2NameShelf) + ')'
            else:
                hits[i][0] = self._convertNameToCorrectCase(hit[0], lowerCaseName2NameShelf)

        hits = [ast.literal_eval(x) for x in set([repr(x) for x in hits])]
        return sorted(hits, key=lambda x:[ int(x[1]), x[0] ])

    def getIndexesFromRowName(self, query):
        return self._getIndexesFromName(query, 'rowName2Pos.shelf', 'rowPos2Name.shelf', \
                                        'rowLowerCaseName2Name.shelf', 'extraRowLowerCaseName2Name.shelf')

    def getIndexesFromColName(self, query):
        return self._getIndexesFromName(query, 'colName2Pos.shelf', 'colPos2Name.shelf', \
                                        'colLowerCaseName2Name.shelf', 'extraColLowerCaseName2Name.shelf')

#    def getCleanColumnName(self):
#        return re.sub(r'^[0-9]+\. ([^\(]+).*', r'\1', capwords(self.getColName()).strip()).strip()
#
#    def getCleanRowName(self):
#        return re.sub(r'^[0-9]+\. ([^\(]+).*', r'\1', self.getRowName().strip()).strip()
#

    def _getGeneListFromShelf(self, geneListShelf):
        colName = self.getColName(lowerCase=True)
        rowName = self.getRowName(lowerCase=True)
        try:
            geneList = geneListShelf[repr((rowName, colName))]
        except:
            geneList = geneListShelf[repr((rowName.replace(' ','_'), colName))]
        #try: #Temporarily
        #    geneList = geneListShelf[repr((rowName.replace(' ','_').lower(), colName.lower()))]
        #except:
        #    geneList = geneListShelf[repr((rowName.replace(' ','_').lower(), colName))]
        return geneList

    def getGeneList(self, filter='all'):
        assert filter in ['all', 'hits', 'nohits']
#        colName = self.getColName(lowerCase=True)
#        rowName = self.getRowName(lowerCase=True)
        rowAndCol2rankedGeneList = self._openShelf('/'.join([self._commonDir, 'rowAndCol2rankedGeneList.shelf']), 'r')
        geneList = self._getGeneListFromShelf(rowAndCol2rankedGeneList)

        if geneList is None:
            return ''

        if filter == 'hits':
            geneList = [x for x in geneList if x[1] > 0]
        elif filter == 'nohits':
            geneList = [x for x in geneList if x[1] == 0]

        return sorted(geneList, key=lambda x:[x[y] for y in [1,0]], reverse=True)

    def getGeneListAsStr(self, filter='all'):
        geneList = self.getGeneList(filter)
        #return self._toStr( ['%s %d (%.2f)' % x for x in geneList] )
        return self._toStr( ['<a style="text-decoration:none;color:#006" target="_blank" href="http://www.ncbi.nlm.nih.gov/omim/?term=%s">%s %d (%.2f)</a>' \
                             % (x[:1] + x) for x in geneList] )

    def getTfbsPrettyNames(self):
        rowName = self.getRowName(lowerCase=True)
        pwmName2PrettyNames = self._openShelf('/'.join([self._commonDir, 'pwmName2PrettyNames.shelf']), 'r')
        return self._toStr( pwmName2PrettyNames.get(rowName) )

    def getTfNames(self):
        rowName = self.getRowName(lowerCase=True)
        pwmName2TfNames = self._openShelf('/'.join([self._commonDir, 'pwmName2TfNames.shelf']), 'r')
        return self._toStr( pwmName2TfNames.get(rowName) )

    def getTfClasses(self):
        rowName = self.getRowName(lowerCase=True)
        pwmName2TfClasses = self._openShelf('/'.join([self._commonDir, 'pwmName2TfClasses.shelf']), 'r')
        return self._toStr( pwmName2TfClasses.get(rowName) )

    def getDiseaseParents(self, toStr=False):
        colName = self.getColName(lowerCase=True, removeParenthesis=True)
        parentShelf = self._openShelf('/'.join([self._commonDir, 'meshChildToAllParentsMergedOnlyDiseasesRanked.shelve']), 'r')
        parents = [p[1] for p in parentShelf[colName]] if colName in parentShelf else []

        if toStr:
            if parents is not []:
                return ' | '.join(parents)
            return '\'' + colName + '\''
        else:
            return parents

    def getColAndRowNames(self, cols, rows, lowerCase=True, removeParenthesis=False):
        colNames = []
        rowNames = []
        for col in cols:
            self._colIdx = col
            colNames.append(self.getColName(lowerCase=lowerCase, removeParenthesis=removeParenthesis))

        for row in rows:
            self._rowIdx = row
            rowNames.append(self.getRowName(lowerCase=lowerCase, removeParenthesis=removeParenthesis))

        return colNames, rowNames

    def getGeneListOfRegulomeCluster(self, cols, rows, colNames, rowNames, colTitle, rowTitle, hitText):
        geneListShelfFn = '/'.join([self._commonDir, 'rowAndCol2rankedGeneList.shelf'])
        #return GalaxyInterface._getGeneListOfRegulomeCluster(colNames, rowNames, shelfFn, colTitle, rowTitle, hitText)

        #print '<pre>'
        #print 'Getting gene lists with diseases ',diseases, ' and tfs ',tfs
        #print '#diseases: ',len(diseases), ' and #tfs: ',len(tfs)
        #colNames, rowNames = self.getColAndRowNames(cols, rows, lowerCase=False)
        colTuples = zip(cols, colNames)
        rowTuples = zip(rows, rowNames)

        allTfNames = set([])
        gene2hitCount = {}
        gene2colNameSet = {}
        gene2rowNameSet = {}
        rowName2sumOfScores = {}
        rowName2hitCount = {}
        rowName2geneSet = {}
        rowName2colNameSet = {}
        rowName2totalHitCount = {}
        colName2sumOfScores = {}
        colName2hitCount = {}
        colName2geneSet = {}
        colName2rowNameSet = {}
        colName2totalGeneCount = {}
        allDiseaseGroups2sumOfScores = {}

        geneListShelf = self._openShelf(geneListShelfFn,'r')
        for col, colName in colTuples:
            self._colIdx = col

            colName2sumOfScores[colName] = 0
            colName2hitCount[colName] = 0
            colName2geneSet[colName] = set([])
            colName2rowNameSet[colName] = set([])
            colName2totalGeneCount[colName] = self.getColElCount()

            try:
                diseaseGroups = self.getDiseaseParents() + [colName]
            except OSError:
                diseaseGroups = None

            for row, rowName in rowTuples:
                self._rowIdx = row

                if rowName not in rowName2hitCount:
                    rowName2sumOfScores[rowName] = 0
                    rowName2hitCount[rowName] = 0
                    rowName2geneSet[rowName] = set([])
                    rowName2colNameSet[rowName] = set([])
                    rowName2totalHitCount[rowName] = self.getRowElCount()

                    try:
                        tfNames = self.getTfNames().split(', ')
                        allTfNames.update(tfNames)
                    except OSError:
                        continue

                if rowName == '' or colName == '':
                    continue

                geneList = self._getGeneListFromShelf(geneListShelf)

                score = self.getValue()
                if score is not None:
                    colName2sumOfScores[colName] += score
                    rowName2sumOfScores[rowName] += score

                if diseaseGroups is not None:
                    for diseaseGroup in diseaseGroups:
                        if diseaseGroup not in allDiseaseGroups2sumOfScores:
                            allDiseaseGroups2sumOfScores[diseaseGroup] = 0
                        allDiseaseGroups2sumOfScores[diseaseGroup] += score

                for geneTriplet in geneList:
                    gene = geneTriplet[0]
                    count = geneTriplet[1]
                    if count==0:
                        continue

                    if not gene in gene2hitCount:
                        gene2hitCount[gene] = 0
                        gene2colNameSet[gene] = set([])
                        gene2rowNameSet[gene] = set([])

                    gene2hitCount[gene] += count
                    gene2colNameSet[gene].add(colName)
                    gene2rowNameSet[gene].add(rowName)

                    rowName2hitCount[rowName] += count
                    rowName2geneSet[rowName].add(gene)
                    rowName2colNameSet[rowName].add(colName)

                    colName2hitCount[colName] += count
                    colName2geneSet[colName].add(gene)
                    colName2rowNameSet[colName].add(rowName)

        sortedTfNames = sorted([x for x in allTfNames if x != ''])
        sortedGenesAndHitCounts = list(reversed( sorted(gene2hitCount.items(), key=lambda t:(t[1],t[0]) )))
        rankedGenes = [x[0] for x in sortedGenesAndHitCounts]
        rankedColNames = [x[1] for x in reversed(sorted([(colName2sumOfScores[colName], colName) for colName in colNames]))]
        rankedRowNames = [x[1] for x in reversed(sorted([(rowName2sumOfScores[rowName], rowName) for rowName in rowNames]))]
        sortedDiseaseGroupsAndSumOfScores = list(reversed(sorted( allDiseaseGroups2sumOfScores.items(), key=lambda t:(t[1],t[0]) )))

        sortedTfNamesOut = ', '.join(sortedTfNames)
        rankedGenesOut = ', '.join(rankedGenes)
        gene2hitCountsOut = ', '.join([str(x[1]) for x in sortedGenesAndHitCounts])
        gene2colNameAssocOut = ', '.join([str(len(gene2colNameSet[g])) for g in rankedGenes])
        gene2rowNameAssocOut = ', '.join([str(len(gene2rowNameSet[g])) for g in rankedGenes])

        rankedColNamesOut = ' | '.join(rankedColNames)
        colName2meanOfScoresOut = ', '.join(['%.2f' % (1.0*colName2sumOfScores[colName]/len(rowNames)) for colName in rankedColNames])
        colName2totalGeneCountOut = ', '.join([colName2totalGeneCount[colName] for colName in rankedColNames])
        colName2geneAssocOut = ', '.join([str(len(colName2geneSet[colName])) for colName in rankedColNames])
        colName2rowNameAssocOut = ', '.join([str(len(colName2rowNameSet[colName])) for colName in rankedColNames])
        colName2hitCountOut = ', '.join([str(colName2hitCount[colName]) for colName in rankedColNames])

        rankedRowNamesOut = ', '.join(rankedRowNames)
        rowName2meanOfScoresOut = ', '.join(['%.2f' % (1.0*rowName2sumOfScores[rowName]/len(colNames)) for rowName in rankedRowNames])
        rowName2totalHitCountOut = ', '.join([rowName2totalHitCount[rowName] for rowName in rankedRowNames])
        rowName2geneAssocOut = ', '.join([str(len(rowName2geneSet[rowName])) for rowName in rankedRowNames])
        rowName2colNameAssocOut = ', '.join([str(len(rowName2colNameSet[rowName])) for rowName in rankedRowNames])
        rowName2hitCountOut = ', '.join([str(rowName2hitCount[rowName]) for rowName in rankedRowNames])

        rankedDiseaseGroupsOut = ' | '.join([x[0] for x in sortedDiseaseGroupsAndSumOfScores])
        diseaseGroup2sumOfScoresOut = ', '.join(['%.2f' % x[1] for x in sortedDiseaseGroupsAndSumOfScores])
        addDiseaseGroups = (len(sortedDiseaseGroupsAndSumOfScores) > 0)

        headerLines = (['All related TFs:'] if sortedTfNamesOut != '' else []) +\
                      ['Ranked gene list:', \
                       'Corresponding total number of ' + hitText + ':', \
                       'Corresponding number of selected ' + colTitle + ' each gene is involved with:', \
                       'Corresponding number of selected ' + rowTitle + ' each gene is involved with:', \
                       '%s ranked according to mean of effect sizes in cluster:' % (colTitle), \
                       'Corresponding mean of effect sizes of each %s:' % self._singular(colTitle), \
                       'Corresponding total number of genes of each %s:' % (self._singular(colTitle)), \
                       'Corresponding number of genes of each %s with at least one %s (of selected %s):' % (self._singular(colTitle), self._singular(hitText), rowTitle), \
                       'Corresponding total number of %s (of selected %s) for each %s (in all genes):' % (hitText, rowTitle, self._singular(colTitle)), \
                       'Corresponding number of selected %s each %s is involved with:' % (rowTitle, self._singular(colTitle)), \
                       '%s ranked according to mean of effect sizes in cluster:' % (rowTitle), \
                       'Corresponding mean of effect sizes of each %s:' % self._singular(rowTitle), \
                       'Corresponding total number of %s for each %s (genome-wide):' % (hitText, self._singular(rowTitle)), \
                       'Corresponding total number of %s for each %s (in all genes in selected %s):' % (hitText, self._singular(rowTitle), colTitle), \
                       'Corresponding number of genes (of selected %s) each %s is involved with:' % (colTitle, self._singular(rowTitle)), \
                       'Corresponding number of selected %s each %s is involved with:' % (colTitle, self._singular(rowTitle))] + \
                       (['Disease groups of selected %s ranked according to sum of effect sizes' % colTitle,
                        'Corresponding sum of effect sizes for each disease group of selected %s' % colTitle] if addDiseaseGroups else [])
        helpLines = (['(List of all TFs that are related to any of the PWMs)'] if sortedTfNamesOut != '' else []) +\
                      ['(All genes of the selected %s with hits of any of the selected %s, ranked according to the total number of %s)' % (colTitle, rowTitle, hitText), \
                       '(For each gene listed above, the total number of %s for any of the selected %s, ' \
                       'multiplied by the number of selected %s containing that gene)' % (hitText, rowTitle, colTitle), \
                       '(In the same order as above)', '(In the same order as above)', \
                       '', '(In the same order as above)', '(In the same order as above)', \
                       '(In the same order as above)', '(In the same order as above)', '(In the same order as above)', \
                       '', '(In the same order as above)', '(In the same order as above)', \
                       '(In the same order as above)', '(In the same order as above)', '(In the same order as above)'] +\
                        (['', '(In the same order as above)'] if addDiseaseGroups else [])
        contentLines = ([sortedTfNamesOut] if sortedTfNamesOut != '' else []) +\
                       [rankedGenesOut, gene2hitCountsOut, gene2colNameAssocOut, gene2rowNameAssocOut, \
                        rankedColNamesOut, colName2meanOfScoresOut, colName2totalGeneCountOut, \
                        colName2geneAssocOut, colName2hitCountOut, colName2rowNameAssocOut,
                        rankedRowNamesOut, rowName2meanOfScoresOut, rowName2totalHitCountOut, \
                        rowName2hitCountOut, rowName2geneAssocOut, rowName2colNameAssocOut] + \
                        ([rankedDiseaseGroupsOut, diseaseGroup2sumOfScoresOut] if addDiseaseGroups else [])
        print '/n'.join([('%s\n' + ('%s\n' % helpLines[i] if helpLines[i] != '' else '') + \
                         '%s\n') % (headerLines[i], contentLines[i]) for i in range(len(headerLines))])
        print '</pre>'
        return '<br>'.join([('<b>%s</b><br>' + ('<i>%s</i><br>' % helpLines[i] if helpLines[i] != '' else '') + \
                            '%s<br>') % (headerLines[i], contentLines[i]) for i in range(len(headerLines))])

    def _getBaseTrackName(self, baseTrackNameFn):
        baseTrackNameFn = '/'.join([self._commonDir, baseTrackNameFn])
        if not os.path.exists(baseTrackNameFn):
            return ''
        return open(baseTrackNameFn, 'r').readline().strip().split(':')

    def getRowTrackName(self):
        return self._getBaseTrackName('rowBaseTrackName.txt') + [self.getRowName(lowerCase=False)]

    def getColTrackName(self):
        return self._getBaseTrackName('colBaseTrackName.txt') + [self.getColName(lowerCase=False)]

    def getPubMedLink(self, useTFs=False):
        colPubMedTerm = self.getColName(lowerCase=False, removeParenthesis=True)
        parStart, parEnd = colPubMedTerm.find('('), colPubMedTerm.find(')')
        if parStart >= 0 and parEnd >=0 and parEnd > parStart:
            colPubMedTerm = colPubMedTerm[0:parStart] + colPubMedTerm[parEnd+1:-1]

        if useTFs:
            rowPubMedTerm = '(' + ' OR '.join([x for x in self.getTfNames().split(', ')]) + ')'
        else:
            rowPubMedTerm = self.getRowName(lowerCase=False, removeParenthesis=True)
        pubMedTerm = quote(colPubMedTerm + ' AND ' + rowPubMedTerm);
        pubMedLink = '<a target="_blank" href="http://www.ncbi.nlm.nih.gov/pubmed/?term='+ pubMedTerm +'">Search PubMed</a>'
        return pubMedLink

    def _exportTrackToFile(self, trackName, fn):
        GalaxyInterface.extractTrackManyBins(self._genome, trackName, '*', '*', True, 'gtrack', True, True, fn)

    def _getExportTrackHref(self, rowOrCol='row'):
        assert rowOrCol in ['row', 'col']

        trackName = self.getRowTrackName() if rowOrCol == 'row' else self.getColTrackName()

        #self._exportTrackToFile(trackName, '/tmp/tmpExportFile.bed')

        track1 = ':'.join(trackName)
        return URL_PREFIX + '/hyper?mako=extract&dbkey=%s&track1=%s' % (self._genome, quote(track1))

    def _getSelectTracksHref(self, withRowTrack=False, withColTrack=False):
        assert withRowTrack or withColTrack

        track1 = track2 = None
        if withRowTrack:
            track1 = ':'.join(self.getRowTrackName())

        if withColTrack:
            if withRowTrack:
                track2 = ':'.join(self.getColTrackName())
            else:
                track1 = ':'.join(self.getColTrackName())

        return URL_PREFIX + '/hyper?dbkey=%s&track1=%s' % (self._genome, quote(track1)) + ('&track2=%s' % quote(track2) if track2 != None else '')

    def getAnalyzeLink(self, withRowTrack=False, withColTrack=False):
        if not (withRowTrack or withColTrack):
            return ''

        selectHref = self._getSelectTracksHref(withRowTrack, withColTrack)
        if withRowTrack and withColTrack:
            return '<a href="' + selectHref + '">Select both tracks in the Genomic HyperBrowser</a>'
        else:
            exportHref = self._getExportTrackHref(rowOrCol=('row' if withRowTrack else 'col'))
            return '<a href="' + exportHref + '">Export</a>/'\
                   '<a href="' + selectHref + '">Select</a> track in the Genomic HyperBrowser'

    def _writeTrackForGeneListWithHits(self, fn):
        GalaxyInterface.getGeneTrackFromGeneList(self._genome, self.getColTrackName(), \
                                                 [x[0] for x in self.getGeneList(filter='hits')], fn)

    def getExportGeneListWithHitsLink(self):
        #self._writeTrackForGeneListWithHits('/tmp/tmpGenes.bed')

        href = URL_PREFIX \
            + '/tool_runner?tool_id=import_genelist&runtool_btn=yes&dbkey=%s&map=%s&col=%d&row=%d&mapid=%s' \
            % (self._genome, self._mapName, self._colIdx, self._rowIdx, self._mapId)

        return '<a href="' + href + '">(Export to the Genomic HyperBrowser)</a>'

    def _getConvertedGeneSymbolsGautvik(self, colNames, rowNames):
        convertFunc = '''
f <- function(probes) {
library(hgu133plus2.db)
syms = unlist(mget(probes, hgu133plus2SYMBOL, ifnotfound=NA))
syms[is.na(syms)]=names(syms[is.na(syms)])
return(syms) }'''

#        getGeneUniverse = '''
#library(hgu133plus2.db);
### Remove genes that have no entrezGene id
#entrezIds <- mget(ls(hgu133plus2ENTREZID), envir=hgu133plus2ENTREZID)
#haveEntrezId <- names(entrezIds)[sapply(entrezIds, function(x) !is.na(x))]
#
### Remove genes with no GO mapping
#haveGo <- sapply(mget(haveEntrezId, hgu133plus2GO),
#function(x) { if (length(x) == 1 && is.na(x))
#FALSE else TRUE
#})
#haveEntrezIdAndGo <- haveEntrezId[haveGo]
#entrezUniverse <- unique(unlist(mget(haveEntrezIdAndGo, hgu133plus2ENTREZID)))
#'''
#        doHyperGTest = '''
#f <- function(probes, geneUniverseFn) {
#    library(hgu133plus2.db)
#    library(GOstats)
#    geneUniverse = scan(geneUniverseFn, what='characters')
#    entrezProbes <- unique(unlist(mget(probes, hgu133plus2ENTREZID)))
#    params <- new("GOHyperGParams", geneIds=entrezProbes, universeGeneIds=geneUniverse, annotation="hgu133plus2.db",
#                  ontology="BP", pvalueCutoff=0.05, conditional=FALSE, testDirection="over")
#    hgOver <- hyperGTest(params)
#    return('hei')
#    tmpFile <- tempfile()
#    htmlReport(hgOver, file=tmpFile)
#    report <- paste(readLines(tmpFile), collapse=' ')
#    unlink(tmpFile)
#    return(report)
#    }
#'''

        #geneUniverseFn = os.sep.join([self._resultDir, 'gene_universe.txt'])
        #if os.path.exists(geneUniverseFn):
        #    geneUniverse =[x.strip() for x in open(geneUniverseFn).readlines()]
        #else:
        #    robjects.r(getGeneUniverse)
        #    geneUniverse = [x for x in robjects.r['entrezUniverse']]
        #
        #    f = open(geneUniverseFn, 'w')
        #    f.write('\n'.join(geneUniverse))
        #    f.close()

        from proto.RSetup import robjects

        html = ''
        for rowOrCol, probes in zip(['cols' if len(colNames) > 1 else 'col', 'rows' if len(rowNames) > 1 else 'row'], \
                                    [colNames, rowNames]):
            geneSymbols = robjects.r(convertFunc)(robjects.StrVector(probes))

            html += '<h3>Gene symbol%s for selected %s</h3>' % ('s' if rowOrCol[-1] == 's' else '', rowOrCol)
            html += ' | '.join(geneSymbols) if not isinstance(geneSymbols, basestring) else geneSymbols

            #html += '<h3>Gene ontology report for selected %s</h3>' % rowOrCol
            #html += robjects.r(doHyperGTest)(robjects.StrVector(probes), geneUniverseFn)
        return html

    def _getStdClusterHtmlText(self, cols, rows, colTitle, rowTitle, hitText, appendGeneList=False):
        colNames, rowNames = self.getColAndRowNames(cols, rows, lowerCase=False, removeParenthesis=True)
        ret = '<h3>' + colTitle + '</h3>' +\
                ' | '.join(colNames) +\
                '<h3>' + rowTitle + '</h3>' +\
                ' | '.join(rowNames) +\
                ('<h3>Information</h3>' + self.getGeneListOfRegulomeCluster(cols, rows, colNames, rowNames, colTitle, rowTitle, hitText) if appendGeneList else '')
        self.close()
        return ret

    def getClusterHtmlText(self, cols, rows):
        if self._mapId in ['disease_tf_count', 'disease_tf_log', 'disease_tf_binary', 'disease_tf_count_noflanks', \
                           'tf_disease_count', 'tf_disease_log', 'tf_disease_binary', 'tf_disease_noflanks_count']:
            return self._getStdClusterHtmlText(cols, rows, 'Diseases', 'TFs', 'TFBS', True)
        elif self._mapId in ['tf_barjoseph_disease_binary',  'tf_barjoseph_disease_1bpupstream_binary']:
            return self._getStdClusterHtmlText(cols, rows, 'Diseases', 'TFs', 'TF hits', True)
        elif self._mapId in ['tf_barjoseph_intogen_tissues_transcript_binary', 'tf_intogen_tissues_transcript_binary']:
            return self._getStdClusterHtmlText(cols, rows, 'IntOGen neoplasms (Topology)', 'TFs', 'TF hits', True)
        elif self._mapId in ['tf_barjoseph_intogen_tumors_transcript_binary', 'tf_intogen_tumors_transcript_binary']:
            return self._getStdClusterHtmlText(cols, rows, 'IntOGen neoplasms (Morphology)', 'TFs', 'TF hits', True)
        elif self._mapId in ['tf_barjoseph_intogen_v1_tissues_transcript_binary', 'tf_intogen_v1_tissues_transcript_binary']:
            return self._getStdClusterHtmlText(cols, rows, 'IntOGen (v1) neoplasms, transcriptional alterations (Topology)', 'TFs', 'TF hits', True)
        elif self._mapId in ['tf_barjoseph_intogen_v1_tumors_transcript_binary', 'tf_intogen_v1_tumors_transcript_binary']:
            return self._getStdClusterHtmlText(cols, rows, 'IntOGen (v1) neoplasms, transcriptional alterations (Morphology)', 'TFs', 'TF hits', True)
        elif self._mapId in ['tf_barjoseph_intogen_v2_tissues_transcript_binary', 'tf_intogen_v2_tissues_transcript_binary']:
            return self._getStdClusterHtmlText(cols, rows, 'IntOGen (v2) neoplasms, transcriptional alterations (Topology)', 'TFs', 'TF hits', True)
        elif self._mapId in ['tf_barjoseph_intogen_v2_tumors_transcript_binary', 'tf_intogen_v2_tumors_transcript_binary']:
            return self._getStdClusterHtmlText(cols, rows, 'IntOGen (v2) neoplasms, transcriptional alterations (Morphology)', 'TFs', 'TF hits', True)
        elif self._mapId in ['tf_barjoseph_intogen_v2_tissues_copynumber_binary', 'tf_intogen_v2_tissues_copynumber_binary']:
            return self._getStdClusterHtmlText(cols, rows, 'IntOGen (v2) neoplasms, copy number alterations (Topololy)', 'TFs', 'TF hits', True)
        elif self._mapId in ['tf_barjoseph_intogen_v2_tumors_copynumber_binary', 'tf_intogen_v2_tumors_copynumber_binary']:
            return self._getStdClusterHtmlText(cols, rows, 'IntOGen (v2) neoplasms, copy number alterations  (Morphology)', 'TFs', 'TF hits', True)
        elif self._mapId in ['tf_barjoseph_phenopedia_binary', 'tf_phenopedia_binary', 'tf_barjoseph_phenopedia_150_binary', 'tf_phenopedia_150_binary']:
            return self._getStdClusterHtmlText(cols, rows, 'Phenopedia diseases', 'TFs', 'TF hits', True)
        elif self._mapId in ['disease_methylations_count', 'histmod_disease_count']:
            return self._getStdClusterHtmlText(cols, rows, 'Diseases', 'Histone modifications', 'modified nucleosomes', True)
        elif self._mapId in ['disease_mirna_count', 'mirna_disease_count']:
            return self._getStdClusterHtmlText(cols, rows, 'Diseases', 'MiRNAs', 'miRNA loci', True)
        elif self._mapId in ['repeats_disease_count', 'disease_repeats_count']:
            return self._getStdClusterHtmlText(cols, rows, 'Diseases', 'Repeat types', 'repeating elements', True)
        elif self._mapId in ['histone_tf_count', 'tf_histmod_count']:
            return self._getStdClusterHtmlText(cols, rows, 'Histone modifications', 'TFs', 'TFBS', False)
        elif self._mapId in ['go_tf_log', 'tf_geneontology_log', 'tf_geneontology_binary', 'tf_barjoseph_geneontology_1bpupstream_binary']:
            return self._getStdClusterHtmlText(cols, rows, 'Gene ontology terms', 'TFs', 'TFBS', True)
        elif self._mapId in ['tf_barjoseph_geneontology_1bpupstream_binary']:
            return self._getStdClusterHtmlText(cols, rows, 'Gene ontology terms', 'TFs', 'TF hits', True)
        elif self._mapId in ['tf_chrarms_count']:
            return self._getStdClusterHtmlText(cols, rows, 'Chromosome arms', 'TFs', 'TFBS', False)
        elif self._mapId in ['histmod_chrarms_count']:
            return self._getStdClusterHtmlText(cols, rows, 'Chromosome arms', 'Histone modifications', 'modified nucleosomes', False)
        elif self._mapId in ['histmod_geneontology_count']:
            return self._getStdClusterHtmlText(cols, rows, 'Gene ontology terms', 'Histone modifications', 'modified nucleosomes', True)
        elif self._mapId in ['gautvik', 'gautvik_least1000', 'gautvik_most1000', 'gautvik_mirna']:
            colNames, rowNames = self.getColAndRowNames(cols, rows, lowerCase=False, removeParenthesis=True)
            html = self._getStdClusterHtmlText(cols, rows, 'Expressed RNA', 'Expressed RNA', '', False)
            html += self._getConvertedGeneSymbolsGautvik(colNames, rowNames)
            return html
        elif self._mapId in ['3d_lieberman']:
            return self._getStdClusterHtmlText(cols, rows, 'Chromosome locations', 'Chromosome locations', '', False)
        elif self._mapId in ['sample_tf_sample_disease', 'tf_encode_gm12878_full_gwas_catalog', 'tf_encode_gm12878_full_gwas_catalog', 'mads_350', 'mads_350', 'mads_350', 'mads_350', 'mads_350', 'ian_mills_grouped_loci_and_proxies_vs_biofeatures', 'gwas_vs_25kb_gwas', 'encode_gwas_vs_dhs', 'encode_tf_vs_tf']:
            return self._getStdClusterHtmlText(cols, rows, 'Rows', 'Columns', '', False)
        return 'Error: MapID not implemented in GoogleMapsInterface'

    def _getStdHtmlText(self, extraTextForRow='', extraTextForCol='', includeGeneLists=True, includeCounts=True, includePVals=True, useTFs=False):
        ret = '<b>Indexes:</b> ' + repr((self._rowIdx, self._colIdx)) + '<br>' +\
                '<h3>' + self.getColName(lowerCase=False, removeParenthesis=True) + '</h3>' +\
                extraTextForCol + \
                ('<b>Number of genes:</b> ' + self.getColElCount() + '<br>' if includeCounts else '') +\
                '<b>Further analysis: </b>' + self.getAnalyzeLink(withColTrack=True) + '<br>' +\
                '<h3>' + self.getRowName(lowerCase=False, removeParenthesis=True) + '</h3>' +\
                extraTextForRow + \
                ('<b>Total count:</b> ' + self.getRowElCount() + '<br>' if includeCounts else '') +\
                '<b>Further analysis: </b>' + self.getAnalyzeLink(withRowTrack=True) + '<br>' +\
                '<h3>Results</h3>' +\
                ('<b>Gene list with hits:</b> ' + self.getGeneListAsStr(filter='hits') + ' ' + self.getExportGeneListWithHitsLink() + '<br>' +\
                '<b>Remaining genes:</b> ' + self.getGeneListAsStr(filter='nohits') + '<br>' if includeGeneLists else '') +\
                ('<b>Count:</b> ' + self.getCount(toStr=True) + '<br>' if includeCounts else '') +\
                '<b>Effect size:</b> ' + self.getValue(toStr=True) + '<br>' +\
                ('<b>P-value:</b> ' + self.getPval(toStr=True) + ' (' + self.getSignificance(toStr=True) + ')<br>' if includePVals else '') +\
                '<b>Literature: </b>' + self.getPubMedLink(useTFs=useTFs) + '<br>' +\
                '<b>Further analysis: </b>' + self.getAnalyzeLink(withRowTrack=True, withColTrack=True) + '<br>'
#                '<b>Test: </b>' + self._toStr(self.getIndexesFromRowName('fox')) + '<br>'
        self.close()
        return ret

    def getHtmlText(self):
        if self._mapId in ['disease_tf_count', 'disease_tf_log', 'disease_tf_binary', 'disease_tf_count_noflanks', \
                           'tf_disease_count', 'tf_disease_log', 'tf_disease_binary', 'tf_disease_noflanks_count', \
                           'tf_barjoseph_disease_binary', 'tf_barjoseph_disease_1bpupstream_binary']:
            return self._getStdHtmlText(extraTextForRow=\
                                        '<b>TF:</b> ' + self.getTfNames() + '<br>' \
                                        '<b>TF classes:</b> ' + self.getTfClasses() + '<br>', \
                                        extraTextForCol=\
                                        '<b>Disease parents:</b> ' + self.getDiseaseParents(toStr=True) + '<br>', \
                                        useTFs=True)
        elif self._mapId in ['tf_barjoseph_intogen_tissues_transcript_binary', 'tf_intogen_tissues_transcript_binary',
                             'tf_barjoseph_intogen_tumors_transcript_binary', 'tf_intogen_tumors_transcript_binary']:
            return self._getStdHtmlText(extraTextForRow=\
                                        '<b>TF:</b> ' + self.getTfNames() + '<br>' \
                                        '<b>TF classes:</b> ' + self.getTfClasses() + '<br>', \
                                        useTFs=True)
        elif self._mapId in ['tf_barjoseph_intogen_v1_tissues_transcript_binary', 'tf_intogen_v1_tissues_transcript_binary',
                             'tf_barjoseph_intogen_v1_tumors_transcript_binary', 'tf_intogen_v1_tumors_transcript_binary']:
            return self._getStdHtmlText(extraTextForRow=\
                                        '<b>TF:</b> ' + self.getTfNames() + '<br>' \
                                        '<b>TF classes:</b> ' + self.getTfClasses() + '<br>', \
                                        useTFs=True)
        elif self._mapId in ['tf_barjoseph_intogen_v2_tissues_transcript_binary', 'tf_intogen_v2_tissues_transcript_binary',
                             'tf_barjoseph_intogen_v2_tumors_transcript_binary', 'tf_intogen_v2_tumors_transcript_binary',
                             'tf_barjoseph_intogen_v2_tissues_copynumber_binary', 'tf_intogen_v2_tissues_copynumber_binary',
                             'tf_barjoseph_intogen_v2_tumors_copynumber_binary', 'tf_intogen_v2_tumors_copynumber_binary']:
            return self._getStdHtmlText(extraTextForRow=\
                                        '<b>TF:</b> ' + self.getTfNames() + '<br>' \
                                        '<b>TF classes:</b> ' + self.getTfClasses() + '<br>', \
                                        useTFs=True)
        elif self._mapId in ['tf_barjoseph_phenopedia_binary', 'tf_phenopedia_binary', 'tf_barjoseph_phenopedia_150_binary', 'tf_phenopedia_150_binary']:
            return self._getStdHtmlText(extraTextForRow=\
                                        '<b>TF:</b> ' + self.getTfNames() + '<br>' \
                                        '<b>TF classes:</b> ' + self.getTfClasses() + '<br>', \
                                        extraTextForCol=\
                                        '<b>Disease parents:</b> ' + self.getDiseaseParents(toStr=True) + '<br>', \
                                        useTFs=True)
        elif self._mapId in ['disease_methylations_count', 'disease_mirna_count', 'disease_repeats_count', \
                             'histmod_disease_count', 'mirna_disease_count', 'repeats_disease_count']:
            return self._getStdHtmlText(extraTextForCol=\
                                        '<b>Disease parents:</b> ' + self.getDiseaseParents(toStr=True) + '<br>')
        elif self._mapId in ['histone_tf_count', 'tf_histmod_count']:
            return self._getStdHtmlText(extraTextForRow=\
                                        '<b>TF:</b> ' + self.getTfNames() + '<br>' \
                                        '<b>TF classes:</b> ' + self.getTfClasses() + '<br>', \
                                        includeGeneLists=False, useTFs=True)
        elif self._mapId in ['go_tf_log', 'tf_geneontology_log', 'tf_geneontology_binary', 'tf_barjoseph_geneontology_1bpupstream_binary']:
            return self._getStdHtmlText(extraTextForRow=\
                                        '<b>TF:</b> ' + self.getTfNames() + '<br>' \
                                        '<b>TF classes:</b> ' + self.getTfClasses() + '<br>', \
                                        includeGeneLists=True, useTFs=True)
        elif self._mapId in ['tf_chrarms_count']:
            return self._getStdHtmlText(extraTextForRow=\
                                        '<b>TF:</b> ' + self.getTfNames() + '<br>' \
                                        '<b>TF classes:</b> ' + self.getTfClasses() + '<br>', \
                                        includeGeneLists=False, useTFs=True)
        elif self._mapId in ['histmod_chrarms_count']:
            return self._getStdHtmlText(includeGeneLists=False, useTFs=False)
        elif self._mapId in ['histmod_geneontology_count']:
            return self._getStdHtmlText(includeGeneLists=True, useTFs=False)
        elif self._mapId in ['gautvik', 'gautvik_least1000', 'gautvik_most1000', 'gautvik_mirna']:
            colName = self.getColName(lowerCase=False, removeParenthesis=True)
            rowName = self.getRowName(lowerCase=False, removeParenthesis=True)
            html = self._getStdHtmlText(includeGeneLists=False, includeCounts=False, includePVals=False, useTFs=False)
            html += self._getConvertedGeneSymbolsGautvik([colName], [rowName])
            return html
        elif self._mapId in ['3d_lieberman', 'sample_tf_sample_disease', 'tf_encode_gm12878_full_gwas_catalog', 'tf_encode_gm12878_full_gwas_catalog', 'mads_350', 'mads_350', 'mads_350', 'mads_350', 'mads_350', 'ian_mills_grouped_loci_and_proxies_vs_biofeatures', 'gwas_vs_25kb_gwas', 'encode_gwas_vs_dhs', 'encode_tf_vs_tf']:
            return self._getStdHtmlText(includeGeneLists=False, includeCounts=False, useTFs=False, includePVals=False)

        return 'Error: MapID not implemented in GoogleMapsInterface'
