import numpy as np
import pandas as pd
from scipy.signal import welch
from scipy import interpolate
import matplotlib.pyplot as plt
import os
from statsmodels.stats.multitest import multipletests

# Function to find all CSV files in a directory and its subdirectories
def find_csv_files(directory):
    csv_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.csv'):
                csv_files.append(os.path.join(root, file))
    return csv_files

# Directory containing the CSV files
data_dir = '/Users/sc/Desktop/Eye movement/data_highcontrast/data_final_separate/mixed/1contrast/Grade6'

# Define parameters for interpolation and Welch's method
fs = 1000  # Sampling rate in Hz
nperseg_fixations = 529 # Larger segment length for fixations
noverlap_fixations = nperseg_fixations // 2  # Ensure that noverlap is less than nperseg_fixations

# Lists to store PSD values for all participants
psd_fixations_all = []

# Initialize a variable to store the maximum PSD length
max_psd_length_fixations = 0

# List of all CSV files in the specified directory and its subdirectories
csv_files_list = find_csv_files(data_dir)

import os

# ... Your previous code ...

# Loop through all CSV files
for csv_file_path in csv_files_list:
    try:
        # Try loading the data from the CSV file
        df = pd.read_csv(csv_file_path)

        # Check if the required columns are present
        if 'Eye movement type' in df.columns and 'Fixation onset' in df.columns and 'Gaze event duration' in df.columns:
            # Filter the data for fixation events
            fixations_data = df[df['Eye movement type'] == 'Fixation']
            fixations_data = fixations_data.dropna(subset=['Eyetracker timestamp'])

            # Calculate the number of rows in the CSV file
            num_rows = len(df)

            # Print the number of rows for this CSV file
            print(f"File: {csv_file_path}, Number of Rows: {num_rows}")

            # Check if the number of rows is less than 50
            if num_rows < 50:
                print(f"File: {csv_file_path} has less than 50 rows. Deleting...")
                os.remove(csv_file_path)
                print(f"File: {csv_file_path} deleted.")

        else:
            print(f"File: {csv_file_path} is not a valid CSV file. Required columns are missing.")

    except pd.errors.EmptyDataError:
        # Handle the case where the CSV file is empty
        print(f"File: {csv_file_path} is empty.")
    except pd.errors.ParserError:
        # Handle the case where the CSV file is invalid
        print(f"File: {csv_file_path} is not a valid CSV file.")

    # Filter the data for fixation events
    fixations_data = df[df['Eye movement type'] == 'Fixation']
    fixations_data = fixations_data.dropna(subset=['Eyetracker timestamp'])

    # Interpolation process
    # Assuming 'Fixation onset' is in milliseconds and is sorted
    if not fixations_data.empty:
        # For fixations
        x_values_fixations = fixations_data['Fixation onset'].values / 1000  # Convert to seconds
        print(x_values_fixations)
        y_values_fixations = fixations_data['Gaze event duration'].values
        if len(x_values_fixations) > 1:  # Check if there is enough data to interpolate
            interp_func_fixations = interpolate.interp1d(x_values_fixations, y_values_fixations, kind='linear', fill_value='extrapolate')
            interpolated_time_fixations = np.arange(x_values_fixations[0], x_values_fixations[-1], 1/fs)
            interpolated_y_values_fixations = interp_func_fixations(interpolated_time_fixations)

            freqs_fixations, psd_fixations = welch(interpolated_y_values_fixations, fs, nperseg=nperseg_fixations,
                                                   noverlap=noverlap_fixations , scaling='density')

            psd_fixations_all.append(psd_fixations)
            max_psd_length_fixations = max(max_psd_length_fixations, len(psd_fixations))
print(len(csv_files_list))
# Find the maximum length among all PSD arrays
max_psd_length = max_psd_length_fixations

psd_fixations_padded = np.array([np.pad(psd, (0, max_psd_length - len(psd)), 'constant') for psd in psd_fixations_all])

# Averaging the padded PSD arrays
avg_psd_fixations = np.mean(psd_fixations_padded, axis=0)

# Define the number of permutations for permutation testing
num_permutations = 1000

def permutation_test(psd_array, max_psd_length, nperseg):
    # This function now accepts the original array of PSDs (not flattened)
    permutation_psd_values = []
    for _ in range(num_permutations):
        permuted_psds = []
        for psd in psd_array:
            # Shuffle each PSD array and then pad it
            permuted_psd = np.random.permutation(psd)
            permuted_padded_psd = np.pad(permuted_psd, (0, max_psd_length - len(permuted_psd)), 'constant')
            permuted_psds.append(permuted_padded_psd)
        # Calculate the PSD of the averaged permuted data
        avg_permuted_psd = np.mean(permuted_psds, axis=0)
        _, permuted_psd = welch(avg_permuted_psd, fs, nperseg=nperseg_fixations , noverlap=noverlap_fixations , scaling='density')
        permutation_psd_values.append(permuted_psd)
    return np.array(permutation_psd_values)

# Apply permutation tests
permutation_psd_fixations = permutation_test(psd_fixations_all, max_psd_length, nperseg_fixations)

psd_fixations_95th = np.percentile(permutation_psd_fixations, 95, axis=0)

# Adjust the length of psd_fixations_95th to match avg_psd_fixations
psd_fixations_95th_adjusted = np.pad(psd_fixations_95th, (0, len(avg_psd_fixations) - len(psd_fixations_95th)), 'constant')

# Now you can compare the adjusted arrays
significant_fixations = avg_psd_fixations > psd_fixations_95th_adjusted

# Correct for multiple comparisons using FDR
_, fixations_pvals_corrected, _, _ = multipletests(significant_fixations, alpha=0.05, method='fdr_bh')
freq_range_mask = (freqs_fixations >= 0) & (freqs_fixations <= 10)

# Find the peak frequency
peak_freq_index = np.argmax(avg_psd_fixations[freq_range_mask])
peak_freq = freqs_fixations[freq_range_mask][peak_freq_index]
peak_power = avg_psd_fixations[freq_range_mask][peak_freq_index]

# Plotting with significant peaks marked
plt.figure(figsize=(12, 6))
plt.plot(freqs_fixations[freq_range_mask], avg_psd_fixations[freq_range_mask], label='Average Fixations')
for i, is_significant in enumerate(significant_fixations):
    if is_significant:
        plt.axvline(freqs_fixations[i], color='pink', linestyle='-', linewidth=1)
# Label the peak frequency
plt.axvline(x=peak_freq, color='green', linestyle='--', label='Peak Frequency')
plt.annotate(f'Peak: {peak_freq:.2f} Hz', xy=(peak_freq, peak_power),
             xytext=(peak_freq + 0.5, peak_power),
             arrowprops=dict(facecolor='green', shrink=0.05),
             horizontalalignment='left', verticalalignment='center')

plt.title('Average Power Spectral Density of Scrambled Fixation Data (0-10 Hz)')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Power Spectral Density')
plt.legend()
plt.grid()
plt.xlim(0,10)

plt.show()


fixation_data = {
    'Frequency (Hz)': freqs_fixations[freq_range_mask],
    'Power Spectral Density': avg_psd_fixations[freq_range_mask],
    'Significant Peak': significant_fixations[freq_range_mask]
}

# Create a DataFrame for fixation data
df_fixations = pd.DataFrame(fixation_data)

# Find the peak frequency for fixations
peak_freq_fixations = freqs_fixations[np.argmax(avg_psd_fixations)]
peak_psd_fixations = np.max(avg_psd_fixations)
peak_significant_fixations = significant_fixations[np.argmax(avg_psd_fixations)]

# # Adding the peak frequency data to the DataFrame
# df_peak_fixations = pd.DataFrame({'Frequency (Hz)': [peak_freq_fixations],
#                                   'Significant Peak': [peak_significant_fixations]})
#
# # Append the peak frequency row to the DataFrame
# df_final_fixations = pd.concat([df_fixations, df_peak_fixations], ignore_index=True)

# Define the full path for saving the CSV file for fixation data
csv_save_path_fixations = '/Users/sc/Desktop/Eye movement/4_fixationpowerspectral_mixed_GRADE6.csv'

# Saving the fixation DataFrame to a CSV file at the specified path
df_fixations.to_csv(csv_save_path_fixations, index=False)
