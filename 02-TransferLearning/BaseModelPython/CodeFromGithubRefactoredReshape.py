import os
os.environ['PYTHONHASHSEED']=str(1)
from numpy.random import seed
seed(1)
import tensorflow
tensorflow.random.set_seed(2)
import random
random.seed(1)

from matplotlib import pyplot as plt

import numpy as np
import pandas as pd
from scipy import stats

from sklearn import preprocessing

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Flatten, Reshape
from keras.utils import np_utils

# Same labels will be reused throughout the program
LABELS = ['Downstairs', 'Jogging', 'Sitting', 'Standing', 'Upstairs', 'Walking']
# The number of steps within one time segment
TIME_PERIODS = 80
# The steps to take from one segment to the next; if this value is equal to
# TIME_PERIODS, then there is no overlap between the segments
STEP_DISTANCE = 40


def read_data(file_path):
    column_names = ['user-id', 'activity', 'timestamp', 'x-axis', 'y-axis', 'z-axis']
    df = pd.read_csv(file_path, header=None, names=column_names, comment=';')
    df.dropna(axis=0, how='any', inplace=True)
    return df


# Load data set containing all the data from csv
df = read_data('WISDM_ar_v1.1_raw.txt')

# Define column name of the label vector
LABEL = 'ActivityEncoded'
# Transform the labels from String to Integer via LabelEncoder
le = preprocessing.LabelEncoder()
# Add a new column to the existing DataFrame with the encoded values
df[LABEL] = le.fit_transform(df['activity'].values.ravel())
num_classes = le.classes_.size

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


def create_segments_and_labels(df, time_steps, step, label_name):
    N_FEATURES = 3  # x, y, z acceleration as features
    segments = []
    labels = []
    for i in range(0, len(df) - time_steps, step):
        xs = df['x-axis'].values[i: i + time_steps]
        ys = df['y-axis'].values[i: i + time_steps]
        zs = df['z-axis'].values[i: i + time_steps]
        # Retrieve the most often used label in this segment
        label = stats.mode(df[label_name][i: i + time_steps])[0][0]
        segments.append([xs, ys, zs])
        labels.append(label)

    reshaped_segments = np.asarray(segments, dtype=np.float32).reshape(-1, time_steps, N_FEATURES)
    keras_y = np_utils.to_categorical(np.asarray(labels).astype('float32'), num_classes)
    return reshaped_segments.astype('float32'), keras_y


x_train, y_train_hot = create_segments_and_labels(df_train, TIME_PERIODS, STEP_DISTANCE, LABEL)

model_m = Sequential()
model_m.add(Dense(32, activation='relu', input_shape=(TIME_PERIODS, 3)))
model_m.add(Dense(16, activation='relu'))
model_m.add(Dense(8, activation='relu', name="headlayer"))
model_m.add(Flatten())
model_m.add(Dense(num_classes, activation='softmax'))
print(model_m.summary())

model_m.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

# Hyper-parameters
BATCH_SIZE = 400
EPOCHS = 50

# Enable validation to use ModelCheckpoint and EarlyStopping callbacks.
history = model_m.fit(x_train, y_train_hot, batch_size=BATCH_SIZE, epochs=EPOCHS,
                      validation_split=0.2, verbose=1)

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

# model_m.save('base_model_github.pbtxt')
# converter = tensorflow.lite.TFLiteConverter.from_keras_model(model_m)
# tflite_model = converter.convert()
# with open("converted_base_model_github.tflite", "wb") as file_handle:
#     file_handle.write(tflite_model)
