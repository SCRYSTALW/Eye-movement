import pandas as pd
import os

# Specify the directory paths
file_path_normal = '/Users/sc/Desktop/Eye movement/data_complete/normal/contrast_1/grade_1_2'
file_out='/Users/sc/Desktop/Eye movement/data_renew/normal/contrast_1/grade_1_2'

# Function to process a CSV file and save it to a new location
def process_csv(input_csv_path, output_csv_path):
    df = pd.read_csv(input_csv_path)

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

    # Save the processed DataFrame to a new CSV file
    df.to_csv(output_csv_path, index=False)

# Process CSV files in the normal directory
for file_name in os.listdir(file_path_normal):
    if file_name.endswith('.csv'):
        input_csv_path = os.path.join(file_path_normal, file_name)
        output_csv_path = os.path.join(file_out, file_name)
        process_csv(input_csv_path, output_csv_path)


print("All files processed.")
