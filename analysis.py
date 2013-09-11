import datetime
from mongo import Mongo
from tfidf import TermFrequency
from languagekit import LanguageKit
from inputs.dicts import Keywords
from collections import namedtuple
from potency import Potency
import multiprocessing as mp
# from multiprocessing import Process, Queue

class Analysis:
    def __init__(self, db, kw, date):
        self.start = datetime.datetime.now()
        self.mongo = Mongo(db=db)
        self.kwds  = Keywords(keywords=kw)
        self.lang  = LanguageKit(keywords=self.kwds)
        self.date  = date
        self.docs  = [self.lang.FilterRetweets(t["text"]) for t in self.mongo.db["posts"].find(
                            {"lang":"en", 'created_at':{"$regex": date}},{"text":1,"_id":0})]
        # self.docs  = [self.lang.FilterRetweets(t["text"]) for t in self.mongo.db["posts"].find(
        #                     {"lang":"en", 'timestamp':{"$gte": start, "$lt": end}},{"text":1,"_id":0})]
        self.docs  = list(set(filter(None, self.docs)))
        self.frequency = []
        self.scores   = []
    
    def ExecTime(self):
        elapsed = datetime.datetime.now() - self.start
        # hours = str(elapsed.seconds//3600) if elapsed.seconds//3600 > 9 else "0" + str(elapsed.seconds//3600)
        # mins = str((elapsed.seconds//60)%60) if (elapsed.seconds//60)%60 > 9 else "0" + str((elapsed.seconds//60)%60)
        hours, rem = divmod(elapsed.seconds, 3600)
        mins, secs = divmod(rem, 60)
        hh = str(hours) if hours > 9 else "0" + str(hours)
        mm = str(mins)  if mins  > 9 else "0" + str(mins)
        ss = str(secs)  if secs  > 9 else "0" + str(secs)
        
        print "\nexecution: ", elapsed.days, "days, ", hh+":"+mm+":"+ss
    
    def TFIDF(self, cores=mp.cpu_count()):
        queue = mp.Queue()
        proc  = {}
        prod  = {}
        
        for n in range(0, cores):
            start = n * (len(self.docs)//cores)
            end   = ((n+1) * (len(self.docs)//cores)) - 1
            proc[n] = mp.Process(target=self.ProcessTFIDF, args=(queue, self.docs[start:end]))
            proc[n].start()
            
            if n == cores-1 and len(self.docs)%cores != 0:
                start = end+1
                end   = len(self.docs)-1 # end+(len(self.docs)%cores)
                proc[n+1] = mp.Process(target=self.ProcessTFIDF, args=(queue, self.docs[start:]))
                proc[n+1].start()
        
        for n in proc: prod[n] = queue.get()
        
        freq = []
        for n in prod: freq += prod[n]
        self.frequency = freq
    
    def ProcessTFIDF(self, queue, docs):
        print"calculating tfidf..."
        frequency = []
        for tweet in docs:
            row = {'text': tweet.replace("\n", " ")}
            text = self.lang.FilterMentions(tweet)
            text = self.lang.FilterLinks(text)
            terms = TermFrequency(text, self.docs)
            row.update(terms.calc(text, self.kwds.keywords))
            frequency.append(row)    
        queue.put(frequency)
    
    def Score(self):
        print"calculating scores..."
        
        for tweet in self.frequency:
            row = namedtuple('tweet', 'score')
            row.tweet = tweet['text']
            row.score = 0
            for w in tweet:
                if w != 'text':
                    if w in self.kwds.negative:
                        if "no " + w in tweet['text'] or "not " + w in tweet['text']:
                           # print "actually pos"
                           row.score += tweet[w]*10
                        else:
                           row.score += tweet[w]*-10
                    elif w in self.kwds.positive:
                        if "no " + w in tweet['text'] or "not " + w in tweet['text']:
                            # print "actually neg"
                            row.score += tweet[w]*-10
                        else:
                            row.score += tweet[w]*10
                    else:
                        row.score += tweet[w]*0.1
            self.scores.append(row)
        
        self.scores = sorted(self.scores, key=lambda s: s.score, reverse=True)    
    
    def Index(self):
        print"calculating index..."
        
        pos = 0
        neg = 0
        neu = 0
        train = []
        
        for x in self.scores:
            if x.score > 2:
                print "Positive    ", x.tweet
                pos += x.score
                train.append({'text': x.tweet, 'classification': "P"})
            elif x.score < 0:
                print "Negative    ", x.tweet 
                neg += x.score
                train.append({'text': x.tweet, 'classification': "N"})
            else:
                # print "Neutral    ", x.tweet 
                neu += x.score
            # print x.score, "\t", x.tweet
        jpndex = int((pos + neg + neu) * 100) / 100.0
        volume = len(self.docs)
        
        print "\njapondex:", jpndex
        print "volume:  ", volume, "\n"
        
        print "applying bayesian calssifier..."
        self.potency = Potency(train)
    
    def WordCloud(self):
        text = "\n".join(self.docs)
        text = self.lang.FilterMentions(text)
        text = self.lang.FilterLinks(text)
        
        tokens = self.lang.Tokenize(text)
        tokens = self.lang.FilterStopwords(tokens)
        colloc = self.lang.Collocations(tokens)
        
        words = self.lang.FilterKeywords(tokens)
        words = self.lang.FilterWordLength(3,words)
        
        fdist = self.lang.Frequency(words)
        fdist = self.lang.FilterFdistStopwords(fdist)
        words = self.lang.FilterHapaxes(fdist)
        
        print "\nWord Cloud:"
        for t in words[:50]: print t[0].encode("utf-8"), ':', t[1]
        
        # for n, w in enumerate(words[:101]):
        #     print "\n"+str(n)+":", w[0], w[1]
        #     for c in colloc[w[0]][:10]: print c
    

# import re
# Wed Sep 11 02:06:16 +0000 2013
stamp = 'Sep 11 01.*2013'
analysis = Analysis("japan", ["japan", "japanese"], stamp)
analysis.TFIDF()
analysis.Score()
analysis.Index()
analysis.WordCloud()
analysis.ExecTime()