"""
getmaps.py
A custom Location class and a series of functions used to perform a request to
either the ArcGIS or Mapbox REST APIs to return a static map image
"""

from typing import Tuple
import json
import sys
import requests
import pyodbc

class Location:
    """
    Represents a geographical location associated with a UPRN
    """
    def __init__(
            self,
            x: str,
            y: str,
            lat: str,
            lng: str,
            address: str,
            uprn: str):
        """
        Args:
            x (str): The x-coordinate of this location
            y (str): The y-coordinate of this location
            lat (str): The latitude of this location
            lng (str): The longitude of this location
            address (str): The address of this location
            uprn (str): The UPRN of this location
        """
        self.x = x
        self.y = y
        self.lat = lat
        self.lng = lng
        self.address = address
        self.uprn = uprn

    def print_location(self):
        """
        Prints the values stored in each variable. Each line is formatted
        <name>: <value>
        """
        for attr, value in self.__dict__.items():
            print(f'{attr}: {value}')


def database_connect(config_path: str) -> pyodbc.Connection:
    """
    Creates a connection to a SQL Server database
    Args:
        config_path (str): The path to a JSON-formatted config file
        containing the connection string parameters
    Returns:
        pyodbc.Connection: A Connection object used as a connection
        to the database
    Raises:
        pyodbc.DatabaseError, pyodbc.InterfaceError: If the connection
        fails
    """
    with open (config_path, 'r') as config_f:
        config = json.load(config_f)
    return pyodbc.connect(
        driver=config['driver'],
        server=config['server'],
        database=config['database'],
        uid=config['uid'],
        pwd=config['pwd'])

def get_input() -> Tuple[str, str]:
    """
    Gets the UPRN and map type as a command line argument, or prompts the
    user for input if no command line argument exists
    Returns:
        Tuple[str, str]: The UPRN and the map type chosen by the user
    """
    # If there are too many arguments
    if len(sys.argv) != 3:
        print(f'{len(sys.argv) -1} arguments found (2 expected)')
    # If there is two extra argument found, check validity
    if len(sys.argv) == 3:
        uprn = sys.argv[1]
        map_type = sys.argv[2]
        if __check_validity(uprn, map_type):
            return (uprn, map_type)
    # If no arguments are found, prompt for input
    uprn = input('Enter a 12-digit UPRN: ')
    map_type = input('Enter a map type (\'Esri\' or \'Mapbox\'): ')
    if __check_validity(uprn, map_type):
        return (uprn, map_type)
    raise ValueError('There was a problem with the arguments')

def __check_validity(uprn: str, map_type: str) -> bool:
    """
    Checks whether the arguments given are valid
    Args:
        uprn: A 12-digit UPRN input
        map_type: A map type (either Mapbox or Esri) input
    Returns:
        bool: True if valid, False (but technically None) if invalid
    Raises:
        ValueError: If there are too many arguments or if the arguments aren't
        valid
    """
    if len(uprn) != 12:
        raise ValueError(f'{uprn} is not a valid UPRN')
    if (map_type != 'Esri') and (map_type != 'Mapbox'):
        raise ValueError(f'{map_type} is not a valid map type')
    return True


def get_location_from_uprn(conn: pyodbc.Connection, uprn: str) -> Location:
    """
    Queries the SQL database for the latitude, longitude and address
    associated with a UPRN and creates a Location object out of it
    Args:
        conn (pyodbc.Connection): The connection to the database to query
        uprn (str): The UPRN to query with
    Returns:
        Location: The Location object containing the latitude, longitude and
        address of the given UPRN, as well as the UPRN itself
    """
    with open('.\\get_location.sql', 'r') as loc_query_f:
        loc_query = loc_query_f.read()
    cursor = conn.cursor()
    cursor.execute(loc_query, uprn)
    loc = cursor.fetchone()
    return Location(
        str(loc.x), str(loc.y), str(loc.lat), str(loc.lng), loc.addr, uprn)

def get_mapbox_map(
        location: Location,
        zoom: str,
        x_size: str,
        y_size: str) -> None:
    """
    Uses the Requests library and the Mapbox API to download a static map
    image of the location
    Args:
        location (Location): The location to get a map for
        zoom (str): The zoom level of the map (minimum 0, maximum 20)
        x_size (str): The width of the output image (px)
        y_size (str): The height of the output image (px)
    """
    with open('./mapbox.key', 'r') as key_f:
        access_token = key_f.read()
    map_uri = 'https://api.mapbox.com/styles/v1/mapbox/streets-v10/static/' \
    f'{location.lng},{location.lat},{zoom},0,0/{x_size}x{y_size}@2x?' \
    f'access_token={access_token}'
    # Download image to file
    req = requests.get(map_uri)
    if req.status_code == 200:
        img_path = f'./img/mapbox-{location.uprn}-{zoom}.png'
        with open(img_path, 'wb') as image_f:
            image_f.write(req.content)

def get_arcgis_map(
        location: Location,
        scale: str,
        x_size: int,
        y_size: int) -> None:
    """
    Uses the Requests library and the ArcGIS to download a static map
    image of the location
    Args:
        location (Location): The location to get a map for
        scale (str): The scale to display the map at (higher numbers are more
        zoomed out)
        x_size (int): The width of the output image (px)
        y_size (int): The height of the output image (px)
    """
    map_uri = 'https://ccvgisapp01:6443/arcgis/rest/services/Printing/' \
        'HDCExportWebMap/GPServer/Export Web Map/execute'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    web_map = __get_json(location.x, location.y, scale, x_size, y_size)
    payload = {
        'Web_Map_as_JSON': web_map,
        'Format': 'PNG32',
        'f': 'json',
        'Layout_Template': 'MAP_ONLY'}
    cafile = '.\\cacert.pem'
    req = requests.post(map_uri, headers=headers, data=payload, verify=cafile)
    if req.status_code == 200:
        # Returns a JSON formatted bytes type
        resp = req.content.decode('utf8')
        img_url = json.loads(resp)['results'][0]['value']['url']
        img_req = requests.get(img_url)
        img_path = f'./img/esri-{location.uprn}-{scale}.png'
        with open(img_path, 'wb') as image_f:
            image_f.write(img_req.content)

def __get_json(x: str, y: str, scale: str, x_size: int, y_size: int) -> str:
    """
    Loads the JSON template from file, fills in the x and y values and
    removes the whitespace so it can be passed as a parameter to the ArcGIS API
    Args:
        x (str): The x-coordinate of the location
        y (str): The y-coordinate of the location
        scale (str): The scale to display the map at (higher numbers are more
        zoomed out)
        x_size (int): The width of the output image (px)
        y_size (int): The height of the output image (px)
    Returns:
        string: The filled in and formatted JSON template as a string
    """
    with open('.\\web_map.json', 'r') as web_map_f:
        web_map = json.load(web_map_f)
    web_map['mapOptions']['extent']['xmin'] = x
    web_map['mapOptions']['extent']['xmax'] = x
    web_map['mapOptions']['extent']['ymin'] = y
    web_map['mapOptions']['extent']['ymax'] = y
    web_map['mapOptions']['scale'] = scale
    web_map['exportOptions']['outputSize'] = [x_size, y_size]
    return str(web_map)
