import pandas as pd

# Save the filtered DataFrames to Excel files
file_path = '/Users/sc/Downloads/6C27.xlsx'
# Save the filtered DataFrames to Excel files
output_file_path='/Users/sc/Downloads/6C27high.xlsx'

df_original = pd.read_excel(file_path)
# Define a condition to filter rows where 'Presented Stimulus name' starts with '1'
condition = df_original['Presented Stimulus name'].str.contains('^1[A-Za-z]', regex=True)
print(condition)
# Filter the DataFrame using the condition
df_filtered = df_original[condition]

# Remove consecutive rows with the same 'Gaze event duration', keeping the first row
mask = df_filtered['Gaze event duration'] != df_filtered['Gaze event duration'].shift(-1)
df_filtered = df_filtered[mask]

df_filtered['Fixation onset'] = (df_filtered['Eyetracker timestamp'] - df_filtered['Eyetracker timestamp'].iloc[0]) / 1000
df_filtered['Saccade'] = df_filtered['Eye movement type'].apply(lambda x: 1 if x == 'Saccade' else 0)
df_filtered['Fixation Duration Diff'] = df_filtered.loc[df_filtered['Eye movement type'] == 'Fixation', 'Gaze event duration'].diff()

saccades_to_remove = []

# Iterate through the DataFrame to identify saccades that are not preceded and succeeded by fixation events
for index, row in df_filtered.iterrows():
    current_event = row['Eye movement type']

    # Check if the current event is a saccade
    if current_event == 'Saccade':
        # Check the previous and next events
        prev_index = index - 1
        next_index = index + 1

        prev_event = df_filtered.loc[prev_index]['Eye movement type'] if prev_index >= 0 else None
        next_event = df_filtered.loc[next_index]['Eye movement type'] if next_index < len(df_filtered) else None

        # If the previous and next events are not 'Fixation', mark the current saccade for removal
        if prev_event != 'Fixation' and next_event != 'Fixation':
            saccades_to_remove.append(index)

# Remove the identified saccades from the DataFrame
df_filtered.drop(saccades_to_remove, inplace=True)

# Calculate the mean 'Gaze event duration' for 'Eye movement type'=='Fixation'
mean_duration = df_filtered [df_filtered ['Eye movement type'] == 'Fixation']['Gaze event duration'].mean()
mean_saccades = df_filtered [df_filtered ['Eye movement type'] == 'Saccade']['Gaze event duration'].mean()
print("Mean Gaze event duration for 'Fixation':", mean_duration)
print("Mean Gaze event duration for 'Saccade':", mean_saccades )

output_file_path='/Users/sc/Downloads/6C27high.xlsx'

df_filtered.to_excel(output_file_path, index=False)
