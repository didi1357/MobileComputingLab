from Utils import get_windowed_feature_lists, prepare_classification_result_plot, export_feature_list,\
    filter_feature_vectors_to_common_number, get_classifier, get_unwindowed_feature_lists, CLASSES
import matplotlib.pyplot as plt

LEARN_WINDOW_TIME_S = 1.2
TEST_WINDOW_TIME_S = 1.2


# First generate a classifier with one feature vector per class:
feature_vectors_per_class = get_unwindowed_feature_lists()
export_feature_list('featurelists/unwindowed.json', feature_vectors_per_class)
unwindowed_classifier = get_classifier(feature_vectors_per_class)

# Then generate a classifier with more than one feature vector per class by windowing the preprocessed files:
feature_vectors_per_class = get_windowed_feature_lists(LEARN_WINDOW_TIME_S)
feature_vectors_per_class = filter_feature_vectors_to_common_number(feature_vectors_per_class)  # biased otherwise
export_feature_list('featurelists/windowed.json', feature_vectors_per_class)
windowed_classifier = get_classifier(feature_vectors_per_class)


# Generate plots showing performance:
for classifier_name, classifier in {'unwindowed': unwindowed_classifier, 'windowed': windowed_classifier}.items():
    for test_class in CLASSES:
        current_test_file = 'preprocessed/{}_3.csv'.format(test_class)
        prepare_classification_result_plot(classifier, current_test_file, TEST_WINDOW_TIME_S, classifier_name)
        plt.savefig('classification_results/{}_{}.png'.format(test_class, classifier_name))
