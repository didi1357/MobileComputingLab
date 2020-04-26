import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

MEAS_DATA_TIMESCALE = 1000 * 1000 * 1000  # ns/s
CLASSES = ['downstairs', 'jogging', 'sitting', 'upstairs', 'walking']
NR_TRAINING_FILES = 3


def plot_file(name, time_data, unified_data):
    readable_time = np.divide(time_data, MEAS_DATA_TIMESCALE)
    x_acc = []
    y_acc = []
    z_acc = []
    x_rot = []
    y_rot = []
    z_rot = []
    for i in range(len(unified_data)):
        x_acc.append(unified_data[i][0])
        y_acc.append(unified_data[i][1])
        z_acc.append(unified_data[i][2])
        x_rot.append(unified_data[i][3])
        y_rot.append(unified_data[i][4])
        z_rot.append(unified_data[i][5])
    fig, ((ax1, ax4), (ax2, ax5), (ax3, ax6)) = plt.subplots(3, 2)
    fig.suptitle(name)
    ax1.plot(readable_time, x_acc)
    ax1.set_title('x acc')
    ax2.plot(readable_time, y_acc)
    ax2.set_title('y acc')
    ax3.plot(readable_time, z_acc)
    ax3.set_title('z acc')
    ax4.plot(readable_time, x_rot)
    ax4.set_title('x rot')
    ax5.plot(readable_time, y_rot)
    ax5.set_title('y rot')
    ax6.plot(readable_time, z_rot)
    ax6.set_title('z rot')
    plt.show()


def parse_preprocessed(file_name):
    parsed = pd.read_csv('training_preprocessed/' + file_name)
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
    rot_x_mean = np.mean(transposed_data[3])
    rot_y_mean = np.mean(transposed_data[4])
    rot_z_mean = np.mean(transposed_data[5])
    acc_x_min = np.min(transposed_data[0])
    acc_y_min = np.min(transposed_data[1])
    acc_z_min = np.min(transposed_data[2])
    rot_x_min = np.min(transposed_data[3])
    rot_y_min = np.min(transposed_data[4])
    rot_z_min = np.min(transposed_data[5])
    acc_x_max = np.max(transposed_data[0])
    acc_y_max = np.max(transposed_data[1])
    acc_z_max = np.max(transposed_data[2])
    rot_x_max = np.max(transposed_data[3])
    rot_y_max = np.max(transposed_data[4])
    rot_z_max = np.max(transposed_data[5])
    acc_x_var = np.std(transposed_data[0])
    acc_y_var = np.std(transposed_data[1])
    acc_z_var = np.std(transposed_data[2])
    rot_x_var = np.std(transposed_data[3])
    rot_y_var = np.std(transposed_data[4])
    rot_z_var = np.std(transposed_data[5])
    return np.array([acc_x_mean, acc_y_mean, acc_z_mean, rot_x_mean, rot_y_mean, rot_z_mean,
                     acc_x_min, acc_y_min, acc_z_min, rot_x_min, rot_y_min, rot_z_min,
                     acc_x_max, acc_y_max, acc_z_max, rot_x_max, rot_y_max, rot_z_max,
                     acc_x_var, acc_y_var, acc_z_var, rot_x_var, rot_y_var, rot_z_var])


def load_features():
    learned_features = dict()
    for class_name in CLASSES:
        feats = np.zeros([1, 24])
        for file_nr in range(NR_TRAINING_FILES):
            cur_time, cur_data = parse_preprocessed('{}_{}.csv'.format(class_name, file_nr))
            feats += feature_vector(cur_data)
        np.divide(feats, NR_TRAINING_FILES)
        learned_features[class_name] = feats

    return learned_features
