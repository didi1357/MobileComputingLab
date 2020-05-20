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
from tensorflow.keras.layers import Dense, Dropout, Flatten, Reshape, InputLayer
from tensorflow.keras.layers import Conv1D, MaxPooling1D, GlobalAveragePooling1D
from keras.utils import np_utils

from sklearn.preprocessing import StandardScaler

# Preprocessing parameters
SEGMENT_DURATION_S = 1.2
FREQUENCY_HZ = 20
NUM_SAMPLES_PER_SEGMENT = int(np.floor(SEGMENT_DURATION_S / (1 / FREQUENCY_HZ)))
STEP_INCREASE_S = SEGMENT_DURATION_S / 2  # this controls the overlap => e.g. window is always shifted by 2s
NUM_SAMPLES_PER_STEP_INCREASE = int(np.floor(STEP_INCREASE_S / (1 / FREQUENCY_HZ)))
NUM_SENSORS = 3
INPUT_SHAPE = NUM_SAMPLES_PER_SEGMENT * NUM_SENSORS
# Hyper-parameters
BATCH_SIZE = 400
EPOCHS = 50
LABELS = ['Downstairs', 'Jogging', 'Sitting', 'Standing', 'Upstairs', 'Walking']

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
# Print all labels ascending:
print(list(le.inverse_transform(range(0, num_classes))))

# Do normalization by user using (val-min)/max:
# for current_user_id in df['user-id'].unique():
#     # shift by min value to have only positives:
#     x_min = df.loc[df['user-id'] == current_user_id]['x-axis'].values.min()
#     y_min = df.loc[df['user-id'] == current_user_id]['y-axis'].values.min()
#     z_min = df.loc[df['user-id'] == current_user_id]['z-axis'].values.min()
#     df.loc[df['user-id'] == current_user_id, 'x-axis'] = df.loc[df['user-id'] == current_user_id]['x-axis'] - x_min
#     df.loc[df['user-id'] == current_user_id, 'y-axis'] = df.loc[df['user-id'] == current_user_id]['y-axis'] - y_min
#     df.loc[df['user-id'] == current_user_id, 'z-axis'] = df.loc[df['user-id'] == current_user_id]['z-axis'] - z_min
#     # divide by max:
#     x_max = df.loc[df['user-id'] == current_user_id]['x-axis'].values.max()
#     y_max = df.loc[df['user-id'] == current_user_id]['y-axis'].values.max()
#     z_max = df.loc[df['user-id'] == current_user_id]['z-axis'].values.max()
#     df.loc[df['user-id'] == current_user_id, 'x-axis'] = df.loc[df['user-id'] == current_user_id]['x-axis'] / x_max
#     df.loc[df['user-id'] == current_user_id, 'y-axis'] = df.loc[df['user-id'] == current_user_id]['y-axis'] / y_max
#     df.loc[df['user-id'] == current_user_id, 'z-axis'] = df.loc[df['user-id'] == current_user_id]['z-axis'] / z_max
# print('Finished normalizing!')

# Do normalization by user using StandardScaler:
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

# # Normalize features for training data set
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
    # reshaped_segments = reshaped_segments_temp.reshape(reshaped_segments_temp.shape[0], INPUT_SHAPE).astype('float32')
    reshaped_segments = reshaped_segments_temp.astype('float32')
    y_data_hot = np_utils.to_categorical(np.asarray(labels).astype('float32'), num_classes)
    return reshaped_segments, y_data_hot


def do_reformatting_by_user_and_activity(data_frame):
    # Reshape data by label/activity:
    segments = []
    labels = []
    for current_activity in data_frame['ActivityEncoded'].unique():
        current_activity_subset = data_frame.loc[data_frame['ActivityEncoded'] == current_activity]
        print('current_activity {} has {} entries'.format(current_activity, len(current_activity_subset)))
        # for cur_user_id in data_frame['user-id'].unique():
        #     current_subset = current_activity_subset.loc[current_activity_subset['user-id'] == cur_user_id]
        #     print('with user {} having {} entries'.format(cur_user_id, len(current_subset)))
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
    # reshaped_segments = reshaped_segments_temp.reshape(reshaped_segments_temp.shape[0], INPUT_SHAPE).astype('float32')
    reshaped_segments = reshaped_segments_temp.astype('float32')
    y_data_hot = np_utils.to_categorical(np.asarray(labels).astype('float32'), num_classes)
    return reshaped_segments, y_data_hot


x_train, y_train = do_reformatting_github(df_train)

model_m = Sequential()
model_m.add(InputLayer(input_shape=(NUM_SAMPLES_PER_SEGMENT, NUM_SENSORS)))
model_m.add(Conv1D(filters=64, kernel_size=3, activation='relu'))
model_m.add(Dropout(0.2))
model_m.add(Conv1D(filters=32, kernel_size=3, activation='relu', name='headlayer'))  # first idea was to use this as headlayer
model_m.add(Dropout(0.2))

# and to retrain these in the head model:
model_m.add(Conv1D(filters=num_classes, kernel_size=3, activation='relu'))
model_m.add(GlobalAveragePooling1D())
model_m.add(Dense(num_classes, activation='softmax'))

# model_m.add(Conv1D(filters=num_classes*2, kernel_size=3, activation='relu'))
# model_m.add(Dropout(0.15))
# model_m.add(Flatten())
# model_m.add(Dense(2 * num_classes, activation='relu', name='headlayer'))
# model_m.add(Dense(num_classes, activation='softmax'))
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


def show_confusion_matrix(validations, predictions):
    matrix = metrics.confusion_matrix(validations, predictions)
    plt.figure(figsize=(6, 4))
    sns.heatmap(matrix,
                cmap='coolwarm',
                linecolor='white',
                linewidths=1,
                xticklabels=LABELS,
                yticklabels=LABELS,
                annot=True,
                fmt='d')
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.show()


# Do normalization of test data:
df_test['x-axis'] = df_test['x-axis'] / df_test['x-axis'].max()
df_test['y-axis'] = df_test['y-axis'] / df_test['y-axis'].max()
df_test['z-axis'] = df_test['z-axis'] / df_test['z-axis'].max()
df_test = df_test.round({'x-axis': 4, 'y-axis': 4, 'z-axis': 4})
# Reformat test data and do evaluation:
x_test, y_test = do_reformatting_github(df_test)
y_pred_test = model_m.predict(x_test)
max_y_pred_test = np.argmax(y_pred_test, axis=1)
max_y_test = np.argmax(y_test, axis=1)
show_confusion_matrix(max_y_test, max_y_pred_test)
score = model_m.evaluate(x_test, y_test, verbose=0)
print('\nAccuracy on test data: %0.2f' % score[1])
print('\nLoss on test data: %0.2f' % score[0])

model_m.save('base_model.h5')
converter = tensorflow.lite.TFLiteConverter.from_keras_model(model_m)
tflite_model = converter.convert()
with open("converted_base_model.tflite", "wb") as file_handle:
    file_handle.write(tflite_model)
