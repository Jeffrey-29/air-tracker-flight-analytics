✈️ Air Tracker: Flight Analytics Dashboard
A comprehensive flight analytics dashboard built using Python, PostgreSQL, and Streamlit, powered by the AeroDataBox API.
📌 Project Overview
Air Tracker fetches real-time aviation data from 15 major airports worldwide and provides interactive visualizations and insights into flight operations, delays, and routes.
🛠️ Tech Stack

Language: Python
Database: PostgreSQL
Dashboard: Streamlit
API: AeroDataBox (via RapidAPI)
Libraries: psycopg2, pandas, plotly, python-dotenv

🗄️ Database Schema
4 tables:

airport — 15 airports (8 international, 7 domestic)
flights — 6000+ flights fetched from the past day
aircraft — 100 aircraft from top 10 airlines
airport_delays — delay statistics for 12 airports

🌍 Airports Covered
International: DXB, SIN, LHR, JFK, SYD, DOH, BKK, CDG
Domestic: MAA, DEL, BOM, BLR, HYD, CCU, COK
📊 Dashboard Features

Overview stats (total airports, flights, delays, cancellations)
Search and filter flights by airline or status
Delay analysis bar chart by airport
Flight status distribution pie chart
Airport details table
Busiest routes leaderboard

⚙️ How to Run

Clone the repository
Create a .env file with your credentials:

API_KEY=your_rapidapi_key
DB_PASSWORD=your_postgres_password

Install dependencies:

pip install streamlit psycopg2-binary pandas plotly python-dotenv requests

Run the Streamlit app:

streamlit run app.py
📁 Project Structure
air-tracker/
├── air_tracker.ipynb   # Data collection and insertion
├── app.py              # Streamlit dashboard
├── queries.sql         # All 11 SQL queries
├── .gitignore          # Excludes .env file
└── README.md
🔒 Security
API keys and database credentials are stored in a .env file and excluded from version control via .gitignore.
