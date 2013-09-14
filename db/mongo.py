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
        # self.db["posts"].find({"lang":"en", 'timestamp':{"$gte": self.start, "$lt": self.end}}, {"text":1,"_id":0})]
        pass
    
    def Count(self):
        pass
    
    def Distinct(self):
        pass
    
    def Min(self):
        pass
    
    def Max(self):
        pass
    
    def Avg(self):
        pass
    
    def Sum(self):
        pass
    
    def Dump(self):
        pass
    
    def DateTime(self, timestamp):
        import time
        return time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(timestamp,'%a %b %d %H:%M:%S +0000 %Y'))
    
    def TimeStamp(self, dt):
        import time
        return time.strptime(dt,'%a %b %d %H:%M:%S +0000 %Y')
    
    