from quick.webtools.imports.TrackSearchTool import TrackSearchTool

class Epigenome2ImputedTrackSearchTool(TrackSearchTool):
#    DATABASE_TRACK_ACCESS_MODULE_CLS = EncodeDatabaseTrackAccessModule
    def __new__(cls, *args, **kwArgs):
        return TrackSearchTool.__new__(Epigenome2ImputedTrackSearchTool, *args, **kwArgs)

    @staticmethod
    def getToolName():
        return "Roadmap Epigenomics (Imputed)"

    @classmethod
    def _getTableName(cls):
        return 'file_epigenome2'
    
    @classmethod
    def _getGlobalSQLFilter(cls):
        #return
        return "url LIKE '%consolidatedImputed%'"

    @classmethod
    def _getClassAttributes(cls, db):
        attributes = []

        ##colList = db._db.getTableCols(cls.TABLE_NAME)
        ##for col in colList:
        ##    attributes.append(col)
        ##attributes.remove('url')
        attributes = ['hb_filesuffix','EID','MARK','MARK CLASS','TYPE~~','ANATOMY~~','GROUP~~',\
                'Epigenome name (from EDACC Release 9 directory)',\
                'Standardized Epigenome name~~','E-Mnemonic']

        return sorted(attributes)

    @classmethod
    def getColListString(cls):
        ##cols = cls.DB._db.correctColumNames\
        ##(cls.DB._db.getTableCols(cls.TABLE_NAME))
        ##cols.insert(0, cols.pop(cols.index('"url"')))
        colListString = ''
        cols = ['"url"','"hb_datatype"','"hb_filesuffix"','"EID"','"MARK"','"MARK CLASS"','"TYPE~~"','"ANATOMY~~"','"GROUP~~"',\
                '"Epigenome name (from EDACC Release 9 directory)"',\
                '"Standardized Epigenome name~~"','"E-Mnemonic"']
        for col in cols:
            colListString += col+','
        
        return cols,colListString.strip(',')
