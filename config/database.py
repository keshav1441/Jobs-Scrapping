from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

class Job(Base):
    __tablename__ = 'jobs'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False)
    company = Column(String(200), nullable=False)
    location = Column(String(200))
    description = Column(Text)
    apply_url = Column(String(1000))
    date_posted = Column(DateTime)
    source_site = Column(String(200), nullable=False)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    salary = Column(String(100))
    job_type = Column(String(100))
    experience_level = Column(String(100))
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'description': self.description,
            'apply_url': self.apply_url,
            'date_posted': self.date_posted.isoformat() if self.date_posted else None,
            'source_site': self.source_site,
            'scraped_at': self.scraped_at.isoformat() if self.scraped_at else None,
            'is_active': self.is_active,
            'salary': self.salary,
            'job_type': self.job_type,
            'experience_level': self.experience_level
        }

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///jobs.db')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
