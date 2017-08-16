import collections
import os
import imp
from quick.trackaccess.EncodeDatabase import EncodeDatabase
##file,filename,data = imp.find_module('EncodeDatabase',\
##                                     ['/cluster/home/abdulara/T1'])
##mod = imp.load_module('EncodeDatabase', file, filename, data)
###############################################################################
class CommonVocabularyParser(object):
    def __init__(self, cvFn, db_cnstr, fieldTable, fileIndexTable):
        self._cvFn = cvFn
        self._fieldTable = fieldTable
        self._fileIndexTable = fileIndexTable
        self._allTerms = self._parseFile()
        self._db = mod.EncodeDatabase(db_cnstr)
        self._db.connect()
        
        self._cols = {}
        self._rowList = []
        
    #===========================================================================
    def _parseFile(self):
        with open(self._cvFn) as f:
            termBlocks = []
            for block in f.read().split('\n\n'):
                if 'type typeOfTerm' in block:
                    termBlocks.append(block.split('\n'))

            #termBlocks = [block.split('\n') for block in f.read().split('\n\n'$

            allTerms = []
            for termBlock in termBlocks:
                terms = collections.OrderedDict()
                for termLine in termBlock:
                    words = termLine.split(' ')
                    if words[0] != '' and not words[0].startswith('#'):
                        terms[ words[0] ] = ' '.join(words[1:])
                allTerms.append(terms)

        return allTerms
    #===========================================================================
    def getAllTerms(self):
        return self._allTerms
    #===========================================================================
    def findAllKeys(self):
        uniqueKeys = collections.OrderedDict()
        for term in self._allTerms:
            uniqueKeys.update(term)
        #return sorted(dict.fromkeys(uniqueKeys))
        return dict.keys(uniqueKeys)
    #===========================================================================
    def makeFieldTable(self):
        cols = dict([[x,None] for x in self.findAllKeys()])
        #cols.extend(['_datatype','_searchable'])
        cols.update({'_datatype':None})        
        cols.update({'_searchable':'BOOLEAN'})
        self._db.runQuery(''.join(['DROP TABLE ', self._fieldTable]))
        self._db.createTableFromDict(self._fieldTable,cols, pk = 'term')
        
        for term in self.getAllTerms():
            term.update({'term':term['term'].lower()})
            term.update({'_datatype':'VARCHAR'})
            term.update({'_searchable':'true'})
            self._db.insertRow(self._fieldTable,term)
        
        with open('field_table_update.txt','r') as f:
           lines = f.readlines()
        for l in lines:
           self._db.runQuery(l)   
    #===========================================================================   
    def _generateDict(self,fields):
        dictionary = {}
        for f in fields:
            dictionary.update({f:None})
        return dictionary
    #===========================================================================
    def getAllFileTerms(self):
        cols = []
        query = ''.join(['SELECT term FROM ', self._fieldTable, ';'])
        colTuples = self._db.runQuery(query)
        for t in colTuples:
            cols.append(t[0])
        return cols
    #===========================================================================
    def makeTrackTableENCODE(self, indexFile):
        self._db.dropTable(self._fileIndexTable)
        cols = self.getAllFileTerms()
        cols.insert(0,'URL')
        self._db.createTableFromList(self._fileIndexTable,cols, pk = 'URL')
        f = open(indexFile,'r')
        lines = f.readlines()
        f.close()
        
        rowList = []
        row = None
        i = 0
        for l in lines:
            if len(l.strip()) == 0:
                continue
            try:        
                rowDict = self._generateDict(cols)
                if l.find('#') >= 0:
                    rowDict.update({'URL':l.split('#')[0].strip()})
                    rowList.append(rowDict)
                    i +=1
                    continue
                rowDict.update({'URL':l.split('\t')[0]})
                row = l.split('\t')[1].split(';')
                for element in row:
                    el = element.strip().split('=')
                    rowDict.update({el[0]:el[1]})
    
                #self._db.insertRow(self._fileIndexTable,rowDict)
                rowList.append(rowDict)
                #print i
                i +=1
            except IndexError as e:
                print 'Error in ['+indexFile+'] Line '+str(i)+': '+str(e)
                print 'Line Text: '+l
                #return dataList
                
        self._db.insertRows(self._fileIndexTable,rowList)
    #===========================================================================
    
    def addTrackIndexData_Independent(self, indexFile, isUCSC = False):
        ENCODE_UCSC_URL='ftp://hgdownload.cse.ucsc.edu/goldenPath/hg19/encodeDCC'
        urlParent = ''
        source = 'Ensembl'
        if isUCSC:
            source = 'UCSC'
            urlParent = '/'.join([ENCODE_UCSC_URL,\
                                os.path.abspath(indexFile).split('/')[-2],''])
        
        self._cols.update({'_source':None})
        self._cols.update({'_url':None})
        
        with open(indexFile,'r') as f:
             lines = f.readlines()
        
               
        #rowList = []
        row = None
        i = 0
        for l in lines:
            if len(l.strip()) == 0:
                continue
            try:        
                rowDict = {}
                rowDict.update({'_source':source})
                if l.find('#') >= 0:
                    rowDict.update({'_url':urlParent + l.split('#')[0].strip()})
                    self._rowList.append(rowDict)
                    i +=1
                    continue
                rowDict.update({'_url':urlParent + l.split('\t')[0]})
                row = l.split('\t')[1].split(';')
                
                for element in row:
                    el = element.strip().split('=')
                    el_name = el[0].strip().lower()
                    if el_name == 'size':
                       rowDict.update({el_name:self._db.getNumeric(el[1])})
                       self._cols.update({el_name:'DECIMAL(20,2)'})
                    elif el_name in ['datesubmitted',\
                                                   'dateresubmitted']:
                       rowDict.update({el_name:el[1]})
                       self._cols.update({el_name:'DATE'})
                    else:      
                       rowDict.update({el_name:el[1]})
                       self._cols.update({el_name:None})
    
                self._rowList.append(rowDict)
                #print i
                i +=1
            except IndexError as e:
                print 'Error in ['+indexFile+'] Line '+str(i)+': '+str(e)
                print 'Line Text: '+l
                #return rowList
        #print str(len(cols.keys())) + ' added cols:' 
        #print cols.keys()               
        #return rowList, cols
    
    #def getUCSCTrackURL(self, filename, )
    #============================================================================
    def makeFileIndexTable_Independent(self):            
        #Add remaining cols to the field table:
        cols = [x[0] for x in self._db.getColGroup(self._fieldTable,'term')]
        remaining = [{'term':x,'_datatype':'VARCHAR','_searchable':'true'}\
         for x in self._cols if not x in cols]
        self._db.insertRows(self._fieldTable,remaining)
        
        #Now create the file index table:
        self._db.dropTable(self._fileIndexTable)
        #self._db.createTableFromList(self._fileIndexTable,cols.keys(), pk = 'URL')
        self._db.createTableFromDict(self._fileIndexTable,self._cols, pk = 'URL')
        #print cols.keys()
        #print str(len(cols.keys())) + 'colums'
        self._db.insertRows(self._fileIndexTable,self._rowList)
        
###############################################################################

#v = CommonVocabularyParser('cv.ra',\
#                           "host='localhost' dbname='abdulara' user='abdulara'"\
#                           "password='144144'",\
#                           'field','file_encode')
#print v.findAllKeys()
#v.makeFieldTable()
#print v.getAllFileTerms()

#cols = v.getAllFileTerms()
#cols.insert(0,'URL')
#v._db.createTableFromList('file_encode',cols, pk = 'URL')

#v.addTrackIndexData_Independent('ENCODE/files.txt')
#v.makeTrackTable_Independent()

