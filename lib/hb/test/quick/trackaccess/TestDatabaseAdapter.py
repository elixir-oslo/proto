import unittest

import psycopg2
import testing.postgresql

from quick.trackaccess.DatabaseTrackAccessModule import DatabaseAdapter

class TestPostgresDatabaseAdapter(unittest.TestCase):
    def setUp(self):
        self.postgresql = testing.postgresql.Postgresql()

    def testCreateTableFromList(self):
        db = DatabaseAdapter(**self.postgresql.dsn())
        db.createTableFromList('testtable', cols = ['a', 'b'], pk = 'b')
        self.assertEquals(['a', 'b'], db.getTableCols('testtable'))

    def runTest(self):
        pass

    def tearDown(self):
        self.postgresql.stop()


if __name__ == "__main__":
    #TestDatabaseTrackAccessModule().run()
    unittest.main()
