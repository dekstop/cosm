import ConfigParser
from datetime import datetime
from decimal import Decimal, InvalidOperation
import os

from sqlalchemy import *
from sqlalchemy.orm import *

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

from models import *

SETTINGS_FILE=os.environ['SETTINGS_FILE']
config = ConfigParser.ConfigParser()
config.readfp(open(SETTINGS_FILE))

# db = create_engine('sqlite:///var/test.db')
# # db.echo = True
# Base.metadata.create_all(db) 
# Session = sessionmaker(bind=db)
# session = Session()

def getTag(session, name):
    try:
      return session.query(Tag).filter_by(name=name).one()
    except:
      tag = Tag(name)
      session.add(tag)
      return tag

def getTags(session, names):
    tags = []
    for name in names:
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

      env.tags = getTags(session, dict['ENV_TAGS'].split(', '))
      
      session.add(env)
      return env

def getStream(session, envid, streamid, dict=None):
    try:
      return session.query(Stream).filter_by(envid=envid).filter_by(id=streamid).one()
    except:
      stream = Stream(envid, streamid)
      if (dict != None):
          stream.unit = dict['STREAM_UNIT']
          stream.tags = getTags(session, dict['STREAM_TAGS'].split(', '))
      
      session.add(stream)
      return stream

