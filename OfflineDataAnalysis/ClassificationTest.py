from Utils import load_features
from sklearn.neighbors import NearestNeighbors
from sklearn.datasets import load_iris

# trained = load_features()

data = load_iris()
print(data)
print(len(data['data']))
print(len(data['target']))