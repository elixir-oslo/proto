import unittest
import gold.application.LogSetup
import logging
from quick.util.DatabaseLogger import MySQLDatabaseLogHandler, UserLogFilter, DatabaseLogRecord
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey

class TestDatabaseLoggingHandler(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.logger = logging.getLogger()
        self.handler = MySQLDatabaseLogHandler("mysql://hb_testing:hb_testing@localhost:3306/hb_testing?unix_socket=/var/lib/mysql/mysql.sock")
        self.logger.addHandler(self.handler)  
        
    def setUp(self):
        pass
    
    def tearDown(self):
        self.handler.Session().query(DatabaseLogRecord).delete()
    
    @unittest.SkipTest
    def testInsertSingleRow(self):
        session = self.handler.Session()
        self.assertEquals(len(session.query(DatabaseLogRecord).all()), 0)
        self.logger.warning("Testing inserting single row")
        self.assertEquals(len(session.query(DatabaseLogRecord).all()), 1)
       
    @unittest.SkipTest 
    def testMakeLogRecord(self):
        session = self.handler.Session()
        self.logger.warning("Testing making log record")
        
    def testDatabase(self):     
        session = self.handler.Session()
        record = session.query(DatabaseLogRecord).all()[0].makeLogRecord()
        #print record, record.message
  
class TestUserLogFilter(unittest.TestCase):
    def setUp(self):
        self.logger = logging.getLogger()        

        #For writing to console
        #consoleHandler = logging.StreamHandler()        
        formatter = logging.Formatter('%(user)s - %(message)s')
        #consoleHandler.setFormatter(formatter)
        #self.logger.addHandler(consoleHandler)
        
        #In addition to the handler which writes to stdout, we also add
        #a helper handler which is used to verify the output
        self.testHandler = TestHandler(Matcher())
        self.testHandler.setFormatter(formatter)
        self.logger.addHandler(self.testHandler)

    def tearDown(self):
        self.logger.removeHandler(self.testHandler)
        self.testHandler.close()

    def testUserLogFilter(self):
        filter = UserLogFilter("testUser")
        self.logger.addFilter(filter)
        
        self.logger.warning("test")
        self.assertTrue(self.testHandler.matches(levelno=logging.WARNING))

#From Vinay Saji. Used for testing proper logging      
from logging.handlers import BufferingHandler

class TestHandler(BufferingHandler):
    def __init__(self, matcher):
        # BufferingHandler takes a "capacity" argument
        # so as to know when to flush. As we're overriding
        # shouldFlush anyway, we can set a capacity of zero.
        # You can call flush() manually to clear out the
        # buffer.
        BufferingHandler.__init__(self, 0)
        self.matcher = matcher

    def shouldFlush(self):
        return False

    def emit(self, record):
        self.buffer.append(record.__dict__)

    def matches(self, **kwargs):
        """
        Look for a saved dict whose keys/values match the supplied arguments.
        """
        result = False
        for d in self.buffer:
            if self.matcher.matches(d, **kwargs):
                result = True
                break
        return result

class Matcher(object):

    _partial_matches = ('msg', 'message')

    def matches(self, d, **kwargs):
        """
        Try to match a single dict with the supplied arguments.

        Keys whose values are strings and which are in self._partial_matches
        will be checked for partial (i.e. substring) matches. You can extend
        this scheme to (for example) do regular expression matching, etc.
        """
        result = True
        for k in kwargs:
            v = kwargs[k]
            dv = d.get(k)
            if not self.match_value(k, dv, v):
                result = False
                break
        return result

    def match_value(self, k, dv, v):
        """
        Try to match a single stored value (dv) with a supplied value (v).
        """
        if type(v) != type(dv):
            result = False
        elif type(dv) is not str or k not in self._partial_matches:
            result = (v == dv)
        else:
            result = dv.find(v) >= 0
        return result

if __name__ == '__main__':
    unittest.main()
