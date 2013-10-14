import MySQLdb
from inputs.config import Config

class Japondex:
    def __init__(self):
        self.config = Config()
        self.user   = self.config.mysql_usr
        self.passwd = self.config.mysql_pass
        self.host   = self.config.mysql_host
        self.db     = self.config.mysql_db
        self.con    = MySQLdb.connect (host=self.host, user=self.user, passwd=self.passwd, db=self.db, port=3306)
        self.cursor = self.con.cursor()
    
    def truncate(self, table):
        self.cursor.execute("TRUNCATE TABLE "+table)
        self.cursor.execute("ALTER TABLE "+table+" AUTO_INCREMENT=1")
    
    def insert(self, rows=[], table=None):
        for row in rows:
            keys   = row.keys()
            values = [row[k] for k in keys]
            query = "INSERT INTO %s (%s) VALUES (%s)" % (table, ", ".join(keys), ", ".join(values))
            print query
            self.cursor.execute(query)
