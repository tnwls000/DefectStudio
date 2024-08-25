from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config import settings

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
Session = sessionmaker(bind=engine)
Base = declarative_base()

