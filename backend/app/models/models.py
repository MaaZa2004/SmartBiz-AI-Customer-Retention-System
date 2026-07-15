from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False) # 'Admin', 'Business Analyst', 'Manager'
    created_at = Column(DateTime, default=datetime.utcnow)

class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(String(50), primary_key=True) # Alphanumeric Customer ID
    name = Column(String(255), nullable=False)
    gender = Column(String(20), nullable=True)
    age = Column(Integer, nullable=True)
    tenure = Column(Integer, nullable=True) # In months
    satisfaction_score = Column(Integer, nullable=True)
    num_orders = Column(Integer, nullable=True)
    total_spending = Column(Numeric(12, 2), default=0.00)
    last_purchase_date = Column(Date, nullable=True)
    product_category = Column(String(100), nullable=True, index=True) # Preferred category
    
    # E-Commerce Churn/Shopwise specific fields
    warehouse_to_home = Column(Integer, nullable=True)
    marital_status = Column(String(20), nullable=True)
    num_addresses = Column(Integer, nullable=True)
    num_devices_registered = Column(Integer, nullable=True)
    days_since_last_order = Column(Integer, nullable=True)
    cashback_amount = Column(Numeric(10, 2), default=0.00)
    complain = Column(Integer, default=0) # 0 = No, 1 = Yes
    churn = Column(Integer, default=0) # 0 = No, 1 = Yes (Target Label)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    sales = relationship("Sale", back_populates="customer", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="customer", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="customer", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="customer", cascade="all, delete-orphan")

class Sale(Base):
    __tablename__ = "sales"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(String(50), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    amount = Column(Numeric(12, 2), nullable=False)
    product_category = Column(String(100), nullable=True)
    
    # Relationships
    customer = relationship("Customer", back_populates="sales")
    transactions = relationship("Transaction", back_populates="sale")

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(String(50), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id", ondelete="SET NULL"), nullable=True)
    transaction_date = Column(DateTime, default=datetime.utcnow, index=True)
    amount = Column(Numeric(12, 2), nullable=False)
    status = Column(String(50), nullable=False) # 'Success', 'Pending', 'Failed'
    
    # Relationships
    customer = relationship("Customer", back_populates="transactions")
    sale = relationship("Sale", back_populates="transactions")

class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(String(50), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    model_type = Column(String(50), nullable=False) # 'churn', 'segment', 'forecast'
    result_value = Column(String(255), nullable=False) # Churn risk level or segment value or forecasted sales
    confidence_score = Column(Numeric(5, 4), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    customer = relationship("Customer", back_populates="predictions")

class Recommendation(Base):
    __tablename__ = "recommendations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(String(50), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    recommendation_text = Column(Text, nullable=False)
    action_type = Column(String(100), nullable=False) # 'retention action', 'marketing suggestion', 'next-best-action'
    priority = Column(String(20), nullable=False) # 'High', 'Medium', 'Low'
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    customer = relationship("Customer", back_populates="recommendations")
