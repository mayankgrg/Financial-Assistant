from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./fin_assistant.db"  

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
metadata = MetaData()
card_offers = Table(
    "card_offers",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, index=True),
    Column("apr", Float),
    Column("annual_fee", Float),
)

def init_db():
    metadata.create_all(engine)
