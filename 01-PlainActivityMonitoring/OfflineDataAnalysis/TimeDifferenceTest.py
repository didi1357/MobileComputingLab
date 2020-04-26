from Utils import my_parse_csv, CLASSES, MEAS_DATA_TIMESCALE

time_data, transposed_data = my_parse_csv('preprocessed/downstairs_1.csv')
previous_time_data = time_data[0]
for time in time_data:
    diff = time - previous_time_data
    previous_time_data = time
    print('Difference: {}'.format(diff / MEAS_DATA_TIMESCALE))

