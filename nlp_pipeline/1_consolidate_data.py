import pandas as pd
import glob
import os
from io import StringIO

# Define the path to the crawler directory
crawler_path = '../crawler'
# Find all JSON files in the crawler directory
json_files = glob.glob(os.path.join(crawler_path, '*.json'))

if not json_files:
    print("No JSON files found in the crawler directory. Please run your crawlers first.")
else:
    print(f"Found {len(json_files)} JSON files to process.")
    
    df_list = []

    for file in json_files:
        print(f"Processing {os.path.basename(file)}...")
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # This handles cases where files might be empty
            if not content:
                print(f" - Warning: {os.path.basename(file)} is empty. Skipping.")
                continue

            fixed_content = content.replace('][', ',')
            
            # Use StringIO to handle the string as a file
            df = pd.read_json(StringIO(fixed_content))
            df_list.append(df)
        except Exception as e:
            print(f" - Could not process {file}. Error: {e}")

    if not df_list:
        print("\nNo data was loaded from any of the files.")
    else:
        print("\nConsolidating all data...")
        master_df = pd.concat(df_list, ignore_index=True)

        # --- Data Cleaning and Normalization ---
        if 'job_title' in master_df.columns:
            master_df.rename(columns={'job_title': 'title'}, inplace=True)
        if 'guide_title' in master_df.columns:
            master_df.rename(columns={'guide_title': 'title'}, inplace=True)
        
        master_df.dropna(subset=['title'], inplace=True)
        
        if 'summary' in master_df.columns:
            # This is the updated way to fill missing values
            master_df['summary'] = master_df['summary'].fillna('')
        
        master_df.drop_duplicates(subset=['url'], inplace=True)

        # --- Save the Consolidated Data ---
        output_filename = 'all_data.csv'
        master_df.to_csv(output_filename, index=False)

        print(f"\nSuccessfully consolidated and cleaned data.")
        print(f"Total documents: {len(master_df)}")
        print(f"Data saved to {output_filename}")