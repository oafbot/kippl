import sys, os
import tweepy
import webbrowser
from inputs.config import Config
from twitbot import TwitBot

class TwitStream: 
    def __init__(self):
        self.config = Config()
        self.auth   = tweepy.OAuthHandler(self.config.consumer_key, self.config.consumer_secret)
        self.auth.set_access_token(self.config.access_token_key, self.config.access_token_secret)

    def Filter(self, follow=None, track=None, path=None):
        self.path   = path
        self.stream = tweepy.streaming.Stream(self.auth, CustomStreamListener(self.path), timeout=60)
        
        print >> sys.stderr, 'Filtering the public timeline for "%s"' % (' '.join(track))
        
        self.stream.filter(follow=follow, track=track)

class CustomStreamListener(tweepy.StreamListener):
    def __init__(self, path):
       tweepy.StreamListener.__init__(self)
       self.path = path
       self.setpath()
                
    def setpath(self):
        if not os.path.isfile(self.path):
            output = "Id,Username,Content,Timestamp,RTs,Favorites,ReplyTo,Hastags,Urls\n"
            self.file = open(self.path, "ab+")
            self.file.write(output.encode('utf-8'))
        else:
            self.file = open(self.path, "ab+")
        
    def writestream(self,status):        
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
        
    def on_status(self, status):
        try:
            self.writestream(status)
            print "%s:\n%s\n%s%s\n" % (status.author.screen_name, status.text, status.created_at,"\n",)
        except Exception, e:
            print >> sys.stderr, 'Encountered Exception:', e
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