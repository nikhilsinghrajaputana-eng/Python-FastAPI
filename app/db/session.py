from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://postgres:password@localhost:5432/fastapi_db"

engine = create_engine(DATABASE_URL)
# connection = engine.connect()
# print("Connected Successfully")

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)