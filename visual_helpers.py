import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np
import re

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
    return human_factors_dict

def get_cf_color_map(contributing_factors_dict):
    final_color_map = {}
    predefined_color_map = {
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
    for factor in contributing_factors_dict:
        if factor in predefined_color_map:
            final_color_map[factor] = predefined_color_map[factor]
        else:
            final_color_map[factor] = "black"
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

    color_map = get_cf_color_map(contributing_factors_dict)
    # Create a bar chart
    x = np.arange(len(sorted_factors))
    width = 0.8  # wider bars

    # Create a wider figure
    fig, ax = plt.subplots(layout='constrained', figsize=(14, 8))

    bars = ax.bar(x, list(sorted_factors.values()), width, color=[color_map.get(factor) for factor in sorted_factors.keys()])

    formatted_labels = get_formatted_labels(sorted_factors)

    ax.set_ylabel('Count of Records')
    ax.set_xticks(x, labels=formatted_labels, fontsize=8)
    
    ax.annotate(n_annotation, xy=(0.9, 0.8), xycoords='axes fraction', ha='center', fontsize=8, bbox=dict(facecolor='white', alpha=0.5, edgecolor='black'))

    # Annotate each bar with its height (count)
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{int(height)}',  
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=6)

    # Save to file if a filename is provided
    if save_file:
        plt.savefig(save_file, dpi=300, bbox_inches='tight')
        plt.close()
    else:
        plt.show()

def human_factors_visualization(human_factors_dict, n_annotation, title, save_file=None):
    """
    Visualizes the contributing factors in a bar chart.
    """
    # Sort the dictionary by alphabetical order of keys ignoring case
    sorted_factors = dict(sorted(human_factors_dict.items(), key=lambda item: item[0].lower()))

    # Create a bar chart
    x = np.arange(len(sorted_factors))
    width = 0.8  # wider bars

    # Create a wider figure
    fig, ax = plt.subplots(layout='constrained', figsize=(14, 8))

    bars = ax.bar(x, list(sorted_factors.values()), width, color="blue")

    formatted_labels = get_formatted_labels(sorted_factors)

    ax.set_ylabel('Count of Records')
    ax.set_xticks(x, labels=formatted_labels, fontsize=8)
    
    ax.annotate(n_annotation, xy=(0.9, 0.8), xycoords='axes fraction', ha='center', fontsize=8, bbox=dict(facecolor='white', alpha=0.5, edgecolor='black'))

    # Annotate each bar with its height (count)
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{int(height)}',  
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=6)

    # Save to file if a filename is provided
    if save_file:
        plt.savefig(save_file, dpi=300, bbox_inches='tight')
        plt.close()
    else:
        plt.show()