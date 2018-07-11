"""
getmaps.py
A custom Location class and a series of functions used to perform a request to
either the ArcGIS or Mapbox REST APIs to return a static map image
"""

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
    with open(config_path, 'r') as config_f:
        config = json.load(config_f)
    return pyodbc.connect(
        driver=config['driver'],
        server=config['server'],
        database=config['database'],
        uid=config['uid'],
        pwd=config['pwd'])


def get_uprn_from_input() -> str:
    """
    Gets the UPRN as a command line argument, or prompts the user for
    input if no command line argument exists
    Returns:
        str: The UPRN input by the user
    Raises:
        ValueError: If there is more than one argument or if the
        argument isn't a valid UPRN
    """
    # If there are too many arguments
    if len(sys.argv) > 2:
        raise ValueError(f'{len(sys.argv) -1} arguments found (1 max)')
    # If there is one extra argument found, check validity
    if len(sys.argv) == 2:
        uprn = sys.argv[1]
        if len(uprn) != 12:
            raise ValueError(f'{uprn} is not a valid UPRN')
        return uprn
    # If no arguments are found, prompt for input
    uprn = input('Enter a 12-digit UPRN: ')
    return uprn


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


def get_arcgis_map(
        location: Location,
        scale: str,
        x_size: int,
        y_size: int,
        dpi: int) -> None:
    """
    Uses the Requests library and the ArcGIS to download a static map
    image of the location
    Args:
        location (Location): The location to get a map for
        scale (str): The scale to display the map at (higher numbers are more
        zoomed out)
        x_size (int): The width of the output image (px)
        y_size (int): The height of the output image (px)
        dpi (int): The DPI of the output image (default is 96)
    """
    map_uri = 'https://ccvgisapp01:6443/arcgis/rest/services/Printing/' \
        'HDCExportWebMap/GPServer/Export Web Map/execute'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    web_map = __get_json(location.x, location.y, scale, x_size, y_size, dpi)
    payload = {
        'Web_Map_as_JSON': web_map,
        'Format': 'JPG',
        'f': 'json',
        'Layout_Template': 'MAP_ONLY'}
    cafile = '.\\cacert.pem'
    req = requests.post(map_uri, headers=headers, data=payload, verify=cafile)
    if req.status_code == 200:
        # Returns a JSON formatted bytes type
        resp = req.content.decode('utf8')
        img_url = json.loads(resp)['results'][0]['value']['url']
        img_req = requests.get(img_url)
        img_path = f'./img/{location.uprn}-{scale}.jpg'
        with open(img_path, 'wb') as image_f:
            image_f.write(img_req.content)


def __get_json(
        x: str,
        y: str,
        scale: str,
        x_size: int,
        y_size: int,
        dpi: int) -> str:
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
        dpi (int): The DPI of the output image (default is 96)
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
    web_map['exportOptions']['dpi'] = dpi
    return str(web_map)
