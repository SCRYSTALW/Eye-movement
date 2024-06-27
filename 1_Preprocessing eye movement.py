import os
import pandas as pd

# Function to check for any format of 'warm' in text
def contains_warm_variant(text):
    text = str(text).lower()  # Convert to string and lowercase for case-insensitive comparison
    return 'warm' in text

# Define a list of specific columns you want to keep
columns_to_keep = [
    'Recording timestamp',
    'Participant name',
    'Recording duration',
    'Presented Stimulus name',
    'Timeline name',
    'Eye movement type',
    'Eyetracker timestamp',
    'Gaze event duration',
    'Fixation point X',
    'Fixation point Y',
    'Pupil diameter left',
    'Pupil diameter right'
]

# stimuli_to_exclude = [
#     'Eyetracker Calibration',
#     '0. warm up (1)'
#     '0. Warm up',
#     '0. warm up',
#     '00B. warm up (1)',
#     'Warm up (B)',
#     '0C. warm-up (1)',
#     '0.7 warm.up (1)',
#     '0.1 warm_up',
#     '0.1 warm.up',
#     '0.2 warm _up',
#     '0.2 warm.up',
#     '0.3 warm_up',
#     '0.3 warm.up',
#     '0.4 warm_up',
#     '0.4 warm.up',
#     '0.5 warm_up',
#     '0.5 warm.up',
#     '0.6 warm_up',
#     '0.6 warm.up',
#     '0.7 warm_up',
#     '0.7 warm.up',
#     '0.8 warm_up',
#     '0.8 warm.up',
#     '0.9 warm_up',
#     '0.9 warm.up',
#     'Warm up.Ｂ',
# ]
# Specify the folder containing your CSV files
folder = '/Users/sc/Desktop/Eye movement/RCSV/Tobii data/tobii_py/raw copy'

# Loop through all files in the specified folder
for filename in os.listdir(folder):
    if filename.endswith('.csv'):  # Process only CSV files
        file_path = os.path.join(folder, filename)
        df_original = pd.read_csv(file_path)  # Read the CSV file into a DataFrame
        df_filtered = df_original[columns_to_keep]  # Keep only the specified columns

        # Remove rows with 'Eye movement type' as 'EyesNotFound' or 'Unclassified'
        df_filtered = df_filtered[~df_filtered['Eye movement type'].isin(['EyesNotFound', 'Unclassified'])]

        # Apply the function to exclude rows where 'Presented Stimulus name' contains any format of 'warm'
        df_filtered = df_filtered[~df_filtered['Presented Stimulus name'].apply(contains_warm_variant)]
        # df_filtered = df_filtered[~df_filtered['Presented Stimulus name'].isin(stimuli_to_exclude) & df_filtered['Presented Stimulus name'].notna()]
        # Continue with your original filtering
        df_filtered.sort_values(by='Eyetracker timestamp', inplace=True)  # Sort the DataFrame

        # Group the DataFrame for fixation duration calculation
        grouped = df_filtered.groupby(['Fixation point X', 'Fixation point Y'])
        df_filtered['fixation duration'] = grouped['Eyetracker timestamp'].transform(lambda x: x.iloc[-1] - x.iloc[0])

        # Find the index where 'Presented Stimulus name' changes to 'A_black_image'
        split_index = df_filtered[df_filtered['Presented Stimulus name'] == 'A_black_image'].index

        # Check if 'A_black_image' exists and split the DataFrame accordingly
        if not split_index.empty:
            split_index_start = split_index[0]
            split_index_end = split_index[-1]
            df_filtered_normal = df_filtered.loc[:split_index_start]
            df_filtered_mixed = df_filtered.loc[split_index_end + 1:]
        else:
            df_filtered_normal = df_filtered.copy()
            df_filtered_mixed = pd.DataFrame(columns=df_filtered.columns)  # Empty DataFrame if 'A_black_image' not found

        # Reset the index of both DataFrames
        df_filtered_normal.reset_index(drop=True, inplace=True)
        df_filtered_mixed.reset_index(drop=True, inplace=True)

        # Prepare output file paths
        base_name = filename.rsplit('.', 1)[0]  # Remove the file extension from the filename
        output_file_path_normal = os.path.join('/Users/sc/Desktop/Eye movement/RCSV/Data_new_processed_2', f'{base_name}.csv')
        output_file_path_mixed = os.path.join('/Users/sc/Desktop/Eye movement/RCSV/Data_new_processed_2', f'{base_name}_m.csv')

        # Save the filtered DataFrames to CSV files
        df_filtered_normal.to_csv(output_file_path_normal, index=False)
        df_filtered_mixed.to_csv(output_file_path_mixed, index=False)

        print(f"Processed and saved: {filename}")
