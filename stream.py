from twitstream import TwitStream

class SearchTwitterStream:
    def __init__(self, keywords):
        self.stream = TwitStream()
        self.stream.Filter(follow=None,track=keywords,path="outputs/stream.csv")