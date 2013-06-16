#!/usr/local/bin/python
import sys, os, os.path

from twitbot import TwitBot
from inputs.config import Config
from inputs.dicts import Keywords
from search import SearchTwitterREST
from stream import SearchTwitterStream

if __name__ == "__main__":
    dirname = os.path.dirname(os.path.abspath(__file__))
    os.chdir(dirname)
    """Handle command line args."""
        
    """Initialize Twitter bot."""
    config = Config()
    bot = TwitBot(
        user=config.user,
        consumer_key=config.consumer_key,
        consumer_secret=config.consumer_secret,
        access_token_key=config.access_token_key,
        access_token_secret=config.access_token_secret)
    
    """Initialize keywords and search."""
    # keywords = Keywords()
    # SearchTwitterREST(keywords, bot)
    # SearchTwitterStream(keywords=keywords.allwords)    
    # bot.GetFriends("oafbot")
    SearchTwitterStream(keywords=['japan'], db="japan")
    # from test import Test
    # test=Test(bot)