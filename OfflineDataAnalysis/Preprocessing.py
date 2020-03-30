import pandas as pd
import os
from Utils import plot_file, MEAS_DATA_TIMESCALE


def preprocess_csv_data(parsed_data):
    x_data_acc = []
    y_data_acc = []
    z_data_acc = []
    x_data_rot = []
    y_data_rot = []
    z_data_rot = []
    time_data_acc = []
    time_data_rot = []
    first_time = parsed_data.values[0][4]
    for i in range(len(parsed_data)):
        if parsed_data.values[i][0] == 0:
            x_data_acc.append(parsed_data.values[i][1])
            y_data_acc.append(parsed_data.values[i][2])
            z_data_acc.append(parsed_data.values[i][3])
            time_data_acc.append((parsed_data.values[i][4] - first_time))
        if parsed_data.values[i][0] == 1:
            x_data_rot.append(parsed_data.values[i][1])
            y_data_rot.append(parsed_data.values[i][2])
            z_data_rot.append(parsed_data.values[i][3])
            time_data_rot.append((parsed_data.values[i][4] - first_time))
    time_data = []
    unified_data = []
    for cnt_acc in range(len(time_data_acc)):
        for cnt_rot in range(len(time_data_rot)):
            if time_data_acc[cnt_acc] == time_data_rot[cnt_rot]:
                time_data.append(time_data_acc[cnt_acc])
                current_data = [x_data_acc[cnt_acc], y_data_acc[cnt_acc], z_data_acc[cnt_acc],
                                x_data_rot[cnt_rot], y_data_rot[cnt_rot], z_data_rot[cnt_rot]]
                unified_data.append(current_data)
                break
    return time_data, unified_data


# for current_file in os.listdir("training_files"):
#     if current_file.endswith(".csv"):
#         plot_file('training_files/' + current_file)

CURRENT_FILE = 'sitting_1.csv'

parsed = pd.read_csv('training_files/' + CURRENT_FILE)
time, data = preprocess_csv_data(parsed)
plot_file(CURRENT_FILE, time, data)

# START_TIME = 0
# STOP_TIME = START_TIME + 1

# output_path = 'training_preprocessed/' + CURRENT_FILE
# with open(output_path, 'w') as file_handle:
#     for i in range(len(time)):
#         if START_TIME * MEAS_DATA_TIMESCALE < time[i] < STOP_TIME * MEAS_DATA_TIMESCALE:
#             file_handle.write('{}, {}, {}, {}, {}, {}, {}\n'.format(time[i], data[i][0], data[i][1], data[i][2],
#                                                                   data[i][3], data[i][4], data[i][5]))
# file_handle.close()

