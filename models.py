from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Text, DateTime

DeclarativeBase = declarative_base()


class Quiz(DeclarativeBase):
    __tablename__ = 'quiz'

    id = Column(Integer, primary_key=True)
    question_text = Column(Text)
    answer = Column(Text)
    date = Column(DateTime)
