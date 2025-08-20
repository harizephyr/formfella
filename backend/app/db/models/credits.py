# credits.py
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Credits(Base):
    __tablename__ = 'credits'
    
    email = Column(String, primary_key=True, index=True)
    credits = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
