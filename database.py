from sqlalchemy.orm import Session, DeclarativeBase, Mapped, mapped_column, sessionmaker
from sqlalchemy import create_engine, String, JSON

engine = create_engine('sqlite:///./jobs.db', echo=True)
session_local = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

class JobTable(Base):
    __tablename__ = 'job_table'
    id: Mapped[int] = mapped_column(primary_key=True)
    job_type: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default='pending')
    payload: Mapped[dict] = mapped_column(JSON)
    value: Mapped[dict | None] = mapped_column(JSON, nullable=True, default=True)
    error: Mapped[str | None] = mapped_column(String, nullable=True, default=True)

def get_session():
    with Session(engine) as session:
        yield session

Base.metadata.create_all(engine)





