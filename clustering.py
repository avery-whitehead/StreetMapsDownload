"""
clustering.py
Uses scikit-learn's DBSCAN clustering algorithm to create clusters from
some CSV data
http://scikit-learn.org/stable/auto_examples/cluster/plot_dbscan.html
"""

from typing import List
import numpy as np
from sklearn.cluster import DBSCAN
import matplotlib.pyplot as plt


def load_csv_data(csv_file: str) -> np.ndarray:
    """
    csv_file (str): The path to the CSV file containing data to be clustered
    """
    X = np.genfromtxt(
        open(csv_file, 'rb'), delimiter=',', skip_header=1, usecols=(2, 3))
    return X


def get_db_object(X: np.ndarray, eps: int, min_points: int) -> DBSCAN:
    """
    Uses DBSCAN to create clusters from CSV data
    Args:
        X (np.ndarray): An array containing the data to be clustered
        eps (int): The epsilon value used in the DBSCAN algorithm, measures
        the mininum distance between two points for them to be considered
        neighbours in a cluster.
        min_points (int): The minimum number of points to form a cluster
    Returns:
        DBSCAN: The DBSCAN object containing the results of the algorithm
    """
    # Use Haversine distance for lat/long data
    db = DBSCAN(eps=eps, min_samples=min_points, metric='haversine').fit(X)
    return db


def get_db_clusters(X: np.ndarray, db: DBSCAN) -> List[np.ndarray]:
    """
    Gets a list of clusters and the objects in each clusters from the results
    of a DBSCAN algorithm
    Args:
        X (np.ndarray): An array containing the data that has been clustered
        db (DBSCAN): The DBSCAN object containing the results of the algorithm
    Returns:
        List[np.ndarray]: A list of clusters; each element in the list is a
        NumPy array of the objects in that cluster
    """
    labels = db.labels_
    # Gets number of clusters in labels
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
    # 0th index is noise
    clusters = [X[labels == i] for i in range(-1, n_clusters_)]
    return clusters


def plot_db_clusters(X: np.ndarray, db: DBSCAN) -> None:
    """
    X (np.ndarray): An array containing the data that has been clustered
    db (DBSCAN): The DBSCAN object containing the results of the algorithm
    """
    labels = db.labels_
    core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
    core_samples_mask[db.core_sample_indices_] = True
    unique_labels = set(labels)
    cmap = plt.get_cmap('gist_earth')
    colors = [cmap(each) for each in np.linspace(0, 1, len(unique_labels))]
    for k, col in zip(unique_labels, colors):
        if k == -1:
            # Black removed and is used for noise instead
            col = [0, 0, 0, 1]
        class_member_mask = (labels == k)
        xy = X[class_member_mask & core_samples_mask]
        plt.plot(
            xy[:, 0],
            xy[:, 1],
            'o',
            markerfacecolor=tuple(col),
            markeredgecolor='white',
            markersize=14)
        xy = X[class_member_mask & ~core_samples_mask]
        plt.plot(
            xy[:, 0],
            xy[:, 1],
            'o',
            markerfacecolor=tuple(col),
            markeredgecolor='white',
            markersize=6)
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
    plt.title(f'Estimated number of clusters: {n_clusters_}')
    plt.show()
