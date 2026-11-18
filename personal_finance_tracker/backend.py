from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, Date
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import date

# =============================================================================
# DATABASE SETUP (SQLite)
# =============================================================================
SQLALCHEMY_DATABASE_URL = "sqlite:///./finance.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Model
class TransactionDB(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float)
    category = Column(String)
    description = Column(String)
    transaction_type = Column(String)  # "Income" or "Expense"
    transaction_date = Column(String)

Base.metadata.create_all(bind=engine)

# =============================================================================
# FASTAPI APP & MODELS
# =============================================================================
app = FastAPI()

class TransactionCreate(BaseModel):
    amount: float
    category: str
    description: str
    transaction_type: str
    transaction_date: str

# =============================================================================
# CRUD OPERATIONS
# =============================================================================
@app.post("/transactions/")
def create_transaction(tx: TransactionCreate):
    """Create a new transaction."""
    db = SessionLocal()
    db_tx = TransactionDB(**tx.dict())
    db.add(db_tx)
    db.commit()
    db.refresh(db_tx)
    db.close()
    return {"message": "Transaction added successfully", "id": db_tx.id}

@app.get("/transactions/")
def get_transactions():
    """Read all transactions."""
    db = SessionLocal()
    transactions = db.query(TransactionDB).order_by(TransactionDB.transaction_date.desc()).all()
    db.close()
    return transactions

@app.delete("/transactions/{tx_id}")
def delete_transaction(tx_id: int):
    """Delete a transaction by ID."""
    db = SessionLocal()
    tx = db.query(TransactionDB).filter(TransactionDB.id == tx_id).first()
    if not tx:
        db.close()
        raise HTTPException(status_code=404, detail="Transaction not found")
    db.delete(tx)
    db.commit()
    db.close()
    return {"message": "Transaction deleted"}