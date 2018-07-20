"""
main_postcodes_overview.py
Uses the classes and functions in getmaps.py and createprints.py to
create a map for each postcode. Creates a single overview map at a high
scale, unlike the several multi-scale maps genereated by main_postcodes.py
"""

from typing import List
import getmaps
import createprints

def _get_all_locations(config_path: str) -> List[getmaps.Location]:
    """
    Wrapper for getmaps.get_all_locations()
    Args:
        config_path (str): The path to a JSON-formatted config file
        containing the database connection string parameters
    Returns:
        List[getmaps.Location]: A list of all Location objects returned
        by a query
    """
    connection = getmaps.database_connect(config_path)
    return getmaps.get_all_locations(connection)


if __name__ == '__main__':
    locations = _get_all_locations('.\\.config')
    template = createprints.open_template()
    scales = [20000]
    maps = [getmaps.get_clustered_map(
        locations, scales[0], 175, 35, 4663, 6214, 96, 'overview')]
    template = createprints.write_text_on_template(
        'Overview map for round changes 2018-07-20',
        template)
    map_image = createprints.open_maps('overview', scales)[0]
    final_map = createprints.paste_single_map(template, map_image)
    result = createprints.save_print('overview', final_map, 'pdf')
    print(result)
    