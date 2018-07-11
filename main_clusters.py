"""
main_clusters.py
Uses the classes and functions in getmaps.py, createprints.py and
clusters.py to create a map for a series of clusters containing
multiple properties and points of interest
"""

# import getmaps
# import createprints
import clustering
# import pyodbc

if __name__ == '__main__':
    X = clustering.load_csv_data('.\\lat_longs.csv')
    # Episilon and minimum sampling values
    db = clustering.get_db_object(X, 0.0125, 3)
    clusters = clustering.get_db_clusters(X, db)
    clustering.plot_db_clusters(X, db)