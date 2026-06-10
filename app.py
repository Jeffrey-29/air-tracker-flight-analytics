import os
from dotenv import load_dotenv
import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px

load_dotenv()

# Page config
st.set_page_config(
    page_title="Air Tracker",
    page_icon="✈️",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main { background-color: #0a0a0f; }
    .stApp { background-color: #0a0a0f; }
    
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border: 1px solid #0f3460;
        border-radius: 12px;
        padding: 20px;
    }
    
    [data-testid="stMetricValue"] {
        color: #00d4ff;
        font-size: 2.5rem !important;
        font-weight: 700;
    }
    
    [data-testid="stMetricLabel"] {
        color: #a0aec0;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    h1, h2, h3 {
        color: #ffffff;
    }

    .section-header {
        color: #00d4ff;
        font-size: 1.4rem;
        font-weight: 600;
        border-left: 4px solid #00d4ff;
        padding-left: 12px;
        margin: 30px 0 15px 0;
    }

    .stDataFrame {
        background-color: #1a1a2e;
        border-radius: 10px;
}

/* DataFrame header */
        [data-testid="stDataFrame"] th {
        color: #ffffff !important;
        font-weight: 700 !important;
        opacity: 1 !important;
        text-shadow: none !important;
    }

/* DataFrame cells */
        [data-testid="stDataFrame"] td {
        color: #ffffff !important;
        opacity: 1 !important;
     }

    div[data-testid="stSelectbox"] label,
    div[data-testid="stTextInput"] label {
        color: #a0aec0;
    }

    .stTextInput input, .stSelectbox select {
        background-color: #1a1a2e;
        color: white;
        border: 1px solid #0f3460;
    }

    footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# Database connection
def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

def run_query(query):
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Header
st.markdown("""
<div style='text-align: center; padding: 40px 0 20px 0;'>
    <h1 style='font-size: 3rem; font-weight: 800; color: white;'>
        ✈️ Air <span style='color: #00d4ff;'>Tracker</span>
    </h1>
    <p style='color: #a0aec0; font-size: 1.1rem;'>Real-time Flight Analytics Dashboard</p>
</div>
""", unsafe_allow_html=True)

st.divider()

# Overview metrics
st.markdown('<div class="section-header">📊 Overview</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_airports = run_query("SELECT COUNT(*) as count FROM airport")
    st.metric("Total Airports", total_airports["count"][0])

with col2:
    total_flights = run_query("SELECT COUNT(*) as count FROM flights")
    st.metric("Total Flights", f"{total_flights['count'][0]:,}")

with col3:
    total_delayed = run_query("SELECT COUNT(*) as count FROM flights WHERE status='Delayed'")
    st.metric("Delayed Flights", total_delayed["count"][0])

with col4:
    total_cancelled = run_query("SELECT COUNT(*) as count FROM flights WHERE status='Canceled'")
    st.metric("Cancelled Flights", total_cancelled["count"][0])

st.divider()

# Search and Filter
st.markdown('<div class="section-header">🔍 Search & Filter Flights</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    airline_filter = st.text_input("Search by airline code (e.g. 6E, EK, AI)")
with col2:
    status_filter = st.selectbox("Filter by status",
        ["All", "Arrived", "Departed", "Delayed", "Canceled", "Expected", "Boarding"])

query = "SELECT flight_number, origin_iata, destination_iata, status, airline_code, aircraft_model FROM flights WHERE 1=1"
if airline_filter:
    query += f" AND airline_code = '{airline_filter.upper()}'"
if status_filter != "All":
    query += f" AND status = '{status_filter}'"
query += " LIMIT 50"

flights_df = run_query(query)
st.dataframe(
    flights_df,
    width="stretch",
    hide_index=True
)

st.divider()

# Charts row
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-header">⏱️ Delay Analysis</div>', unsafe_allow_html=True)
    delay_df = run_query("""
        SELECT a.name, ad.total_flights, ad.delayed_flights, ad.canceled_flights
        FROM airport_delays ad
        JOIN airport a ON ad.airport_iata = a.iata_code
        ORDER BY ad.delayed_flights DESC
    """)
    fig = px.bar(
        delay_df,
        x="name",
        y="delayed_flights",
        color="delayed_flights",
        color_continuous_scale="Blues",
        template="plotly_dark"
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        xaxis_tickangle=-45,
        coloraxis_showscale=False
    )
    st.plotly_chart(fig)


with col2:
    st.markdown('<div class="section-header">📈 Flight Status Distribution</div>', unsafe_allow_html=True)
    status_df = run_query("""
        SELECT status, COUNT(*) as count 
        FROM flights 
        WHERE status IS NOT NULL
        GROUP BY status 
        ORDER BY count DESC
    """)
    fig2 = px.pie(
        status_df,
        names="status",
        values="count",
        color_discrete_sequence=px.colors.sequential.Blues_r,
        template="plotly_dark"
    )
    fig2.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig2)

st.divider()

# Airport Details
st.markdown('<div class="section-header">🏢 Airport Details</div>', unsafe_allow_html=True)
airports_df = run_query("SELECT name, city, country, continent, timezone FROM airport ORDER BY name")
st.dataframe(

    airports_df,

    width="stretch",

    hide_index=True

)

st.divider()

# Busiest Routes
st.markdown('<div class="section-header">🏆 Busiest Routes</div>', unsafe_allow_html=True)
routes_df = run_query("""
    SELECT origin_iata, destination_iata, COUNT(*) as flight_count
    FROM flights
    WHERE origin_iata IS NOT NULL AND destination_iata IS NOT NULL
    GROUP BY origin_iata, destination_iata
    ORDER BY flight_count DESC
    LIMIT 10
""")
st.dataframe(

    routes_df,

    width="stretch",

    hide_index=True

)
