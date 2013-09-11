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
    
    """Initialize Twitter bot."""
    config = Config()
    bot = TwitBot(
        user=config.user,
        consumer_key=config.consumer_key,
        consumer_secret=config.consumer_secret,
        access_token_key=config.access_token_key,
        access_token_secret=config.access_token_secret)
    
    """Handle command line args."""
    db = sys.argv[1]  if len(sys.argv)>1 else config.db
    kw = sys.argv[2:] if len(sys.argv)>2 else [db]
    
    """Initialize keywords and search."""
    k = Keywords(keywords=kw).keywords
    SearchTwitterStream(keywords=k, db=db)