# !/software/VERSIONS/python2-2.7.6/bin/python

__author__="Azab and Sveinung"
__date__ ="$Sep 4, 2014$"
__PythonVersion__= "2.7 [MSC v.1500 32 bit (Intel)]"

import psycopg2
import sqlite3

import re
from collections import namedtuple

from quick.trackaccess.TrackAccessModule import TrackAccessModule
from config.Config import HB_SOURCE_DATA_BASE_DIR

ValueWithCount = namedtuple('ValueWithCount', ('val', 'count'))
DBMS_LIST = ['psql','sqlite']

class DatabaseError(Exception):
    pass

class DatabaseTrackAccessModule(TrackAccessModule):
    
    def __init__(self, isSqlite = False,raiseDBErrors = True):
        if not isSqlite:
            self._db = DatabaseAdapter(host='localhost', database='abc',
                                       user='def', password='ghi') # To be filled out
        else:
            self._db = DatabaseAdapter(db_file = HB_SOURCE_DATA_BASE_DIR + '/trackaccess/imports.db')
            
        self._db.raiseDBErrors = raiseDBErrors
    
    def createLastUpdateTable(self):
        self._db.dropTable('last_update')
        self._db.createTableFromList('Last_update',['table_name','update_date'], pk = 'table_name')
        rows = []
        rows.append({'table_name':'file_cgatlas','update_date':None})
        rows.append({'table_name':'file_encode','update_date':None})
        rows.append({'table_name':'file_fantom5','update_date':None})
        rows.append({'table_name':'file_epigenome','update_date':None})
        rows.append({'table_name':'file_epigenome2','update_date':None})
        rows.append({'table_name':'file_ebihub','update_date':None})
        rows.append({'table_name':'file_icgc','update_date':None})
        rows.append({'table_name':'file_gwas','update_date':None})
        self._db.insertRows('Last_update',rows)
        
    def createMetadataTable(self):
        self._db.createTableFromList('file_col_metadata',['col_readable_name','col_name',
                                                'table_name','col_description',
                                                'col_val'],
                                                pk = ['table_name','col_name','col_val'])
    def createDataTypeTable(self):
        self._db.dropTable('data_type')
        self._db.createTableFromList('data_type',['ID','type_name','Encode','Epigenome2','ICGC','CGAtlas','FANTOM5','GWAS','EBIHub']\
                                     , pk = 'type_name')
        rows = []
        f = open(HB_SOURCE_DATA_BASE_DIR + '/trackaccess/data_type.tsv')
        lines = f.readlines()
        f.close()
        for line in lines:
            if line.startswith('#'):
                continue
            type_name = line.split('\t')[0]
            extensions = line.split('\t')[1:]
            #if extensions.strip() == '.':
            #    file_name_content = line.split('\t')[2]
            #else:
            #    file_name_content = ''
            rows.append({'type_name':type_name,'Encode':extensions[0],'Epigenome2':extensions[1],'ICGC':extensions[2],\
                         'CGAtlas':extensions[3],'FANTOM5':extensions[4],'GWAS':extensions[5],'EBIHub':extensions[6]})
        self._db.insertRows('data_type',rows)
        
    def createFileTypeTable(self):
        self._db.dropTable('file_type')
        self._db.createTableFromList('file_type',['type_name','extensions'], pk = 'type_name')
        rows = []
        f = open('file_type.tsv')
        lines = f.readlines()
        f.close()
        for line in lines:
            if line.startswith('#'):
                continue
            type_name = line.split('\t')[0]
            extensions = line.split('\t')[1]
            #if extensions.strip() == '.':
            #    file_name_content = line.split('\t')[2]
            #else:
            #    file_name_content = ''
            rows.append({'type_name':type_name,'extensions':extensions})
        self._db.insertRows('file_type',rows)
        
    def getValueListWithCounts(self, tablename, attribute, prevSelected):
        WHERE = ''

        for prevCol, prevVal in prevSelected.iteritems():
            prevCol = self._db.correctColumNames([prevCol])[0]
            
            if type(prevVal) is list:
                WHERE += prevCol + ' in ('
                for val in prevVal:
                    WHERE += '"' + val + '", '
                if WHERE.endswith(', '):
                    WHERE = WHERE.strip(', ')
                WHERE += ') AND '
            else:
                WHERE += prevCol + " LIKE '" + prevVal + "' AND "
    
        if WHERE.endswith('AND '):
            WHERE = WHERE.strip('AND ')

        rows = self._db.getColGroup(tablename, attribute,\
                                    where=WHERE, ordered = True)
        return [ValueWithCount(v,c) for v,c in rows]
    
    def getAttributesDetails(self,tablename,cols=None):
        query = "SELECT col_name, col_readable_name, col_description FROM file_col_metadata WHERE table_name LIKE '"+tablename+"' AND col_val = '.';"
        output = self._db.runQuery(query)
        if len(output) == 0:
            return None
        resultFull = {}
        for name,rname,desc in output:
                resultFull[name] = rname,desc
        if cols == None:
            result = resultFull
        elif type(cols) is list:
            result = {}
            for col in cols:
                result[col] = resultFull[col]
        return result    
    
    def getAttributeNameFromReadableName(self, tablename, rName):
        query = "SELECT col_name FROM file_col_metadata WHERE table_name LIKE '" + tablename + "' AND col_val = '.' AND col_readable_name LIKE '" + rName + "';"
        result = self._db.runQuery(query)
        if len(result) > 0:
            return result[0][0]
        else:
            raise DatabaseError('Attribute readable name "%s" has no associated column name\nQuery:%s' % (rName,query))
    def getAttributeReadableNameFromName(self, tablename, name):
        query = "SELECT col_readable_name FROM file_col_metadata WHERE table_name LIKE '" + tablename + "' AND col_val = '.' AND col_name LIKE '" + name + "';"
        result = self._db.runQuery(query)
        if len(result) > 0:
            return result[0][0]
        else:
            return    
    def getAttributeValuesDetails(self,tablename,cols=None, addColNameToDescription = False):
        query = "SELECT col_name, col_val, col_readable_name, col_description FROM file_col_metadata WHERE table_name LIKE '"+tablename+"' AND col_val != '.';"
        output = self._db.runQuery(query)
        if len(output) == 0:
            return None
        resultFull = {}
        for name,val,rname,desc in output:
                if not addColNameToDescription:
                    resultFull[(name,val)] = rname,desc
                else:
                    resultFull[(name,val)] = val.upper() +' - '+ rname,desc
        if cols == None:
            result = resultFull
        elif type(cols) is dict:
            '''
            Selecting specific values of attributes in the form: {<attr_val>:<attr_name>}.
            The attr_val is set as the key in the dict since attr_name can be repeated
            for different values.
            '''
            result = {}
            for colkey in cols.keys():
                '''Here put the name before the value'''
                result[cols[colkey],colkey] = resultFull[cols[colkey],colkey]
        return result
    
    def getAllFileTypes(self):
        query = "SELECT * FROM file_type;"
        output = self._db.runQuery(query)
        if len(output) == 0:
            return None
        result = {}
        for name,ext in output:
            ext = ext.replace('\n','')
            extList = ext.split(',')
            result[name] = extList
        return result
    
    
    def getDataType(self,filename,database):
        from fnmatch import fnmatch
        #query = "SELECT type_name FROM file_type WHERE extensions LIKE '%"+extension+"%';"
        query = "SELECT type_name,"+database+" FROM data_type;"
        output = self._db.runQuery(query)
        datatype = None
        for type_name,exts in output:
            #exts = exts.replace('\n','')
            if exts.strip() == '.':
                continue
            for ext in exts.lower().split(','):
                if not ext.startswith('*'):
                    ext = '*'+ext
                if fnmatch(filename.lower(),ext):
                #if filename.lower().endswith(ext):
                    return type_name
        return 'Others'
    
    def getTableDataTypes(self,tablename,WHERE = None):
        if WHERE:
            query = "SELECT data_type.type_name, count(*) FROM data_type,"+ tablename +" WHERE data_type.type_name = "+ tablename +".hb_datatype AND "+ WHERE +" GROUP BY data_type.type_name;"
        else:
            query = "SELECT data_type.type_name, count(*) FROM data_type,"+ tablename +" WHERE data_type.type_name = "+ tablename +".hb_datatype GROUP BY data_type.type_name;"
        
        output = self._db.runQuery(query)
        if output[0][0].find('Error') > -1:
            return output[0][0]
        datatypes = []
        for type_name,count in output:
            datatypes.append((type_name,int(count)))
        
        return datatypes
    
    def getFileTypes(self,extension):
        #query = "SELECT type_name FROM file_type WHERE extensions LIKE '%"+extension+"%';"
        query = "SELECT * FROM file_type;"
        output = self._db.runQuery(query)
        types = []
        for name,exts in output:
            exts = exts.replace('\n','')
            if extension.lower() in exts.lower().split(','):
                types.append(name)
        if len(types) == 0:
            return None
        return types
        #return [el[0] for el in output]
    
    def getAllFileExtensions(self):
        query = "SELECT extensions FROM file_type;"
        output = self._db.runQuery(query)
        if len(output) == 0:
            return None
        result = [el[0] for el in output]
        result = ','.join(result).replace('\n','')
        return result.split(',')
    
    def getFileExtensions(self,fileType):
        query = "SELECT extensions FROM file_type WHERE type_name LIKE '"+fileType+"';"
        output = self._db.runQuery(query)
        if len(output) == 0:
            return None
        result = output[0][0].replace('\n','')
        return result.split(',')
    
    def updateLastUpdateTable(self,table_name):
        from datetime import datetime
        query = "UPDATE last_update SET update_date = datetime('now') WHERE table_name LIKE '"+table_name+"';"
        self._db.runQuery(query)
        print 'Update time set to\t'+ str(datetime.now())
        return query
        
class EncodeDatabaseTrackAccessModule(DatabaseTrackAccessModule):
    TABLE_NAME = 'file_encode'

class DatabaseAdapter(object):
    def __init__(self, **connKwArgs):
        self._connKwArgs = connKwArgs
        self.isSqlite = False
        try:
            self._connKwArgs['db_file']
            self.isSqlite = True
        except:
            pass
        self._connection = None
        self.connect()
        self._reservedWords = None
        self._generateReservedWordList()
        self.raiseDBErrors = True

    def connect(self):
        if self.isSqlite:
            self._connection = sqlite3.connect(self._connKwArgs['db_file'])
            #To use regular strings instead of unicode strings which is the default:
            # self._connection.text_factory = sqlite3.OptimizedUnicode
            self._connection.text_factory = lambda x: unicode(x, "utf8", "ignore")

        else:
            self._connection = psycopg2.connect(**self._connKwArgs)
        return True

    def disconnect(self):
        if self._connection == None:
            print 'Connection is already closed!'
            return False
        self._connection.close()
        self._connection = None
        return True

    def _generateReservedWordList(self):#For psql only
        if self.isSqlite:
            return
        if self._connection == None:
            print 'Error: No open db connection'
            return
        query = "SELECT word FROM pg_get_keywords() WHERE catcode != 'U';"
        self._reservedWords = [x[0] for x in self.runQuery(query)]

    # Add "<col-name>" for column names with reserved psql words
    def correctColumNames(self,cols):
        #print cols
        if self._connection == None:
            print 'Error: No open db connection'
            return
        #print cols
        if None in cols:
            cols.pop(cols.index(None))
        if type(cols) is list:
            for i in range(len(cols)):
                  #for w in self._reservedWords:
                  #    if cols[i].strip() == w.strip():
                         cols[i] = '"' + cols[i] + '"'
        elif type(cols) is dict:
            for k in cols.keys():
                  #for w in self._reservedWords:
                  #    if k.strip() == w.strip():
                         cols['"' + k + '"'] = cols.pop(k)
        

        return cols

    def createTableFromDict(self, tableName, colsDict, pk = []):
        if not type(pk) == list:
            pk = [pk]#In case the pk is a string
        if self._connection == None:
            print 'Error: No open db connection'
            return

        colsDict = self.correctColumNames(colsDict)
        pk = self.correctColumNames(pk)
        
        query = 'CREATE TABLE IF NOT EXISTS '+tableName+'('
        for k in colsDict.keys():
            colType = 'VARCHAR'
            #if self.isSqlite:
            #    colType = 'TEXT'
            if colsDict[k] != None:
               colType = colsDict[k]
            query += ' '.join([k,colType,','])
        
        if not set(pk).issubset(set(colsDict.keys())):
            print 'WARNING: Primary key creation failed for table: '+tableName
            print 'Primary key('+str(pk)+') is not a subset of the table columns'
        elif len(pk) > 0 and set(pk).issubset(set(colsDict.keys())):
            query += 'PRIMARY KEY('+','.join(pk)+')'

        query = query.strip(',')+');'

        self.runQuery(query)

        return query

    def createTableFromList(self, tableName, cols, pk = []):
        colsDict = {}
        for col in cols:
            colsDict[col] = 'VARCHAR'
            #if self.isSqlite:
            #    colsDict[col] = 'TEXT'
        return self.createTableFromDict(tableName,colsDict,pk)
        
    def getWildCardsMatchingValues(self, table_name, col_name, wc_formula):
        from fnmatch import fnmatch
        query = "SELECT " + col_name + ", count(*) FROM " + table_name + " WHERE " + col_name + " IS NOT NULL group by " + col_name + ";"
        rows = self.runQuery(query)
        List = []
        import unicodedata
        for row in rows:
            '''Here, we ignore the case'''
            #print row[0].upper(),wc_formula.upper()
            val = row[0]
            if isinstance(row[0], unicode):
                val = unicodedata.normalize("NFKD", row[0])
            if fnmatch(val.upper(),wc_formula.upper()) and not row[0] in List:
                List.append(row[0])
        # if len(List) == 0:
        #     raise DatabaseError('Error for query "%s":\nreturned zero matching rows for the formula: %s' % (query,wc_formula))
        return List
    def getREMatchingValues(self, table_name, col_name, re_formula):
        query = "SELECT " + col_name + " FROM " + table_name + " WHERE " + col_name + " IS NOT NULL;"
        rows = self.runQuery(query)
        List = []
        for row in rows:
            '''Here, we ignore the case'''
            if re.match(re_formula.upper(),row[0].upper()) != None and not row[0] in List:
                List.append(row[0])
        return List
    
    def addColumns(self,tablename,cols):
        if self.isSqlite:
            query = "ALTER TABLE "+tablename+" ADD "
            addList = []
            if type(cols) is list:
                for col in cols:
                    addList.append(col+ ' VARCHAR;')
            elif type(cols) is dict:
                for k in cols.keys():
                    colType = 'VARCHAR'
                    if colsDict[k] != None:
                       colType = colsDict[k]
                    addList.append(' '.join([k,colType,';']))
            for add in addList:
                self.runQuery(query + add)
            return query
        
        query = "ALTER TABLE "+tablename+" ADD ("
        if type(cols) is list:
           for col in cols:
               query += ''.join([col,' VARCHAR,'])
        elif type(cols) is dict:
           for k in cols.keys():
               colType = 'VARCHAR'
               if colsDict[k] != None:
                  colType = colsDict[k]
               query += ' '.join([k,colType,','])

        query = query.strip(',')+');'
        self.runQuery(query)

        return query

    def dropTable(self, tablename):
        query = ''.join(['DROP TABLE IF EXISTS ', tablename])
        self.runQuery(query)
        return query

    def deleteRows(self, tablename, where = None):
        query = "DELETE FROM "+tablename
        if where != None:
            query += " WHERE "+where
        query += ";"
        self.runQuery(query)
        return query
    
    def insertRows(self,tableName,rowDictList):
        if len(rowDictList) == 0:
            print 'No rows inserted in '+tableName
            return 0
        from progressbar import ProgressBar
        pbar = ProgressBar()
        tableCols = self.getTableCols(tableName)
        
        insert = 0
        error = 0
        for rowDict in pbar(rowDictList):
            out = self.insertRow(tableName, rowDict)

            if len(out)>0 and out[0][0].find('Error')>-1:
               error += 1
            else:
               insert += 1
        print str(insert) + ' rows inserted in '+tableName+'\t'\
        + str(error) + ' rows had errors'
        return 0

    def insertRow(self,tableName,rowDict):
        cols = dict.keys(rowDict)
        cols = self.correctColumNames(cols)
        values = dict.values(rowDict)
        query = 'INSERT INTO '+tableName+' ('
        for col in cols:
            query += col + ','
        query = query.strip(',') + ') VALUES ('

        for val in values:
            if val is None:
                query += "NULL,"
            else:
                query += "'" + str(val).replace("'","''") + "'" +  ','
        query = query.strip(',') + ');'

        return self.runQuery(query)

    def getTableCols(self, tableName,withDataType = False, ordered = False):
        query = "SELECT column_name,data_type FROM information_schema.columns "\
                "WHERE table_name = '" + tableName + "'"
        if ordered:
           query += " order by column_name;"
        else:
           query += ";"
        if self.isSqlite:
            query = "PRAGMA table_info("+tableName+");"
        #if len(where) > 0:
        #    query += ''.join(', ', where, ';')
        #else:
        #    query += ';'

        result = self.runQuery(query)
        
        if result == None:
            return None
        if self.isSqlite:
            result = [(str(x[1]),str(x[2])) for x in result]
            if ordered:
                result.sort()
        if withDataType:
            #result.sort(key=lambda x: x[1])
            return result
        cols = []
        for el in result:
            cols.append(el[0])
        return cols

    def getColGroup(self, tablename, col, where = None, ordered = False):
        col = self.correctColumNames([col])[0]
        
        query = ''.join(['select ',col,' , count(*) from ',tablename])

        if where == None or where.strip() == '':
           query += ' group by ' + col 
        else:
           query += ' '.join([' where ',where,'group by ',col])

        if ordered:
           query += ' order by '+col+';'
        else:
           query += ';'

        return self.runQuery(query)

    def getSizeAbbrev(self,strVal):
        try:
           val = float(strVal)
        except:
           return strVal
        suff1 = {1e3:'K',1e6:'M',1e9:'G',1e12:'T',1e15:'Y',1:''}
        suff2 = {1e-9:'n',1e-6:'u',1e-3:'m',1:''}

        dev =1
        if val>1:
           for x in suff1.keys():
               if val > (x/10):
                  dev = x
           return ("%.2f" % (val/dev))+suff1[dev]
        else:
           for x in suff2.keys():
               if val > x:
                  dev = x
           return ("%.2f" % (val/dev))+suff2[dev]
        return val

    def getNumeric(self,strVal):
        suffixes = {'n':1e-9,'u':1e-6,'m':1e-3,'K':1e3,'M':1e6,'G':1e9,\
                    'T':1e12,'Y':1e15}
        try:
           return float(strVal)
        except:
           #val = filter(lambda x: x.isdigit(), strVal)
           suff = strVal[-1]
           try:
               val = float(strVal[:-1])
           except:
               return float(filter(lambda x: x.isdigit(), strVal+'0'))
           if any(suff == s for s in suffixes.keys()):
              return val * suffixes[suff]
           else:
              return float(filter(lambda x: x.isdigit(), strVal+'0'))

    def getRowsDicts(self,cols,query):
        rows = self.runQuery(query)
        result = []
        for row in rows:
            if row == None or len(row)<len(cols):
               continue
            rowDict = {}
            i = 0
            for col in cols:
                rowDict[col] = row[i]
                i+=1
            result.append(rowDict)
        return result
    
    def runQuery(self, query):
        cr = self._connection.cursor()
        if not self.isSqlite:
            self._connection.set_isolation_level(0)
        try:
            rows = []
            cr.execute(query)
            try:
               rows= cr.fetchall()
            except:
               pass
            self._connection.commit()
            return rows
        except (sqlite3.Error,psycopg2.Error) as e:
            
            if self.isSqlite:
                err = e.args[0]
            else:
                err = e.pgerror    
            
            if self.raiseDBErrors:
                raise DatabaseError('Error for query "%s":\n%s' % (query, err))
            else:
                print err
                print 'Query: '+query
                print '-'*30
                return [(err + '\n'+ 'Error query: \n'+query,None)]
        cr.close()


#execfile('CommonVocabularyParser.py')
#voc = CommonVocabularyParser('cv.ra')
#cols = voc.findAllKeys()
#terms = voc.getAllTerms()
#print terms[0]

#db = DatabaseAdapter("host='localhost' dbname='abdulara' user='abdulara' password='144144'")
##db.connect()
#======================================================
#Manual unit tests:
#======================================================
#print db.createTableFromList('tab', cols, pk = 'term')
#print db.insertRow('tab', terms[0])
#print db.getTableCols('file_encode')
#------------------------------------------------------
#rows = db.runQuery('select term from tab;',True)
#for r in rows:
#    print r[0]
#------------------------------------------------------
#cols = ['case']
#cols = ['name','case','id','cast']
#cols = db.correctColumNames(cols)
#print cols
#------------------------------------------------------
#print db.getSizeAbbrev(0.00000120650)
#------------------------------------------------------
#colList = db.getTableCols('file_encode', ordered = True)
#ATTRIBUTES = []
#for col in colList:
#   searchable = db.runQuery("select term,_searchable,_datatype from field where term = '"+col+"';")
#   print searchable
#    if str(searchable[0][0]) == 't':
#      ATTRIBUTES.append(col)
#print ATTRIBUTES
#======================================================
#db.dropTable('file_encode')
#======================================================
#print db.getColGroup('file_encode','lab')
#======================================================
# db = DatabaseTrackAccessModule(True)
############################Database Tests########################################
#print db._db.dropTable('tab')
#print db._db.createTableFromList('tab', ['a1','b1','c1'], pk = 'a1')
#print db._db.getColGroup('tab','b1')
#print db._db.addColumns('tab',['f1','g1'])
#print db._db.getTableCols('file_epigenome2',ordered = True)
#print db._db.insertRow('tab',{'a1':'12','b1':2,'c1':3})
#db._db.insertRows('tab',[{'a1':'2','b1':2,'c1':3},{'a1':'3','b1':2,'c1':3},{'a1':'4','b1':2,'c1':3}])
##########################################################################################
#print db.getAllFileTypes()
#print db.getFileTypes('bam')
#print db.getAllFileExtensions()
#print db.getDataType('xxx.gz')
#print db.getAttributesDetails('file_cgatlas')
#print db.getAttributesDetails('file_cgatlas',['cancertype','centername'])
#print db.getAttributeValuesDetails('file_cgatlas')
#print db.getAttributeValuesDetails('file_cgatlas',{'acc':'cancertype','blca':'cancertype','brca':'cancertype'})
#print db.getAttributesDetails('file_fantom5',['Comment [sequence_raw_file]','Parameter [run_name]','Protocol REF__2__'])
#print db.getValueListWithCounts('file_encode','antibody',{'cell':['RCC_7860','BC_Small_Intestine_01-11002','Myometr','Dnd41']})
#print db.getAttributeNameFromReadableName('file_gwas','CNV')
#print db.getAttributeReadableNameFromName('file_encode','tablename')
#print db.getAttributeNameFromReadableName('file_epigenome2','%COLOR%')
#print db.getAttributeReadableNameFromName('file_epigenome2','color~~')
#print db._db.getREMatchingValues('file_encode','tablename','(wgEncodeBroadHistone.*H3k04me1)')
#print db._db.getREMatchingValues('file_encode','tablename','(.*H3k0?4me1)')
#print db._db.getREMatchingValues('file_epigenome','"experiment"','(.*Chromatin_Accessibility.*)')
#print len(db._db.getREMatchingValues('file_encode','tablename','(.*H3k0?4me1.*)'))
#print db._db.getREMatchingValues('file_encode','cell','(ag0.*)')##Returns an empty list
#print db._db.getWildCardsMatchingValues('file_encode','tablename','wgEncode????Histone*H3k04me1*')
#print db._db.getWildCardsMatchingValues('file_epigenome2','"Standardized Epigenome name~~"','Primary Natural Killer cells from peripheral*')
##db.disconnect()
