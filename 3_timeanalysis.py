import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
import pandas as pd
from scipy import interpolate

file_path ='/Users/sc/Downloads/6C27high.xlsx'

df_filtered = pd.read_excel(file_path)

# Filter the data for fixation events
fixations_data = df_filtered[df_filtered['Eye movement type'] == 'Fixation']

# Assign the 'Fixation Duration Diff' as y-value
y_values = fixations_data['Fixation Duration Diff'].values

# Convert 'Fixation onset' from ms to seconds for x-value
x_values = fixations_data['Fixation onset'].values / 1000

# Interpolate to a sampling rate of 1000Hz
fs = 1000  # Desired sampling rate
total_duration = x_values[-1] - x_values[0]  # Duration of the time series
interpolated_time = np.linspace(x_values[0], x_values[-1], int(total_duration * fs))

# Create a linear interpolation function based on the original data
interpolation_function = interpolate.interp1d(x_values, y_values, kind='linear', fill_value='extrapolate')

# Apply the interpolation function to the interpolated_time points
interpolated_y_values = interpolation_function(interpolated_time)

# Plot the interpolated data
plt.figure(figsize=(10, 5))
plt.plot(interpolated_time, interpolated_y_values, label='Fixation Duration Differences')
plt.xlabel('Fixation onset (s)')
plt.ylabel('Δ Fixation duration (ms)')
plt.title('Fixation duration differences')
plt.legend()
plt.show()
