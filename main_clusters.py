"""
main_clusters.py
Uses the classes and functions in getmaps.py, createprints.py and
clusters.py to create a map for a series of clusters containing
multiple properties and points of interest
"""

from typing import List
import csv
import getmaps
# import createprints
import clustering

def _get_all_locations(config_path: str) -> List[getmaps.Location]:
    """
    Wrapper for getmaps.get_all_locations()
    Args:
        config_path (str): The path to a JSON-formatted config file
        containing the database connection string parameters
    Returns:

    """
    connection = getmaps.database_connect(config_path)
    return getmaps.get_all_locations(connection)

def _write_locations_to_csv(locations: List[getmaps.Location]) -> str:
    """
    Writes the locations returned by getmaps.get_all_locations() to a CSV
    file that can be read and used by the clustering algorithm
    Args:
        locations (List[getmaps.Location]): A list of Locations to
        convert to CSV format and write to file
    Returns:
        str: The path of the file that's been written to
    """
    csv_path = '.\\data.csv'
    with open(csv_path, 'w+') as csv_file:
        writer = csv.writer(csv_file, delimiter=',', lineterminator='\n')
        writer.writerow(['X', 'Y', 'Latitude', 'Longitude', 'Address', 'UPRN'])
        for location in locations:
            writer.writerow(list(location))
    return csv_path

def _get_locations_from_cluster(
        locations: List[getmaps.Location],
        cluster: List[List[float]]) -> List[getmaps.Location]:
    """
    Iterates over the list of all Location objects and matches the
    X/Y float values for the values of each point in a cluster
    Args:
        locations (List[getmaps.Location]): A list of Location objects
        cluster (List[List[float, float]]): A nested list of X/Y pairs, each
        pair represents a point in a cluster and the top-level list is the
        cluster as a whole
    Returns:
        List[getmaps.Location]: A list of Locations that directly maps to
        a cluster.
    """
    cluster_locations = []
    for location in locations:
        for point in cluster:
            if (location.x == '{:.2f}'.format(point[0]) and
                    location.y == '{:.2f}'.format(point[1])):
                cluster_locations.append(location)
    return cluster_locations


if __name__ == '__main__':
    locations = _get_all_locations('.\\.config')
    csv_path = _write_locations_to_csv(locations)
    X = clustering.load_csv_data(csv_path)
    # Episilon and minimum sampling values
    # db = clustering.get_db_object(X, 0.0002, 2)
    db = clustering.get_db_object(X, 0.09, 2)
    clusters = clustering.get_db_clusters(X, db)
    clustering.plot_db_clusters(X, db)
    cluster_locations_list = []
    for cluster in clusters:
        cluster_locations = _get_locations_from_cluster(locations, cluster.tolist())
        cluster_locations_list.append(cluster_locations)
    print(len(cluster_locations_list))
