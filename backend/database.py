import os
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    Text,
    DateTime,
)
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

load_dotenv()

# 1. Get the URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./intellectmoney.db")

# 2. FIX FOR RENDER: SQLAlchemy requires 'postgresql://', but Render gives 'postgres://'
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# 3. Configure Engine Arguments
engine_args = {}
# If using SQLite (Local testing), we need this argument
if "sqlite" in DATABASE_URL:
    engine_args["connect_args"] = {"check_same_thread": False}

# 4. Create the Engine (Pass **engine_args here!)
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    **engine_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- MODELS ---

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    fullname = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    # Relationships
    financial_plans = relationship("FinancialPlan", back_populates="owner")


class FinancialPlan(Base):
    __tablename__ = "financial_plans"
    id = Column(Integer, primary_key=True, index=True)
    
    # Inputs
    income = Column(Float, nullable=False)
    expenses = Column(Float, nullable=False)
    savings = Column(Float, nullable=False)
    risk_tolerance = Column(String, nullable=False)
    
    # AI Outputs
    ai_summary = Column(Text, nullable=True)
    recommendations_json = Column(Text, nullable=True)
    portfolio_json = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="financial_plans")


# --- HELPERS ---

def get_db():
    """Dependency to get a DB session for each request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_database():
    """Creates all database tables."""
    Base.metadata.create_all(bind=engine)