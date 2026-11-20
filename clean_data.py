"""
Ola Ride Insights - Data Cleaning & Preprocessing
Input : OLA_DataSet.xlsx (sheet 'July')
Output: ola_cleaned.csv, vehicle_images.csv, ola.db (SQLite, used by Streamlit)
"""
import os
import sqlite3
import numpy as np
import pandas as pd

RAW = "OLA_DataSet.xlsx"

# ---------- 1. Load ----------
df = pd.read_excel(RAW, sheet_name="July")
icons = pd.read_excel(RAW, sheet_name="Sheet2", header=None, names=["Vehicle_Type", "Vehicle_Image_URL"])
print("Raw shape:", df.shape)

# ---------- 2. Standardise column names ----------
df.columns = [c.strip().replace(" ", "_") for c in df.columns]

# ---------- 3. Remove duplicates / trim text ----------
df = df.drop_duplicates(subset="Booking_ID")
df["Time"] = df["Time"].astype(str)                       # Excel gives datetime.time objects
for c in df.columns:
    if pd.api.types.is_string_dtype(df[c]) or df[c].dtype == object:
        df[c] = df[c].astype("string").str.strip().astype(object)

# ---------- 4. Data types ----------
df["Date"] = pd.to_datetime(df["Date"])
df["Time"] = df["Date"].dt.strftime("%H:%M:%S")          # Time col was a duplicate of Date's time part
df["Date"] = df["Date"].dt.normalize()                   # keep only the date in 'Date'

# ---------- 5. Missing values ----------
# NULLs are STRUCTURAL (e.g. ratings/payment exist only for Success rides), so we do NOT impute numbers.
cat_cols = ["Canceled_Rides_by_Customer", "Canceled_Rides_by_Driver",
            "Incomplete_Rides", "Incomplete_Rides_Reason", "Payment_Method"]
df[cat_cols] = df[cat_cols].fillna("Not Applicable")
# V_TAT, C_TAT, Driver_Ratings, Customer_Rating stay NULL for non-success rides (correct for averages)

# ---------- 6. Feature engineering ----------
df["Year"] = df["Date"].dt.year
df["Month"] = df["Date"].dt.month_name()
df["Day"] = df["Date"].dt.day
df["Day_Name"] = df["Date"].dt.day_name()
df["Week_Of_Month"] = (df["Date"].dt.day - 1) // 7 + 1
df["Is_Weekend"] = df["Date"].dt.dayofweek.isin([5, 6]).astype(int)
df["Hour"] = df["Time"].str[:2].astype(int)
df["Time_Of_Day"] = pd.cut(df["Hour"], bins=[-1, 5, 11, 16, 20, 23],
                           labels=["Night", "Morning", "Afternoon", "Evening", "Late Night"]).astype(str)
df["Is_Success"] = (df["Booking_Status"] == "Success").astype(int)
df["Revenue"] = np.where(df["Is_Success"] == 1, df["Booking_Value"], 0)   # money only counts when ride succeeds
df["Same_Pickup_Drop"] = (df["Pickup_Location"] == df["Drop_Location"]).astype(int)  # anomaly flag
df["Distance_Bucket"] = pd.cut(df["Ride_Distance"], bins=[-1, 0, 10, 25, 50],
                               labels=["No Ride (0)", "Short (1-10)", "Medium (11-25)", "Long (26-50)"]).astype(str)

# Vehicle image URL moved to a lookup table (was repeated on 100k+ rows)
df = df.drop(columns=["Vehicle_Images"])

# ---------- 7. Validation ----------
assert df["Booking_ID"].is_unique
assert (df.loc[df.Is_Success == 0, "Ride_Distance"] == 0).all()
assert df.loc[df.Is_Success == 1, "Driver_Ratings"].notna().all()
print("Clean shape:", df.shape)
print(df["Booking_Status"].value_counts())

# ---------- 8. Save ----------
df.to_csv("ola_cleaned.csv", index=False)
icons.to_csv("vehicle_images.csv", index=False)
with sqlite3.connect("ola.db") as con:
    out = df.copy()
    out["Date"] = out["Date"].dt.strftime("%Y-%m-%d")
    out.to_sql("ola_rides", con, if_exists="replace", index=False)
    icons.to_sql("vehicle_images", con, if_exists="replace", index=False)
print("Saved: ola_cleaned.csv, vehicle_images.csv, ola.db")
