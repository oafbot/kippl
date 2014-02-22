from twitstream import TwitStream
import time

class SearchTwitterStream:
    def __init__(self, keywords=None, follow=None, csv=None, db=None):
        path="outputs/"+csv if csv else None
        self.stream = TwitStream()
        try:
            self.stream.Filter(follow=follow,track=keywords,path=path,db=db)
        except Exception, e:
            for i in range(0,100):
                while True:
                    try:
                        time.sleep(10)
                        self.stream.Filter(follow=follow,track=keywords,path=path,db=db)
                    except:
                        continue
                    break
    

