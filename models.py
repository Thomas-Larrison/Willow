from sqlalchemy import Column, Float, String, DateTime, Integer
from db import Base
from datetime import datetime

class PriceData(Base):
    __tablename__ = "price_data"
    id = Column(Integer, primary_key=True, index=True)
    pair = Column(String, index=True)
    price = Column(Float)
    volume = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class IndicatorScore(Base):
    __tablename__ = "indicator_scores"
    id = Column(Integer, primary_key=True, index=True)
    pair = Column(String, index=True)
    score = Column(Float)
    price = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
