import os, os.path
#import unicodedata

class SearchTwitterREST:
    def __init__(self, keywords, bot):
        self.bookmarks = {}

        if not os.path.isfile("outputs/tweets.csv"):
            self.csv = "Id,Username,Keyword,Content,Timestamp,RTs,Favorites,ReplyTo,Hastags,Urls\n"
        else:
            self.csv = "" 

        f = open("outputs/tweets.csv", "ab+")
        self.Search(keywords, bot, f)


    def Search(self, keywords, bot, f):   
        for terms in keywords.GetKeywords():
            for term in terms:
                import os.path
                if os.path.isfile("inputs/latest_tweets.p"):
                    lastbatch = bot.LoadTweetIds()
                    if term in lastbatch:
                        since = lastbatch[term]
                    else:
                        since = None
                    search = bot.Request(bot.Search, term=term, count=100, page=1, lang="en", since_id=since)
                else:
                    search = bot.Request(bot.Search, term=term, count=100, page=1, lang="en")
                
                for result in search:
                    date = bot.Clean(result.created_at)
                    text = bot.Clean(result.text)
                    urls = []
                    hashtags = []

                    for hashtag in result.hashtags:
                       hashtags.append(hashtag.text)

                    for url in result.urls:
                       urls.append(url.expanded_url)
                                        
                    self.csv += str(result.id)+","+\
                           result.user.screen_name+","+\
                           term+","+\
                           text+","+\
                           date+","+\
                           str(result.retweet_count)+","+\
                           str(result.favorite_count)+","+\
                           str(result.in_reply_to_status_id)+","+\
                           ' '.join(hashtags)+","+\
                           ' '.join(urls)+","+\
                           "\n"
                           #str(bot.api.GetStatus(result.id).retweet_count)+","+\
                           #str(bot.api.GetStatus(result.id).favorite_count)+","+\
                
                if(search and search[0]):
                    self.bookmarks[term] = search[0].id
        
                rate = bot.api.GetRateLimitStatus()["remaining_hits"]
                print "Rate limit:", rate, "-----------", term
                f.write(self.csv.encode('utf-8'))
                self.csv = ""
        bot.SaveTweetIds(self.bookmarks)
        f.close()
