import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import json
import math
import os

from sklearn.neighbors import KNeighborsClassifier

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


def feature_vectors(time_data, transposed_data, window_length_s):
    un_transposed = np.transpose(transposed_data)

    features = []
    next_window = 1
    begin_index = 0
    for current_index in range(len(time_data)):
        current_time = time_data[current_index] / MEAS_DATA_TIMESCALE
        if current_time > window_length_s * next_window:
            current_data_window = un_transposed[begin_index:current_index]
            transposed_again = np.transpose(current_data_window)
            features.append(feature_vector(transposed_again))
            begin_index = current_index
            next_window += 1

    return features


def get_unwindowed_feature_lists():
    feature_vectors_per_class = dict()
    for cnt_class in range(len(CLASSES)):
        class_name = CLASSES[cnt_class]
        for file_nr in range(NR_TRAINING_FILES):
            print('Training on preprocessed/{}_{}.csv (unwindowed)'.format(class_name, file_nr))
            cur_time, cur_data = my_parse_csv('preprocessed/{}_{}.csv'.format(class_name, file_nr))
            single_feature_vector = feature_vector(cur_data)
            complete_feature_vector_for_current_class = []
            if cnt_class in feature_vectors_per_class:
                complete_feature_vector_for_current_class = feature_vectors_per_class[cnt_class]
            complete_feature_vector_for_current_class.append(single_feature_vector)
            feature_vectors_per_class[cnt_class] = complete_feature_vector_for_current_class
    return feature_vectors_per_class


def get_windowed_feature_lists(window_length_s):
    feature_vectors_per_class = dict()
    for cnt_class in range(len(CLASSES)):
        class_name = CLASSES[cnt_class]
        for file_nr in range(NR_TRAINING_FILES):
            print('Training on preprocessed/{}_{}.csv: '.format(class_name, file_nr), end='')
            cur_time, cur_data = my_parse_csv('preprocessed/{}_{}.csv'.format(class_name, file_nr))
            feature_vector_list = feature_vectors(cur_time, cur_data, window_length_s)
            print('Found {} feature vectors'.format(len(feature_vector_list)))
            complete_feature_vector_for_current_class = []
            if cnt_class in feature_vectors_per_class:
                complete_feature_vector_for_current_class = feature_vectors_per_class[cnt_class]
            complete_feature_vector_for_current_class.extend(feature_vector_list)
            feature_vectors_per_class[cnt_class] = complete_feature_vector_for_current_class
    return feature_vectors_per_class


def filter_feature_vectors_to_common_number(feature_vectors_per_class):
    new_feature_vectors_per_class = dict()

    common_nr_of_feature_vectors = math.inf
    for cnt_class, feature_vector_list in feature_vectors_per_class.items():
        common_nr_of_feature_vectors = min(common_nr_of_feature_vectors, len(feature_vector_list))
    print('Common minimum of feature vectors for all classes={}'.format(common_nr_of_feature_vectors))

    for cnt_class, feature_vector_list in feature_vectors_per_class.items():
        print('Filtering class {}, had {} vectors, '.format(CLASSES[cnt_class], len(feature_vector_list)), end='')
        for i in range(len(feature_vector_list)):
            if i == 0:
                new_feature_vectors_per_class[cnt_class] = [feature_vector_list[0]]
            elif i < common_nr_of_feature_vectors:
                new_feature_vectors_per_class[cnt_class].append(feature_vector_list[i])
            else:
                break
        print('now has {} vectors'.format(len(new_feature_vectors_per_class[cnt_class])))

    return new_feature_vectors_per_class


def export_feature_list(file_path, feature_vectors_per_class):
    exportable_feature_vectors_per_class = dict()

    for cnt_class, current_feature_vector_list in feature_vectors_per_class.items():
        new_feature_vectors = []
        for current_feature_vector in current_feature_vector_list:
            new_feature_vectors.append(current_feature_vector.tolist())  # feature vectors are numpy arrays :S
        exportable_feature_vectors_per_class[CLASSES[cnt_class]] = new_feature_vectors

    with open(file_path, 'w') as file_handle:
        json.dump(exportable_feature_vectors_per_class, file_handle, separators=(',', ':'), sort_keys=True, indent=4)


def get_classifier(feature_vectors_per_class):
    X = []
    Y = []
    for cnt_class, feature_vector_list in feature_vectors_per_class.items():
        for i in range(len(feature_vector_list)):
            X.append(feature_vector_list[i])
            Y.append(cnt_class)  # index of CLASSES is name to class nr mapping!
    print('Using a total of {} feature vectors for KNN'.format(len(Y)))
    calculated_k = math.floor(math.sqrt(len(Y)))
    print('Calculated K={}'.format(calculated_k))
    classifier = KNeighborsClassifier(n_neighbors=calculated_k)
    classifier.fit(X, Y)
    return classifier


def prepare_classification_result_plot(trained_classifier, test_file_path, test_window_time, classifier_name):
    x_time, x_data = my_parse_csv(test_file_path)
    test_vectors = feature_vectors(x_time, x_data, test_window_time)
    # predict/predict_proba expects an array and returns an array of results..
    all_probabilities = trained_classifier.predict_proba(test_vectors)
    transposed_probabilities = np.transpose(all_probabilities)
    window_nr = range(len(all_probabilities))
    fig, ((ax1, ax4), (ax2, ax5), (ax3, ax6)) = plt.subplots(3, 2, constrained_layout=True)
    fig.suptitle('Probabilities for {} with {} classifier'.format(os.path.basename(test_file_path), classifier_name))
    ax1.plot(window_nr, transposed_probabilities[0])
    ax1.set_title(CLASSES[0])
    ax2.plot(window_nr, transposed_probabilities[1])
    ax2.set_title(CLASSES[1])
    ax3.plot(window_nr, transposed_probabilities[2])
    ax3.set_title(CLASSES[2])
    ax4.plot(window_nr, transposed_probabilities[3])
    ax4.set_title(CLASSES[3])
    ax5.plot(window_nr, transposed_probabilities[4])
    ax5.set_title(CLASSES[4])
    ax6.plot(window_nr, transposed_probabilities[5])
    ax6.set_title(CLASSES[5])
    ylimits = [-0.1, 1.1]
    ax1.set_ylim(ylimits)
    ax2.set_ylim(ylimits)
    ax3.set_ylim(ylimits)
    ax4.set_ylim(ylimits)
    ax5.set_ylim(ylimits)
    ax6.set_ylim(ylimits)
