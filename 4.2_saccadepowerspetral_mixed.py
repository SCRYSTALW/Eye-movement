import numpy as np
import pandas as pd
from scipy.signal import welch
import os
from statsmodels.stats.multitest import multipletests
import matplotlib.pyplot as plt

# Directory containing the CSV files and subfolders
data_dir = '/Users/sc/Desktop/Eye movement/data_combined/data_mostupdated/mixed/contrast_1/grade_5_6'
def count_csv_files(directory):
    csv_count = 0  # Initialize the count to zero
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.csv'):
                csv_count += 1  # Increment the count for each CSV file found
    return csv_count

# Calculate the number of CSV files in the specified directory and its subdirectories
num_csv_files = count_csv_files(data_dir)

# Print the result
print(f"Number of CSV files: {num_csv_files}")
# Define parameters for interpolation and Welch's method
fs = 2000  # Sampling rate in Hz
nperseg_saccades = 1025# Smaller segment length for saccades

# Lists to store PSD values for all participants
psd_saccades_all = []
max_psd_length_saccades = 0

# Function to find all CSV files in a directory and its subdirectories
def find_csv_files(directory):
    csv_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.csv'):
                csv_files.append(os.path.join(root, file))
    return csv_files

# List of all CSV files in the specified directory and its subdirectories
csv_files_list = find_csv_files(data_dir)
# Loop through all CSV files
for csv_file_path in csv_files_list:
    try:
        # Try loading the data from the CSV file
        df = pd.read_csv(csv_file_path)

        # Filter the data for saccade events and drop NaN values from the relevant column
        saccades_data = df[df['Eye movement type'] == 'Saccade'].dropna(subset=['Eyetracker timestamp'])

        if not saccades_data.empty:
            # For saccades, create a binary array with '1' at saccade onsets
            # Convert 'Fixation onset' to seconds
            saccade_onset_times = saccades_data['Fixation onset'].values / 1000
            # Adjust the values so that the first value is treated as 0
            saccade_onset_times -= saccade_onset_times[0]

            # Determine the total duration from the saccade data
            duration = np.max(saccade_onset_times)  # Updated to use max onset time
            num_samples = int(duration * fs)
            time_series = np.zeros(num_samples)

            # Create a binary time series for saccades
            for saccade_time in saccade_onset_times:
                interp_index = int(saccade_time * fs)
                if 0 <= interp_index < num_samples:
                    time_series[interp_index] = 1  # Mark the onset of a saccade

            # Compute the PSD for the binary time series
            freqs_saccades, psd_saccades = welch(time_series, fs, nperseg=nperseg_saccades, scaling='density')
            psd_saccades_all.append(psd_saccades)
            max_psd_length_saccades = max(max_psd_length_saccades, len(psd_saccades))

    except Exception as e:
        print(f"An error occurred with file {csv_file_path}: {e}")


# Find the maximum length among all PSD arrays
max_psd_length = max_psd_length_saccades

psd_saccades_padded = np.array([np.pad(psd, (0, max_psd_length - len(psd)), 'constant') for psd in psd_saccades_all])
avg_psd_saccades = np.mean(psd_saccades_padded, axis=0)
# Define the number of permutations for permutation testing
num_permutations = 10000
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
        _, permuted_psd = welch(avg_permuted_psd, fs, nperseg=nperseg, noverlap=nperseg // 2, scaling='density')
        permutation_psd_values.append(permuted_psd)
    return np.array(permutation_psd_values)

# Apply permutation tests
permutation_psd_saccades = permutation_test(psd_saccades_all, max_psd_length, nperseg_saccades)
psd_saccades_95th = np.percentile(permutation_psd_saccades, 95, axis=0)
# Adjust the length of psd_fixations_95th to match avg_psd_fixations
psd_saccades_95th_adjusted = np.pad(psd_saccades_95th, (0, len(avg_psd_saccades) - len(psd_saccades_95th)), 'constant')
# Now you can compare the adjusted arrays
significant_saccades = avg_psd_saccades > psd_saccades_95th_adjusted
# Correct for multiple comparisons using FDR
_, saccades_pvals_corrected, _, _ = multipletests(significant_saccades, alpha=0.05, method='fdr_bh')
# Scale the PSD data for saccades
scaled_psd_saccades = avg_psd_saccades * 1e6

# For averaged saccades
plt.figure(figsize=(12, 6))

# Create a boolean mask for the frequency range within (0-10 Hz)
freq_range_mask_saccades = (freqs_saccades >= 0) & (freqs_saccades <= 50)

# Use np.where to find the indices that satisfy the condition
indices_saccades = np.where(freq_range_mask_saccades)
# Apply the indices to both frequency values and PSD values
freqs_saccades_filtered = freqs_saccades[indices_saccades]
scaled_psd_saccades_filtered = scaled_psd_saccades[indices_saccades]
# Now let's find the appropriate y-axis limits
y_min = 0
y_max = np.max(scaled_psd_saccades_filtered)


# Plotting the scaled PSD using freqs_saccades_filtered as x-axis values
plt.plot(freqs_saccades_filtered, scaled_psd_saccades_filtered, label='Average Saccades')
# Assuming significant_saccades is a boolean array indicating significant frequencies
# Mask it with the frequency range mask to get the significant frequencies within the range
significant_freq_mask_saccades = significant_saccades[indices_saccades]
# Plotting the scaled significant peaks
plt.scatter(freqs_saccades_filtered[significant_freq_mask_saccades],
            scaled_psd_saccades_filtered[significant_freq_mask_saccades], color='red', label='Significant Peaks')
plt.xlim(0, 10)
plt.ylim([y_min, y_max])
plt.title('Average Power Spectral Density of Saccade Data (0-10 Hz)')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Power Spectral Density (×10^-6)')
plt.legend()
plt.grid()
plt.axvline(x=freqs_saccades_filtered[np.argmax(scaled_psd_saccades_filtered)], color='green', linestyle='--', label='Peak Frequency')

# Annotate the frequency value at y_max
plt.annotate(f'Freq: {freqs_saccades_filtered[np.argmax(scaled_psd_saccades_filtered)]:.2f} Hz',
             xy=(freqs_saccades_filtered[np.argmax(scaled_psd_saccades_filtered)], y_max),
             xytext=(freqs_saccades_filtered[np.argmax(scaled_psd_saccades_filtered)] + 0.5, y_max * 0.9),
             arrowprops=dict(arrowstyle='->', lw=1.5),
             color='green')
plt.show()



# Collecting data for the DataFrame
data = {
    'Frequency (Hz)': freqs_saccades_filtered,
    'Power Spectral Density (×10^-6)': scaled_psd_saccades_filtered,
    'Significant Peak': significant_freq_mask_saccades
}

# Create a DataFrame
df_saccades = pd.DataFrame(data)

# Define the full path for saving the CSV file for fixation data
csv_save_path_saccades = '/Users/sc/Desktop/Eye movement/g5_6.m.csv'


# Saving the fixation DataFrame to a CSV file at the specified path
df_saccades.to_csv(csv_save_path_saccades, index=False)

