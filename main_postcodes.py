"""
main_postcodes.py
Uses the classes and functions in getmaps.py and createprints.py to
create a map for each postcode. Does not use an actual clustering
algorithm unlike main_clusters.py
"""

from collections import defaultdict
from random import shuffle
from typing import List, Tuple
from getmaps import Location
import getmaps
import createprints

class Postcode:
    """
    Contains the Locations that are under the same postcode
    """
    def __init__(
            self,
            postcode: str,
            locations: List[Location],
            fill_colour: Tuple[int, int, int, int],
            outline_colour: Tuple[int, int, int, int]):
        """
        Args:
            postcode (str): The postcode of this object
            locations (List[Location]): The list of locations that share
            this postcode
            fill_colour (Tuple[int, int, int, int]): The RGBA colour used
            to fill the circles that identify this postcode on the map
            outline_colour (Tuple[int, int, int, int]): The RGBA colour used
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


def _get_colours(
        index: int
    ) -> Tuple[Tuple[int, int, int, int], Tuple[int, int, int, int]]:
    """
    Gets a colour value to instantiate a Postcode object based on its index
    in the dictionary. Colours found at https://www.materialui.co/colors
    Args:
        index(int): The index of the postcode in the dictionary
    Returns:
        Tuple[Tuple[int, int, int, int], Tuple[int, int, int, int]]: A pair
        of RGBA tuples for the fill and outline colours
    """
    fill_colours = [
        (229, 115, 115, 255),
        (240, 98, 146, 255),
        (86, 104, 200, 255),
        (149, 117, 205, 255),
        (121, 134, 203, 255),
        (100, 181, 246, 255),
        (79, 195, 247, 255),
        (77, 208, 225, 255),
        (77, 182, 172, 255),
        (129, 199, 132, 255),
        (174, 213, 129, 255),
        (220, 231, 117, 255),
        (255, 241, 118, 255),
        (255, 213, 79, 255),
        (255, 183, 77, 255),
        (255, 138, 101, 255),
        (161, 136, 127, 255),
        (224, 224, 224, 255),
        (144, 164, 174, 255)]
    outline_colours = [
        (244, 67, 54, 255),
        (233, 30, 99, 255),
        (156, 39, 176, 255),
        (103, 58, 183, 255),
        (63, 81, 181, 255),
        (33, 150, 243, 255),
        (3, 169, 244, 255),
        (0, 188, 212, 255),
        (0, 150, 136, 255),
        (76, 175, 80, 255),
        (139, 195, 74, 255),
        (205, 220, 57, 255),
        (255, 235, 59, 255),
        (255, 193, 7, 255),
        (255, 152, 0, 255),
        (255, 87, 34, 255),
        (121, 85, 72, 255),
        (158, 158, 158, 255),
        (96, 125, 139, 255)]
    return (
        fill_colours[index % len(fill_colours)],
        outline_colours[index % len(outline_colours)])

if __name__ == '__main__':
    locations = _get_all_locations('.\\.config')
    postcode_groups = _group_locations_by_postcode(locations)
    postcode_objs = []
    for index, (postcode, group) in enumerate(postcode_groups.items()):
        # Create a Postcode object for each postcode
        colour = _get_colours(index)
        postcode_objs.append(Postcode(postcode, group, colour[0], colour[1]))
    # Shuffle the Postcode objects so the colour distribution is less uniform
    shuffle(postcode_objs)
    for postcode_obj in postcode_objs:
        postcode_obj.print_postcode()
        template = createprints.open_template()
        scales = [1750, 10000]
        maps = [
            getmaps.get_clustered_map(
                postcode_obj.locations,
                scales[0],
                20,
                postcode_obj.fill_colour,
                3,
                postcode_obj.outline_colour,
                4663,
                3502,
                600,
                postcode_obj.postcode),
            getmaps.get_clustered_map(
                postcode_obj.locations,
                scales[1],
                10,
                postcode_obj.fill_colour,
                1.5,
                postcode_obj.outline_colour,
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
