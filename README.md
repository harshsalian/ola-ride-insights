# 🚖 Ola Ride Insights

SQL + Python + Power BI + Streamlit analytics on Ola ride-booking data (July 2024, 103,024 bookings).

## Project files
```
app.py                  # Streamlit app
requirements.txt
ola.db                  # SQLite copy of the cleaned data (used by Streamlit)
ola_cleaned.csv         # cleaned data (Power BI / MySQL)
ola_queries.sql         # the 10 SQL questions
create_table_mysql.sql  # MySQL schema
clean_data.py           # EDA-driven cleaning & feature engineering
POWERBI_GUIDE.md        # dashboard build steps + DAX
```

## How to run
```bash
pip install -r requirements.txt
python clean_data.py        # only if you want to regenerate data (needs OLA_DataSet.xlsx next to it; also: pip install openpyxl)
streamlit run app.py
```

## Data cleaning (summary)
| Issue | Treatment |
|-------|-----------|
| `Date` held date+time and `Time` duplicated it | `Date` = date only, `Time` kept as HH:MM:SS |
| Column `Vehicle Images` (space, same URL repeated 100k times) | Removed; moved to `vehicle_images.csv` lookup |
| 39,057 NULLs in ratings, TAT, payment, incomplete flag | **Structural, not missing** – these exist only for successful rides. Numeric columns left NULL (so averages stay correct); text columns set to `Not Applicable` |
| Cancel / incomplete reason columns mostly NULL | `Not Applicable` when the event did not happen |
| `Ride_Distance = 0` for all non-success bookings | Kept; all distance metrics use Success rides only |
| Duplicates / whitespace | Booking_ID unique (0 duplicates); text trimmed |

**Derived features:** Day, Day_Name, Week_Of_Month, Is_Weekend, Hour, Time_Of_Day, Is_Success, Revenue, Same_Pickup_Drop (anomaly flag), Distance_Bucket.

## SQL answers (verified)
| # | Question | Result |
|---|----------|--------|
| 1 | Successful bookings | 63,967 rows |
| 2 | Avg distance / vehicle (Success) | eBike 25.15, Prime Plus 25.03, Prime Sedan 25.01, Mini 24.98, Bike 24.93, Prime SUV 24.88, **Auto 10.04** |
| 3 | Cancelled by customers | **10,499** |
| 4 | Top customer by rides | CID954071 (5 rides); then 4-ride customers CID189965, CID199017, CID201733, CID263459 |
| 5 | Driver cancels: personal & car issue | **6,542** |
| 6 | Prime Sedan driver rating max / min | **5.0 / 3.0** |
| 7 | UPI rides | 25,881 rows |
| 8 | Avg customer rating / vehicle | all ≈ 4.0 (3.99 – 4.01) |
| 9 | Total booking value (Success) | **₹3,50,80,467** |
| 10 | Incomplete rides + reason | 3,926 rows |

## Key insights
- **Only 62.1% of bookings succeed**; 37.9% fail – driver cancellations (18,434) are the biggest leak, followed by customer cancellations (10,499) and "driver not found" (10,124).
- **Top driver cancel reason:** Personal & car-related issue (6,542). **Top customer cancel reason:** driver not moving towards pickup (3,175) – a driver-side service problem, not customer behaviour.
- **Cash is still the leading payment mode** (₹1.93 cr), then UPI (₹1.42 cr); cards are under 5% of revenue → opportunity for card/UPI incentives.
- **Peak demand hours:** 8 AM, 12 PM and 3 PM; weekdays (Mon–Tue) are busiest → allocate drivers accordingly.
- **Autos run much shorter trips** (avg 10 km vs ~25 km for every other vehicle) → ideal for short-hop / last-mile positioning.
- All 7 vehicle types have very similar success rates (61–63%) and ratings (~4.0), so cancellations are a platform-wide issue rather than a single vehicle category.
- **Anomaly check:** 2,121 bookings have identical pickup and drop location (1,306 of them "successful") → candidates for fraud / data-quality review.
- Incomplete rides: 3,926 – reasons are Customer Demand (1,601), Vehicle Breakdown (1,591), Other (734).

## Power BI
See `POWERBI_GUIDE.md`. Dashboard link / screenshots: _add here_

## Tech stack
Python, Pandas, NumPy, SQL (MySQL), Power BI, Streamlit, Plotly
