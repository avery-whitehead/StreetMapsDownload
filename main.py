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
        uprn = getmaps.get_uprn_from_input()
        location = getmaps.get_location_from_uprn(connection, uprn)
        location.print_location()
        # Get the maps
        template = createprints.open_template()
        # Most zoomed in to least zoomed in
        scales = [1000, 10000]
        maps = [
            getmaps.get_arcgis_map(location, scales[0], 4663, 3502, 600),
            getmaps.get_arcgis_map(location, scales[1], 4663, 2649, 1200)]
        template = createprints.write_text_on_template(
            location.address, uprn, template)
        # Create and print the maps
        map_images = createprints.open_maps(uprn, scales)
        print_map = createprints.paste_maps(template, map_images)
        final_maps = createprints.draw_circle_on_template(print_map)
        result = createprints.save_print(uprn, final_maps, 'pdf')
        print(result)
    except (pyodbc.DatabaseError, pyodbc.InterfaceError, ValueError) as error:
        print(error)
