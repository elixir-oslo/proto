from proto.hyperbrowser.HtmlCore import HtmlCore
from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
from quick.gwas.GwasResults import GwasResults


class MultiGwasResults(dict):
    'Has traits (diseases) as keys, and objects of class GwasResults as values'
    def getRefSubTypes(self):
        assert len(self)>0, 'Does not contain results for any disease'
        arbitraryGwasResults = self.values()[0]
        refSubTypes = arbitraryGwasResults.getRefSubTypes()
        for disease in self.keys():
            assert self[disease].getRefSubTypes() == refSubTypes, 'incompatible refSubTypes between diseases'
        return refSubTypes

    def getResDictKeys(self):
        assert len(self)>0, 'Does not contain results for any disease'
        arbitraryGwasResults = self.values()[0]
        return arbitraryGwasResults.getResDictKeys()
            
    def getDiseases(self):
        return self.keys()
    
    def getSingleResultValue(self, disease, refSubType):
        return self[disease].getAllGlobalResults(fillInNoneValues=True)[refSubType] #fixme: is this okay to be true..?
    
    def getSingleResultTableLink(self, disease, refSubType, linkText):
        return self[disease].getResultTableLink(refSubType, linkText)
    
    def getColoredSortedReferencesTable(self, colorFn):
        #see getHtmlResultsTable
        from collections import defaultdict
        colorSchemeDict = defaultdict(dict)
        colorScheme = open(colorFn).read().split('\n')
        diseases = colorScheme[0].strip().split('\t')[1:]
        for line in colorScheme[1:]:
            tab = line.split('\t')
            refSubType = tab[0]
            for index, color in enumerate(tab[1:]):
                colorSchemeDict[refSubType][diseases[index]] = color
        
        
        core = HtmlCore()
        
        resultDict = defaultdict(list)
        for refSubType in self.getRefSubTypes():
            for disease in self.getDiseases():
                value = self.getSingleResultValue(disease, refSubType)
                resultDict[disease].append((value, refSubType, colorSchemeDict[refSubType][disease]))
        
        sortedResultTab = [(k, sorted(v, reverse=True)) for k, v in resultDict.items()]
        core.tableHeader([v[0] for v in sortedResultTab], sortable = False)
        tdCellTemplate = '<td bgcolor="%s">%s (%f)</td>'
        for i in range(len(sortedResultTab[0][1])):
            core.append('<tr>') 
            for v in range(len(sortedResultTab)):
                value, refSubType, colNum = sortedResultTab[v][1][i]
                color = 'green' if colNum == '1' else 'red'
                
                core.append(tdCellTemplate % (color, refSubType, value ))
            core.append('</tr>\n')
            
        core.tableFooter()
        core.end()
        return str(core)
    
    def getHtmlResultsTable(self, includeResultTables=False):
        core = HtmlCore()
        core.tableHeader(['-']+self.getDiseases(), sortable = True)
        #assert len(disRes)>0, 'No gwas Dataset found, i.e. no subtrack found for ' + gwasTnBase
        #print "ALLrows: ", rows
        #print "AllCols: ",
        for refSubType in self.getRefSubTypes():
            if includeResultTables:
                core.tableLine([refSubType] + [self.getSingleResultTableLink(disease, refSubType, str(self.getSingleResultValue(disease, refSubType))) for disease in self.getDiseases()])
            else:
                core.tableLine([refSubType] + [self.getSingleResultValue(disease, refSubType) for disease in self.getDiseases()])
            
        #for row in rows:
            #print "ROW: ", 
            #core.tableLine([row] + [disRes[col][row].getGlobalResult().get('Result') if (disRes[col][row].getGlobalResult() is not None) else "MISSING" for col in disRes.keys()])
            #core.tableLine([row] + [disRes[col][row].get('Result') if (disRes[col][row] is not None) else "MISSING" for col in disRes.keys()])
        core.tableFooter()
        core.end()
        return str(core)


    
    def getLinksToAllLocalHtmlResultsTables(self, galaxyFn):
        core = HtmlCore()
        core.tableHeader(['-']+self.getResDictKeys(), sortable = True)
        for disease in self.getDiseases():
            core.tableLine([disease] + [(self[disease].getLinkToSingleLocalHtmlResultsTable('Table', disease, resDictKey, galaxyFn) + ' / ' +\
                                        self[disease].getLinkToLocalResultsHeatmap('Heatmap', disease, resDictKey, galaxyFn) )\
                                        for resDictKey in self.getResDictKeys() ])
                #text += 'Local results for %s:<br>' % disease
        core.tableFooter()        
        return str(core)

    def getLinkToClusteredHeatmap(self, linkText, galaxyFn):
        values = []
        refSubTypes = self.getRefSubTypes()
        diseases = self.getDiseases()
        numRows=len(refSubTypes)
        for refSubType in refSubTypes:
            for disease in diseases:
                values.append(self.getSingleResultValue(disease, refSubType))
        
        if None in values:
            return 'Not generated, due to missing values'
        
        from proto.RSetup import r, robjects
        r('library(gplots)')
        dataMatrix = r.matrix(robjects.FloatVector(values),nrow=numRows)
        dataMatrix= r('function(data,names){rownames(data)=names; data}')(dataMatrix,refSubTypes)
        dataMatrix= r('function(data,names){colnames(data)=names; data}')(dataMatrix,diseases)
        
        sf = GalaxyRunSpecificFile(['heatmap.png'], galaxyFn)
        sf.openRFigure(h=4000,w=4000)
        r("function(data){heatmap.2(data,col =c('#99FFFF',colorRampPalette(c('cyan','blue', 'black', 'red', 'yellow'))(161),'#FFFF66'), breaks = seq(0,2,length=164),trace='none',margins=c(15,15))}")(dataMatrix)
        #r("function(data){heatmap(data)}")(dataMatrix)
        sf.closeRFigure()
        return sf.getLink(linkText)
        
        
    def __setitem__(self, key, item):
        assert isinstance(key, basestring)
        assert isinstance(item, GwasResults)
        dict.__setitem__(self, key, item)
