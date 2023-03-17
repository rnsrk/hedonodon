"""Script to initialize the database.
     Serves database url, engine, connection and session.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base

databaseUrl = 'sqlite:///database.db'
engine = create_engine(databaseUrl, future=True)
connection = engine.connect()
session = Session(engine)
Base = declarative_base()

def init_db():
     """Initialize the database.
     """
     Base.metadata.create_all(bind=engine)
