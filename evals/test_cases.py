"""
Pre-defined expense scenarios used to evaluate the pipeline.

Each scenario has:
  - name: short label
  - description: human-readable summary
  - expenses: list of dicts (date, description, amount, category)
  - expected_signals: keywords that a correct analysis MUST mention
    (used by scorer.py — simple substring checks, case-insensitive)
"""

TEST_CASES = [
    {
        "name": "Student Budget",
        "description": "Student with high food-delivery spend and low fixed costs.",
        "expenses": [
            {"date": "2024-01-02", "description": "Uber Eats", "amount": 34.50, "category": "Food Delivery"},
            {"date": "2024-01-05", "description": "DoorDash", "amount": 28.00, "category": "Food Delivery"},
            {"date": "2024-01-08", "description": "Grocery Store", "amount": 55.00, "category": "Groceries"},
            {"date": "2024-01-10", "description": "Uber Eats", "amount": 22.00, "category": "Food Delivery"},
            {"date": "2024-01-12", "description": "Netflix", "amount": 15.99, "category": "Entertainment"},
            {"date": "2024-01-15", "description": "DoorDash", "amount": 31.00, "category": "Food Delivery"},
            {"date": "2024-01-18", "description": "Spotify", "amount": 9.99, "category": "Entertainment"},
            {"date": "2024-01-20", "description": "Grocery Store", "amount": 48.00, "category": "Groceries"},
            {"date": "2024-01-23", "description": "Uber Eats", "amount": 26.50, "category": "Food Delivery"},
            {"date": "2024-01-25", "description": "Public Transit Pass", "amount": 35.00, "category": "Transport"},
        ],
        "expected_signals": ["food", "delivery", "groceries", "entertainment"],
    },
    {
        "name": "Professional",
        "description": "Working professional with high rent and moderate dining.",
        "expenses": [
            {"date": "2024-01-01", "description": "Rent Payment", "amount": 1850.00, "category": "Housing"},
            {"date": "2024-01-03", "description": "Whole Foods", "amount": 120.00, "category": "Groceries"},
            {"date": "2024-01-05", "description": "Restaurant Dinner", "amount": 68.00, "category": "Dining"},
            {"date": "2024-01-08", "description": "Electric Bill", "amount": 85.00, "category": "Utilities"},
            {"date": "2024-01-10", "description": "Internet Bill", "amount": 60.00, "category": "Utilities"},
            {"date": "2024-01-12", "description": "Coffee Shop", "amount": 45.00, "category": "Dining"},
            {"date": "2024-01-15", "description": "Gym Membership", "amount": 50.00, "category": "Health"},
            {"date": "2024-01-18", "description": "Lunch Out", "amount": 55.00, "category": "Dining"},
            {"date": "2024-01-22", "description": "Car Insurance", "amount": 140.00, "category": "Insurance"},
            {"date": "2024-01-28", "description": "Whole Foods", "amount": 110.00, "category": "Groceries"},
        ],
        "expected_signals": ["housing", "rent", "dining", "utilities"],
    },
    {
        "name": "Overspender",
        "description": "Lifestyle inflation — entertainment and dining dominate.",
        "expenses": [
            {"date": "2024-01-02", "description": "Concert Tickets", "amount": 250.00, "category": "Entertainment"},
            {"date": "2024-01-04", "description": "Fancy Restaurant", "amount": 180.00, "category": "Dining"},
            {"date": "2024-01-06", "description": "Bar Tab", "amount": 95.00, "category": "Dining"},
            {"date": "2024-01-08", "description": "Steam Games", "amount": 60.00, "category": "Entertainment"},
            {"date": "2024-01-10", "description": "Clothes Shopping", "amount": 320.00, "category": "Shopping"},
            {"date": "2024-01-13", "description": "Movie Night (multiple)", "amount": 75.00, "category": "Entertainment"},
            {"date": "2024-01-16", "description": "Sushi Restaurant", "amount": 140.00, "category": "Dining"},
            {"date": "2024-01-20", "description": "Online Shopping", "amount": 210.00, "category": "Shopping"},
            {"date": "2024-01-24", "description": "Sports Event", "amount": 190.00, "category": "Entertainment"},
            {"date": "2024-01-28", "description": "Wine & Dine", "amount": 120.00, "category": "Dining"},
        ],
        "expected_signals": ["entertainment", "dining", "shopping", "saving"],
    },
    {
        "name": "Saver",
        "description": "Disciplined saver with low discretionary spend.",
        "expenses": [
            {"date": "2024-01-01", "description": "Rent", "amount": 900.00, "category": "Housing"},
            {"date": "2024-01-03", "description": "Aldi Groceries", "amount": 60.00, "category": "Groceries"},
            {"date": "2024-01-05", "description": "Savings Transfer", "amount": 500.00, "category": "Savings"},
            {"date": "2024-01-08", "description": "Electric Bill", "amount": 55.00, "category": "Utilities"},
            {"date": "2024-01-10", "description": "Emergency Fund Transfer", "amount": 200.00, "category": "Savings"},
            {"date": "2024-01-12", "description": "Bus Pass", "amount": 30.00, "category": "Transport"},
            {"date": "2024-01-15", "description": "Aldi Groceries", "amount": 55.00, "category": "Groceries"},
            {"date": "2024-01-20", "description": "Phone Bill", "amount": 35.00, "category": "Utilities"},
            {"date": "2024-01-22", "description": "Library Fine", "amount": 3.00, "category": "Miscellaneous"},
            {"date": "2024-01-28", "description": "Investment Transfer", "amount": 300.00, "category": "Savings"},
        ],
        "expected_signals": ["savings", "housing", "groceries", "emergency"],
    },
    {
        "name": "Inconsistent",
        "description": "Mix of large one-off expenses and small recurring ones.",
        "expenses": [
            {"date": "2024-01-01", "description": "Laptop Repair", "amount": 450.00, "category": "Electronics"},
            {"date": "2024-01-03", "description": "Coffee", "amount": 4.50, "category": "Dining"},
            {"date": "2024-01-05", "description": "Grocery Store", "amount": 72.00, "category": "Groceries"},
            {"date": "2024-01-07", "description": "Dentist Visit", "amount": 220.00, "category": "Health"},
            {"date": "2024-01-10", "description": "Coffee", "amount": 5.00, "category": "Dining"},
            {"date": "2024-01-14", "description": "Parking Ticket", "amount": 75.00, "category": "Transport"},
            {"date": "2024-01-15", "description": "Coffee", "amount": 4.75, "category": "Dining"},
            {"date": "2024-01-18", "description": "Flight Ticket", "amount": 380.00, "category": "Travel"},
            {"date": "2024-01-22", "description": "Coffee", "amount": 4.50, "category": "Dining"},
            {"date": "2024-01-25", "description": "Grocery Store", "amount": 68.00, "category": "Groceries"},
        ],
        "expected_signals": ["health", "travel", "unusual", "one-time"],
    },
]
