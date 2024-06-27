import os
import pandas as pd
import re
# # Define your input directories for 'normal' and 'mixed'
# input_dir_normal = '/Users/sc/Desktop/Eye movement/RCSV/Data_new_processed_separate/normal'
# input_dir_mixed = '/Users/sc/Desktop/Eye movement/RCSV/Data_new_processed_separate/mixed'

# # Define your output directories for 'normal' and 'mixed'
# output_dir_normal = '/Users/sc/Desktop/Eye movement/RCSV/Data_new_processed_final/normal'
# output_dir_mixed = '/Users/sc/Desktop/Eye movement/RCSV/Data_new_processed_final/mixed'

file_path_normal= '/Users/sc/Desktop/Eye movement/data_allcontrasts/normal'
file_path_mixed= '/Users/sc/Desktop/Eye movement/data_allcontrasts/mixed'
output_base_path_normal='/Users/sc/Desktop/Eye movement/data_mostupdated/normal'
output_base_path_mixed='/Users/sc/Desktop/Eye movement/data_mostupdated/mixed'
#
##remove '10' in the file contrast 1

#
#
# # Folder paths
# folder_path_normal = '/Users/sc/Desktop/Eye movement/RCSV/update0/normal'  # Folder containing CSV files
# output_base_path_normal = '/Users/sc/Desktop/Eye movement/RCSV/update1'
#
# # Regex pattern to filter out certain rows based on 'Presented Stimulus name'
# pattern = r'10[a-zA-Z]'  # Matches '10' followed by any letter
#
# # Process each CSV file in the folder
# for file_name in os.listdir(folder_path_normal):
#     # Check if the file is a CSV file
#     if file_name.endswith('.csv'):
#         file_path = os.path.join(folder_path_normal, file_name)  # Full path to the CSV file
#         df_original = pd.read_csv(file_path)  # Read the CSV file into a DataFrame
#
#         # Filter out rows where 'Presented Stimulus name' matches the pattern
#         df_original = df_original[~df_original['Presented Stimulus name'].astype(str).str.contains(pattern)]
#
#         # Keep only rows with the same 'Presented Stimulus name' as in the first row
#         first_stimulus_name = df_original['Presented Stimulus name'].iloc[0]
#         df_2 = df_original[df_original['Presented Stimulus name'] == first_stimulus_name]
#
#         # Construct the output file path and save the filtered DataFrame to a new CSV file
#         output_file_path = os.path.join(output_base_path_normal, file_name)
#         df_2.to_csv(output_file_path, index=False)  # Save without row indices

# # Ensure output directories exist
# os.makedirs(output_dir_normal, exist_ok=True)
# os.makedirs(output_dir_mixed, exist_ok=True)
#
# # Function to process and rename files
# def process_and_rename_files(input_directory, output_directory, prefix):
#     for filename in os.listdir(input_directory):
#         if filename.endswith('.csv'):
#             # Remove 'primary school screen' from the filename if present
#             new_filename = filename.replace('primary school screen', '').strip('_')
#             # Prepend the new prefix and other fixed information
#             new_filename = f"{prefix}_HCPS_{new_filename}"
#
#             # Define full file paths
#             old_file_path = os.path.join(input_directory, filename)
#             new_file_path = os.path.join(output_directory, new_filename)
#
#             # Insert your data processing here if needed, then save
#             # For demonstration, we'll just rename/move without additional processing
#             os.rename(old_file_path, new_file_path)
#             print(f"Renamed and moved file from {old_file_path} to {new_file_path}")
#
# # Process and rename files in 'normal' directory
# process_and_rename_files(input_dir_normal, output_dir_normal, 'NORMAL')
#
# # Process and rename files in 'mixed' directory
# process_and_rename_files(input_dir_mixed, output_dir_mixed, 'MIXED')
#
# print("All files processed and renamed.")

def process_dataframe(df):
    df = df.copy()  # Create a copy of the DataFrame to avoid SettingWithCopyWarning

    # Drop consecutive duplicates in 'Gaze event duration'
    df = df[df['Gaze event duration'] != df['Gaze event duration'].shift()]

    # Convert 'Eye movement type' to binary 'Saccade'
    df['Saccade'] = df['Eye movement type'].apply(lambda x: 1 if x == 'Saccade' else 0)

    # Filter out unwanted saccades and fixations based on duration
    df = df[((df['Eye movement type'] == 'Fixation') & (df['Gaze event duration'] >= 80) & (df['Gaze event duration'] <= 1000)) |
            ((df['Eye movement type'] == 'Saccade') & (df['Gaze event duration'] <= 80))]

    # Calculate 'Fixation Duration Diff' for consecutive fixations
    # First, ensure the calculation is only applied within each fixation by creating a helper series
    fixation_mask = df['Eye movement type'] == 'Fixation'
    df.loc[fixation_mask, 'Fixation Duration Diff'] = df.loc[fixation_mask, 'Gaze event duration'].diff()

    return df

    # Recalculate 'Fixation onset'
    if not df.empty:
        df['Fixation onset'] = (df['Eyetracker timestamp'] - df['Eyetracker timestamp'].iloc[0]) / 1000
    return df


def process_csv(input_csv_path, output_base_path):
    # Parse contrast from file name
    match_contrast = re.search(r'_contrast_(\d+).csv', input_csv_path)
    contrast = match_contrast.group(1) if match_contrast else 'unknown'

    # Parse grade from file name
    parts = input_csv_path.split('_')  # Split the file name by underscore
    print(f"Filename parts: {parts}")  # See how the filename is being split
    grade_segment = parts[3].strip()  # Assuming the fourth segment should contain the grade information
    print(f"Grade segment before taking first character: '{grade_segment}'")  # See the whole segment intended for grade
    grade = grade_segment[0] if grade_segment else 'unknown'  # Safely extract first character
    print(f"Extracted grade: {grade}")

    # Set the new output path based on contrast and grade
    output_csv_path = os.path.join(output_base_path, f'contrast_{contrast}', f'grade_{grade}')
    os.makedirs(output_csv_path, exist_ok=True)  # Create directories if they don't exist

    df_original = pd.read_csv(input_csv_path)
    #
    # first_stimulus_name = df_original['Presented Stimulus name'].iloc[0]
    # df_filtered = df_original[df_original['Presented Stimulus name'] == first_stimulus_name]
    # # Process the filtered dataframe
    # df_processed = process_dataframe(df_filtered)
    # Save the processed dataframe
    final_output_csv_path = os.path.join(output_csv_path, os.path.basename(input_csv_path))
    df_original.to_csv(final_output_csv_path, index=False)
    print(f"Processed file saved to {final_output_csv_path}")

# Process CSV files in the normal and mixed directories
for file_path, output_base_path in [(file_path_normal, output_base_path_normal), (file_path_mixed, output_base_path_mixed)]:
    for file_name in os.listdir(file_path):
        if file_name.endswith('.csv'):
            input_csv_path = os.path.join(file_path, file_name)
            process_csv(input_csv_path, output_base_path)

print("All files processed.")
