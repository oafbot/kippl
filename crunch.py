from analysis import Analysis
from datetime import timedelta, datetime
from util.output import Output
from db.jpndex import Japondex

timer  = datetime.now()
output = Output()

h = 0
start = datetime(2013, 7, 27, 5)
while start < datetime(2013, 8, 2, 8):

     start = datetime(2013, 7, 27, 5) + timedelta(hours=h)
     end   = datetime(2013, 7, 27, 5) + timedelta(hours=h+1)
     analysis = Analysis("japan", ["japan", "japanese"], start, end)
     if analysis.docs:
         tfidf = analysis.TFIDF()
         score = analysis.Score()
         index = analysis.Index()
         cloud = analysis.WordCloud()
         bayes = analysis.Classifier()
         output.exec_time(timer)
         h += 1
         rows=[{'stamp':"'"+str(start)+"'", 'jpndex':str(index[0]), 'volume':str(index[1])}]
         Japondex().insert(table='jpndex', rows=rows)
         rows=[{'stamp':"'"+str(start)+"'", 'term':"'"+word[0].encode("utf-8")+"'", 'frequency':str(word[1])} for word in cloud[:50]]
         Japondex().insert(table='wordcloud',rows=rows)




#ts = datetime(2013, 9, 7)
#for d in range(0,1):
#    start = ts + timedelta(days=d)
#    end   = ts + timedelta(days=d+1)
#
#    # start = datetime(2013, 7, 1)
#    # end  = datetime(2013, 9, 12)
#    analysis = Analysis("japan", ["japan", "japanese"], start, end)
#
#    tfidf = analysis.TFIDF()
#    score = analysis.Score()
#    index = analysis.Index()
#    cloud = analysis.WordCloud()



# for h in range(0,5):
#     start = datetime(2013, 7, 11, 18) + timedelta(hours=h)
#     end   = datetime(2013, 7, 11, 19) + timedelta(hours=h)
#     
#     analysis = Analysis("japan", ["japan", "japanese"], start, end)
#     analysis.TFIDF()
#     analysis.Score()
#     analysis.Index()
#     analysis.WordCloud()
#     # analysis.ExecTime()
#     # analysis.Classifier()
    

# ts = datetime(2013, 9, 7)
# for d in range(0,1):
#     start = ts + timedelta(days=d)
#     end   = ts + timedelta(days=d+1)
# 
#     # start = datetime(2013, 7, 1)
#     # end  = datetime(2013, 9, 12)
#     analysis = Analysis("japan", ["japan", "japanese"], start, end)
# 
#     tfidf = analysis.TFIDF()
#     score = analysis.Score()
#     index = analysis.Index()
#     cloud = analysis.WordCloud()
#     bayes = analysis.Classifier()
# 
#     output.exec_time(timer)