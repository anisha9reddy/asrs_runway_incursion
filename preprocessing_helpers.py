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
        # replace missing info with empty strings 
        row0 = df.iloc[0].fillna('')
        row1 = df.iloc[1].fillna('')
        
        # merge info from first and second row to create header
        df.columns = row1 + " [" + row0 + "]"
        df = df.drop([0, 1]).reset_index(drop=True)
        
        # Verify header creation
        print(f"Header set successfully. Number of columns: {len(df.columns)}")
        print(f"First few columns: {list(df.columns)[:3]}")
        
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
        
        print(f"Created {category} subset with {len(new_df.columns)} columns")
        
        if len(new_df.columns) == 0:
            print(f"WARNING: No columns found for category '{category}'")
            
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
    