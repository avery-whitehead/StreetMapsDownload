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


def open_maps(uprn: str, scales: List[int]) -> List['Image']:
    """
    Opens the two map image files to be placed on the page
    Args:
        uprn (str): The UPRN of the location on the maps, used to get the
        filenames
        scales (List[int]): A list of the zoom levels of the images, suffixed
        to the filenames
    Returns:
        List[Image]: A list of two Images containing the loaded maps
    """
    return [
        Image.open(f'.\\img\\{uprn}-{str(scales[0])}.jpg').convert('RGB'),
        Image.open(f'.\\img\\{uprn}-{str(scales[1])}.jpg').convert('RGB')]


def write_text_on_template(
        addr_str: str,
        uprn: str,
        template: Image) -> Image:
    """
    Creates a text box using the Pillow ImageFont and ImageDraw object,
    fills it with the address of the location on the maps and writes it on
    the template
    Args:
        addr_str (str): The address of the location on the maps
        uprn (str): The UPRN of the location on the maps
        template (Image): The template to write the text on
    Returns:
        Image: The template with the text added
    """
    draw = ImageDraw.Draw(template)
    font_path = 'C:\\Windows\\Fonts\\OpenSans-Regular.ttf'
    font = ImageFont.truetype(font_path, 96)
    draw.text((150, 150), f'{uprn}\n{addr_str}', 'black', font=font)
    return template


def paste_maps(template: Image, maps: List['Image']) -> Image:
    """
    Overlays the map images on to the template image
    Args:
        template (Image): The base template image
    Returns:
        Image: The template image with the map images pasted on
    """
    template.paste(maps[0], (148, 652))
    template.paste(maps[1], (148, 4217))
    return template


def draw_circle_on_template(print_map: Image):
    """
    Draws a circle over the centre of the maps (so needs to be called atfer
    paste_maps)
    Args:
        print_map (Image): The base template Image with the maps already
        pasted on
    """
    # [top left x, top left y, bottom right x, bottom right y]
    top_mask = __draw_ellipse(print_map, [2334, 2321, 2521, 2508], 12, 4)
    bot_mask = __draw_ellipse(print_map, [2236, 5311, 2686, 5761], 20, 4)
    print_map.paste('black', mask=top_mask)
    print_map.paste('black', mask=bot_mask)
    return print_map


def __draw_ellipse(
        img: Image,
        bounds: List[int],
        width: int,
        antialias: int) -> Image:
    """
    Helper function for drawing ellipses with a specified thickness.
    Credit to https://stackoverflow.com/a/34926008
    Args:
        img (Image): The image to paste the ellipse on
        bounds List[int]: The bounding box the circle occupies. Takes the
        format [top left x, top left y, bottom right x, bottom right y]
        width: The width of the ellipse line (px)
        antialiasing: The level of antialising to apply to the line
    """
    # Use a single channel image (mode='L') as mask
    mask = Image.new(
        size=[int(dim * antialias) for dim in img.size],
        mode='L', color='black')
    draw = ImageDraw.Draw(mask)
    # Draw outer shape in outline colour and inner shape in black/transparent
    for offset, fill in (width / -2.0, 'white'), (width / 2.0, 'black'):
        left, top = [(value + offset) * antialias for value in bounds[:2]]
        right, bottom = [(value - offset) * antialias for value in bounds[2:]]
        draw.ellipse([left, top, right, bottom], fill=fill)
    # Downsample the mask using PIL.Image.LANCZOS
    return mask.resize(img.size, Image.LANCZOS)


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
