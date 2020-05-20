import numpy as np
import pandas as pd
from sklearn import preprocessing


# KNOWN_DIFFERENCES_MS = [50, 100]  # 50*2 if single event was lost..
KNOWN_DIFFERENCES_MS = [50, 100, 40, 80]
ALLOWED_DEVIATION_MS = 2

# Load data set containing all the data from csv
column_names = ['user-id', 'activity', 'timestamp', 'x-axis', 'y-axis', 'z-axis']
df = pd.read_csv('WISDM_ar_v1.1_raw.txt', header=None, names=column_names, comment=';')
df.dropna(axis=0, how='any', inplace=True)
# Define column name of the label vector
LABEL = 'ActivityEncoded'
# Transform the labels from String to Integer via LabelEncoder
le = preprocessing.LabelEncoder()
# Add a new column to the existing DataFrame with the encoded values
df[LABEL] = le.fit_transform(df['activity'].values.ravel())
num_classes = le.classes_.size

for cur_user_id in df['user-id'].unique():
    current_user_subset = df.loc[df['user-id'] == cur_user_id]
    for current_activity in current_user_subset['ActivityEncoded'].unique():
        current_activity_subset = current_user_subset.loc[current_user_subset['ActivityEncoded'] == current_activity]
        unique_timestamped_rows = current_activity_subset.drop_duplicates(subset='timestamp')
        numpy_array = np.array(unique_timestamped_rows['timestamp'].values.ravel())
        last_element = numpy_array[0]
        differences = []
        for element in numpy_array[1:]:
            difference_ms = (element - last_element) / (1000 * 1000)
            differences.append(difference_ms)
            last_element = element
        strange_differences = []
        expected_differences = []
        for difference_ms in differences:
            is_normal = False
            for known_ms in KNOWN_DIFFERENCES_MS:
                if abs(difference_ms - known_ms) < ALLOWED_DEVIATION_MS:
                    is_normal = True
            if is_normal:
                expected_differences.append(difference_ms)
            else:
                strange_differences.append(difference_ms)
        # if len(strange_differences) > len(expected_differences):
        if len(strange_differences) > 400:
            print('===================USER{}, activity{}================='.format(cur_user_id, current_activity))
            print('strange vs normal = {} vs {} entries!'.format(len(strange_differences), len(expected_differences)))
            print('strange mean:{}'.format(np.mean(strange_differences[0:10])))
            print(strange_differences[:30])
