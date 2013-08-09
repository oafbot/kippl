import couchdb
import json
import sys
import time
import hashlib
from couchdb.design import ViewDefinition
from inputs.config import Config

class Couch:
    def __init__(self, user=None, db=None): 
        self.config = Config()
        self.user = user if user else self.config.user
        self.server = couchdb.Server(self.config.couchdb_host)
        self.dbname = db if db else "db_"+hashlib.sha224(str(time.time())).hexdigest()
        
        try:
            self.db = self.server.create(self.dbname)
        except couchdb.http.PreconditionFailed, e:
            # Already exists, so append instead
            self.db = self.server[self.dbname]
        
    def Update(self, data):
        if type(data) is list:
            dump = data
        else:
            dump=[data]        
        self.db.update(dump, all_or_nothing=True)
        
    def Alias(self, index, path):
        key = "".join(["['"+obj+"']" for obj in path.split(".")])
        mapper = 'def '+index+'(doc): yield (doc'+key+', doc)'
        view = ViewDefinition('index', index, mapper, language='python')
        view.sync(self.db)
    
    def Index(self, index):
        if type(index) is list:
            name = ""
            name += "_and_".join(["_".join([obj for obj in i.split(".")]) for i in index])
            mapper = 'def '+name+'(doc): yield (['+",".join(["doc"+"".join(["['"+obj+"']" 
                         for obj in i.split(".")]) for i in index])+'] , doc)'
        else:
            name = str("_".join([obj for obj in index.split(".")]))
            key = "".join(["['"+obj+"']" for obj in index.split(".")])
            mapper = 'def '+name+'(doc): yield (doc'+key+', doc)'
        
        view = ViewDefinition('index', name, mapper, language='python')
        view.sync(self.db)
        return name
    
    def IndexDate(self, index):        
        name = str("_".join([obj for obj in index.split(".")]))
        key = "".join(["['"+obj+"']" for obj in index.split(".")])
        date  = 'datetime.timetuple(parse(doc'+key+'))[:-3]'
        epoch = 'calendar.timegm('+date+')'
        # mapper = 'def '+name+'(doc): yield (['+epoch+','+date+'], doc)'
        mapper = 'def '+name+'''(doc): 
                  from dateutil.parser import parse
                  from datetime import datetime
                  import calendar
                  yield (['''+epoch+', list('+date+')], doc)'
        view = ViewDefinition('index', name, mapper, language='python')
        view.sync(self.db)
        return name
        
    def GetIndex(self, index, **kwargs):
        """ 
        kwargs are as follows:
        descending:     If true, return documents in descending key order.
        endkey:         Stop returning records when the specified key is reached.
        endkey_docid:   Stop returning records when the specified document ID is reached.
        group:          If true, group the results using the reduce function to a group or single row.
        group_level:    Description Specify the group level to be used.
        include_docs:   If true, include the full content of the documents in the response.
        inclusive_end:  If true, includes specified end key in the result.
        key:            Return only documents that match the specified key.
        limit:          Limit the number of the returned documents to the specified number.
        reduce:         If true, use the reduction function.
        skip:           Skip this number of records before starting to return the results.
        stale:          Allow the results from a stale view to be used.
        startkey:       Return records starting with the specified key
        startkey_docid: Return records starting with the specified document ID.
        update_seq:     If true, include the update sequence in the generated results.
        """
        select = kwargs.pop('select') if 'select' in kwargs else None
        try:
            if not select or select == "*":
                result = [t.value for t in self.db.view('index/'+index, **kwargs)]
            else:
                if type(select) is list:
                    keys = ["".join(["['"+obj+"']" for obj in s.split(".")]) for s in select]
                else:
                    keys = ["".join(["['"+obj+"']" for obj in select.split(".")])]
                result = [[eval('t.value'+key) for key in keys] for t in self.db.view('index/'+index, **kwargs)]
        except IndexError, e:
            result = []
        return result
        
    def Select(self, index, **kwargs):
        name = self.Index(index)
        return self.GetIndex(name, **kwargs)
    
    def Distinct(self, index, **kwargs):
        name = "distinct_"+str("_".join([obj for obj in index.split(".")]))
        key = "".join(["['"+obj+"']" for obj in index.split(".")])
        mapper  = 'def '+name+'(doc): yield (doc'+key+', doc'+key+')'
        # reducer = 'def '+name+'_reduce(keys, values, rereduce): return values'
        
        view = ViewDefinition('index', name, mapper, language='python')
        view.sync(self.db)
        return list(set(self.SelectIndex(name, **kwargs)))
        
    def Count(self, index, **kwargs):
        return len(self.Select(index, **kwargs))
    
    def Sum(self, index, **kwargs):
        pass
    
    def Avg(self, index, **kwargs):
        pass
        
    def Max(self, index):
        key = "".join(["['"+obj+"']" for obj in index.split(".")])
        mapper = 'def max_'+index+'(doc): yield (None, doc'+key+')'
        
        def max_reduce(keys, values, rereduce):
            return max(values)
        
        view = ViewDefinition('index', 'max_'+index, mapper, max_reduce, language='python')
        view.sync(self.db)
        try:
            return [twid for twid in self.db.view('index/max_'+index)][0].value
        except IndexError, e:
            return 0
    
    def Min(self, index):
        key = "".join(["['"+obj+"']" for obj in index.split(".")])
        mapper = 'def min_'+index+'(doc): yield (None, doc'+key+')'

        def min_reduce(keys, values, rereduce):
            return min(values)

        view = ViewDefinition('index', 'min_'+index, mapper, min_reduce, language='python')
        view.sync(self.db)
        try:
            return [twid for twid in self.db.view('index/min_'+index)][0].value
        except IndexError, e:
            return 0                
    
    def Dump(self, index, **kwargs):
        if type(index) is list:
            pass
            # name = ""
            # name += "_and_".join(["_".join([obj for obj in i.split(".")]) for i in index])
            # mapper = 'def dump_'+name+'(doc): yield (['+",".join(["doc"+"".join(["['"+obj+"']" 
            #              for obj in i.split(".")]) for i in index])+'] , doc)'
        else:
            # keystring = str(key) if key else ""
            name = str("_".join([obj for obj in index.split(".")]))
            k = "".join(["['"+obj+"']" for obj in index.split(".")])
            mapper  = 'def dump_'+name+'(doc): yield (None, doc'+k+')'
            reducer = 'def reduce_dump(keys, values): return "\n".join(values)'
        
        view = ViewDefinition('index', name, mapper, reducer, language='python')
        view.sync(self.db)
        return name
    
        
    def DumpTweets(self, user='all', retweets=False, mentions=False):
        def tweets_text_dump(doc):
            yield (doc['user']['screen_name'], doc['text'])
        
        def reduce_filter_rt(keys, values):
            import re
            return "\n".join([v for v in values if not re.match('^RT', v)])
        
        def reduce_tweets(keys, values, rereduce):
            return "\n".join(values)
 
        dump = ""
        if not retweets:
            name = user + "_filter_retweets"
            view = ViewDefinition('dump', name, tweets_text_dump, reduce_filter_rt, language='python')
            view.sync(self.db)
            dump += [txt for txt in self.db.view('dump/'+name)][0].value
        else:
            view = ViewDefinition('dump', user, tweets_text_dump, reduce_tweets, language='python')
            view.sync(self.db)
            dump += [txt for txt in self.db.view('dump/'+user)][0].value
            
        return dump

    def IndexUsers(self, username=None):
        self.couch.Index('user', 'user.screen_name')

    def IndexTweets(self, twid=None):
        self.couch.Index('tweet', 'id')    

    # def ExtractAndFilter(self, user='all', filters=):
    #     pass
        