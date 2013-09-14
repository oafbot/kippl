from twitstream import TwitStream

class SearchTwitterStream:
    def __init__(self, keywords=None, follow=None, csv=None, db=None):
        path="outputs/"+csv if csv else None
        self.stream = TwitStream()
        self.stream.Filter(follow=follow,track=keywords,path=path,db=db)
    
