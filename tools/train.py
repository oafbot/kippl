import sys, os, os.path, cPickle as pickle
dirname = os.path.dirname(os.path.abspath(__file__))
os.chdir(dirname)

sys.path.append( '../' )
from lang.potency import Potency

train1 = pickle.load(open('../outputs/trainset-0-99.pk'))
train2 = pickle.load(open('../outputs/trainset-100-200.pk'))
train3 = pickle.load(open('../outputs/trainset-200-300.pk'))
train4 = pickle.load(open('../outputs/trainset-300-1000.pk'))
train5 = pickle.load(open('../outputs/trainset-1000-2000.pk'))
train6 = pickle.load(open('../outputs/trainset-2000-3000.pk'))
train  = train1 + train2 + train3 + train4 + train5 + train6

potency = Potency(train)