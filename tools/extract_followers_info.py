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

# members = bot.api.GetListMembers('ClubDiabetes')


def GetListMembers(list_slug, owner_id, cursor=-1):
    # mostly copied from the GetFriends method in
    # https://github.com/bear/python-twitter/blob/master/twitter.py
    url = '%s/lists/members.json' % (bot.api.base_url)
    parameters = {"cursor":cursor, "slug":list_slug, "owner_id": owner_id}
    json = bot.api._FetchUrl(url, parameters=parameters)
    data = bot.api._ParseAndCheckTwitter(json)
    return [twitter.User.NewFromJsonDict(x) for x in data['users']]

# lists = bot.api.GetLists(screen_name='DiabeticFury')
# for l in lists: print l

# user = bot.api.GetUser(screen_name='DiabeticFury')
# members = GetListMembers('ClubDiabetes1', user.id)
# print [m.name for m in members]

import tweepy
config = Config()
auth = tweepy.OAuthHandler(config.consumer_key, config.consumer_secret)
auth.set_access_token(config.access_token_key, config.access_token_secret)
api = tweepy.API(auth) # Don't forget to use authentication for private lists/users.

users=[]
count=0

csv = CsvHelper(path="../outputs/list.csv", 
                columns=["Id","List","UserId","Username","Statuses", "Followers"])
listnames = ['ClubDiabetes','ClubDiabetes1','ClubDiabetes2','ClubDiabetes3']

for listname in listnames:
    # Iterate through all members of the owner's list
    for member in tweepy.Cursor(api.list_members, 'DiabeticFury', listname).items():
        users.append(member.id)

    start=0
    end=99
    while len(users)-1 > end:
        usersdump = bot.api.UsersLookup(user_id=users[start:end])
        for u in usersdump:
            print "statuses:", u.statuses_count, "followers:", u.followers_count
            csv.LineIn([str(count),listname,str(u.id),u.screen_name,str(u.statuses_count), str(u.followers_count)])
            csv.LineOut()
            count+=1
        start = end+1
        end = end+99 if end+99 < len(users)-1 else len(users)-1
csv.Close()