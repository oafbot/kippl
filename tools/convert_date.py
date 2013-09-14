import datetime
from mongo import Mongo

mongo = Mongo(db="japan")
# posts = [t for t in mongo.db["posts"].find().batch_size(30)]

# print len(posts)
count = 0

for post in mongo.db["posts"].find().batch_size(30):
    if post.has_key('created_at'):
        post['timestamp'] = mongo.DateTime(post['created_at'])
        mongo.db["posts"].update({'_id':post['_id']}, {"$set":{'timestamp':post['timestamp']}}, upsert=False)
        count += 1
        print post['timestamp'], count