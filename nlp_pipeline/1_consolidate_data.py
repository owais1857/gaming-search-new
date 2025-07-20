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
            
            if not content:
                print(f" - Warning: {os.path.basename(file)} is empty. Skipping.")
                continue

            fixed_content = content.replace('][', ',')
            
            df = pd.read_json(StringIO(fixed_content))
            df_list.append(df)
        except Exception as e:
            print(f" - Could not process {file}. Error: {e}")

    if not df_list:
        print("\nNo data was loaded from any of the files.")
    else:
        print("\nConsolidating all data...")
        master_df = pd.concat(df_list, ignore_index=True)

        # --- CORRECTED Data Cleaning and Normalization ---
        # 1. Coalesce all 'title-like' columns into a single 'title' column
        if 'job_title' in master_df.columns:
            master_df['title'] = master_df['title'].fillna(master_df['job_title'])
        if 'guide_title' in master_df.columns:
            master_df['title'] = master_df['title'].fillna(master_df['guide_title'])
        
        # 2. Drop the old, now redundant columns
        master_df.drop(columns=['job_title', 'guide_title'], errors='ignore', inplace=True)

        # 3. Now that 'title' is consolidated, drop any rows where it's still missing
        master_df.dropna(subset=['title'], inplace=True)
        
        if 'summary' in master_df.columns:
            master_df['summary'] = master_df['summary'].fillna('')
        
        master_df.drop_duplicates(subset=['url'], inplace=True)

        # --- Save the Consolidated Data ---
        output_filename = 'all_data.csv'
        master_df.to_csv(output_filename, index=False)

        print(f"\nSuccessfully consolidated and cleaned data.")
        print(f"Total documents: {len(master_df)}")
        print(f"Data saved to {output_filename}")