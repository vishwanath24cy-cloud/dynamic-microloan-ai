"""Synthetic Financial Dataset Generator for AI-Based Dynamic Microloan Repayment & Cash-Flow Planner.

Generates 500 borrowers across 18 monthly cycles (Jan 2025 - Jun 2026),
yielding 9,000 realistic transaction & repayment records across 8 distinct financial behavior patterns.
"""
import csv
import random
from pathlib import Path
from datetime import datetime

# Set seed for reproducible synthetic data generation
random.seed(42)

DATA_DIR = Path(__file__).resolve().parent

# Dates for 18 monthly cycles (Jan 2025 to Jun 2026)
MONTHS = [
    "2025-01-31", "2025-02-28", "2025-03-31", "2025-04-30", "2025-05-31", "2025-06-30",
    "2025-07-31", "2025-08-31", "2025-09-30", "2025-10-31", "2025-11-30", "2025-12-31",
    "2026-01-31", "2026-02-28", "2026-03-31", "2026-04-30", "2026-05-31", "2026-06-30",
]

# Realistic names and occupations for synthetic borrowers
FIRST_NAMES = [
    "Aarav", "Bhavna", "Chirag", "Deepika", "Eshwar", "Farhan", "Geeta", "Harish", "Indira", "Jatin",
    "Kavita", "Lalit", "Meera", "Naveen", "Omkar", "Pooja", "Qadir", "Rajesh", "Sunita", "Tushar",
    "Usha", "Vikram", "Wasim", "Yash", "Zainab", "Ananya", "Bharat", "Chetan", "Divya", "Ganesh",
    "Hema", "Imran", "Jyoti", "Kiran", "Madhav", "Neelam", "Pankaj", "Ritu", "Suresh", "Tanvi",
    "Vandana", "Amit", "Bina", "Dinesh", "Gita", "Kishore", "Manish", "Preeti", "Ramesh", "Sanjay"
]

LAST_NAMES = [
    "Sharma", "Patel", "Verma", "Nair", "Rao", "Khan", "Gupta", "Joshi", "Das", "Deshmukh",
    "Iyer", "Chauhan", "Mishra", "Reddy", "Kulkarni", "Mehta", "Bhat", "Singh", "Yadav", "Pandey",
    "Mukherjee", "Chatterjee", "Shetty", "Pillai", "Gowda", "Naidu", "Sengupta", "Chopra", "Malhotra", "Kapoor"
]

OCCUPATIONS_BY_SCENARIO = {
    "stable_income": [
        "Primary School Teacher", "Bank Clerk", "Government Peon", "Supermarket Cashier",
        "Hospital Lab Technician", "Post Office Assistant", "Hardware Shop Manager", "Pharmacy Assistant"
    ],
    "temporary_income_decrease": [
        "Artisan Textile Weaver", "Handicraft Sculptor", "Freelance Graphic Designer",
        "Boutique Tailor", "Jewelry Goldsmith", "Pottery Maker"
    ],
    "two_consecutive_months_high_stress": [
        "Independent Delivery Driver", "Shared Auto Driver", "Mini-truck Transporter",
        "Mobile Phone Repairer", "Appliance Service Electrician"
    ],
    "seasonal_income": [
        "Agricultural Produce Trader", "Mango Orchard Cultivator", "Cotton Farmer",
        "Tourist Guide & Cab Driver", "Festive Clay Idol Maker", "Grain Wholesaler"
    ],
    "continuous_deterioration": [
        "Small Cafeteria Operator", "Traditional Bookstore Owner", "Typewriting & Photocopy Shop",
        "Video Game Parlor Operator", "Local DVD & Repair Rental Shop"
    ],
    "increasing_expenses": [
        "Welding Workshop Owner", "General Provision Store Owner", "Laundry Dry-cleaner",
        "Bakery Owner", "Tea Stall Franchise Owner"
    ],
    "repeated_late_repayments": [
        "Daily Wage Construction Mason", "Vegetable Cart Hawker", "Street Food Cart Vendor",
        "Loading Laborer", "Domestic Cleaning Contractor"
    ],
    "micro_enterprise_growth": [
        "Specialty Coffee Stall", "Organic Spice Packager", "Home Tiffin Delivery",
        "Tailoring Academy Tutor", "Handmade Soap Maker"
    ],
}

# Distribution of 500 borrowers across 8 financial scenarios
SCENARIO_DISTRIBUTION = [
    ("stable_income", 120),
    ("temporary_income_decrease", 70),
    ("two_consecutive_months_high_stress", 60),
    ("seasonal_income", 70),
    ("continuous_deterioration", 50),
    ("increasing_expenses", 50),
    ("repeated_late_repayments", 50),
    ("micro_enterprise_growth", 30),
]


def generate_borrowers_and_transactions():
    borrowers = []
    transactions = []

    borrower_id_counter = 1

    # Define exact configurations for IDs 1 to 5 to match existing demo database
    demo_configs = {
        1: ("Aarav Sharma", 34, "Grocery Store Owner", 50000.0, 4500.0, "stable_income", 46000.0, 28500.0),
        2: ("Bhavna Patel", 29, "Artisan Textile Weaver", 30000.0, 2800.0, "temporary_income_decrease", 25000.0, 16000.0),
        3: ("Chirag Verma", 42, "Independent Delivery Driver", 40000.0, 3600.0, "two_consecutive_months_high_stress", 32000.0, 22000.0),
        4: ("Deepika Nair", 36, "Agricultural Produce Trader", 60000.0, 5200.0, "seasonal_income", 38000.0, 24000.0),
        5: ("Eshwar Rao", 48, "Small Cafeteria Operator", 75000.0, 6800.0, "continuous_deterioration", 52000.0, 36000.0),
    }

    for scenario_name, count in SCENARIO_DISTRIBUTION:
        # Determine how many in this scenario were handled by demo_configs
        current_scenario_borrowers = 0

        while current_scenario_borrowers < count:
            b_id = borrower_id_counter

            if b_id in demo_configs:
                name, age, occupation, loan_amt, emi, scenario, base_inc, base_exp = demo_configs[b_id]
            else:
                first = random.choice(FIRST_NAMES)
                last = random.choice(LAST_NAMES)
                name = f"{first} {last}"
                age = random.randint(22, 58)
                occupation = random.choice(OCCUPATIONS_BY_SCENARIO[scenario_name])
                loan_amt = round(random.choice([25000, 30000, 40000, 50000, 60000, 75000, 80000]), 2)
                # EMI typically 8% to 10% of principal for 12-14 month microloans
                emi = round(loan_amt * random.uniform(0.085, 0.098), 2)
                scenario = scenario_name

                # Baseline income scaled appropriately for the EMI (income usually 5x to 10x of EMI)
                base_inc = round(emi * random.uniform(5.5, 9.5), 2)
                base_exp = round(base_inc * random.uniform(0.55, 0.70), 2)

            borrower_record = {
                "borrower_id": b_id,
                "name": name,
                "age": age,
                "occupation": occupation,
                "loan_amount": loan_amt,
                "emi_amount": emi,
                "loan_start_date": "2025-01-15",
                "repayment_frequency": "monthly",
                "financial_scenario": scenario,
            }
            borrowers.append(borrower_record)

            # Generate 18 monthly transaction cycles for this borrower
            running_cash_balance = round(base_inc * random.uniform(0.3, 0.6), 2)

            for m_idx, month_date in enumerate(MONTHS):
                # Apply financial pattern logic based on scenario
                m_num = m_idx + 1  # 1 to 18

                if scenario == "stable_income":
                    # Stable salary or shop revenue with minor random noise (±3%)
                    noise_inc = random.uniform(-0.03, 0.04)
                    noise_exp = random.uniform(-0.02, 0.03)
                    inc = round(base_inc * (1 + noise_inc), 2)
                    exp = round(base_exp * (1 + noise_exp), 2)
                    avail = round(inc - exp, 2)
                    days_late = 0
                    rep_amt = emi
                    status = "paid"

                elif scenario == "temporary_income_decrease":
                    # Normal for months 1-4, sharp shock in months 5-6 (or 11-12), then rebounds
                    if m_num in [5, 6]:
                        inc = round(base_inc * random.uniform(0.50, 0.60), 2)  # 40-50% drop
                        exp = round(base_exp * random.uniform(0.85, 0.95), 2)
                        days_late = random.randint(4, 9)
                        rep_amt = emi
                        status = "late"
                    elif m_num == 7:
                        inc = round(base_inc * random.uniform(0.75, 0.85), 2)  # partial recovery
                        exp = round(base_exp * random.uniform(0.90, 1.00), 2)
                        days_late = random.randint(1, 4)
                        rep_amt = emi
                        status = "paid"
                    else:
                        inc = round(base_inc * random.uniform(0.96, 1.05), 2)
                        exp = round(base_exp * random.uniform(0.95, 1.02), 2)
                        days_late = 0
                        rep_amt = emi
                        status = "paid"
                    avail = round(inc - exp, 2)

                elif scenario == "two_consecutive_months_high_stress":
                    # Severe shock in months 8 and 9 (or 5 and 6)
                    if m_num in [8, 9]:
                        inc = round(base_inc * random.uniform(0.40, 0.50), 2)
                        exp = round(base_exp * random.uniform(0.95, 1.08), 2)  # expenses exceed income
                        days_late = random.randint(15, 25)
                        rep_amt = emi
                        status = "late"
                    elif m_num == 10:
                        inc = round(base_inc * random.uniform(0.65, 0.75), 2)
                        exp = round(base_exp * random.uniform(0.95, 1.02), 2)
                        days_late = random.randint(6, 12)
                        rep_amt = emi
                        status = "late"
                    else:
                        inc = round(base_inc * random.uniform(0.95, 1.04), 2)
                        exp = round(base_exp * random.uniform(0.95, 1.02), 2)
                        days_late = 0
                        rep_amt = emi
                        status = "paid"
                    avail = round(inc - exp, 2)

                elif scenario == "seasonal_income":
                    # Months 3-5 (March-May) off-season lean; Months 9-11 (Sept-Nov) festive/harvest surge
                    month_in_year = (m_idx % 12) + 1
                    if month_in_year in [3, 4, 5]:
                        # Lean / sowing
                        inc = round(base_inc * random.uniform(0.48, 0.62), 2)
                        exp = round(base_exp * random.uniform(0.85, 0.95), 2)
                        days_late = random.randint(3, 8)
                        rep_amt = emi
                        status = "paid"
                    elif month_in_year in [9, 10, 11]:
                        # Harvest / festival boom
                        inc = round(base_inc * random.uniform(1.45, 1.85), 2)
                        exp = round(base_exp * random.uniform(1.05, 1.15), 2)
                        days_late = 0
                        rep_amt = emi
                        status = "paid"
                    else:
                        inc = round(base_inc * random.uniform(0.92, 1.08), 2)
                        exp = round(base_exp * random.uniform(0.95, 1.03), 2)
                        days_late = 0
                        rep_amt = emi
                        status = "paid"
                    avail = round(inc - exp, 2)

                elif scenario == "continuous_deterioration":
                    # Gradual multi-month decay
                    decay_factor = max(0.28, 1.0 - (m_num * 0.042))
                    inc = round(base_inc * decay_factor * random.uniform(0.95, 1.03), 2)
                    exp = round(base_exp * max(0.80, 1.0 - (m_num * 0.012)), 2)  # expenses are sticky
                    avail = round(inc - exp, 2)

                    if m_num <= 4:
                        days_late = 0
                        rep_amt = emi
                        status = "paid"
                    elif m_num <= 8:
                        days_late = random.randint(10, 20)
                        rep_amt = emi
                        status = "late"
                    elif m_num <= 12:
                        days_late = random.randint(28, 45)
                        rep_amt = round(emi * 0.5, 2)
                        status = "missed"
                    else:
                        days_late = random.randint(55, 90)
                        rep_amt = 0.0
                        status = "missed"

                elif scenario == "increasing_expenses":
                    # Income flat, but expenses rise steadily due to family/medical/inflation (+3% per month)
                    inc = round(base_inc * random.uniform(0.97, 1.03), 2)
                    exp_factor = 1.0 + (m_num * 0.028)
                    exp = round(base_exp * exp_factor, 2)
                    avail = round(inc - exp, 2)

                    if avail >= emi * 1.5:
                        days_late = 0
                        rep_amt = emi
                        status = "paid"
                    elif avail >= emi:
                        days_late = random.randint(2, 6)
                        rep_amt = emi
                        status = "paid"
                    elif avail > 0:
                        days_late = random.randint(8, 16)
                        rep_amt = emi
                        status = "late"
                    else:
                        days_late = random.randint(22, 35)
                        rep_amt = round(max(0, avail + emi * 0.5), 2)
                        status = "late"

                elif scenario == "repeated_late_repayments":
                    # Tight cash flow every month, available cash barely near EMI
                    inc = round(emi * random.uniform(2.8, 3.5), 2)
                    exp = round(inc - (emi * random.uniform(0.85, 1.15)), 2)
                    avail = round(inc - exp, 2)
                    # Frequent payment delay of 5-18 days
                    days_late = random.randint(5, 18)
                    rep_amt = emi
                    status = "late"

                elif scenario == "micro_enterprise_growth":
                    # Positive growth trend (+2.5% per month) with slight volatility
                    growth_factor = 1.0 + (m_num * 0.025)
                    inc = round(base_inc * growth_factor * random.uniform(0.92, 1.08), 2)
                    exp = round(base_exp * (1 + (m_num * 0.012)) * random.uniform(0.95, 1.04), 2)
                    avail = round(inc - exp, 2)
                    days_late = 0
                    rep_amt = emi
                    status = "paid"

                else:
                    # Default fallback
                    inc = base_inc
                    exp = base_exp
                    avail = round(inc - exp, 2)
                    days_late = 0
                    rep_amt = emi
                    status = "paid"

                # Update cumulative cash balance
                running_cash_balance = round(running_cash_balance + avail - rep_amt, 2)

                transaction_record = {
                    "borrower_id": b_id,
                    "date": month_date,
                    "income": inc,
                    "expenses": exp,
                    "available_cash": avail,
                    "cash_balance": running_cash_balance,
                    "emi_amount": emi,
                    "repayment_amount": rep_amt,
                    "days_late": days_late,
                    "repayment_status": status,
                    "financial_scenario": scenario,
                }
                transactions.append(transaction_record)

            borrower_id_counter += 1
            current_scenario_borrowers += 1

    return borrowers, transactions


def save_dataset_to_csv(borrowers, transactions):
    borrowers_file = DATA_DIR / "borrowers.csv"
    transactions_file = DATA_DIR / "borrower_transactions.csv"

    # 1. Write borrowers.csv
    borrower_fields = [
        "borrower_id", "name", "age", "occupation", "loan_amount",
        "emi_amount", "loan_start_date", "repayment_frequency", "financial_scenario"
    ]
    with open(borrowers_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=borrower_fields)
        writer.writeheader()
        writer.writerows(borrowers)

    print(f"Saved {len(borrowers)} borrowers to {borrowers_file}")

    # 2. Write borrower_transactions.csv
    transaction_fields = [
        "borrower_id", "date", "income", "expenses", "available_cash",
        "cash_balance", "emi_amount", "repayment_amount", "days_late",
        "repayment_status", "financial_scenario"
    ]
    with open(transactions_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=transaction_fields)
        writer.writeheader()
        writer.writerows(transactions)

    print(f"Saved {len(transactions)} transaction records to {transactions_file}")


if __name__ == "__main__":
    b_data, tx_data = generate_borrowers_and_transactions()
    save_dataset_to_csv(b_data, tx_data)
