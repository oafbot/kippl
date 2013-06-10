import sys, os, os.path
import twitter

dirname = os.path.dirname(os.path.abspath(__file__))
os.chdir(dirname)

sys.path.append( '../' )
from twitbot import TwitBot
from inputs.config import Config

config = Config()
bot = TwitBot(
    user=config.user,
    consumer_key=config.consumer_key,
    consumer_secret=config.consumer_secret,
    access_token_key=config.access_token_key,
    access_token_secret=config.access_token_secret)

import tweepy
config = Config()
auth = tweepy.OAuthHandler(config.consumer_key, config.consumer_secret)
auth.set_access_token(config.access_token_key, config.access_token_secret)
api = tweepy.API(auth) # Don't forget to use authentication for private lists/users.

from couch import Couch
couch = Couch(db="diabetes")

users=[]
#SSEMt
# listnames = ['ClubDiabetes','ClubDiabetes1','ClubDiabetes2','ClubDiabetes3']
listnames = ['ClubDiabetes']
for listname in listnames:
    # Iterate through all members of the owner's list
    for member in tweepy.Cursor(api.list_members, 'DiabeticFury', listname).items():
        users.append(member.id)
        print member.screen_name
        # tweets = bot.Request(bot.Timeline, bot, member.screen_name, count=100, since=self.couch.MaxTweetId())
        tweets = bot.History(member.screen_name)
        print len(tweets)
        if len(tweets)>0:
            couch.Update(tweets)
