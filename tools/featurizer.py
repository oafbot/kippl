#!/usr/local/bin/python
import sys, os, os.path, termios, fcntl
dirname = os.path.dirname(os.path.abspath(__file__))
os.chdir(dirname)

sys.path.append( '../' )
from mongo import Mongo
from lang.languagekit import LanguageKit
from inputs.dicts import Keywords

fd = sys.stdin.fileno()
oldterm = termios.tcgetattr(fd)
newattr = termios.tcgetattr(fd)
newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
termios.tcsetattr(fd, termios.TCSANOW, newattr)

oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)

if __name__ == "__main__":
    
    # db = sys.argv[1] if len(sys.argv)>1 else ""
    mongo = Mongo(db="japan")
    kwds  = Keywords(keywords=["japan", "japanese"])
    lang  = LanguageKit(keywords=kwds)
    
    doclist = [lang.FilterRetweets(t["text"]) for t in mongo.db["posts"].find(
                                {"lang":"en"},{"text":1,"_id":0})]                                
    count = 0
    
    try:
        while 1:
            try:
                c = sys.stdin.read(1)
                if not c:
                   print doclist[count],
                elif c:
                    count += 1
                    print repr(c)
                    print doclist[count]
            except IOError: pass
    finally:
        termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
        fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)