"""
createprints.py
Uses the Pillow library to organise the images created by getmaps.py on
an A4 sheet and convert that to a printable PDF
"""

from typing import List
from PIL import Image

def open_template(map_type: str) -> Image:
    """
    Opens a template image based on the type of map being used.
    Args:
        map_type (str): Either 'Mapbox' or 'Esri'. Mapbox images have to be
        smaller than Esri images, so the template needs to be smaller too
    Returns:
        Image: The imported template file
    """
    if map_type == 'Esri':
        template = Image.open('.\\img\\template.png')
    if map_type == 'Mapbox':
        template = Image.open('.\\img\\template_small.png')
    return template

def open_maps(uprn: str, map_type: str, scales: List[int]) -> List['Image']:
    """
    Opens the three map image files to be placed on the page
    Args:
        uprn (str): The UPRN of the location the maps depict, used to get
        the filenames
        map_type (str): Either 'Mapbox' or 'Esri'. Different map types
        have different filenames
        scales (List[int]): A list of the zoom levels of the images, suffixed
        to the filenames
    Returns:
        List[Image]: A list of three Images containing the loaded maps
    """
    return [
        Image.open(f'.\\img\\{map_type.lower()}-{uprn}-{str(scales[0])}.png'),
        Image.open(f'.\\img\\{map_type.lower()}-{uprn}-{str(scales[1])}.png'),
        Image.open(f'.\\img\\{map_type.lower()}-{uprn}-{str(scales[2])}.png')]

def paste_maps(map_type: str, template: Image, maps: List['Image']) -> Image:
    """
    Overlays the map images on to the template image
    Args:
        map_type (str): Either 'Mapbox' or 'Esri'. Each map type has a
        diferent template, so a different location of the maps on the page
        template (Image): The base template image
    """
    pass
