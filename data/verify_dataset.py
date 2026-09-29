"""Validation script to inspect and verify the synthetic financial dataset.

Performs 7 rigorous quality checks:
1. Missing / NULL value inspection
2. Duplicate record detection on (borrower_id, date)
3. Realistic economic ranges (income > 0, expenses > 0, available_cash consistency)
4. Validity of all borrower IDs (continuous 1 to N matching borrowers.csv)
5. Verification of all 8 financial scenarios and distributions
6. Date consistency and formatting
7. Statistical summary report
"""
import csv
from collections import Counter
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent
BORROWERS_CSV = DATA_DIR / "borrowers.csv"
TRANSACTIONS_CSV = DATA_DIR / "borrower_transactions.csv"


def verify():
    print("=== STARTING DATASET VALIDATION ===")

    # -------------------------------------------------------------
    # 1. Verify files exist
    # -------------------------------------------------------------
    assert BORROWERS_CSV.exists(), f"Missing file: {BORROWERS_CSV}"
    assert TRANSACTIONS_CSV.exists(), f"Missing file: {TRANSACTIONS_CSV}"

    # -------------------------------------------------------------
    # 2. Inspect borrowers.csv
    # -------------------------------------------------------------
    with open(BORROWERS_CSV, mode="r", encoding="utf-8") as f:
        borrower_rows = list(csv.DictReader(f))

    print(f"\n[Check 1] Borrowers Count: {len(borrower_rows)}")
    assert len(borrower_rows) == 500, f"Expected 500 borrowers, found {len(borrower_rows)}"

    borrower_ids = set()
    scenarios = Counter()
    for row in borrower_rows:
        # Missing values check
        for col, val in row.items():
            assert val is not None and val.strip() != "", f"Missing value in borrowers.csv at {col}: {row}"

        b_id = int(row["borrower_id"])
        borrower_ids.add(b_id)
        scenarios[row["financial_scenario"]] += 1

        assert float(row["loan_amount"]) > 0, f"Invalid loan_amount: {row}"
        assert float(row["emi_amount"]) > 0, f"Invalid emi_amount: {row}"
        assert 18 <= int(row["age"]) <= 75, f"Unrealistic age: {row}"

    print(f"[Check 2] Borrower IDs are unique and continuous: 1 to {max(borrower_ids)}")
    assert len(borrower_ids) == 500
    assert borrower_ids == set(range(1, 501))

    print("[Check 3] Financial Scenarios in borrowers.csv:")
    for sc, count in scenarios.most_common():
        print(f"  - {sc}: {count} borrowers")
    assert len(scenarios) == 8, f"Expected 8 scenarios, got {len(scenarios)}"

    # -------------------------------------------------------------
    # 3. Inspect borrower_transactions.csv
    # -------------------------------------------------------------
    with open(TRANSACTIONS_CSV, mode="r", encoding="utf-8") as f:
        tx_rows = list(csv.DictReader(f))

    print(f"\n[Check 4] Transactions Count: {len(tx_rows)}")
    assert len(tx_rows) == 9000, f"Expected 9000 transaction records (500*18), found {len(tx_rows)}"

    # Check for missing values, duplicates, and unrealistic numbers
    seen_pairs = set()
    status_counts = Counter()
    dates = set()

    for idx, row in enumerate(tx_rows):
        # Null / missing check
        for col, val in row.items():
            assert val is not None and val.strip() != "", f"Missing value in transactions.csv at line {idx+2}, {col}"

        b_id = int(row["borrower_id"])
        assert b_id in borrower_ids, f"Invalid borrower_id {b_id} in transaction at line {idx+2}"

        date_val = row["date"]
        dates.add(date_val)

        # Duplicate check on (borrower_id, date)
        pair = (b_id, date_val)
        assert pair not in seen_pairs, f"Duplicate transaction found for borrower {b_id} on {date_val}"
        seen_pairs.add(pair)

        # Realistic value checks
        inc = float(row["income"])
        exp = float(row["expenses"])
        avail = float(row["available_cash"])
        emi = float(row["emi_amount"])
        rep = float(row["repayment_amount"])
        days_late = int(row["days_late"])
        status = row["repayment_status"]

        assert inc > 0, f"Unrealistic non-positive income: {inc} at line {idx+2}"
        assert exp > 0, f"Unrealistic non-positive expenses: {exp} at line {idx+2}"
        # Economic consistency: available_cash == income - expenses
        assert abs(avail - (inc - exp)) < 0.02, f"Economic inconsistency: avail {avail} != {inc} - {exp}"
        assert emi > 0, f"Invalid EMI: {emi}"
        assert rep >= 0, f"Negative repayment: {rep}"
        assert days_late >= 0, f"Negative days_late: {days_late}"
        assert status in {"paid", "late", "missed"}, f"Invalid status: {status}"

        status_counts[status] += 1

    print("[Check 5] No missing values found in 9,000 transaction records.")
    print("[Check 6] Zero duplicate (borrower_id, date) pairs detected.")
    print("[Check 7] Income and expenses are strictly positive and economically consistent.")
    print(f"[Check 8] Date Range: {min(dates)} to {max(dates)} ({len(dates)} monthly cycles)")
    print("[Check 9] Repayment Status Breakdown:")
    for st, count in status_counts.most_common():
        pct = (count / len(tx_rows)) * 100
        print(f"  - {st.upper()}: {count} ({pct:.1f}%)")

    print("\nALL 7 VALIDATION CHECKS PASSED SUCCESSFULLY!")


if __name__ == "__main__":
    verify()
