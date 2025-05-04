#!/usr/bin/env python3
"""
Test script to verify data processing functionality
"""
import os
import sys
import preprocessing_helpers as pph
import visual_helpers as vh

def main():
    """Test data processing and visualization generation"""
    # Check if CSV file exists
    csv_file = 'Jan1990_Jan2025.csv'
    print(f"Checking for data file: {csv_file}")
    
    if not os.path.exists(csv_file):
        print(f"ERROR: CSV file not found: {csv_file}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Files in directory: {os.listdir('.')}")
        sys.exit(1)
    
    print(f"File exists: {csv_file}, size: {os.path.getsize(csv_file) / (1024*1024):.1f} MB")
    
    # Check if the file is readable
    try:
        with open(csv_file, 'r') as f:
            header = f.readline()
            print(f"File is readable. First line preview: {header[:50]}...")
    except Exception as e:
        print(f"ERROR: Cannot read file: {e}")
        sys.exit(1)
    
    # Test loading the data
    try:
        print("Testing data loading...")
        runway_df = pph.load_data(csv_file)
        print("Data loaded successfully")
        
        # Test setting the header
        print("Testing header setting...")
        runway_df = pph.set_header(runway_df)
        print("Header set successfully")
        
        # Test date filtering with a small range
        print("\nTesting date filtering with 2020-01 to 2020-12...")
        runway_df = pph.convert_dates(runway_df)
        filtered_df = pph.get_data_in_date_range('01', '2020', '12', '2020', runway_df)
        
        # Check if we have results
        if len(filtered_df) == 0:
            print("WARNING: No data found for the 2020 test period")
        else:
            print(f"Found {len(filtered_df)} records for 2020")
            
            # Test visualization generation for a small dataset
            print("\nTesting visualization generation...")
            assessments_df = pph.create_data_subset(filtered_df, 'Assessments')
            person1_df = pph.create_data_subset(filtered_df, 'Person 1')
            
            # Generate test visualizations
            test_file = 'test_contributing_factors.png'
            print(f"Generating test file: {test_file}")
            
            cf_dict = vh.get_contributing_factors(assessments_df)
            if cf_dict:
                vh.contributing_factors_visualization(
                    cf_dict, 
                    n_annotation=f"n={len(assessments_df)}", 
                    title="Test Contributing Factors (2020)",
                    save_file=test_file
                )
                
                if os.path.exists(test_file):
                    print(f"SUCCESS: Test visualization created: {test_file}")
                else:
                    print(f"ERROR: Failed to create test visualization")
            else:
                print("ERROR: No contributing factors data found")
        
        print("\nAll tests completed")
        
    except Exception as e:
        print(f"ERROR during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 