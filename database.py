from sqlalchemy.orm import Session, DeclarativeBase, Mapped, mapped_column, sessionmaker
from sqlalchemy import create_engine, String, JSON
from sqlalchemy.pool import NullPool
import os

DB_URL = os.environ.get(
    'DATABASE_URL',
    'postgresql+psycopg://scraper:scraperpass@localhost:5433/scraperdb'
)

engine = create_engine(DB_URL, poolclass=NullPool)
session_local = sessionmaker(bind=engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

class JobTable(Base):
    __tablename__ = 'job_table'
    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[str] = mapped_column(String, default='pending')
    url: Mapped[str] = mapped_column(String)
    value: Mapped[dict | None] = mapped_column(JSON, nullable=True, default=True)
    error: Mapped[str | None] = mapped_column(String, nullable=True, default=True)

def get_session():
    with Session(engine) as session:
        yield session

Base.metadata.create_all(engine)
print(DB_URL)




