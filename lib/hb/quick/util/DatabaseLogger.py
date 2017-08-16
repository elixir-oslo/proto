import logging

from sqlalchemy import MetaData, Column, Integer, String, Column, create_engine, Float, Table, Sequence
from sqlalchemy.orm import mapper, sessionmaker

class MySQLDatabaseLogHandler(logging.Handler):
    def __init__(self, databaseAddress):
        logging.Handler.__init__(self)
        self.databaseEngine =  create_engine(databaseAddress)
        self.metaData = MetaData()
        
        logRecordTable = Table("logRecords", self.metaData,
                               Column("id", Integer, Sequence('logRecordSeq'), primary_key=True),
                               Column("created", Float),
                               Column("funcName", String(50)),
                               Column("levelno", Integer),
                               Column("lineno", Integer),
                               Column("message", String(400)),
                               Column("name", String(50)),
                               Column("pathname", String(200))
                               )
        
        self.metaData.create_all(self.databaseEngine)
        mapper(DatabaseLogRecord, logRecordTable)
        self.Session = sessionmaker(bind=self.databaseEngine)
        
    def emit(self, record):
        if not (self.filter(record)):
            return
        
        self.format(record)
        databaseRecord = DatabaseLogRecord(record)
        session = self.Session()
        session.add(databaseRecord)
        session.commit()           
        
class DatabaseLogRecord(object):
    def __init__(self, record):
        self.created = record.created
        self.funcName = record.funcName
        self.levelno = record.levelno
        self.lineno = record.lineno
        self.message = record.message
        self.name = record.name
        self.pathname = record.pathname      
        
    def makeLogRecord(self):
        attrdict = {"created": self.created, "funcName": self.funcName, "levelno": self.levelno, "message": self.message, 
                    "name": self.name, "pathname": self.pathname}
        return logging.makeLogRecord(attrdict)
        
class UserLogFilter(logging.Filter):
    def __init__(self, userName):
        logging.Filter.__init__(self)
        self.userName = userName
        
    def filter(self, record): 
        record.userName = self.userName
        return True
