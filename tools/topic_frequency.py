import csv
import sys, os, os.path
import twitter

dirname = os.path.dirname(os.path.abspath(__file__))
os.chdir(dirname)

sys.path.append( '../' )
from twitbot import TwitBot
from inputs.config import Config
from csvhelper import CsvHelper

config = Config()
bot = TwitBot(
    user=config.user,
    consumer_key=config.consumer_key,
    consumer_secret=config.consumer_secret,
    access_token_key=config.access_token_key,
    access_token_secret=config.access_token_secret)

csvout = CsvHelper(path="../outputs/list2.csv", 
                columns=["Id","List","UserId","Username","Statuses","OnTopic","Frequency"])
                
with open('../outputs/list.csv', 'rb') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for num, row in enumerate(reader):
        if num != 0 and row[1]=="ClubDiabetes2":
            term = "@"+row[3]+" "+"diabetes"
            search = bot.Request(bot.Search, term=term, count=100, page=1, lang="en")
            count = len(search) if search else 0
            # denom = int(row[5]) 
            # perc = float(count / int(row[5]))*100 if int(row[5]) > 0 else 0
            
            if count > 0:
               perc = float(count) / float(row[5])*100
            else:
                perc = 0.0
            print row[3]+",", str(count)+",", str(perc)+"%"
            csvout.LineIn([row[0],row[1],row[2],row[3],row[5],str(count),str(perc)])
            csvout.LineOut()
csvout.Close()            
# with open('../outputs/list2.csv', 'wb') as f:
#     writer = csv.writer(f)
#     writer.writerows(counts)              
