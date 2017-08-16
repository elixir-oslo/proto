# !/software/VERSIONS/python2-2.7.6/bin/python

__author__="Abdulrahman Azab"
__date__ ="$March 30, 2015$"
__PythonVersion__= "2.7 [MSC v.1500 32 bit (Intel)]"

import os
# import sys
#
# reload(sys)
# sys.setdefaultencoding('utf-8')

from collections import OrderedDict, namedtuple
from unidecode import unidecode
from quick.gsuite.GSuiteHbIntegration import getSubtracksAsGSuite
from quick.trackaccess.DatabaseTrackAccessModule import DatabaseTrackAccessModule
from quick.webtools.GeneralGuiTool import GeneralGuiTool

from quick.webtools.imports.EncodeTrackSearchTool import EncodeTrackSearchTool
from quick.webtools.imports.CGAtlasTrackSearchTool import CGAtlasTrackSearchTool
from quick.webtools.imports.FANTOM5TrackSearchTool import FANTOM5TrackSearchTool
from quick.webtools.imports.ICGCTrackSearchTool import ICGCTrackSearchTool
from quick.webtools.imports.EBIHubTrackSearchTool import EBIHubTrackSearchTool
from quick.webtools.imports.Epigenome2TrackSearchTool import Epigenome2TrackSearchTool
from quick.webtools.imports.Epigenome2ImputedTrackSearchTool import Epigenome2ImputedTrackSearchTool
from quick.webtools.imports.GWASTrackSearchTool import GWASTrackSearchTool

from proto.hyperbrowser.HtmlCore import HtmlCore
from gold.gsuite.GSuite import GSuite
from gold.gsuite.GSuiteTrack import GSuiteTrack, HttpGSuiteTrack, HttpsGSuiteTrack, FtpGSuiteTrack, RsyncGSuiteTrack
from gold.application.DataTypes import getSupportedFileSuffixesForGSuite
from gold.util.RandomUtil import random
import quick.gsuite.GSuiteUtils as GSuiteUtils
#import gold.gsuite.GSuiteComposer as GSuiteComposer
#import gold.gsuite.GSuiteParser as GSuiteParser

#importing from: '/hyperbrowser/src/hb_core_developer/trunk/data'
from config.Config import HB_SOURCE_DATA_BASE_DIR
from third_party.asteval_raise_errors import Interpreter

VocabularyElement = namedtuple('VocabularyElement', ('category', 'subCategory','sourceTool','sourceTable','sourceTableFilter','toolAttr','toolVal','fileType'))

class TrackGlobalSearchModule(object):
    def __init__(self, isSqlite = True):
        self.DOWNLOAD_PROTOCOL = None
        self.exception = None
        self.DB = DatabaseTrackAccessModule(isSqlite)
        self.VOCABULARY = []
        self.Rpositories = []
        #self.VOCABULARY_TABLE = 'global_search_vocabulary'
        #self.COLS = []
        self.SOURCE = {'EncodeTrackSearchTool': 'ENCODE',
#                      'EpigenomeTrackSearchTool': 'Roadmap Epigenomics',
                      'Epigenome2TrackSearchTool': 'Roadmap Epigenomics',
                      'Epigenome2ImputedTrackSearchTool': 'Roadmap Epigenomics Imputed',
                      'CGAtlasTrackSearchTool': 'TCGA',
                      'FANTOM5TrackSearchTool': 'FANTOM',
                      'EBIHubTrackSearchTool': 'EBIHub',
                      'ICGCTrackSearchTool': 'ICGC'}

        with open(os.path.join(HB_SOURCE_DATA_BASE_DIR, 'TrackTextSearch', 'Vocabulary.tsv'),'r') as f:
            lines = f.readlines()

        for line in lines:
            if line.startswith('#'):
                continue
            lineList = line.split('\t')
            category = lineList[0]
            subCategory = lineList[1]
            sourceTool = lineList[2]
            sourceTable = None

            aeval = Interpreter()
            for sourceTool in self.SOURCE.keys():
                aeval.symtable[sourceTool] = globals()[sourceTool]

            for k in self.SOURCE.keys():
                if self.SOURCE[k].upper() == lineList[2].upper():
                    sourceTool = k
                    sourceToolCls = aeval(k)
                    sourceTable = sourceToolCls._getTableName()
                    sourceTableFilter = sourceToolCls._getGlobalSQLFilter()
                    break

            toolInput = lineList[-1].split(':')[1]
            toolAttr = toolInput.split('=')[0].strip()
            toolVal_text = toolInput.split('=')[1].strip()

            toolVal = toolVal_text

            self.VOCABULARY.append \
                (VocabularyElement(category,subCategory,sourceTool,sourceTable,sourceTableFilter,toolAttr,toolVal,None))

            self.items = []
            self.sourceCounts = {}
            self.rows = []

    #def createVocabularyTable(self,vocabulary_file):
    #    self.DB._db.dropTable(self.VOCABULARY_TABLE)
    #    self.DB._db.createTableFromDict(self.VOCABULARY_TABLE,self._cols, pk = 'url')
    #    self.DB._db.insertRows(self._fileIndexTable,self._rowList)

    def getCategories(self):
        category_list = []
        for cat in self.VOCABULARY:
            if not cat.category in category_list:
                category_list.append(cat.category)
        return sorted(category_list, key=lambda s: s.lower())#case insensitive sorting

    def getSubCategories(self,category):
        List = [ve.subCategory for ve in self.VOCABULARY if ve.category == category]
        List = list(set(List))
        #List.sort()
        return sorted(List, key=lambda s: s.lower())#case insensitive sorting

    def getAllItems(self):
        return self.VOCABULARY

    def getItems(self,category,subCategory):
        items = []

        for el in self.VOCABULARY:
            if category.upper() == el.category.upper() and  subCategory.upper() == el.subCategory.upper():
                items.append(el)
        return items

    def getSourceToolURLParams(self, category, subCategory, source):
        allItems = self.getItems(category, subCategory)
        sourceTool = None
        compare = {}

        for k,v in self.SOURCE.items():
            if source == v:
                sourceTool = k
                break
        items = [x for x in allItems if x.sourceTool == sourceTool]
        
        attr_val_dict = {}
        i = 0
        for item in items:
            attr_val_dict['attributeList'+str(i)] = item.toolAttr
            attr_val_dict['multiSelect'+str(i)] = 'Text Search'
            #attr_val_dict['valueList'+str(i)] = hit.toolVal
            attr_val_dict['multiValueReceiver'+str(i)] = item.toolVal
            i += 1
        
        return sourceTool, attr_val_dict
        

    def dataSourceExists(self,source):
        for key, value in self.SOURCE.items():
            if source == value:
                return True
        return False

    def getDataSources(self,items):
        #self.items = []
        #if category != None and subCategory != None:
        #    self.items = self.getItems(category,subCategory)
        #else:
        #    return
        #if len(self.items) == 0:
        #    return

        self.sourceCounts = dict.fromkeys(self.SOURCE.keys(),0)
        for item in items:
            src = item.sourceTool
            #if item.sourceTool in cls.SOURCE.keys():
            self.sourceCounts[item.sourceTool] = len(self.getRows(item,filterFileSuffix = True))

        self.Rpositories = [self.SOURCE[src]+ ' ['+str(self.sourceCounts[src])+']' for src in self.sourceCounts.keys() if self.sourceCounts[src] > 0]

        sourceDict = [(self.SOURCE[src],self.sourceCounts[src]) for src in self.sourceCounts.keys() if self.sourceCounts[src] > 0]
        #sourceList.insert(0,'All Original Tracks')
        return sourceDict

    def getAllFileTypes(self):
        fileTypesDict = self.DB.getAllFileTypes()
        return [x for x in fileTypesDict.keys()]

    def getDataTypes(self,items,source = 'All'):
        rows = []
        source = source.strip()
        sourceTool = 'None'
        for key, value in self.SOURCE.items():
            if source == value:
                sourceTool = key
        for item in items:
            if not 'All' in source and item.sourceTool != sourceTool:
                continue
            rows.extend(self.getItemDataTypes(item))
        #print rows
        datatypes = {}
        for row in rows:
            
            try:
                if row[0] in datatypes.keys():
                    datatypes[row[0]] += int(row[1])
                else:
                    datatypes[row[0]] = int(row[1])
            except Exception as ex:

                raise Exception(str(ex)+'----'+unicode(row))
                
        return datatypes    
    
    def filterRowsByDataTypes(self, rows, dataTypes = []):
        if len(dataTypes)== 0 or len(dataTypes) == 1 and 'All' in dataTypes[0]:
            return rows
        else:
            fRows = []
            for row in rows:
                if self._isValidRowOfDataType(row,dataTypes):
                    fRows.append(row)
            return fRows

    def getFileTypes(self,items,source = 'All'):
        rows = []
        source = source.strip()
        sourceTool = 'None'
        for key, value in self.SOURCE.items():
            if source == value:
                sourceTool = key

        fileExtList = self.DB.getAllFileExtensions()
        #print fileExtList
        fileTypes = []
        for item in items:
            if not 'All' in source and item.sourceTool != sourceTool:
                continue
            #cols, colListString = self.getColListString(item.sourceTable)
            #attribute_col_name = self.DB.getAttributeNameFromReadableName(item.sourceTable,item.toolAttr)
            rows.extend(self.getRows(item))

        for ext in fileExtList:
            count = 0
            for row in rows:
                url = row[0].strip()
                if url.lower().endswith('.'+ext.lower()):
                    count += 1
            if count > 0:
                fileTypes.extend([x+'['+str(count)+']' for x in self.DB.getFileTypes(ext)])
                
        #for row in rows:
        #    url = row[0].strip()
        #    for ext in fileExtList:
        #        if url.lower().endswith('.'+ext.lower()):
        #            fileTypes.extend(self.DB.getFileTypes(ext))

        return list(set(fileTypes))
        #return fileTypes

    def filterRowsByFileTypes(self, rows, fileTypes = []):
        if len(fileTypes)== 0:
            return rows
        else:
            fRows = []
            for row in rows:
                if self._isValidRow(row,fileTypes):
                    fRows.append(row)
            return fRows

    #old#def getTrackFileList(self, category, subCategory, source = 'All', fileTypes = []):
    def getTrackFileList(self, category, subCategory, source = 'All', dataTypes = []):
        fileList = []

        if source.find('HyperBrowser') > -1:
            HBGsuite = getSubtracksAsGSuite('hg19', ['Sample data', 'Chromatin catalog', category, subCategory])
            for track in HBGsuite.allTracks():
                fileList.append((track.title,True))
            return OrderedDict(fileList)

        items = self.getItems(category,subCategory)
        source = source.strip()
        sourceTool = 'None'

        for key, value in self.SOURCE.items():
            if source == value:
                sourceTool = key

        allRows = []
        i = 0
        htmlDict = {}
        for item in items:
            if not 'All' in source and item.sourceTool != sourceTool:
                continue

            try:
                rows = self.getRows(item)
            except Exception as e:
                print item
                raise e

            ##selectedRows = self.filterRowsByFileTypes(rows,fileTypes)
            selectedRows = self.filterRowsByDataTypes(rows,dataTypes)
            #allRows.extend(selectedRows)
            for row in selectedRows:
                filename = row[0].split('/')[-1]
                fileList.append((str(i) + ' - ' + filename,True))
                htmlDict[filename] = unicode(HtmlCore().link(filename, row[0]))
                #fileList.append((str(i) + ' - ' + str(HtmlCore().link(filename, row[0])),True))
                #fileList.append((str(i) + ' - ' +self.SOURCE[item.sourceTool]+' - '+ filename,True))
                #fileList.append(('< a href = "'+row[0]+'">' +filename+'</a>',True))
                i+=1

        #for row in allRows:
        #    filename = row[0].split('/')[-1]
        #    fileList.append((str(i) + ' - ' + filename+'\t'+,True))
        #    i+=1
        html = HtmlCore()
        #return html.tableFromDictionary(htmlDict)
        return OrderedDict(fileList)
    
    #Old#def getGSuite(self, category, subCategory, source = 'All', fileTypes = [], selectedFileIDs = None):
    def getGSuite(self, category, subCategory, source = 'All', dataTypes = [], filterFileSuffix=False, selectedFileIDs = None):
        if source.find('HyperBrowser') > -1:
            HBGSuite = getSubtracksAsGSuite('hg19', ['Sample data', 'Chromatin catalog', category, subCategory])
            if selectedFileIDs is not None:
                gSuite = GSuite()
                for trackTitle,selected in selectedFileIDs.iteritems():
                    if selected:
                        for track in HBGSuite.allTracks():
                            if trackTitle == track.title:
                                gSuite.addTrack(track)
                                break
                return gSuite
            else:
               return HBGSuite
        else:
            items = self.getItems(category,subCategory)
            #Old#gSuite = self.getGSuiteFromItems(items,source,fileTypes,selectedFileIDs)
            gSuite = self.getGSuiteFromItems(items,source,dataTypes,filterFileSuffix,selectedFileIDs)
            return gSuite


    def getRowsDicts(self, category, subCategory, source = 'All', dataTypes = [], selectedFileIDs = None, filterFileSuffix = False):
        if source.find('HyperBrowser') > -1:
            return
        else:
            items = self.getItems(category,subCategory)
            return self.getRowsDictsFromItems(items,source,dataTypes,selectedFileIDs,filterFileSuffix)

    def getRowsDictsFromItems(self, items, source = 'All', dataTypes = [], selectedFileIDs = None, filterFileSuffix = False):
        source = source.strip()
        sourceTool = 'None'

        for key, value in self.SOURCE.items():
            if source == value:
                sourceTool = key
        ##return source+'--'+sourceTool

        Rows = []
        for item in items:
            if not 'All' in source and item.sourceTool != sourceTool:
                continue

            cols, colListString = self.getColListString(item.sourceTable)
            try:
                rows = self.getRows(item,filterFileSuffix)
            except Exception as e:
                print item
                raise e
            Rows.extend(self.convertRowsToDicts(cols,self.filterRowsByDataTypes(rows,dataTypes)))

        return Rows

    #Old#def getGSuiteFromItems(self, items, source = 'All', fileTypes = [], selectedFileIDs = None):
    def getGSuiteFromItems(self, items, source = 'All', dataTypes = [], filterFileSuffix = False, selectedFileIDs = None):
        source = source.strip()
        sourceTool = 'None'

        gSuite = GSuite()

        for key, value in self.SOURCE.items():
            if source == value:
                sourceTool = key
        ##return source+'--'+sourceTool
        
        for item in items:
            if not 'All' in source and item.sourceTool != sourceTool:
                continue

            #attribute_col_name = self.DB.getAttributeNameFromReadableName(item.sourceTable,item.toolAttr)
            try:
                Rows = self.getRows(item,filterFileSuffix,False)
            except Exception as e:
                print item
                raise e


            #Old#rows = self.filterRowsByFileTypes(Rows,fileTypes)
            rows = self.filterRowsByDataTypes(Rows,dataTypes)
            ##rows = []
            ##if len(fileTypes)== 0:
            ##    rows = allRows
            ##else:
            ##    for row in allRows:
            ##        if self._isValidRow(row,fileTypes):
            ##            rows.append(row)

            #Pass gSuite byref (which is the default in python if you will change, not reset):
            self.appendGsuiteFromRows(gSuite,rows,item,selectedFileIDs)


        return gSuite

    #old#def getRandomGSuite(self, category, subCategory, source = 'All', fileTypes = [], count = 10, seed = 9001):
    def getRandomGSuite(self, category, subCategory, source = 'All', dataTypes = [], filterFileSuffix = False, count = 10, seed = 9001):
        #old#gSuite = self.getGSuite(category,subCategory,source,fileTypes)
        gSuite = self.getGSuite(category,subCategory,source,dataTypes,filterFileSuffix)
        
        return GSuiteUtils.getRandomGSuite(gSuite, count)
    
        #if source.find('HyperBrowser') > -1:
        #    HBGSuite = GSuiteUtils.getSubtracksAsGSuite('hg19', ['Sample data', 'Chromatin catalog', category, subCategory])
        #    return self.getRandomGSuiteFromGSuite(HBGSuite, count)
        #
        #items = self.getItems(category,subCategory)
        #source = source.strip()
        #sourceTool = 'None'
        #
        #gSuite = GSuite()
        #
        #for key, value in self.SOURCE.items():
        #    if source == value:
        #        sourceTool = key
        #
        ###countPerItem = count/len(items)
        ###if countPerItem == 0:
        ###    countPerItem =1
        #
        ##rows = self.getRandomRows(items,count,fileTypes)
        ##self.appendGsuiteFromRows(gSuite,rows,item)
        #
        #remainingRowsCount = count
        #
        #for i in range(len(items)):
        #    item = items[i]
        #    if not 'All' in source and item.sourceTool != sourceTool:
        #        continue
        #    ##if remainingRowsCount < countPerItem:
        #    ##    countPerItem = remainingRowsCount
        #    elif remainingRowsCount < 1:
        #        break
        #    rows = self.getRandomRows(item,remainingRowsCount,fileTypes)
        #
        #    #rows = self.filterRowsByFileTypes(allRows,fileTypes)
        #
        #    remainingRowsCount -= len(rows)
        #
        #    self.appendGsuiteFromRows(gSuite,rows,item)
        #
        #return gSuite


    #def getRandomGSuiteFromGSuite(self,gSuite,count = 10):
    #    trackTitles = [track.title for track in gSuite.allTracks()]
    #    selectedTrackTitles = []
    #    remainingRowsCount = count
    #    random.seed(9001)
    #    for i in range(count):
    #        if len(trackTitles) == 0:
    #            break
    #        index = random.randint(0,len(trackTitles)-1)
    #        selectedTrackTitles.append(trackTitles[index])
    #        trackTitles.pop(index)
    #    rGSuite = GSuite()
    #    for t in selectedTrackTitles:
    #        for track in gSuite.allTracks():
    #            if t == track.title:
    #                rGSuite.addTrack(track)
    #                break
    #    return rGSuite

    def getGsuiteFromRandomRows(self,count = 10):
        random.seed(9001)
        rItem = self.VOCABULARY[random.randint(0,len(self.VOCABULARY)-1)]
        rRows = self.getRandomRows(rItem,count)
        gSuite = GSuite()
        self.appendGsuiteFromRows(gSuite,rRows,rItem)
        return gSuite


    def appendGsuiteFromRows(self,gSuite,rows,item, selectedFileIDs = None):

        cols, colListString = self.getColListString(item.sourceTable)

        colListString = colListString.replace(',','\t')
        #colListString = colListString.replace('_','').lower()
        colListString = colListString.replace('"','')
        colListString = colListString.strip('\t')
        colList = colListString.split('\t')

        selectedRows = self._getSelectedRows(rows,selectedFileIDs)
        #test#print 'count = '+str(len(selectedRows))
        for count, row in enumerate(selectedRows):
            #row = rows[i]
            if row == None or len(row)<len(cols):
               continue

            url = row[0].strip()
            if self.DOWNLOAD_PROTOCOL != None:
                protocol = url.split(':')[0]
                url = url.replace(protocol+':',self.DOWNLOAD_PROTOCOL+':')

            uri = str(url)
            # from gold.gsuite.GSuiteTrack import urlparse
            # parsedUrl = urlparse.urlparse(url)
            #
            # sitename = parsedUrl.netloc
            # filepath = parsedUrl.path
            # query = parsedUrl.query
            # #sitename = url.split(':')[1].strip('/').split('/')[0]
            # ###filename = url.split('/')[-1]
            # #filepath = url.split(sitename)[1]
            # suffix = self._getGSuiteTrackSuffix(url)
            # uri = None
            # if url.startswith('ftp:'):
            #     uri = FtpGSuiteTrack.generateURI(netloc=sitename, path=filepath, suffix = suffix, query=query)
            # elif url.startswith('http:'):
            #     uri = HttpGSuiteTrack.generateURI(netloc=sitename, path=filepath, suffix = suffix, query=query)
            # elif url.startswith('https:'):
            #     uri = HttpsGSuiteTrack.generateURI(netloc=sitename, path=filepath, suffix = suffix, query=query)
            # elif url.startswith('rsync:'):
            #     uri = RsyncGSuiteTrack.generateURI(netloc=sitename, path=filepath, suffix = suffix, query=query)

            attr_val_list = []
            
            for j in range(1,len(row)):
                try:
                    if row[j] is None or unicode(row[j]).strip() == '':
                        continue
                except Exception as ex:
                    raise ValueError('Row value Error: '+str(ex))
                
                colReadableName = self.DB.getAttributeReadableNameFromName(item.sourceTable, colList[j])
                if colReadableName is None:
                    colReadableName = colList[j]
                ## some datatypes are not string, e.g. datetime, and some others contain non-printable characters, e.g. \x00
                import string
                value = filter(lambda x: x in string.printable, unidecode(unicode(row[j])))
                attr_val_list.append((colReadableName,value))
                
            try:
                gSuite.addTrack(GSuiteTrack(uri, genome='hg19', doUnquote = True, attributes=OrderedDict(attr_val_list)))
            except Exception as e:
                print str(e)

            #return gSuite

    def _getGSuiteTrackSuffix(self,url):
        return None

    def _isValidRowOfDataType(self,row,dataTypes):
        datatype = row[1].strip()
        if datatype in dataTypes:
            return True

    def _isValidRow(self,row,fileTypes):
        url = row[0].strip()
        for ft in fileTypes:
            for ext in self.DB.getFileExtensions(ft):
                if url.lower().endswith('.'+ext.lower()):
                    return True
        return False

    def getRandomTracks(self,gSuite,count = 10):
        #random.seed(9001)
        #iGSuite = GSuite()
        #
        #for track in gSuite:
        return

    def getRandomRows(self, item, count = 10, fileTypes = []):
        #rows = self.getRows(item)
        #rows = []
        #for item in items:
        #    rows.extend(self.filterRowsByFileTypes(self.getRows(item),fileTypes))
        rows = self.filterRowsByFileTypes(self.getRows(item),fileTypes)
        
        if len(rows) == 0:
            return []
        rRows = []
        random.seed(9001)
        for i in range(count):
            if len(rows) == 0:
                break
            index = random.randint(0,len(rows)-1)
            rRows.append(rows[index])
            rows.pop(index)
        return rRows

    def getAllRows(self):
        rows = []
        for item in self.VOCABULARY:
            rows.extend(self.getRows(item))
        return rows

    def getItemDataTypes(self,item):
        cols, colListString = self.getColListString(item.sourceTable)

        suffixes = getSupportedFileSuffixesForGSuite()
        WHERE = 'hb_filesuffix in ('
        for s in suffixes:
            WHERE += '"'+s+'",'
        WHERE = WHERE.rstrip(',')+')'
        if item.sourceTableFilter:
            WHERE += ' AND ' + item.sourceTableFilter + ' AND '
        else:
            WHERE += ' AND '
        
        attribute_col_name = self.DB.getAttributeNameFromReadableName(item.sourceTable,item.toolAttr)
        multi_val_rec = item.toolVal
        multi_val_list = self.DB._db.getWildCardsMatchingValues(item.sourceTable,self.DB._db.correctColumNames([attribute_col_name])[0],multi_val_rec)
        ##This commented-out section if for using regex instead of wild-cards
        ##if multi_val_rec.find('.*') > -1:
        ##    multi_val_rec = '(' + multi_val_rec.strip() + ')'
        ##else:
        ##    multi_val_rec = '(.*' + multi_val_rec + '.*)'
        ##multi_val_list = self.DB._db.getREMatchingValues(item.sourceTable,self.DB._db.correctColumNames([attribute_col_name])[0],multi_val_rec)

        WHERE += '"'+attribute_col_name  + '" in ('
        for val in multi_val_list:
            WHERE += '"' + val + '", '
        if WHERE.endswith(', '):
            WHERE = WHERE.strip(', ')
        WHERE += ')'

        query = "SELECT hb_datatype,COUNT(*) FROM "+item.sourceTable+" "
        query += "WHERE " + WHERE + " GROUP BY hb_datatype;"
        
        try:
            rows = self.DB._db.runQuery(query)
        except Exception as e:
            print multi_val_list
            print item.sourceTable
            print self.DB._db.correctColumNames([attribute_col_name])[0]
            print multi_val_rec
            raise e

        if len(rows) == 0 or rows == None:
           return [('EMPTY Result for ['+self.DB._db.correctColumNames([attribute_col_name])[0]+'] = ['+multi_val_rec+'] for Query:\n' + query,)]
        
        return rows
        
    def convertRowsToDicts(self,cols,rows):
        result = []
        for row in rows:
            if row == None or len(row)<len(cols):
               continue
            rowDict = {}
            i = 0
            for col in cols:
                rowDict[col.strip('"')] = row[i]
                i+=1
            result.append(rowDict)
        return result

    def getRows(self, item, filterFileSuffix = False, asDicts = False):

        cols, colListString = self.getColListString(item.sourceTable)

        WHERE = ''
        if filterFileSuffix:
            suffixes = getSupportedFileSuffixesForGSuite()
            WHERE = 'hb_filesuffix in ('
            for s in suffixes:
                WHERE += '"'+s+'",'
            WHERE = WHERE.rstrip(',')+') AND '
        if item.sourceTableFilter:
            WHERE += item.sourceTableFilter + ' AND '

        
        attribute_col_name = self.DB.getAttributeNameFromReadableName(item.sourceTable,item.toolAttr)

        multi_val_rec = item.toolVal
        multi_val_list = self.DB._db.getWildCardsMatchingValues(item.sourceTable,self.DB._db.correctColumNames([attribute_col_name])[0],multi_val_rec)
        ##This commented-out section if for using regex instead of wild-cards
        ##if multi_val_rec.find('.*') > -1:
        ##    multi_val_rec = '(' + multi_val_rec.strip() + ')'
        ##else:
        ##    multi_val_rec = '(.*' + multi_val_rec + '.*)'
        ##multi_val_list = self.DB._db.getREMatchingValues(item.sourceTable,self.DB._db.correctColumNames([attribute_col_name])[0],multi_val_rec)

        WHERE += '"'+attribute_col_name  + '" in ('
        for val in multi_val_list:
            WHERE += '"' + val + '", '
        if WHERE.endswith(', '):
            WHERE = WHERE.strip(', ')
        WHERE += ')'

        query = "SELECT "+colListString+" FROM "+item.sourceTable+" "
        query += "WHERE " + WHERE + "ORDER BY "+colListString+";"

        try:
            if asDicts:
                rows = self.DB._db.getRowsDicts(cols,query)
            else:
                rows = self.DB._db.runQuery(query)
        except Exception as e:
            print multi_val_list
            print item.sourceTable
            print self.DB._db.correctColumNames([attribute_col_name])[0]
            print multi_val_rec
            raise e

        if len(rows) == 0 or rows == None:
            return [('EMPTY Result for Query:\n' + query,)]

        return rows

    #def _getSelectedRows(self, rows):
    #    for row in rows:
    #        yield row

    def _getSelectedRows(cls, rows, selectedFileIDs = None):

        if selectedFileIDs is None:
            return rows
            #for row in rows:
            #    yield row
        else:
            filelist = [row[0].split('/')[-1] for row in rows]
            print filelist
            print '--------'
            print selectedFileIDs
            
            rowDict = {}
            for i, row in enumerate(rows):
                rowKey = unicode(i) + ' - ' + row[0].split('/')[-1]
                rowDict[rowKey] = row
            
            print '--------'
            print rowDict.keys()
            
            selectedRows = []
            for fileID,selected in selectedFileIDs.iteritems():
                if selected:
                    for key in rowDict.keys():
                        #if fileID.split('-')[1].strip() == key.split('-')[1].strip():
                        if fileID == key:
                            selectedRows.append(rowDict[key])
                            rowDict.pop(key)
                            break
            return selectedRows
            #for row in selectedRows:
            #    yield row

    def getColListString(self,tablename):
        cols = self.DB._db.correctColumNames\
        (self.DB._db.getTableCols(tablename))
        colListString = ''
        try:
            cols.insert(0, cols.pop(cols.index('"url"')))
        except:
            cols.insert(0, cols.pop(cols.index('"_url"')))

        cols.insert(1,cols.pop(cols.index('"hb_datatype"')))
        for col in cols:
            colListString += col + ','

        return cols,colListString.strip(',')


###############################################################################
#gsm = TrackGlobalSearchModule()
###############################
##Test (Validity of metadata):
###############################
#items = gsm.getItems('Histone modifications (get all modifications for selected cell)','iPS-18 Cells')
#print items
#db = DatabaseTrackAccessModule(isSqlite = True)
#print '"'+items[0].sourceTable+'"'
#print '"'+items[0].toolAttr+'"'
#print db.getAttributeNameFromReadableName(items[0].sourceTable,items[0].toolAttr)
###############################################################################
#print gsm.getRows(items[0])
#print gsm.getGSuite(self, category, subCategory)
#print gsm.getAllFileTypes()
