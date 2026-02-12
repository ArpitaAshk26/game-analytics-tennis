import streamlit as st
import pandas as pd
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from streamlit_app.utils.db_helper import DatabaseHelper
from streamlit_app.utils.visualizations import *

# Page configuration
st.set_page_config(
    page_title="Venues Analysis",
    page_icon="🏟️",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
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
    </style>
""", unsafe_allow_html=True)

# Initialize database helper
@st.cache_resource
def get_db_helper():
    return DatabaseHelper()

db = get_db_helper()

# Header
st.markdown('<p class="main-header">🏟️ Venues & Complexes Analysis</p>', unsafe_allow_html=True)
st.markdown("---")

# Tab layout
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 All Venues",
    "🏢 By Complex",
    "🌍 By Country",
    "🕐 Timezones",
    "📊 Statistics"
])

# ==================== TAB 1: All Venues ====================
with tab1:
    st.markdown('<p class="sub-header">📋 All Venues with Complex Names</p>', unsafe_allow_html=True)
    
    all_venues = db.get_all_venues_with_complex()
    
    # Search functionality
    search_venue = st.text_input("🔎 Search venue or city", placeholder="Enter venue or city name...")
    
    if search_venue:
        filtered_venues = all_venues[
            (all_venues['venue_name'].str.contains(search_venue, case=False, na=False)) |
            (all_venues['city_name'].str.contains(search_venue, case=False, na=False))
        ]
        st.success(f"Found {len(filtered_venues)} venue(s)")
    else:
        filtered_venues = all_venues
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Venues", len(all_venues))
    with col2:
        st.metric("Countries", all_venues['country_name'].nunique())
    with col3:
        st.metric("Cities", all_venues['city_name'].nunique())
    
    # Display table
    st.dataframe(filtered_venues, use_container_width=True, height=500)
    
    # Download button
    csv = filtered_venues.to_csv(index=False)
    st.download_button(
        label="📥 Download Venues Data",
        data=csv,
        file_name="venues.csv",
        mime="text/csv"
    )

# ==================== TAB 2: By Complex ====================
with tab2:
    st.markdown('<p class="sub-header">🏢 Venues by Complex</p>', unsafe_allow_html=True)
    
    complex_counts = db.get_venues_count_by_complex()
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.dataframe(complex_counts, use_container_width=True, height=400)
    
    with col2:
        # Bar chart - top complexes
        top_complexes = complex_counts.head(15)
        fig = create_bar_chart(
            top_complexes,
            x='complex_name',
            y='venue_count',
            title='Top 15 Complexes by Venue Count'
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    # Complexes with multiple venues
    st.markdown("---")
    st.markdown("### 🏢 Complexes with Multiple Venues")
    
    multi_venue_complexes = db.get_complexes_with_multiple_venues()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Complexes with >1 Venue", len(multi_venue_complexes))
        st.dataframe(multi_venue_complexes, use_container_width=True, height=400)
    
    with col2:
        if len(multi_venue_complexes) > 0:
            fig = create_pie_chart(
                multi_venue_complexes.head(10),
                names='complex_name',
                values='venue_count',
                title='Top 10 Multi-Venue Complexes'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Specific complex details
    st.markdown("---")
    st.markdown("### 🔍 Venue Details by Complex")
    
    all_complexes = db.get_all_complexes()['complex_name'].tolist()
    selected_complex = st.selectbox("Select a complex", all_complexes)
    
    if selected_complex:
        complex_venues = db.get_venues_by_complex(selected_complex)
        st.info(f"Found {len(complex_venues)} venue(s) in {selected_complex}")
        st.dataframe(complex_venues, use_container_width=True)

# ==================== TAB 3: By Country ====================
with tab3:
    st.markdown('<p class="sub-header">🌍 Venues by Country</p>', unsafe_allow_html=True)
    
    country_counts = db.get_venues_grouped_by_country()
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.dataframe(country_counts.head(20), use_container_width=True, height=500)
    
    with col2:
        # Top countries chart
        top_countries = country_counts.head(15)
        fig = create_bar_chart(
            top_countries,
            x='country_name',
            y='venue_count',
            title='Top 15 Countries by Venue Count'
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    # World map visualization
    st.markdown("---")
    st.markdown("### 🗺️ Global Venue Distribution")
    
    # Get all venues for map
    all_venues_map = db.get_all_venues_with_complex()
    
    # Create choropleth map
    fig = px.choropleth(
        country_counts,
        locations='country_name',
        locationmode='country names',
        color='venue_count',
        title='Global Venue Distribution',
        color_continuous_scale='Blues',
        labels={'venue_count': 'Number of Venues'}
    )
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    # Country-specific details
    st.markdown("---")
    st.markdown("### 🔍 Venues in Specific Country")
    
    all_countries_list = country_counts['country_name'].tolist()
    selected_country = st.selectbox("Select a country", all_countries_list)
    
    if selected_country:
        country_venues = db.get_venues_by_country(selected_country)
        st.success(f"Found {len(country_venues)} venue(s) in {selected_country}")
        st.dataframe(country_venues, use_container_width=True, height=400)

# ==================== TAB 4: Timezones ====================
with tab4:
    st.markdown('<p class="sub-header">🕐 Venues by Timezone</p>', unsafe_allow_html=True)
    
    timezone_venues = db.get_all_venues_with_timezones()
    
    # Timezone distribution
    timezone_counts = timezone_venues.groupby('timezone').size().reset_index(name='count')
    timezone_counts = timezone_counts.sort_values('count', ascending=False)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.dataframe(timezone_counts, use_container_width=True, height=500)
    
    with col2:
        # Top timezones chart
        top_timezones = timezone_counts.head(15)
        fig = create_bar_chart(
            top_timezones,
            x='timezone',
            y='count',
            title='Top 15 Timezones by Venue Count'
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    # Filter by timezone
    st.markdown("---")
    st.markdown("### 🔍 Venues in Specific Timezone")
    
    selected_timezone = st.selectbox("Select timezone", timezone_counts['timezone'].tolist())
    
    if selected_timezone:
        tz_venues = timezone_venues[timezone_venues['timezone'] == selected_timezone]
        st.info(f"Found {len(tz_venues)} venue(s) in {selected_timezone}")
        st.dataframe(tz_venues, use_container_width=True)

# ==================== TAB 5: Statistics ====================
with tab5:
    st.markdown('<p class="sub-header">📊 Venue Statistics Overview</p>', unsafe_allow_html=True)
    
    all_venues_stats = db.get_all_venues_with_complex()
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Venues", len(all_venues_stats))
    
    with col2:
        st.metric("Total Complexes", all_venues_stats['complex_name'].nunique())
    
    with col3:
        st.metric("Countries", all_venues_stats['country_name'].nunique())
    
    with col4:
        st.metric("Timezones", all_venues_stats['timezone'].nunique())
    
    st.markdown("---")
    
    # Distribution charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🌍 Top 10 Countries")
        country_dist = all_venues_stats.groupby('country_name').size().reset_index(name='count')
        country_dist = country_dist.sort_values('count', ascending=False).head(10)
        
        fig = create_pie_chart(
            country_dist,
            names='country_name',
            values='count',
            title='Venue Distribution by Country (Top 10)'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 🏙️ Top 10 Cities")
        city_dist = all_venues_stats.groupby('city_name').size().reset_index(name='count')
        city_dist = city_dist.sort_values('count', ascending=False).head(10)
        
        fig = create_pie_chart(
            city_dist,
            names='city_name',
            values='count',
            title='Venue Distribution by City (Top 10)'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Summary table
    st.markdown("---")
    st.markdown("### 📋 Summary by Country")
    
    summary = all_venues_stats.groupby('country_name').agg({
        'venue_name': 'count',
        'complex_name': 'nunique',
        'city_name': 'nunique'
    }).reset_index()
    
    summary.columns = ['Country', 'Venues', 'Complexes', 'Cities']
    summary = summary.sort_values('Venues', ascending=False)
    
    st.dataframe(summary, use_container_width=True, height=500)

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: gray;'>
        <p>Venues & Complexes Analysis | Data from SportRadar API</p>
    </div>
""", unsafe_allow_html=True)