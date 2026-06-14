-- ============================================================
-- Air Tracker: Flight Analytics
-- PostgreSQL schema definition
-- Run once before populating data via air_tracker.ipynb
--   psql -d air_tracker -f schema.sql
-- ============================================================

-- Airport master table
CREATE TABLE airport (
    airport_id  SERIAL PRIMARY KEY,
    icao_code   TEXT UNIQUE,
    iata_code   TEXT UNIQUE,
    name        TEXT,
    city        TEXT,
    country     TEXT,
    continent   TEXT,
    latitude    REAL,
    longitude   REAL,
    timezone    TEXT
);

-- Flight records (departures + arrivals)
CREATE TABLE flights (
    flight_id             TEXT PRIMARY KEY,
    flight_number         TEXT,
    aircraft_model        TEXT,
    aircraft_registration TEXT,
    origin_iata           TEXT,
    destination_iata      TEXT,
    scheduled_departure   TEXT,
    actual_departure      TEXT,
    scheduled_arrival     TEXT,
    actual_arrival        TEXT,
    status                TEXT,
    airline_code          TEXT
);

-- If the flights table already exists without this column, run instead:
--   ALTER TABLE flights ADD COLUMN aircraft_registration TEXT;

-- Aircraft fleet details
CREATE TABLE aircraft (
    aircraft_id    SERIAL PRIMARY KEY,
    registration   TEXT UNIQUE,
    model          TEXT,
    manufacturer   TEXT,
    icao_type_code TEXT,
    owner          TEXT
);

-- Airport-level delay statistics (one current snapshot per airport)
CREATE TABLE airport_delays (
    delay_id         SERIAL PRIMARY KEY,
    airport_iata     TEXT UNIQUE,
    delay_date       TEXT,
    total_flights    INTEGER,
    delayed_flights  INTEGER,
    avg_delay_min    INTEGER,
    median_delay_min INTEGER,
    canceled_flights INTEGER
);
