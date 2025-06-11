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

# Apply theme CSS with proper dark mode
theme_class = "dark-theme" if st.session_state.get('dark_theme', False) else ""

st.markdown(f"""
<style>
    /* Hide Streamlit default elements */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    /* Apply theme class to root and body */
    html, body, .stApp {{
        background: {"linear-gradient(135deg, #0f1219 0%, #1b2636 35%, #343869 75%, #484c7a 100%)" if st.session_state.get('dark_theme', False) else "#f5f7fa"};
        background-attachment: fixed;
        color: {"#e9e9e9" if st.session_state.get('dark_theme', False) else "#333"};
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        transition: all 0.3s ease;
    }}
    
    /* Sticky header taking full width */
    .main-header {{
        background: {"rgba(15, 18, 25, 0.95)" if st.session_state.get('dark_theme', False) else "#0056b3"};
        color: white;
        padding: 1.5rem 2rem;
        box-shadow: 0 2px 15px rgba(0, 0, 0, 0.4);
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        width: 100%;
        z-index: 1000;
        backdrop-filter: blur(15px);
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-sizing: border-box;
    }}
    
    .main-header h1 {{
        font-size: 2rem;
        font-weight: 300;
        letter-spacing: 1px;
        margin: 0;
        flex-grow: 1;
        text-align: center;
    }}
    
    /* Theme toggle button in header */
    .theme-toggle-btn {{
        background: rgba(255, 255, 255, 0.15) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        padding: 0.4rem 0.8rem !important;
        border-radius: 20px !important;
        font-size: 0.75rem !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
        backdrop-filter: blur(10px) !important;
        min-width: 60px !important;
        font-weight: 500 !important;
    }}
    
    .theme-toggle-btn:hover {{
        background: rgba(255, 255, 255, 0.25) !important;
        transform: translateY(-1px) !important;
    }}
    

    
    /* Add padding to body to account for fixed header */
    .main .block-container {{
        padding-top: 120px !important;
    }}
    
    /* Panels with theme support */
    .date-selector, .filter-section, .viz-container {{
        background: {"rgba(30, 35, 48, 0.8)" if st.session_state.get('dark_theme', False) else "white"};
        padding: 2rem;
        border-radius: 8px;
        box-shadow: {"0 4px 20px rgba(0, 0, 0, 0.4)" if st.session_state.get('dark_theme', False) else "0 2px 10px rgba(0, 0, 0, 0.05)"};
        margin-bottom: 2rem;
        border: 1px solid {"rgba(255, 255, 255, 0.1)" if st.session_state.get('dark_theme', False) else "#eee"};
        transition: all 0.3s;
        backdrop-filter: blur(10px);
    }}
    
    .date-selector h2, .filter-section h3, .viz-container h2 {{
        color: {"#c5cde8" if st.session_state.get('dark_theme', False) else "#0056b3"};
        margin-bottom: 1.5rem;
        font-weight: 300;
    }}
    
    /* Light mode dropdown styling */
    {"" if st.session_state.get('dark_theme', False) else '''
    .stSelectbox [data-baseweb="select"] > div,
    .stSelectbox [data-baseweb="select"] ul,
    .stSelectbox [data-baseweb="select"] li,
    .stSelectbox [data-baseweb="select"] [role="listbox"],
    .stSelectbox [data-baseweb="select"] [role="option"],
    .stSelectbox div[data-baseweb="popover"] > div,
    .stSelectbox div[data-baseweb="popover"] li {
        background: white !important;
        color: #333 !important;
        border-color: #ddd !important;
    }
    
    .stSelectbox [data-baseweb="select"] li:hover,
    .stSelectbox [data-baseweb="select"] [role="option"]:hover,
    .stSelectbox div[data-baseweb="popover"] li:hover {
        background: #f0f7ff !important;
        color: #0056b3 !important;
    }
    
    .stSelectbox [data-baseweb="select"] li[aria-selected="true"],
    .stSelectbox [data-baseweb="select"] [role="option"][aria-selected="true"],
    .stSelectbox div[data-baseweb="popover"] li[aria-selected="true"] {
        background: #e7f0f7 !important;
        color: #0056b3 !important;
    }
    '''}
    
    /* Override ALL Streamlit text colors in dark mode */
    {"" if not st.session_state.get('dark_theme', False) else '''
    .stMarkdown, .stText, p, span, div, h1, h2, h3, h4, h5, h6,
    .stSelectbox label, .stMultiSelect label, .stCheckbox label,
    .stExpander .streamlit-expanderHeader,
    .stMetric .metric-container .metric-label,
    .stInfo, .stSuccess, .stWarning, .stError {
        color: #e9e9e9 !important;
    }
    
    .stSelectbox > div > div,
    .stMultiSelect > div > div {
        background: rgba(20, 26, 40, 0.7) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        color: #e9e9e9 !important;
    }
    
    .stSelectbox > div > div > div,
    .stMultiSelect > div > div > div {
        color: #e9e9e9 !important;
    }
    
    /* Dropdown options styling for dark mode */
    .stSelectbox [data-baseweb="select"] > div,
    .stSelectbox [data-baseweb="select"] ul,
    .stSelectbox [data-baseweb="select"] li,
    .stSelectbox [data-baseweb="select"] [role="listbox"],
    .stSelectbox [data-baseweb="select"] [role="option"],
    .stSelectbox div[data-baseweb="popover"] > div,
    .stSelectbox div[data-baseweb="popover"] li,
    .stSelectbox [data-baseweb="popover"] [data-baseweb="menu"],
    .stSelectbox [data-baseweb="popover"] [data-baseweb="menu"] > ul,
    .stSelectbox [data-baseweb="popover"] [data-baseweb="menu"] li,
    div[data-baseweb="popover"] div[data-baseweb="menu"],
    div[data-baseweb="popover"] div[data-baseweb="menu"] ul,
    div[data-baseweb="popover"] div[data-baseweb="menu"] li,
    div[data-baseweb="popover"] ul[role="listbox"],
    div[data-baseweb="popover"] li[role="option"] {
        background: rgba(20, 26, 40, 0.95) !important;
        color: #e9e9e9 !important;
        border-color: rgba(255, 255, 255, 0.2) !important;
        backdrop-filter: blur(10px) !important;
    }
    
    .stSelectbox [data-baseweb="select"] li:hover,
    .stSelectbox [data-baseweb="select"] [role="option"]:hover,
    .stSelectbox div[data-baseweb="popover"] li:hover,
    .stSelectbox [data-baseweb="popover"] [data-baseweb="menu"] li:hover,
    div[data-baseweb="popover"] div[data-baseweb="menu"] li:hover,
    div[data-baseweb="popover"] li[role="option"]:hover {
        background: rgba(60, 70, 120, 0.8) !important;
        color: #ffffff !important;
    }
    
    .stSelectbox [data-baseweb="select"] li[aria-selected="true"],
    .stSelectbox [data-baseweb="select"] [role="option"][aria-selected="true"],
    .stSelectbox div[data-baseweb="popover"] li[aria-selected="true"],
    .stSelectbox [data-baseweb="popover"] [data-baseweb="menu"] li[aria-selected="true"],
    div[data-baseweb="popover"] div[data-baseweb="menu"] li[aria-selected="true"],
    div[data-baseweb="popover"] li[role="option"][aria-selected="true"] {
        background: rgba(60, 70, 120, 0.9) !important;
        color: #ffffff !important;
    }
    
    /* Additional comprehensive dropdown styling for dark mode */
    [data-baseweb="popover"] {
        backdrop-filter: blur(15px) !important;
    }
    
    [data-baseweb="popover"] > div {
        background: rgba(20, 26, 40, 0.95) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 8px !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6) !important;
    }
    
    [data-baseweb="menu"] {
        background: rgba(20, 26, 40, 0.95) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
    }
    
    [data-baseweb="menu"] ul {
        background: transparent !important;
    }
    
    [data-baseweb="menu"] li {
        background: transparent !important;
        color: #e9e9e9 !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    [data-baseweb="menu"] li:hover {
        background: rgba(60, 70, 120, 0.6) !important;
        color: #ffffff !important;
    }
    
    [data-baseweb="menu"] li:last-child {
        border-bottom: none !important;
    }
    
    .stInfo {
        background: rgba(30, 40, 60, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: #e9e9e9 !important;
    }
    
    .stExpander {
        background: rgba(30, 35, 48, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    .stMetric {
        background: rgba(30, 35, 48, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px;
        padding: 1rem;
    }
    '''}
    
    /* Buttons with theme support for ALL buttons */
    .stButton > button {{
        background: {"linear-gradient(90deg, #3a4a7c 0%, #4b4d7f 100%)" if st.session_state.get('dark_theme', False) else "#0056b3"} !important;
        color: white !important;
        border: none !important;
        padding: 0.75rem 2rem !important;
        border-radius: 4px !important;
        font-weight: bold !important;
        font-size: 1rem !important;
        cursor: pointer !important;
        transition: all 0.3s !important;
        width: 100% !important;
    }}
    
    .stButton > button:hover {{
        background: {"linear-gradient(90deg, #455893 0%, #585a98 100%)" if st.session_state.get('dark_theme', False) else "#003d82"} !important;
        transform: translateY(-1px) !important;
    }}
    
    /* Light mode button styling */
    {"" if st.session_state.get('dark_theme', False) else '''
    .stButton > button {{
        background: #0056b3 !important;
        color: white !important;
        border: none !important;
        padding: 0.75rem 2rem !important;
        border-radius: 4px !important;
        font-weight: bold !important;
        font-size: 1rem !important;
        cursor: pointer !important;
        transition: all 0.3s !important;
        width: 100% !important;
    }}
    
    .stButton > button:hover {{
        background: #003d82 !important;
        transform: translateY(-1px) !important;
    }}
    '''}
    
    /* State chips with theme support */
    .state-chip {{
        background: {"rgba(60, 70, 120, 0.4)" if st.session_state.get('dark_theme', False) else "#e7f0f7"} !important;
        color: {"#c5d0f0" if st.session_state.get('dark_theme', False) else "#0056b3"} !important;
        padding: 0.25rem 0.75rem !important;
        border-radius: 20px !important;
        font-size: 0.85rem !important;
        margin: 0.25rem !important;
        display: inline-block !important;
        transition: all 0.3s !important;
    }}
    
    /* Page navigation with theme support */
    .page-navigation {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 2rem 0;
        padding: 1rem;
        background: {"rgba(30, 35, 48, 0.8)" if st.session_state.get('dark_theme', False) else "white"};
        border-radius: 8px;
        box-shadow: {"0 4px 20px rgba(0, 0, 0, 0.4)" if st.session_state.get('dark_theme', False) else "0 2px 10px rgba(0, 0, 0, 0.05)"};
        border: 1px solid {"rgba(255, 255, 255, 0.1)" if st.session_state.get('dark_theme', False) else "#eee"};
    }}
    
    .filters-summary {{
        color: {"#c5cde8" if st.session_state.get('dark_theme', False) else "#0056b3"};
        font-weight: 500;
    }}
    
    .success-message {{
        background: {"rgba(30, 40, 60, 0.8)" if st.session_state.get('dark_theme', False) else "rgba(240, 248, 255, 0.8)"};
        color: {"#e9e9e9" if st.session_state.get('dark_theme', False) else "#0056b3"};
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border: 1px solid {"rgba(255, 255, 255, 0.1)" if st.session_state.get('dark_theme', False) else "#eee"};
    }}
    
    /* Sidebar styling if enabled */
    .css-1d391kg {{
        background: {"rgba(15, 18, 25, 0.9)" if st.session_state.get('dark_theme', False) else "white"};
    }}
    
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

# Initialize theme state
if 'dark_theme' not in st.session_state:
    st.session_state.dark_theme = False

# Apply theme class to the entire app
theme_class = "dark-theme" if st.session_state.dark_theme else ""

# Theme toggle functionality using sidebar (hidden but functional)
with st.sidebar:
    if st.button(f"{'☀️ Light Mode' if st.session_state.dark_theme else '🌙 Dark Mode'}", key="theme_toggle", help="Toggle theme"):
        old_theme = st.session_state.dark_theme
        st.session_state.dark_theme = not st.session_state.dark_theme
        
        # Only force chart regeneration if we're currently on the visualizations page
        if (st.session_state.current_page == 'visualizations' and 
            st.session_state.get('generated_charts')):
            st.session_state.generated_charts = None
            st.session_state.force_chart_regeneration = True
        
        # Also clear any cached visualization data for BERTopic and LDA pages
        if 'berttopic_viz_cache' in st.session_state:
            st.session_state.berttopic_viz_cache = {}
        if 'lda_viz_cache' in st.session_state:
            st.session_state.lda_viz_cache = {}
        
        st.rerun()

# Global theme change handler - regenerate charts if theme changed and we have data
if (st.session_state.get('force_chart_regeneration', False) and 
    st.session_state.get('last_generation_params') and 
    st.session_state.current_page == 'visualizations'):
    # This will be handled in the visualizations page section
    pass

# CSS to position the theme toggle button below the header
st.markdown("""
<style>
/* Hide the sidebar completely */
.css-1d391kg, [data-testid="stSidebar"] {
    display: none !important;
}

/* Position the theme toggle button from sidebar absolutely */
[data-testid="stSidebar"] .stButton > button {
    position: fixed !important;
    top: 110px !important;
    right: 24px !important;
    z-index: 1001 !important;
    background: rgba(255, 255, 255, 0.15) !important;
    color: white !important;
    border: 1px solid rgba(255, 255, 255, 0.3) !important;
    padding: 0.5rem 1rem !important;
    border-radius: 25px !important;
    font-size: 0.8rem !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;
    backdrop-filter: blur(10px) !important;
    min-width: 120px !important;
    font-weight: 500 !important;
    width: auto !important;
    white-space: nowrap !important;
    display: block !important;
}

[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255, 255, 255, 0.25) !important;
    transform: translateY(-1px) !important;
}

/* Make sidebar theme toggle button visible even though sidebar is hidden */
[data-testid="stSidebar"] .stButton {
    position: fixed !important;
    top: 110px !important;
    right: 24px !important;
    z-index: 1001 !important;
    display: block !important;
}
</style>
""", unsafe_allow_html=True)

# Header with sticky positioning
st.markdown(f"""
<div class="{theme_class}">
<div class="main-header">
    <h1>ASRS Runway Incursion Data Visualization</h1>
</div>
</div>

<script>
// Apply theme to Streamlit app container
document.addEventListener('DOMContentLoaded', function() {{
    const app = document.querySelector('.stApp');
    if (app && "{theme_class}" === "dark-theme") {{
        app.classList.add('dark-theme');
    }} else if (app) {{
        app.classList.remove('dark-theme');
    }}
}});
</script>
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
    st.markdown(f'<div class="{theme_class}">', unsafe_allow_html=True)
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
                            
                            # Apply dark mode styling if enabled
                            dark_mode = st.session_state.get('dark_theme', False)
                            if dark_mode:
                                text_color = '#e9e9e9'
                                grid_color = (1, 1, 1, 0.2)  # RGBA for grid lines
                                bg_color = (0, 0, 0, 0)  # Transparent background
                                ax_bg_color = (0, 0, 0, 0)  # Transparent axes background
                            else:
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
                            if dark_mode:
                                annotation_bg = (30/255, 35/255, 48/255, 0.8)  # RGBA normalized
                                annotation_edge = (1, 1, 1, 0.3)  # RGBA for white with transparency
                            else:
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

                            # Apply dark mode styling if enabled
                            dark_mode = st.session_state.get('dark_theme', False)
                            if dark_mode:
                                bar_color = "#6b73ff"  # Brighter blue for dark mode
                                text_color = '#e9e9e9'
                                grid_color = (1, 1, 1, 0.2)  # RGBA for grid lines
                                bg_color = (0, 0, 0, 0)  # Transparent background
                                ax_bg_color = (0, 0, 0, 0)  # Transparent axes background
                            else:
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
                            if dark_mode:
                                annotation_bg = (30/255, 35/255, 48/255, 0.8)  # RGBA normalized
                                annotation_edge = (1, 1, 1, 0.3)  # RGBA for white with transparency
                            else:
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
                        
                        # Store charts in session state with theme info
                        st.session_state.generated_charts = {
                            'contributing_factors': fig1,
                            'human_factors': fig2,
                            'theme_when_generated': dark_mode,  # Store theme state
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
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close theme div

# Page 2: Visualizations (matching original design)
elif st.session_state.current_page == 'visualizations':
    st.markdown(f'<div class="{theme_class}">', unsafe_allow_html=True)
    # Navigation bar
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("← Back to Filters", key="back_to_filters"):
            go_to_page('filters')
            st.rerun()
    
    with col2:
        # Date display removed as requested
        pass
    
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
    
    # Auto-regenerate charts if theme was changed or if force_chart_regeneration flag is set
    if (st.session_state.get('last_generation_params') and 
        (st.session_state.get('force_chart_regeneration', False) or 
         (st.session_state.get('generated_charts') and 
          st.session_state.generated_charts.get('theme_when_generated') != st.session_state.get('dark_theme', False)))):
        
        current_theme = st.session_state.get('dark_theme', False)
        st.session_state.force_chart_regeneration = False  # Reset the flag
        
        with st.spinner("🎨 Updating charts for current theme..."):
            # Get stored generation parameters
            params = st.session_state.last_generation_params
            
            # Regenerate charts with current theme (reuse the chart generation logic)
            try:
                # Filter data by date range
                filtered_df = pph.get_data_in_date_range(
                    str(params['start_month']).zfill(2), str(params['start_year']),
                    str(params['end_month']).zfill(2), str(params['end_year']),
                    st.session_state.runway_df
                )
                
                # Create data subsets
                place_df = pph.create_data_subset(filtered_df, 'Place')
                assessments_df = pph.create_data_subset(filtered_df, 'Assessments')
                person1_df = pph.create_data_subset(filtered_df, 'Person 1')
                
                # Add ACN columns if needed
                for df in [place_df, assessments_df, person1_df]:
                    if "ACN" in filtered_df.columns and "ACN" not in df.columns:
                        df["ACN"] = filtered_df["ACN"]
                
                # Apply location filtering if it was enabled
                if params['enable_state_filter'] and params['selected_states']:
                    state_filters_dict = {state: True for state in params['selected_states']}
                    state_ACNs = pph.get_state_ACNs(state_filters_dict, place_df)
                    
                    if len(state_ACNs) > 0:
                        filtered_df = pph.get_ACN_filtered_df(filtered_df, state_ACNs)
                        assessments_df = pph.get_ACN_filtered_df(assessments_df, state_ACNs)
                        person1_df = pph.get_ACN_filtered_df(person1_df, state_ACNs)
                
                # Generate titles
                date_range = f"{months[params['start_month']]} {params['start_year']} - {months[params['end_month']]} {params['end_year']}"
                
                # Extract data for visualizations
                contributing_factors_dict = vh.get_contributing_factors(assessments_df)
                person1_human_factors_dict, human_factors_count = vh.get_human_factors_person1(person1_df, assessments_df)
                
                # Create visualizations with current theme
                fig1 = None
                fig2 = None
                
                # Generate contributing factors chart
                if contributing_factors_dict:
                    sorted_factors = dict(sorted(contributing_factors_dict.items(), key=lambda item: item[0].lower()))
                    
                    # Apply current theme styling
                    dark_mode = current_theme
                    if dark_mode:
                        text_color = '#e9e9e9'
                        grid_color = (1, 1, 1, 0.2)
                        bg_color = (0, 0, 0, 0)
                        ax_bg_color = (0, 0, 0, 0)
                    else:
                        text_color = 'black'
                        grid_color = '#dddddd'
                        bg_color = 'white'
                        ax_bg_color = '#f8f8f8'
                    
                    color_map = vh.get_cf_color_map(contributing_factors_dict, dark_mode=dark_mode)
                    
                    x = np.arange(len(sorted_factors))
                    width = 0.8
                    
                    plt.rcParams.update({
                        'font.size': 12, 'axes.titlesize': 16, 'axes.labelsize': 14,
                        'xtick.labelsize': 11, 'ytick.labelsize': 12, 'legend.fontsize': 12,
                        'figure.titlesize': 18
                    })
                    
                    fig1, ax1 = plt.subplots(layout='constrained', figsize=(14, 8))
                    fig1.patch.set_facecolor(bg_color)
                    ax1.set_facecolor(ax_bg_color)
                    ax1.grid(axis='y', linestyle='--', alpha=0.3, color=grid_color)
                    
                    bars = ax1.bar(x, list(sorted_factors.values()), width, 
                                 color=[color_map.get(factor) for factor in sorted_factors.keys()],
                                 edgecolor=None, linewidth=0)
                    
                    formatted_labels = vh.get_formatted_labels(list(sorted_factors.keys()))
                    ax1.set_ylabel('Count of Records', color=text_color, fontsize=14)
                    ax1.set_xticks(x, labels=formatted_labels, fontsize=11)
                    plt.setp(ax1.get_xticklabels(), color=text_color)
                    plt.setp(ax1.get_yticklabels(), color=text_color, fontsize=12)
                    
                    record_count = len(assessments_df)
                    n_annotation = f"n={record_count}"
                    if dark_mode:
                        annotation_bg = (30/255, 35/255, 48/255, 0.8)
                        annotation_edge = (1, 1, 1, 0.3)
                    else:
                        annotation_bg = 'white'
                        annotation_edge = 'black'
                    
                    ax1.annotate(n_annotation, xy=(0.9, 0.8), xycoords='axes fraction', ha='center', fontsize=12, 
                                color=text_color, bbox=dict(facecolor=annotation_bg, alpha=0.7, edgecolor=annotation_edge))
                    
                    for bar in bars:
                        height = bar.get_height()
                        ax1.annotate(f'{int(height)}', xy=(bar.get_x() + bar.get_width() / 2, height),
                                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', 
                                    fontsize=10, color=text_color, weight='bold')
                    
                    for spine in ax1.spines.values():
                        spine.set_color(grid_color)
                        spine.set_linewidth(0.5)
                
                # Generate human factors chart
                if person1_human_factors_dict:
                    sorted_factors = dict(sorted(person1_human_factors_dict.items(), key=lambda item: item[0].lower()))
                    
                    if dark_mode:
                        bar_color = "#6b73ff"
                    else:
                        bar_color = "blue"
                    
                    x = np.arange(len(sorted_factors))
                    width = 0.8
                    
                    fig2, ax2 = plt.subplots(layout='constrained', figsize=(14, 8))
                    fig2.patch.set_facecolor(bg_color)
                    ax2.set_facecolor(ax_bg_color)
                    ax2.grid(axis='y', linestyle='--', alpha=0.3, color=grid_color)
                    
                    bars = ax2.bar(x, list(sorted_factors.values()), width, 
                                 color=bar_color, edgecolor=None, linewidth=0)
                    
                    formatted_labels = vh.get_formatted_labels(list(sorted_factors.keys()))
                    ax2.set_ylabel('Count of Records', color=text_color, fontsize=14)
                    ax2.set_xticks(x, labels=formatted_labels, fontsize=11)
                    plt.setp(ax2.get_xticklabels(), color=text_color)
                    plt.setp(ax2.get_yticklabels(), color=text_color, fontsize=12)
                    
                    n_annotation = f"n={human_factors_count}"
                    ax2.annotate(n_annotation, xy=(0.9, 0.8), xycoords='axes fraction', ha='center', fontsize=12, 
                                color=text_color, bbox=dict(facecolor=annotation_bg, alpha=0.7, edgecolor=annotation_edge))
                    
                    for bar in bars:
                        height = bar.get_height()
                        ax2.annotate(f'{int(height)}', xy=(bar.get_x() + bar.get_width() / 2, height),
                                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', 
                                    fontsize=10, color=text_color, weight='bold')
                    
                    for spine in ax2.spines.values():
                        spine.set_color(grid_color)
                        spine.set_linewidth(0.5)
                
                # Update charts with new theme
                st.session_state.generated_charts = {
                    'contributing_factors': fig1,
                    'human_factors': fig2,
                    'theme_when_generated': current_theme,
                    'summary': params  # Keep existing summary
                }
                
                st.success("✅ Charts updated for current theme!")
                
            except Exception as e:
                st.error(f"❌ Error updating charts: {str(e)}")
    
    # Display visualizations
    if st.session_state.generated_charts:
        charts = st.session_state.generated_charts
        
        st.markdown('<div class="success-message">✅ Visualizations generated successfully!</div>', 
                  unsafe_allow_html=True)
        
        # Summary info
        summary = charts['summary']
        if isinstance(summary, dict) and 'date_range' in summary:
            st.markdown(f"**Analysis Summary:** {summary['date_range']} | {summary['total_records']:,} records")
        elif st.session_state.get('last_generation_params'):
            params = st.session_state.last_generation_params
            date_range = f"{months[params['start_month']]} {params['start_year']} - {months[params['end_month']]} {params['end_year']}"
            st.markdown(f"**Analysis Summary:** {date_range}")
        
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
                if isinstance(summary, dict) and 'total_records' in summary:
                    st.metric("Total Incidents", f"{summary['total_records']:,}")
                else:
                    st.metric("Total Incidents", "N/A")
            with col2:
                if isinstance(summary, dict) and 'contributing_factors_count' in summary:
                    st.metric("Contributing Factors", summary['contributing_factors_count'])
                else:
                    st.metric("Contributing Factors", "N/A")
            with col3:
                if isinstance(summary, dict) and 'human_factors_count' in summary:
                    st.metric("Human Factors Cases", summary['human_factors_count'])
                else:
                    st.metric("Human Factors Cases", "N/A")
    else:
        st.warning("No visualizations available. Please go back to filters and generate visualizations.")
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close theme div

# Page 3: BERTopic
elif st.session_state.current_page == 'berttopic':
    st.markdown(f'<div class="{theme_class}">', unsafe_allow_html=True)
    # Navigation bar
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("← Back to Visualizations", key="back_to_viz_from_bert"):
            go_to_page('visualizations')
            st.rerun()
    
    with col2:
        # Date display removed as requested
        pass
    
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
        
        # Center the BERTopic visualization using a CSS container
        centered_html = f"""
        <div style="
            display: flex;
            justify-content: center;
            align-items: flex-start;
            width: 100%;
            height: 800px;
            overflow: auto;
        ">
            <div style="max-width: 100%; max-height: 100%;">
                {html_content}
            </div>
        </div>
        """
        st.components.v1.html(centered_html, height=800, scrolling=True)
    else:
        st.error(f"❌ BERTopic visualization file not found: {html_file}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)  # Close theme div

# Page 4: LDA
elif st.session_state.current_page == 'lda':
    st.markdown(f'<div class="{theme_class}">', unsafe_allow_html=True)
    # Navigation bar
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("← Back to Visualizations", key="back_to_viz_from_lda"):
            go_to_page('visualizations')
            st.rerun()
    
    with col2:
        # Date display removed as requested  
        pass
    
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
        
        # Display LDA visualization at full width to prevent cutting
        st.components.v1.html(html_content, height=700, scrolling=True)
    else:
        st.error(f"❌ LDA visualization file not found: {html_file}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)  # Close theme div 