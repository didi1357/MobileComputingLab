import tensorflow as tf
from tensorflow.keras.models import Sequential, Model, load_model, save_model
from tensorflow.keras import layers
from tensorflow.keras.regularizers import l2
from tfltransfer import bases
from tfltransfer import heads
from tfltransfer import optimizers
from tfltransfer.tflite_transfer_converter import TFLiteTransferConverter

model_m = load_model('../BaseModelPython/base_model_github.pbtxt')
model = Model(model_m.input, model_m.get_layer('headlayer').output)
save_model(model, 'chopped_model_github.pbtxt', include_optimizer=False, save_format="tf")

# --------------- on-device model conversion ---------------- #

# Model configuration.
num_classes = 6
learning_rate = 0.001
batch_size = 5
l2_rate = 0.0001
hidden_units = 6
input_shape = model.get_layer('headlayer').output.shape


base = bases.SavedModelBase('chopped_model_github.pbtxt')
head = tf.keras.Sequential([
    layers.Flatten(input_shape=(1, 80, 8)),
    layers.Dense(
        units=hidden_units,
        activation="relu",
        kernel_regularizer=l2(l2_rate)),
    layers.Dense(
        units=num_classes,
        activation="softmax",
        kernel_regularizer=l2(l2_rate)),
])

# Optimizer is ignored by the converter.
head.compile(loss="categorical_crossentropy", optimizer="adam")

converter = TFLiteTransferConverter(num_classes, base, heads.KerasModelHead(head), optimizers.SGD(learning_rate),
                                    train_batch_size=batch_size)

converter.convert_and_save('head_model_github')
