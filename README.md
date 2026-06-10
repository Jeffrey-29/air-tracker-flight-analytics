# ✈️ Air Tracker: Flight Analytics

A flight analytics dashboard built using Python, PostgreSQL, AeroDataBox API, and Streamlit.

## Project Overview

The goal of this project is to collect flight and airport data from the AeroDataBox API, store it in a PostgreSQL database, and analyze the data using SQL queries and interactive visualizations.

The dashboard allows users to explore airport information, search flights, analyze delays, and view route statistics through a simple web interface.

## Technologies Used

- Python
- PostgreSQL
- Streamlit
- Pandas
- Plotly
- Psycopg2
- AeroDataBox API
- Python Dotenv

## Database Tables

### Airport

Stores airport information such as:

- Airport name
- IATA code
- ICAO code
- City
- Country
- Timezone
- Coordinates

### Aircraft

Stores aircraft details such as:

- Registration number
- Model
- Manufacturer
- Owner

### Flights

Stores flight information including:

- Flight number
- Origin airport
- Destination airport
- Departure and arrival times
- Airline code
- Flight status

### Airport Delays

Stores delay statistics for airports such as:

- Total flights
- Delayed flights
- Average delay
- Median delay
- Cancelled flights

## Features

### Dashboard Overview

Displays:

- Total Airports
- Total Flights
- Delayed Flights
- Cancelled Flights

### Flight Search and Filtering

Users can:

- Search flights by airline code
- Filter flights by status
- View flight details in a table

### Delay Analysis

Visualizes:

- Delayed flights by airport
- Flight status distribution

### Airport Details

Displays airport information including:

- Name
- City
- Country
- Continent
- Timezone

### Route Analysis

Shows the busiest flight routes based on flight count.

## SQL Analysis

The following SQL queries were implemented:

1. Total flights for each aircraft model
2. Aircraft assigned to more than 5 flights
3. Airports with more than 5 outbound flights
4. Top 3 destination airports by arrivals
5. Domestic and International flight classification
6. Most recent arrivals at DEL airport
7. Airports with no arriving flights
8. Flight status count by airline
9. Cancelled flights analysis
10. City pairs operated by multiple aircraft models
11. Delay percentage by destination airport

## Dashboard Screenshots

### Dashboard Overview
![Dashboard Overview](screenshots/dashboard_overview.png)

### Flight Search & Filter
![Flight Search](screenshots/flight_search.png)

### Delay Analysis
![Delay Analysis](screenshots/delay_analysis.png)

### Airport Details
![Airport Details](screenshots/airport_details.png)

### Busiest Routes
![Busiest Routes](screenshots/busiest_routes.png)

## Installation

Clone the repository:

git clone https://github.com/Jeffrey-29/air-tracker-flight-analytics.git 
cd air-tracker-flight-analytics 

Install dependencies:

pip3 install -r requirements.txt 

Create a .env file and add your database credentials and API key.

Example:

DB_HOST=localhost
DB_PORT=5432
DB_NAME=air_tracker
DB_USER=postgres
DB_PASSWORD=your_password

API_KEY=your_api_key

Run the Streamlit application:

streamlit run app.py 

## Project Structure

air-tracker-flight-analytics/
│
├── app.py
├── air_tracker.ipynb
├── queries.sql
├── requirements.txt
├── README.md
└── screenshots/

## Author

Jeffrey Gabriel
