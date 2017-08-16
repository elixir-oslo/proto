from quick.webtools.imports.TrackSearchTool import TrackSearchTool

class Epigenome2TrackSearchTool(TrackSearchTool):
#    DATABASE_TRACK_ACCESS_MODULE_CLS = EncodeDatabaseTrackAccessModule
    def __new__(cls, *args, **kwArgs):
        return TrackSearchTool.__new__(Epigenome2TrackSearchTool, *args, **kwArgs)

    @staticmethod
    def getToolName():
        return "Roadmap Epigenomics"

    @classmethod
    def _getTableName(cls):
        return 'file_epigenome2'

    @classmethod
    def _getGlobalSQLFilter(cls):
        #return
        return "NOT url LIKE '%consolidatedImputed%'"
    
    @classmethod
    def _getClassAttributes(cls, db):
        return ['hb_cell_tissue_type','hb_target','hb_genomebuild',\
                'MARK','MARK CLASS','Standardised epigenome name','Epigenome Mnemonic~~',\
                'Single Donor (SD) /Composite (C)~43~47','AGE (Post Birth in YEARS/ Fetal in GESTATIONAL WEEKS/CELL LINE CL) ~~',\
                'Epigenome ID (EID)~~','GROUP~~','ANATOMY~~','TYPE~~','SOLID / LIQUID~64~23','Single Donor (SD) /Composite (C)~43~47',\
                'SEX (Male_COMMA_ Female_COMMA_ Mixed_COMMA_ Unknown)~33~50','ETHNICITY~~']
        # # attributes = []
        # # 
        # # colList = db._db.getTableCols(cls.TABLE_NAME)
        # # for col in colList:
        # #     attributes.append(col)
        # # attributes.remove('url')
        # # attributes.remove('hb_datatype')
        # # 
        # # return attributes

    @classmethod
    def getColListString(cls):
        cols = cls.DB._db.correctColumNames\
        (cls.DB._db.getTableCols(cls.TABLE_NAME))
        colListString = ''
        cols.insert(0, cols.pop(cols.index('"url"')))
        cols.insert(1, cols.pop(cols.index('"hb_datatype"')))
        cols.insert(2, cols.pop(cols.index('"hb_filesuffix"')))
        for col in cols:
            colListString += col+','

        return cols,colListString.strip(',')
