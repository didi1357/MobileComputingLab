from Utils import my_parse_csv, CLASSES, MEAS_DATA_TIMESCALE
import numpy as np
import matplotlib.pyplot as plt


for class_name in CLASSES:
    time_data, transposed_data = my_parse_csv('preprocessed/{}_2.csv'.format(class_name))
    readable_time = np.divide(time_data, MEAS_DATA_TIMESCALE)
    fig, (ax1, ax2, ax3) = plt.subplots(3)
    fig.suptitle('{}'.format(class_name))
    ax1.plot(readable_time, transposed_data[0])
    ax1.set_title('x acc')
    ax2.plot(readable_time, transposed_data[1])
    ax2.set_title('y acc')
    ax3.plot(readable_time, transposed_data[2])
    ax3.set_title('z acc')
    plt.savefig('preprocessed_plotted/{}_2.png'.format(class_name))
