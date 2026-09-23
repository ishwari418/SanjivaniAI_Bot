import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker

from config import Config

engine = create_engine(Config.DATABASE_URL, connect_args={"check_same_thread": False}
                        if Config.DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String, nullable=False)
    doc_type = Column(String, default="general")  # attendance, exam, hostel, etc.
    status = Column(String, default="uploaded")     # uploaded, processing, processed, failed
    num_chunks = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "doc_type": self.doc_type,
            "status": self.status,
            "num_chunks": self.num_chunks,
            "error_message": self.error_message,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
        }


def init_db():
    Base.metadata.create_all(bind=engine)


def get_session():
    return SessionLocal()
