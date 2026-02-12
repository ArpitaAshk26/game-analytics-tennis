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
    page_title="Competitions Analysis",
    page_icon="🏆",
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
st.markdown('<p class="main-header">🏆 Competitions Analysis</p>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar filters

categories = db.get_all_categories()['category_name'].tolist()
selected_category = "All"

# Tab layout
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 All Competitions", 
    "📊 By Category", 
    "👥 Doubles", 
    "🌳 Hierarchy",
    "📈 Distribution"
])

# ==================== TAB 1: All Competitions ====================
with tab1:
    st.markdown('<p class="sub-header">📋 All Competitions with Categories</p>', unsafe_allow_html=True)
    
    all_competitions = db.get_all_competitions_with_category()
    
    # Add search
    search_comp = st.text_input("🔎 Search competition", placeholder="Enter competition name...")
    
    if search_comp:
        filtered_comps = all_competitions[
            all_competitions['competition_name'].str.contains(search_comp, case=False, na=False)
        ]
        st.success(f"Found {len(filtered_comps)} competition(s)")
    else:
        filtered_comps = all_competitions
    
    # Display summary
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Competitions", len(all_competitions))
    with col2:
        st.metric("Total Categories", all_competitions['category_name'].nunique())
    with col3:
        doubles_count = len(all_competitions[all_competitions['type'] == 'doubles'])
        st.metric("Doubles Competitions", doubles_count)
    
    # Display table
    st.dataframe(filtered_comps, use_container_width=True, height=500)
    
    # Download button
    csv = filtered_comps.to_csv(index=False)
    st.download_button(
        label="📥 Download Data as CSV",
        data=csv,
        file_name="competitions.csv",
        mime="text/csv"
    )

# ==================== TAB 2: By Category ====================
with tab2:
    st.markdown('<p class="sub-header">📊 Competitions Count by Category</p>', unsafe_allow_html=True)
    
    category_counts = db.get_competitions_count_by_category()
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.dataframe(category_counts, use_container_width=True, height=400)
    
    with col2:
        # Bar chart
        fig = create_bar_chart(
            category_counts,
            x='category_name',
            y='competition_count',
            title='Number of Competitions per Category'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Pie chart
    st.markdown("### 📊 Category Distribution")
    fig_pie = create_pie_chart(
        category_counts,
        names='category_name',
        values='competition_count',
        title='Competition Distribution by Category'
    )
    st.plotly_chart(fig_pie, use_container_width=True)
    
    # Specific category details
    st.markdown("---")
    st.markdown("### 🔍 Competition Details by Category")
    
    selected_cat_detail = st.selectbox("Select a category to view competitions", categories)
    
    if selected_cat_detail:
        cat_comps = db.get_competitions_by_category(selected_cat_detail)
        st.info(f"Found {len(cat_comps)} competitions in {selected_cat_detail}")
        st.dataframe(cat_comps, use_container_width=True, height=400)

# ==================== TAB 3: Doubles Competitions ====================
with tab3:
    st.markdown('<p class="sub-header">👥 Doubles Competitions</p>', unsafe_allow_html=True)
    
    doubles_comps = db.get_doubles_competitions()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total Doubles Competitions", len(doubles_comps))
    
    with col2:
        male_doubles = len(doubles_comps[doubles_comps['gender'] == 'men'])
        female_doubles = len(doubles_comps[doubles_comps['gender'] == 'women'])
        st.metric("Men's Doubles", male_doubles)
        st.metric("Women's Doubles", female_doubles)
    
    # Gender distribution chart
    gender_dist = doubles_comps.groupby('gender').size().reset_index(name='count')
    fig = create_pie_chart(
        gender_dist,
        names='gender',
        values='count',
        title='Doubles Competitions by Gender'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Display table
    st.dataframe(doubles_comps, use_container_width=True, height=500)

# ==================== TAB 4: Competition Hierarchy ====================
with tab4:
    st.markdown('<p class="sub-header">🌳 Competition Hierarchy</p>', unsafe_allow_html=True)
    
    # Top-level competitions
    st.markdown("### 🔝 Top-Level Competitions (No Parent)")
    top_level = db.get_top_level_competitions()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Top-Level Competitions", len(top_level))
    with col2:
        st.info("These are main tournaments without parent competitions")
    
    st.dataframe(top_level, use_container_width=True, height=400)
    
    # Parent-Child relationships
    st.markdown("---")
    st.markdown("### 👨‍👧 Parent-Child Competitions")
    parent_child = db.get_parent_child_competitions()
    
    if len(parent_child) > 0:
        st.success(f"Found {len(parent_child)} sub-competitions")
        st.dataframe(parent_child, use_container_width=True, height=400)
    else:
        st.warning("""
        ⚠️ No parent-child relationships found in current dataset.
        
        **Note:** The SportRadar trial API returns only current active competitions 
        without historical parent tournament data. In a production environment with 
        complete data, this section would display the full tournament hierarchy.
        """)

# ==================== TAB 5: Type Distribution ====================
with tab5:
    st.markdown('<p class="sub-header">📈 Competition Type Distribution by Category</p>', unsafe_allow_html=True)
    
    type_dist = db.get_competition_type_distribution()
    
    # Pivot table for better visualization
    pivot_data = type_dist.pivot(
        index='category_name',
        columns='type',
        values='count'
    ).fillna(0)
    
    st.dataframe(pivot_data, use_container_width=True)
    
    # Stacked bar chart
    fig = px.bar(
        type_dist,
        x='category_name',
        y='count',
        color='type',
        title='Competition Type Distribution by Category',
        barmode='stack',
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
    
    # Category-wise breakdown
    st.markdown("---")
    st.markdown("### 📊 Detailed Breakdown")
    
    selected_cat_dist = st.selectbox(
        "Select category for detailed view",
        type_dist['category_name'].unique()
    )
    
    cat_data = type_dist[type_dist['category_name'] == selected_cat_dist]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.dataframe(cat_data[['type', 'count']], use_container_width=True)
    
    with col2:
        fig_pie = create_pie_chart(
            cat_data,
            names='type',
            values='count',
            title=f'Competition Types in {selected_cat_dist}'
        )
        st.plotly_chart(fig_pie, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: gray;'>
        <p>Competitions Analysis | Data from SportRadar API</p>
    </div>
""", unsafe_allow_html=True)