import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import preprocessing_helpers as pph
import visual_helpers as vh
import os
import json
from datetime import datetime, date
from pathlib import Path
from visual_helpers import get_contributing_factors, get_human_factors_person1, get_formatted_labels, get_title

# Define months dictionary globally (to fix NameError)
months = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
    7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
}

# Configure Streamlit page
st.set_page_config(
    page_title="ASRS Runway Incursion Analysis Dashboard",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS to match original design
st.markdown("""
<style>
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Root variables matching original design */
    :root {
        --light-bg: #f5f7fa;
        --light-text: #333;
        --light-title: #0056b3;
        --light-panel-bg: white;
        --light-panel-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        --light-border: #eee;
        --light-btn-bg: #0056b3;
        --light-btn-hover: #003d82;
        --header-bg: #0056b3;
    }
    
    /* Main container */
    .stApp {
        background: var(--light-bg);
    }
    
    /* Header matching original */
    .main-header {
        background: var(--header-bg);
        color: white;
        padding: 1.5rem 0;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
        margin: -1rem -1rem 2rem -1rem;
        position: relative;
    }
    
    .main-header h1 {
        font-size: 2rem;
        font-weight: 300;
        letter-spacing: 1px;
        margin: 0;
    }
    
    /* Date selector panel matching original */
    .date-selector {
        background: var(--light-panel-bg);
        padding: 2rem;
        border-radius: 8px;
        box-shadow: var(--light-panel-shadow);
        margin-bottom: 2rem;
        border: 1px solid var(--light-border);
    }
    
    .date-selector h2 {
        color: var(--light-title);
        margin-bottom: 1.5rem;
        font-size: 1.5rem;
        font-weight: 300;
    }
    
    /* Date inputs horizontal layout */
    .date-inputs {
        display: flex;
        flex-wrap: wrap;
        gap: 1.5rem;
        margin-bottom: 2rem;
    }
    
    /* State filter section */
    .filter-section {
        background: var(--light-panel-bg);
        padding: 2rem;
        border-radius: 8px;
        box-shadow: var(--light-panel-shadow);
        margin-bottom: 2rem;
        border: 1px solid var(--light-border);
    }
    
    .filter-section h3 {
        color: var(--light-title);
        margin-bottom: 1.5rem;
        font-size: 1.3rem;
        font-weight: 300;
    }
    
    /* Buttons matching original style */
    .stButton > button {
        background: var(--light-btn-bg) !important;
        color: white !important;
        border: none !important;
        padding: 0.75rem 2rem !important;
        border-radius: 4px !important;
        font-weight: bold !important;
        font-size: 1rem !important;
        cursor: pointer !important;
        transition: background 0.3s !important;
        width: 100% !important;
    }
    
    .stButton > button:hover {
        background: var(--light-btn-hover) !important;
    }
    
    /* Navigation buttons */
    .nav-buttons {
        display: flex;
        gap: 1rem;
        justify-content: center;
        margin: 2rem 0;
    }
    
    .nav-button {
        background: var(--light-btn-bg);
        color: white;
        padding: 0.75rem 1.5rem;
        border: none;
        border-radius: 4px;
        font-weight: bold;
        cursor: pointer;
        text-decoration: none;
        display: inline-block;
        transition: background 0.3s;
    }
    
    .nav-button:hover {
        background: var(--light-btn-hover);
        color: white;
        text-decoration: none;
    }
    
    /* Visualization containers */
    .viz-container {
        background: var(--light-panel-bg);
        padding: 2rem;
        border-radius: 8px;
        box-shadow: var(--light-panel-shadow);
        margin: 1rem 0;
        border: 1px solid var(--light-border);
    }
    
    .viz-container h2 {
        color: var(--light-title);
        margin-bottom: 1.5rem;
        font-size: 1.3rem;
        font-weight: 300;
    }
    
    /* Page navigation */
    .page-navigation {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 2rem 0;
        padding: 1rem;
        background: var(--light-panel-bg);
        border-radius: 8px;
        box-shadow: var(--light-panel-shadow);
    }
    
    .back-btn, .next-btn {
        background: #f0f0f0;
        color: #333;
        padding: 0.5rem 1rem;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        text-decoration: none;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        transition: background 0.3s;
    }
    
    .back-btn:hover, .next-btn:hover {
        background: #e0e0e0;
        color: #333;
        text-decoration: none;
    }
    
    .filters-summary {
        font-weight: bold;
        color: var(--light-title);
    }
    
    /* Success message */
    .success-message {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
        text-align: center;
    }
    
    /* Loading message */
    .loading-message {
        text-align: center;
        font-size: 1.1rem;
        color: var(--light-text);
        padding: 2rem;
        background: var(--light-panel-bg);
        border-radius: 8px;
        border: 1px solid var(--light-border);
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 0.6; }
        50% { opacity: 1; }
        100% { opacity: 0.6; }
    }
    
    /* State chips styling */
    .state-chip {
        display: inline-block;
        background: #e7f0f7;
        color: #0056b3;
        padding: 0.25rem 0.75rem;
        margin: 0.25rem;
        border-radius: 15px;
        font-size: 0.9rem;
        border: 1px solid #d1ecf1;
    }
    
    /* Hide Streamlit selectbox styling */
    .stSelectbox > label {
        font-weight: 600;
        color: var(--light-title);
    }
    
    /* Custom multiselect styling */
    .stMultiSelect > label {
        font-weight: 600;
        color: var(--light-title);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for page navigation
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'filters'
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'runway_df' not in st.session_state:
    st.session_state.runway_df = None
if 'last_generation_params' not in st.session_state:
    st.session_state.last_generation_params = None
if 'generated_charts' not in st.session_state:
    st.session_state.generated_charts = None

# Header matching original design
st.markdown("""
<div class="main-header">
    <h1>ASRS Runway Incursion Data Visualization</h1>
</div>
""", unsafe_allow_html=True)

# Data loading function
@st.cache_data
def load_and_preprocess_data():
    """Load and preprocess the ASRS data"""
    try:
        csv_file = 'Jan1990_Jan2025.csv'
        
        # Load and preprocess data
        runway_df = pph.load_data(csv_file)
        runway_df = pph.set_header(runway_df)
        
        # Remove empty columns and columns with minimal data
        runway_df, _ = pph.delete_empty_columns(runway_df)
        runway_df, _ = pph.delete_minimal_data_columns(runway_df, threshold=100)
        
        # Convert dates
        runway_df = pph.convert_dates(runway_df)
        
        # Create subsets
        place_df = pph.create_data_subset(runway_df, 'Place')
        assessments_df = pph.create_data_subset(runway_df, 'Assessments')
        person1_df = pph.create_data_subset(runway_df, 'Person 1')
        
        return runway_df, place_df, assessments_df, person1_df
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None, None, None, None

# Load data
if not st.session_state.data_loaded:
    with st.spinner("Loading ASRS data..."):
        df, place_df, assessments_df, person1_df = load_and_preprocess_data()
        if df is not None:
            st.session_state.runway_df = df
            st.session_state.place_df = place_df
            st.session_state.assessments_df = assessments_df
            st.session_state.person1_df = person1_df
            st.session_state.data_loaded = True

# Define months dictionary globally (moved from inside function to fix NameError)
months = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
    7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
}

# Navigation functions
def go_to_page(page_name):
    st.session_state.current_page = page_name

# Page 1: Filters (matching original design)
if st.session_state.current_page == 'filters':
    if st.session_state.data_loaded and st.session_state.runway_df is not None:
        
        # Date selector section
        st.markdown('<div class="date-selector">', unsafe_allow_html=True)
        st.markdown("<h2>Select Date Range</h2>", unsafe_allow_html=True)
        
        # Date inputs in horizontal layout
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            start_month = st.selectbox("Start Month:", list(months.keys()), 
                                     format_func=lambda x: months[x], key="start_month")
            
        with col2:
            start_year = st.selectbox("Start Year:", list(range(1990, 2026)), 
                                    index=20, key="start_year")  # Default to 2010
            
        with col3:
            end_month = st.selectbox("End Month:", list(months.keys()), 
                                   format_func=lambda x: months[x], 
                                   index=11, key="end_month")  # Default to December
            
        with col4:
            end_year = st.selectbox("End Year:", list(range(1990, 2026)), 
                                  index=35, key="end_year")  # Default to 2025
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # State filtering section
        st.markdown('<div class="filter-section">', unsafe_allow_html=True)
        st.markdown("<h3>Filter by Location (Optional)</h3>", unsafe_allow_html=True)
        
        enable_state_filter = st.checkbox("Enable Location Filtering", key="enable_state_filter")
        
        selected_states = []
        if enable_state_filter:
            # Get unique states from data
            sample_df = pph.create_data_subset(st.session_state.runway_df, 'Place')
            state_column = "State Reference [Place.1]"
            
            if state_column in sample_df.columns:
                all_locations = sorted(sample_df[state_column].dropna().unique())
                
                # Categorize locations
                us_states = {
                    'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
                    'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
                    'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
                    'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
                    'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY', 'DC'
                }
                us_territories = {'PR', 'VI', 'GU', 'AS', 'MP'}
                canadian_provinces = {'AB', 'BC', 'MB', 'NB', 'NL', 'NS', 'NT', 'NU', 'ON', 'PE', 'PQ', 'SK', 'YT'}
                
                # Categorize the actual data
                us_locs = [loc for loc in all_locations if loc in us_states]
                territory_locs = [loc for loc in all_locations if loc in us_territories]
                canadian_locs = [loc for loc in all_locations if loc in canadian_provinces]
                other_locs = [loc for loc in all_locations if loc not in us_states and loc not in us_territories and loc not in canadian_provinces]
                
                st.info(f"📍 {len(all_locations)} locations: {len(us_locs)} US States/DC, {len(territory_locs)} US Territories, {len(canadian_locs)} Canadian Provinces, {len(other_locs)} Other")
                
                # Location selection with better organization
                # Quick select buttons setup
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Quick Select:**")
                    us_only_clicked = st.button("🇺🇸 US States Only", key="us_only")
                    north_america_clicked = st.button("🌎 North America", key="north_america")
                
                # Prepare display options
                all_options = []
                if us_locs:
                    all_options.extend([f"🇺🇸 {loc}" for loc in us_locs])
                if territory_locs:
                    all_options.extend([f"🏝️ {loc}" for loc in territory_locs])
                if canadian_locs:
                    all_options.extend([f"🇨🇦 {loc}" for loc in canadian_locs])
                if other_locs:
                    all_options.extend([f"🌐 {loc}" for loc in other_locs])
                
                # Set default selections based on button clicks
                if us_only_clicked:
                    default_selection = [f"🇺🇸 {loc}" for loc in us_locs]
                elif north_america_clicked:
                    default_selection = ([f"🇺🇸 {loc}" for loc in us_locs] + 
                                       [f"🏝️ {loc}" for loc in territory_locs] + 
                                       [f"🇨🇦 {loc}" for loc in canadian_locs])
                else:
                    default_selection = all_options  # Default to all locations
                
                with col2:
                    st.markdown("**Or choose specific locations:**")
                    selected_display = st.multiselect(
                        "Select Locations:",
                        options=all_options,
                        default=default_selection,
                        help="🇺🇸 = US States/DC, 🏝️ = US Territories, 🇨🇦 = Canadian Provinces, 🌐 = Other",
                        key="selected_states_display"
                    )
                
                # Extract actual state codes from the display format
                selected_states = [item.split(' ', 1)[1] for item in selected_display]
                
                if selected_states:
                    # Display selected locations as chips
                    chips_html = "".join([f'<span class="state-chip">{state}</span>' for state in selected_states[:10]])
                    if len(selected_states) > 10:
                        chips_html += f'<span class="state-chip">+{len(selected_states)-10} more</span>'
                    st.markdown(f"**Selected:** {chips_html}", unsafe_allow_html=True)
                else:
                    st.warning("⚠️ No locations selected - this will result in no data")
            else:
                st.error("State information not available in the dataset")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Generate button
        start_date = date(start_year, start_month, 1)
        end_date = date(end_year, end_month, 1)
        
        if start_date >= end_date:
            st.error("❌ End date must be after start date")
        elif enable_state_filter and not selected_states:
            st.error("❌ Please select at least one location when location filtering is enabled")
        else:
            if st.button("Generate Visualizations", type="primary", key="generate_btn"):
                # Store generation parameters
                st.session_state.last_generation_params = {
                    'start_month': start_month,
                    'start_year': start_year,
                    'end_month': end_month,
                    'end_year': end_year,
                    'enable_state_filter': enable_state_filter,
                    'selected_states': selected_states
                }
                
                with st.spinner("🔄 Generating visualizations..."):
                    try:
                        # Filter data by date range
                        filtered_df = pph.get_data_in_date_range(
                            str(start_month).zfill(2), str(start_year),
                            str(end_month).zfill(2), str(end_year),
                            st.session_state.runway_df
                        )
                        
                        if len(filtered_df) == 0:
                            st.error("❌ No data found for the selected date range")
                            st.stop()
                        
                        # Create data subsets
                        place_df = pph.create_data_subset(filtered_df, 'Place')
                        assessments_df = pph.create_data_subset(filtered_df, 'Assessments')
                        person1_df = pph.create_data_subset(filtered_df, 'Person 1')
                        
                        # Add ACN columns if needed
                        for df in [place_df, assessments_df, person1_df]:
                            if "ACN" in filtered_df.columns and "ACN" not in df.columns:
                                df["ACN"] = filtered_df["ACN"]
                        
                        # Apply location filtering if enabled
                        if enable_state_filter and selected_states:
                            state_filters_dict = {state: True for state in selected_states}
                            state_ACNs = pph.get_state_ACNs(state_filters_dict, place_df)
                            
                            if len(state_ACNs) == 0:
                                st.error("❌ No data found for the selected locations")
                                st.stop()
                            
                            # Filter all dataframes
                            filtered_df = pph.get_ACN_filtered_df(filtered_df, state_ACNs)
                            assessments_df = pph.get_ACN_filtered_df(assessments_df, state_ACNs)
                            person1_df = pph.get_ACN_filtered_df(person1_df, state_ACNs)
                        
                        # Generate titles
                        date_range = f"{months[start_month]} {start_year} - {months[end_month]} {end_year}"
                        
                        cf_title = f"Contributing Factors / Situations ({date_range})"
                        hf_title = f"Human Factors ({date_range})"
                        
                        if enable_state_filter and selected_states:
                            location_info = f" - {len(selected_states)} Locations"
                            cf_title += location_info
                            hf_title += location_info
                        
                        # Extract data for visualizations
                        contributing_factors_dict = vh.get_contributing_factors(assessments_df)
                        person1_human_factors_dict, human_factors_count = vh.get_human_factors_person1(person1_df, assessments_df)
                        
                        # Create visualizations using original visual_helpers.py functions
                        fig1 = None
                        fig2 = None
                        
                        # Generate contributing factors chart exactly like original
                        if contributing_factors_dict:
                            # Sort the dictionary by alphabetical order of keys ignoring case - exactly like original
                            sorted_factors = dict(sorted(contributing_factors_dict.items(), key=lambda item: item[0].lower()))
                            
                            # Original styling
                            dark_mode = False
                            text_color = 'black'
                            grid_color = '#dddddd'
                            bg_color = 'white'
                            ax_bg_color = '#f8f8f8'
                            
                            # Get color map from original function
                            color_map = vh.get_cf_color_map(contributing_factors_dict, dark_mode=dark_mode)
                            
                            # Create bar chart exactly like original
                            x = np.arange(len(sorted_factors))
                            width = 0.8  # wider bars like original

                            # Set larger font sizes exactly like original
                            plt.rcParams.update({
                                'font.size': 12,          # Base font size
                                'axes.titlesize': 16,     # Title font size
                                'axes.labelsize': 14,     # Axis label font size
                                'xtick.labelsize': 11,    # X-tick label font size
                                'ytick.labelsize': 12,    # Y-tick label font size
                                'legend.fontsize': 12,    # Legend font size
                                'figure.titlesize': 18    # Figure title font size
                            })

                            # Create a wider figure with appropriate background - exactly like original
                            fig1, ax1 = plt.subplots(layout='constrained', figsize=(14, 8))
                            fig1.patch.set_facecolor(bg_color)
                            ax1.set_facecolor(ax_bg_color)
                            
                            # Add subtle grid lines exactly like original
                            ax1.grid(axis='y', linestyle='--', alpha=0.3, color=grid_color)
                            
                            # Plot with improved aesthetics exactly like original
                            bars = ax1.bar(x, list(sorted_factors.values()), width, 
                                         color=[color_map.get(factor) for factor in sorted_factors.keys()],
                                         edgecolor=None,
                                         linewidth=0)

                            formatted_labels = vh.get_formatted_labels(list(sorted_factors.keys()))

                            # Set text colors for labels with larger font exactly like original
                            ax1.set_ylabel('Count of Records', color=text_color, fontsize=14)
                            ax1.set_xticks(x, labels=formatted_labels, fontsize=11)
                            plt.setp(ax1.get_xticklabels(), color=text_color)
                            plt.setp(ax1.get_yticklabels(), color=text_color, fontsize=12)
                            
                            # Record count annotation exactly like original
                            record_count = len(assessments_df)
                            n_annotation = f"n={record_count}"
                            annotation_bg = 'white'
                            annotation_edge = 'black'
                            annotation_text_color = text_color
                            ax1.annotate(n_annotation, xy=(0.9, 0.8), xycoords='axes fraction', ha='center', fontsize=12, 
                                        color=annotation_text_color,
                                        bbox=dict(facecolor=annotation_bg, alpha=0.7, edgecolor=annotation_edge))

                            # Annotate each bar with its height exactly like original
                            for bar in bars:
                                height = bar.get_height()
                                ax1.annotate(f'{int(height)}',  
                                            xy=(bar.get_x() + bar.get_width() / 2, height),
                                            xytext=(0, 3),  # 3 points vertical offset
                                            textcoords="offset points",
                                            ha='center', va='bottom', fontsize=10,
                                            color=text_color,
                                            weight='bold')
                            
                            # Improve spines appearance exactly like original
                            for spine in ax1.spines.values():
                                spine.set_color(grid_color)
                                spine.set_linewidth(0.5)
                        
                        # Generate human factors chart exactly like original
                        if person1_human_factors_dict:
                            # Sort exactly like original
                            sorted_factors = dict(sorted(person1_human_factors_dict.items(), key=lambda item: item[0].lower()))

                            # Use original styling exactly
                            dark_mode = False
                            bar_color = "blue"
                            text_color = 'black'
                            grid_color = '#dddddd'
                            bg_color = 'white'
                            ax_bg_color = '#f8f8f8'
                            
                            # Set larger font sizes exactly like original
                            plt.rcParams.update({
                                'font.size': 12,          # Base font size
                                'axes.titlesize': 16,     # Title font size
                                'axes.labelsize': 14,     # Axis label font size
                                'xtick.labelsize': 11,    # X-tick label font size
                                'ytick.labelsize': 12,    # Y-tick label font size
                                'legend.fontsize': 12,    # Legend font size
                                'figure.titlesize': 18    # Figure title font size
                            })

                            # Create bar chart exactly like original
                            x = np.arange(len(sorted_factors))
                            width = 0.8  # wider bars

                            # Create figure exactly like original
                            fig2, ax2 = plt.subplots(layout='constrained', figsize=(14, 8))
                            fig2.patch.set_facecolor(bg_color)
                            ax2.set_facecolor(ax_bg_color)
                            
                            # Add subtle grid lines exactly like original
                            ax2.grid(axis='y', linestyle='--', alpha=0.3, color=grid_color)

                            # Plot exactly like original
                            bars = ax2.bar(x, list(sorted_factors.values()), width, 
                                         color=bar_color,
                                         edgecolor=None,
                                         linewidth=0)

                            formatted_labels = vh.get_formatted_labels(list(sorted_factors.keys()))

                            # Set text colors exactly like original
                            ax2.set_ylabel('Count of Records', color=text_color, fontsize=14)
                            ax2.set_xticks(x, labels=formatted_labels, fontsize=11)
                            plt.setp(ax2.get_xticklabels(), color=text_color)
                            plt.setp(ax2.get_yticklabels(), color=text_color, fontsize=12)
                            
                            # Annotation exactly like original
                            n_annotation = f"n={human_factors_count}"
                            annotation_bg = 'white'
                            annotation_edge = 'black'
                            annotation_text_color = text_color
                            ax2.annotate(n_annotation, xy=(0.9, 0.8), xycoords='axes fraction', ha='center', fontsize=12, 
                                        color=annotation_text_color,
                                        bbox=dict(facecolor=annotation_bg, alpha=0.7, edgecolor=annotation_edge))

                            # Annotate each bar exactly like original
                            for bar in bars:
                                height = bar.get_height()
                                ax2.annotate(f'{int(height)}',  
                                            xy=(bar.get_x() + bar.get_width() / 2, height),
                                            xytext=(0, 3),  # 3 points vertical offset
                                            textcoords="offset points",
                                            ha='center', va='bottom', fontsize=10,
                                            color=text_color,
                                            weight='bold')
                            
                            # Improve spines exactly like original
                            for spine in ax2.spines.values():
                                spine.set_color(grid_color)
                                spine.set_linewidth(0.5)
                        
                        # Store charts in session state
                        st.session_state.generated_charts = {
                            'contributing_factors': fig1,
                            'human_factors': fig2,
                            'summary': {
                                'date_range': date_range,
                                'total_records': len(filtered_df),
                                'states_count': len(selected_states) if enable_state_filter and selected_states else None,
                                'contributing_factors_count': len(contributing_factors_dict),
                                'human_factors_count': human_factors_count
                            }
                        }
                        
                        # Navigate to visualizations page
                        st.session_state.current_page = 'visualizations'
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error generating visualizations: {str(e)}")
                        st.exception(e)
    else:
        st.error("❌ Data not loaded. Please refresh the page.")
        if st.button("🔄 Retry Loading Data"):
            st.session_state.data_loaded = False
            st.rerun()

# Page 2: Visualizations (matching original design)
elif st.session_state.current_page == 'visualizations':
    # Navigation bar
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("← Back to Filters", key="back_to_filters"):
            go_to_page('filters')
            st.rerun()
    
    with col2:
        if st.session_state.last_generation_params:
            params = st.session_state.last_generation_params
            summary_text = f"{months[params['start_month']]} {params['start_year']} - {months[params['end_month']]} {params['end_year']}"
            if params['enable_state_filter'] and params['selected_states']:
                summary_text += f" | {len(params['selected_states'])} States"
            st.markdown(f"<div class='filters-summary'>{summary_text}</div>", unsafe_allow_html=True)
    
    with col3:
        col3a, col3b = st.columns(2)
        with col3a:
            if st.button("BERTopic →", key="to_berttopic"):
                go_to_page('berttopic')
                st.rerun()
        with col3b:
            if st.button("LDA →", key="to_lda"):
                go_to_page('lda')
                st.rerun()
    
    # Display visualizations
    if st.session_state.generated_charts:
        charts = st.session_state.generated_charts
        
        st.markdown('<div class="success-message">✅ Visualizations generated successfully!</div>', 
                  unsafe_allow_html=True)
        
        # Summary info
        summary = charts['summary']
        st.markdown(f"**Analysis Summary:** {summary['date_range']} | {summary['total_records']:,} records")
        
        # Display charts side by side
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="viz-container">', unsafe_allow_html=True)
            st.pyplot(charts['contributing_factors'], use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col2:
            st.markdown('<div class="viz-container">', unsafe_allow_html=True)
            st.pyplot(charts['human_factors'], use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Data insights
        with st.expander("📈 Data Insights", expanded=False):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Incidents", f"{summary['total_records']:,}")
            with col2:
                st.metric("Contributing Factors", summary['contributing_factors_count'])
            with col3:
                st.metric("Human Factors Cases", summary['human_factors_count'])
    else:
        st.warning("No visualizations available. Please go back to filters and generate visualizations.")

# Page 3: BERTopic
elif st.session_state.current_page == 'berttopic':
    # Navigation bar
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("← Back to Visualizations", key="back_to_viz_from_bert"):
            go_to_page('visualizations')
            st.rerun()
    
    with col2:
        if st.session_state.last_generation_params:
            params = st.session_state.last_generation_params
            summary_text = f"{months[params['start_month']]} {params['start_year']} - {months[params['end_month']]} {params['end_year']}"
            st.markdown(f"<div class='filters-summary'>{summary_text}</div>", unsafe_allow_html=True)
    
    with col3:
        if st.button("LDA →", key="bert_to_lda"):
            go_to_page('lda')
            st.rerun()
    
    st.markdown('<div class="viz-container">', unsafe_allow_html=True)
    st.markdown("<h2>BERTopic Visualizations</h2>", unsafe_allow_html=True)
    
    # BERTopic model selection
    berttopic_options = {
        "6 Topics (2012-2017)": "bertopic_visualization_6_topic_2012_to_2017.html",
        "21 Topics (2012-2017)": "bertopic_visualization_21_topic_2012_to_2017.html", 
        "6 Topics (2018-2025)": "bertopic_visualization_6_topic_2018_to_2025.html",
        "6 Topics (2001-2025)": "bertopic_visualization_6_topic_2001_to_2025.html"
    }
    
    selected_model = st.selectbox(
        "Select BERTopic Model:",
        list(berttopic_options.keys()),
        help="Different models trained on different time periods and topic counts"
    )
    
    html_file = f"nlp_visuals/berttopic/{berttopic_options[selected_model]}"
    
    if os.path.exists(html_file):
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        st.components.v1.html(html_content, height=800, scrolling=True)
    else:
        st.error(f"❌ BERTopic visualization file not found: {html_file}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Page 4: LDA
elif st.session_state.current_page == 'lda':
    # Navigation bar
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("← Back to Visualizations", key="back_to_viz_from_lda"):
            go_to_page('visualizations')
            st.rerun()
    
    with col2:
        if st.session_state.last_generation_params:
            params = st.session_state.last_generation_params
            summary_text = f"{months[params['start_month']]} {params['start_year']} - {months[params['end_month']]} {params['end_year']}"
            st.markdown(f"<div class='filters-summary'>{summary_text}</div>", unsafe_allow_html=True)
    
    with col3:
        if st.button("BERTopic →", key="lda_to_bert"):
            go_to_page('berttopic')
            st.rerun()
    
    st.markdown('<div class="viz-container">', unsafe_allow_html=True)
    st.markdown("<h2>LDA Topic Modeling Visualizations</h2>", unsafe_allow_html=True)
    
    # LDA model selection
    lda_options = {
        "2012-2017": "lda_visualization_2012_to_2017.html",
        "2018-2025": "lda_visualization_2018_to_2025.html",
        "2001-2025 (All Years)": "lda_visualization_2001_to_2025.html"
    }
    
    selected_period = st.selectbox(
        "Select LDA Time Period:",
        list(lda_options.keys()),
        help="Different LDA models trained on different time periods"
    )
    
    html_file = f"nlp_visuals/lda/{lda_options[selected_period]}"
    
    if os.path.exists(html_file):
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        st.components.v1.html(html_content, height=800, scrolling=True)
    else:
        st.error(f"❌ LDA visualization file not found: {html_file}")
    
    st.markdown('</div>', unsafe_allow_html=True) 