import os
from sqlalchemy import create_engine

DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://user:password@localhost/app")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

def get_engine():
    return engine
