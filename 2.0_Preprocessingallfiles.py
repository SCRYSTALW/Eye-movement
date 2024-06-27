# 1. Separate data into 'normal' and 'mixed' categories, and all contrasts
# 2. Remove saccades >=80ms and fixations >1000ms or <=80ms.
# 3. Remove duplicate rows if they have the same gaze event duration.
# 4. Remove saccades that are not preceded and succeeded by fixation events.
# 5. Remove CSV files with less than 50 rows.

import pandas as pd
import os

# Define file paths
file_path = '/Users/sc/Desktop/Eye movement/RCSV/Data_new_processed_final'
output_path_normal = '/Users/sc/Desktop/Eye movement/RCSV/Data_new_processed_final_grade/normal'
output_path_mixed = '/Users/sc/Desktop/Eye movement/RCSV/Data_new_processed_final_grade/mixed'


def process_dataframe(df):
    df = df.copy()  # Create a copy of the DataFrame to avoid SettingWithCopyWarning

    # Drop consecutive duplicates in 'Gaze event duration'
    df = df.loc[df['Gaze event duration'] != df['Gaze event duration'].shift()]

    # Ensure that 'Saccade' column is binary (0 or 1)
    df['Saccade'] = df['Eye movement type'].apply(lambda x: 1 if x == 'Saccade' else 0)

    # Remove consecutive rows with cumulative 'Saccade' greater than 1 until it becomes 1
    while True:
        cumulative_saccade = df['Saccade'].rolling(2).sum()
        if (cumulative_saccade > 1).any():
            index_to_remove = cumulative_saccade[cumulative_saccade > 1].index[0]
            df.drop(index_to_remove, inplace=True)
        else:
            break
    saccades_to_remove = []
    df = df.reset_index(drop=True)
    #
    # # Iterate through the DataFrame
    # for index, row in df.iterrows():
    #     if row['Eye movement type'] == 'Saccade':
    #         # Check if previous and next indices are within bounds
    #         if 0 <= index - 1 < len(df) and 0 <= index + 1 < len(df):
    #             prev_event = df.at[index - 1, 'Eye movement type']
    #             next_event = df.at[index + 1, 'Eye movement type']
    #
    #             if prev_event != 'Fixation' and next_event != 'Fixation':
    #                 saccades_to_remove.append(index)

    # Drop saccades not between fixations
    df.drop(saccades_to_remove, inplace=True)

    # Additional filtering based on 'Gaze event duration'
    df = df[((df['Eye movement type'] == 'Fixation') & (df['Gaze event duration'] >= 80) & (
                df['Gaze event duration'] < 1000)) |
            ((df['Eye movement type'] == 'Saccade') & (df['Gaze event duration'] <= 80))]
    if not df.empty:
        df['Fixation onset'] = (df['Eyetracker timestamp'] - df['Eyetracker timestamp'].iloc[0]) / 1000

    return df


def process_file(file_full_path, output_path):
    df_original = pd.read_csv(file_full_path)
    # Calculate the number of rows in the CSV file
    num_rows = len(df_original)

    # Print the number of rows for this CSV file
    print(f"File: {file_full_path}, Number of Rows: {num_rows}")

    # Check if the number of rows is less than 50
    if num_rows < 50:
        print(f"File: {file_full_path} has less than 50 rows. Deleting...")
        os.remove(file_full_path)
        print(f"File: {file_full_path} deleted.")
        return  # Stop processing this file
    for i in range(1, 10):
        # Filter by 'Presented Stimulus name'
        condition = df_original['Presented Stimulus name'].str.startswith(str(i))
        df_filtered = process_dataframe(df_original[condition].copy())

        # Save the filtered dataframe
        output_filename = f"{os.path.basename(file_full_path).replace('.csv', '')}_contrast_{i}.csv"
        df_filtered.to_csv(os.path.join(output_path, output_filename), index=False)

# Process files
for file in os.listdir(file_path):
    if file.endswith('.csv'):
        file_full_path = os.path.join(file_path, file)
        selected_output_path = output_path_normal if 'NORMAL' in file else output_path_mixed
        process_file(file_full_path, selected_output_path)

print("All files processed.")
