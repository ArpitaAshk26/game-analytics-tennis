import streamlit as st
import pandas as pd
import sys
import os
import plotly.express as px  # Add this line
import plotly.graph_objects as go  # Add this line

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from streamlit_app.utils.db_helper import DatabaseHelper
from streamlit_app.utils.visualizations import *
# Page configuration
st.set_page_config(
    page_title="Rankings Analysis",
    page_icon="📊",
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
st.markdown('<p class="main-header">📊 Player Rankings Analysis</p>', unsafe_allow_html=True)
st.markdown("---")

# Tab layout
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏆 Leaderboards",
    "🔍 Search & Filter",
    "🌍 Country Analysis",
    "📈 Rank Movements",
    "📊 Statistics"
])

# ==================== TAB 1: Leaderboards ====================
with tab1:
    st.markdown('<p class="sub-header">🏆 Top Players Leaderboards</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🥇 Top Ranked Players")
        
        top_n = st.slider("Select number of top players", 5, 50, 10, key="top_rank")
        top_ranked = db.get_top_n_competitors(top_n)
        
        st.dataframe(
            top_ranked.style.background_gradient(subset=['points'], cmap='YlOrRd'),
            use_container_width=True,
            height=500
        )
    
    with col2:
        st.markdown("### ⭐ Highest Points")
        
        highest_points = db.get_highest_points_competitors()
        
        st.dataframe(
            highest_points.style.background_gradient(subset=['points'], cmap='Blues'),
            use_container_width=True,
            height=500
        )
    
    # Visualization
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        # Top 10 by rank
        fig = create_bar_chart(
            top_ranked.head(10),
            x='name',
            y='points',
            title='Top 10 Players by Rank - Points Comparison',
            color='country'
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Movement analysis for top 10
        movement_data = top_ranked.head(10)
        fig = px.scatter(
            movement_data,
            x='rank',
            y='points',
            size='points',
            color='movement',
            hover_data=['name', 'country'],
            title='Top 10 Players - Rank vs Points',
            color_continuous_scale='RdYlGn'
        )
        st.plotly_chart(fig, use_container_width=True)

# ==================== TAB 2: Search & Filter ====================
with tab2:
    st.markdown('<p class="sub-header">🔍 Search & Filter Players</p>', unsafe_allow_html=True)
    
    # Search by name
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_name = st.text_input("🔎 Search player by name", placeholder="Enter player name...")
    
    # Filters
    st.markdown("### 🎯 Advanced Filters")
    
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
        results = db.search_competitor(search_name)
        st.success(f"🔍 Found {len(results)} player(s) matching '{search_name}'")
    else:
        results = db.filter_competitors(
            rank_min=rank_min,
            rank_max=rank_max,
            country=None if country_filter == "All" else country_filter,
            points_min=points_min if points_min > 0 else None
        )
        st.info(f"📊 Showing {len(results)} player(s) matching your filters")
    
    # Display results
    if len(results) > 0:
        st.dataframe(
            results.style.background_gradient(subset=['points'], cmap='Greens'),
            use_container_width=True,
            height=400
        )
        
        # Download button
        csv = results.to_csv(index=False)
        st.download_button(
            label="📥 Download Results",
            data=csv,
            file_name="filtered_players.csv",
            mime="text/csv"
        )
        
        # Player details section
        st.markdown("---")
        st.markdown("### 👤 Player Details")
        
        selected_player = st.selectbox("Select a player to view details", results['name'].tolist())
        
        if selected_player:
            player_data = results[results['name'] == selected_player].iloc[0]
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("🏅 Rank", f"#{int(player_data['rank'])}")
            
            with col2:
                st.metric("🌍 Country", player_data['country'])
            
            with col3:
                movement = int(player_data['movement'])
                st.metric("📊 Movement", movement, delta=movement)
            
            with col4:
                st.metric("⭐ Points", f"{int(player_data['points']):,}")
            
            with col5:
                st.metric("🎾 Competitions", int(player_data['competitions_played']))
    else:
        st.warning("No players found matching your criteria")

# ==================== TAB 3: Country Analysis ====================
with tab3:
    st.markdown('<p class="sub-header">🌍 Country-Wise Analysis</p>', unsafe_allow_html=True)
    
    country_stats = db.get_competitors_per_country()
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Countries", len(country_stats))
    
    with col2:
        top_country = country_stats.iloc[0]
        st.metric("Most Players", f"{top_country['country']} ({int(top_country['competitor_count'])})")
    
    with col3:
        avg_points_all = country_stats['avg_points'].mean()
        st.metric("Global Avg Points", f"{avg_points_all:.0f}")
    
    st.markdown("---")
    
    # Table and charts
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📋 Country Statistics")
        st.dataframe(
            country_stats.style.background_gradient(subset=['competitor_count', 'avg_points'], cmap='YlGnBu'),
            use_container_width=True,
            height=500
        )
    
    with col2:
        st.markdown("### 📊 Top 15 Countries by Player Count")
        top_countries = country_stats.head(15)
        
        fig = create_bar_chart(
            top_countries,
            x='country',
            y='competitor_count',
            title='Top 15 Countries by Number of Players'
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    # Additional visualizations
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🌍 Top 10 Countries Distribution")
        top_10_countries = country_stats.head(10)
        
        fig = create_pie_chart(
            top_10_countries,
            names='country',
            values='competitor_count',
            title='Player Distribution (Top 10 Countries)'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📈 Average Points by Country (Top 15)")
        top_points_countries = country_stats.nlargest(15, 'avg_points')
        
        fig = create_bar_chart(
            top_points_countries,
            x='country',
            y='avg_points',
            title='Top 15 Countries by Average Points'
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    # Country-specific analysis
    st.markdown("---")
    st.markdown("### 🔍 Specific Country Analysis")
    
    selected_country_analysis = st.selectbox(
        "Select a country for detailed analysis",
        country_stats['country'].tolist()
    )
    
    if selected_country_analysis:
        country_players = db.filter_competitors(country=selected_country_analysis)
        country_total = db.get_country_total_points(selected_country_analysis).iloc[0]['total_points']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Players", len(country_players))
        
        with col2:
            st.metric("Total Points", f"{int(country_total):,}")
        
        with col3:
            avg_points = country_players['points'].mean()
            st.metric("Average Points", f"{avg_points:.0f}")
        
        st.dataframe(country_players, use_container_width=True, height=400)

# ==================== TAB 4: Rank Movements ====================
with tab4:
    st.markdown('<p class="sub-header">📈 Rank Movement Analysis</p>', unsafe_allow_html=True)
    
    all_competitors = db.get_all_competitors_with_rank()
    
    # Stable rank players
    stable_players = db.get_stable_rank_competitors()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ⏸️ Stable Rankings (No Movement)")
        st.metric("Players with Stable Rank", len(stable_players))
        st.dataframe(stable_players, use_container_width=True, height=400)
    
    with col2:
        # Movement distribution
        st.markdown("### 📊 Movement Distribution")
        
        movement_up = len(all_competitors[all_competitors['movement'] > 0])
        movement_down = len(all_competitors[all_competitors['movement'] < 0])
        movement_stable = len(all_competitors[all_competitors['movement'] == 0])
        
        movement_data = pd.DataFrame({
            'category': ['⬆️ Moved Up', '⬇️ Moved Down', '⏸️ Stable'],
            'count': [movement_up, movement_down, movement_stable]
        })
        
        fig = create_pie_chart(
            movement_data,
            names='category',
            values='count',
            title='Rank Movement Distribution'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Biggest movers
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ⬆️ Biggest Climbers")
        climbers = all_competitors.nlargest(10, 'movement')
        st.dataframe(climbers[['name', 'country', 'rank', 'movement', 'points']], use_container_width=True)
    
    with col2:
        st.markdown("### ⬇️ Biggest Fallers")
        fallers = all_competitors.nsmallest(10, 'movement')
        st.dataframe(fallers[['name', 'country', 'rank', 'movement', 'points']], use_container_width=True)
    
    # Movement vs Points scatter
    st.markdown("---")
    st.markdown("### 📊 Movement vs Points Analysis")
    
    fig = px.scatter(
        all_competitors,
        x='points',
        y='movement',
        color='movement',
        hover_data=['name', 'country', 'rank'],
        title='Rank Movement vs Points',
        color_continuous_scale='RdYlGn',
        labels={'movement': 'Rank Movement', 'points': 'Points'}
    )
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

# ==================== TAB 5: Statistics ====================
with tab5:
    st.markdown('<p class="sub-header">📊 Overall Statistics</p>', unsafe_allow_html=True)
    
    all_data = db.get_all_competitors_with_rank()
    
    # Key metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Players", len(all_data))
    
    with col2:
        st.metric("Avg Rank", f"{all_data['rank'].mean():.1f}")
    
    with col3:
        st.metric("Avg Points", f"{all_data['points'].mean():.0f}")
    
    with col4:
        st.metric("Max Points", f"{all_data['points'].max():,}")
    
    with col5:
        st.metric("Avg Competitions", f"{all_data['competitions_played'].mean():.1f}")
    
    st.markdown("---")
    
    # Distribution charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Points Distribution")
        fig = px.histogram(
            all_data,
            x='points',
            nbins=50,
            title='Distribution of Player Points',
            labels={'points': 'Points', 'count': 'Number of Players'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📊 Competitions Played Distribution")
        fig = px.histogram(
            all_data,
            x='competitions_played',
            nbins=30,
            title='Distribution of Competitions Played',
            labels={'competitions_played': 'Competitions', 'count': 'Number of Players'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Summary statistics table
    st.markdown("---")
    st.markdown("### 📋 Detailed Statistics")
    
    summary_stats = all_data[['rank', 'points', 'movement', 'competitions_played']].describe()
    st.dataframe(summary_stats, use_container_width=True)
    
    # Correlations
    st.markdown("---")
    st.markdown("### 🔗 Points vs Competitions Played")
    
    fig = px.scatter(
        all_data,
        x='competitions_played',
        y='points',
        color='rank',
        size='points',
        hover_data=['name', 'country'],
        title='Relationship between Competitions Played and Points',
        color_continuous_scale='Viridis'
    )
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: gray;'>
        <p>Player Rankings Analysis | Data from SportRadar API</p>
    </div>
""", unsafe_allow_html=True)