from matplotlib import pyplot as plt

import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats

from sklearn import metrics
from sklearn.metrics import classification_report
from sklearn import preprocessing

import tensorflow
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Flatten, Reshape
from tensorflow.keras.layers import Conv2D, MaxPooling2D
from keras.utils import np_utils

from sklearn.preprocessing import StandardScaler

# Preprocessing parameters
SEGMENT_DURATION_S = 4
FREQUENCY_HZ = 20
NUM_SAMPLES_PER_SEGMENT = int(np.floor(SEGMENT_DURATION_S / (1 / FREQUENCY_HZ)))
STEP_INCREASE_S = 2  # this controls the overlap => e.g. window is always shifted by 2s
NUM_SAMPLES_PER_STEP_INCREASE = int(np.floor(STEP_INCREASE_S / (1 / FREQUENCY_HZ)))
NUM_SENSORS = 3
INPUT_SHAPE = NUM_SAMPLES_PER_SEGMENT * NUM_SENSORS
# Hyper-parameters
BATCH_SIZE = 400
EPOCHS = 50

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

# Do normalization by user:
# for current_user_id in df['user-id'].unique():
#     scaler = StandardScaler()
#     x_data = df.loc[df['user-id'] == current_user_id]['x-axis']
#     y_data = df.loc[df['user-id'] == current_user_id]['y-axis']
#     z_data = df.loc[df['user-id'] == current_user_id]['z-axis']
#     whole_array = [x_data, y_data, z_data]
#     transposed = np.transpose(whole_array)
#     scaler.fit(transposed)
#     print('mean:{}, var{}'.format(scaler.mean_, scaler.var_))
#     new_array = scaler.transform(transposed)
#     whole_array = np.transpose(new_array)
#     df.loc[df['user-id'] == current_user_id, 'x-axis'] = whole_array[0]
#     df.loc[df['user-id'] == current_user_id, 'y-axis'] = whole_array[1]
#     df.loc[df['user-id'] == current_user_id, 'z-axis'] = whole_array[2]
#     print('max: {}, {}, {}; min: {},{},{}'.format(max(whole_array[0]), max(whole_array[1]), max(whole_array[2]),
#                                                   min(whole_array[0]), min(whole_array[1]), min(whole_array[2])))
# print('Finished normalizing!')

# Differentiate between test set and training set
df_test = df[df['user-id'] > 28]
df_train = df[df['user-id'] <= 28]

# Normalize features for training data set
pd.options.mode.chained_assignment = None  # default='warn'
df_train['x-axis'] = df_train['x-axis'] / df_train['x-axis'].max()
df_train['y-axis'] = df_train['y-axis'] / df_train['y-axis'].max()
df_train['z-axis'] = df_train['z-axis'] / df_train['z-axis'].max()
# Round numbers
df_train = df_train.round({'x-axis': 4, 'y-axis': 4, 'z-axis': 4})


def do_reformatting_github(data_frame):
    segments = []
    labels = []
    data_frame_test = data_frame.loc[:]
    for i in range(0, len(data_frame_test) - NUM_SAMPLES_PER_SEGMENT, NUM_SAMPLES_PER_STEP_INCREASE):
        x_series = data_frame_test['x-axis'].values[i: i + NUM_SAMPLES_PER_SEGMENT]
        y_series = data_frame_test['y-axis'].values[i: i + NUM_SAMPLES_PER_SEGMENT]
        z_series = data_frame_test['z-axis'].values[i: i + NUM_SAMPLES_PER_SEGMENT]
        # Retrieve the most often used label in this segment
        label = stats.mode(data_frame_test[LABEL][i: i + NUM_SAMPLES_PER_SEGMENT])[0][0]
        segments.append([x_series, y_series, z_series])
        labels.append(label)

    # Bring the segments into a better shape
    reshaped_segments_temp = np.asarray(segments, dtype=np.float32).reshape(-1, NUM_SAMPLES_PER_SEGMENT, NUM_SENSORS)
    reshaped_segments = reshaped_segments_temp.reshape(reshaped_segments_temp.shape[0], INPUT_SHAPE).astype('float32')
    y_data_hot = np_utils.to_categorical(np.asarray(labels).astype('float32'), num_classes)
    return reshaped_segments, y_data_hot


def do_reformatting_by_user_and_activity(data_frame):
    # Reshape data by label/activity:
    segments = []
    labels = []
    for current_activity in data_frame['ActivityEncoded'].unique():
        current_activity_subset = data_frame.loc[data_frame['ActivityEncoded'] == current_activity]
        # print('current_activity {} has {} entries'.format(current_activity, len(current_activity_subset)))
        # for cur_user_id in data_frame['user-id'].unique():
        #     current_subset = current_activity_subset.loc[current_activity_subset['user-id'] == cur_user_id]
        #     # print('with user {} having {} entries'.format(cur_user_id, len(current_subset)))
        #     for i in range(0, len(current_subset) - NUM_SAMPLES_PER_SEGMENT, NUM_SAMPLES_PER_STEP_INCREASE):
        #         x_series = current_subset['x-axis'].values[i: i + NUM_SAMPLES_PER_SEGMENT]
        #         y_series = current_subset['y-axis'].values[i: i + NUM_SAMPLES_PER_SEGMENT]
        #         z_series = current_subset['z-axis'].values[i: i + NUM_SAMPLES_PER_SEGMENT]
        #         segments.append([x_series, y_series, z_series])
        #         labels.append(current_activity)
        for i in range(0, len(current_activity_subset) - NUM_SAMPLES_PER_SEGMENT, NUM_SAMPLES_PER_STEP_INCREASE):
            x_series = current_activity_subset['x-axis'].values[i: i + NUM_SAMPLES_PER_SEGMENT]
            y_series = current_activity_subset['y-axis'].values[i: i + NUM_SAMPLES_PER_SEGMENT]
            z_series = current_activity_subset['z-axis'].values[i: i + NUM_SAMPLES_PER_SEGMENT]
            segments.append([x_series, y_series, z_series])
            labels.append(current_activity)

    # Transfer data to numpy format for keras:
    reshaped_segments_temp = np.asarray(segments, dtype=np.float32).reshape(-1, NUM_SAMPLES_PER_SEGMENT, NUM_SENSORS)
    reshaped_segments = reshaped_segments_temp.reshape(reshaped_segments_temp.shape[0], INPUT_SHAPE).astype('float32')
    y_data_hot = np_utils.to_categorical(np.asarray(labels).astype('float32'), num_classes)
    return reshaped_segments, y_data_hot


x_train, y_train = do_reformatting_by_user_and_activity(df_train)

model_m = Sequential()
model_m.add(Reshape((NUM_SAMPLES_PER_SEGMENT, 3), input_shape=(INPUT_SHAPE,)))
model_m.add(Dense(32, activation='relu'))
model_m.add(Dense(16, activation='relu'))
model_m.add(Dense(8, activation='relu', name="headlayer"))
model_m.add(Flatten())
model_m.add(Dense(num_classes, activation='softmax'))
print(model_m.summary())

model_m.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

# Enable validation to use ModelCheckpoint and EarlyStopping callbacks.
history = model_m.fit(x_train, y_train, batch_size=BATCH_SIZE, epochs=EPOCHS,
                      validation_split=0.2, verbose=1)

plt.figure(figsize=(12, 6))
plt.plot(history.history['accuracy'], 'r', label='Accuracy of training data')
plt.plot(history.history['val_accuracy'], 'b', label='Accuracy of validation data')
plt.plot(history.history['loss'], 'r--', label='Loss of training data')
plt.plot(history.history['val_loss'], 'b--', label='Loss of validation data')
plt.title('Model Accuracy and Loss')
plt.ylabel('Accuracy and Loss')
plt.xlabel('Training Epoch')
plt.ylim([0, 1.5])
plt.legend()
plt.show()
