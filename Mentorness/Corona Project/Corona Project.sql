--Write a code to check NULL values
SELECT COUNT(*) AS null_count
FROM MyData.dbo.[Corona Virus Dataset]
WHERE Province IS NULL or
Country_Region IS NULL or
Latitude IS NULL or
Longitude IS NULL or
Date IS NULL or
Confirmed IS NULL or
Deaths IS NULL or
Recovered IS NULL;


--If NULL values are present, update them with zeros for all columns.
UPDATE MyData.dbo.[Corona Virus Dataset]
SET Province = COALESCE(Province, ''),
    Country_Region = COALESCE(Country_Region, ''),
    Latitude = COALESCE(Latitude, 0.0),
	Longitude = COALESCE(Longitude, 0.0),
	Date = COALESCE(Date, '2020-01-02'),
	Confirmed = COALESCE(Confirmed, 0),
	Deaths = COALESCE(Deaths, 0),
	Recovered = COALESCE(Recovered, 0);


--check total number of rows
SELECT COUNT(*) AS total_rows
FROM MyData.dbo.[Corona Virus Dataset];


--Check what is start_date and end_date
SELECT MIN(date) AS start_date,
       MAX(date) AS end_date
FROM MyData.dbo.[Corona Virus Dataset];


--Number of month present in dataset
SELECT DATEPART(month, date) AS month,
       COUNT(*) AS month_count
FROM MyData.dbo.[Corona Virus Dataset]
GROUP BY DATEPART(month, date)
ORDER BY month;


--Find monthly average for confirmed, deaths, recovered
SELECT DATEPART(month, date) AS month,
       AVG(confirmed) AS avg_confirmed,
       AVG(deaths) AS avg_deaths,
       AVG(recovered) AS avg_recovered
FROM MyData.dbo.[Corona Virus Dataset]
GROUP BY DATEPART(month, date)
ORDER BY month;


--Find most frequent value for confirmed, deaths, recovered each month 
SELECT 
    month,
    MAX(CASE WHEN confirmed_mode_count = max_confirmed_mode_count THEN confirmed_mode_value END) AS confirmed_mode,
    MAX(CASE WHEN deaths_mode_count = max_deaths_mode_count THEN deaths_mode_value END) AS deaths_mode,
    MAX(CASE WHEN recovered_mode_count = max_recovered_mode_count THEN recovered_mode_value END) AS recovered_mode
FROM (
    SELECT 
        DATEPART(month, date) AS month,
        confirmed AS confirmed_mode_value,
        COUNT(*) AS confirmed_mode_count,
        deaths AS deaths_mode_value,
        COUNT(*) AS deaths_mode_count,
        recovered AS recovered_mode_value,
        COUNT(*) AS recovered_mode_count,
        MAX(COUNT(*)) OVER(PARTITION BY DATEPART(month, date)) AS max_confirmed_mode_count,
        MAX(COUNT(*)) OVER(PARTITION BY DATEPART(month, date)) AS max_deaths_mode_count,
        MAX(COUNT(*)) OVER(PARTITION BY DATEPART(month, date)) AS max_recovered_mode_count
    FROM MyData.dbo.[Corona Virus Dataset]
    GROUP BY DATEPART(month, date), confirmed, deaths, recovered
) AS sub
GROUP BY month;


--Find minimum values for confirmed, deaths, recovered per year.
SELECT YEAR(date) AS year,
       MIN(confirmed) AS min_confirmed,
       MIN(deaths) AS min_deaths,
       MIN(recovered) AS min_recovered
FROM MyData.dbo.[Corona Virus Dataset]
GROUP BY YEAR(date);


--Find maximum values of confirmed, deaths, recovered per year.
SELECT YEAR(date) AS year,
       MAX(confirmed) AS max_confirmed,
       MAX(deaths) AS max_deaths,
       MAX(recovered) AS max_recovered
FROM MyData.dbo.[Corona Virus Dataset]
GROUP BY YEAR(date);


--The total number of case of confirmed, deaths, recovered each month.
SELECT DATEPART(month, date) AS month,
       SUM(confirmed) AS total_confirmed,
       SUM(deaths) AS total_deaths,
       SUM(recovered) AS total_recovered
FROM MyData.dbo.[Corona Virus Dataset]
GROUP BY DATEPART(month, date)
ORDER BY DATEPART(month, date);


--Check how corona virus spread out with respect to confirmed case
--      (Eg.: total confirmed cases, their average, variance & STDEV )
SELECT SUM(confirmed) AS total_confirmed,
       AVG(confirmed) AS avg_confirmed,
       VAR(confirmed) AS variance_confirmed,
       STDEV(confirmed) AS stdev_confirmed
FROM MyData.dbo.[Corona Virus Dataset];


--Check how corona virus spread out with respect to death case per month
--      (Eg.: total confirmed cases, their average, variance & STDEV )
SELECT DATEPART(month, date) AS month,
       SUM(deaths) AS total_deaths,
       AVG(deaths) AS avg_deaths,
       VAR(deaths) AS variance_deaths,
       STDEV(deaths) AS stdev_deaths
FROM MyData.dbo.[Corona Virus Dataset]
GROUP BY DATEPART(month, date)
ORDER BY month;


--Check how corona virus spread out with respect to recovered case
--      (Eg.: total confirmed cases, their average, variance & STDEV )
SELECT SUM(recovered) AS total_recovered,
       AVG(recovered) AS avg_recovered,
       VAR(recovered) AS variance_recovered,
       STDEV(recovered) AS stdev_recovered
FROM MyData.dbo.[Corona Virus Dataset];


--Find Country having highest number of the Confirmed case
SELECT top 1 Country_Region,
       sum(confirmed) AS sum_confirmed
FROM MyData.dbo.[Corona Virus Dataset]
GROUP BY Country_Region
ORDER BY sum_confirmed DESC


--Find Country having lowest number of the death case
SELECT top 4 Country_Region,
       sum(deaths) AS sum_deaths
FROM MyData.dbo.[Corona Virus Dataset]
GROUP BY Country_Region
ORDER BY sum_deaths ASC;

--Find top 5 countries having highest recovered case
SELECT TOP 5 Country_Region,
       MAX(recovered) AS max_recovered
FROM MyData.dbo.[Corona Virus Dataset]
GROUP BY Country_Region
ORDER BY max_recovered DESC;