import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

MEAS_DATA_TIMESCALE = 1000 * 1000 * 1000  # ns/s
CLASSES = ['downstairs', 'jogging', 'sitting', 'upstairs', 'walking']
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
    for i in range(len(parsed)):
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


def load_features():
    learned_features = dict()
    for class_name in CLASSES:
        feats = np.zeros([1, 24])
        for file_nr in range(NR_TRAINING_FILES):
            cur_time, cur_data = my_parse_csv('training_files/{}_{}.csv'.format(class_name, file_nr))
            feats += feature_vector(cur_data)
        np.divide(feats, NR_TRAINING_FILES)
        learned_features[class_name] = feats

    return learned_features
