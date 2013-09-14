import math
from languagekit import LanguageKit
# from inputs.dicts import Keywords

class TermFrequency:    
    def __init__(self, corpus, lang=LanguageKit()):
        self.lang   = lang
        self.corpus = corpus
        self.length = len(corpus)
    
    def filter(self, doc):
        tokens = self.lang.FilterStopwords(doc)
        tokens = self.lang.FilterWordLength(2, tokens)
        tokens = self.lang.FilterKeywords(tokens)
        return tokens
    
    def freq(self, word, doc):
        return doc.count(word)
    
    def tf(self, word, doc):
        return (self.freq(word, doc) / float(len(doc)))
    
    def containing(self, word):
        count = 1
        for doc in self.corpus:
            if word in doc: count += 1
        return count
    
    def idf(self, word):
        return math.log(self.length / float(self.containing(word)))
    
    def tf_idf(self, word, doc):
        return (self.tf(word, doc) * self.idf(word))
    
    def calc(self, text):
        dic = {}
        doc = self.lang.Tokenize(text)
        for w in self.filter(doc):
            dic[w] = self.tf_idf(w, doc)
        return dic
    