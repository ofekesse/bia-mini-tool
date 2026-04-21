import pandas as pd
import re
import os
import glob
import sys
from google import genai
from dotenv import load_dotenv

load_dotenv()

EXCEL_FILE_PATTERN = "*.xlsx"
HEADER_ROW_INDEX = 3

def extract_hours_to_numeric(text):
    """
    Helper function to normalize textual timeframes into pure numeric hours.
    Example: "24 Hours" -> 24.0, "1 Month" -> 720.0, "5 Minutes" -> 0.08
    """
    text = str(text).lower().strip()
    if text in ['nan', 'none', '']: return 9999.0 # Default high penalty for missing data

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

def choose_excel_file():
    """
    Scans the current directory for Excel files and lets the user choose one.
    """
    # Find all Excel files in the folder
    files = glob.glob(EXCEL_FILE_PATTERN)

    if not files:
        print("No Excel files found in the current directory!")
        sys.exit(1)
    
    print("Available BIA files:")
    for i, file in enumerate(files, start=1):
        print(f"[{i}] {file}")

    # Keep asking until the user makes a valid choice
    while True:
        try:
            choice = int(input("Enter the number of the file you want to use: "))
            if 1 <= choice <= len(files):
                selected_file = files[choice - 1]
                print(f"You selected: {selected_file}\n")
                return selected_file
            else:
                print("Invalid choice. Please select a valid file number.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def get_ai_analysis(sorted_data):
    """Sends the analyzed table to Gemini for GRC insights"""
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    
    # Buildind a structed prompt
    prompt = f"""
    As a Senior GRC Expert, review the following BIA (Business Impact Analysis) data from Teads. 
    My internal prioritization engine has sorted these processes in the following recovery order (from first to recover to last):
    
    Data: {sorted_data.to_dict(orient='records')}

    Please provide your analysis structured in two main parts:

    PART 1: RECOVERY PRIORITY ASSESSMENT & DEVIL'S ADVOCATE
    My internal prioritization engine sorted these processes mathematically based on: Status -> RTO -> MAO -> RPO -> Time-Critical. 
    However, I need you to act as a critical "Devil's Advocate". Do NOT just agree with the math. 
    Based on your industry experience in Ad-Tech:
    1. Are any of these systems misclassified in their initial 'Process Status' or 'RTO'? (e.g., Should a system labeled 'Important' actually be 'Critical'?).
    2. If you were the CISO, would you manually override my engine's final sorting order? If yes, explicitly state your proposed order (1 to 4) and justify the business reasons for the override.

    PART 2: PROCESS ANALYSIS & CONTROLS
    For each process in the list, please provide:
    1. A short summary of the business impact if it fails.
    2. One specific security CONTROL (Preventive, Detective, or Corrective) that could mitigate the risk.
    3. A detailed explanation of why this control is effective for this specific process, considering its RTO, MAO, RPO, and Time-Critical status.

    Format the output clearly with headings.
    """

    print("\nConsulting with AI Expert... Please wait.\n")
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
    )

    return response.text


def main():
    print("Loading BIA Data & Starting Prioritization Engine...\n")
    
    # 0. Let user choose the Excel file
    EXCEL_FILE = choose_excel_file()

    try:
        df = pd.read_excel(EXCEL_FILE, header=HEADER_ROW_INDEX)
        df = df.dropna(subset=['Process'])
        
        # Normalization & Scoring
        status_weights = {'Critical': 3, 'Important': 2, 'Supportive': 1}
        df['Status_Score'] = df['Process Status'].map(status_weights)
        df['RTO_Numeric'] = df['Process RTO'].apply(extract_hours_to_numeric)
        df['MAO_Numeric'] = df['Process MAO'].apply(extract_hours_to_numeric)
        df['RPO_Numeric'] = df['Process RPO'].apply(extract_hours_to_numeric)
        df['Time_Flag'] = df['Time-Critical'].apply(
            lambda x: 0 if pd.isna(x) or str(x).strip().lower() == 'none' else 1
        )

        # THE SORTING ENGINE (Tie-breaker Logic)
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
        display_cols = ['Process', 'Process Status', 'Process RTO', 'Process MAO', 'Process RPO', 'Time-Critical']
        print("\n" + "="*50)
        print("INTERNAL ENGINE ANALYSIS RESULTS:")
        print("\n" + "="*50)
        print(df_sorted[display_cols].reset_index(drop=True))
        
        # AI Integration
        ai_insights = get_ai_analysis(df_sorted[display_cols])
        print("\n" + "="*50)
        print("AI-Generated GRC Insights:")
        print("\n" + "="*50)
        print(ai_insights)

    except Exception as e:
        print(f"Error running the engine: {e}")

if __name__ == "__main__":
    main()