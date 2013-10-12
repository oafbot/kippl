import nltk, re
from inputs.dicts import Keywords

class LanguageKit:
    def __init__(self, keywords=Keywords()):
        self.stopset = set(nltk.corpus.stopwords.words('english'))
        self.common  = keywords.common + keywords.common2
        self.positive = keywords.positive
        self.negative = keywords.negative
        self.keywords = keywords.keywords
        self.spamlist = keywords.spamlist
		self.stoptwit = keywords.stoptweets
        self.scanned  = []
        self.redundant= []
        self.possible_spam = []
    
    def LoadFile(self, path, file):
        return nltk.corpus.PlaintextCorpusReader(path, file)
    
    def Tokenize(self, txt):
        # hyphen = r'(\w+\-\s?\w+)'
        # wordr = r"[\w']+"
        # regx = "|".join([ hyphen, wordr])
        regx = "\w+-\w+|[\w']+"
        #"[\w']+"
        tokenizer = nltk.tokenize.RegexpTokenizer(regx)
        #tokens = nltk.word_tokenize(txt) # tokenize text
        tokens = []
        txt = self.StripHtml(txt)
        for word in tokenizer.tokenize(txt):
            word = word.lower()
            if word.isalpha() or all(w.isalpha() for w in word.split("-")): # drop all non-words
                word = nltk.WordNetLemmatizer().lemmatize(word)
                tokens.append(word)
        return tokens
    
    def Frequency(self, words):
        self.fdist = nltk.FreqDist(words)
        self.vocab = self.fdist.keys()
        self.hapaxes = self.fdist.hapaxes()
        return self.fdist
    
    def Collocations(self, words, ngram=3):
        # from nltk import bigrams
        import nltk.collocations
        import nltk.corpus
        import collections
        
        if ngram is 3:
            tgm    = nltk.collocations.TrigramAssocMeasures()
            finder = nltk.collocations.TrigramCollocationFinder.from_words(words)
            scored = finder.score_ngrams( tgm.likelihood_ratio  )
        elif ngram is 2:
            bgm    = nltk.collocations.BigramAssocMeasures()
            finder = nltk.collocations.BigramCollocationFinder.from_words(words)
            scored = finder.score_ngrams( bgm.likelihood_ratio  )
        
        # Group bigrams by first word in bigram.                                        
        prefix_keys = collections.defaultdict(list)
        for key, scores in scored:
           prefix_keys[key[0]].append((key, scores))

        # Sort keyed bigrams by strongest association.                                  
        for key in prefix_keys:
           prefix_keys[key].sort(key = lambda x: -x[1])
        
        return prefix_keys
        
        # print 'doctor', prefix_keys['doctor'][:5]
        # print 'baseball', prefix_keys['baseball'][:5]
        # print 'happy', prefix_keys['happy'][:5]
    
    def CollocationPairs(self, words, n):
        colloc = self.Collocations(words, n)
        ngrams = []
        for c in colloc:
            for w in colloc[c]:
                if w: ngrams.append((c, w[0]))
        return ngrams
    
    def StripHtml(self, text):
        import lxml.html
        try:
            text = lxml.html.tostring(text)
        except:
            text = text.replace("&amp;", "&")
        return text
    
    def FilterMentions(self, text):
        text = re.sub('@([A-Za-z0-9_]+)', "", text)
        text = re.sub('/@(\w+)\s\b/i', "", text)
        return text
    
    def FilterLinks(self, text):
        text = re.sub('http://',"", text)
        text = re.sub('http',"", text)
        text = re.sub('t.co/.*', "", text)
        text = re.sub('^[a-zA-Z0-9\-\.]+\.(com|org|net|mil|edu|COM|ORG|NET|MIL|EDU)$',"", text)
        return text
    
    def isRetweet(self, tweet):
        return True if re.match('^RT', tweet) else False
    
    def FilterRetweets(self, tweet):
        return "" if re.match('^RT', tweet) else tweet
    
    def FilterFdistStopwords(self, words):
        filtered = dict([(word, words[word]) for word in words 
                        if word not in self.stopset and word not in self.common
                        and word not in self.keywords])
        return sorted(filtered.items(), key=lambda x: x[1], reverse=True)
    
    def FilterKeywords(self, words):
        filtered = [word for word in words if word not in self.keywords]
        return filtered
    
    def FilterStopwords(self, words):
        filtered = [word for word in words if word not in self.stopset and word]
        return filtered
	
    def FilterTwitterStopwords(self, words):
		return [word for word in words if word not in self.stoptwit and word]	
	
    def FilterCommon(self, words):
        filtered = [word for word in words if word not in self.common and word]
        return filtered
    
    def FilterWordLength(self, length, words):
        longer = [w for w in words if len(w) > length]
        # longer = [(w[0].lower(), w[1] ) for w in longer]
        return longer
    
    def FilterHapaxes(self, words):
        return [w for w in words if w[0] not in self.hapaxes]
    
    def FilterRedundant(self, docs):
        pass
    
    def FilterSpam(self, corpus):
        corp = []
        for doc in corpus:
            if any(spam for spam in self.spamlist if spam in doc.lower()):
                pass
            else:
                corp.append(doc)
        # corp = [doc for doc in corpus for spam in self.spamlist if spam not in doc.lower()]
        return list(set(filter(None, corp)))
    
    def FilterPositive(self, tokens):
        return [word for word in tokens if word not in self.positive]
    
    def FilterNegative(self, tokens):
        return [word for word in tokens if word not in self.negative]
    
    def SimpleSpamFilter(self, docs):
        import string
        corpus = []
        
        for text in docs:
            t = self.FilterMentions(text)
            t = self.FilterLinks(t)
            t = re.sub(re.compile(r'\s+'), ' ', t)
            # t = ' '.join(t.split())
            t = ''.join([i for i in t if i not in set(string.punctuation)])
            t = ''.join([i for i in t if not i.isdigit()])
            t = t.strip().lower()
            
            if t not in self.scanned and t:
                if self.possible_spam:
                    for spam in self.possible_spam:
                        if re.search(re.escape(t),spam) or re.search(re.escape(spam),t):
                            # self.redundant.append(text)
                            self.possible_spam.append(t)
                            self.possible_spam = list(set(self.possible_spam))
                        else:
                            corpus.append(text)
                else: corpus.append(text)
                self.scanned.append(t)
            elif t:
                # self.redundant.append(text)
                self.possible_spam.append(t)
                self.possible_spam = list(set(self.possible_spam))
        return list(set(filter(None, corpus)))
            
    
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
    
    def Postag(self, text):
        sentences = nltk.sent_tokenize(text)
        sentences = [nltk.word_tokenize(sent) for sent in sentences]
        sentences = [nltk.pos_tag(sent) for sent in sentences]
        return sentences
    
    def Chunker(self, text):
        sents = self.Postag(text)
        # grammar = "NP: {<DT>?<JJ>*<NN>}"
        grammar = """
        NP: {<DT>? <JJ>* <NN>*} # NP 
        P: {<IN>}           # Preposition
        V: {<V.*>}          # Verb
        PP: {<P> <NP>}      # PP -> P NP
        VP: {<V> <NP|PP>*}  # VP -> V (NP|PP)*
        """
        cp = nltk.RegexpParser(grammar)
        # sents = [x for x in sents if x]
        return [cp.parse(s) for s in sents if s]
        # result.draw()
    