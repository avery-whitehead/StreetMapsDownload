"""
main.py
TODO:
createprints.py
"""

import getmaps
import pyodbc

if __name__ == '__main__':
    try:
        # Connect to the database
        connection = getmaps.database_connect('.\\.config')
        # Get the UPRN from command line arguments or user input
        (uprn, map_type) = getmaps.get_input()
        location = getmaps.get_location_from_uprn(connection, uprn)
        location.print_location()
        if map_type == 'Esri':
            getmaps.get_arcgis_map(location, 1500, 4663, 3210)
            getmaps.get_arcgis_map(location, 10000, 2225, 3358)
            getmaps.get_arcgis_map(location, 25000, 2225, 3358)
        if map_type == 'Mapbox':
            #Mapbox API sizes are limited to 1028x1028
            getmaps.get_mapbox_map(location, 17, 1020, 702)
            getmaps.get_mapbox_map(location, 14, 487, 735)
            getmaps.get_mapbox_map(location, 11, 487, 735)
    except (pyodbc.DatabaseError, pyodbc.InterfaceError, ValueError) as error:
        print(error)
