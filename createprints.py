"""
createprints.py
Uses the Pillow library to organise the images created by getmaps.py on
an A4 sheet and convert that to a printable PDF
"""

from typing import List
from PIL import Image, ImageFont, ImageDraw


def open_template() -> Image:
    """
    Opens a base template image
    Returns:
        Image: The imported template file
    """
    template = Image.open('.\\img\\template.jpg')
    return template


def open_maps(prefix: str, scales: List[int]) -> List['Image']:
    """
    Opens the two map image files to be placed on the page
    Args:
        prefix (str): The filename prefix
        scales (List[int]): A list of the zoom levels of the images, suffixed
        to the filenames
    Returns:
        List[Image]: A list of two Images containing the loaded maps
    """
    maps = []
    for scale in scales:
        maps.append(
            Image.open(f'.\\img\\{prefix}-{str(scale)}.jpg').convert('RGB'))
    return maps


def write_text_on_template(
        addr_str: str,
        template: Image) -> Image:
    """
    Creates a text box using the Pillow ImageFont and ImageDraw object,
    fills it with the address of the location on the maps and writes it on
    the template
    Args:
        addr_str (str): The address of the location on the maps
        template (Image): The template to write the text on
    Returns:
        Image: The template with the text added
    """
    draw = ImageDraw.Draw(template)
    font_path = 'C:\\Windows\\Fonts\\OpenSans-Regular.ttf'
    font = ImageFont.truetype(font_path, 96)
    draw.text((150, 150), f'{addr_str}', 'black', font=font)
    return template


def paste_maps(template: Image, maps: List['Image']) -> Image:
    """
    Overlays the map images on to the template image
    Args:
        template (Image): The base template image
        maps (List[Image]): The list of images to paste on the template
    Returns:
        Image: The template image with the map images pasted on
    """
    template.paste(maps[0], (148, 652))
    template.paste(maps[1], (148, 4217))
    return template

def paste_single_map(template: Image, map_: Image) -> Image:
    """
    Overlays a single map image on to the template image
    Args:
        template (Image): The base template image
        map_ (Image): The single image to paste on the template
    Returns:
        Image: The template image with the map image pasted on
    """
    paste_coords = (148, 652)
    template.paste(map_, paste_coords)
    return template


def save_print(uprn: str, print_map: Image, ext: str) -> str:
    """
    Saves the print of all the maps in the template to file
    Args:
        uprn (str): The UPRN of the location depicted in the map
        print_map (Image): The image of the map to save to file
        ext (str): The file extension/format to save as (PDF or JPEG)
    """
    save_path = f'.\\img\\{uprn}.{ext}'
    print_map.save(save_path, format=ext, resolution=300)
    return f'Saved image: {save_path}'
