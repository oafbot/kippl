#!/usr/local/bin/python
import sys, os, os.path

dirname = os.path.dirname(os.path.abspath(__file__))
os.chdir(dirname)

sys.path.append( '../' )
from twitbot import TwitBot
from inputs.config import Config
from inputs.dicts import Keywords
from search import SearchTwitterREST
from stream import SearchTwitterStream
from csvhelper import CsvHelper


"""Handle command line args."""
    
"""Initialize Twitter bot."""
config = Config()
bot = TwitBot(
    user=config.user,
    consumer_key=config.consumer_key,
    consumer_secret=config.consumer_secret,
    access_token_key=config.access_token_key,
    access_token_secret=config.access_token_secret)

csv = CsvHelper(path="../outputs/users.csv", 
                columns=["Keyword","UserId","Username","Name","Location","Listed","Followers",
                         "Verified","Protected","Description","Language","Statuses","CreatedOn","Url"])

"""Initialize keywords and search."""
keywords = Keywords()
for term in keywords.obvious:
    print "-----------", term
    users = bot.Request(bot.UserSearch, term=term)
    if users:
        for user in users:
            location = "None" if user.location is None else user.location
            description = "None" if user.description is None else user.description
            url = "None" if user.url is None else user.url
            
            location = csv.Scrub(location)
            description = csv.Scrub(description)
            date = csv.Scrub(user.created_at)
            url = csv.Scrub(url)
            
            csv.LineIn([
                term,
                str(user.id),
                user.screen_name,
                user.name,
                location,
                str(user.listed_count),
                str(user.followers_count),
                str(user.verified),
                str(user.protected),
                description,
                user.lang,
                str(user.statuses_count),
                date,
                url
            ])
            csv.LineOut()
    else:
        print "No Users!!"
csv.Close()
