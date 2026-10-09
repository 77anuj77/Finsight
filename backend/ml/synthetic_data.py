"""
Synthetic Data Generator for FinSight
Generates realistic financial transaction data for testing and ML training.
"""
import os
import sys
import uuid
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import List, Dict, Any, Optional
import random
import numpy as np

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.db.postgres import SessionLocal, init_db
from backend.app.db.mongo import get_mongo_db
from backend.app.models.user import User
from backend.app.models.account import Account
from backend.app.models.category import Category
from backend.app.models.transaction import Transaction as TransactionModel
from backend.app.models.budget import Budget
from backend.app.models.goal import SavingsGoal
from backend.app.models.audit import AuditLog
from backend.app.core.security import get_password_hash


# Set seeds for reproducibility
SEED = 42
random.seed(SEED)
np.random.seed(SEED)


# Category definitions matching the schema
CATEGORIES = [
    {"id": 1, "name": "Income", "kind": "INCOME", "is_default": True},
    {"id": 2, "name": "Food & Dining", "kind": "EXPENSE", "is_default": True},
    {"id": 3, "name": "Transport", "kind": "EXPENSE", "is_default": True},
    {"id": 4, "name": "Rent", "kind": "EXPENSE", "is_default": True},
    {"id": 5, "name": "Education", "kind": "EXPENSE", "is_default": True},
    {"id": 6, "name": "Subscriptions", "kind": "EXPENSE", "is_default": True},
    {"id": 7, "name": "Shopping", "kind": "EXPENSE", "is_default": True},
    {"id": 8, "name": "Entertainment", "kind": "EXPENSE", "is_default": True},
    {"id": 9, "name": "Health", "kind": "EXPENSE", "is_default": True},
    {"id": 10, "name": "Savings", "kind": "EXPENSE", "is_default": True},
    {"id": 11, "name": "Other", "kind": "EXPENSE", "is_default": True},
    {"id": 0, "name": "Transfer", "kind": "EXPENSE", "is_default": True},  # Special transfer category
]


# Payee patterns for realistic data
PAYEES_BY_CATEGORY = {
    2: ["Zomato", "Swiggy", "College Canteen", "Local Restaurant", "Coffee Shop", "Mess Bill", "Food Court"],
    3: ["Uber", "Ola", "Rapido", "Metro Card", "Bus Pass", "Petrol Pump", "Auto Rickshaw", "Train Ticket"],
    4: ["Hostel Rent", "PG Accommodation", "Apartment Rent", "Security Deposit"],
    5: ["College Fees", "Exam Fees", "Course Materials", "Online Course", "Certification", "Books"],
    6: ["Netflix", "Spotify", "Amazon Prime", "YouTube Premium", "GitHub Copilot", "Cloud Storage"],
    7: ["Amazon", "Flipkart", "Myntra", "Electronics Store", "Clothing Store", "Mobile Recharge"],
    8: ["Movie Theater", "Steam", "PlayStation Store", "Concert Tickets", "Gaming", "Events"],
    9: ["Pharmacy", "Doctor Consultation", "Hospital", "Gym Membership", "Health Checkup", "Medicines"],
    10: ["SIP Investment", "Fixed Deposit", "PPF", "Emergency Fund", "Mutual Fund"],
    11: ["Miscellaneous", "Cash Withdrawal", "Gift", "Donation", "Other"],
}


# Transaction patterns
INCOME_PAYEES = ["Monthly Allowance", "Stipend", "Part-time Job", "Freelance", "Internship", "Scholarship"]


def create_users(db, num_users: int = 200) -> List[User]:
    """Create synthetic users."""
    users = []
    for i in range(num_users):
        user = User(
            id=str(uuid.uuid4()),
            email=f"student{i+1}@college.edu",
            password_hash=get_password_hash("Password123!"),
            full_name=f"Student {i+1}",
            role="USER",
            currency="INR",
            monthly_income=round(np.random.lognormal(9.2, 0.4), 2),  # ~10k-15k typical
            is_active=True,
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 365)),
            updated_at=datetime.utcnow(),
        )
        users.append(user)
        db.add(user)

    db.commit()
    for user in users:
        db.refresh(user)

    print(f"Created {len(users)} users")
    return users


def create_categories(db) -> List[Category]:
    """Create default categories."""
    categories = []
    for cat_data in CATEGORIES:
        cat = Category(**cat_data)
        categories.append(cat)
        db.add(cat)

    db.commit()
    print(f"Created {len(categories)} categories")
    return categories


def create_accounts(db, users: List[User]) -> List[Account]:
    """Create accounts for each user."""
    account_types = ["CASH", "BANK", "UPI", "CARD"]
    accounts = []

    for user in users:
        num_accounts = random.randint(2, 4)
        for j in range(num_accounts):
            acc_type = random.choice(account_types)
            # Initial balance based on user income
            initial_balance = Decimal(str(round(user.monthly_income * random.uniform(0.1, 0.5), 2)))

            account = Account(
                id=str(uuid.uuid4()),
                user_id=user.id,
                name=f"{acc_type} Account {j+1}",
                type=acc_type,
                balance=initial_balance,
                currency="INR",
                is_active=True,
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 300)),
            )
            accounts.append(account)
            db.add(account)

    db.commit()
    for acc in accounts:
        db.refresh(acc)

    print(f"Created {len(accounts)} accounts")
    return accounts


def generate_transactions_for_user(
    user: User,
    accounts: List[Account],
    start_date: date,
    end_date: date,
    db
) -> List[TransactionModel]:
    """Generate realistic transactions for a single user."""
    transactions = []
    user_accounts = [a for a in accounts if a.user_id == user.id]

    if not user_accounts:
        return transactions

    current_date = start_date
    monthly_income = Decimal(str(user.monthly_income))

    while current_date <= end_date:
        # Monthly income on 1st of each month
        if current_date.day == 1:
            # Credit income to primary bank account
            bank_account = next((a for a in user_accounts if a.type == "BANK"), user_accounts[0])

            income_amount = monthly_income * Decimal(str(random.uniform(0.9, 1.1)))
            income_amount = Decimal(str(round(income_amount, 2)))

            txn = TransactionModel(
                id=str(uuid.uuid4()),
                account_id=bank_account.id,
                user_id=user.id,
                category_id=1,  # Income
                type="INCOME",
                amount=income_amount,
                payee=random.choice(INCOME_PAYEES),
                transacted_at=datetime.combine(current_date, datetime.min.time()) + timedelta(hours=random.randint(9, 11)),
                notes="Monthly income",
                flag_status="NORMAL",
                source="AUTO",
                receipt_ref=None,
                created_at=datetime.utcnow(),
            )
            transactions.append(txn)
            db.add(txn)

            # Update account balance
            bank_account.balance += income_amount

        # Daily expenses (multiple per day)
        num_daily_txns = random.randint(1, 4)
        for _ in range(num_daily_txns):
            # Pick random account (weighted towards cash/UPI)
            weights = [0.3 if a.type == "CASH" else 0.4 if a.type == "UPI" else 0.2 if a.type == "CARD" else 0.1
                      for a in user_accounts]
            account = random.choices(user_accounts, weights=weights)[0]

            # Pick expense category based on realistic distribution
            expense_categories = [2, 3, 4, 5, 6, 7, 8, 9, 11]
            cat_weights = [0.35, 0.15, 0.10, 0.08, 0.07, 0.10, 0.05, 0.05, 0.05]  # Food highest
            category_id = random.choices(expense_categories, weights=cat_weights)[0]

            # Amount based on category
            if category_id == 4:  # Rent - larger, less frequent
                if current_date.day not in [1, 15]:
                    continue
                amount = Decimal(str(round(user.monthly_income * random.uniform(0.3, 0.5), 2)))
            elif category_id == 5:  # Education - occasional
                if random.random() > 0.1:
                    continue
                amount = Decimal(str(round(random.uniform(500, 5000), 2)))
            elif category_id == 6:  # Subscriptions - monthly
                if current_date.day != 5:
                    continue
                amount = Decimal(str(round(random.uniform(100, 1000), 2)))
            else:
                # Regular daily expenses
                amount = Decimal(str(round(random.uniform(20, 800), 2)))

            # Skip if amount > account balance
            if amount > account.balance:
                continue

            # Occasional fraud-like patterns (2% of transactions)
            is_suspicious = random.random() < 0.02
            flag_status = "SUSPICIOUS" if is_suspicious else "NORMAL"

            # For suspicious, make amount unusual
            if is_suspicious:
                amount = amount * Decimal(str(random.uniform(3, 10)))
                if amount > account.balance:
                    amount = account.balance * Decimal('0.9')

            payee = random.choice(PAYEES_BY_CATEGORY.get(category_id, ["Unknown"]))

            txn = TransactionModel(
                id=str(uuid.uuid4()),
                account_id=account.id,
                user_id=user.id,
                category_id=category_id,
                type="EXPENSE",
                amount=amount,
                payee=payee,
                transacted_at=datetime.combine(current_date, datetime.min.time()) + timedelta(hours=random.randint(7, 22)),
                notes=f"{payee} payment",
                flag_status=flag_status,
                source="MANUAL",
                receipt_ref=None,
                created_at=datetime.utcnow(),
            )
            transactions.append(txn)
            db.add(txn)

            # Update account balance
            account.balance -= amount

        current_date += timedelta(days=1)

    return transactions


def create_budgets(db, users: List[User], start_date: date, end_date: date) -> List[Budget]:
    """Create budgets for users."""
    budgets = []
    expense_cats = [2, 3, 4, 5, 6, 7, 8, 9, 11]

    current = start_date.replace(day=1)
    while current <= end_date:
        for user in users:
            # Each user has budgets for 4-6 categories
            user_cats = random.sample(expense_cats, k=random.randint(4, 6))
            for cat_id in user_cats:
                # Budget based on user income
                if cat_id == 4:  # Rent
                    limit = Decimal(str(round(user.monthly_income * random.uniform(0.3, 0.5), 2)))
                elif cat_id == 2:  # Food
                    limit = Decimal(str(round(user.monthly_income * random.uniform(0.2, 0.35), 2)))
                elif cat_id == 3:  # Transport
                    limit = Decimal(str(round(user.monthly_income * random.uniform(0.08, 0.15), 2)))
                else:
                    limit = Decimal(str(round(user.monthly_income * random.uniform(0.03, 0.12), 2)))

                budget = Budget(
                    id=str(uuid.uuid4()),
                    user_id=user.id,
                    category_id=cat_id,
                    month=current,
                    limit_amount=limit,
                    created_at=datetime.utcnow(),
                )
                budgets.append(budget)
                db.add(budget)

        # Next month
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)

    db.commit()
    print(f"Created {len(budgets)} budgets")
    return budgets


def create_goals(db, users: List[User]) -> List[SavingsGoal]:
    """Create savings goals for users."""
    goals = []
    goal_templates = [
        ("Emergency Fund", 0.15, 180),
        ("New Laptop", 0.08, 120),
        ("Trip Fund", 0.05, 90),
        ("Course Certification", 0.03, 60),
        ("Gadget Fund", 0.04, 90),
    ]

    for user in users:
        num_goals = random.randint(1, 3)
        templates = random.sample(goal_templates, k=num_goals)

        for name, sweep_pct, days in templates:
            target = Decimal(str(round(user.monthly_income * random.uniform(2, 6), 2)))
            deadline = date.today() + timedelta(days=days)

            goal = SavingsGoal(
                id=str(uuid.uuid4()),
                user_id=user.id,
                name=name,
                target_amount=target,
                current_amount=Decimal('0.00'),
                auto_sweep_pct=Decimal(str(sweep_pct * 100)),
                deadline=deadline,
                status="ACTIVE",
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 60)),
                updated_at=datetime.utcnow(),
            )
            goals.append(goal)
            db.add(goal)

    db.commit()
    print(f"Created {len(goals)} savings goals")
    return goals


def sync_to_mongo(transactions: List[TransactionModel], users: List[User], accounts: List[Account]):
    """Sync generated data to MongoDB for analytics."""
    mongo_db = get_mongo_db()
    if mongo_db is None:
        print("MongoDB not available, skipping sync")
        return

    # Sync transactions
    for txn in transactions:
        # Find related data
        account = next((a for a in accounts if a.id == txn.account_id), None)
        user = next((u for u in users if u.id == txn.user_id), None)

        if not account or not user:
            continue

        doc = {
            "tx_id": str(txn.id),
            "user_id": str(txn.user_id),
            "account_id": str(txn.account_id),
            "type": txn.type,
            "amount": float(txn.amount),
            "category_id": txn.category_id,
            "payee": txn.payee,
            "transacted_at": txn.transacted_at.isoformat() if hasattr(txn.transacted_at, 'isoformat') else str(txn.transacted_at),
            "month_key": txn.transacted_at.strftime("%Y-%m") if hasattr(txn.transacted_at, 'strftime') else datetime.utcnow().strftime("%Y-%m"),
            "notes": txn.notes,
            "flag_status": txn.flag_status,
            "source": txn.source,
            "receipt_ref": txn.receipt_ref,
            "created_at": datetime.utcnow(),
            "features": {
                "amount_z": 0.0,  # Would compute from user history
                "is_weekend": txn.transacted_at.weekday() >= 5 if hasattr(txn.transacted_at, 'weekday') else False,
                "hour_of_day": txn.transacted_at.hour if hasattr(txn.transacted_at, 'hour') else 12,
                "days_since_last_txn": 0,
                "is_new_payee": False,
            }
        }

        mongo_db.txn_analytics.update_one(
            {"tx_id": str(txn.id)},
            {"$set": doc},
            upsert=True
        )

    # Sync users
    for user in users:
        doc = {
            "user_id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "currency": user.currency,
            "monthly_income": float(user.monthly_income),
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if hasattr(user.created_at, 'isoformat') else str(user.created_at),
            "updated_at": datetime.utcnow(),
        }
        mongo_db.users.update_one(
            {"user_id": str(user.id)},
            {"$set": doc},
            upsert=True
        )

    # Sync accounts
    for account in accounts:
        doc = {
            "account_id": str(account.id),
            "user_id": str(account.user_id),
            "name": account.name,
            "type": account.type,
            "balance": float(account.balance),
            "currency": account.currency,
            "is_active": account.is_active,
            "created_at": account.created_at.isoformat() if hasattr(account.created_at, 'isoformat') else str(account.created_at),
            "updated_at": datetime.utcnow(),
        }
        mongo_db.accounts.update_one(
            {"account_id": str(account.id)},
            {"$set": doc},
            upsert=True
        )

    print(f"Synced {len(transactions)} transactions, {len(users)} users, {len(accounts)} accounts to MongoDB")


def main():
    """Main function to generate all synthetic data."""
    print("=" * 60)
    print("FinSight Synthetic Data Generator")
    print("=" * 60)

    # Initialize databases
    init_db()
    db = SessionLocal()

    try:
        # Date range: last 12 months
        end_date = date.today()
        start_date = end_date - timedelta(days=365)

        print(f"\nGenerating data from {start_date} to {end_date}")

        # Create categories first
        create_categories(db)

        # Create users
        users = create_users(db, num_users=200)

        # Create accounts
        accounts = create_accounts(db, users)

        # Generate transactions
        print("\nGenerating transactions...")
        all_transactions = []
        for i, user in enumerate(users):
            if i % 50 == 0:
                print(f"  Processing user {i+1}/{len(users)}")
            txns = generate_transactions_for_user(user, accounts, start_date, end_date, db)
            all_transactions.extend(txns)

        db.commit()
        print(f"Created {len(all_transactions)} transactions")

        # Create budgets
        create_budgets(db, users, start_date, end_date)

        # Create goals
        create_goals(db, users)

        # Sync to MongoDB
        print("\nSyncing to MongoDB...")
        sync_to_mongo(all_transactions, users, accounts)

        # Print summary
        print("\n" + "=" * 60)
        print("DATA GENERATION COMPLETE")
        print("=" * 60)
        print(f"Users: {len(users)}")
        print(f"Accounts: {len(accounts)}")
        print(f"Transactions: {len(all_transactions)}")
        print(f"Date range: {start_date} to {end_date}")

        # Transaction stats
        income_txns = [t for t in all_transactions if t.type == "INCOME"]
        expense_txns = [t for t in all_transactions if t.type == "EXPENSE"]
        suspicious_txns = [t for t in all_transactions if t.flag_status == "SUSPICIOUS"]

        print(f"Income transactions: {len(income_txns)}")
        print(f"Expense transactions: {len(expense_txns)}")
        print(f"Suspicious transactions: {len(suspicious_txns)}")
        print(f"Total income: ₹{sum(float(t.amount) for t in income_txns):,.2f}")
        print(f"Total expenses: ₹{sum(float(t.amount) for t in expense_txns):,.2f}")

    finally:
        db.close()


if __name__ == "__main__":
    main()