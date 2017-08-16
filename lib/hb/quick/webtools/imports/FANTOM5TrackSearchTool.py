from quick.webtools.imports.TrackSearchTool import TrackSearchTool
from quick.trackaccess.DatabaseTrackAccessModule import DatabaseTrackAccessModule
from quick.webtools.GeneralGuiTool import GeneralGuiTool

class FANTOM5TrackSearchTool(TrackSearchTool):
#    DATABASE_TRACK_ACCESS_MODULE_CLS = EncodeDatabaseTrackAccessModule
    def __new__(cls, *args, **kwArgs):
        return TrackSearchTool.__new__(FANTOM5TrackSearchTool, *args, **kwArgs)
    
    @staticmethod
    def getToolName():
        return "FANTOM 5"
    
    @classmethod
    def _getTableName(cls):
        return 'file_fantom5'
    
    @classmethod
    def _unquoteTrackURL(cls):
        return False
    
    @classmethod
    def _getClassAttributes(cls, db):
        attributes = []
        
        colList = cls.DB._db.getTableCols(cls.TABLE_NAME)
        for col in colList:
            attributes.append(col)
        
        attributes.remove('url')
        attributes.remove('hb_datatype')
        attributes.remove('Protocol REF')
        attributes.remove('Extract Name__2__')
        attributes.remove('Protocol REF__2__')
        attributes.remove('File Name')
        attributes.remove('Protocol REF__4__')
        attributes.remove('File Name__2__')
        
                
        return attributes

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
