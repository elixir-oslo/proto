import psycopg2

class EncodeDatabase(object):
    def __init__(self, connStr):
        self._connStr = connStr
        self._connection = None

    def connect(self):
        self._connection = psycopg2.connect(self._connStr)

    def disconnect(self):
        self._connection.close()
        self._connection = None

    
