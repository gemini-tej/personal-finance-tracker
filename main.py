import json
import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum

class TransactionType(Enum):
    INCOME = "income"
    EXPENSE = "expense"

@dataclass
class Transaction:
    amount: float
    category: str
    description: str
    date: datetime.date
    transaction_type: TransactionType
    
    def to_dict(self):
        return {
            'amount': self.amount,
            'category': self.category,
            'description': self.description,
            'date': self.date.isoformat(),
            'type': self.transaction_type.value
        }

class FinanceTracker:
    def __init__(self, data_file: str = "transactions.json"):
        self.data_file = data_file
        self.transactions: List[Transaction] = []
        self.load_data()
    
    def load_data(self):
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                for item in data:
                    transaction = Transaction(
                        amount=item['amount'],
                        category=item['category'],
                        description=item['description'],
                        date=datetime.date.fromisoformat(item['date']),
                        transaction_type=TransactionType(item['type'])
                    )
                    self.transactions.append(transaction)
        except FileNotFoundError:
            self.transactions = []
    
    def save_data(self):
        with open(self.data_file, 'w') as f:
            json.dump([t.to_dict() for t in self.transactions], f, indent=2)
    
    def add_transaction(self, amount: float, category: str, description: str, 
                       transaction_type: TransactionType):
        transaction = Transaction(
            amount=amount,
            category=category,
            description=description,
            date=datetime.date.today(),
            transaction_type=transaction_type
        )
        self.transactions.append(transaction)
        self.save_data()
    
    def get_balance(self) -> float:
        balance = 0
        for transaction in self.transactions:
            if transaction.transaction_type == TransactionType.INCOME:
                balance += transaction.amount
            else:
                balance -= transaction.amount
        return balance
    
    def get_monthly_summary(self, year: int, month: int) -> Dict:
        monthly_transactions = [
            t for t in self.transactions 
            if t.date.year == year and t.date.month == month
        ]
        
        income = sum(t.amount for t in monthly_transactions 
                    if t.transaction_type == TransactionType.INCOME)
        expenses = sum(t.amount for t in monthly_transactions 
                      if t.transaction_type == TransactionType.EXPENSE)
        
        category_breakdown = {}
        for transaction in monthly_transactions:
            if transaction.category not in category_breakdown:
                category_breakdown[transaction.category] = 0
            if transaction.transaction_type == TransactionType.EXPENSE:
                category_breakdown[transaction.category] += transaction.amount
        
        return {
            'income': income,
            'expenses': expenses,
            'net': income - expenses,
            'category_breakdown': category_breakdown
        }

def main():
    tracker = FinanceTracker()
    
    while True:
        print("\n--- Personal Finance Tracker ---")
        print("1. Add Income")
        print("2. Add Expense") 
        print("3. View Balance")
        print("4. Monthly Summary")
        print("5. Exit")
        
        choice = input("Choose an option: ")
        
        if choice == '1':
            amount = float(input("Enter income amount: "))
            category = input("Enter category: ")
            description = input("Enter description: ")
            tracker.add_transaction(amount, category, description, TransactionType.INCOME)
            print("Income added successfully!")
            
        elif choice == '2':
            amount = float(input("Enter expense amount: "))
            category = input("Enter category: ")
            description = input("Enter description: ")
            tracker.add_transaction(amount, category, description, TransactionType.EXPENSE)
            print("Expense added successfully!")
            
        elif choice == '3':
            balance = tracker.get_balance()
            print(f"Current balance: ${balance:.2f}")
            
        elif choice == '4':
            year = int(input("Enter year: "))
            month = int(input("Enter month: "))
            summary = tracker.get_monthly_summary(year, month)
            print(f"\nMonthly Summary for {month}/{year}:")
            print(f"Income: ${summary['income']:.2f}")
            print(f"Expenses: ${summary['expenses']:.2f}")
            print(f"Net: ${summary['net']:.2f}")
            print("Category Breakdown:")
            for category, amount in summary['category_breakdown'].items():
                print(f"  {category}: ${amount:.2f}")
                
        elif choice == '5':
            break
        else:
            print("Invalid option!")

if __name__ == "__main__":
    main()
