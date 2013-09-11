#!/usr/local/bin/python
import sys, os, os.path, cPickle as pickle
# from collections import namedtuple

dirname = os.path.dirname(os.path.abspath(__file__))
os.chdir(dirname)

sys.path.append( '../' )
from mongo import Mongo
from languagekit import LanguageKit
from inputs.dicts import Keywords

if __name__ == "__main__":
    mongo = Mongo(db="japan")
    kwds  = Keywords(keywords=["japan", "japanese"])
    lang  = LanguageKit(keywords=kwds)
    docs  = [lang.FilterRetweets(t["text"]) for t in mongo.db["posts"].find(
                                {"lang":"en"},{"text":1,"_id":0})]
    size  = len(docs)-1
    start = int(sys.argv[1]) if len(sys.argv)>1 else 0
    end   = int(sys.argv[2]) if len(sys.argv)>2 else size

                                 
    count = start
    features = []
    print end+1-start
    
    for tweet in docs[start:end]:
        if tweet:
            count = docs[start:end].index(tweet)+start
            i = raw_input('['+str(count)+'] '+tweet.replace("\n", " ").encode("utf-8")+": ")
            if i is "n" or i is "p":
                row = {'text':tweet.replace("\n", " "), 'classification':i.upper()}
                features.append(row)
            
    pickle.dump(features, open("../outputs/trainset-"+str(start)+"-"+str(end)+".pk", "wb" ))

            