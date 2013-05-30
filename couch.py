import couchdb
import json
from couchdb.design import ViewDefinition
from inputs.config import Config


class Couch:
    def __init__(self, user=None): 
        self.config = Config()
        self.user = user if user else self.config.user
        self.server = couchdb.Server(self.config.couchdb_host)
        self.dbname = 'tweets-public-timeline'
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
        
        