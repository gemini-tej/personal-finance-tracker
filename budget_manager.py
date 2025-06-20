import json
import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from main import Transaction, TransactionType

@dataclass
class BudgetCategory:
    name: str
    monthly_limit: float
    current_spent: float = 0.0
    
    def to_dict(self):
        return {
            'name': self.name,
            'monthly_limit': self.monthly_limit,
            'current_spent': self.current_spent
        }

class BudgetManager:
    def __init__(self, budget_file: str = "budget.json"):
        self.budget_file = budget_file
        self.categories: Dict[str, BudgetCategory] = {}
        self.load_budget()
    
    def load_budget(self):
        try:
            with open(self.budget_file, 'r') as f:
                data = json.load(f)
                for item in data:
                    category = BudgetCategory(
                        name=item['name'],
                        monthly_limit=item['monthly_limit'],
                        current_spent=item.get('current_spent', 0.0)
                    )
                    self.categories[item['name']] = category
        except FileNotFoundError:
            self.categories = {}
    
    def save_budget(self):
        with open(self.budget_file, 'w') as f:
            json.dump([cat.to_dict() for cat in self.categories.values()], f, indent=2)
    
    def set_category_budget(self, category_name: str, monthly_limit: float):
        if category_name in self.categories:
            self.categories[category_name].monthly_limit = monthly_limit
        else:
            self.categories[category_name] = BudgetCategory(category_name, monthly_limit)
        self.save_budget()
    
    def update_spending(self, transactions: List[Transaction], year: int, month: int):
        monthly_expenses = [
            t for t in transactions 
            if (t.date.year == year and t.date.month == month and 
                t.transaction_type == TransactionType.EXPENSE)
        ]
        
        for category in self.categories.values():
            category.current_spent = 0.0
        
        for transaction in monthly_expenses:
            if transaction.category in self.categories:
                self.categories[transaction.category].current_spent += transaction.amount
        
        self.save_budget()
    
    def get_budget_status(self) -> Dict[str, Dict]:
        status = {}
        for name, category in self.categories.items():
            remaining = category.monthly_limit - category.current_spent
            percentage_used = (category.current_spent / category.monthly_limit) * 100
            
            if percentage_used <= 75:
                alert_level = "green"
            elif percentage_used <= 90:
                alert_level = "yellow"
            else:
                alert_level = "red"
            
            status[name] = {
                'limit': category.monthly_limit,
                'spent': category.current_spent,
                'remaining': remaining,
                'percentage_used': percentage_used,
                'alert_level': alert_level
            }
        
        return status
    
    def get_overspent_categories(self) -> List[str]:
        return [
            name for name, category in self.categories.items()
            if category.current_spent > category.monthly_limit
        ]
    
    def get_total_budget(self) -> float:
        return sum(category.monthly_limit for category in self.categories.values())
    
    def get_total_spent(self) -> float:
        return sum(category.current_spent for category in self.categories.values())
    
    def suggest_reallocation(self) -> Dict[str, str]:
        suggestions = {}
        overspent = []
        underspent = []
        
        for name, category in self.categories.items():
            if category.current_spent > category.monthly_limit:
                overspent.append((name, category.current_spent - category.monthly_limit))
            elif category.current_spent < category.monthly_limit * 0.7:
                underspent.append((name, category.monthly_limit - category.current_spent))
        
        if overspent and underspent:
            overspent.sort(key=lambda x: x[1], reverse=True)
            underspent.sort(key=lambda x: x[1], reverse=True)
            
            for over_cat, over_amount in overspent:
                for under_cat, under_amount in underspent:
                    if under_amount >= over_amount:
                        suggestions[over_cat] = f"Consider reallocating ${over_amount:.2f} from {under_cat}"
                        break
        
        return suggestions
    
    def generate_budget_report(self) -> str:
        report = "=== MONTHLY BUDGET REPORT ===\n\n"
        
        status = self.get_budget_status()
        overspent = self.get_overspent_categories()
        
        report += f"Total Budget: ${self.get_total_budget():.2f}\n"
        report += f"Total Spent: ${self.get_total_spent():.2f}\n"
        report += f"Overall Remaining: ${self.get_total_budget() - self.get_total_spent():.2f}\n\n"
        
        if overspent:
            report += "🚨 OVERSPENT CATEGORIES:\n"
            for category in overspent:
                cat_status = status[category]
                report += f"  • {category}: ${cat_status['spent']:.2f} / ${cat_status['limit']:.2f} "
                report += f"({cat_status['percentage_used']:.1f}%)\n"
            report += "\n"
        
        report += "CATEGORY BREAKDOWN:\n"
        for name, cat_status in status.items():
            emoji = "🔴" if cat_status['alert_level'] == "red" else "🟡" if cat_status['alert_level'] == "yellow" else "🟢"
            report += f"{emoji} {name}: ${cat_status['spent']:.2f} / ${cat_status['limit']:.2f} "
            report += f"({cat_status['percentage_used']:.1f}%)\n"
        
        suggestions = self.suggest_reallocation()
        if suggestions:
            report += "\n💡 REALLOCATION SUGGESTIONS:\n"
            for category, suggestion in suggestions.items():
                report += f"  • {category}: {suggestion}\n"
        
        return report

def create_sample_budget():
    budget_manager = BudgetManager()
    budget_manager.set_category_budget("Food", 600.0)
    budget_manager.set_category_budget("Transportation", 200.0)
    budget_manager.set_category_budget("Entertainment", 150.0)
    budget_manager.set_category_budget("Utilities", 300.0)
    budget_manager.set_category_budget("Shopping", 250.0)
    print("Sample budget created with default categories!")

if __name__ == "__main__":
    create_sample_budget()