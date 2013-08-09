class Database:
    def __init__(self, dbtype, dbname):
        self.dbname = dbname
        
        if dbtype is "couch":
            from couch import Couch
            self.db = Couch(db=self.dbname)
        elif dbtype is "mongo":
            from mongo import Mongo
            self.db = Mongo(db=self.dbname)
        
    def Update(self, table):
        pass
        
    def Select():
        pass
        
    def Count():
        pass
    
    def Distinct():
        pass

    def Min():
        pass

    def Max():
        pass

    def Avg():
        pass

    def Sum():
        pass
        
    def Dump():
        pass    