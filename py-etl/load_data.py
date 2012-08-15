import argparse
import csv
from datetime import datetime
from decimal import Decimal, InvalidOperation
import os.path
import sys

from sqlalchemy import *
from sqlalchemy.orm import *
# from sqlalchemy.schema import *

from app import *
from models import *

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Load sensor data.')
    parser.add_argument('filename', help='the data file to be loaded')
    parser.add_argument('--skip-header', dest='skipheader', 
        action='store_true', help='skip the first row of data')
    parser.add_argument('--no-cache', dest='nocache', 
        action='store_true', help='don\'t cache foreign key IDs' )
    parser.add_argument('-b', '--batch-size', dest='batchsize', 
        action='store', default=10000,
        help='transaction size (in number of lines)')
    parser.add_argument('-f', '--date-format', dest='dateformat', 
        action='store', default='%Y-%m-%dT%H:%M:%S.%fZ',
        help='POSIX date format for the timestamp column')
    args = parser.parse_args()

    if (os.path.isfile(args.filename)==False):
        print "File doesn't exist: %s" % (args.filename)
        sys.exit(1)

    # Assumes first line is header if no "fieldnames" param is given:
    reader = csv.reader(open(args.filename, 'rb'), 
        delimiter='	', quoting=csv.QUOTE_NONE)
    
    if (args.skipheader):
        reader.next()
    
    initDb()
    session = getSession()

    # print "Loading raw data..."
    # for line in reader:
    #     
    #     rs = RawData(
    #         line[0], 
    #         line[1], 
    #         datetime.strptime(line[2], args.dateformat), 
    #         line[3].strip())
    # 
    #     session.add(rs)
    #     session.commit()
    # 
    # print "Converting data..."

    fkCache = {}

    print "Loading data..."
    for line in reader:
        
        envid = line[0]
        streamid = line[1]
        updated = datetime.strptime(line[2], args.dateformat)
        
        value = None
        try:
            value = Decimal(line[3].strip())
        except InvalidOperation:
            pass
        
        # Look up foreign key
        fk = None
        if (args.nocache):
            fk = getStream(session, envid, streamid)
        else:
            key = (envid, streamid)
            if (not key in fkCache):
                # print "Caching foreign key for stream %s" % str(key)
                fkCache[key] = getStream(session, envid, streamid)
            fk = fkCache[key]
        
        # Store record
        data = Data(
            fk,
            updated, 
            value)
    
        session.add(data)
        session.flush()
        
        if (reader.line_num % 1000 == 0):
            print "%d lines..." % reader.line_num

        if (reader.line_num % args.batchsize == 0):
            print "committ()"
            session.commit()

    print "%d lines." % reader.line_num
    print "committ()"
    session.commit()
