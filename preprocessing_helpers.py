import pandas as pd 
import numpy as np 
import datetime as dt
import os

def load_data(csv):
    """Load data from CSV file with error handling"""
    if not os.path.exists(csv):
        raise FileNotFoundError(f"CSV file not found: {csv}")
    
    try:
        df = pd.read_csv(csv, header=None, low_memory=False)
        print(f"Successfully loaded CSV file with shape: {df.shape}")
        return df
    except pd.errors.EmptyDataError:
        raise ValueError(f"The CSV file {csv} is empty")
    except pd.errors.ParserError:
        raise ValueError(f"Error parsing CSV file {csv}. The file may be corrupted.")
    except Exception as e:
        raise Exception(f"Error loading CSV file {csv}: {str(e)}")

def set_header(df):
    """Set header from first two rows of dataframe"""
    try:
        # Save the ACN values from rows 1+ before header changes
        acn_values = df.iloc[1:, 0].reset_index(drop=True)
        
        # replace missing info with empty strings 
        row0 = df.iloc[0].fillna('')
        row1 = df.iloc[1].fillna('')
        
        # merge info from first and second row to create header
        df.columns = row1 + " [" + row0 + "]"
        df = df.drop([0, 1]).reset_index(drop=True)
        
        # Rename the ACN column explicitly
        if df.columns[0] == "ACN []":
            df = df.rename(columns={"ACN []": "ACN"})
        elif df.columns[0] == " []":
            df = df.rename(columns={" []": "ACN"})
        
        # If ACN column got lost in the header manipulation, add it back
        if "ACN" not in df.columns:
            df["ACN"] = acn_values
            
        # Verify header creation
        print(f"Header set successfully. Number of columns: {len(df.columns)}")
        print(f"First few columns: {list(df.columns)[:3]}")
        print(f"ACN column exists: {'ACN' in df.columns}")
        
        return df
    except IndexError:
        raise ValueError("DataFrame doesn't have enough rows to set header (needs at least 2 rows)")
    except Exception as e:
        raise Exception(f"Error setting header: {str(e)}")

def delete_minimal_data_columns(df, threshold=10):
    """Delete columns with minimal data"""
    try:
        minimal_data_columns = []
        for col in df.columns:
            if df[col].count() <= threshold:
                minimal_data_columns.append(col)
        
        print(f"Removing {len(minimal_data_columns)} columns with <= {threshold} non-null values")
        
        if minimal_data_columns:
            df = df.drop(columns=minimal_data_columns)
            
        return df, minimal_data_columns
    except Exception as e:
        raise Exception(f"Error deleting minimal data columns: {str(e)}")

def delete_empty_columns(df):
    """Delete completely empty columns"""
    try:
        empty_columns = []
        for col in df.columns:
            if df[col].count() == 0:
                empty_columns.append(col)
        
        print(f"Removing {len(empty_columns)} empty columns")
        
        if empty_columns:
            df = df.drop(columns=empty_columns)
            
        return df, empty_columns
    except Exception as e:
        raise Exception(f"Error deleting empty columns: {str(e)}")

def create_data_subset(df, category):
    """Create a subset dataframe based on category"""
    try:
        new_df = pd.DataFrame()
        for col in df.columns:
            try:
                start_index = col.index("[")
                end_index = col.index("]")
                label = col[start_index+1 : end_index]
                if category in label:
                    new_df[col] = df[col]
            except ValueError:
                # Skip columns without proper formatting
                continue
        
        # Always include the ACN column if it exists in the original dataframe
        if "ACN" in df.columns and "ACN" not in new_df.columns:
            new_df["ACN"] = df["ACN"]
        
        print(f"Created {category} subset with {len(new_df.columns)} columns")
        
        if len(new_df.columns) == 0:
            print(f"WARNING: No columns found for category '{category}'")
        
        print(f"ACN column present in {category} subset: {'ACN' in new_df.columns}")
            
        return new_df
    except Exception as e:
        raise Exception(f"Error creating data subset for {category}: {str(e)}")

def convert_dates(df):
    """Convert date column to datetime objects"""
    try:
        if "Date [Time]" not in df.columns:
            raise ValueError("Date [Time] column not found in dataframe")
        
        # Handle any bad date formats
        try:
            new_col = pd.to_datetime(df["Date [Time]"], format='%Y%m', errors='coerce')
            # Check for NaT values
            nat_count = new_col.isna().sum()
            if nat_count > 0:
                print(f"WARNING: {nat_count} date values could not be parsed and were set to NaT")
                
            df["Date [Time]"] = new_col
            print(f"Converted dates. Date range: {df['Date [Time]'].min()} to {df['Date [Time]'].max()}")
            return df
        except Exception as e:
            raise ValueError(f"Error converting dates: {str(e)}")
    except Exception as e:
        raise Exception(f"Error in convert_dates: {str(e)}")

def get_data_in_date_range(start_month, start_year, end_month, end_year, df):
    """Filter dataframe to specified date range"""
    try:
        if "Date [Time]" not in df.columns:
            raise ValueError("Date [Time] column not found in dataframe")
        
        # Convert string inputs to proper format
        start = pd.to_datetime(start_year + start_month, format='%Y%m')
        end = pd.to_datetime(end_year + end_month, format='%Y%m')
        
        print(f"Filtering data from {start.strftime('%b %Y')} to {end.strftime('%b %Y')}")
        
        # Get counts before filtering
        total_count = len(df)
        
        # Filter the dataframe
        filtered_df = df[(df["Date [Time]"] >= start) & (df["Date [Time]"] <= end)]
        
        # Get counts after filtering
        filtered_count = len(filtered_df)
        
        print(f"Data filtered: {filtered_count} records kept out of {total_count} ({filtered_count/total_count:.1%})")
        
        if filtered_count == 0:
            print("WARNING: No data found for the specified date range!")
            
        return filtered_df
    except Exception as e:
        raise Exception(f"Error filtering data by date range: {str(e)}")
    
# given state dict with {state abbreviation: boolean} return all ACNs that are in requested states (those in dict marked True)
def get_state_ACNs(state_dict, place_df):
    state_ACNs = []
    
    # The correct column name is "State Reference [Place.1]"
    state_column = "State Reference [Place.1]"
    
    # Check if the dataframe has the State Reference column
    if state_column not in place_df.columns:
        print(f"WARNING: '{state_column}' column not found in place_df")
        print(f"Available columns: {sorted(place_df.columns)}")
        return state_ACNs
    
    # Check if ACN column exists
    if "ACN" not in place_df.columns:
        print("WARNING: 'ACN' column not found in place_df")
        return state_ACNs
    
    # Debug information
    print(f"Starting state filtering with {len(state_dict)} states in filter")
    print(f"Total rows in place_df: {len(place_df)}")
    print(f"Selected states: {[s for s in state_dict if state_dict[s]]}")
    
    # Get a list of states that are selected (value is True)
    selected_states = [state for state in state_dict if state_dict[state]]
    
    # Filter using loc for better performance and to avoid iteration
    filtered_df = place_df.loc[place_df[state_column].isin(selected_states)]
    state_ACNs = filtered_df["ACN"].tolist()
    
    print(f"Found {len(state_ACNs)} ACNs from selected states")
    
    # Print some sample ACNs for debugging
    if state_ACNs:
        print(f"Sample ACNs: {state_ACNs[:5]}")
    
    return state_ACNs

# convert airport string from locale format to just airport code (either IATA or ICAO)
def convert_airport_string(airport_string):
    if airport_string is None:
        return []
    elif "." in airport_string:
        index = airport_string.index(".")
        return [airport_string[:index]]
    elif ";" in airport_string:
        index = airport_string.index(";")
        return [airport_string[:index], airport_string[index+1:]]
    else:
        return [airport_string]

# given airport dict with {airport abbreviation: boolean} return all ACNs that are in requested airports (those in dict marked True)
def get_airport_ACNs(airport_dict, place_df):
    airport_ACNs = []
    for key, airport_string in place_df["Locale Reference [Place]"].items():
        airports = convert_airport_string(str(airport_string))
        # at most two airports will be returned
        for airport in airports:
            if airport not in airport_dict:
                continue
            elif airport_dict[airport] is True:
                ACN = place_df.iloc[key]["ACN"]
                airport_ACNs.append(ACN)
                continue 
    return airport_ACNs

def merge_ACNs(ACN_list1, ACN_list2, merge_operation="OR"):
    merge_operation = merge_operation.strip()
    merge_operation = merge_operation.upper()
    return_ACNs = []
    if merge_operation == "AND":
        for ACN in ACN_list1:
            if ACN in ACN_list2:
                return_ACNs.append(ACN)
    elif merge_operation == "OR":
        return_ACNs = ACN_list1
        for ACN in ACN_list2:
            if ACN not in ACN_list1:
                return_ACNs.append(ACN)
    else:
        return "INVALID MERGE OPERATION - ONLY ACCEPT 'AND' or 'OR"
    return return_ACNs

# return a modified df with ACNs in ACN_list
def get_ACN_filtered_df(original_df, ACN_list):
    # Check if ACN column exists
    if "ACN" not in original_df.columns:
        print(f"WARNING: 'ACN' column not found in dataframe with columns: {list(original_df.columns)[:5]}...")
        return original_df
    
    # Debug information
    print(f"Filtering dataframe with {len(original_df)} rows using {len(ACN_list)} ACNs")
    
    # Filter using isin for better performance
    filtered_df = original_df[original_df["ACN"].isin(ACN_list)].reset_index(drop=True)
    
    # Print result information
    print(f"After filtering: {len(filtered_df)} rows retained")
    
    return filtered_df