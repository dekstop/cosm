import argparse
import csv
import os.path
import sys

from sqlalchemy import *
from sqlalchemy.orm import *
# from sqlalchemy.schema import *

from app import *
from models import *

def convert(dict):
    out = {}
    for k, v in dict.iteritems():
        out[k.decode("utf-8")] = v.decode("utf-8")
        # out[unicode(k, 'utf-8')] = unicode(v, 'utf-8')
    return out

# ========
# = Main =
# ========

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Load sensor metadata.')
    parser.add_argument('envfile', help='environments metadata file')
    parser.add_argument('streamfile', help='datastreams metadata file')
    args = parser.parse_args()

    if (os.path.isfile(args.envfile)==False):
        print "File doesn't exist: %s" % (args.envfile)
        sys.exit(1)

    if (os.path.isfile(args.streamfile)==False):
        print "File doesn't exist: %s" % (args.streamfile)
        sys.exit(1)

    # init DB
    initDb()
    session = getSession()

    # first load environments
    print "Loading %s ..." % (args.envfile)
    reader = csv.DictReader(open(args.envfile, 'rb'), 
        delimiter='	', quoting=csv.QUOTE_NONE)
    
    for line in reader:
        line = convert(line)
        env = getEnvironment(session, line['ID'], line)
        session.flush()
        if (reader.line_num % 1000 == 0):
            print "%d lines..." % reader.line_num

    print "%d lines." % reader.line_num

    # then load streams
    print "Loading %s ..." % (args.streamfile)
    reader = csv.DictReader(open(args.streamfile, 'rb'), 
        delimiter='	', quoting=csv.QUOTE_NONE)
    
    for line in reader:
        line = convert(line)
        stream = getStream(session, line['ID'], line['STREAM_ID'], line)
        session.flush()
        if (reader.line_num % 1000 == 0):
            print "%d lines..." % reader.line_num

    print "%d lines." % reader.line_num

    session.commit()
