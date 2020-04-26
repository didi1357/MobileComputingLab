import pandas as pd
import os
from Utils import plot_parsed, MEAS_DATA_TIMESCALE, my_parse_csv

# for current_file in os.listdir("measurements"):
#     if current_file.endswith(".csv"):
#         time, data = my_parse_csv('measurements/' + current_file)
#         plot_parsed(current_file, time, data)

current_file = 'walking_3.csv'
time, data = my_parse_csv('measurements/' + current_file)
plot_parsed(current_file, time, data)

START_TIME = 10
STOP_TIME = 60

output_path = 'preprocessed/' + current_file
with open(output_path, 'w') as file_handle:
    for i in range(len(time)):
        if START_TIME * MEAS_DATA_TIMESCALE < time[i] < STOP_TIME * MEAS_DATA_TIMESCALE:
            file_handle.write('{}, {}, {}, {}\n'.format(time[i], data[0][i], data[1][i], data[2][i]))
file_handle.close()
