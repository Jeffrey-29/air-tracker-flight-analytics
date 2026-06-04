import os
from dotenv import load_dotenv
import streamlit as st
import psycopg2
import pandas as pd

load_dotenv()

# Database connection
def get_connection():
    return psycopg2.connect(
        host="localhost",
        port="5432",
        database="air_tracker",
        user="postgres",
        password=os.getenv("DB_PASSWORD") 
    )

# Run any SQL query and return a dataframe
def run_query(query):
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# App title
st.title("✈️ Air Tracker: Flight Analytics Dashboard")
st.markdown("Real-time aviation data from 15 major airports worldwide")

# Homepage stats
st.header("📊 Overview")
col1, col2, col3 = st.columns(3)

with col1:
    total_airports = run_query("SELECT COUNT(*) as count FROM airport")
    st.metric("Total Airports", total_airports["count"][0])

with col2:
    total_flights = run_query("SELECT COUNT(*) as count FROM flights")
    st.metric("Total Flights", total_flights["count"][0])

with col3:
    total_delayed = run_query("SELECT COUNT(*) as count FROM flights WHERE status='Delayed'")
    st.metric("Delayed Flights", total_delayed["count"][0])

# Search and Filter Flights
st.header("🔍 Search & Filter Flights")

col1, col2 = st.columns(2)
with col1:
    airline_filter = st.text_input("Search by airline code (e.g. 6E, EK, AI)")
with col2:
    status_filter = st.selectbox("Filter by status", 
        ["All", "Arrived", "Departed", "Delayed", "Canceled", "Expected"])

query = "SELECT flight_number, origin_iata, destination_iata, status, airline_code, aircraft_model FROM flights WHERE 1=1"

if airline_filter:
    query += f" AND airline_code = '{airline_filter.upper()}'"
if status_filter != "All":
    query += f" AND status = '{status_filter}'"

query += " LIMIT 50"
flights_df = run_query(query)
st.dataframe(flights_df)

# Airport Details
st.header("🏢 Airport Details")
airports_df = run_query("SELECT name, city, country, continent, timezone FROM airport")
st.dataframe(airports_df)

# Delay Analysis
st.header("⏱️ Delay Analysis by Airport")
delay_df = run_query("""
    SELECT a.name, ad.total_flights, ad.delayed_flights, ad.canceled_flights
    FROM airport_delays ad
    JOIN airport a ON ad.airport_iata = a.iata_code
    ORDER BY ad.delayed_flights DESC
""")
st.bar_chart(delay_df.set_index("name")["delayed_flights"])
st.dataframe(delay_df)

# Route Leaderboard
st.header("🏆 Busiest Routes")
routes_df = run_query("""
    SELECT origin_iata, destination_iata, COUNT(*) as flight_count
    FROM flights
    WHERE origin_iata IS NOT NULL AND destination_iata IS NOT NULL
    GROUP BY origin_iata, destination_iata
    ORDER BY flight_count DESC
    LIMIT 10
""")
st.dataframe(routes_df)