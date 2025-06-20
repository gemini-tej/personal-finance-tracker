import json
import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum
from budget_manager import BudgetManager
from utils import format_currency, get_financial_health_score

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
        self.budget_manager = BudgetManager()
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
        
        # Update budget tracking
        current_date = datetime.date.today()
        self.budget_manager.update_spending(self.transactions, current_date.year, current_date.month)
    
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
        print("5. Budget Management")
        print("6. Financial Health Score")
        print("7. Exit")
        
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
            
            # Check budget status after adding expense
            status = tracker.budget_manager.get_budget_status()
            if category in status and status[category]['alert_level'] == 'red':
                print(f"⚠️  Warning: You've exceeded your budget for {category}!")
            
        elif choice == '3':
            balance = tracker.get_balance()
            print(f"Current balance: {format_currency(balance)}")
            
        elif choice == '4':
            year = int(input("Enter year: "))
            month = int(input("Enter month: "))
            summary = tracker.get_monthly_summary(year, month)
            print(f"\nMonthly Summary for {month}/{year}:")
            print(f"Income: {format_currency(summary['income'])}")
            print(f"Expenses: {format_currency(summary['expenses'])}")
            print(f"Net: {format_currency(summary['net'])}")
            print("Category Breakdown:")
            for category, amount in summary['category_breakdown'].items():
                print(f"  {category}: {format_currency(amount)}")
        
        elif choice == '5':
            print("\n--- Budget Management ---")
            print("1. Set Category Budget")
            print("2. View Budget Status")
            print("3. Budget Report")
            print("4. Back to Main Menu")
            
            budget_choice = input("Choose an option: ")
            
            if budget_choice == '1':
                category = input("Enter category name: ")
                limit = float(input("Enter monthly budget limit: "))
                tracker.budget_manager.set_category_budget(category, limit)
                print(f"Budget set for {category}: {format_currency(limit)}")
            
            elif budget_choice == '2':
                status = tracker.budget_manager.get_budget_status()
                print("\n--- Budget Status ---")
                for category, info in status.items():
                    emoji = "🔴" if info['alert_level'] == "red" else "🟡" if info['alert_level'] == "yellow" else "🟢"
                    print(f"{emoji} {category}: {format_currency(info['spent'])} / {format_currency(info['limit'])} ({info['percentage_used']:.1f}%)")
            
            elif budget_choice == '3':
                report = tracker.budget_manager.generate_budget_report()
                print(report)
        
        elif choice == '6':
            current_date = datetime.date.today()
            summary = tracker.get_monthly_summary(current_date.year, current_date.month)
            
            # Calculate total savings (simplified)
            total_savings = max(0, tracker.get_balance())
            
            health_score = get_financial_health_score(
                summary['income'], 
                summary['expenses'], 
                total_savings
            )
            
            print(f"\n--- Financial Health Score ---")
            print(f"Score: {health_score['score']}/100 (Grade: {health_score['grade']})")
            print(f"Savings Rate: {health_score['savings_rate']:.1f}%")
            print(f"Expense Ratio: {health_score['expense_ratio']:.1f}%")
            print(f"Emergency Fund: {health_score['emergency_fund_months']:.1f} months")
            
            if health_score['recommendations']:
                print("\nRecommendations:")
                for rec in health_score['recommendations']:
                    print(f"• {rec}")
                
        elif choice == '7':
            break
        else:
            print("Invalid option!")

if __name__ == "__main__":
    main()