from Utils import feature_vector, CLASSES, NR_TRAINING_FILES, my_parse_csv
import numpy as np
from sklearn.neighbors import KNeighborsClassifier

X = []
Y = []
for cnt_classes in range(len(CLASSES)):
    class_name = CLASSES[cnt_classes]
    for file_nr in range(NR_TRAINING_FILES):
        cur_time, cur_data = my_parse_csv('preprocessed/{}_{}.csv'.format(class_name, file_nr))
        cur_features = feature_vector(cur_data)
        X.append(cur_features)
        Y.append(cnt_classes)  # index of CLASSES is name to class nr mapping!

clf = KNeighborsClassifier(1)
clf.fit(X, Y)

x_time, x_data = my_parse_csv('preprocessed/upstairs_3.csv')
x_feat = feature_vector(x_data)
# print(CLASSES[clf.predict([x_feat])[0]])  # predict expects an array and returns an array of results..
probabilities = clf.predict_proba([x_feat])[0]
for cnt_classes in range(len(CLASSES)):
    class_name = CLASSES[cnt_classes]
    print('{}: {}%'.format(class_name, probabilities[cnt_classes] * 100))
