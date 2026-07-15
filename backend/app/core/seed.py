import os
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.core.db import SessionLocal, engine
from app.models.models import Base, User, Customer, Sale, Transaction
from app.core.security import get_password_hash

def seed_database():
    print("--- Starting Database Seeding from Kaggle Dataset ---")
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    
    try:
        # 1. Create Default Users (if not exists)
        if not db.query(User).first():
            users_to_create = [
                {"name": "Admin User", "email": "admin@smartbiz.com", "password": "adminpassword", "role": "Admin"},
                {"name": "Analyst User", "email": "analyst@smartbiz.com", "password": "analystpassword", "role": "Business Analyst"},
                {"name": "Manager User", "email": "manager@smartbiz.com", "password": "managerpassword", "role": "Manager"},
            ]
            for u in users_to_create:
                new_user = User(
                    name=u["name"],
                    email=u["email"],
                    password_hash=get_password_hash(u["password"]),
                    role=u["role"]
                )
                db.add(new_user)
            print("Default credentials registered:")
            print("  - Admin: admin@smartbiz.com / adminpassword")
            print("  - Analyst: analyst@smartbiz.com / analystpassword")
            print("  - Manager: manager@smartbiz.com / managerpassword")

        # 2. Load Kaggle CSV Dataset
        csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "ml", "data", "ecommerce_customer_churn.csv"))
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Customer data source CSV not found at {csv_path}")

        df = pd.read_csv(csv_path)
        print(f"Loaded Kaggle dataset with {len(df)} lines to seed.")

        # Wipe existing customer records to prevent duplication or primary key conflicts
        db.query(Transaction).delete()
        db.query(Sale).delete()
        db.query(Customer).delete()
        db.commit()
        print("Cleared previous customer tables.")

        # Demographics pools
        genders = ["Male", "Female"]
        first_names = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]

        customers = []
        sales_to_insert = []
        transactions_to_insert = []

        start_date = datetime.now() - timedelta(days=365)

        # Helper to convert numpy/pandas type to python native or None
        def val_or_none(val, transform_fn=lambda x: x):
            if pd.isna(val) or val is None:
                return None
            try:
                return transform_fn(val)
            except Exception:
                return None

        print("Processing Kaggle rows...")
        for idx, row in df.iterrows():
            cid = f"C-1{10000 + idx}"
            name = f"{random.choice(first_names)} {random.choice(last_names)}"
            gender = random.choice(genders)
            age = random.randint(18, 72)
            
            # Map Kaggle columns to Customer schema
            tenure = val_or_none(row.get("Tenure"), int)
            satisfaction = val_or_none(row.get("SatisfactionScore"), int)
            category = val_or_none(row.get("PreferedOrderCat"), str)
            distance = val_or_none(row.get("WarehouseToHome"), int)
            marital = val_or_none(row.get("MaritalStatus"), str)
            addresses = val_or_none(row.get("NumberOfAddress"), int)
            devices = val_or_none(row.get("NumberOfDeviceRegistered"), int)
            days_since = val_or_none(row.get("DaySinceLastOrder"), int)
            cashback = val_or_none(row.get("CashbackAmount"), float)
            complain = val_or_none(row.get("Complain"), int)
            churn = val_or_none(row.get("Churn"), int)

            if not category:
                category = "Others"

            # Estimate orders and spending synthetically for dashboard visualization
            num_orders = random.randint(1, 15)
            # spending is roughly proportional to cashback (cashback is ~10-15% of order value)
            cashback_val = cashback if cashback is not None else random.uniform(10.0, 150.0)
            total_spend = cashback_val * random.uniform(7.0, 11.0)
            
            last_date = (datetime.now() - timedelta(days=int(days_since if days_since is not None else random.randint(1, 30)))).date()

            cust = Customer(
                id=cid,
                name=name,
                gender=gender,
                age=age,
                tenure=tenure,
                satisfaction_score=satisfaction,
                num_orders=num_orders,
                total_spending=round(total_spend, 2),
                last_purchase_date=last_date,
                product_category=category,
                warehouse_to_home=distance,
                marital_status=marital,
                num_addresses=addresses,
                num_devices_registered=devices,
                days_since_last_order=days_since,
                cashback_amount=cashback_val,
                complain=complain if complain is not None else 0,
                churn=churn if churn is not None else 0
            )
            customers.append(cust)

            # To avoid slow seeding times, only create individual Sale & Transaction records
            # for the first 250 customers (this populates a rich history for detail views)
            if idx < 250:
                running_spend = 0.0
                for j in range(num_orders):
                    sale_date = start_date + timedelta(days=random.randint(1, 350))
                    amount = round(total_spend / num_orders * random.uniform(0.8, 1.2), 2)
                    running_spend += amount

                    new_sale = Sale(
                        customer_id=cid,
                        date=sale_date.date(),
                        amount=amount,
                        product_category=category
                    )
                    # We will bulk save sales, but we need IDs. To do it easily in SQLite/MySQL,
                    # we can append them or write them directly.
                    # In our bulk pipeline, we can just save Customer first, and then save sales.
                    # Since MySQL auto-increments Sale.id, we can append Transaction with a placeholder sale_id 
                    # or write them in chunks.
                    sales_to_insert.append(new_sale)

        # Batch insert customers for blazing fast execution
        print(f"Bulk saving {len(customers)} Customer records...")
        db.bulk_save_objects(customers)
        db.commit()
        print("Customers seeded successfully.")

        if sales_to_insert:
            print(f"Saving {len(sales_to_insert)} Sales history records...")
            db.bulk_save_objects(sales_to_insert)
            db.commit()
            
            # Retrieve sales to generate matching transaction records
            db_sales = db.query(Sale).all()
            for s in db_sales:
                trans_status = "Success" if random.random() < 0.92 else random.choice(["Failed", "Pending"])
                new_trans = Transaction(
                    customer_id=s.customer_id,
                    sale_id=s.id,
                    transaction_date=datetime.combine(s.date, datetime.min.time()) + timedelta(hours=random.randint(8, 20)),
                    amount=s.amount,
                    status=trans_status
                )
                transactions_to_insert.append(new_trans)
                
            print(f"Saving {len(transactions_to_insert)} Transaction logs...")
            db.bulk_save_objects(transactions_to_insert)
            db.commit()

        print("--- Database Seeding Completed Successfully ---")

    except Exception as e:
        db.rollback()
        print(f"Seeding failed: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
