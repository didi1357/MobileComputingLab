import os
import pandas as pd
import matplotlib.pyplot as plt

BEGIN_TIMES = {'1.downstairs.log': 3000, '1.upstairs.log': 3000, '1.standing.log': 5000, '1.sitting.log': 5000,
               '1.walking.log': 5000, '1.jogging.log': 5000, '0.downstairs.log': 2000, '0.upstairs.log': 2000,
               '0.standing.log': 10000, '0.sitting.log': 10000, '0.walking.log': 5000, '0.jogging.log': 5000}

CLASSES = {'downstairs': 0, 'upstairs': 1, 'sitting': 2, 'standing': 3, 'walking': 4, 'jogging': 5}
PHONE_POS = {'0': 'hand', '1': 'pocket'}

for current_file in sorted(os.listdir("files")):
    if current_file.endswith(".log"):
        column_names = ['timestamp', 'x', 'y', 'z', 'knn', 'tl', 'bm']
        data_frame = pd.read_csv('files/' + current_file, header=None, names=column_names)
        zero_time = data_frame['timestamp'][0]
        data_frame['timestamp'] = (data_frame['timestamp'] - zero_time) / (1000 * 1000)
        current_begin_time = BEGIN_TIMES[current_file]
        data_frame = data_frame.loc[data_frame['timestamp'] > current_begin_time]
        end_time = data_frame['timestamp'].iloc[-1]
        data_frame = data_frame.loc[data_frame['timestamp'] < end_time - 3000]
        current_class = current_file[2:-4]
        current_class_nr = CLASSES[current_class]
        phone_pos_nr = current_file[0]
        correct_knn = 0
        correct_tl = 0
        correct_bm = 0
        for index, row in data_frame.iterrows():
            if row['knn'] == current_class_nr:
                correct_knn += 1
            if row['tl'] == current_class_nr:
                correct_tl += 1
            if row['bm'] == current_class_nr:
                correct_bm += 1
        knn_rate = correct_knn * 100 / len(data_frame)
        tl_rate = correct_tl * 100 / len(data_frame)
        bm_rate = correct_bm * 100 / len(data_frame)
        humantext = 'Classification results for {} with phone in {}: KNN={:5.1f}%, TL={:5.1f}%, BM={:5.1f}%'
        latextext = '{}, phone in {} & {:.1f} & {:.1f} & {:.1f} \\\\'
        print(latextext.format(current_class, PHONE_POS[phone_pos_nr], knn_rate, tl_rate, bm_rate))
        # plt.title(current_file)
        # plt.plot(data_frame['timestamp'], data_frame['x'])
        # plt.show()
