import numpy as np
import pandas as pd
from sklearn import preprocessing

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
        non_double = current_activity_subset.drop_duplicates(subset='timestamp')
        numpy_array = np.array(non_double['timestamp'].values.ravel())
        if len(numpy_array) > 1:
            last_element = numpy_array[0]
            begin_index = 0
            for i in range(1, len(numpy_array)):
                element = numpy_array[i]
                difference_ms = abs((element - last_element) / (1000 * 1000))
                last_element = element
                if difference_ms > 1000 or i == len(numpy_array) - 1:  # new start detected or last element:
                    current_recording = non_double[begin_index:i]
                    begin_index = i
                    timestamps = current_recording['timestamp'].values.ravel()
                    length = (timestamps[-1] - timestamps[0]) / (1000 * 1000 * 1000)
                    print('USER{}, activity{}: {}s'.format(cur_user_id, current_activity, length))
