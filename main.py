"""
main.py
Uses the classes and functions in getmaps.py and createprints.py to
get and layout three different elevations of maps on a page
"""

import getmaps
import createprints
import pyodbc

if __name__ == '__main__':
    try:
        # Connect to the database
        connection = getmaps.database_connect('.\\.config')
        # Get the UPRN from command line arguments or user input
        (uprn, map_type) = getmaps.get_input()
        location = getmaps.get_location_from_uprn(connection, uprn)
        location.print_location()
        # Get the maps
        if map_type == 'Esri':
            # Most zoomed in to least zoomed in
            scales = [1500, 10000, 25000]
            maps = [
                getmaps.get_arcgis_map(location, scales[0], 4663, 3210),
                getmaps.get_arcgis_map(location, scales[1], 2225, 3358),
                getmaps.get_arcgis_map(location, scales[2], 2225, 3358)]
        if map_type == 'Mapbox':
            # Most zoomed in to least zoomed in
            scales = [17, 14, 11]
            #Mapbox API sizes are limited to 1028x1028
            maps = [
                getmaps.get_mapbox_map(location, scales[0], 1020, 702),
                getmaps.get_mapbox_map(location, scales[1], 487, 735),
                getmaps.get_mapbox_map(location, scales[2], 487, 735)]
        # Print the maps
        template = createprints.open_template(map_type)
        map_images = createprints.open_maps(uprn, map_type, scales)
        print_map = createprints.paste_maps(map_type, template, map_images)
        result = createprints.save_print(uprn, map_type, print_map, 'pdf')
        print(result)
    except (pyodbc.DatabaseError, pyodbc.InterfaceError, ValueError) as error:
        print(error)
