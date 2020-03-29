import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


MEAS_DATA_TIMESCALE = 1000 * 1000 * 1000  # ns/s
CLASSES = ['downstairs', 'jogging', 'sitting', 'upstairs', 'walking']


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
    parsed = pd.read_csv('preprocessed/' + file_name)
    time_data = []
    unified_data = []
    for i in range(len(parsed)):
        time_data.append(parsed.values[i][0])
        unified_data.append(parsed.values[i][1:])
    return time_data, np.transpose(unified_data)