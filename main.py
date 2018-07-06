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
        template = createprints.open_template(map_type)
        if map_type == 'Esri':
            # Most zoomed in to least zoomed in
            scales = [1000, 10000]
            maps = [
                getmaps.get_arcgis_map(location, scales[0], 4663, 3502),
                getmaps.get_arcgis_map(location, scales[1], 4663, 2649)]
            template = createprints.write_text_on_template(
                location.address, uprn, map_type, template)
        if map_type == 'Mapbox':
            # Most zoomed in to least zoomed in
            scales = [17, 14]
            #Mapbox API sizes are limited to 1028x1028
            maps = [
                getmaps.get_mapbox_map(location, scales[0], 957, 719),
                getmaps.get_mapbox_map(location, scales[1], 957, 544)]
            template = createprints.write_text_on_template(
                location.address, uprn, map_type, template)
        # Create and print the maps
        map_images = createprints.open_maps(uprn, map_type, scales)
        print_map = createprints.paste_maps(map_type, template, map_images)
        final_maps = createprints.draw_circle_on_template(map_type, print_map)
        result = createprints.save_print(uprn, map_type, final_maps, 'pdf')
        print(result)
    except (pyodbc.DatabaseError, pyodbc.InterfaceError, ValueError) as error:
        print(error)
