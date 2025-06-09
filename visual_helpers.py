import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np
import re
import os
import sys
import platform

def is_dark_mode():
    """
    Detect if system is in dark mode, returns True if dark mode is active.
    This is a best-effort detection that works on different platforms.
    """
    # Check if an environment variable is set (can be set by the client app)
    if os.environ.get('DARK_MODE') == '1':
        return True
        
    # For macOS
    if platform.system() == 'Darwin':
        try:
            import subprocess
            cmd = 'defaults read -g AppleInterfaceStyle'
            result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
            return result.stdout.strip() == 'Dark'
        except:
            pass
    
    # Default to False if we can't detect
    return False

def get_contributing_factors(assessments_df):
    contributing_factors_dict = {}
    none_count = 0
    for factors_list in assessments_df["Contributing Factors / Situations [Assessments]"]:
        if pd.isna(factors_list):
            none_count += 1
            continue
        factors_list = factors_list.split(";")
        for factor in factors_list:
            factor = factor.strip()
            if factor not in contributing_factors_dict:
                contributing_factors_dict[factor] = 1
            else:
                contributing_factors_dict[factor] += 1
    print("No contributing factors found for", none_count, "records")
    print(len(assessments_df) - none_count, "records have contributing factors")
    return contributing_factors_dict

def get_human_factors_person1(person_df, assessments_df):
    human_factors_dict = {}
    none_count = 0
    human_factors_count = 0
    
    for key, factor in assessments_df["Contributing Factors / Situations [Assessments]"].items():
        if pd.isna(factor):
            continue
        if "Human Factors" in factor:
            human_factors_count += 1
            factors_list = person_df["Human Factors [Person 1.7]"][key]
            if pd.isna(factors_list):
                none_count += 1
                continue
            factors_list = factors_list.split(";")
            for factor in factors_list:
                factor = factor.strip()
                if factor not in human_factors_dict:
                    human_factors_dict[factor] = 1
                else:
                    human_factors_dict[factor] += 1
                
    print("No human factors found for", none_count, "records")
    print(human_factors_count - none_count, "records have human factors")
    print("Total records with Human Factors as contributing factor:", human_factors_count)
    
    return human_factors_dict, human_factors_count

def get_cf_color_map(contributing_factors_dict, dark_mode=False):
    final_color_map = {}
    
    # Define color maps for light and dark modes
    light_color_map = {
        "Aircraft": "grey",
        "Airport": "lightblue",
        "Airspace Structure": "orange",
        "ATC Equipment / Nav Facility / Buildings": "navajowhite",
        "Chart Or Publication": "green",
        "Company Policy": "springgreen",
        "Environment - Non Weather Related": "red",
        "Equipment / Tooling": "lightcoral",
        "Human Factors": "blue",
        "Incorrect / Not Installed / Unavailable Part": "black",
        "Manuals": "sienna",
        "Procedure": "darksalmon",
        "Software and Automation": "black",
        "Staffing": "orchid",
        "Weather": "lightpink"
    }
    
    # Enhanced color palette for dark mode with more vibrant, aesthetically pleasing colors
    dark_color_map = {
        "Aircraft": "#8ecae6",  # Light blue
        "Airport": "#219ebc",   # Teal blue
        "Airspace Structure": "#ffb703",  # Amber
        "ATC Equipment / Nav Facility / Buildings": "#fb8500",  # Orange
        "Chart Or Publication": "#70e000",  # Lime green
        "Company Policy": "#38b000",  # Green
        "Environment - Non Weather Related": "#ff5a5f",  # Coral red
        "Equipment / Tooling": "#ef476f",  # Raspberry
        "Human Factors": "#4361ee",  # Vibrant blue
        "Incorrect / Not Installed / Unavailable Part": "#e2e2e2",  # Light gray
        "Manuals": "#f3a738",  # Golden amber
        "Procedure": "#f77f00",  # Burnt orange
        "Software and Automation": "#a8dadc",  # Powder blue
        "Staffing": "#9d4edd",  # Purple
        "Weather": "#ffafcc"    # Pink
    }
    
    # Choose the appropriate color map
    predefined_color_map = dark_color_map if dark_mode else light_color_map
    
    for factor in contributing_factors_dict:
        if factor in predefined_color_map:
            final_color_map[factor] = predefined_color_map[factor]
        else:
            final_color_map[factor] = "#e2e2e2" if dark_mode else "black"
            
    return final_color_map

def get_formatted_labels(sorted_factors):
    formatted_labels = []
    for factor in sorted_factors:
        # Split at " ", "- ", or "/ ", keeping the punctuation
        matches = re.split(r'(?:/ |- | )', factor)
        separators = re.findall(r'(?:/ |- | )', factor)

        # Reconstruct with newlines only at plain spaces
        result = matches[0]
        for sep, word in zip(separators, matches[1:]):
            if sep == " ":
                result += "\n" + word
            else:
                result += sep[0] + word  # Keep "/" or "-" without newline

        formatted_labels.append(result)
    return formatted_labels

def get_title(start_month, start_year, end_month, end_year, title):
    month_dict = {
        "01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr", "05": "May", "06": "June", 
        "07": "July", "08": "Aug", "09": "Sept", "10": "Oct", "11": "Nov", "12": "Dec"
    }
    start_month_string = month_dict[start_month]
    end_month_string = month_dict[end_month]
    date_string = "(" + start_month_string + " " + start_year + " - " + end_month_string + " " + end_year + ")"
    return title + " " + date_string


def contributing_factors_visualization(contributing_factors_dict, n_annotation, title, save_file=None):
    # Sort the dictionary by alphabetical order of keys ignoring case
    sorted_factors = dict(sorted(contributing_factors_dict.items(), key=lambda item: item[0].lower()))

    # Check if dark mode is enabled
    dark_mode = is_dark_mode()
    
    # Set the appropriate style for the plot
    if dark_mode:
        plt.style.use('dark_background')
        # Dark mode styling with blue tint to match the app's theme
        text_color = '#e9e9e9'  # Slightly off-white for better readability
        grid_color = '#2c3e50'  # Darker blue-gray
        bg_color = '#1b2636'    # Dark blue to match app background
        fig_edge_color = '#343869'  # Slightly purplish blue accent
        ax_bg_color = '#1e293b'  # Slightly lighter than bg for contrast
    else:
        plt.style.use('default')
        text_color = 'black'
        grid_color = '#dddddd'
        bg_color = 'white'
        fig_edge_color = '#cccccc'
        ax_bg_color = '#f8f8f8'
        
    # Get color map appropriate for the current mode
    color_map = get_cf_color_map(contributing_factors_dict, dark_mode=dark_mode)
    
    # Create a bar chart
    x = np.arange(len(sorted_factors))
    width = 0.8  # wider bars

    # Set larger font sizes for all text elements
    plt.rcParams.update({
        'font.size': 12,          # Base font size
        'axes.titlesize': 16,     # Title font size
        'axes.labelsize': 14,     # Axis label font size
        'xtick.labelsize': 11,    # X-tick label font size
        'ytick.labelsize': 12,    # Y-tick label font size
        'legend.fontsize': 12,    # Legend font size
        'figure.titlesize': 18    # Figure title font size
    })

    # Create a wider figure with appropriate background
    fig, ax = plt.subplots(layout='constrained', figsize=(14, 8))
    fig.patch.set_facecolor(bg_color)
    ax.set_facecolor(ax_bg_color)
    
    # Add subtle grid lines
    ax.grid(axis='y', linestyle='--', alpha=0.3, color=grid_color)
    
    # Plot with improved aesthetics - using proper color format for matplotlib
    bars = ax.bar(x, list(sorted_factors.values()), width, 
                 color=[color_map.get(factor) for factor in sorted_factors.keys()],
                 edgecolor=(1, 1, 1, 0.1) if dark_mode else None,  # RGBA tuple format
                 linewidth=0.5 if dark_mode else 0)

    formatted_labels = get_formatted_labels(sorted_factors)

    # Set text colors for labels with larger font
    ax.set_ylabel('Count of Records', color=text_color, fontsize=14)
    ax.set_xticks(x, labels=formatted_labels, fontsize=11)
    plt.setp(ax.get_xticklabels(), color=text_color)
    plt.setp(ax.get_yticklabels(), color=text_color, fontsize=12)
    
    # Customize annotation based on theme - with larger font
    annotation_bg = '#1e2a45' if dark_mode else 'white'
    annotation_edge = '#3c4c72' if dark_mode else 'black'
    annotation_text_color = text_color
    ax.annotate(n_annotation, xy=(0.9, 0.8), xycoords='axes fraction', ha='center', fontsize=12, 
                color=annotation_text_color,
                bbox=dict(facecolor=annotation_bg, alpha=0.7, edgecolor=annotation_edge))

    # Annotate each bar with its height (count) with improved contrast and larger font
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{int(height)}',  
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=10,
                    color=text_color,
                    weight='bold')
    
    # Removed title since it's already in the dashboard
    
    # Improve spines appearance
    for spine in ax.spines.values():
        spine.set_color(grid_color)
        spine.set_linewidth(0.5)

    # Save to file if a filename is provided
    if save_file:
        plt.savefig(save_file, dpi=300, bbox_inches='tight', facecolor=bg_color)
        plt.close()
    else:
        plt.show()

def human_factors_visualization(human_factors_dict, n_annotation, title, save_file=None):
    """
    Visualizes the human factors in a bar chart.
    """
    # Sort the dictionary by alphabetical order of keys ignoring case
    sorted_factors = dict(sorted(human_factors_dict.items(), key=lambda item: item[0].lower()))

    # Check if dark mode is enabled
    dark_mode = is_dark_mode()
    
    # Set the appropriate style for the plot
    if dark_mode:
        plt.style.use('dark_background')
        bar_color = "#4cc9f0"  # More vibrant cyan blue for dark mode
        # Dark mode styling with blue tint to match the app's theme
        text_color = '#e9e9e9'  # Slightly off-white for better readability
        grid_color = '#2c3e50'  # Darker blue-gray
        bg_color = '#1b2636'    # Dark blue to match app background
        fig_edge_color = '#343869'  # Slightly purplish blue accent
        ax_bg_color = '#1e293b'  # Slightly lighter than bg for contrast
    else:
        plt.style.use('default')
        bar_color = "blue"
        text_color = 'black'
        grid_color = '#dddddd'
        bg_color = 'white'
        fig_edge_color = '#cccccc'
        ax_bg_color = '#f8f8f8'
    
    # Set larger font sizes for all text elements
    plt.rcParams.update({
        'font.size': 12,          # Base font size
        'axes.titlesize': 16,     # Title font size
        'axes.labelsize': 14,     # Axis label font size
        'xtick.labelsize': 11,    # X-tick label font size
        'ytick.labelsize': 12,    # Y-tick label font size
        'legend.fontsize': 12,    # Legend font size
        'figure.titlesize': 18    # Figure title font size
    })

    # Create a bar chart
    x = np.arange(len(sorted_factors))
    width = 0.8  # wider bars

    # Create a wider figure with appropriate background
    fig, ax = plt.subplots(layout='constrained', figsize=(14, 8))
    fig.patch.set_facecolor(bg_color)
    ax.set_facecolor(ax_bg_color)
    
    # Add subtle grid lines
    ax.grid(axis='y', linestyle='--', alpha=0.3, color=grid_color)

    # Plot with improved aesthetics
    bars = ax.bar(x, list(sorted_factors.values()), width, 
                 color=bar_color,
                 edgecolor=(1, 1, 1, 0.1) if dark_mode else None,
                 linewidth=0.5 if dark_mode else 0)

    formatted_labels = get_formatted_labels(sorted_factors)

    # Set text colors for labels with larger font
    ax.set_ylabel('Count of Records', color=text_color, fontsize=14)
    ax.set_xticks(x, labels=formatted_labels, fontsize=11)
    plt.setp(ax.get_xticklabels(), color=text_color)
    plt.setp(ax.get_yticklabels(), color=text_color, fontsize=12)
    
    # Customize annotation based on theme - with larger font
    annotation_bg = '#1e2a45' if dark_mode else 'white'
    annotation_edge = '#3c4c72' if dark_mode else 'black'
    annotation_text_color = text_color
    ax.annotate(n_annotation, xy=(0.9, 0.8), xycoords='axes fraction', ha='center', fontsize=12, 
                color=annotation_text_color,
                bbox=dict(facecolor=annotation_bg, alpha=0.7, edgecolor=annotation_edge))

    # Annotate each bar with its height (count) with improved contrast and larger font
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{int(height)}',  
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=10,
                    color=text_color,
                    weight='bold')
    
    # Removed title since it's already in the dashboard
    
    # Improve spines appearance
    for spine in ax.spines.values():
        spine.set_color(grid_color)
        spine.set_linewidth(0.5)

    # Save to file if a filename is provided
    if save_file:
        plt.savefig(save_file, dpi=300, bbox_inches='tight', facecolor=bg_color)
        plt.close()
    else:
        plt.show()