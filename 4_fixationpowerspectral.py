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
data_dir = '/Users/sc/Desktop/Eye movement/data_combined/data_mostupdated——2/normal/contrast_1/grade_5_6'


# Define parameters for interpolation and Welch's method
fs = 1000  # Sampling rate in Hz
nperseg_fixations = 4096  # Larger segment length for fixations

# Lists to store PSD values for all participants
psd_fixations_all = []
# Initialize a variable to store the maximum PSD length
max_psd_length_fixations = 0

# List of all CSV files in the specified directory and its subdirectories
csv_files_list = find_csv_files(data_dir)

# Loop through all CSV files
for csv_file_path in csv_files_list:
    # Load the data
    df = pd.read_csv(csv_file_path)

    # Filter the data for fixation events
    fixations_data = df[df['Eye movement type'] == 'Fixation'].dropna(subset=['Fixation Duration Diff'])


    # Interpolation process
    # Assuming 'Fixation onset' is in milliseconds and is sorted
    if not fixations_data.empty:
        # For fixations
        x_values_fixations = fixations_data['Fixation onset'].values / 1000  # Convert to seconds
        y_values_fixations = fixations_data['Fixation Duration Diff'].values
        if len(x_values_fixations) > 1:  # Check if there is enough data to interpolate
            interp_func_fixations = interpolate.interp1d(x_values_fixations, y_values_fixations, kind='linear', fill_value='extrapolate')
            interpolated_time_fixations = np.arange(x_values_fixations[0], x_values_fixations[-1], 1/fs)
            interpolated_y_values_fixations = interp_func_fixations(interpolated_time_fixations)

            freqs_fixations, psd_fixations = welch(interpolated_y_values_fixations, fs, nperseg=nperseg_fixations,
                                                         noverlap=nperseg_fixations // 2, scaling='density')

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
        _, permuted_psd = welch(avg_permuted_psd, fs, nperseg=nperseg, noverlap=nperseg // 2, scaling='density')
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
# Highlight the significant frequencies with a red line
for i, is_significant in enumerate(significant_fixations):
    if is_significant:
        plt.axvline(freqs_fixations[i], color='pink', linestyle='-', linewidth=1)

# Label the peak frequency
plt.axvline(x=peak_freq, color='green', linestyle='--', label='Peak Frequency')
plt.annotate(f'Peak: {peak_freq:.2f} Hz', xy=(peak_freq, peak_power),
             xytext=(peak_freq + 0.5, peak_power),
             arrowprops=dict(facecolor='green', shrink=0.05),
             horizontalalignment='left', verticalalignment='center')

plt.title('Average Power Spectral Density of Fixation Data (0-10 Hz)')
plt.xlim(0,10)
plt.xlabel('Frequency (Hz)')
plt.ylabel('Power Spectral Density')
plt.legend()
plt.grid()
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

# Define the full path for saving the CSV file for fixation data
csv_save_path_fixations = '/Users/sc/Desktop/Eye movement/5_data_for_plotting/fixation_mixed/grade5——6.csv'

# Saving the fixation DataFrame to a CSV file at the specified path
df_fixations.to_csv(csv_save_path_fixations, index=False)
