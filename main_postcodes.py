"""
main_postcodes.py
Uses the classes and functions in getmaps.py and createprints.py to
create a map for each postcode. Does not use an actual clustering
algorithm unlike main_clusters.py
"""

from colorsys import hls_to_rgb
from collections import defaultdict
from typing import List, Tuple
from getmaps import Location
import random
import getmaps
import createprints
import colourgen

class Postcode:
    """
    Contains the Locations that are under the same postcode
    """
    def __init__(
            self,
            postcode: str,
            locations: List[Location],
            fill_colour: Tuple[int],
            outline_colour: Tuple[int]):
        """
        Args:
            postcode (str): The postcode of this object
            locations (List[Location]): The list of locations that share
            this postcode
            fill_colour (Tuple[int]): The RGBA colour used
            to fill the circles that identify this postcode on the map
            outline_colour (Tuple[int]): The RGBA colour used
            to outline the circles that identify this postcode on the map
        """
        self.postcode = postcode
        self.locations = locations
        self.fill_colour = fill_colour
        self.outline_colour = outline_colour


    def print_postcode(self):
        """
        Prints the values stored in each variable. Each line is formatted
        <name>: <value>
        """
        for attr, value in self.__dict__.items():
            print(f'{attr}: {value}')


def _get_all_locations(config_path: str) -> List[Location]:
    """
    Wrapper for getmaps.get_all_locations()
    Args:
        config_path (str): The path to a JSON-formatted config file
        containing the database connection string parameters
    Returns:
        List[Location]: A list of all Location objects returned
        by a query
    """
    connection = getmaps.database_connect(config_path)
    return getmaps.get_all_locations(connection)


def _group_locations_by_postcode(
        locations: List[Location]) -> List[List[Location]]:
    """
    Groups a list of Location objects into a nested list, where each sublist
    contains the Location objects with the same postcode
    Args:
        locations (List[Location]): The list of Location objects to
        group
    Returns:
        List[List[Location]]: The nested list of grouped Location
        objects
    """
    postcode_dict = defaultdict(list)
    for location in locations:
        postcode_dict[location.postcode].append(location)
    return postcode_dict


def _generate_colours(amount: int) -> List[List[Tuple[int]]]:
    """
    Creates a list of uniformly distributed RGBA colours. Colour values
    in Python are between 0 and 1, but the values in the ArcGIS webmap JSON
    are between 0 and 255.
    Args:
        amount (int): The amount of colours to generate
    Returns:
        List[List[Tuple[int]]]: A list of pairs of RGBA colours - the
        first element in the pair is the fill colour, the second is the
        outline colour
    """
    colours = []
    fill = colourgen.get_rgb_fill(amount)
    for i in range(amount):
        line = (fill[i][0] - 45, fill[i][1] - 45, fill[i][2], 255)
        colours.append([fill[i], line])
    return colours



if __name__ == '__main__':
    locations = _get_all_locations('.\\.config')
    postcode_groups = _group_locations_by_postcode(locations)
    postcode_objs = []
    colours = _generate_colours(len(postcode_groups))
    for index, (postcode, group) in enumerate(postcode_groups.items()):
        # Create a Postcode object for each postcode
        postcode_objs.append(Postcode(
            postcode,
            group,
            colours[index][0],
            colours[index][1]))
    # Creates an overview map out of all the postcodes
    template = createprints.open_template()
    scales = [23000]
    maps = [getmaps.get_clustered_map(
        postcode_objs,
        scales[0],
        90,
        15,
        4663,
        6214,
        128,
        'overview')]
    map_image = createprints.open_maps('overview', scales)[0]
    final_map = createprints.paste_single_map(template, map_image)
    result = createprints.save_print('overview', final_map, 'pdf')
    print(result)
    for postcode_obj in postcode_objs:
        template = createprints.open_template()
        scales = [1750, 10000]
        maps = [
            getmaps.get_clustered_map(
                [postcode_obj],
                scales[0],
                20,
                3,
                4663,
                3502,
                600,
                postcode_obj.postcode),
            getmaps.get_clustered_map(
                [postcode_obj],
                scales[1],
                10,
                1.5,
                4663,
                2649,
                1200,
                postcode_obj.postcode)]
        template = createprints.write_text_on_template(
            f'{postcode_obj.locations[0].street}, ' \
            f'{postcode_obj.locations[0].town}, ' \
            f'{postcode_obj.postcode}',
            template)
        map_images = createprints.open_maps(postcode_obj.postcode, scales)
        pasted = createprints.paste_maps(template, map_images)
        result = createprints.save_print(postcode_obj.postcode, pasted, 'pdf')
        print(result)
