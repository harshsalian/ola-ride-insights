# Power BI Guide – Ola Ride Insights (≈1.5–2 hours)

## 1. Load data
**Option A (easy, recommended):** Home → Get Data → Text/CSV → `data/ola_cleaned.csv` → *Transform Data* → check types:
`Date` = Date, `Time` = Time, ratings/TAT = Decimal, `Booking_Value`, `Ride_Distance`, `Revenue` = Whole number → Close & Apply.

**Option B (project asks for MySQL):** Get Data → MySQL database → server `localhost`, database `ola_db`, table `ola_rides`
(needs MySQL Connector/NET installed).

Also load `data/vehicle_images.csv` and relate `Vehicle_Type` (Many-to-one, `vehicle_images[Vehicle_Type]` → `ola_cleaned[Vehicle_Type]`).
Select column `Vehicle_Image_URL` → Column tools → Data category = **Image URL**.

## 2. DAX measures (Modeling → New measure)
```DAX
Total Bookings   = COUNTROWS(ola_cleaned)
Successful Rides = CALCULATE([Total Bookings], ola_cleaned[Booking_Status] = "Success")
Success Rate %   = DIVIDE([Successful Rides], [Total Bookings])
Cancelled Rides  = CALCULATE([Total Bookings], ola_cleaned[Booking_Status] IN {"Canceled by Customer","Canceled by Driver"})
Cancellation Rate % = DIVIDE([Cancelled Rides], [Total Bookings])
Total Revenue    = CALCULATE(SUM(ola_cleaned[Booking_Value]), ola_cleaned[Booking_Status] = "Success")
Avg Booking Value = DIVIDE([Total Revenue], [Successful Rides])
Total Distance   = CALCULATE(SUM(ola_cleaned[Ride_Distance]), ola_cleaned[Booking_Status] = "Success")
Avg Distance     = DIVIDE([Total Distance], [Successful Rides])
Avg Driver Rating   = AVERAGE(ola_cleaned[Driver_Ratings])
Avg Customer Rating = AVERAGE(ola_cleaned[Customer_Rating])
```
(Ratings are blank for non-success rides, so AVERAGE ignores them automatically – that's why we did not fill them.)

## 3. Pages & visuals (matches the 5 views in the project doc)
Add slicers on **every page**: Date (between), Vehicle_Type, Booking_Status. Use Sync slicers.

| Page | Visual | Fields |
|------|--------|--------|
| **1. Overall** | KPI cards | Total Bookings, Success Rate %, Cancellation Rate %, Total Revenue |
| | Ride Volume Over Time (Line) | Axis `Date`, Values `Total Bookings` |
| | Booking Status Breakdown (Donut) | Legend `Booking_Status`, Values `Total Bookings` |
| **2. Vehicle Type** | Top 5 Vehicle Types by Ride Distance (Bar) | Axis `Vehicle_Type`, Values `Total Distance`; Filters → Top N = 5 by Total Distance |
| | Table with vehicle icon | `Vehicle_Image_URL`, `Vehicle_Type`, `Avg Distance`, `Total Bookings` |
| **3. Revenue** | Revenue by Payment Method (Donut/Bar) | `Payment_Method` (filter out "Not Applicable"), `Total Revenue` |
| | Top 5 Customers by Booking Value (Bar) | `Customer_ID`, `Total Revenue`; Top N = 5 |
| | Ride Distance Distribution per Day (Column/Line) | Axis `Date`, Values `Total Distance` |
| **4. Cancellation** | Customer cancel reasons (Bar) | `Canceled_Rides_by_Customer` (exclude "Not Applicable"), Count of `Booking_ID` |
| | Driver cancel reasons (Bar) | `Canceled_Rides_by_Driver` (exclude "Not Applicable"), Count of `Booking_ID` |
| **5. Ratings** | Driver Ratings distribution (Column) | Axis `Driver_Ratings` (rounded), Count |
| | Customer Ratings distribution (Column) | Axis `Customer_Rating`, Count |
| | Customer vs Driver Ratings (Clustered bar / Scatter) | `Vehicle_Type`, `Avg Customer Rating`, `Avg Driver Rating` |

Tips: dark/Ola-yellow (#FFD200) + black theme, a title bar on each page, page-navigation buttons (Insert → Buttons → Navigator).

## 4. Publish & embed in Streamlit
1. Home → Publish → My workspace (free work/school Power BI account – steps are in the project doc).
2. Open the report in app.powerbi.com → File → Embed report → **Publish to web (public)** → copy the link.
3. Paste it in `app.py` → `POWER_BI_URL = "https://app.powerbi.com/view?r=..."`.
   (If "Publish to web" is disabled, just add dashboard screenshots + the link in the README.)
