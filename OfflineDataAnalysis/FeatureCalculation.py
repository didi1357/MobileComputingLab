import numpy as np
from Utils import plot_file, CLASSES, parse_preprocessed

NR_TRAINING_FILES = 2


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


learned_features = dict()
for class_name in CLASSES:
    feats = np.zeros([1, 24])
    for file_nr in range(NR_TRAINING_FILES):
        cur_time, cur_data = parse_preprocessed('{}_{}.csv'.format(class_name, file_nr))
        feats += feature_vector(cur_data)
    np.divide(feats, NR_TRAINING_FILES)
    learned_features[class_name] = feats


