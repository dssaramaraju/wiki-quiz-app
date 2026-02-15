from sqlalchemy import Column, Integer, String, Text
from database import Base

class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    quiz_data = Column(Text, nullable=False)
    score = Column(Integer, default=0)