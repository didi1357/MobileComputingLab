import pandas as pd
import os
from Utils import plot_parsed, MEAS_DATA_TIMESCALE, my_parse_csv

# for current_file in os.listdir("files"):
#     if current_file.endswith(".csv"):
#         time, data = my_parse_csv('files/' + current_file)
#         plot_parsed(current_file, time, data)

current_file = 'standing_3.csv'
time, data = my_parse_csv('files/' + current_file)
plot_parsed(current_file, time, data)

START_TIME = 0
STOP_TIME = START_TIME + 1

# output_path = 'testing_preprocessed/' + CURRENT_FILE
# with open(output_path, 'w') as file_handle:
#     for i in range(len(time)):
#         if START_TIME * MEAS_DATA_TIMESCALE < time[i] < STOP_TIME * MEAS_DATA_TIMESCALE:
#             file_handle.write('{}, {}, {}, {}, {}, {}, {}\n'.format(time[i], data[i][0], data[i][1], data[i][2],
#                                                                   data[i][3], data[i][4], data[i][5]))
# file_handle.close()

