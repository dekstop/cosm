from app import Base
# from decimal import Decimal
# from datetime import datetime
from sqlalchemy import *
from sqlalchemy.orm import *

class Tag(Base):
    __tablename__ = 'tag'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Tag:%s>" % (self.name)

env_tags = Table('env_tags', Base.metadata,
    Column('env_id', Integer, ForeignKey('environment.id')),
    Column('tag_id', Integer, ForeignKey('tag.id'))
)
stream_tags = Table('stream_tags', Base.metadata,
    Column('stream_id', Integer, ForeignKey('stream.id')),
    Column('tag_id', Integer, ForeignKey('tag.id'))
)

class Environment(Base):
    __tablename__ = 'environment'
    id = Column(Integer, primary_key=True)
    creator = Column(String)
    created = Column(DateTime, nullable=False)
    updated = Column(DateTime, nullable=False)
    title = Column(String, nullable=False)
    feed = Column(String, nullable=False)
    status = Column(String, nullable=False)
    private = Column(String, nullable=False)

    location = Column(String)
    location_domain = Column(String)
    location_exposure = Column(String)
    location_disposition = Column(String)
    latitude = Column(Numeric)
    longitude = Column(Numeric)
    
    tags = relationship("Tag", secondary=env_tags)
    streams = relationship("Stream")
    
    Index('idx_environment_id_lat_lon', 'id', 'latitude', 'longitude', unique=False)

    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return "<Stream: %d %s>" % (self.id, self.title)

    # ...

class Stream(Base):
    __tablename__ = 'stream'
    id = Column(Integer, primary_key=True)

    envid = Column(Integer, ForeignKey('environment.id'))
    streamid = Column(String)
    unit = Column(String)
    
    tags = relationship("Tag", secondary=stream_tags)
    env = relationship("Environment")
    
    UniqueConstraint('envid', 'streamid', name='uix_stream_envid_streamid')
    # Index('idx_stream_envid_streamid', 'envid', 'streamid', unique=True)

    def __init__(self, envid, streamid):
        self.envid = envid
        self.streamid = streamid

    def __repr__(self):
        return "<Stream: %d.%s>" % (self.envid, self.streamid)

    # ...
