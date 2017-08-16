import numpy

from gold.result.Results import Results
from gold.result.ResultsViewer import ResultsViewer
from proto.hyperbrowser.HtmlCore import HtmlCore
from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile


class GwasResults(dict):
    "Keeps results for a single Gwas track. Inherits dict. Each key corresponds to a reference subtype (e.g. a single cell type or TF). Each value corresponds to a Results object"
    _MAIN_RES_DICT_KEY = None #Defined in subclasses
    def __init__(self, gwasId=None, verbose=False, galaxyFn=None):
        self._gwasId = gwasId
        self._verbose = verbose
        self._galaxyFn = galaxyFn
    
    def getRefSubTypes(self):
        return self.keys()
    
    def getResDictKeys(self):
        assert len(self.getRefSubTypes())>0
        return self[ self.getRefSubTypes()[0] ].getResDictKeys()
    
    def getLocalRegions(self):
        assert len(self.getRefSubTypes()) > 0
        localRegions = self[ self.getRefSubTypes()[0] ].keys()
        for refSubType in self.getRefSubTypes():
            assert self[refSubType].keys() == localRegions, (self[refSubType].keys(), localRegions)
        return localRegions
    
    def __setitem__(self, key, item):
        assert isinstance(key, basestring)
        assert isinstance(item, Results), (key,item)
        dict.__setitem__(self, key, item)
        
    def getAllGlobalResultDicts(self, assertNoNones=False):
        resDicts = dict([(key, res.getGlobalResult()) for key,res in self.items()])
        if assertNoNones:
            assert all(resDict is not None for resDict in resDicts.values())
        return resDicts
    
    def getResult(self, refSubType):
        return self[refSubType]
    
    def getResultTableLink(self, refSubType, linkText):
        assert self._galaxyFn is not None and self._gwasId is not None
        res = self.getResult(refSubType)
        basedir  = GalaxyRunSpecificFile(['ResultTableDetails', self._gwasId, refSubType],self._galaxyFn).getDiskPath(ensurePath=True)
        staticFile = GalaxyRunSpecificFile(['ResultTables', self._gwasId, refSubType+'.html'], self._galaxyFn)

        core = HtmlCore()
        core.begin()
        if hasattr(res, 'batchText'):
            core.paragraph('<pre> Corresponding batch command line:\n ' + res.batchText + '</pre>')
        core.paragraph(str(ResultsViewer(res, basedir) ))
        core.end()
        staticFile.writeTextToFile( str(core) )
        #staticFile.writeTextToFile( str(ResultsViewer(res, basedir) ) )
        return staticFile.getLink(linkText)
        #GalaxyInterface._viewResults(res, galaxyFn)
    
    def getAllGlobalResults(self, resDictKey=None, fillInNoneValues=False):
        if resDictKey is None:
            resDictKey = self._MAIN_RES_DICT_KEY
        if not fillInNoneValues:
            for key,resDict in self.getAllGlobalResultDicts().items():
                assert resDict is not None, (key,resDict, self.getAllGlobalResultDicts())
                assert resDictKey in resDict, (key,resDict, resDictKey, self.getAllGlobalResultDicts())
        
        if self._verbose:
            for key,resDict in self.getAllGlobalResultDicts().items():
                if resDict is None:
                    print 'Result dict missing for:',key,'<br>'
                elif resDictKey not in resDict:
                    print 'Key "%s" missing among keys (%s) for: %s' % (resDictKey, resDict.keys(), key), '<br>'
        results = dict( [(key, None if (resDict is None and fillInNoneValues) else resDict.get(resDictKey)) for key,resDict in self.getAllGlobalResultDicts().items()] )
        return results

    def getAllLocalResults(self, resDictKey=None, fillInNoneValues=False):
        if resDictKey is None:
            resDictKey = self._MAIN_RES_DICT_KEY
        assert fillInNoneValues
        #if not fillInNoneValues:
        #    for key,resDict in self.getAllGlobalResultDicts().items():
        #        assert resDict is not None, (key,resDict, self.getAllGlobalResultDicts())
        #        assert resDictKey in resDict, (key,resDict, resDictKey, self.getAllGlobalResultDicts())
        #localRegions = self.getLocalRegions()
        localResults = {}
        for refSubType in self.getRefSubTypes():
            localResults[refSubType] = dict([(localRegion, (None if self[refSubType] is None else self[refSubType][localRegion].get(resDictKey)) ) for localRegion in self.getLocalRegions()])
                    
        return localResults

    def getHtmlLocalResultsTable(self, resDictKey=None, fillInNoneValues=False):
        allLocalResults = self.getAllLocalResults(resDictKey, fillInNoneValues)
        allLocalRegions = self.getLocalRegions()
        allRefSubTypes = self.getRefSubTypes()
        
        core = HtmlCore()
        core.tableHeader(['-']+allRefSubTypes, sortable = True)
        #for refSubType in allLocalResults.keys():            
        #    core.tableLine([refSubType] + [allLocalResults[refSubType][localRegion] for localRegion in localRegions])
        for localRegion in allLocalRegions:         
            core.tableLine([localRegion] + [allLocalResults[refSubType][localRegion] for refSubType in allRefSubTypes])
        core.tableFooter()
        #core.end()
        return str(core)

    def getLinkToSingleLocalHtmlResultsTable(self, linkText, disease, resDictKey, galaxyFn):
        core = HtmlCore()
        core.begin()        
        core.paragraph( self.getHtmlLocalResultsTable(resDictKey, fillInNoneValues=True) )
        core.end()
        
        staticFile = GalaxyRunSpecificFile(['LocalResultTables', resDictKey, disease+'.html'], galaxyFn)
        staticFile.writeTextToFile( str(core) )
        return staticFile.getLink(linkText)

    def getLinkToLocalResultsHeatmap(self, linkText,disease, resDictKey, galaxyFn):
        values = []
        allLocalResults = self.getAllLocalResults(resDictKey, fillInNoneValues=True)        
        allLocalRegions = self.getLocalRegions()        
        refSubTypes = self.getRefSubTypes()
        numRows=len(allLocalRegions)
        for localRegion in allLocalRegions:         
            for refSubType in refSubTypes:
                values.append(allLocalResults[refSubType][localRegion])
        
        if None in values or any(numpy.isnan(x) for x in values):
            return 'Not generated, due to missing values'
        #if not ( 0 < (float(sum(values)) / len(values)) < 100000):
        #    return 'Not generated, due to too small/large values (average: %s)' % (float(sum(values)) / len(values))
        maxVal = max(values)
        from proto.RSetup import r, robjects
        r('library(gplots)')
        dataMatrix = r.matrix(robjects.FloatVector(values),nrow=numRows)
        if (r.length(r.unique(r.colSums(dataMatrix))) <= 1) or (r.length(r.unique(r.rowSums(dataMatrix))) <= 1):
            return 'Not generated, due to lacking variation'
        dataMatrix= r('function(data,names){rownames(data)=names; data}')(dataMatrix,[str(x) for x in allLocalRegions])
        dataMatrix= r('function(data,names){colnames(data)=names; data}')(dataMatrix,refSubTypes)
        #print 'dimensions dataMatrix: ', r.dim(dataMatrix), dataMatrix
        sf = GalaxyRunSpecificFile(['LocalResultTables', resDictKey, disease+'_heatmap.png'], galaxyFn)
        sf.openRFigure(h=4000,w=4000)
        r("function(data,maxVal){heatmap.2(data,col =c('#99FFFF',colorRampPalette(c('cyan','blue', 'black', 'red', 'yellow'))(161),'#FFFF66'), breaks = seq(0,maxVal,length=164),trace='none',margins=c(15,15))}")(dataMatrix, maxVal)
        #r("function(data){heatmap(data)}")(dataMatrix)
        sf.closeRFigure()
        return sf.getLink(linkText)

    def __str__(self):
        return 'GwasResults:<br>' + '<br>'.join([key+':'+str(res) for key,res in self.items()])
    
class EnrichmentGwasResults(GwasResults):
    #_MAIN_RES_DICT_KEY = 'Result'
    _MAIN_RES_DICT_KEY = 'Differential relative coverage'
    #def __init__(self, verbose):        
    #    GwasResults.__init__(self, verbose)

class HypothesisTestingGwasResults(GwasResults):
    #_MAIN_RES_DICT_KEY = 'Result'
    _MAIN_RES_DICT_KEY = 'P-value'
    #def __init__(self, verbose):        
    #    GwasResults.__init__(self, verbose)
