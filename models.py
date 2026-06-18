from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.sql import func
from database import Base
import datetime

class ExerciseLog(Base):
    __tablename__ = "exercise_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    datetime = Column(DateTime, default=func.now()) # Automatically records time
    exercise = Column(String, nullable=False)
    amount = Column(Float, nullable=False) # Float allows for decimals (e.g., 5.5 miles)