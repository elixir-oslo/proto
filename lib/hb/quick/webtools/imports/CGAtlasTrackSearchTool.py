from quick.webtools.imports.TrackSearchTool import TrackSearchTool
from quick.trackaccess.DatabaseTrackAccessModule import DatabaseTrackAccessModule
from quick.webtools.GeneralGuiTool import GeneralGuiTool

class CGAtlasTrackSearchTool(TrackSearchTool):
#    DATABASE_TRACK_ACCESS_MODULE_CLS = EncodeDatabaseTrackAccessModule
    def __new__(cls, *args, **kwArgs):
        return TrackSearchTool.__new__(CGAtlasTrackSearchTool, *args, **kwArgs)
    
    @staticmethod
    def getToolName():
        return "The Cancer Genome Atlas (TCGA)"
    
    @classmethod
    def _getRepoInfo(cls):
        return ['The Cancer Genome Atlas', 'https://tcga-data.nci.nih.gov/tcga/',\
                'TCGA Data Portal']
    
    @classmethod
    def _getTableName(cls):
        return 'file_cgatlas'
    
    @classmethod
    def _getClassAttributes(cls, db):
        attributes = []
        
        colList = db._db.getTableCols(cls.TABLE_NAME)   
        for col in colList:
            attributes.append(col)
        attributes.remove('url')
        attributes.remove('hb_datatype')
        attributes.remove('centertype')
                
        return attributes

    @classmethod
    def _getClassAttributeValuesDetails(cls,db):
        return db.getAttributeValuesDetails(cls.TABLE_NAME, addColNameToDescription = True)
    
    @classmethod
    def getColListString(cls):
        cols = cls.DB._db.correctColumNames\
        (cls.DB._db.getTableCols(cls.TABLE_NAME))
        colListString = ''
        cols.insert(0, cols.pop(cols.index('"url"')))
        cols.insert(1, cols.pop(cols.index('"hb_datatype"')))
        for col in cols:
            colListString += col + ','
        
        return cols,colListString.strip(',')
