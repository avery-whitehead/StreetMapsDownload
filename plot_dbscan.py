"""
plot_dbscan.py
Uses the DBSCAN clustering algorithm to create clusters from lat/long data
http://scikit-learn.org/stable/auto_examples/cluster/plot_dbscan.html
"""

import numpy as np
from sklearn.cluster import DBSCAN
import matplotlib.pyplot as plt

# Loads lat/long data
csv_f = '.\\lat_longs.csv'
X = np.genfromtxt(open(csv_f, 'rb'), delimiter=',', skip_header=1)
# Computes DBSCAN
db = DBSCAN(eps=0.01, min_samples=3, metric='haversine').fit(X)
core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
core_samples_mask[db.core_sample_indices_] = True
labels = db.labels_
# Gets number of clusters in labels, ignoring noise if present.
n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
print(f'Estimated number of clusters: {n_clusters_}')
# Plots the clusters
unique_labels = set(labels)
cmap = plt.get_cmap('tab20b')
colors = [cmap(each) for each in np.linspace(0, 1, len(unique_labels))]
for k, col in zip(unique_labels, colors):
    if k == -1:
        # Black removed and is used for noise instead
        col = [0, 0, 0, 1]
    class_member_mask = (labels == k)
    xy = X[class_member_mask & core_samples_mask]
    plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col), markeredgecolor='white', markersize=14)
    xy = X[class_member_mask & ~core_samples_mask]
    plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col), markeredgecolor='white', markersize=6)
plt.title(f'Estimated number of clusters: {n_clusters_}')
plt.show()
