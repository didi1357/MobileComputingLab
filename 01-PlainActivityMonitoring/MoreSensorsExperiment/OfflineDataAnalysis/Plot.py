import pandas as pd
import os
from Utils import plot_save_file, MEAS_DATA_TIMESCALE


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


for current_file in os.listdir("training_files"):
    if current_file.endswith(".csv"):
        parsed = pd.read_csv("training_files/" + current_file)
        time, data = preprocess_csv_data(parsed)
        plot_save_file(current_file, time, data)

