import os
from datetime import date
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
        font-size: 2.2rem !important;
        font-weight: 700;
    }

    [data-testid="stMetricLabel"] {
        color: #a0aec0;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    h1, h2, h3 { color: #ffffff; }

    .section-header {
        color: #00d4ff;
        font-size: 1.4rem;
        font-weight: 600;
        border-left: 4px solid #00d4ff;
        padding-left: 12px;
        margin: 30px 0 15px 0;
    }

    .stDataFrame { background-color: #1a1a2e; border-radius: 10px; }

    [data-testid="stDataFrame"] th {
        color: #ffffff !important;
        font-weight: 700 !important;
        opacity: 1 !important;
        text-shadow: none !important;
    }
    [data-testid="stDataFrame"] td { color: #ffffff !important; opacity: 1 !important; }

    div[data-testid="stSelectbox"] label,
    div[data-testid="stTextInput"] label,
    div[data-testid="stDateInput"] label { color: #a0aec0; }

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


@st.cache_data(ttl=300)
def run_query(query, params=None):
    """Run a parameterised query and return a DataFrame (cached 5 min)."""
    conn = get_connection()
    try:
        df = pd.read_sql(query, conn, params=params)
    finally:
        conn.close()
    return df


def header(text):
    st.markdown(f'<div class="section-header">{text}</div>', unsafe_allow_html=True)


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

# ---------------------------------------------------------------------------
# 1. HOMEPAGE DASHBOARD — summary statistics
# ---------------------------------------------------------------------------
header("📊 Overview")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    total_airports = run_query("SELECT COUNT(*) AS count FROM airport")
    st.metric("Total Airports", int(total_airports["count"][0]))

with col2:
    total_flights = run_query("SELECT COUNT(*) AS count FROM flights")
    st.metric("Total Flights", f"{int(total_flights['count'][0]):,}")

with col3:
    total_aircraft = run_query("SELECT COUNT(*) AS count FROM aircraft")
    st.metric("Aircraft Tracked", int(total_aircraft["count"][0]))

with col4:
    total_delayed = run_query("SELECT COUNT(*) AS count FROM flights WHERE status='Delayed'")
    st.metric("Delayed Flights", int(total_delayed["count"][0]))

with col5:
    avg_delay = run_query("""
        SELECT ROUND(
            COUNT(CASE WHEN status = 'Delayed' THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0), 1
        ) AS rate
        FROM flights
    """)
    rate = avg_delay["rate"][0]
    st.metric("Avg Delay Rate", f"{rate}%" if rate is not None else "N/A")

st.divider()

# ---------------------------------------------------------------------------
# 2. SEARCH AND FILTER FLIGHTS
# ---------------------------------------------------------------------------
header("🔍 Search & Filter Flights")

origin_options = run_query("""
    SELECT DISTINCT origin_iata FROM flights
    WHERE origin_iata IS NOT NULL ORDER BY origin_iata
""")["origin_iata"].tolist()

c1, c2, c3 = st.columns(3)
with c1:
    flight_no = st.text_input("Search by flight number (e.g. 6E 123)")
with c2:
    airline_filter = st.text_input("Search by airline code (e.g. 6E, EK, AI)")
with c3:
    status_filter = st.selectbox(
        "Filter by status",
        ["All", "Arrived", "Departed", "Delayed", "Canceled", "Expected", "Boarding"]
    )

c4, c5 = st.columns(2)
with c4:
    origin_filter = st.selectbox("Filter by origin airport", ["All"] + origin_options)
with c5:
    use_dates = st.checkbox("Filter by departure date range")
    date_range = None
    if use_dates:
        date_range = st.date_input(
            "Departure date range",
            value=(date(2024, 1, 1), date.today()),
        )

# Build a parameterised query — no string interpolation of user input.
query = """
    SELECT flight_number, origin_iata, destination_iata, status,
           airline_code, aircraft_model, aircraft_registration, scheduled_departure
    FROM flights
    WHERE 1=1
"""
params = []
if flight_no:
    query += " AND flight_number ILIKE %s"
    params.append(f"%{flight_no}%")
if airline_filter:
    query += " AND airline_code = %s"
    params.append(airline_filter.upper())
if status_filter != "All":
    query += " AND status = %s"
    params.append(status_filter)
if origin_filter != "All":
    query += " AND origin_iata = %s"
    params.append(origin_filter)
if use_dates and date_range and len(date_range) == 2:
    query += " AND scheduled_departure >= %s AND scheduled_departure <= %s"
    params.append(str(date_range[0]))
    params.append(f"{date_range[1]} 23:59")
query += " ORDER BY scheduled_departure DESC NULLS LAST LIMIT 100"

flights_df = run_query(query, params=tuple(params) if params else None)
st.caption(f"Showing {len(flights_df)} flight(s) (max 100).")
st.dataframe(flights_df.fillna(""), use_container_width=True, hide_index=True)

st.divider()

# ---------------------------------------------------------------------------
# 3. AIRPORT DETAILS VIEWER — pick one airport, see details + linked flights
# ---------------------------------------------------------------------------
header("🏢 Airport Details Viewer")

airport_names = run_query("SELECT name FROM airport ORDER BY name")["name"].tolist()
if airport_names:
    selected = st.selectbox("Select an airport", airport_names)
    info = run_query(
        "SELECT * FROM airport WHERE name = %s", params=(selected,)
    ).iloc[0]

    d1, d2, d3, d4 = st.columns(4)
    d1.metric("City", info["city"] or "—")
    d2.metric("Country", info["country"] or "—")
    d3.metric("IATA / ICAO", f"{info['iata_code']} / {info['icao_code']}")
    d4.metric("Timezone", info["timezone"] or "—")

    linked = run_query("""
        SELECT flight_number, origin_iata, destination_iata, status,
               airline_code, scheduled_departure
        FROM flights
        WHERE origin_iata = %s OR destination_iata = %s
        ORDER BY scheduled_departure DESC
        LIMIT 100
    """, params=(info["iata_code"], info["iata_code"]))
    st.markdown(f"**Linked flights at {info['iata_code']}:** {len(linked)} (max 100 shown)")
    st.dataframe(linked.fillna(""), use_container_width=True, hide_index=True)

st.divider()

# ---------------------------------------------------------------------------
# 4. DELAY ANALYSIS — percentages and distribution
# ---------------------------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    header("⏱️ Delay Rate by Airport")
    delay_df = run_query("""
        SELECT a.name,
               COUNT(*) AS total_flights,
               COUNT(CASE WHEN f.status = 'Delayed' THEN 1 END) AS delayed_flights,
               ROUND(COUNT(CASE WHEN f.status = 'Delayed' THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0), 1) AS delay_pct
        FROM flights f
        JOIN airport a ON f.destination_iata = a.iata_code
        GROUP BY a.name
        ORDER BY delay_pct DESC
    """)
    fig = px.bar(
        delay_df, x="name", y="delay_pct",
        color="delay_pct", color_continuous_scale="Blues",
        template="plotly_dark", labels={"delay_pct": "Delay %", "name": "Airport"}
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False, xaxis_tickangle=-45, coloraxis_showscale=False
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    header("📈 Flight Status Distribution")
    status_df = run_query("""
        SELECT status, COUNT(*) AS count
        FROM flights
        WHERE status IS NOT NULL
        GROUP BY status
        ORDER BY count DESC
    """)
    fig2 = px.pie(
        status_df, names="status", values="count",
        color_discrete_sequence=px.colors.sequential.Blues_r, template="plotly_dark"
    )
    fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ---------------------------------------------------------------------------
# 5. ROUTE LEADERBOARDS — busiest routes + most delayed airports
# ---------------------------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    header("🏆 Busiest Routes")
    routes_df = run_query("""
        SELECT origin_iata, destination_iata, COUNT(*) AS flight_count
        FROM flights
        WHERE origin_iata IS NOT NULL AND destination_iata IS NOT NULL
        GROUP BY origin_iata, destination_iata
        ORDER BY flight_count DESC
        LIMIT 10
    """)
    st.dataframe(routes_df, width="stretch", hide_index=True)

with col2:
    header("🚦 Most Delayed Airports")
    delayed_airports = run_query("""
        SELECT a.name,
               ad.total_flights,
               ad.delayed_flights,
               ROUND(ad.delayed_flights * 100.0 / NULLIF(ad.total_flights, 0), 1) AS delay_pct
        FROM airport_delays ad
        JOIN airport a ON ad.airport_iata = a.iata_code
        ORDER BY delay_pct DESC
        LIMIT 10
    """)
    st.dataframe(delayed_airports, width="stretch", hide_index=True)
