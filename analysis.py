import datetime
import multiprocessing as mp
from db.mongo import Mongo
from lang.tfidf import TermFrequency
from lang.languagekit import LanguageKit
from inputs.dicts import Keywords
from inputs.config import Config
from lang.potency import Potency
from collections import namedtuple
from util.output import Output
from util.multicore import Multicore

class Analysis:
    def __init__(self, db, kw, start, end):
        # self.timer = datetime.datetime.now()
        self.mongo = Mongo(db=db)
        self.kwds  = Keywords(keywords=kw)
        self.lang  = LanguageKit(keywords=self.kwds)
        self.start = str(start)
        self.end   = str(end)
        self.docs  = [self.lang.FilterRetweets(t["text"]) for t in self.mongo.db["posts"].find(
                     {"lang":"en", 'timestamp':{"$gte": self.start, "$lt": self.end}}, {"text":1,"_id":0})]
        
        # Spamfilter, remove redundant
        self.docs = list(set(filter(None, self.docs)))
        self.docs = self.lang.FilterSpam(self.docs)
        self.docs = self.lang.SimpleSpamFilter(self.docs)
        
        self.multicore = Multicore()
        self.frequency = []
        self.scores    = []
        self.trace     = Config().out
        self.output    = Output(self.trace)
        
    
    def TFIDF(self, cores=mp.cpu_count()):
        termf = TermFrequency(self.docs, lang=self.lang)
        self.frequency = self.multicore.run(func=self.ProcessTFIDF, tasks=self.docs, args=(termf,))
        return self.frequency
    
    def ProcessTFIDF(self, termf, queue=None, pid=None, tasks=None):
        frequency = []
        if pid==0:
            self.output.statusbar(len(tasks), title="calculating tfidf...")
        for tweet in tasks:
            if pid==0:
                self.output.on_status()
            row = {'analysis_text': tweet.replace("\n", " ")}
            text = self.lang.FilterMentions(tweet)
            text = self.lang.FilterLinks(text)
            row.update(termf.calc(text))
            frequency.append(row)
        queue.put(frequency)
    
    def Score(self):
        self.output.statusbar(len(self.frequency), title="calculating scores...")
        
        for tweet in self.frequency:
            self.output.on_status()
            row = namedtuple('tweet', 'score')
            row.tweet = tweet['analysis_text']
            row.score = 0
            for w in tweet:
                if w != 'analysis_text':
                    if w in self.kwds.negative:
                        if "no " + w in tweet['analysis_text'] or "not " + w in tweet['analysis_text']:
                           row.score += tweet[w]*10 # actually pos
                        else:
                           row.score += tweet[w]*-10
                    elif w in self.kwds.positive:
                        if "no " + w in tweet['analysis_text'] or "not " + w in tweet['analysis_text']:
                            row.score += tweet[w]*-10 # actually neg
                        else:
                            row.score += tweet[w]*10
                    else:
                        row.score += tweet[w]*0.1
            self.scores.append(row)
        self.scores = sorted(self.scores, key=lambda s: s.score, reverse=True)    
        return self.scores
    
    def Index(self):
        if self.trace: print"calculating index..."
        pos, neg, neu = 0, 0, 0
        self.train = []
        
        for x in self.scores:
            if x.score > 2:
                if self.trace: print "Positive    ", x.tweet.encode('utf-8')
                pos += x.score
                self.train.append({'text': x.tweet, 'classification': "P"})
            elif x.score < 0:
                if self.trace: print "Negative    ", x.tweet.encode('utf-8') 
                neg += x.score
                self.train.append({'text': x.tweet, 'classification': "N"})
            else:
                #if self.trace: print "Neutral    ", x.tweet 
                neu += x.score
        jpndex = int((pos + neg + neu) * 100) / 100.0
        volume = len(self.docs)
        
        print "\njapondex:", jpndex
        print "volume:  ", volume, "\n"
        
        return (jpndex, volume)
    
    def Classifier(self):
        if self.trace: 
            print "\napplying bayesian calssifier..."
        self.potency = Potency(self.train, self.lang, self.trace)
        return self.potency
    
    def WordCloud(self):
        text = "\n".join(self.docs)
        text = self.lang.FilterMentions(text)
        text = self.lang.FilterLinks(text)
        
        tokens = self.lang.Tokenize(text)
        tokens = self.lang.FilterStopwords(tokens)
        tokens = self.lang.FilterTwitterStopwords(tokens)
        tokens = self.lang.FilterCommon(tokens)
        tokens = self.lang.FilterKeywords(tokens)
        tokens = self.lang.FilterWordLength(2,tokens)
        colloc = self.lang.Collocations(tokens, 3)
        self.tokens = tokens
        
        fdist = self.lang.Frequency(tokens)
        fdist = self.lang.FilterFdistStopwords(fdist)
        words = self.lang.FilterHapaxes(fdist)
        
        if self.trace:
            print "\nWord Cloud:"
            for t in words[:50]: print t[0].encode("utf-8"), ':', t[1]

        # for n, w in enumerate(words[:101]):
        #             print "\n"+str(n)+":", w[0], w[1]
        #             for c in colloc[w[0]][:10]: print c
        return words
    
    def Chunker(self):
        self.output.statusbar(len(self.docs), title="calculating chunks...")
        chunks = []
        for tweet in self.docs:
            text = self.lang.FilterMentions(tweet)
            text = self.lang.FilterLinks(text)
            chunks.append(self.lang.Chunker(text))
            self.output.on_status()
        return chunks
    
    def TopRetweets(self, cap=10):
        self.rts = [t["text"] for t in self.mongo.db["posts"].find(
                     {"lang":"en", 'timestamp':{"$gte": self.start, "$lt": self.end}}, {"text":1,"_id":0}) 
                     if self.lang.isRetweet(t["text"])]
        counts = [(rt, self.rts.count(rt)) for rt in set(self.rts)]
        counts = sorted(counts, key=lambda tup: tup[1], reverse=True)[0:cap]
        for c in counts:
            print c[1], c[0]
    
    def TopLocations(self):
        from collections import Counter
        self.timezone = [u['user']["time_zone"] for u in self.mongo.db["posts"].find({'user.time_zone':{"$ne" : ""}, 
                        'timestamp':{"$gte": self.start, "$lt": self.end}}, {'_id':0,'user.time_zone':1})]
        self.timezone = filter(None, self.timezone)
        counts = Counter(self.timezone)
        self.locations = sorted(counts.iteritems(), key=lambda x: x[1], reverse=True)
    
        