import datetime
from typing import List, Dict, Tuple
import matplotlib.pyplot as plt
import pandas as pd

def validate_amount(amount_str: str) -> float:
    try:
        amount = float(amount_str)
        if amount <= 0:
            raise ValueError("Amount must be positive")
        return amount
    except ValueError:
        raise ValueError("Invalid amount format")

def get_date_range(start_date: datetime.date, end_date: datetime.date) -> List[datetime.date]:
    date_list = []
    current_date = start_date
    while current_date <= end_date:
        date_list.append(current_date)
        current_date += datetime.timedelta(days=1)
    return date_list

def calculate_trend(data: List[Tuple[datetime.date, float]], period_days: int = 30) -> str:
    if len(data) < 2:
        return "insufficient_data"
    
    recent_data = data[-period_days:]
    older_data = data[-period_days*2:-period_days] if len(data) >= period_days*2 else data[:-period_days]
    
    if not older_data:
        return "insufficient_data"
    
    recent_avg = sum(item[1] for item in recent_data) / len(recent_data)
    older_avg = sum(item[1] for item in older_data) / len(older_data)
    
    if recent_avg > older_avg * 1.1:
        return "increasing"
    elif recent_avg < older_avg * 0.9:
        return "decreasing"
    else:
        return "stable"

def generate_spending_chart(category_data: Dict[str, float], output_file: str = "spending_chart.png"):
    categories = list(category_data.keys())
    amounts = list(category_data.values())
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(categories, amounts, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'])
    
    plt.title('Monthly Spending by Category', fontsize=16, fontweight='bold')
    plt.xlabel('Categories', fontsize=12)
    plt.ylabel('Amount ($)', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    
    for bar, amount in zip(bars, amounts):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(amounts)*0.01, 
                f'${amount:.0f}', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()

def export_to_csv(transactions_data: List[Dict], filename: str = "transactions_export.csv"):
    df = pd.DataFrame(transactions_data)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    df.to_csv(filename, index=False)
    return filename

def calculate_savings_rate(income: float, expenses: float) -> float:
    if income == 0:
        return 0.0
    return ((income - expenses) / income) * 100

def get_budget_status(actual_expense: float, budgeted_amount: float) -> Dict[str, any]:
    if budgeted_amount == 0:
        return {"status": "no_budget", "percentage": 0, "remaining": 0}
    
    percentage_used = (actual_expense / budgeted_amount) * 100
    remaining = budgeted_amount - actual_expense
    
    if percentage_used <= 80:
        status = "good"
    elif percentage_used <= 100:
        status = "warning"
    else:
        status = "over_budget"
    
    return {
        "status": status,
        "percentage": percentage_used,
        "remaining": remaining
    }

def format_currency(amount: float, currency_symbol: str = "$") -> str:
    return f"{currency_symbol}{amount:,.2f}"

def parse_date_input(date_str: str) -> datetime.date:
    formats = ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y%m%d']
    
    for fmt in formats:
        try:
            return datetime.datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    
    raise ValueError(f"Unable to parse date: {date_str}")

def get_financial_health_score(income: float, expenses: float, savings: float) -> Dict[str, any]:
    if income == 0:
        return {"score": 0, "grade": "F", "recommendations": ["Increase income sources"]}
    
    savings_rate = (savings / income) * 100
    expense_ratio = (expenses / income) * 100
    
    score = 0
    if savings_rate >= 20:
        score += 40
    elif savings_rate >= 10:
        score += 25
    elif savings_rate >= 5:
        score += 15
    
    if expense_ratio <= 50:
        score += 30
    elif expense_ratio <= 70:
        score += 20
    elif expense_ratio <= 90:
        score += 10
    
    emergency_fund_months = savings / (expenses / 12) if expenses > 0 else 0
    if emergency_fund_months >= 6:
        score += 30
    elif emergency_fund_months >= 3:
        score += 20
    elif emergency_fund_months >= 1:
        score += 10
    
    grade_map = {
        (90, 100): "A+",
        (80, 89): "A",
        (70, 79): "B",
        (60, 69): "C",
        (50, 59): "D",
        (0, 49): "F"
    }
    
    grade = "F"
    for (min_score, max_score), letter_grade in grade_map.items():
        if min_score <= score <= max_score:
            grade = letter_grade
            break
    
    recommendations = []
    if savings_rate < 10:
        recommendations.append("Increase savings rate to at least 10%")
    if expense_ratio > 70:
        recommendations.append("Reduce monthly expenses")
    if emergency_fund_months < 3:
        recommendations.append("Build emergency fund (3-6 months expenses)")
    
    return {
        "score": score,
        "grade": grade,
        "savings_rate": savings_rate,
        "expense_ratio": expense_ratio,
        "emergency_fund_months": emergency_fund_months,
        "recommendations": recommendations
    }