import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import interpolate
import os

def plot_time_analysis(directory, save_path, grades):
    colors = ['red', 'green', 'blue', 'cyan', 'magenta', 'yellow', 'black', 'orange']
    plt.figure(figsize=(10, 5))

    # Initialize a dictionary to hold aggregated data for each grade
    aggregated_data = {f'Grade {grade}': {'x_values': [], 'y_values': []} for grade in grades}

    for grade in grades:
        grade_folder = f'grade_{grade}'
        grade_path = os.path.join(directory, grade_folder)
        if os.path.isdir(grade_path):
            for file in os.listdir(grade_path):
                if file.endswith('.csv'):
                    file_path = os.path.join(grade_path, file)
                    df_filtered = pd.read_csv(file_path)

                    # Filter for fixation data and drop NaN values
                    fixations_data = df_filtered[df_filtered['Eye movement type'] == 'Fixation'].dropna(subset=['Fixation Duration Diff', 'Fixation onset'])
                    y_values = fixations_data['Fixation Duration Diff'].values
                    x_values = fixations_data['Fixation onset'].values / 1000

                    # Aggregate data for the same grade
                    if len(x_values) > 1 and len(y_values) > 1:
                        aggregated_data[f'Grade {grade}']['x_values'].extend(x_values)
                        aggregated_data[f'Grade {grade}']['y_values'].extend(y_values)

    # Interpolate and plot data for each grade
    for grade, data in aggregated_data.items():
        if data['x_values'] and data['y_values']:
            # Sort data by x_values before interpolation to avoid issues
            sorted_indices = np.argsort(data['x_values'])
            sorted_x_values = np.array(data['x_values'])[sorted_indices]
            sorted_y_values = np.array(data['y_values'])[sorted_indices]

            # Perform interpolation
            total_duration = sorted_x_values[-1] - sorted_x_values[0]
            interpolated_time = np.linspace(sorted_x_values[0], sorted_x_values[-1], int(total_duration * 1000))
            interpolation_function = interpolate.interp1d(sorted_x_values, sorted_y_values, kind='linear', fill_value='extrapolate')
            interpolated_y_values = interpolation_function(interpolated_time)

            # Plot
            color = colors[grades.index(int(grade.split()[-1])) % len(colors)]  # Select color based on grade index
            plt.plot(interpolated_time, interpolated_y_values, label=grade, color=color)

    plt.xlabel('Fixation onset (s)')
    plt.ylabel('Δ Fixation duration (ms)')
    plt.title('Combined Fixation Duration Differences by Grade')
    plt.legend()
    plt.savefig(save_path)
    plt.show()

# Define path and call the function for normal 1contrast
normal_1contrast_directory = '/Users/sc/Desktop/Eye movement/datafinal/normal/contrast_1'
normal_1contrast_save_path = '/Users/sc/Desktop/Eye movement/datafinal/normal/combined_contrast_1_plot.png'
plot_time_analysis(normal_1contrast_directory, normal_1contrast_save_path, grades=range(1, 7))  # grades from 1 to 6
