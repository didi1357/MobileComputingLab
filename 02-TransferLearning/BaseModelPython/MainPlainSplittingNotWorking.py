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

column_names = ['user-id', 'activity', 'timestamp', 'x-axis', 'y-axis', 'z-axis']
df = pd.read_csv('WISDM_ar_v1.1_raw.txt', header=None, names=column_names, comment=';')
df.dropna(axis=0, how='any', inplace=True)  # remove none values
# class to number encoding:
labelEncoder = preprocessing.LabelEncoder()
df['ActivityEncoded'] = labelEncoder.fit_transform(df['activity'].values.ravel())
num_classes = labelEncoder.classes_.size
print('Finished parsing {} entries.'.format(len(df)))

# # Describe the data
# df.head(5)
# # Show how many training examples exist for each of the six activities
# df['activity'].value_counts().plot(kind='bar', title='Training Examples by Activity Type')
# plt.show()
# # Better understand how the recordings are spread across the different users
# df['user-id'].value_counts().plot(kind='bar', title='Training Examples by User')
# plt.show()

# Do normalization by user:
for current_user_id in df['user-id'].unique():
    # shift by min value to have only positives:
    x_min = df.loc[df['user-id'] == current_user_id]['x-axis'].values.min()
    y_min = df.loc[df['user-id'] == current_user_id]['y-axis'].values.min()
    z_min = df.loc[df['user-id'] == current_user_id]['z-axis'].values.min()
    df.loc[df['user-id'] == current_user_id, 'x-axis'] = df.loc[df['user-id'] == current_user_id]['x-axis'] - x_min
    df.loc[df['user-id'] == current_user_id, 'y-axis'] = df.loc[df['user-id'] == current_user_id]['y-axis'] - y_min
    df.loc[df['user-id'] == current_user_id, 'z-axis'] = df.loc[df['user-id'] == current_user_id]['z-axis'] - z_min
    # divide by max:
    x_max = df.loc[df['user-id'] == current_user_id]['x-axis'].values.max()
    y_max = df.loc[df['user-id'] == current_user_id]['y-axis'].values.max()
    z_max = df.loc[df['user-id'] == current_user_id]['z-axis'].values.max()
    df.loc[df['user-id'] == current_user_id, 'x-axis'] = df.loc[df['user-id'] == current_user_id]['x-axis'] / x_max
    df.loc[df['user-id'] == current_user_id, 'y-axis'] = df.loc[df['user-id'] == current_user_id]['y-axis'] / y_max
    df.loc[df['user-id'] == current_user_id, 'z-axis'] = df.loc[df['user-id'] == current_user_id]['z-axis'] / z_max
print('Finished normalizing!')


# Split into test and training:
df_test = df[df['user-id'] > 28]
df_train = df[df['user-id'] <= 28]


def do_reformatting(data_frame):
    # Reshape data by label/activity:
    segments = []
    activities = []
    for current_activity in data_frame['ActivityEncoded'].unique():
        current_activity_subset = data_frame.loc[data_frame['ActivityEncoded'] == current_activity]
        print('Working on activity {} => {} elements'.format(labelEncoder.inverse_transform([current_activity]),
                                                             len(current_activity_subset)))
        for cur_user_id in data_frame['user-id'].unique():
            current_subset = current_activity_subset.loc[current_activity_subset['user-id'] == cur_user_id]
            print('Working on user {} => {} elements'.format(cur_user_id, len(current_subset)))
            for i in range(0, len(current_subset) - NUM_SAMPLES_PER_SEGMENT, NUM_SAMPLES_PER_STEP_INCREASE):
                x_series = current_subset['x-axis'].values[i: i + NUM_SAMPLES_PER_SEGMENT]
                y_series = current_subset['y-axis'].values[i: i + NUM_SAMPLES_PER_SEGMENT]
                z_series = current_subset['z-axis'].values[i: i + NUM_SAMPLES_PER_SEGMENT]
                segments.append([x_series, y_series, z_series])
                activities.append(current_activity)
    print('Reshaped to {} entries consisting of arrays containing x, y, z time-series data.'.format(len(segments)))

    # Transfer data to numpy format for keras:
    x_data = np.asarray(segments, dtype=np.float32)
    x_data = x_data.reshape(x_data.shape[0], INPUT_SHAPE).astype('float32')
    y_data = np.asarray(activities).astype('float32')
    y_data_hot = np_utils.to_categorical(y_data, num_classes)
    print('Preprocessing done. X shape: {}, Y shape:{}'.format(x_data.shape, y_data_hot.shape))
    return x_data, y_data_hot


x_train, y_train = do_reformatting(df_train)

# Finally, preprocessing done => Do model training:
model_m = Sequential()
model_m.add(Reshape((NUM_SENSORS, NUM_SAMPLES_PER_SEGMENT), input_shape=(INPUT_SHAPE,)))
model_m.add(Dense(32, activation='relu'))
model_m.add(Dense(16, activation='relu'))
model_m.add(Dense(8, activation='relu', name="headlayer"))
model_m.add(Flatten())
model_m.add(Dense(num_classes, activation='softmax'))
print(model_m.summary())

model_m.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
# Enable validation to use ModelCheckpoint and EarlyStopping callbacks:
history = model_m.fit(x_train, y_train, batch_size=BATCH_SIZE, epochs=EPOCHS, validation_split=0.2, verbose=1)
print('Training done!')

plt.figure(figsize=(12, 6))
plt.plot(history.history['accuracy'], 'r', label='Accuracy of training data')
plt.plot(history.history['val_accuracy'], 'b', label='Accuracy of validation data')
plt.plot(history.history['loss'], 'r--', label='Loss of training data')
plt.plot(history.history['val_loss'], 'b--', label='Loss of validation data')
plt.title('Model Accuracy and Loss')
plt.ylabel('Accuracy and Loss')
plt.xlabel('Training Epoch')
plt.ylim(0)
plt.legend()
plt.show()

x_test, y_test = do_reformatting(df_test)
score = model_m.evaluate(x_test, y_test, verbose=0)
print('Accuracy on test data: {}'.format(score[1]))
print('Loss on test data: {}'.format(score[0]))
