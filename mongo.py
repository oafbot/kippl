import pymongo
from pymongo import MongoClient

class Mongo:
    def __init__(self, user=None, db=None):
        from inputs.config import Config
        self.config = Config()
        self.client = MongoClient()
        # self.db = self.client.(db)
        # self.db = getattr(self.client, db)
        self.db = self.client.japan
        
    def Update(self, data, collection=None):
        collection = "posts" if not collection else collection
        self.Insert(data, collection)
        
    def Insert(self, object, name):
        import numpy, decimal
        
        for post in object:
            for key in post:
                #print type(post[key]), post[key]
                if type(post[key]).__module__ == numpy.__name__:
                    post[key] = numpy.asscalar(post[key])
                if type(post[key]) is decimal.Decimal:
                    post[key] = float(post[key])
            posts = self.db[name]
            post_id = posts.insert(post)
    
    def Select(select=None, where=None, exclude=None, limit=None):
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