import twitter
import time, sys
from urllib2 import URLError

class TwitBot:
    def __init__(self, user, consumer_key, consumer_secret, access_token_key, access_token_secret):
        """Enter pydoc twitter.Api for information about the Python-twitter wrapper class."""
        self.user = user
        self.api  = twitter.Api(
                        consumer_key=consumer_key, 
                        consumer_secret=consumer_secret, 
                        access_token_key=access_token_key, 
                        access_token_secret=access_token_secret)
    
    def Post(self, content):
        status = self.api.PostUpdate(content)

    def Timeline(self, user, since=None, maxid=None, count=None):
        timeline = self.api.GetUserTimeline(screen_name=user, since_id=since, max_id=maxid, count=count)
        return timeline
        
    def Search(self, term=None, since_id=None, max_id=None, until=None, 
               count=15, page=1, lang=None, geocode=None):
        results=[]
        pages=15
        
        for page in range(1, pages+1):
            next = self.api.GetSearch(term=term, per_page=count, page=page, until=until, 
                                      since_id=since_id, max_id=max_id, include_entities=True)
            print "tweets:", len(next), "\tpage:", page
            
            if(len(next)>80):
                results += next
            else:
                results += next
                break;
        return results
    
    def UserSearch(self, term=None):
        results=[]
        pages=50
        for page in range(1, pages+1):
            next = self.api.GetUsersSearch(term=term, page=page, count=20, include_entities=True)
            
            print "users:", len(next), "\tpage:", page
            
            if(len(next)>10):
                results += next
            else:
                results += next
                break;
        return results
        
    
    def HandleError(self, e, wait=2):
        if wait > 3600:
            print >> sys.stderr, "Too many retries. Exiting."
            raise e
        if isinstance(e, twitter.TwitterError):
            if(e.message == "You have been rate limited. Enhance your calm." 
            or e.message == "Over capacity"
            or e.message == "Rate limit exceeded. Clients may not make more than 350 requests per hour."):
                status = self.api.GetRateLimitStatus()
                now = time.time()
                when = status["reset_time_in_seconds"]
                sleep = when - now
                print >> sys.stderr, "Rate limit reached: sleeping for %i secs" % (sleep,)
                time.sleep(sleep)
                return 2
        elif e.code == 401:
            print dir(e)
            print >> sys.stderr, "Encountered 401 Error (Not Authorized)"
            return None
        elif e.code in(502, 503):
            print dir(e)
            print >> sys.stderr, "Encountered %i Error. Will retry in %i seconds" % (e.e.code, wait)
            time.sleep(wait)
            wait *= 1.5
            return wait
        else:
            print dir(e)
            raise e
        
    def Request(self, func, max_error=3, *args, **kwArgs):
        wait=2
        error_count=0
        while True:
            try:
                return func(*args, **kwArgs)
            except twitter.TwitterError, e:
                error_count = 0
                wait = self.HandleError(e, wait)
                if wait is None:
                    return
            except HTTPError, e:
                error_count = 0
                wait = self.HandleError(e, wait)
                if wait is None:
                    return
            except URLError, e:
                error_count += 1
                print sys.stderr, "URLError encountered. Continuing..."
                if error_count > max_error:
                    print >> sys.stderr, "Too many consecutive errors. Aborting."
                    raise
    
    def Clean(self, target):
        import re
        target=target.replace(",", "")
        target=re.sub("\n", " ", target)
        target=re.sub("\r", " ", target)
        return target
    
    def Serialize(self, object, path):
        import cPickle as pickle
        pickle.dump( object, open( path, "wb" ) )
    
    def Unserialize(self, path):
        import cPickle as pickle
        return pickle.load( open( path, "rb" ) )
        
    def SaveTweetIds(self, object):
        self.Serialize(object, "inputs/latest_tweets.p")

    def LoadTweetIds(self):
        return self.Unserialize("inputs/latest_tweets.p")
