import pandas as pd
import re

EXCEL_FILE = "BIA_-_2026_-_combined_-_tests.xlsx"
HEADER_ROW_INDEX = 3

def extract_hours_to_numeric(text):
    """
    Helper function to normalize textual timeframes into pure numeric hours.
    Example: "24 Hours" -> 24.0, "1 Month" -> 720.0, "5 Minutes" -> 0.08
    """
    text = str(text).lower().strip()
    if text == 'nan' or text == 'none' or text == '':
        return 9999.0 # Default high penalty for missing data

    # Handle minutes
    if 'minute' in text:
        numbers = re.findall(r'\d+', text)
        return int(numbers[0]) / 60.0 if numbers else 0.0

    # Extract standard numbers
    numbers = re.findall(r'\d+', text)
    if not numbers:
        return 9999.0
        
    val = float(numbers[0])

    # Convert specific terms to hours
    if 'day' in text:
        return val * 24.0
    if 'week' in text:
        return val * 168.0
    if 'month' in text:
        return val * 720.0
    if 'year' in text:
        return val * 8760.0

    return val

def main():
    print("Loading BIA Data & Starting Prioritization Engine...\n")
    
    try:
        # 1. Load Data
        df = pd.read_excel(EXCEL_FILE, header=HEADER_ROW_INDEX)
        df = df.dropna(subset=['Process'])
        
        # 2. Create Numeric Weights for Status
        # Critical gets the highest weight so it's sorted to the top
        status_weights = {'Critical': 3, 'Important': 2, 'Supportive': 1}
        df['Status_Score'] = df['Process Status'].map(status_weights)
        
        # 3. Create Boolean Flag for Time-Critical constraints
        # If the cell is empty or says 'None', it's 0. Otherwise, it gets a 1 boost.
        df['Time_Flag'] = df['Time-Critical'].apply(
            lambda x: 0 if pd.isna(x) or str(x).strip().lower() == 'none' else 1
        )
        
        # 4. Normalize RTO, MAO and RPO to pure numbers
        df['RTO_Numeric'] = df['Process RTO'].apply(extract_hours_to_numeric)
        df['MAO_Numeric'] = df['Process MAO'].apply(extract_hours_to_numeric)
        df['RPO_Numeric'] = df['Process RPO'].apply(extract_hours_to_numeric)

        # 5. THE SORTING ENGINE (Tie-breaker Logic)
        # Priority 1: Status_Score (Descending - Critical first)
        # Priority 2: RTO_Numeric (Ascending - Shortest recovery time first)
        # Priority 3: MAO_Numeric (Ascending - Shortest max outage first)
        # Priority 4: RPO_Numeric (Ascending - Shortest data loss window first)
        # Priority 5: Time_Flag (Descending - True first)
        df_sorted = df.sort_values(
            by=['Status_Score', 'RTO_Numeric', 'MAO_Numeric', 'RPO_Numeric', 'Time_Flag'],
            ascending=[False, True, True, True, False]
        )
        
        # Optional: Display all columns for debugging:
        # pd.set_option('display.max_columns', None)
        # pd.set_option('display.width', 1000)

        # Select columns to display to the user
        display_cols = ['Process', 'Process Status', 'Time-Critical', 'Process RTO', 'Process MAO', 'Process RPO']
        
        print("Final Recovery Prioritization List (Top to Bottom):")
        print("=" * 100)
        print(df_sorted[display_cols].reset_index(drop=True))
        print("=" * 100)
        print("\nLogic applied: Status -> Time-Critical Boost -> Shortest RTO -> Shortest MAO")

    except Exception as e:
        print(f"Error running the engine: {e}")

if __name__ == "__main__":
    main()