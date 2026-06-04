-- Query 1: Total flights per aircraft model
SELECT aircraft_model, COUNT(*) as total_flights
FROM flights
WHERE aircraft_model IS NOT NULL
GROUP BY aircraft_model
ORDER BY total_flights DESC;

-- Query 2: Aircraft with more than 5 flights
SELECT aircraft_model, COUNT(*) as flight_count
FROM flights
WHERE aircraft_model IS NOT NULL
GROUP BY aircraft_model
HAVING COUNT(*) > 5
ORDER BY flight_count DESC;

-- Query 3: Airports with more than 5 outbound flights
SELECT a.name, COUNT(*) as outbound_flights
FROM flights f
JOIN airport a ON f.origin_iata = a.iata_code
GROUP BY a.name
HAVING COUNT(*) > 5
ORDER BY outbound_flights DESC;

-- Query 4: Top 3 destination airports by arriving flights
SELECT a.name, a.city, COUNT(*) as arriving_flights
FROM flights f
JOIN airport a ON f.destination_iata = a.iata_code
GROUP BY a.name, a.city
ORDER BY arriving_flights DESC
LIMIT 3;

-- Query 5: Domestic vs International flights
SELECT 
    f.flight_number,
    f.origin_iata,
    f.destination_iata,
    CASE 
        WHEN a1.country = a2.country THEN 'Domestic'
        ELSE 'International'
    END as flight_type
FROM flights f
LEFT JOIN airport a1 ON f.origin_iata = a1.iata_code
LEFT JOIN airport a2 ON f.destination_iata = a2.iata_code
ORDER BY flight_type;

-- Query 6: 5 most recent arrivals at DEL
SELECT 
    f.flight_number,
    f.aircraft_model,
    a.name as departure_airport,
    f.scheduled_arrival
FROM flights f
JOIN airport a ON f.origin_iata = a.iata_code
WHERE f.destination_iata = 'DEL'
AND f.scheduled_arrival IS NOT NULL
ORDER BY f.scheduled_arrival DESC
LIMIT 5;

-- Query 7: Airports with no arriving flights
SELECT a.name, a.iata_code
FROM airport a
WHERE a.iata_code NOT IN (
    SELECT DISTINCT destination_iata 
    FROM flights 
    WHERE destination_iata IS NOT NULL
);

-- Query 8: Flight count by status per airline
SELECT 
    airline_code,
    COUNT(CASE WHEN status = 'Arrived' THEN 1 END) as arrived,
    COUNT(CASE WHEN status = 'Departed' THEN 1 END) as departed,
    COUNT(CASE WHEN status = 'Canceled' THEN 1 END) as cancelled,
    COUNT(CASE WHEN status = 'Delayed' THEN 1 END) as delayed,
    COUNT(CASE WHEN status NOT IN ('Arrived','Departed','Canceled','Delayed') THEN 1 END) as other
FROM flights
WHERE airline_code IS NOT NULL
GROUP BY airline_code
ORDER BY airline_code;

-- Query 9: All cancelled flights
SELECT 
    f.flight_number,
    f.aircraft_model,
    a1.name as origin_airport,
    a2.name as destination_airport,
    f.scheduled_departure
FROM flights f
LEFT JOIN airport a1 ON f.origin_iata = a1.iata_code
LEFT JOIN airport a2 ON f.destination_iata = a2.iata_code
WHERE f.status = 'Canceled'
ORDER BY f.scheduled_departure DESC;

-- Query 10: City pairs with more than 2 aircraft models
SELECT 
    f.origin_iata,
    f.destination_iata,
    COUNT(DISTINCT f.aircraft_model) as different_models
FROM flights f
WHERE f.aircraft_model IS NOT NULL
GROUP BY f.origin_iata, f.destination_iata
HAVING COUNT(DISTINCT f.aircraft_model) > 2
ORDER BY different_models DESC;

-- Query 11: Delay percentage per destination airport
SELECT 
    a.name as destination_airport,
    COUNT(*) as total_arrivals,
    COUNT(CASE WHEN f.status = 'Delayed' THEN 1 END) as delayed_flights,
    ROUND(COUNT(CASE WHEN f.status = 'Delayed' THEN 1 END) * 100.0 / COUNT(*), 2) as delay_percentage
FROM flights f
JOIN airport a ON f.destination_iata = a.iata_code
GROUP BY a.name
HAVING COUNT(*) > 0
ORDER BY delay_percentage DESC;