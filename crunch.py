from analysis import Analysis
from datetime import timedelta, datetime
from util.output import Output

timer  = datetime.now()
output = Output()

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
    

ts = datetime(2013, 9, 7)
for d in range(0,1):
    start = ts + timedelta(days=d)
    end   = ts + timedelta(days=d+1)

    # start = datetime(2013, 7, 1)
    # end  = datetime(2013, 9, 12)
    analysis = Analysis("japan", ["japan", "japanese"], start, end)

    tfidf = analysis.TFIDF()
    score = analysis.Score()
    index = analysis.Index()
    cloud = analysis.WordCloud()
    bayes = analysis.Classifier()

    output.exec_time(timer)