# Re-importing necessary libraries after execution state reset
import pandas as pd
import matplotlib.pyplot as plt

# Re-loading the CSV files
df_path_normal = '/Users/sc/Desktop/Eye movement/5_data_for_plotting/saccade_new'
# df_path_scrambled = '/Users/sc/Desktop/Eye movement/4_fixationpowerspectral_mixed.csv'

df_normal = pd.read_csv(df_path_normal)
# df_scrambled = pd.read_csv(df_path_scrambled)
# Plotting the data
plt.figure(figsize=(12, 6))
y_max = max(df_normal['Power Spectral Density'].max(), df_scrambled['Power Spectral Density'].max())

# Plot for normal data
plt.plot(df_normal['Frequency (Hz)'], df_normal['Power Spectral Density'], label='Normal')
plt.plot(df_scrambled['Frequency (Hz)'], df_scrambled['Power Spectral Density'], label='Scrambled')
# Adding significant peak markers for normal data above the highest PSD value
significant_indices_normal = df_normal['Significant Peak'] == True
plt.scatter(df_normal['Frequency (Hz)'][significant_indices_normal],
            [y_max] * significant_indices_normal.sum(),  # Place them at the top of the figure
            color='red', s=20, label='statistically significant frequencies (p<0.05, FDR-corrected)_Normal')
# Adding significant peak markers for scrambled data above the highest PSD value
significant_indices_scrambled = df_scrambled['Significant Peak'] == True
plt.scatter(df_scrambled['Frequency (Hz)'][significant_indices_scrambled],
            [y_max] * significant_indices_scrambled.sum(),  # Place them at the top of the figure
            color='pink', s=20, label='statistically significant frequencies (p<0.05, FDR-corrected)_scrambled')
# Adding labels, title and grid
plt.title('Fixations')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Power Spectral Density')
plt.legend()
plt.xlim(0, 10)

# Show the plot
plt.show()

