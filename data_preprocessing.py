import pandas as pd 
import numpy as np 
import preprocessing_helpers as pph
import visual_helpers as vh
import argparse
import sys
import os
import traceback

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Process ASRS runway incursion data and generate visualizations')
    parser.add_argument('--start-month', type=str, required=True, help='Start month (01-12)')
    parser.add_argument('--start-year', type=str, required=True, help='Start year (e.g., 2020)')
    parser.add_argument('--end-month', type=str, required=True, help='End month (01-12)')
    parser.add_argument('--end-year', type=str, required=True, help='End year (e.g., 2025)')
    args = parser.parse_args()

    # Print arguments for debugging
    print(f"Processing data with parameters: start_month={args.start_month}, start_year={args.start_year}, end_month={args.end_month}, end_year={args.end_year}")
    
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
            time_df = pph.create_data_subset(runway_df, 'Time')
            place_df = pph.create_data_subset(runway_df, 'Place')
            environment_df = pph.create_data_subset(runway_df, 'Environment')
            aircraft1_df = pph.create_data_subset(runway_df, 'Aircraft 1')
            component_df = pph.create_data_subset(runway_df, 'Component')
            aircraft2_df = pph.create_data_subset(runway_df, 'Aircraft 2')
            person1_df = pph.create_data_subset(runway_df, 'Person 1')
            person2_df = pph.create_data_subset(runway_df, 'Person 2')
            events_df = pph.create_data_subset(runway_df, 'Events')
            assessments_df = pph.create_data_subset(runway_df, 'Assessments')
            report1_df = pph.create_data_subset(runway_df, 'Report 1')
            report2_df = pph.create_data_subset(runway_df, 'Report 2')
        except Exception as e:
            print(f"ERROR creating data subsets: {str(e)}")
            print(traceback.format_exc())
            sys.exit(1)

        # GENERATE CONTRIBUTING FACTORS AND HUMAN FACTORS DATA VISUALIZATION
        print("Generating visualizations...")
        try:
            # Get titles
            cf_title = vh.get_title(start_month, start_year, end_month, end_year, "Contributing Factors / Situations")
            hf_title = vh.get_title(start_month, start_year, end_month, end_year, "Human Factors")
            
            # Extract contributing factors
            contributing_factors_dict = vh.get_contributing_factors(assessments_df)
            if not contributing_factors_dict:
                print("WARNING: No contributing factors found in data")
            
            # Extract human factors
            person1_human_factors_dict = vh.get_human_factors_person1(person1_df, assessments_df)
            if not person1_human_factors_dict:
                print("WARNING: No human factors found in data")
            
            # Generate files
            contributing_factors_file = f'contributing_factors_{start_month}{start_year}-{end_month}{end_year}.png'
            human_factors_file = f'human_factors_{start_month}{start_year}-{end_month}{end_year}.png'
            
            # Generate visualizations
            print(f"Generating contributing factors visualization: {contributing_factors_file}")
            vh.contributing_factors_visualization(contributing_factors_dict, n_annotation=f"n={len(assessments_df)}", title=cf_title, save_file=contributing_factors_file)
            
            print(f"Generating human factors visualization: {human_factors_file}")
            vh.human_factors_visualization(person1_human_factors_dict, n_annotation=f"n={len(person1_df)}", title=hf_title, save_file=human_factors_file)
            
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
