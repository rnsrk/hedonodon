from DbSetup import Base
from sqlalchemy import Column, Date, Integer, Float, String

class Toots(Base):
    __tablename__ = 'Toots'
    __table_args__ = {'extend_existing': True}
    index = Column(Integer, primary_key=True)
    compound =  Column(Float)
    datetime = Column(Date)
    language = Column(String(3))
    sentiment = Column(String(8))
    tootId = Column(String(255))
    toot = Column(String(600))
    userName = Column(String(255))
    userId = Column(String(255))



class Sentiments(Base):
    __tablename__ = 'Sentiments'
    __table_args__ = {'extend_existing': True}
    index = Column(Integer, primary_key=True)
    sentimentCount = Column(Integer)
    date = Column(Date, primary_key =  True)
    sentiment = Column(String(8))


class Compounds(Base):
    __tablename__ = 'Compounds'
    __table_args__ = {'extend_existing': True}
    index = Column(Integer, primary_key=True)
    date = Column(Date, primary_key =  True)
    compoundAvg = Column(Float)