import pandas as pd 
import numpy as np 
import preprocessing_helpers as pph
import visual_helpers as vh
import argparse
import sys
import os
import traceback
import json

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Process ASRS runway incursion data and generate visualizations')
    parser.add_argument('--start-month', type=str, required=True, help='Start month (01-12)')
    parser.add_argument('--start-year', type=str, required=True, help='Start year (e.g., 2020)')
    parser.add_argument('--end-month', type=str, required=True, help='End month (01-12)')
    parser.add_argument('--end-year', type=str, required=True, help='End year (e.g., 2025)')
    parser.add_argument('--state-filter', type=str, help='JSON string of state filters {state: bool}')
    parser.add_argument('--dark-mode', action='store_true', help='Generate visualizations optimized for dark mode')
    args = parser.parse_args()

    # Print arguments for debugging
    print(f"Processing data with parameters: start_month={args.start_month}, start_year={args.start_year}, end_month={args.end_month}, end_year={args.end_year}")
    
    # Set dark mode environment variable if specified
    if args.dark_mode:
        os.environ['DARK_MODE'] = '1'
        print("Dark mode enabled for visualizations")
    
    # Parse state filters if provided
    state_filters = None
    if args.state_filter:
        try:
            state_filters = json.loads(args.state_filter)
            print(f"State filtering enabled with {len([s for s in state_filters if state_filters[s]])} states selected")
        except Exception as e:
            print(f"Error parsing state filters: {str(e)}")
            print(f"State filter argument: {args.state_filter}")
    
    try:
        # Check if CSV file exists
        csv_file = 'Jan1990_Jan2025.csv'
        if not os.path.exists(csv_file):
            print(f"ERROR: CSV file not found: {csv_file}")
            print(f"Current working directory: {os.getcwd()}")
            print(f"Files in directory: {os.listdir('.')}")
            sys.exit(1)
            
        # LOAD DATA and SET HEADER
        print(f"Loading data from {csv_file}...")
        try:
            runway_df = pph.load_data(csv_file)
            print(f"Data loaded successfully. Shape: {runway_df.shape}")
            runway_df = pph.set_header(runway_df)
        except Exception as e:
            print(f"ERROR loading or setting header: {str(e)}")
            print(traceback.format_exc())
            sys.exit(1)

        pd.set_option('display.max_columns', None)

        # REMOVE EMPTY COLUMNS and COLUMNS W/ MINIMAL DATA (<= 100 entries)
        print("Preprocessing data...")
        try:
            runway_df, empty_columns = pph.delete_empty_columns(runway_df)
            runway_df, missing_data_columns = pph.delete_minimal_data_columns(runway_df, threshold=100)
        except Exception as e:
            print(f"ERROR preprocessing data: {str(e)}")
            print(traceback.format_exc())
            sys.exit(1)

        # CONVERT DATE ENTRIES TO DATETIME OBJECTS, formatted month/year
        try:
            runway_df = pph.convert_dates(runway_df)
        except Exception as e:
            print(f"ERROR converting dates: {str(e)}")
            print(traceback.format_exc())
            sys.exit(1)

        # Filter data by date range
        start_month = args.start_month
        start_year = args.start_year
        end_month = args.end_month
        end_year = args.end_year
        
        print(f"Filtering data for date range: {start_month}/{start_year} - {end_month}/{end_year}")
        try:
            runway_df = pph.get_data_in_date_range(start_month, start_year, end_month, end_year, runway_df)
            print(f"Filtered dataset has {len(runway_df)} records")
            
            if len(runway_df) == 0:
                print("ERROR: No data found for the specified date range")
                sys.exit(1)
        except Exception as e:
            print(f"ERROR filtering data by date range: {str(e)}")
            print(traceback.format_exc())
            sys.exit(1)

        # SPLIT DATAFRAME INTO MULTIPLE DATAFRAMES
        print("Creating data subsets...")
        try:
            # Add ACN to each dataframe to ensure it's available for filtering
            time_df = pph.create_data_subset(runway_df, 'Time')
            if "ACN" in runway_df.columns and "ACN" not in time_df.columns:
                time_df["ACN"] = runway_df["ACN"]
                
            place_df = pph.create_data_subset(runway_df, 'Place')
            if "ACN" in runway_df.columns and "ACN" not in place_df.columns:
                place_df["ACN"] = runway_df["ACN"]
                
            environment_df = pph.create_data_subset(runway_df, 'Environment')
            if "ACN" in runway_df.columns and "ACN" not in environment_df.columns:
                environment_df["ACN"] = runway_df["ACN"]
                
            aircraft1_df = pph.create_data_subset(runway_df, 'Aircraft 1')
            if "ACN" in runway_df.columns and "ACN" not in aircraft1_df.columns:
                aircraft1_df["ACN"] = runway_df["ACN"]
                
            component_df = pph.create_data_subset(runway_df, 'Component')
            if "ACN" in runway_df.columns and "ACN" not in component_df.columns:
                component_df["ACN"] = runway_df["ACN"]
                
            aircraft2_df = pph.create_data_subset(runway_df, 'Aircraft 2')
            if "ACN" in runway_df.columns and "ACN" not in aircraft2_df.columns:
                aircraft2_df["ACN"] = runway_df["ACN"]
                
            person1_df = pph.create_data_subset(runway_df, 'Person 1')
            if "ACN" in runway_df.columns and "ACN" not in person1_df.columns:
                person1_df["ACN"] = runway_df["ACN"]
                
            person2_df = pph.create_data_subset(runway_df, 'Person 2')
            if "ACN" in runway_df.columns and "ACN" not in person2_df.columns:
                person2_df["ACN"] = runway_df["ACN"]
                
            events_df = pph.create_data_subset(runway_df, 'Events')
            if "ACN" in runway_df.columns and "ACN" not in events_df.columns:
                events_df["ACN"] = runway_df["ACN"]
                
            assessments_df = pph.create_data_subset(runway_df, 'Assessments')
            if "ACN" in runway_df.columns and "ACN" not in assessments_df.columns:
                assessments_df["ACN"] = runway_df["ACN"]
                
            report1_df = pph.create_data_subset(runway_df, 'Report 1')
            if "ACN" in runway_df.columns and "ACN" not in report1_df.columns:
                report1_df["ACN"] = runway_df["ACN"]
                
            report2_df = pph.create_data_subset(runway_df, 'Report 2')
            if "ACN" in runway_df.columns and "ACN" not in report2_df.columns:
                report2_df["ACN"] = runway_df["ACN"]
                
            # Print ACN column status for debugging
            print(f"ACN column check: runway_df: {'ACN' in runway_df.columns}, place_df: {'ACN' in place_df.columns}")
        except Exception as e:
            print(f"ERROR creating data subsets: {str(e)}")
            print(traceback.format_exc())
            sys.exit(1)
        
        # Apply state filtering if provided
        if state_filters and any(state_filters.values()):
            try:
                # Get list of states that are selected (value is True)
                selected_states = {state: True for state in state_filters if state_filters[state]}
                
                if selected_states:
                    print(f"Filtering by {len(selected_states)} states")
                    
                    # Debug: Check what states actually exist in the data
                    state_column = "State Reference [Place.1]"
                    if state_column in place_df.columns:
                        unique_states = place_df[state_column].dropna().unique()
                        print(f"Unique states in data: {sorted(unique_states)}")
                        print(f"Number of unique states: {len(unique_states)}")
                        print(f"Sample states: {list(unique_states)[:10]}")
                        
                        # Check if any of our selected states are in the data
                        states_found = [s for s in selected_states if s in unique_states]
                        print(f"Selected states found in data: {states_found}")
                    else:
                        print(f"WARNING: '{state_column}' column not found")
                        print(f"Available columns in place_df: {sorted(place_df.columns)}")
                    
                    # Get ACNs for records in the selected states
                    state_ACNs = pph.get_state_ACNs(selected_states, place_df)
                    print(f"Found {len(state_ACNs)} records matching the state filter")
                    
                    if len(state_ACNs) == 0:
                        print("ERROR: No data found for the selected states")
                        sys.exit(1)
                    
                    # Filter all dataframes by the ACNs
                    runway_df = pph.get_ACN_filtered_df(runway_df, state_ACNs)
                    time_df = pph.get_ACN_filtered_df(time_df, state_ACNs)
                    place_df = pph.get_ACN_filtered_df(place_df, state_ACNs)
                    environment_df = pph.get_ACN_filtered_df(environment_df, state_ACNs)
                    aircraft1_df = pph.get_ACN_filtered_df(aircraft1_df, state_ACNs)
                    component_df = pph.get_ACN_filtered_df(component_df, state_ACNs)
                    aircraft2_df = pph.get_ACN_filtered_df(aircraft2_df, state_ACNs)
                    person1_df = pph.get_ACN_filtered_df(person1_df, state_ACNs)
                    person2_df = pph.get_ACN_filtered_df(person2_df, state_ACNs)
                    events_df = pph.get_ACN_filtered_df(events_df, state_ACNs)
                    assessments_df = pph.get_ACN_filtered_df(assessments_df, state_ACNs)
                    report1_df = pph.get_ACN_filtered_df(report1_df, state_ACNs)
                    report2_df = pph.get_ACN_filtered_df(report2_df, state_ACNs)
                    
                    print(f"Filtered data has {len(runway_df)} records after state filtering")
            except Exception as e:
                print(f"ERROR applying state filters: {str(e)}")
                print(traceback.format_exc())

        # GENERATE CONTRIBUTING FACTORS AND HUMAN FACTORS DATA VISUALIZATION
        print("Generating visualizations...")
        try:
            # Get titles
            cf_title = vh.get_title(start_month, start_year, end_month, end_year, "Contributing Factors / Situations")
            hf_title = vh.get_title(start_month, start_year, end_month, end_year, "Human Factors")
            
            # Add state filter info to titles if applicable
            if state_filters and any(state_filters.values()):
                selected_states = [state for state in state_filters if state_filters[state]]
                if len(selected_states) < len(state_filters):
                    state_suffix = f" (Filtered to {len(selected_states)} states)"
                    cf_title += state_suffix
                    hf_title += state_suffix
            
            # Extract contributing factors
            contributing_factors_dict = vh.get_contributing_factors(assessments_df)
            if not contributing_factors_dict:
                print("WARNING: No contributing factors found in data")
                
            # Count occurrences of "Human Factors" in contributing factors
            human_factors_count = contributing_factors_dict.get("Human Factors", 0)
            print(f"Human Factors count in contributing factors: {human_factors_count}")
            
            # Extract human factors
            person1_human_factors_dict, _ = vh.get_human_factors_person1(person1_df, assessments_df)
            if not person1_human_factors_dict:
                print("WARNING: No human factors found in data")
            
            # Generate files
            file_suffix = ""
            if state_filters and any(state_filters.values()):
                selected_states = [state for state in state_filters if state_filters[state]]
                if len(selected_states) < len(state_filters):
                    file_suffix = f"_states_{len(selected_states)}"
            
            contributing_factors_file = f'contributing_factors_{start_month}{start_year}-{end_month}{end_year}{file_suffix}.png'
            human_factors_file = f'human_factors_{start_month}{start_year}-{end_month}{end_year}{file_suffix}.png'
            
            # Generate visualizations
            print(f"Generating contributing factors visualization: {contributing_factors_file}")
            vh.contributing_factors_visualization(contributing_factors_dict, n_annotation=f"n={len(assessments_df)}", title=cf_title, save_file=contributing_factors_file)
            
            print(f"Generating human factors visualization: {human_factors_file}")
            vh.human_factors_visualization(person1_human_factors_dict, n_annotation=f"n={human_factors_count}", title=hf_title, save_file=human_factors_file)
            
            # Verify files were created
            if not os.path.exists(contributing_factors_file) or not os.path.exists(human_factors_file):
                print(f"ERROR: Failed to create one or more visualization files")
                print(f"Contributing factors file exists: {os.path.exists(contributing_factors_file)}")
                print(f"Human factors file exists: {os.path.exists(human_factors_file)}")
                sys.exit(1)
                
            print(f"Generated visualizations for date range: {start_month}/{start_year} - {end_month}/{end_year}")
            print(f"Files saved: {contributing_factors_file}, {human_factors_file}")
        except Exception as e:
            print(f"ERROR generating visualizations: {str(e)}")
            print(traceback.format_exc())
            sys.exit(1)
        
        # Ensure all output is flushed
        sys.stdout.flush()
        
    except Exception as e:
        print(f"UNEXPECTED ERROR in data processing: {str(e)}")
        print(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
