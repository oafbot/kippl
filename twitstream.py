import sys, os
import tweepy
import webbrowser
import json
from inputs.config import Config
from twitbot import TwitBot

class TwitStream: 
    def __init__(self):
        self.config = Config()
        self.auth   = tweepy.OAuthHandler(self.config.consumer_key, self.config.consumer_secret)
        self.auth.set_access_token(self.config.access_token_key, self.config.access_token_secret)
        # self.api = tweepy.API(self.auth, parser=MyModelParser())

    def Filter(self, follow=None, track=None, path=None, db=None):
        self.csv = path
        self.stream = tweepy.streaming.Stream(self.auth, StreamListener(path=path, db=db), timeout=60)
        
        print >> sys.stderr, 'Filtering the public timeline for "%s"' % (' '.join(track))
        
        self.stream.filter(follow=follow, track=track)

class StreamListener(tweepy.StreamListener):
    def __init__(self, path=None, db=None):
       tweepy.StreamListener.__init__(self)
       self.csv = path
       self.dbname = db
       self.data = []
       if path:
           self.setpath()
       if db or (not db and not path):
           self.setdb()
                
    def setpath(self):
        if not os.path.isfile(self.csv):
            output = "Id,Username,Content,Timestamp,RTs,Favorites,ReplyTo,Hastags,Urls\n"
            self.file = open(self.csv, "ab+")
            self.file.write(output.encode('utf-8'))
        else:
            self.file = open(self.csv, "ab+")
    
    def setdb(self):
        from couch import Couch
        self.db = Couch(db=self.dbname)
        
    def writestream(self,status):
        if self.csv:
            date = self.Clean(str(status.created_at))
            text = self.Clean(status.text)
                
            urls = []
            hashtags = []
                             
            for hashtag in status.entities["hashtags"]:
                hashtags.append(hashtag['text'])
        
            for url in status.entities["urls"]:
                urls.append(url['expanded_url'])
        
            self.output = str(status.id)+","+\
                    status.author.screen_name+","+\
                    text+","+\
                    date+","+\
                    str(status.retweet_count)+","+\
                    str(status.favorite_count)+","+\
                    str(status.in_reply_to_status_id)+","+\
                    ' '.join(hashtags)+","+\
                    ' '.join(urls)+","+\
                    "\n"
            self.file.write(self.output.encode('utf-8'))
        
        if self.dbname or (not self.dbname and not self.csv):
            data = {}
            # stat = status.__getstate__()
            # del stat['author']
            # for key in stat:
            #     # print key, type(stat[key]), stat[key] 
            #     if type(stat[key]) is tweepy.models.User:
            #         print "user!!!!"
            #         user_object = stat[key].__getstate__()
            #         user = {}
            #         for k in user_object:
            #             if type(user_object[k]) is datetime.datetime:
            #                 user[k] = user_object[k].strftime('%a %b %d %H:%M:%S +0000 %Y')
            #             else:
            #                 user[k] = user_object[k]
            #         data[key] = user
            #     elif type(stat[key]) is tweepy.models.Place:
            #         print "place!!!!"
            #         data[key] = stat[key].__getstate__()
            #     elif type(stat[key]) is tweepy.models.Status:
            #         print "status!!!"
            #         data[key] = stat[key].__getstate__()                    
            #     elif type(stat[key]) is datetime.datetime:
            #         print "date!!!!"
            #         data[key] = stat[key].strftime('%a %b %d %H:%M:%S +0000 %Y') # Wed Jun 05 22:11:25 +0000 2013
            #     else:
            #         data[key] = stat[key]
            
            data = self.process_dict(status, data, self.process)
            # data = self.serialize(status, {})
            
            # pickled = jsonpickle.encode(data)
            # data = json.loads(pickled)
            # del data['_api']
            # data = simplejson.loads(simplejson.dumps(data))
            # import pprint
            # pp = pprint.PrettyPrinter(indent=4)
            # pp.pprint(data)
            if len(self.data) < 500:
                self.data.append(data)
                # print "appending", len(self.data)
            else:
                self.db.Update(self.data)
                self.data=[]
                self.data.append(data)
                # print "updating", len(self.data)
        
    def on_status(self, status):
        try:
            self.writestream(status)
            print "%s:\n%s\n%s%s\n" % (status.author.screen_name, status.text, status.created_at,"\n",)
        except Exception, e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print >> sys.stderr, 'Encountered Exception:', e, fname, exc_tb.tb_lineno
            # print(exc_type, fname, exc_tb.tb_lineno)
            # import traceback
            # print traceback.format_exc()
            pass

    def on_error(self, status_code):
        print >> sys.stderr, 'Encountered error with status code:', status_code
        return True # Don't kill stream

    def on_timeout(self):
        print >> sys.stderr, 'Timeout...'
        return True # Don't kill stream
        
    def Clean(self, target):
        import re
        target=target.replace(",", "")
        target=re.sub("\n", " ", target)
        return target 
        

    def serialize(self, object, data, key=None):
        import datetime
        
        if type(object) is tweepy.models.Status:
            for s in object.__getstate__():
                data[s] = None
                data[s] = self.serialize(object.__getstate__()[s], data[s], key=s)
        elif type(object) is tweepy.models.User:
            for s in object.__getstate__():
                data[s] = None
                data[s] = self.serialize(object.__getstate__()[s], data[s], key=s)
        elif type(object) is datetime.datetime:
            data[key] = object.strftime('%a %b %d %H:%M:%S +0000 %Y')
        else:
            data[key] = object
        
        return data

    def process(self, key, value):
        import datetime
        if type(value) is tweepy.models.User:
            print "user!!!!"
            return value.__getstate__()
        elif type(stat[key]) is tweepy.models.Place:
            print "place!!!!"
            return value.__getstate__()
        elif type(stat[key]) is tweepy.models.Status:
            print "status!!!"
            return value.__getstate__()                    
        elif type(stat[key]) is datetime.datetime:
            print "date!!!!"
            return value.strftime('%a %b %d %H:%M:%S +0000 %Y') # Wed Jun 05 22:11:25 +0000 2013
        else:
            return value

    def process_dict(self, obj, dict, callback):
        for k, v in dict.items():
            if hasattr(v, 'items'):
                self.process_dict(v, dict, callback)
            else:
                dict[k] = callback(k, v)
        return dict    

# class MyModelParser(tweepy.parsers.ModelParser):
#     def parse(self, method, payload):
#         result = super(MyModelParser, self).parse(method, payload)
#         result._payload = simplejson.loads(payload)
#         return result


# elif type(object) is dict:
#     d = {}
#     for o in object:
#         d[o] = self.serialize(object[o], data, key=o)
#     data[key] = d
# elif type(object) is list:
#     data[key] = [self.serialize(l, data) for l in object]