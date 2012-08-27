from app import Base
# from decimal import Decimal
# from datetime import datetime
from sqlalchemy import *
from sqlalchemy.orm import *

class RawData(Base):
    __tablename__ = 'data_raw'
    id = Column(Integer, primary_key=True)
    
    envid = Column(Integer, nullable=False)
    streamid = Column(String, nullable=False)
    updated = Column(DateTime, nullable=False)
    value = Column(String)

    def __init__(self, envid, streamid, updated, value):
        self.envid = envid
        self.streamid = streamid
        self.updated = updated
        self.value = value

    def __repr__(self):
        return "<RawData: %d.%s %s>" % (self.envid, self.streamid, self.value)

class Data(Base):
    __tablename__ = 'data'
    id = Column(Integer, primary_key=True)
    
    streamid = Column(Integer, ForeignKey('stream.id'))
    # streamid = Column(Integer, nullable=False)
    updated = Column(DateTime, nullable=False)
    value = Column(Numeric)
    
    stream = relationship("Stream")
    
    Index('idx_data_updated', 'updated', unique=False)

    def __init__(self, stream, updated, value):
        self.stream = stream
        self.updated = updated
        self.value = value

    def __repr__(self):
        return "<Data: %s %s>" % (self.stream, self.value)

# Aggregation table.
class DataDays(Base):
    __tablename__ = 'data_days'

    # Composite primary key
    date = Column(String, primary_key=True)
    streamid = Column(Integer, ForeignKey('stream.id'), primary_key=True)
    count = Column(Integer)
    min = Column(Numeric)
    max = Column(Numeric)
    mean = Column(Numeric)
    median = Column(Numeric)
    sd = Column(Numeric)
    
    Index('date', 'streamid', unique=True)

    def __init__(self, date, stream, count, min, max, mean, median, sd):
        self.stream = stream
        self.updated = updated
        self.count = count
        self.min = min
        self.max = max
        self.mean = mean
        self.median = median
        self.sd = sd

    def __repr__(self):
        return "<DataDays: %s %s %s>" % (self.date, self.stream, self.mean)