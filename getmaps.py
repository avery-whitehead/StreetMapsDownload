"""
getmaps.py
A custom Location class and a series of functions used to perform a request to
either the ArcGIS or Mapbox REST APIs to return a static map image
"""

from typing import List, Tuple
import json
import sys
from shapely.geometry import MultiPoint
from latlon_to_bng import WGS84toOSGB36 as lat_long_to_x_y
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
            street: str,
            town: str,
            postcode: str,
            uprn: str):
        """
        Args:
            x (str): The x-coordinate of this location
            y (str): The y-coordinate of this location
            lat (str): The latitude of this location
            lng (str): The longitude of this location
            address (str): The full address of this location
            street (str): The street this location is on
            town (str): The town this location is in
            postcode (str): The postcode this location is in
            uprn (str): The UPRN of this location
        """
        self.x = x
        self.y = y
        self.lat = lat
        self.lng = lng
        self.address = address
        self.street = street
        self.town = town
        self.postcode = postcode
        self.uprn = uprn

    def print_location(self):
        """
        Prints the values stored in each variable. Each line is formatted
        <name>: <value>
        """
        for attr, value in self.__dict__.items():
            print(f'{attr}: {value}')

    def __iter__(self):
        """
        Overrides the bult-in __iter__ method to return a list of a
        Location's attributes
        """
        return iter([
            self.x,
            self.y,
            self.lat,
            self.lng,
            self.address,
            self.street,
            self.town,
            self.postcode,
            self.uprn])


def database_connect(config_path: str) -> pyodbc.Connection:
    """
    Creates a connection to a SQL Server database
    Args:
        config_path (str): The path to a JSON-formatted config file
        containing the connection string parameters
    Returns:
        pyodbc.Connection: A Connection object used as a connection
        to the database
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
    Queries the SQL database for the X, Y, latitude, longitude and address
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
        str(loc.x),
        str(loc.y),
        str(loc.lat),
        str(loc.lng),
        loc.addr,
        loc.street,
        loc.town,
        loc.postcode,
        uprn)


def get_all_locations(conn: pyodbc.Connection) -> List[Location]:
    """
    Queries the SQL database for every X, Y, latitude, longitude, address
    and UPRN under a specific constraint and creates a list of location
    objects containing each one
    Args:
        conn (pyodbc.Connection): The connection to the database to query
    Returns:
        List[Location]: A list of Location objects containing information
        about the locations returned by the SQL query
    """
    locations = []
    with open('.\\get_all_locations.sql', 'r') as loc_query_f:
        loc_query_all = loc_query_f.read()
    cursor = conn.cursor()
    cursor.execute(loc_query_all)
    locs = cursor.fetchall()
    for loc in locs:
        locations.append(Location(
            '{:.2f}'.format(loc.x),
            '{:.2f}'.format(loc.y),
            '{:.15f}'.format(loc.lat),
            '{:.15f}'.format(loc.lng),
            loc.addr,
            loc.street,
            loc.town,
            loc.postcode,
            str(loc.uprn)))
    return locations


def get_arcgis_map(
        location: Location,
        scale: str,
        x_size: int,
        y_size: int,
        dpi: int,
        prefix: str) -> None:
    """
    Uses the Requests library and the ArcGIS API to download a static map
    image of the location
    Args:
        location (Location): The location to get a map for
        scale (str): The scale to display the map at (higher numbers are more
        zoomed out)
        x_size (int): The width of the output image (px)
        y_size (int): The height of the output image (px)
        dpi (int): The DPI of the output image (default is 96)
        prefix(str): The filename prefix to save the file with
    """
    map_uri = 'https://ccvgisapp01:6443/arcgis/rest/services/Printing/' \
        'HDCExportWebMap/GPServer/Export Web Map/execute'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    web_map = _get_json(location.x, location.y, scale, x_size, y_size, dpi)
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
        img_path = f'./img/{prefix}-{scale}.jpg'
        with open(img_path, 'wb') as image_f:
            image_f.write(img_req.content)


def _get_json(
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


def get_clustered_map(
        cluster: List[Location],
        scale: str,
        circle_size: int,
        circle_colour: Tuple[int, int, int, int],
        outline_width: float,
        outline_colour: Tuple[int, int, int, int],
        x_size: int,
        y_size: int,
        dpi: int,
        prefix: str) -> None:
    """
    Uses the Requests library and the ArcGIS API to download a static map
    image of a cluster of locations, with each location highlighted with
    a marker
    Args:
        cluster (List[Location]): The cluster of locations to display on a map
        scale (str): The scale to display the map at (higher numbers are more
        zoomed out)
        circle_size (int): The radius of the circle markers
        circle_colour (Tuple[int, int, int, int]): RGBA colour value used to
        fill the circle
        outline_width (float): The width of the circle marker outline
        outline_colour (Tuple[int, int, int, int]): RGBA colour value used to
        draw the circle outline
        x_size (int): The width of the output image (px)
        y_size (int): The height of the output image (px)
        dpi (int): The DPI of the output image (default is 96)
        prefix(str): The filename prefix to save the file with
    """
    map_uri = 'https://ccvgisapp01:6443/arcgis/rest/services/Printing/' \
        'HDCExportWebMap/GPServer/Export Web Map/execute'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    web_map = _get_clustered_json(
        scale,
        circle_size,
        circle_colour,
        outline_width,
        outline_colour,
        cluster,
        x_size,
        y_size,
        dpi)
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
        img_path = f'./img/{prefix}-{scale}.jpg'
        with open(img_path, 'wb') as image_f:
            image_f.write(img_req.content)


def _get_clustered_json(
        scale: str,
        circle_size: int,
        circle_colour: Tuple[int, int, int, int],
        outline_width: float,
        outline_colour: Tuple[int, int, int, int],
        cluster: List[Location],
        x_size: int,
        y_size: int,
        dpi: int) -> str:
    """
    Loads the JSON template from file, fills in the x and y values and
    removes the whitespace so it can be passed as a parameter to the ArcGIS API
    Args:
        scale (str): The scale to display the map at (higher numbers are more
        zoomed out)
        circle_size (int): The radius of the circle markers
        circle_colour (Tuple[int, int, int, int]): RGBA colour value used to
        fill the circle
        outline_width (float): The width of the circle marker outline
        outline_colour (Tuple[int, int, int, int]): RGBA colour value used to
        draw the circle outline
        cluster (List[Location]): The cluster of Location objects to draw as
        features on the map
        x_size (int): The width of the output image (px)
        y_size (int): The height of the output image (px)
        dpi (int): The DPI of the output image (default is 96)
    Returns:
        string: The filled in and formatted JSON template as a string
    """
    with open('.\\web_map_clustered.json', 'r') as web_map_f:
        web_map = json.load(web_map_f)
    (x, y) = _get_centroid(cluster)
    web_map['mapOptions']['extent']['xmin'] = x
    web_map['mapOptions']['extent']['xmax'] = x
    web_map['mapOptions']['extent']['ymin'] = y
    web_map['mapOptions']['extent']['ymax'] = y
    web_map['mapOptions']['scale'] = scale
    web_map['operationalLayers'][0]['featureCollection']['layers'][0]['layerDefinition']['drawingInfo']['renderer']['symbol']['size'] = circle_size
    web_map['operationalLayers'][0]['featureCollection']['layers'][0]['layerDefinition']['drawingInfo']['renderer']['symbol']['color'] = list(circle_colour)
    web_map['operationalLayers'][0]['featureCollection']['layers'][0]['layerDefinition']['drawingInfo']['renderer']['symbol']['outline']['width'] = outline_width
    web_map['operationalLayers'][0]['featureCollection']['layers'][0]['layerDefinition']['drawingInfo']['renderer']['symbol']['outline']['color'] = list(outline_colour)
    web_map['operationalLayers'][0]['featureCollection']['layers'][0]['featureSet']['features'] = _convert_cluster_to_operational_layers(cluster)
    web_map['exportOptions']['outputSize'] = [x_size, y_size]
    web_map['exportOptions']['dpi'] = dpi
    print(json.dumps(web_map))
    return json.dumps(web_map)


def _get_centroid(cluster: List[Location]) -> Tuple[float, float]:
    """
    Given a list of Location objects, gets the centre point of the lat/long
    pairs and converts them to X/Y coordinates
    Args:
        cluster (List[Location]): The Location objects containing the
        lat/long pairs
    Returns:
        Tuple(float, float): The X and Y coordinate of the centre point
    """
    lat_long_list = []
    for location in cluster:
        lat_long_list.append((float(location.lat), float(location.lng)))
    points = MultiPoint(lat_long_list)
    centroid_tuple = list(points.centroid.coords)[0]
    return lat_long_to_x_y(centroid_tuple[0], centroid_tuple[1])


def _convert_cluster_to_operational_layers(cluster: List[Location]) -> str:
    """
    Converts a cluster of Location objects to a JSON array to be used
    in ArcGIS's ExportWebMap JSON
    Args:
        cluster (List[Location]): The cluster of Location objects to draw as
        features on the map
    Returns:
        str: The operationalLayers array containing the cluster locations as a
        no-whitespace JSON string
    """
    features = []
    for location in cluster:
        feature = {}
        geometry = {}
        geometry['x'] = location.x
        geometry['y'] = location.y
        spatial_reference = {}
        spatial_reference['wkid'] = 27700
        geometry['spatialReference'] = spatial_reference
        feature['geometry'] = geometry
        features.append(feature)
    return features
