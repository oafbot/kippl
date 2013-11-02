class Config:
    def __init__(self):
        self.db   = "mongo_db_name"
        self.host = "hostname:27017"
        self.out  = True
        
        self.mysql_pass = ""
        self.mysql_usr  = ""
        self.mysql_db   = ""
        self.mysql_host = 'localhost'
        # self.couchdb_host = "http://localhost:5984"
        
        self.user=""
        self.consumer_key=''
        self.consumer_secret=''
        self.access_token_key=''
        self.access_token_secret=''
