from quick.webtools.imports.TrackSearchTool import TrackSearchTool
from quick.trackaccess.DatabaseTrackAccessModule import DatabaseTrackAccessModule
from quick.webtools.GeneralGuiTool import GeneralGuiTool

class EBIHubTrackSearchTool(TrackSearchTool):
#    DATABASE_TRACK_ACCESS_MODULE_CLS = EncodeDatabaseTrackAccessModule
    def __new__(cls, *args, **kwArgs):
        return TrackSearchTool.__new__(EBIHubTrackSearchTool, *args, **kwArgs)
    
    @staticmethod
    def getToolName():
        return "BLUEPRINT project hub"
    
    @classmethod
    def _getTableName(cls):
        return 'file_ebihub'
    
    # @classmethod
    # def _getGSuiteTrackSuffix(cls,url):
    #     s = url.split('/')[-1].split('.')[-1]
    #     if s.lower() == 'gz':
    #         return '.'.join(url.split('/')[-1].split('.')[-2:])
    #     else:
    #         return s
    
    @classmethod
    def _getClassAttributes(cls, db):
        attributes = []
        
        colList = db._db.getTableCols(cls.TABLE_NAME)   
        for col in colList:
            attributes.append(col)
        attributes.remove('url')
        attributes.remove('hb_datatype')
                
        return attributes

    @classmethod
    def _getClassAttributeValuesDetails(cls,db):
        return db.getAttributeValuesDetails(cls.TABLE_NAME)
    
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

    @classmethod
    def _getDownloadProtocol(cls):
        return 'ftp'
