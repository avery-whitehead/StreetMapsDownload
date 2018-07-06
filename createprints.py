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
        template = Image.open('.\\img\\template.jpg')
    if map_type == 'Mapbox':
        template = Image.open('.\\img\\template_small.jpg')
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
    partial_path = f'.\\img\\{map_type.lower()}-{uprn}'
    return [
        Image.open(f'{partial_path}-{str(scales[0])}.jpg').convert('RGB'),
        Image.open(f'{partial_path}-{str(scales[1])}.jpg').convert('RGB'),
        Image.open(f'{partial_path}-{str(scales[2])}.jpg').convert('RGB')]

def paste_maps(map_type: str, template: Image, maps: List['Image']) -> Image:
    """
    Overlays the map images on to the template image
    Args:
        map_type (str): Either 'Mapbox' or 'Esri'. Each map type has a
        diferent template, so a different location of the maps on the page
        template (Image): The base template image
    Returns:
        Image: The template image with the map images pasted on
    """
    if map_type == 'Esri':
        template.paste(maps[0], (148, 149))
        template.paste(maps[1], (148, 3508))
        template.paste(maps[2], (2586, 3508))
    if map_type == 'Mapbox':
        template.paste(maps[0], (63, 64))
        template.paste(maps[1], (63, 1532))
        template.paste(maps[2], (1129, 1532))
    return template

def save_print(uprn: str, map_type: str, print_map: Image, ext: str) -> str:
    """
    Saves the print of all the maps in the template to file
    Args:
        uprn (str): The UPRN of the location depicted in the map
        map_type (str): Either 'Mapbox' or 'Esri'
        print_map (Image): The image of the map to save to file
        ext (str): The file extension/format to save as (PDF or JPEG)
    """
    save_path = f'.\\img\\{map_type.lower()}-{uprn}.{ext}'
    print_map.save(save_path, format=ext, resolution=300)
    return f'Saved image: {save_path}'

