import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

MEAS_DATA_TIMESCALE = 1000 * 1000 * 1000  # ns/s
CLASSES = ['upstairs', 'downstairs', 'walking', 'jogging', 'sitting', 'standing']
NR_TRAINING_FILES = 3


def plot_parsed(name, time_data, transposed_data):
    readable_time = np.divide(time_data, MEAS_DATA_TIMESCALE)
    fig, (ax1, ax2, ax3) = plt.subplots(3)
    fig.suptitle(name)
    ax1.plot(readable_time, transposed_data[0])
    ax1.set_title('x acc')
    ax2.plot(readable_time, transposed_data[1])
    ax2.set_title('y acc')
    ax3.plot(readable_time, transposed_data[2])
    ax3.set_title('z acc')
    plt.show()


def my_parse_csv(file_path):
    parsed = pd.read_csv(file_path)
    time_data = []
    unified_data = []
    first_time = parsed.values[0][0]
    remove_first_time = False
    if first_time / MEAS_DATA_TIMESCALE > 0.25:
        remove_first_time = True  # shift times to 0 if first_time is > 0.25s upon load
    for i in range(len(parsed)):
        if remove_first_time:
            time_data.append(parsed.values[i][0] - first_time)
        else:
            time_data.append(parsed.values[i][0])
        unified_data.append(parsed.values[i][1:])
    return time_data, np.transpose(unified_data)


def feature_vector(transposed_data):
    acc_x_mean = np.mean(transposed_data[0])
    acc_y_mean = np.mean(transposed_data[1])
    acc_z_mean = np.mean(transposed_data[2])
    acc_x_min = np.min(transposed_data[0])
    acc_y_min = np.min(transposed_data[1])
    acc_z_min = np.min(transposed_data[2])
    acc_x_max = np.max(transposed_data[0])
    acc_y_max = np.max(transposed_data[1])
    acc_z_max = np.max(transposed_data[2])
    acc_x_var = np.std(transposed_data[0])
    acc_y_var = np.std(transposed_data[1])
    acc_z_var = np.std(transposed_data[2])
    return np.array([acc_x_mean, acc_y_mean, acc_z_mean,
                     acc_x_min, acc_y_min, acc_z_min,
                     acc_x_max, acc_y_max, acc_z_max,
                     acc_x_var, acc_y_var, acc_z_var])


def feature_vectors(time_data, transposed_data, window_length=0.5):
    un_transposed = np.transpose(transposed_data)

    features = []
    next_window = 1
    begin_index = 0
    for current_index in range(len(time_data)):
        current_time = time_data[current_index] / MEAS_DATA_TIMESCALE
        if current_time > window_length * next_window:
            current_data_window = un_transposed[begin_index:current_index]
            transposed_again = np.transpose(current_data_window)
            features.append(feature_vector(transposed_again))
            begin_index = current_index
            next_window += 1

    return features
