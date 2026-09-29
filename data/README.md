# Data Directory

This folder contains the SQLite database, synthetic dataset generation scripts, and historical transaction datasets for the **AI-Based Dynamic Microloan Repayment & Cash-Flow Planner**.

---

## Files

1. **`microloans.db`**:
   - SQLite database automatically initialized by FastAPI on backend startup.
2. **`generate_dataset.py`**:
   - Synthetic dataset generator script creating 500 borrowers and 9,000 monthly transaction records across 8 financial scenarios.
3. **`verify_dataset.py`**:
   - Validation script checking missing values, duplicates, economic consistency, and scenario distribution.
4. **`borrowers.csv`** (500 records):
   - Metadata for all 500 synthetic borrowers (`borrower_id`, `name`, `age`, `occupation`, `loan_amount`, `emi_amount`, `loan_start_date`, `repayment_frequency`, `financial_scenario`).
5. **`borrower_transactions.csv`** (9,000 records):
   - Monthly historical transaction records spanning 18 months (`2025-01-31` to `2026-06-30`).

---

## Dataset Schema (`borrower_transactions.csv`)

| Column | Type | Description |
|---|---|---|
| `borrower_id` | Integer | Unique identifier (1 to 500) |
| `date` | String | End of month date (`YYYY-MM-DD`) |
| `income` | Float | Monthly gross income / revenue |
| `expenses` | Float | Monthly cost of living and business operations |
| `available_cash` | Float | Calculated net surplus: `income - expenses` |
| `cash_balance` | Float | Cumulative savings/account cash balance |
| `emi_amount` | Float | Contracted monthly loan installment |
| `repayment_amount` | Float | Actual amount repaid in the cycle |
| `days_late` | Integer | Delay in days (0 = on-time) |
| `repayment_status` | String | `paid`, `late`, or `missed` |
| `financial_scenario` | String | Underlying behavioral archetype |

---

## Financial Scenarios Represented

1. **`stable_income`** (116 borrowers): Regular income and steady surplus, zero defaults.
2. **`temporary_income_decrease`** (71 borrowers): 1-2 month isolated shock (illness/supply delay), minor delays, quick full recovery.
3. **`two_consecutive_months_high_stress`** (61 borrowers): Severe 2-month deficit triggering persistent stress criteria.
4. **`seasonal_income`** (71 borrowers): Agricultural/tourism cycle with predictable off-season lean and harvest surge.
5. **`continuous_deterioration`** (51 borrowers): Multi-month business contraction leading to chronic delinquency and missed payments.
6. **`increasing_expenses`** (50 borrowers): Flat revenue with inflation/medical cost escalation squeezing liquidity.
7. **`repeated_late_repayments`** (50 borrowers): Daily wage/marginal cash flow with frequent 5-18 day payment delays.
8. **`micro_enterprise_growth`** (30 borrowers): Growing micro-business with upward revenue trajectory (+2.5%/mo).

---

## How to Regenerate & Validate

```bash
cd data
python generate_dataset.py
python verify_dataset.py
```
