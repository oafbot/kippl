import nltk
from inputs.dicts import Keywords

class LanguageKit:
    def __init__(self):
        keywords = Keywords()
        self.stopset = set(nltk.corpus.stopwords.words('english'))
        self.tokens = []
        self.common = keywords.common
        self.positive = keywords.positive
        self.negative = keywords.negative
                                                 
    def Tokenize(self, txt):
        tokenizer = nltk.tokenize.RegexpTokenizer("[\w']+")
        #tokens = nltk.word_tokenize(txt) # tokenize text
        for word in tokenizer.tokenize(txt):
            word = word.lower()
            # if word.isalpha(): # drop all non-words
            self.tokens.append(word)
        return self.tokens
    
    def Frequency(self, words):
        self.fdist = nltk.FreqDist(words)
        self.vocab = self.fdist.keys()
        self.hapaxes = self.fdist.hapaxes()
        return self.fdist

    def Collocations(self, words):
        # from nltk import bigrams
        import nltk.collocations
        import nltk.corpus
        import collections

        bgm    = nltk.collocations.BigramAssocMeasures()
        finder = nltk.collocations.BigramCollocationFinder.from_words(words)
        scored = finder.score_ngrams( bgm.likelihood_ratio  )

        # Group bigrams by first word in bigram.                                        
        prefix_keys = collections.defaultdict(list)
        for key, scores in scored:
           prefix_keys[key[0]].append((key[1], scores))

        # Sort keyed bigrams by strongest association.                                  
        for key in prefix_keys:
           prefix_keys[key].sort(key = lambda x: -x[1])
        
        return prefix_keys
        
        # print 'doctor', prefix_keys['doctor'][:5]
        # print 'baseball', prefix_keys['baseball'][:5]
        # print 'happy', prefix_keys['happy'][:5]

    
    def FilterMentions(self, text):
        import re
        text = re.sub('@([A-Za-z0-9_]+)', "", text)
        text = re.sub('/@(\w+)\s\b/i', "", text)
        return text
        
    def FilterLinks(self, text):
        import re
        text = re.sub('http://',"", text)
        text = re.sub('t.co/.*', "", text)
        text = re.sub('^[a-zA-Z0-9\-\.]+\.(com|org|net|mil|edu|COM|ORG|NET|MIL|EDU)$',"", text)
        return text
    
    def isRetweet(self, tweet):
        import re
        return True if re.match('^RT', tweet) else False
    
    def FilterRetweets(self, tweet):
        import re
        return "" if re.match('^RT', tweet) else tweet
    
    def FilterFdistStopwords(self, words):
        filtered = dict([(word, words[word]) for word in words 
                        if word not in self.stopset and word not in self.common])
        return sorted(filtered.items(), key=lambda x: x[1], reverse=True)

    def FilterStopwords(self, words):
        filtered = [word for word in words 
                        if word not in self.stopset and word not in self.common]
        return filtered
    
    def FilterWordLength(self, length, words):
        longer = [w for w in words if len(w[0]) > length]
        longer = [(w[0].lower(), w[1] ) for w in longer]
        return longer
    
    def FilterHapaxes(self, words):
        return [w for w in words if w[0] not in self.hapaxes]
        
    def Intersection(self, a, b):
        intersection=[]
        for tup1 in a:
            for tup2 in b:
                if tup1[0] in tup2:
                    intersection.append(tup1[0])
        return list(set(intersection))

    def Difference(self, words, intersection):
        difference=[]
        for tup in words:
            if tup[0] not in intersection:
                difference.append(tup)
        return list(set(difference))
        # for t in sorted(diff1): print t[0], ':', t[1]
        
    def LoadFile(self, path, file):
        return nltk.corpus.PlaintextCorpusReader(path, file)
