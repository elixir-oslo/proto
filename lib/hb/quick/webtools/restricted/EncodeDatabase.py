# !/software/VERSIONS/python2-2.7.6/bin/python

__author__="Sveinung and Azab"
__date__ ="$Sep 4, 2014$"
__PythonVersion__= "2.7 [MSC v.1500 32 bit (Intel)]"

import psycopg2

from collections import namedtuple
ValueWithCount = namedtuple('ValueWithCount', ('val', 'count'))

class DatabaseError(Exception):
    pass

class EncodeDatabase(object):
    def __init__(self, connStr):
        self._connStr = connStr
        self._connection = None
        self._reservedWords = None
        self.connect()
        self._generateReservedWordList()
        
    # Implementation of abstract classes

    def getValueListWithCounts(self, attribute, prevSelected):
        return self._getValueListWithCounts(attribute, prevSelected)

    #===========================================================================
    def connect(self):
        self._connection = psycopg2.connect(self._connStr)
        return True

    def disconnect(self):
        if self._connection == None:
            print 'Connection is already closed!'
            return False
        self._connection.close()
        self._connection = None
        return True
    #===========================================================================
    def _generateReservedWordList(self):
       if self._connection == None:
            print 'Error: No open db connection'
            return
       query = "select word from pg_get_keywords() where catcode != 'U';"
       self._reservedWords = [x[0] for x in self.runQuery(query)]
    #===========================================================================
    # Add "<col-name>" for column names with reserved psql words
    def correctColumNames(self,cols):
        if self._connection == None:
            print 'Error: No open db connection'
            return
        if type(cols) is list:
          for i in range(len(cols)):
              for w in self._reservedWords:
                  if cols[i].strip() == w.strip():
                     cols[i] = '"' + cols[i] + '"'
        elif type(cols) is dict:
           for k in cols.keys():
              for w in self._reservedWords:
                  if k.strip() == w.strip():
                     cols['"' + k + '"'] = cols.pop(k)

        return cols
    #===========================================================================
    def createTableFromDict(self, tableName, colsDict, pk = None):
        if self._connection == None:
            print 'Error: No open db connection'
            return

        colsDict = self.correctColumNames(colsDict)

        query = 'CREATE TABLE IF NOT EXISTS '+tableName+'('
        for k in colsDict.keys():
            colType = 'VARCHAR'
            if colsDict[k] != None:
               colType = colsDict[k]
            query += ' '.join([k,colType,','])
        if pk != None and pk in colsDict.keys():
            query += 'PRIMARY KEY('+pk+')'

        query = query.strip(',')+');'

        self.runQuery(query)

        return query
    #===========================================================================
    def createTableFromList(self, tableName, cols, pk = None):
        if self._connection == None:
            print 'Error: No open db connection'
            return

        cols = self.correctColumNames(cols)

        query = 'CREATE TABLE IF NOT EXISTS '+tableName+'('
        for col in cols:
            query += ''.join([col,' VARCHAR,'])
        if pk != None and pk in cols:
            query += 'PRIMARY KEY('+pk+')'

        query = query.strip(',')+');'

        self.runQuery(query)

        return query
    #===========================================================================
    def addColumns(self,tablename,cols):
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
    #===========================================================================
    def dropTable(self, tablename):
        query = ''.join(['DROP TABLE IF EXISTS ', tablename])
        self.runQuery(query)
        return query
    #===========================================================================
    def insertRows(self,tableName,rowDictList):
        tableCols = self.getTableCols(tableName)
        #cols = dict.keys(rowDictList[0])
        #errorCols = []
        #for col in cols:
        #    if not any(col in c for c in tableCols):
        #       errorCols.append(col)
        #if len(errorCols) > 0:
        #   print 'Class Error: '+str(len(errorCols))+' colums don''t exist'\
        #         ' in table ' + tableName
        #   print errorCols
        #   print 'cols of inserted row:'
        #   print cols
        #   print 'cols of table:'
        #   print tableCols
        #   return 1
        insert = 0
        error = 0
        for rowDict in rowDictList:
            out = self.insertRow(tableName, rowDict)

            if len(out)>0 and out[0][0].find('ERROR')>-1:
               error += 1
            else:
               insert += 1
        print str(insert) + ' rows inserted in '+tableName+'\t'\
        + str(error) + ' rows had error'
        return 0
    #===========================================================================
    def insertRow(self,tableName,rowDict):
        cols = dict.keys(rowDict)
        cols = self.correctColumNames(cols)
        values = dict.values(rowDict)
        query = 'INSERT INTO '+tableName+' ('
        for col in cols:
            query += col + ','
        query = query.strip(',') + ') VALUES ('

        for val in values:
            query += "'" + str(val).replace("'","''") + "'" +  ','
        query = query.strip(',') + ');'

        return self.runQuery(query)
    #===========================================================================
    def getTableCols(self, tableName,withDataType = False, ordered = False):
        query = "select column_name,data_type from information_schema.columns "\
                "WHERE table_name = '" + tableName + "'"
        if ordered:
           query += " order by column_name;"
        else:
           query += ";"
        #if len(where) > 0:
        #    query += ''.join(', ', where, ';')
        #else:
        #    query += ';'

        result = self.runQuery(query)
        if result == None:
            return None
        if withDataType:
           return result
        cols = []
        for el in result:
            cols.append(el[0])
        return cols
    #===========================================================================
    def getColGroup(self, tablename, col, where = None, ordered = False):
        col = self.correctColumNames([col])[0]
        if col.strip() != '':
            return
        query = ''.join(['select ',col,', count(*) from ',tablename])

        if where == None or where.strip() == '':
           query += ' group by '+col
        else:
           query += ' '.join([' where',where,'group by',col])

        if ordered:
           query += ' order by '+col+';'
        else:
           query += ';'

        try:
            return self.runQuery(query)
        except:
            passs

    def _getValueListWithCounts(self, col, prevSelected):
        WHERE = ''

        for prevCol, prevVal in prevSelected.iteritems():
            prevCol = self.correctColumNames([prevCol])[0]
            WHERE += prevCol + " LIKE '" + prevVal + "' AND "

        if WHERE.endswith('AND '):
           WHERE = WHERE.strip('AND ')

        rows = self.getColGroup('file_encode', col,\
                                where = WHERE, ordered = True)

        return [ValueWithCount(v,c) for v,c in rows]
    #===========================================================================
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
    #===========================================================================
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

    #===========================================================================
    def runQuery(self, query, returnrows = False):
        cr = self._connection.cursor()
        self._connection.set_isolation_level(0)
        try:
            rows = []
            cr.execute(query)
            try:
               rows= cr.fetchall()
            except:
               pass
            return rows
        except psycopg2.Error as e:
        #    raise DatabaseError('Error for query "%s":\n%s' % (query, e.pgerror))
            print 'Query: '+query
            return [(e.pgerror + '\n'+ 'Query: \n'+query,None)]
        cr.close()
################################################################################



#execfile('CommonVocabularyParser.py')
#voc = CommonVocabularyParser('cv.ra')
#cols = voc.findAllKeys()
#terms = voc.getAllTerms()
#print terms[0]

db = EncodeDatabase("host='localhost' dbname='abdulara' user='abdulara' password='144144'")
##db.connect()
#======================================================
#Manual unit tests:
#======================================================
#print db.createTableFromList('tab',cols, pk = 'term')
#print db.insertRow('tab',terms[0])
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
#db.dropTable('fileencode')
#======================================================
#print db.getColGroup('file_encode','lab')

##db.disconnect()
