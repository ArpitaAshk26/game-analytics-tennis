import streamlit as st
import pandas as pd
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from streamlit_app.utils.db_helper import DatabaseHelper
from streamlit_app.utils.visualizations import *

# Page configuration
st.set_page_config(
    page_title="Tennis Analytics Dashboard",
    page_icon="🎾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #ff7f0e;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize database helper
@st.cache_resource
def get_db_helper():
    return DatabaseHelper()

db = get_db_helper()

# Main Page
st.markdown('<p class="main-header">🎾 Tennis Analytics Dashboard</p>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar
st.sidebar.title("📊 Navigation")
st.sidebar.info("""
    **Welcome to Tennis Analytics!**
    
    Explore comprehensive tennis data including:
    - 🏆 Competitions & Categories
    - 🏟️ Venues & Complexes
    - 📊 Player Rankings & Statistics
""")

# Get dashboard statistics
stats = db.get_dashboard_stats().iloc[0]

# Display Key Metrics
st.markdown('<p class="sub-header">📈 Key Statistics</p>', unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        label="🎾 Total Competitors",
        value=f"{int(stats['total_competitors']):,}"
    )

with col2:
    st.metric(
        label="🌍 Countries",
        value=f"{int(stats['total_countries']):,}"
    )

with col3:
    st.metric(
        label="⭐ Highest Points",
        value=f"{int(stats['highest_points']):,}"
    )

with col4:
    st.metric(
        label="🏆 Competitions",
        value=f"{int(stats['total_competitions']):,}"
    )

with col5:
    st.metric(
        label="🏟️ Venues",
        value=f"{int(stats['total_venues']):,}"
    )

st.markdown("---")

# Competitor Search & Filter Section
st.markdown('<p class="sub-header">🔍 Competitor Search & Filter</p>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    search_name = st.text_input("🔎 Search competitor by name", placeholder="Enter competitor name...")

with col2:
    st.write("")  # Spacing

# Filters
col1, col2, col3, col4 = st.columns(4)

with col1:
    rank_min = st.number_input("Min Rank", min_value=1, value=1, step=1)

with col2:
    rank_max = st.number_input("Max Rank", min_value=1, value=100, step=1)

with col3:
    countries = db.get_all_countries()['country'].tolist()
    country_filter = st.selectbox("Country", ["All"] + countries)

with col4:
    points_min = st.number_input("Min Points", min_value=0, value=0, step=100)

# Apply filters
if search_name:
    competitors_df = db.search_competitor(search_name)
    st.success(f"Found {len(competitors_df)} competitor(s) matching '{search_name}'")
else:
    competitors_df = db.filter_competitors(
        rank_min=rank_min,
        rank_max=rank_max,
        country=None if country_filter == "All" else country_filter,
        points_min=points_min if points_min > 0 else None
    )

# Display results
if len(competitors_df) > 0:
    st.dataframe(competitors_df, use_container_width=True, height=400)
    
    # Competitor Details Viewer
    st.markdown('<p class="sub-header">👤 Competitor Details</p>', unsafe_allow_html=True)
    
    selected_competitor = st.selectbox(
        "Select a competitor to view details",
        competitors_df['name'].tolist()
    )
    
    if selected_competitor:
        competitor_details = competitors_df[competitors_df['name'] == selected_competitor].iloc[0]
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Rank", f"#{int(competitor_details['rank'])}")
        
        with col2:
            st.metric("Country", competitor_details['country'])
        
        with col3:
            movement = int(competitor_details['movement'])
            st.metric("Movement", movement, delta=movement)
        
        with col4:
            st.metric("Points", f"{int(competitor_details['points']):,}")
        
        with col5:
            st.metric("Competitions Played", int(competitor_details['competitions_played']))
else:
    st.warning("No competitors found matching the criteria.")

st.markdown("---")

# Country-Wise Analysis
st.markdown('<p class="sub-header">🌍 Country-Wise Analysis</p>', unsafe_allow_html=True)

country_stats = db.get_competitors_per_country()

col1, col2 = st.columns(2)

with col1:
    st.dataframe(
        country_stats.head(20),
        use_container_width=True,
        height=400
    )

with col2:
    # Top 10 countries by competitor count
    top_countries = country_stats.head(10)
    fig = create_bar_chart(
        top_countries,
        x='country',
        y='competitor_count',
        title='Top 10 Countries by Competitor Count'
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Leaderboards
st.markdown('<p class="sub-header">🏆 Leaderboards</p>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.subheader("🥇 Top Ranked Competitors")
    top_ranked = db.get_top_n_competitors(10)
    st.dataframe(top_ranked, use_container_width=True, height=400)

with col2:
    st.subheader("⭐ Highest Points")
    highest_points = db.get_highest_points_competitors()
    st.dataframe(highest_points, use_container_width=True, height=400)

st.markdown("---")

# Footer
st.markdown("""
    <div style='text-align: center; color: gray; padding: 2rem;'>
        <p>Tennis Analytics Dashboard | Powered by SportRadar API & Streamlit</p>
        <p>Data updated in real-time from MSSQL Database</p>
    </div>
""", unsafe_allow_html=True)