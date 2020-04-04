from Utils import feature_vectors, feature_vector, CLASSES, NR_TRAINING_FILES, my_parse_csv
from sklearn.neighbors import KNeighborsClassifier
import math
import matplotlib.pyplot as plt
import numpy as np

LEARN_WINDOW_TIME_S = 1.2
TEST_WINDOW_TIME_S = LEARN_WINDOW_TIME_S
K = 3

feature_vectors_per_class = dict()
for cnt_class in range(len(CLASSES)):
    class_name = CLASSES[cnt_class]
    for file_nr in range(NR_TRAINING_FILES):
        print('Training on preprocessed/{}_{}.csv: '.format(class_name, file_nr), end='')
        cur_time, cur_data = my_parse_csv('preprocessed/{}_{}.csv'.format(class_name, file_nr))
        feature_vector_list = feature_vectors(cur_time, cur_data, LEARN_WINDOW_TIME_S)
        print('Found {} feature vectors'.format(len(feature_vector_list)))
        feature_vectors_per_class[cnt_class] = feature_vector_list

common_nr_of_feature_vectors = math.inf
for cnt_class, feature_vector_list in feature_vectors_per_class.items():
    common_nr_of_feature_vectors = min(common_nr_of_feature_vectors, len(feature_vector_list))
print('Common minimum of feature vectors for all classes={}'.format(common_nr_of_feature_vectors))

X = []
Y = []
for cnt_class, feature_vector_list in feature_vectors_per_class.items():
    for i in range(len(feature_vector_list)):
        if i < common_nr_of_feature_vectors:
            X.append(feature_vector_list[i])
            Y.append(cnt_class)  # index of CLASSES is name to class nr mapping!

print('Using a total of {} feature vectors for KNN'.format(len(Y)))
calculated_k = math.floor(math.sqrt(len(Y)))
print('Calculated K={}'.format(calculated_k))
clf = KNeighborsClassifier(n_neighbors=calculated_k)
clf.fit(X, Y)

current_test_file = 'preprocessed/walking_3.csv'
x_time, x_data = my_parse_csv(current_test_file)
test_vectors = feature_vectors(x_time, x_data, TEST_WINDOW_TIME_S)
# predict/predict_proba expects an array and returns an array of results..
all_probabilities = clf.predict_proba(test_vectors)
transposed_probabilities = np.transpose(all_probabilities)
window_nr = range(len(all_probabilities))
fig, ((ax1, ax4), (ax2, ax5), (ax3, ax6)) = plt.subplots(3, 2)
fig.suptitle('Probabilities for {}'.format(current_test_file))
ax1.plot(window_nr, transposed_probabilities[0])
ax1.set_title(CLASSES[0])
ax2.plot(window_nr, transposed_probabilities[1])
ax2.set_title(CLASSES[1])
ax3.plot(window_nr, transposed_probabilities[2])
ax3.set_title(CLASSES[2])
ax4.plot(window_nr, transposed_probabilities[3])
ax4.set_title(CLASSES[3])
ax5.plot(window_nr, transposed_probabilities[4])
ax5.set_title(CLASSES[4])
ax6.plot(window_nr, transposed_probabilities[5])
ax6.set_title(CLASSES[5])
ax1.set_ylim([0, 1])
ax2.set_ylim([0, 1])
ax3.set_ylim([0, 1])
ax4.set_ylim([0, 1])
ax5.set_ylim([0, 1])
ax6.set_ylim([0, 1])
plt.show()
# for cnt_class in range(len(CLASSES)):
#     class_name = CLASSES[cnt_class]
#     print('{}: {}%'.format(class_name, probabilities[cnt_class] * 100))
