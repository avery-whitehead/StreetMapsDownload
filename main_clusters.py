"""
main_clusters.py
Uses the classes and functions in getmaps.py, createprints.py and
clusters.py to create a map for a series of clusters containing
multiple properties and points of interest
"""

import csv
import getmaps
# import createprints
import clustering

def _write_locations_to_csv(config_path: str) -> str:
    """
    Writes the locations returned by getmaps.get_all_locations() to a CSV
    file that can be read and used by the clustering algorithm
    Args:
        config_path (str): The path to a JSON-formatted config file
        containing the database connection string parameters
    Returns:
        str: The path of the file that's been written to
    """
    connection = getmaps.database_connect(config_path)
    locations = getmaps.get_all_locations(connection)
    csv_path = '.\\data.csv'
    with open(csv_path, 'w+') as csv_file:
        writer = csv.writer(csv_file, delimiter=',', lineterminator='\n')
        writer.writerow(['X', 'Y', 'Latitude', 'Longitude', 'Address', 'UPRN'])
        for location in locations:
            writer.writerow(list(location))
    return csv_path


if __name__ == '__main__':
    csv_path = _write_locations_to_csv('.\\.config')
    X = clustering.load_csv_data(csv_path)
    # Episilon and minimum sampling values
    db = clustering.get_db_object(X, 0.0003, 3)
    clusters = clustering.get_db_clusters(X, db)
    clustering.plot_db_clusters(X, db)
    print(clusters)