import os
from sqlmodel import create_engine, SQLModel, Session
from dotenv import load_dotenv


load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def init_db():
    print("Initializing database")
    global engine
    engine = create_engine(DATABASE_URL)
    SQLModel.metadata.create_all(engine)
    return engine


def get_session():
    with Session(engine) as session:
        yield session