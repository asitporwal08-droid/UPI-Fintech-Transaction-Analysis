# UPI / Fintech Transaction Analysis — Findings

## Scope and caveat
This is a **synthetic practice dataset** containing no real customer records. The `is_flagged` field is generated using illustrative rules. A flag means “review this record,” not confirmed fraud.

## Data quality checks
- Rows before cleaning: **10,000**
- Duplicate transaction IDs detected: **0**
- Rows removed for duplicate IDs / missing timestamps or amounts / invalid amounts: **0** (categories may overlap)
- Invalid or missing amount values detected before cleaning: **0**
- Missing values before cleaning:
- `transaction_id`: 0
- `timestamp`: 0
- `customer_id`: 0
- `amount_inr`: 0
- `payment_method`: 0
- `merchant_category`: 0
- `transaction_status`: 0
- `device_type`: 0
- `city`: 0
- `is_flagged`: 0

## Dataset overview
- Rows after cleaning: **10,000**
- Successful transactions: **9,092**
- Total transaction value: **₹3,356,771.74**
- Average transaction amount: **₹335.68**

## Key summaries
### By status
| transaction_status   |   transaction_count |   total_amount_inr |   average_amount_inr |
|:---------------------|--------------------:|-------------------:|---------------------:|
| SUCCESS              |                9092 |         3047086.37 |               335.14 |
| FAILED               |                 718 |          250885.98 |               349.42 |
| PENDING              |                 190 |           58799.39 |               309.47 |

### By payment method
| payment_method   |   transaction_count |   total_amount_inr |
|:-----------------|--------------------:|-------------------:|
| UPI              |                7126 |         2360222.16 |
| Card             |                1891 |          652688.02 |
| Wallet           |                 983 |          343861.56 |

### Illustrative risk flags
- Flagged records: **0** (0.00% of cleaned records)
- Hour with the largest number of flagged records: **N/A**
- Rule logic: amount at least ₹10,000 between 01:00 and 04:59, or amount at least ₹30,000 with a synthetic random condition.

## Interpretation
These results demonstrate data cleaning, feature engineering, aggregation, and visualization. They do **not** estimate real fraud prevalence or model accuracy. Real-world use would require a properly sourced dataset, verified fraud labels, validation, privacy safeguards, and domain review.

## Charts
- `figures/transactions_by_status.png`
- `figures/transactions_by_hour.png`
- `figures/value_by_payment_method.png`
- `figures/flags_by_hour.png`
