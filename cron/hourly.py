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
rt    = analysis.TopRetweets(cap=5)

output.exec_time(timer)
# try:
#     rows=[{'stamp':"'"+str(end)[:-9]+"'", 'jpndex':str(index[0]), 'volume':str(index[1])}]
#     Japondex().insert(table='jpndex', rows=rows)
# except Exception,e:
#     with open("../outputs/errors.log", "a+") as f: f.write(str(e))
# try:
#     rows=[{'stamp':"'"+str(end)[:-9]+"'", 'term':"'"+word[0].encode("utf-8")+"'", 'frequency':str(word[1])} for word in cloud[:50]]
#     Japondex().insert(table='wordcloud',rows=rows)
# except Exception,e:
#     with open("../outputs/errors.log", "a+") as f: f.write(str(e))
# try:
#     rows=[{'stamp':"'"+str(end)[:-6]+"'", 'term':"'"+word[0].encode("utf-8")+"'", 'classification':"'"+word[1].encode("utf-8")+"'"} for word in bayes.top[:35]]
#     Japondex().insert(table='predictors',rows=rows)
# except Exception,e:
#     with open("../outputs/errors.log", "a+") as f: f.write(str(e))
try:
    rows=[{'stamp':"'"+str(end)[:-6]+"'", 'retweet':"'"+t[0].encode("utf-8")+"'", 'count':t[1]} for t in rt]
    Japondex().insert(table='retweets',rows=rows)
except Exception,e:
    with open("../outputs/errors.log", "a+") as f: f.write(str(e))
