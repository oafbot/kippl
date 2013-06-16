class TweetDB:
    def __init__(self, db):
        """docstring for __init__"""
        from couch import Couch
        self.couch=Couch(db=db)
        
    def BuildIndecies(self):
        self.couch.Index('user.id')
        self.couch.Index('user.screen_name')
        self.couch.Index('id')
    
    