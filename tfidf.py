import math

class TermFrequency:    
    def __init__(self, doc, doclist):
        self.doc = self.tokenize(doc)
        self.doclist = doclist
    
    def tokenize(self, txt, keywords=[], filter=False):
        from languagekit import LanguageKit
        from inputs.dicts import Keywords

        lang = LanguageKit(Keywords(keywords))
        if filter:
            tokens = lang.Tokenize(txt)
            tokens = lang.FilterStopwords(tokens)
            tokens = lang.FilterWordLength(2, tokens)
        else:
            tokens = lang.Tokenize(txt)
        return tokens
    
    def freq(self, word, doc):
        return doc.count(word)

    def wordcount(self):
        return len(self.doc)

    def tf(self, word):
        return (self.freq(word, self.doc) / float(self.wordcount()))

    def containing(self, word):
        count = 0
        for document in self.doclist:
            if self.freq(word, self.tokenize(document)) > 0:
                count += 1
        return 1 + count

    def idf(self, word):
        return math.log(len(self.doclist) / float(self.containing(word)))

    def tf_idf(self, word):
        return (self.tf(word) * self.idf(word))
        
    def calc(self, words, kw):
        dic = {}
        for w in self.tokenize(words, keywords=kw, filter=True):
            dic[w] = self.tf_idf(w)
        return dic