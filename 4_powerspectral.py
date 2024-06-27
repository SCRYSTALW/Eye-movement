# To calculate the Power Spectral Density (PSD) for the fixation and saccade data,
# we will use the Welch method from the scipy.signal library.
# Re-importing necessary libraries as the execution state was reset
import numpy as np
import pandas as pd
from scipy import interpolate
from scipy.fft import fft, fftfreq
import matplotlib.pyplot as plt
from scipy.signal import welch
import os

# Re-load the filtered data
file_path ='/Users/sc/Downloads/6C27high.xlsx'
df_filtered = pd.read_excel(file_path)

# Filter the data for fixation and saccade events
fixations_data = df_filtered[df_filtered['Eye movement type'] == 'Fixation']
saccades_data = df_filtered[df_filtered['Eye movement type'] == 'Saccade']

# Interpolate the 'Gaze event duration' for fixations and saccades
# Assuming that the 'Fixation onset' column is sorted and has no NaNs

# Fixations
y_values_fixations = fixations_data['Gaze event duration'].values
x_values_fixations = fixations_data['Fixation onset'].values / 1000  # Convert from ms to seconds

# Saccades
y_values_saccades = saccades_data['Gaze event duration'].values
x_values_saccades = saccades_data['Fixation onset'].values / 1000  # Convert from ms to seconds
# Interpolate to a sampling rate of 1000Hz
# For fixations
# Define the desired sampling rate
fs = 1000  # Desired sampling rate in Hz
total_duration_fixations = x_values_fixations[-1] - x_values_fixations[0]
interpolated_time_fixations = np.linspace(x_values_fixations[0], x_values_fixations[-1], int(total_duration_fixations * fs))
interpolation_function_fixations = interpolate.interp1d(x_values_fixations, y_values_fixations, kind='linear', fill_value='extrapolate')
interpolated_y_values_fixations = interpolation_function_fixations(interpolated_time_fixations)

# For saccades
total_duration_saccades = x_values_saccades[-1] - x_values_saccades[0]
interpolated_time_saccades = np.linspace(x_values_saccades[0], x_values_saccades[-1], int(total_duration_saccades * fs))
interpolation_function_saccades = interpolate.interp1d(x_values_saccades, y_values_saccades, kind='linear', fill_value='extrapolate')
interpolated_y_values_saccades = interpolation_function_saccades(interpolated_time_saccades)


# Power Spectral Density calculation using Welch's method
# Define parameters for Welch's method
nperseg = 4096  # Length of each segment for FFT
noverlap = nperseg // 2  # Overlap between segments

# For fixations
frequencies_fixations, psd_fixations = welch(
    interpolated_y_values_fixations,
    fs=fs,
    window='hanning',
    nperseg=nperseg,
    noverlap=noverlap,
    scaling='density'
)

# For saccades
frequencies_saccades, psd_saccades = welch(
    interpolated_y_values_saccades,
    fs=fs,
    window='hanning',
    nperseg=nperseg,
    noverlap=noverlap,
    scaling='density'
)

# Extract base file name without extension
base_file_name = os.path.splitext(os.path.basename(file_path))[0]
# Create figure names
fixation_figure_name = base_file_name + '_fixation.png'
saccade_figure_name = base_file_name + '_saccade.png'

# Plotting the PSD results with frequency range 0 to 10 Hz
# For fixations
plt.figure(figsize=(12, 6))
mask_fix_psd = (frequencies_fixations > 0) & (frequencies_fixations <= 10)
plt.plot(frequencies_fixations[mask_fix_psd], psd_fixations[mask_fix_psd])
plt.title('Power Spectral Density of Fixation Data (0-10 Hz)')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Power/Frequency (dB/Hz)')
plt.grid()
plt.savefig(f'/Users/sc/Downloads/{fixation_figure_name}', format='png')

plt.show()


# For saccades
plt.figure(figsize=(12, 6))
mask_sacc_psd = (frequencies_saccades > 0) & (frequencies_saccades <= 10)
plt.plot(frequencies_saccades[mask_sacc_psd], psd_saccades[mask_sacc_psd])
plt.title('Power Spectral Density of Saccade Data (0-10 Hz)')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Power/Frequency (dB/Hz)')
plt.grid()
plt.savefig(f'/Users/sc/Downloads/{saccade_figure_name}', format='png')
plt.show()

