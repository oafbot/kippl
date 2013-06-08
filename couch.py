import couchdb
import json
import sys
from couchdb.design import ViewDefinition
from inputs.config import Config

class Couch:
    def __init__(self, user=None, dbname='tweets-public-timeline'): 
        self.config = Config()
        self.user = user if user else self.config.user
        self.server = couchdb.Server(self.config.couchdb_host)
        self.dbname = dbname
        try:
            self.db = self.server.create(self.dbname)
        except couchdb.http.PreconditionFailed, e:
            # Already exists, so append instead
            self.db = self.server[self.dbname]
        
    def Update(self, data):
        dump = []
        for d in data:
            dump.append(d.AsDict())
        self.db.update(dump, all_or_nothing=True)
        # json_data=json.dumps(data, default=lambda o: o.__dict__)
    
    def Select(self, index, **kwargs):
        try:
            result = [t for t in self.db.view('index/'+index, **kwargs)]
        except IndexError, e:
            result = []
        return result
    
    def Index(self, index, path):
        key = "".join(["['"+obj+"']" for obj in path.split(".")])
        mapper = 'def '+index+'(doc): yield (doc'+key+', doc)'
        view = ViewDefinition('index', index, mapper, language='python')
        view.sync(self.db)
                
    def IndexUser(self, username=None):
        def user_mapper(doc):
            yield (doc['user']['screen_name'], doc)

        view = ViewDefinition('index', 'user', user_mapper, language='python')
        view.sync(self.db)
        try:
            result = [twid for twid in self.db.view('index/user', key=username)]
        except IndexError, e:
            result = []
        return result
    
    def IndexId(self, twid=None):
        def tweet_mapper(doc):
            yield (doc['id'], doc)

        view = ViewDefinition('index', 'tweet', tweet_mapper, language='python')
        view.sync(self.db)
        try:
            result = [t for t in self.db.view('index/tweet', key=twid)]
        except IndexError, e:
            result = []
        return result
                
    def MaxTweetId(self):
        def id_mapper(doc):
            yield (doc['user']['screen_name'], doc['id'])

        def max_tweet_reduce(keys, values, rereduce):
            return max(values)

        view = ViewDefinition('index', 'max_tweet_id', id_mapper, max_tweet_reduce, language='python')
        view.sync(self.db)
        try:
            since = int([twid for twid in self.db.view('index/max_tweet_id')][0].value)
        except IndexError, e:
            since = 1
        return since

    def MinTweetId(self):
        def id_mapper(doc):
            yield (None, doc['id'])

        def min_tweet_reduce(keys, values):
            return min(values)

        view = ViewDefinition('index', 'min_tweet_id', id_mapper, min_tweet_reduce, language='python')
        view.sync(self.db) 
        try:
            since = int([twid for twid in self.db.view('index/min_tweet_id')][0].value)
        except IndexError, e:
            since = 1
        return since
        
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
    
    # def ExtractAndFilter(self, user='all', filters=):
    #     pass
    
    # def ToString(self,a):
    #     import collections
    #     res = ''
    #     if isinstance(a, collections.Iterable):
    #         for item in a:
    #             res +=  str(self.ToString(item)) + '\n'
    #     else:
    #         res = str(a)
    #     return res
        