# if __name__ == "__main__" and __package__ is None:
#     __package__ = "cron"

from datetime import timedelta, datetime
import sys, os, os.path, pytz


dirname = os.path.dirname(os.path.abspath(__file__))
os.chdir(dirname)
sys.path.append( '../' )
from analysis import Analysis
from util.output import Output
from db.jpndex import Japondex

timer  = datetime.now()
output = Output()
now    = datetime.utcnow().replace(tzinfo=pytz.utc, minute=0, second=0, microsecond=0)

start = now + timedelta(hours=-1)
end   = now 

analysis = Analysis("japan", ["japan", "japanese"], start, end)

tfidf = analysis.TFIDF()
score = analysis.Score()
index = analysis.Index()
cloud = analysis.WordCloud()
bayes = analysis.Classifier()

output.exec_time(timer)
rows=[{'stamp':"'"+str(end)[:-9]+"'", 'jpndex':str(index[0]), 'volume':str(index[1])}]
Japondex().insert(table='jpndex', rows=rows)
rows=[{'stamp':"'"+str(end)[:-9]+"'", 'term':"'"+word[0].encode("utf-8")+"'", 'frequency':str(word[1])} for word in cloud[:50]]
Japondex().insert(table='wordcloud',rows=rows)
