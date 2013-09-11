import nltk, random
from languagekit import LanguageKit
from inputs.dicts import Keywords

class Potency:
    def __init__(self, tweets):
        print "positive:", len([t['text'] for t in tweets if t['classification'] == 'P'])
        print "negative:", len([t['text'] for t in tweets if t['classification'] == 'N'])
        
        postext = "\n".join(list(t['text'] for t in tweets if t['classification'] == 'P'))
        negtext = "\n".join(list(t['text'] for t in tweets if t['classification'] == 'N'))
                
        self.pos = [(word,'P') for word in self.tokenize(postext)]
        self.neg = [(word,'N') for word in self.tokenize(negtext)]    
                
        words = self.pos + self.neg
        # random.shuffle(words)
        self.features = [(self.featurize(w), a) for (w,a) in words]
        self.trainset = self.features[:len(self.features)*3/4]
        self.testset  = self.features[len(self.features)*3/4:]
        # trainset = featuresets
        self.classifier = nltk.NaiveBayesClassifier.train(self.trainset)
        
        self.classifier.show_most_informative_features(50)
        print "accuracy:", nltk.classify.accuracy(self.classifier, self.testset)

        self.top = [t[1] for t in self.classifier.most_informative_features(50)]

    def featurize(self, word):
        return {'word': word}
    
    def tokenize(self, text):
        kwds   = Keywords(keywords=["japan", "japanese"])
        lang   = LanguageKit(keywords=kwds)
        text   = lang.FilterMentions(text)
        text   = lang.FilterLinks(text)
        
        tokens = lang.Tokenize(text)
        tokens = lang.FilterWordLength(2, tokens)
        # tokens = lang.FilterKeywords(tokens)
        tokens = lang.FilterStopwords(tokens)
        # tokens = lang.FilterCommon(tokens)
        # tokens = lang.CollocationPairs(tokens)
        
        return tokens
        
    def Scores(self):
        self.wordscores = {}

        for (label, fname), probdist in self.classifier._feature_probdist.items():
            for fval in probdist.samples():
                self.wordscores[fval] = probdist.prob(fval)
        
        scores = sorted(self.wordscores, key=lambda s: self.wordscores[s], reverse=True)  
        
        for w in scores:
            print str(self.wordscores[w]), "\t", w