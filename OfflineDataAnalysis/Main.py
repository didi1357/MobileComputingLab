import pandas as pd
import os
import matplotlib.pyplot as plt

for current_file in os.listdir("files"):
    if current_file.endswith(".csv"):
        parsed_data = pd.read_csv('files/' + current_file)
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
                time_data_acc.append((parsed_data.values[i][4] - first_time) / (1000 * 1000 * 1000))
            if parsed_data.values[i][0] == 1:
                x_data_rot.append(parsed_data.values[i][1])
                y_data_rot.append(parsed_data.values[i][2])
                z_data_rot.append(parsed_data.values[i][3])
                time_data_rot.append((parsed_data.values[i][4] - first_time) / (1000 * 1000 * 1000))
        fig, ((ax1, ax4), (ax2, ax5), (ax3, ax6)) = plt.subplots(3, 2)
        fig.suptitle(current_file)
        ax1.plot(time_data_acc, x_data_acc)
        ax1.set_title('x acc')
        ax2.plot(time_data_acc, y_data_acc)
        ax2.set_title('y acc')
        ax3.plot(time_data_acc, z_data_acc)
        ax3.set_title('z acc')
        ax4.plot(time_data_rot, x_data_rot)
        ax4.set_title('x rot')
        ax5.plot(time_data_rot, y_data_rot)
        ax5.set_title('y rot')
        ax6.plot(time_data_rot, z_data_rot)
        ax6.set_title('z rot')
        plt.show()


