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
        self.docs  = list(set(filter(None, self.docs)))
        self.frequency = []
        self.scores    = []
        self.output    = Output()
        self.trace     = Config().out
        self.multicore = Multicore()
    
    def TFIDF(self, cores=mp.cpu_count()):
        termf = TermFrequency(self.docs, lang=self.lang)
        
        if self.trace:
            print "\ncalculating tfidf..."
            self.output.status_start("Processed")
        
        self.frequency = self.multicore.run(func=self.ProcessTFIDF, tasks=self.docs, args=(termf,))
        
        if self.trace: 
            self.output.status_end("Processed")
        return self.frequency
    
    def ProcessTFIDF(self, termf, queue=None, pid=None, tasks=None):
        frequency = []
        count = 0.0        
        for tweet in tasks:
            if pid==0 and self.trace:
                self.output.statusbar(count, len(tasks), "Processed")
                count += 1.00
            row = {'analysis_text': tweet.replace("\n", " ")}
            text = self.lang.FilterMentions(tweet)
            text = self.lang.FilterLinks(text)
            row.update(termf.calc(text))
            frequency.append(row)
        queue.put(frequency)
    
    def Score(self):
        if self.trace: 
            print"calculating scores..."
            self.output.status_start("Processed")
            count = 0.0
        
        for tweet in self.frequency:
            if self.trace:
                self.output.statusbar(count, len(self.frequency), "Processed")
                count += 1
            
            row = namedtuple('tweet', 'score')
            row.tweet = tweet['analysis_text']
            row.score = 0
            for w in tweet:
                if w != 'analysis_text':
                    if w in self.kwds.negative:
                        if "no " + w in tweet['analysis_text'] or "not " + w in tweet['analysis_text']:
                           # print "actually pos"
                           row.score += tweet[w]*10
                        else:
                           row.score += tweet[w]*-10
                    elif w in self.kwds.positive:
                        if "no " + w in tweet['analysis_text'] or "not " + w in tweet['analysis_text']:
                            # print "actually neg"
                            row.score += tweet[w]*-10
                        else:
                            row.score += tweet[w]*10
                    else:
                        row.score += tweet[w]*0.1
            self.scores.append(row)
        
        self.scores = sorted(self.scores, key=lambda s: s.score, reverse=True)    
        
        if self.trace: self.output.status_end("Processed")
        
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
        colloc = self.lang.Collocations(tokens)
        
        words = self.lang.FilterKeywords(tokens)
        words = self.lang.FilterWordLength(3,words)
        
        fdist = self.lang.Frequency(words)
        fdist = self.lang.FilterFdistStopwords(fdist)
        words = self.lang.FilterHapaxes(fdist)
        
        if self.trace:
            print "\nWord Cloud:"
            for t in words[:50]: print t[0].encode("utf-8"), ':', t[1]
        
        # for n, w in enumerate(words[:101]):
        #     print "\n"+str(n)+":", w[0], w[1]
        #     for c in colloc[w[0]][:10]: print c
        
        return words
    
    def Chunker(self):
        self.output.status_start(title="calculating chunks...", trace=self.trace)
        chunks = []
        for tweet in self.docs:
            text = self.lang.FilterMentions(tweet)
            text = self.lang.FilterLinks(text)
            chunks.append(self.lang.Chunker(text))
            self.output.statusbar(len(self.docs))
        return chunks
    
