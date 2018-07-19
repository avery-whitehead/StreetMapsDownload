"""
main_postcodes.py
Uses the classes and functions in getmaps.py and createprints.py to
create a map for each postcode. Does not use an actual clustering
algorithm unlike main_clusters.py
"""

from collections import defaultdict
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


def _group_locations_by_postcode(
        locations: List[getmaps.Location]) -> List[List[getmaps.Location]]:
    """
    Groups a list of Location objects into a nested list, where each sublist
    contains the Location objects with the same postcode
    Args:
        locations (List[getmaps.Location]): The list of Location objects to
        group
    Returns:
        List[List[getmaps.Location]]: The nested list of grouped Location
        objects
    """
    postcode_dict = defaultdict(list)
    for location in locations:
        postcode_dict[location.postcode].append(location)
    return postcode_dict


if __name__ == '__main__':
    locations = _get_all_locations('.\\.config')
    postcode_groups = _group_locations_by_postcode(locations)
    for postcode, group in postcode_groups.items():
        template = createprints.open_template()
        scales = [1750, 10000]
        maps = [
            getmaps.get_clustered_map(
                group, scales[0], 20, 3, 4663, 3502, 600),
            getmaps.get_clustered_map(
                group, scales[1], 10, 1.5, 4663, 2649, 1200)]
        template = createprints.write_text_on_template(
            f'{group[0].street}, {group[0].town}, {postcode}',
            template)
        map_images = createprints.open_maps(postcode, scales)
        final_maps = createprints.paste_maps(template, map_images)
        result = createprints.save_print(postcode, final_maps, 'pdf')
        print(result)
