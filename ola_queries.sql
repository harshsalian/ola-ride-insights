-- =====================================================================
-- OLA RIDE INSIGHTS : SQL QUERIES   (MySQL 8 compatible; also runs on SQLite)
-- Table: ola_rides  (loaded from data/ola_cleaned.csv)
-- Note: Ride_Distance = 0 for every non-success booking, so distance
--       averages are computed on Success rides only.
-- =====================================================================

-- Q1. Retrieve all successful bookings
SELECT * FROM ola_rides WHERE Booking_Status = 'Success';

-- Q2. Average ride distance for each vehicle type
SELECT Vehicle_Type, ROUND(AVG(Ride_Distance), 2) AS Avg_Ride_Distance
FROM ola_rides
WHERE Booking_Status = 'Success'
GROUP BY Vehicle_Type
ORDER BY Avg_Ride_Distance DESC;

-- Q3. Total number of cancelled rides by customers
SELECT COUNT(*) AS Cancelled_By_Customers
FROM ola_rides
WHERE Booking_Status = 'Canceled by Customer';

-- Q4. Top 5 customers with the highest number of rides
SELECT Customer_ID, COUNT(Booking_ID) AS Total_Rides
FROM ola_rides
GROUP BY Customer_ID
ORDER BY Total_Rides DESC, Customer_ID
LIMIT 5;

-- Q5. Rides cancelled by drivers due to personal & car related issues
SELECT COUNT(*) AS Driver_Cancel_Personal_Car_Issue
FROM ola_rides
WHERE Canceled_Rides_by_Driver = 'Personal & Car related issue';

-- Q6. Maximum and minimum driver ratings for Prime Sedan bookings
SELECT MAX(Driver_Ratings) AS Max_Driver_Rating,
       MIN(Driver_Ratings) AS Min_Driver_Rating
FROM ola_rides
WHERE Vehicle_Type = 'Prime Sedan';

-- Q7. All rides where payment was made using UPI
SELECT * FROM ola_rides WHERE Payment_Method = 'UPI';

-- Q8. Average customer rating per vehicle type
SELECT Vehicle_Type, ROUND(AVG(Customer_Rating), 2) AS Avg_Customer_Rating
FROM ola_rides
GROUP BY Vehicle_Type
ORDER BY Avg_Customer_Rating DESC;

-- Q9. Total booking value of rides completed successfully
SELECT SUM(Booking_Value) AS Total_Successful_Booking_Value
FROM ola_rides
WHERE Booking_Status = 'Success';

-- Q10. All incomplete rides along with the reason
SELECT Booking_ID, Date, Vehicle_Type, Customer_ID, Incomplete_Rides_Reason
FROM ola_rides
WHERE Incomplete_Rides = 'Yes';
