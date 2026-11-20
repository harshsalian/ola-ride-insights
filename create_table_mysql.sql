-- Run in MySQL Workbench, then load data/ola_cleaned.csv via the Table Data Import Wizard
-- (or LOAD DATA LOCAL INFILE ...).
CREATE DATABASE IF NOT EXISTS ola_db;
USE ola_db;

DROP TABLE IF EXISTS ola_rides;
CREATE TABLE ola_rides (
    Date                        DATE,
    Time                        TIME,
    Booking_ID                  VARCHAR(20) PRIMARY KEY,
    Booking_Status              VARCHAR(30),
    Customer_ID                 VARCHAR(20),
    Vehicle_Type                VARCHAR(20),
    Pickup_Location             VARCHAR(60),
    Drop_Location               VARCHAR(60),
    V_TAT                       FLOAT NULL,
    C_TAT                       FLOAT NULL,
    Canceled_Rides_by_Customer  VARCHAR(60),
    Canceled_Rides_by_Driver    VARCHAR(60),
    Incomplete_Rides            VARCHAR(20),
    Incomplete_Rides_Reason     VARCHAR(40),
    Booking_Value               INT,
    Payment_Method              VARCHAR(20),
    Ride_Distance               INT,
    Driver_Ratings              FLOAT NULL,
    Customer_Rating             FLOAT NULL,
    Year                        INT,
    Month                       VARCHAR(12),
    Day                         INT,
    Day_Name                    VARCHAR(12),
    Week_Of_Month               INT,
    Is_Weekend                  TINYINT,
    Hour                        INT,
    Time_Of_Day                 VARCHAR(12),
    Is_Success                  TINYINT,
    Revenue                     INT,
    Same_Pickup_Drop            TINYINT,
    Distance_Bucket             VARCHAR(20)
);

CREATE INDEX idx_status  ON ola_rides (Booking_Status);
CREATE INDEX idx_vehicle ON ola_rides (Vehicle_Type);
CREATE INDEX idx_cust    ON ola_rides (Customer_ID);
CREATE INDEX idx_pay     ON ola_rides (Payment_Method);

-- Easiest load method (CSV has a header row; empty cells = NULL):
-- LOAD DATA LOCAL INFILE 'C:/path/ola_cleaned.csv' INTO TABLE ola_rides
-- FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' LINES TERMINATED BY '\n' IGNORE 1 ROWS;
