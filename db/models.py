from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, JSON, BigInteger, TIMESTAMP, Boolean, Float, DateTime, LargeBinary, \
    PrimaryKeyConstraint
from sqlalchemy.dialects.postgresql.json import JSONB

url = 'postgresql://aidyn:aidyn@localhost:9393/sdukz'

engine = create_engine(url, client_encoding='utf-8', echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)


class Student(Base):
    __tablename__ = 'student'
    id = Column(BigInteger, primary_key=True)
    created = Column(TIMESTAMP)
    student_id = Column(String, unique=True)
    password = Column(String)
    content = Column(JSONB)
    chat_id = Column(String)
    user_id = Column(String)


def create_table():
    Base.metadata.create_all(engine)


if __name__ == '__main__':
    create_table()
