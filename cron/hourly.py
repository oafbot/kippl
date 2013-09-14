# if __name__ == "__main__" and __package__ is None:
#     __package__ = "cron"

from datetime import timedelta, datetime
import sys, os, os.path

dirname = os.path.dirname(os.path.abspath(__file__))
os.chdir(dirname)
sys.path.append( '../' )
from analysis import Analysis
from util.output import Output
from db.jpndex import Japondex

timer  = datetime.now()
output = Output()

start = datetime(2013, 7, 11, 22) + timedelta(hours=-1)
end   = datetime(2013, 7, 11, 22)

analysis = Analysis("japan", ["japan", "japanese"], start, end)

tfidf = analysis.TFIDF()
score = analysis.Score()
index = analysis.Index()
cloud = analysis.WordCloud()
bayes = analysis.Classifier()

output.exec_time(timer)
rows={'stamp':"'"+str(start)+"'", 'jpndex':str(index[0]), 'volume':str(index[1])}
Japondex().insert(table='jpndex', rows=rows)
