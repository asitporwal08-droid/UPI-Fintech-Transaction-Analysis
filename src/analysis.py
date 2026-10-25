"""Reproducible beginner-level analysis of synthetic UPI-style transactions."""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "upi_transactions.csv"
FIGURES = ROOT / "reports" / "figures"
REPORT_PATH = ROOT / "reports" / "findings.md"

def main():
    FIGURES.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(DATA_PATH)

    # 1) Inspect and clean
    rows_before = len(df)
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    duplicate_ids = int(df["transaction_id"].duplicated().sum())
    missing_by_column = df.isna().sum()
    invalid_amounts = int((df["amount_inr"].isna() | (df["amount_inr"] < 0)).sum())
    df = df.drop_duplicates(subset=["transaction_id"]).copy()
    df = df.dropna(subset=["timestamp", "amount_inr"]).copy()
    df = df[df["amount_inr"] >= 0].copy()

    # 2) Feature engineering
    df["hour"] = df["timestamp"].dt.hour
    df["month"] = df["timestamp"].dt.to_period("M").astype(str)
    df["amount_band"] = pd.cut(
        df["amount_inr"],
        bins=[-0.01, 500, 2000, 10000, float("inf")],
        labels=["0-500", "501-2000", "2001-10000", "10000+"]
    )

    # 3) Summaries
    by_status = df.groupby("transaction_status", as_index=False).agg(
        transaction_count=("transaction_id", "count"),
        total_amount_inr=("amount_inr", "sum"),
        average_amount_inr=("amount_inr", "mean")
    ).sort_values("transaction_count", ascending=False)
    by_hour = df.groupby("hour", as_index=False).agg(
        transaction_count=("transaction_id", "count"),
        average_amount_inr=("amount_inr", "mean")
    )
    by_method = df.groupby("payment_method", as_index=False).agg(
        transaction_count=("transaction_id", "count"),
        total_amount_inr=("amount_inr", "sum")
    ).sort_values("total_amount_inr", ascending=False)
    flagged = df[df["is_flagged"] == 1]
    flag_hour = flagged.groupby("hour").size().sort_values(ascending=False)
    top_flag_hour = int(flag_hour.index[0]) if not flag_hour.empty else None
    flag_count = int(len(flagged))
    flag_pct = (100 * flag_count / len(df)) if len(df) else 0
    successful_count = int((df["transaction_status"] == "SUCCESS").sum())

    # 4) Charts
    plt.figure(figsize=(8, 5))
    status_counts = df["transaction_status"].value_counts()
    plt.bar(status_counts.index, status_counts.values)
    plt.title("Transaction Count by Status")
    plt.xlabel("Transaction status")
    plt.ylabel("Number of transactions")
    plt.tight_layout()
    plt.savefig(FIGURES / "transactions_by_status.png", dpi=150)
    plt.close()

    plt.figure(figsize=(9, 5))
    plt.plot(by_hour["hour"], by_hour["transaction_count"], marker="o")
    plt.title("Transaction Volume by Hour")
    plt.xlabel("Hour of day (0–23)")
    plt.ylabel("Number of transactions")
    plt.xticks(range(0, 24, 2))
    plt.tight_layout()
    plt.savefig(FIGURES / "transactions_by_hour.png", dpi=150)
    plt.close()

    plt.figure(figsize=(8, 5))
    plt.bar(by_method["payment_method"], by_method["total_amount_inr"])
    plt.title("Total Transaction Value by Payment Method")
    plt.xlabel("Payment method")
    plt.ylabel("Total value (INR)")
    plt.tight_layout()
    plt.savefig(FIGURES / "value_by_payment_method.png", dpi=150)
    plt.close()

    plt.figure(figsize=(9, 5))
    flag_counts = df.groupby(["hour", "is_flagged"]).size().unstack(fill_value=0)
    flag_counts.plot(kind="bar", figsize=(9, 5), ax=plt.gca())
    plt.title("Illustrative Rule-Based Flags by Hour")
    plt.xlabel("Hour of day")
    plt.ylabel("Number of transactions")
    plt.legend(title="Flagged (1=yes)")
    plt.tight_layout()
    plt.savefig(FIGURES / "flags_by_hour.png", dpi=150)
    plt.close()

    # 5) Export tables
    by_status.to_csv(ROOT / "reports" / "summary_by_status.csv", index=False)
    by_hour.to_csv(ROOT / "reports" / "summary_by_hour.csv", index=False)
    by_method.to_csv(ROOT / "reports" / "summary_by_method.csv", index=False)

    # 6) Report with actual computed values
    missing_text = "\n".join(f"- `{col}`: {int(count)}" for col, count in missing_by_column.items())
    report = f"""# UPI / Fintech Transaction Analysis — Findings

## Scope and caveat
This is a **synthetic practice dataset** containing no real customer records. The `is_flagged` field is generated using illustrative rules. A flag means “review this record,” not confirmed fraud.

## Data quality checks
- Rows before cleaning: **{rows_before:,}**
- Duplicate transaction IDs detected: **{duplicate_ids:,}**
- Rows removed for duplicate IDs / missing timestamps or amounts / invalid amounts: **{rows_before-len(df):,}** (categories may overlap)
- Invalid or missing amount values detected before cleaning: **{invalid_amounts:,}**
- Missing values before cleaning:
{missing_text}

## Dataset overview
- Rows after cleaning: **{len(df):,}**
- Successful transactions: **{successful_count:,}**
- Total transaction value: **₹{df['amount_inr'].sum():,.2f}**
- Average transaction amount: **₹{df['amount_inr'].mean():,.2f}**

## Key summaries
### By status
{by_status.to_markdown(index=False, floatfmt=".2f")}

### By payment method
{by_method.to_markdown(index=False, floatfmt=".2f")}

### Illustrative risk flags
- Flagged records: **{flag_count:,}** ({flag_pct:.2f}% of cleaned records)
- Hour with the largest number of flagged records: **{top_flag_hour if top_flag_hour is not None else 'N/A'}**
- Rule logic: amount at least ₹10,000 between 01:00 and 04:59, or amount at least ₹30,000 with a synthetic random condition.

## Interpretation
These results demonstrate data cleaning, feature engineering, aggregation, and visualization. They do **not** estimate real fraud prevalence or model accuracy. Real-world use would require a properly sourced dataset, verified fraud labels, validation, privacy safeguards, and domain review.

## Charts
- `figures/transactions_by_status.png`
- `figures/transactions_by_hour.png`
- `figures/value_by_payment_method.png`
- `figures/flags_by_hour.png`
"""
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(f"Analysis complete. Clean rows: {len(df):,}")
    print(f"Flagged demo records: {flag_count:,} ({flag_pct:.2f}%)")
    print(f"Findings report: {REPORT_PATH}")
    print(f"Charts saved to: {FIGURES}")

if __name__ == "__main__":
    main()
