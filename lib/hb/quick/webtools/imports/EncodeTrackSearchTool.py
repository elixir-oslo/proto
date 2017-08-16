from quick.webtools.imports.TrackSearchTool import TrackSearchTool

class EncodeTrackSearchTool(TrackSearchTool):
#    DATABASE_TRACK_ACCESS_MODULE_CLS = EncodeDatabaseTrackAccessModule
    def __new__(cls, *args, **kwArgs):
        return TrackSearchTool.__new__(EncodeTrackSearchTool, *args, **kwArgs)
    
    @staticmethod
    def getToolName():
        return "ENCODE (UCSC and Ensembl)"
    
    @classmethod
    def _getRepoInfo(cls):
        return ['ENCODE (UCSC and Ensembl)', 'http://www.genome.gov/ENCODE/',\
                'The ENCODE Project: ENCyclopedia Of DNA Elements']
    
    @classmethod
    def _getTableName(cls):
        return 'file_encode'
    
    @classmethod
    def _getClassAttributes(cls, db):
        return ['datatype','hb_cell_tissue_type','hb_target','hb_genomebuild','antibody','rnaextract','cell',\
                      'localization','phase','settype','control','view','quality','obtainedby','biorep','sex',\
                      'replicate','lab','softwareversion','seqplatform','protocol','treatment','dataversion','geosampleaccession',
                        'tablename']
        # # attributes = []
        # # nonSearchable = ['md5sum','size','dateresubmitted','datesubmitted','dateunrestricted','hb_datatype','_source','_url']
        # # colList = db._db.getTableCols(cls.TABLE_NAME, ordered = True)
        # # for col in colList:
        # #     #searchable = db._db.runQuery\
        # #     #    ("SELECT _searchable FROM field WHERE term = '"+col+"';")
        # #     #print searchable
        # #     if not col in nonSearchable: 
        # #         attributes.append(col)
        # # #attributes.append('hb_datatype')        
        # # return attributes
    
    @classmethod
    def getColListString(cls):
        cols = cls.DB._db.correctColumNames\
            (cls.DB._db.getTableCols(cls.TABLE_NAME))
        colListString = ''
        cols.insert(0, cols.pop(cols.index('"_url"')))
        cols.insert(1, cols.pop(cols.index('"hb_datatype"')))
        cols.insert(2, cols.pop(cols.index('"hb_filesuffix"')))
        cols.insert(3, cols.pop(cols.index('"datatype"')))
        cols.insert(4, cols.pop(cols.index('"cell"')))
        cols.insert(5, cols.pop(cols.index('"antibody"')))
        cols.insert(6, cols.pop(cols.index('"_source"')))
        for col in cols:
            colListString += col+','
        return cols,colListString.strip(',')
    
    @classmethod
    def _getDownloadProtocol(cls):
        return 'rsync'