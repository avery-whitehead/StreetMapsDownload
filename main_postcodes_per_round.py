"""
main_postcodes_per_round.py
Uses the classes and functions in getmaps.py and createprints.py to
create a map for each postcode on each round. Does not use an
actual clustering algorithm unlike main_clusters.py
"""

import os
import glob
from collections import defaultdict
from typing import List, Tuple
from colorsys import rgb_to_hls
from PyPDF2 import PdfFileMerger, PdfFileReader
from getmaps import Location
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
            outline_colour: Tuple[int],
            rounds: List[str]):
        """
        Args:
            postcode (str): The postcode of this object
            locations (List[Location]): The list of locations that share
            this postcode
            fill_colour (Tuple[int]): The RGBA colour used
            to fill the circles that identify this postcode on the map
            outline_colour (Tuple[int]): The RGBA colour used
            to outline the circles that identify this postcode on the map
            rounds (List[str]): The list of rounds that serve this postcode
        """
        self.postcode = postcode
        self.locations = locations
        self.fill_colour = fill_colour
        self.outline_colour = outline_colour
        self.rounds = rounds


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
    postcode_list = defaultdict(list)
    for location in locations:
        postcode_list[location.postcode].append(location)
    return postcode_list


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
    colours.sort(key=lambda x: rgb_to_hls(x[0][0], x[0][1], x[0][2]))
    return colours


def _get_rounds(config_path: str) -> List[str]:
    """
    Gets a list of the unique round type and number pairs that have been
    changed
    Args:
        config_path (str): The path to a JSON-formatted config file
        containing the database connection string parameters
    Returns:
        List[str]: A list of round type and number pairs with no duplicate
        values
    """
    connection = getmaps.database_connect(config_path)
    rounds = []
    with open ('.\\get_rounds.sql', 'r') as rounds_query_f:
        rounds_query = rounds_query_f.read()
    cursor = connection.cursor()
    cursor.execute(rounds_query)
    rows = cursor.fetchall()
    for row in rows:
        for col in row:
            if col != None:
                rounds.append(col)
    return list(set(rounds))


def _assign_rounds_to_postcodes(postcode_objs: List[Postcode]) -> List[Postcode]:
    """
    Fills in the rounds attribute of a Postcode object with the rounds
    of the Location objects in its locations attribute
    Args:
        postcode_objs (List[Postcode]): The list of Postcode objects
    Returns:
        List[Postcode]: The list of Postcode objects, now with rounds attached
    """
    for postcode_obj in postcode_objs:
        rounds = []
        for location in postcode_obj.locations:
            for rnd in location.rounds:
                if rnd not in rounds and rnd is not None:
                    rounds.append(rnd)
        postcode_obj.rounds = rounds
    return postcode_objs


def _merge_pdfs(rounds: List[str]) -> None:
    """
    Creates a list of lists, where each sublist is a group of PDFs in the
    same round. Merges the PDFs into one file in the same order as the
    list
    Args:
        rounds (List[str]): The list of rounds
    """
    round_pdfs = []
    pdf_files = glob.glob('.\\img\\*.pdf')
    for rnd in rounds:
        round_pdf = [
            f for f in pdf_files
            if f'{rnd}-' in f
            and 'overview' not in f]
        if os.path.exists(f'.\\img\\{rnd}-overview.pdf'):
            round_pdf[:0] = [f'.\\img\\{rnd}-overview.pdf']
        round_pdfs.append(round_pdf)
    # Flatten list
    round_pdfs = [pdf for pdf_list in round_pdfs for pdf in pdf_list]
    print(round_pdfs)
    merger = PdfFileMerger()
    for pdf in round_pdfs:
        merger.append(PdfFileReader(pdf), 'rb')
    with open('.\\test.pdf', 'wb') as pdf_out:
        merger.write(pdf_out)
    merger.close()


def _cleanup_files() -> None:
    """
    Removes all the PDFs and images from the ./img folder except
    the template image
    """
    # Gets a flat list of all PDF and JPG files
    files = [
        f for f_ in [
            glob.glob(ext) for ext in ('.\\img\\*.jpg', '.\\img\\*.pdf')]
        for f in f_]
    files.remove('.\\img\\template.jpg')
    for f in files:
        os.remove(f)


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
            colours[index][1],
            None))
    postcode_objs.sort(key=lambda x: (sum([float(i.lat) for i in x.locations]) / len(x.locations)) + sum([float(i.lng) for i in x.locations]) / len(x.locations))
    postcode_objs = _assign_rounds_to_postcodes(postcode_objs)
    rounds = _get_rounds('.\\.config')
    for rnd in rounds:
        rnd_postcodes = [p for p in postcode_objs if rnd in p.rounds]
        # Creates an overview map out of all the postcodes in this round
        template = createprints.open_template()
        template = createprints.write_text_on_template(f'{rnd} Overview', template)
        scales = [60000]
        maps = [getmaps.get_clustered_map(
            rnd_postcodes,
            scales[0],
            90,
            15,
            4663,
            6214,
            128,
            'overview')]
        map_image = createprints.open_maps('overview', scales)[0]
        final_map = createprints.paste_single_map(template, map_image)
        result = createprints.save_print(f'{rnd}-overview', final_map, 'pdf')
        print(result)
        # Creates a map for each postcode in the round
        for postcode_obj in rnd_postcodes:
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
                f'{rnd}, ' \
                f'{postcode_obj.locations[0].street}, ' \
                f'{postcode_obj.locations[0].town}, ' \
                f'{postcode_obj.postcode}',
                template)
            map_images = createprints.open_maps(postcode_obj.postcode, scales)
            pasted = createprints.paste_maps(template, map_images)
            result = createprints.save_print(
                f'{rnd}-{postcode_obj.postcode}', pasted, 'pdf')
            print(result)
    _merge_pdfs(rounds)
    _cleanup_files()
