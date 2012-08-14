import ConfigParser
from datetime import datetime
from decimal import Decimal, InvalidOperation
import os

from sqlalchemy import *
from sqlalchemy.orm import *

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

from models import *

# ==============
# = DB Session =
# ==============

config = None
db = None
Session = None
session = None

def getConfig():
    global config
    if (config==None):
        SETTINGS_FILE=os.environ['SETTINGS_FILE']
        config = ConfigParser.ConfigParser()
        config.readfp(open(SETTINGS_FILE))
    return config

def getDb():
    global db
    if (db==None):
        db = create_engine(getConfig().get('db', 'uri'))
        # db.echo = True
    return db

def initDb():
    Base.metadata.create_all(getDb())

def getSession():
    global Session, session
    if (Session==None):
        Session = sessionmaker(bind=getDb())
    if (session==None):
        session = Session()
    return session

# ==================
# = SQL Constructs =
# ==================

from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import ColumnClause

class ToIsoDate(ColumnClause):
    pass

@compiles(ToIsoDate, 'postgresql')
def compile_toisodate(element, compiler, **kw):
    return "TO_CHAR(%s, 'YYYY-MM-DDTHH24:MI:SS')" % element.name
    
@compiles(ToIsoDate, 'sqlite')
def compile_toisodate(element, compiler, **kw):
    return "strftime('%%Y-%%m-%%dT%%H:%%M:%%S', %s)" % element.name


class ToHour(ColumnClause):
    pass

@compiles(ToHour, 'postgresql')
def compile_tohour(element, compiler, **kw):
    return "TO_CHAR(%s, 'YYYY-MM-DDTHH24:00:00')" % element.name
    
@compiles(ToHour, 'sqlite')
def compile_tohour(element, compiler, **kw):
    return "strftime('%%Y-%%m-%%dT%%H:00:00', %s)" % element.name


class ToDay(ColumnClause):
    pass

@compiles(ToDay, 'postgresql')
def compile_today(element, compiler, **kw):
    return "TO_CHAR(%s, 'YYYY-MM-DD')" % element.name
    
@compiles(ToDay, 'sqlite')
def compile_today(element, compiler, **kw):
    return "strftime('%%Y-%%m-%%d', %s)" % element.name

# ========
# = Util =
# ========

# See http://www.peterbe.com/plog/uniqifiers-benchmark
# This is not order preserving.
def unique(seq):
    return {}.fromkeys(seq).keys()

# =======
# = ORM =
# =======

def getTag(session, name):
    try:
      return session.query(Tag).filter_by(name=name).one()
    except:
      tag = Tag(name)
      session.add(tag)
      return tag

def getTags(session, names):
    tags = []
    for name in unique(names):
        tags.append(getTag(session, name))
    return tags

def getEnvironment(session, id, dict):
    try:
        return session.query(Environment).filter_by(id=id).one()
    except:
        env = Environment(id)

        env.creator = dict['CREATOR']
        env.created = datetime.strptime(dict['CREATED_AT'], '%Y-%m-%dT%H:%M:%S.%fZ')
        env.updated = datetime.strptime(dict['UPDATED_AT'], '%Y-%m-%dT%H:%M:%S.%fZ')
        env.title = dict['TITLE']
        env.feed = dict['FEED']
        env.status = dict['STATUS']
        env.private = dict['PRIVATE']
        env.location = dict['LOCATION']
        env.location_domain = dict['LOCATION_DOMAIN']
        env.location_exposure = dict['LOCATION_EXPOSURE']
        env.location_disposition = dict['LOCATION_DISPOSITION']
        try:
            env.latitude = Decimal(dict['LAT'])
            env.longitude = Decimal(dict['LON'])
        except InvalidOperation:
            env.latitude = None
            env.longitude = None

        # if (len(dict['ENV_TAGS']) > 0):
        #     env.tags = getTags(session, dict['ENV_TAGS'].split(', '))
        env.tags = getTags(session, dict['ENV_TAGS'].split(', '))

        session.add(env)
        return env

def getStream(session, envid, streamid, dict=None):
    try:
        return session.query(Stream).filter_by(envid=envid).filter_by(streamid=streamid).one()
    except:
        stream = Stream(envid, streamid)
        if (dict != None):
            stream.unit = dict['STREAM_UNIT']
            # if (len(dict['STREAM_TAGS']) > 0):
            #     stream.tags = getTags(session, dict['STREAM_TAGS'].split(', '))
            stream.tags = getTags(session, dict['STREAM_TAGS'].split(', '))

        session.add(stream)
        return stream
