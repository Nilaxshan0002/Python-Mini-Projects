import json
import os
from datetime import datetime

# ==========================================
# 1. OOP Structure & Data Handling
# ==========================================
class Transaction:
    """Represents a single income or expense record."""
    def __init__(self, trans_type, category, amount, description, date):
        self.type = trans_type      # "Income" or "Expense"
        self.category = category    # e.g., "Food", "Salary"
        self.amount = amount
        self.description = description
        self.date = date

    def to_dict(self):
        """Converts the object to a dictionary for JSON saving."""
        return {
            "type": self.type,
            "category": self.category,
            "amount": self.amount,
            "description": self.description,
            "date": self.date
        }

class BudgetTracker:
    """Manages the list of transactions, calculations, and storage."""
    def __init__(self, filename="budget_data.json"):
        self.filename = filename
        self.transactions = self.load_data()

    def load_data(self):
        """Loads transactions from the JSON file."""
        if not os.path.exists(self.filename):
            return []
        try:
            with open(self.filename, 'r') as file:
                data = json.load(file)
                return [Transaction(item['type'], item['category'], item['amount'], item['description'], item['date']) for item in data]
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def save_data(self):
        """Saves transactions to the JSON file."""
        with open(self.filename, 'w') as file:
            json.dump([t.to_dict() for t in self.transactions], file, indent=4)

    def add_transaction(self, trans_type, category, amount, description):
        """Adds a new transaction and saves it."""
        date = datetime.now().strftime("%Y-%m-%d")
        new_trans = Transaction(trans_type, category, amount, description, date)
        self.transactions.append(new_trans)
        self.save_data()
        print(f"✅ {trans_type} of ${amount:.2f} added successfully!")

    def calculate_balance(self):
        """Calculates total income, total expense, and current balance."""
        total_income = sum(t.amount for t in self.transactions if t.type == "Income")
        total_expense = sum(t.amount for t in self.transactions if t.type == "Expense")
        balance = total_income - total_expense
        return total_income, total_expense, balance

    def generate_report(self):
        """Generates a detailed financial report."""
        if not self.transactions:
            print("\n📭 No transactions found. Add some income or expenses first.")
            return

        total_income, total_expense, balance = self.calculate_balance()

        print("\n===================================")
        print("📊 PERSONAL BUDGET REPORT 📊")
        print("===================================")
        print(f"💰 Total Income:  ${total_income:.2f}")
        print(f"💸 Total Expense: ${total_expense:.2f}")
        print("-----------------------------------")
        
        if balance >= 0:
            print(f"✅ Current Balance: ${balance:.2f} (You are in the green!)")
        else:
            print(f"🚨 Current Balance: ${balance:.2f} (Warning: You are over budget!)")
        print("===================================")

        print("\n📂 Breakdown by Category:")
        categories = {}
        for t in self.transactions:
            # Only count expenses for the category breakdown
            if t.type == "Expense":
                categories[t.category] = categories.get(t.category, 0) + t.amount
        
        if categories:
            for cat, amount in categories.items():
                print(f"  • {cat}: ${amount:.2f}")
        else:
            print("  No expenses recorded yet.")
        print("===================================\n")


# ==========================================
# 2. Input Validation Helpers
# ==========================================

def get_valid_amount(prompt):
    """Ensures the user inputs a valid positive number for money."""
    while True:
        try:
            amount = float(input(prompt))
            if amount <= 0:
                print("❌ Amount must be greater than zero.")
                continue
            return amount
        except ValueError:
            print("❌ Invalid input. Please enter a valid number (e.g., 50.00).")

def get_valid_choice(prompt, valid_choices):
    """Ensures user picks a valid menu option."""
    choice = input(prompt).strip()
    while choice not in valid_choices:
        print(f"❌ Invalid choice. Please enter one of: {', '.join(valid_choices)}")
        choice = input(prompt).strip()
    return choice

# ==========================================
# 3. CLI & Flowchart Logic
# ==========================================

def main():
    tracker = BudgetTracker()

    while True:
        print("\n=================================")
        print("💵 PERSONAL BUDGET TRACKER 💵")
        print("=================================")
        print("1. Add Income")
        print("2. Add Expense")
        print("3. View Report & Balance")
        print("4. View Transaction History")
        print("5. Exit")
        print("=================================")
        
        choice = get_valid_choice("Select an option (1-5): ", ['1', '2', '3', '4', '5'])

        if choice == '1' or choice == '2':
            trans_type = "Income" if choice == '1' else "Expense"
            print(f"\n--- Adding {trans_type} ---")
            
            # Category Input
            category = input("Enter category (e.g., Salary, Food, Rent, Fun): ").strip()
            if not category:
                category = "Uncategorized"

            # Amount Input (Validation happens here)
            amount = get_valid_amount("Enter amount: $")
            
            # Description Input
            description = input("Enter a brief description: ").strip()
            
            # Save it
            tracker.add_transaction(trans_type, category, amount, description)

        elif choice == '3':
            # Calculate and Generate Report
            tracker.generate_report()

        elif choice == '4':
            # Show History
            if not tracker.transactions:
                print("\n📭 No transactions recorded yet.")
            else:
                print("\n--- 📜 TRANSACTION HISTORY ---")
                for t in reversed(tracker.transactions): # Show newest first
                    sign = "+" if t.type == "Income" else "-"
                    print(f"[{t.date}] {sign}${t.amount:.2f} | {t.category} | {t.description}")
                print("------------------------------")

        elif choice == '5':
            print("👋 Goodbye! Your financial data has been saved.")
            break

if __name__ == "__main__":
    main()