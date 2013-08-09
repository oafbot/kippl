#!/usr/local/bin/python
import sys, os, os.path

dirname = os.path.dirname(os.path.abspath(__file__))
os.chdir(dirname)

sys.path.append( '../' )
from couch import Couch

if __name__ == "__main__":
    
    db = sys.argv[1] if len(sys.argv)>1 else ""
    couch = Couch(db=db)
    
    print "\nIndexing..."
    print couch.Index('user.screen_name')
    print couch.Index('lang')
    print couch.IndexDate('created_at')
    print ""

